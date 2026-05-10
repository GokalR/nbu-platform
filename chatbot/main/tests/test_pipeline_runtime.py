"""Pipeline factory + LegacyPipeline + EvidencePipeline wiring."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import pytest
from sqlalchemy import create_engine

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query import (
    EvidenceLlmNarrator,
    EvidencePipeline,
    LegacyPipeline,
    QueryService,
    make_pipeline_from_settings,
)


@dataclass
class _LegacyPlanner:
    response: str = ""
    seen: list[str] = field(default_factory=list)

    def plan(self, q: str) -> str:
        self.seen.append(q)
        return self.response


@dataclass
class _EvidencePlanner:
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


def _seed(engine, codes=(1100, 1200)):
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


def test_legacy_pipeline_returns_uniform_dict() -> None:
    engine = _engine()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "user_message": "ok",
        }
    )
    svc = QueryService(engine, _LegacyPlanner(response=raw))
    pipe = LegacyPipeline(service=svc)
    out = pipe.answer("region kodlari")
    assert out["pipeline"] == "legacy"
    assert out["ok"] is True
    assert out["kind"] == "sql_result"
    assert out["row_count"] == 2
    assert isinstance(out["debug_notes"], list)


def test_legacy_pipeline_empty_question_short_circuits() -> None:
    engine = _engine()
    svc = QueryService(engine, _LegacyPlanner(response="should not be used"))
    pipe = LegacyPipeline(service=svc)
    out = pipe.answer("   ")
    assert out["kind"] == "empty_question"
    assert out["answer"] == "Savol yozing."


def test_evidence_pipeline_runs_primary_and_context() -> None:
    engine = _engine()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "ok",
            "primary_sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "context_queries": [
                {"purpose": "total", "sql": "SELECT COUNT(*) AS n FROM v_regions"}
            ],
        }
    )

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        _ = model, api_key
        assert "1,100" in prompt
        assert "## total" in prompt
        return "Region kodlari 1,100 va 1,200; jami 2 ta viloyat mavjud."

    cfg = Settings(
        anthropic_api_key="x",
        llm_provider="anthropic",
        llm_model="claude-test",
    )
    pipe = EvidencePipeline(
        engine=engine,
        planner=_EvidencePlanner(response=raw),
        narrator=EvidenceLlmNarrator(settings=cfg, provider_call=fake_provider),
    )
    out = pipe.answer("Region kodlari?")
    assert out["pipeline"] == "evidence"
    assert out["ok"] is True
    assert out["kind"] == "sql_result"
    assert "1,100" in out["answer"]
    assert "2 ta" in out["answer"]


def test_evidence_pipeline_records_bad_context_in_debug_notes() -> None:
    engine = _engine()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [{"purpose": "bad", "sql": "SELECT * FROM v_regions"}],
        }
    )
    cfg = Settings(
        anthropic_api_key="x",
        llm_provider="anthropic",
        llm_model="claude-test",
    )
    pipe = EvidencePipeline(
        engine=engine,
        planner=_EvidencePlanner(response=raw),
        narrator=EvidenceLlmNarrator(settings=cfg, provider_call=lambda *_: "ok 1100 1200"),
    )
    out = pipe.answer("codes")
    assert out["ok"] is True
    assert any("context[bad]" in n for n in out["debug_notes"])


def test_factory_legacy_default() -> None:
    engine = _engine()
    legacy_planner = _LegacyPlanner(response='{"kind":"clarify","sql":null,"user_message":"?"}')
    cfg = Settings(query_pipeline_mode="legacy")
    pipe = make_pipeline_from_settings(engine, legacy_planner=legacy_planner, settings=cfg)
    assert isinstance(pipe, LegacyPipeline)


def test_factory_evidence_when_mode_is_evidence() -> None:
    engine = _engine()
    cfg = Settings(query_pipeline_mode="evidence")
    pipe = make_pipeline_from_settings(
        engine,
        evidence_planner=_EvidencePlanner(response="{}"),
        settings=cfg,
    )
    assert isinstance(pipe, EvidencePipeline)


def test_factory_rejects_missing_planner_for_chosen_mode() -> None:
    engine = _engine()
    with pytest.raises(ValueError):
        make_pipeline_from_settings(engine, settings=Settings(query_pipeline_mode="evidence"))
    with pytest.raises(ValueError):
        make_pipeline_from_settings(engine, settings=Settings(query_pipeline_mode="legacy"))


def test_factory_rejects_unknown_mode() -> None:
    engine = _engine()
    with pytest.raises(ValueError):
        make_pipeline_from_settings(
            engine,
            legacy_planner=_LegacyPlanner(),
            settings=Settings(query_pipeline_mode="weird"),
        )
