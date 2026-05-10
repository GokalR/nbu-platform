"""Phase 3B/3C: factory memory wiring and eval isolation."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from sqlalchemy import create_engine

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.eval.parser import EvalCase
from cerr_chatbot.eval.runner import run_eval_with_pipeline
from cerr_chatbot.query.pipeline import EvidencePipeline, make_pipeline_from_settings
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
    MemorySnapshot,
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


def test_factory_attaches_in_memory_store_when_ephemeral() -> None:
    eng = _engine()
    settings = Settings(query_pipeline_mode="evidence", query_memory_mode="ephemeral")
    pipe = make_pipeline_from_settings(
        eng, evidence_planner=_Planner(), settings=settings
    )
    assert isinstance(pipe, EvidencePipeline)
    assert isinstance(pipe.memory_store, InMemorySessionMemoryStore)


def test_factory_leaves_memory_store_none_when_off() -> None:
    eng = _engine()
    settings = Settings(query_pipeline_mode="evidence", query_memory_mode="off")
    pipe = make_pipeline_from_settings(
        eng, evidence_planner=_Planner(), settings=settings
    )
    assert isinstance(pipe, EvidencePipeline)
    assert pipe.memory_store is None


def test_factory_default_memory_mode_is_off() -> None:
    eng = _engine()
    settings = Settings(query_pipeline_mode="evidence")
    pipe = make_pipeline_from_settings(
        eng, evidence_planner=_Planner(), settings=settings
    )
    assert isinstance(pipe, EvidencePipeline)
    assert pipe.memory_store is None


def test_factory_invalid_memory_mode_raises() -> None:
    eng = _engine()
    settings = Settings(query_pipeline_mode="evidence", query_memory_mode="weird")
    with pytest.raises(ValueError, match="QUERY_MEMORY_MODE"):
        make_pipeline_from_settings(
            eng, evidence_planner=_Planner(), settings=settings
        )


def test_factory_legacy_with_ephemeral_does_not_break() -> None:
    """Legacy path has no memory store; ephemeral setting must not raise."""
    eng = _engine()

    class _LegacyPlanner:
        def plan(self, q: str) -> str:
            return ""

    settings = Settings(query_pipeline_mode="legacy", query_memory_mode="ephemeral")
    pipe = make_pipeline_from_settings(
        eng, legacy_planner=_LegacyPlanner(), settings=settings
    )
    assert pipe is not None


class _MemoryAwarePipeline:
    def __init__(self) -> None:
        self.store = InMemorySessionMemoryStore()
        self.session_ids: list[str | None] = []

    def answer(
        self,
        q: str,
        *,
        max_rows: int = 10,
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> dict:
        self.session_ids.append(session_id)
        _ = max_rows, include_debug
        if session_id:
            self.store.set(
                session_id,
                MemorySnapshot(
                    last_question=q,
                    last_resolved_question=q,
                    last_answer_type="sql_result",
                    last_columns=("c",),
                    last_row_count=1,
                    last_result_summary="row_count=1; columns=c",
                    created_at="2026-05-10T00:00:00+00:00",
                ),
            )
        return {
            "ok": True,
            "kind": "sql_result",
            "answer": "x",
            "sql": None,
            "row_count": 1,
            "columns": [],
            "debug_notes": [],
        }


def test_eval_runner_passes_session_id_none() -> None:
    pipe = _MemoryAwarePipeline()
    cases = [
        EvalCase(case_number=1, title="t1", question="q1", expected_answer="a1"),
        EvalCase(case_number=2, title="t2", question="q2", expected_answer="a2"),
    ]
    run_eval_with_pipeline(pipe, cases)
    assert pipe.session_ids == [None, None]
    assert pipe.store.get("") is None
