"""run_eval_with_pipeline: works with both legacy and evidence pipelines."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.eval import EvalCase, run_eval_with_pipeline
from cerr_chatbot.query import (
    EvidenceLlmNarrator,
    EvidencePipeline,
    LegacyPipeline,
    QueryService,
)


@dataclass
class _StubPlanner:
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
    with e.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for i, code in enumerate((1100, 1200)):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                f"region_code, region_name_cyr) VALUES (1, 'f{i}', 0, {code}, 'R{code}')"
            )
    return e


def test_eval_runs_against_legacy_pipeline() -> None:
    engine = _engine()
    raw = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "user_message": "ok",
        }
    )
    pipe = LegacyPipeline(service=QueryService(engine, _StubPlanner(response=raw)))
    cases = [EvalCase(1, "t", "Region kodlari?", "1100, 1200")]
    report = run_eval_with_pipeline(pipe, cases)
    assert report.total == 1
    assert report.passed == 1
    assert report.cases[0].service_kind == "sql_result"
    assert "1100" in report.cases[0].actual_answer
    assert "1200" in report.cases[0].actual_answer


def test_eval_runs_against_evidence_pipeline() -> None:
    engine = _engine()
    plan_raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "context_queries": [],
        }
    )
    cfg = Settings(
        anthropic_api_key="x",
        llm_provider="anthropic",
        llm_model="claude-test",
    )
    nar = EvidenceLlmNarrator(
        settings=cfg,
        provider_call=lambda *_: "Region kodlari 1100 va 1200 topildi.",
    )
    pipe = EvidencePipeline(engine=engine, planner=_StubPlanner(response=plan_raw), narrator=nar)
    cases = [EvalCase(1, "t", "Region kodlari?", "1100, 1200")]
    report = run_eval_with_pipeline(pipe, cases)
    assert report.total == 1
    assert report.passed == 1
    assert report.cases[0].service_kind == "sql_result"
    assert "1100" in report.cases[0].actual_answer
    assert "1200" in report.cases[0].actual_answer
