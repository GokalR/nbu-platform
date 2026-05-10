"""Pending-clarification flow: clarify on turn 1, planner combines on turn 2."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query.answer import Answer
from cerr_chatbot.query.evidence_narrator import EvidenceLlmNarrator
from cerr_chatbot.query.evidence_planner import build_evidence_planner_prompt
from cerr_chatbot.query.pipeline import EvidencePipeline
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
    MemorySnapshot,
)


def _engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed(eng):
    with eng.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for i, code in enumerate((1100, 1200, 1300)):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                f"region_code, region_name_cyr) VALUES (1, 'f{i}', 0, {code}, 'R{code}')"
            )


class _StaticNarrator(EvidenceLlmNarrator):
    def __init__(self) -> None:
        pass

    def narrate(self, result):  # type: ignore[override]
        cols: tuple[str, ...] = ()
        rows = 0
        sql = None
        if result.pack is not None:
            cols = result.pack.primary.columns
            rows = result.pack.primary.row_count
            sql = result.pack.primary.sql
        return Answer(
            text=result.user_message or "static",
            kind=result.kind,
            sql=sql,
            row_count=rows,
            columns=cols,
        )


@dataclass
class _ScriptedPlanner:
    responses: list[str] = field(default_factory=list)
    seen_snapshots: list[MemorySnapshot | None] = field(default_factory=list)
    seen_questions: list[str] = field(default_factory=list)

    def plan(self, q: str, *, memory_snapshot: MemorySnapshot | None = None) -> str:
        self.seen_questions.append(q)
        self.seen_snapshots.append(memory_snapshot)
        return self.responses[len(self.seen_questions) - 1]


def _pipeline(planner, store):
    eng = _engine()
    _seed(eng)
    return EvidencePipeline(
        engine=eng, planner=planner, narrator=_StaticNarrator(), memory_store=store
    )


def test_prompt_includes_pending_clarify_guide_when_last_was_clarify() -> None:
    snap = MemorySnapshot(
        last_question="Samarqand haqida malumot ber",
        last_resolved_question="Samarqand haqida malumot ber",
        last_answer_type="clarify",
        last_columns=(),
        last_row_count=0,
        last_result_summary="pending_clarification=true; assistant_asked=Qaysi ko'rsatkich?",
        created_at="2026-05-10T12:00:00+00:00",
    )
    p = build_evidence_planner_prompt("umumiy ma'lumot", memory_snapshot=snap)
    assert "pending_clarification=true" in p
    assert "CLARIFICATION request" in p
    assert "ANSWER to that clarification" in p
    assert "Combine the previous user question" in p
    assert "Samarqand haqida malumot ber" in p


def test_prompt_omits_pending_clarify_guide_when_last_was_sql_result() -> None:
    snap = MemorySnapshot(
        last_question="Aholi soni?",
        last_resolved_question="Toshkent viloyati aholi soni",
        last_answer_type="sql_result",
        last_columns=("region_name_cyr", "population"),
        last_row_count=1,
        last_result_summary="row_count=1; columns=region_name_cyr,population",
        created_at="2026-05-10T12:00:00+00:00",
    )
    p = build_evidence_planner_prompt("va reytingi?", memory_snapshot=snap)
    assert "CLARIFICATION request" not in p
    assert "ANSWER to that clarification" not in p


def test_two_turn_clarify_then_resolved_sql_plan() -> None:
    store = InMemorySessionMemoryStore()
    clarify_raw = json.dumps(
        {
            "kind": "clarify",
            "user_message": "Qaysi ko'rsatkich kerak: aholi, reyting bali yoki tadbirkorlik?",
        }
    )
    sql_raw = json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "ok",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "memory_use": "used",
            "resolved_question": "Samarqand viloyati bo'yicha umumiy ma'lumot",
        }
    )
    planner = _ScriptedPlanner(responses=[clarify_raw, sql_raw])
    pipe = _pipeline(planner, store)

    out1 = pipe.answer("Samarqand haqida malumot ber", session_id="u1")
    assert out1["kind"] == "clarify"
    assert planner.seen_snapshots[0] is None

    snap_after_turn1 = store.get("u1")
    assert snap_after_turn1 is not None
    assert snap_after_turn1.last_answer_type == "clarify"
    assert snap_after_turn1.last_question == "Samarqand haqida malumot ber"
    assert "pending_clarification=true" in snap_after_turn1.last_result_summary

    out2 = pipe.answer("umumiy ma'lumot", session_id="u1")
    assert out2["kind"] == "sql_result"
    assert "memory_snapshot_sent_to_planner=true" in out2["debug_notes"]
    sent = planner.seen_snapshots[1]
    assert sent is not None
    assert sent.last_answer_type == "clarify"
    assert sent.last_question == "Samarqand haqida malumot ber"

    fresh = store.get("u1")
    assert fresh is not None
    assert fresh.last_answer_type == "sql_result"
    assert fresh.last_resolved_question == "Samarqand viloyati bo'yicha umumiy ma'lumot"


def test_different_session_does_not_receive_pending_memory() -> None:
    store = InMemorySessionMemoryStore()
    clarify_raw = json.dumps(
        {"kind": "clarify", "user_message": "Qaysi ko'rsatkich?"}
    )
    sql_raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
        }
    )
    planner = _ScriptedPlanner(responses=[clarify_raw, sql_raw])
    pipe = _pipeline(planner, store)

    pipe.answer("Samarqand haqida malumot ber", session_id="alice")
    pipe.answer("umumiy ma'lumot", session_id="bob")

    assert planner.seen_snapshots[1] is None


def test_full_new_question_can_still_ignore_pending_memory() -> None:
    store = InMemorySessionMemoryStore()
    clarify_raw = json.dumps({"kind": "clarify", "user_message": "Qaysi ko'rsatkich?"})
    sql_raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "memory_use": "ignored",
        }
    )
    planner = _ScriptedPlanner(responses=[clarify_raw, sql_raw])
    pipe = _pipeline(planner, store)
    pipe.answer("Samarqand haqida malumot ber", session_id="u1")
    out2 = pipe.answer(
        "Top 5 viloyat aholi soni bo'yicha", session_id="u1"
    )
    assert out2["kind"] == "sql_result"
    assert "memory_use=ignored" in out2["debug_notes"]
