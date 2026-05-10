"""Phase 4: planner reads optional MemorySnapshot from prompt context."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.eval.parser import EvalCase
from cerr_chatbot.eval.runner import run_eval_with_pipeline
from cerr_chatbot.query.answer import Answer
from cerr_chatbot.query.evidence import evidence_ask
from cerr_chatbot.query.evidence_narrator import EvidenceLlmNarrator
from cerr_chatbot.query.evidence_planner import (
    EvidenceLlmPlanner,
    build_evidence_planner_prompt,
    render_memory_snapshot_for_prompt,
)
from cerr_chatbot.query.pipeline import EvidencePipeline
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
    MemorySnapshot,
)


@dataclass
class _RecordingPlanner:
    """Captures every plan() call so we can inspect what memory was passed."""

    response: str = ""
    seen_questions: list[str] = field(default_factory=list)
    seen_snapshots: list[MemorySnapshot | None] = field(default_factory=list)

    def plan(self, q: str, *, memory_snapshot: MemorySnapshot | None = None) -> str:
        self.seen_questions.append(q)
        self.seen_snapshots.append(memory_snapshot)
        return self.response


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
        return Answer(text="static", kind=result.kind, sql=sql, row_count=rows, columns=cols)


def _engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed(e):
    with e.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for i, code in enumerate((1100, 1200, 1300)):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                f"region_code, region_name_cyr) VALUES (1, 'f{i}', 0, {code}, 'R{code}')"
            )


def _snapshot() -> MemorySnapshot:
    return MemorySnapshot(
        last_question="Toshkent viloyatining aholisi?",
        last_resolved_question="Toshkent viloyatining aholisi qancha?",
        last_answer_type="sql_result",
        last_columns=("region_name_cyr", "population"),
        last_row_count=1,
        last_result_summary="row_count=1; columns=region_name_cyr,population",
        created_at="2026-05-10T12:00:00+00:00",
    )


def _sql_plan(extra: dict | None = None) -> str:
    body: dict = {
        "kind": "sql_plan",
        "primary_sql": "SELECT region_code FROM v_regions",
        "context_queries": [],
    }
    if extra:
        body.update(extra)
    return json.dumps(body)


# ---------- prompt builder ----------


def test_prompt_without_memory_excludes_context_block() -> None:
    p = build_evidence_planner_prompt("Top viloyatlar?")
    assert "OPTIONAL CONVERSATION CONTEXT" not in p
    assert "Previous focus" not in p


def test_prompt_with_memory_includes_context_block_and_fields() -> None:
    snap = _snapshot()
    p = build_evidence_planner_prompt("va aholisi?", memory_snapshot=snap)
    assert "OPTIONAL CONVERSATION CONTEXT" in p
    assert "Previous turn" in p
    assert "Toshkent viloyatining aholisi qancha?" in p
    assert "row_count=1" in p
    assert "region_name_cyr" in p
    assert "2026-05-10T12:00:00+00:00" in p
    # User question still appears verbatim and after the memory block.
    assert "USER QUESTION:" in p
    user_idx = p.index("USER QUESTION:")
    mem_idx = p.index("OPTIONAL CONVERSATION CONTEXT")
    assert mem_idx < user_idx


def test_prompt_memory_block_does_not_leak_sql_or_rows() -> None:
    snap = _snapshot()
    p = build_evidence_planner_prompt("va aholisi?", memory_snapshot=snap)
    # Locate the context block bounds so we don't false-positive on
    # SQL that legitimately appears in the catalog/few-shot sections.
    start = p.index("OPTIONAL CONVERSATION CONTEXT")
    end = p.index("USER QUESTION:", start)
    block = p[start:end]
    assert "SELECT" not in block
    assert "FROM" not in block
    assert "primary_sql" not in block
    # Numeric row values are not part of the snapshot — only row_count is.
    assert "3000000" not in block


def test_render_memory_snapshot_is_pure_json() -> None:
    snap = _snapshot()
    rendered = render_memory_snapshot_for_prompt(snap)
    parsed = json.loads(rendered)
    assert set(parsed) == {
        "last_question",
        "last_resolved_question",
        "last_answer_type",
        "last_columns",
        "last_row_count",
        "last_result_summary",
        "created_at",
    }


# ---------- adapter forwards memory ----------


def test_evidence_llm_planner_forwards_memory_into_prompt() -> None:
    snap = _snapshot()
    captured: list[str] = []

    def fake(model: str, prompt: str, api_key: str) -> str:  # noqa: ARG001
        captured.append(prompt)
        return _sql_plan()

    settings = Settings(
        anthropic_api_key="x", llm_provider="anthropic", llm_model="claude-test"
    )
    pl = EvidenceLlmPlanner(settings=settings, provider_call=fake)
    pl.plan("va aholisi?", memory_snapshot=snap)
    assert len(captured) == 1
    assert "OPTIONAL CONVERSATION CONTEXT" in captured[0]
    assert "Toshkent viloyatining aholisi qancha?" in captured[0]


def test_evidence_llm_planner_no_memory_leaves_prompt_unchanged() -> None:
    captured: list[str] = []

    def fake(model: str, prompt: str, api_key: str) -> str:  # noqa: ARG001
        captured.append(prompt)
        return _sql_plan()

    settings = Settings(
        anthropic_api_key="x", llm_provider="anthropic", llm_model="claude-test"
    )
    pl = EvidenceLlmPlanner(settings=settings, provider_call=fake)
    pl.plan("Top viloyatlar?")
    assert "OPTIONAL CONVERSATION CONTEXT" not in captured[0]


# ---------- evidence_ask passes memory through ----------


def test_evidence_ask_forwards_memory_snapshot_to_planner() -> None:
    eng = _engine()
    _seed(eng)
    planner = _RecordingPlanner(response=_sql_plan())
    snap = _snapshot()
    res = evidence_ask(eng, planner, "va aholisi?", memory_snapshot=snap)
    assert res.kind == "sql_result"
    assert planner.seen_snapshots == [snap]


def test_conversational_router_short_circuit_skips_planner_even_with_memory() -> None:
    eng = _engine()
    planner = _RecordingPlanner(response=_sql_plan())
    snap = _snapshot()
    res = evidence_ask(eng, planner, "Salom", memory_snapshot=snap)
    assert res.kind == "greeting"
    assert planner.seen_questions == []
    assert planner.seen_snapshots == []


# ---------- pipeline reads before planning ----------


def _pipeline(planner, store):
    eng = _engine()
    _seed(eng)
    return EvidencePipeline(
        engine=eng, planner=planner, narrator=_StaticNarrator(), memory_store=store
    )


def test_pipeline_reads_memory_before_planning() -> None:
    store = InMemorySessionMemoryStore()
    snap = _snapshot()
    store.set("u1", snap)
    planner = _RecordingPlanner(response=_sql_plan())
    pipe = _pipeline(planner, store)
    out = pipe.answer("va aholisi?", session_id="u1")
    assert out["ok"] is True
    assert planner.seen_snapshots == [snap]
    assert "memory_snapshot_sent_to_planner=true" in out["debug_notes"]


def test_pipeline_does_not_read_memory_when_no_session_id() -> None:
    store = InMemorySessionMemoryStore()
    store.set("u1", _snapshot())
    planner = _RecordingPlanner(response=_sql_plan())
    pipe = _pipeline(planner, store)
    pipe.answer("q")
    assert planner.seen_snapshots == [None]


def test_pipeline_does_not_read_memory_when_no_store() -> None:
    planner = _RecordingPlanner(response=_sql_plan())
    pipe = _pipeline(planner, None)
    pipe.answer("q", session_id="u1")
    assert planner.seen_snapshots == [None]


def test_pipeline_writes_updated_snapshot_after_success() -> None:
    store = InMemorySessionMemoryStore()
    store.set("u1", _snapshot())
    planner = _RecordingPlanner(
        response=_sql_plan({"resolved_question": "rewritten standalone Q", "memory_use": "used"})
    )
    pipe = _pipeline(planner, store)
    pipe.answer("va aholisi?", session_id="u1")
    fresh = store.get("u1")
    assert fresh is not None
    assert fresh.last_question == "va aholisi?"
    assert fresh.last_resolved_question == "rewritten standalone Q"


# ---------- resolved_question flows into pack ----------


def test_used_memory_resolved_question_is_pack_question() -> None:
    eng = _engine()
    _seed(eng)
    planner = _RecordingPlanner(
        response=_sql_plan(
            {"resolved_question": "Toshkent viloyatining aholisi?", "memory_use": "used"}
        )
    )
    res = evidence_ask(eng, planner, "va aholisi?", memory_snapshot=_snapshot())
    assert res.pack is not None
    assert res.pack.question == "Toshkent viloyatining aholisi?"
    assert "memory_use=used" in res.debug_notes


def test_ignored_memory_keeps_current_question() -> None:
    eng = _engine()
    _seed(eng)
    planner = _RecordingPlanner(
        response=_sql_plan({"memory_use": "ignored"})
    )
    res = evidence_ask(eng, planner, "Top viloyatlar?", memory_snapshot=_snapshot())
    assert res.pack is not None
    assert res.pack.question == "Top viloyatlar?"
    assert "memory_use=ignored" in res.debug_notes


def test_unclear_memory_with_clarify_works_normally() -> None:
    eng = _engine()
    planner = _RecordingPlanner(
        response=json.dumps(
            {
                "kind": "clarify",
                "user_message": "iltimos aniqlashtiring",
                "memory_use": "unclear",
            }
        )
    )
    res = evidence_ask(eng, planner, "...", memory_snapshot=_snapshot())
    assert res.kind == "clarify"
    assert res.user_message == "iltimos aniqlashtiring"


# ---------- standalone vs follow-up flows ----------


def test_standalone_question_with_memory_present_planner_ignores_it() -> None:
    store = InMemorySessionMemoryStore()
    store.set("u1", _snapshot())
    planner = _RecordingPlanner(response=_sql_plan({"memory_use": "ignored"}))
    pipe = _pipeline(planner, store)
    out = pipe.answer("Top 5 viloyat aholi soni bo'yicha", session_id="u1")
    assert out["ok"] is True
    # Memory was offered but planner chose to ignore.
    assert planner.seen_snapshots[-1] is not None


def test_follow_up_question_with_memory_planner_uses_resolved_question() -> None:
    store = InMemorySessionMemoryStore()
    store.set("u1", _snapshot())
    planner = _RecordingPlanner(
        response=_sql_plan(
            {
                "memory_use": "used",
                "resolved_question": "Toshkent viloyati uchun reyting bali",
            }
        )
    )
    pipe = _pipeline(planner, store)
    pipe.answer("va reytingi?", session_id="u1")
    fresh = store.get("u1")
    assert fresh is not None
    assert fresh.last_resolved_question == "Toshkent viloyati uchun reyting bali"


def test_clarify_context_is_available_to_next_user_answer() -> None:
    store = InMemorySessionMemoryStore()
    planner = _RecordingPlanner(
        response=json.dumps(
            {
                "kind": "clarify",
                "user_message": "Qaysi ko'rsatkich kerak?",
            }
        )
    )
    pipe = _pipeline(planner, store)
    pipe.answer("Samarqand haqida ma'lumot ber", session_id="u1")
    pending = store.get("u1")
    assert pending is not None
    assert pending.last_answer_type == "clarify"
    assert pending.last_question == "Samarqand haqida ma'lumot ber"
    assert "pending_clarification=true" in pending.last_result_summary

    planner.response = _sql_plan(
        {
            "memory_use": "used",
            "resolved_question": "Samarqand bo'yicha umumiy ma'lumot",
        }
    )
    pipe.answer("Umumiy ma'lumot", session_id="u1")
    assert planner.seen_snapshots[-1] == pending
    fresh = store.get("u1")
    assert fresh is not None
    assert fresh.last_resolved_question == "Samarqand bo'yicha umumiy ma'lumot"


# ---------- eval still isolated ----------


def test_eval_runner_does_not_leak_memory_between_cases() -> None:
    store = InMemorySessionMemoryStore()
    store.set("anything", _snapshot())
    planner = _RecordingPlanner(response=_sql_plan())
    pipe = _pipeline(planner, store)
    cases = [
        EvalCase(case_number=1, title="t", question="q1", expected_answer="x"),
        EvalCase(case_number=2, title="t", question="q2", expected_answer="x"),
    ]
    run_eval_with_pipeline(pipe, cases)
    # Eval forces session_id=None → planner never sees memory snapshots.
    assert planner.seen_snapshots == [None, None]
