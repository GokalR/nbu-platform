"""Phase 3A: EvidencePipeline writes a snapshot when memory_store + session_id."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query.evidence_narrator import EvidenceLlmNarrator
from cerr_chatbot.query.pipeline import EvidencePipeline
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
)


@dataclass
class _Planner:
    response: str = ""
    seen: list[str] = field(default_factory=list)

    def plan(self, q: str, *, memory_snapshot=None) -> str:  # noqa: ARG002
        self.seen.append(q)
        return self.response


def _engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed(engine, codes=(1100, 1200, 1300)) -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for i, code in enumerate(codes):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                f"region_code, region_name_cyr) VALUES (1, 'f{i}', 0, {code}, 'R{code}')"
            )


def _sql_plan(primary: str = "SELECT region_code FROM v_regions") -> str:
    return json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "ok",
            "primary_sql": primary,
            "context_queries": [],
        }
    )


class _StaticNarrator(EvidenceLlmNarrator):
    def __init__(self) -> None:
        pass

    def narrate(self, result):  # type: ignore[override]
        from cerr_chatbot.query.answer import Answer

        cols: tuple[str, ...] = ()
        rows = 0
        sql = None
        if result.pack is not None:
            cols = result.pack.primary.columns
            rows = result.pack.primary.row_count
            sql = result.pack.primary.sql
        return Answer(text="static", kind=result.kind, sql=sql, row_count=rows, columns=cols)


def _pipeline(planner: _Planner, store: InMemorySessionMemoryStore | None = None):
    return EvidencePipeline(
        engine=_seeded_engine(),
        planner=planner,
        narrator=_StaticNarrator(),
        memory_store=store,
    )


def _seeded_engine():
    e = _engine()
    _seed(e)
    return e


def test_sql_result_writes_snapshot_when_store_and_session() -> None:
    store = InMemorySessionMemoryStore()
    pipe = _pipeline(_Planner(response=_sql_plan()), store)
    out = pipe.answer("list region codes", session_id="user-42")
    assert out["ok"] is True
    snap = store.get("user-42")
    assert snap is not None
    assert snap.last_question == "list region codes"
    assert snap.last_resolved_question == "list region codes"
    assert snap.last_answer_type == "sql_result"
    assert snap.last_columns == ("region_code",)
    assert snap.last_row_count == 3


def test_no_session_id_means_no_write() -> None:
    store = InMemorySessionMemoryStore()
    pipe = _pipeline(_Planner(response=_sql_plan()), store)
    pipe.answer("q")
    assert store.get("") is None


def test_no_store_does_not_crash() -> None:
    pipe = _pipeline(_Planner(response=_sql_plan()), None)
    out = pipe.answer("q", session_id="user-42")
    assert out["ok"] is True


def test_clarify_writes_pending_snapshot() -> None:
    store = InMemorySessionMemoryStore()
    raw = json.dumps({"kind": "clarify", "user_message": "Qaysi ko'rsatkich kerak?"})
    pipe = _pipeline(_Planner(response=raw), store)
    pipe.answer("vague", session_id="user-42")
    snap = store.get("user-42")
    assert snap is not None
    assert snap.last_question == "vague"
    assert snap.last_answer_type == "clarify"
    assert snap.last_columns == ()
    assert snap.last_row_count == 0
    assert "pending_clarification=true" in snap.last_result_summary


def test_no_data_does_not_write_snapshot() -> None:
    store = InMemorySessionMemoryStore()
    raw = json.dumps({"kind": "no_data", "user_message": "yo'q"})
    pipe = _pipeline(_Planner(response=raw), store)
    pipe.answer("missing metric", session_id="user-42")
    assert store.get("user-42") is None


def test_unsupported_does_not_write_snapshot() -> None:
    store = InMemorySessionMemoryStore()
    raw = json.dumps({"kind": "unsupported", "user_message": "no"})
    pipe = _pipeline(_Planner(response=raw), store)
    pipe.answer("DROP TABLE", session_id="user-42")
    assert store.get("user-42") is None


def test_planner_error_does_not_write_snapshot() -> None:
    store = InMemorySessionMemoryStore()
    raw = '{"kind": "weird"}'
    pipe = _pipeline(_Planner(response=raw), store)
    pipe.answer("q", session_id="user-42")
    assert store.get("user-42") is None


def test_session_isolation_in_pipeline() -> None:
    store = InMemorySessionMemoryStore()
    pipe = _pipeline(_Planner(response=_sql_plan()), store)
    pipe.answer("q1", session_id="alice")
    pipe.answer("q2", session_id="bob")
    a = store.get("alice")
    b = store.get("bob")
    assert a is not None and a.last_question == "q1"
    assert b is not None and b.last_question == "q2"


def test_snapshot_uses_resolved_question_from_pack() -> None:
    store = InMemorySessionMemoryStore()
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "ok",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "resolved_question": "rewritten by planner",
        }
    )
    pipe = _pipeline(_Planner(response=raw), store)
    pipe.answer("orig", session_id="s1")
    snap = store.get("s1")
    assert snap is not None
    assert snap.last_question == "orig"
    assert snap.last_resolved_question == "rewritten by planner"
