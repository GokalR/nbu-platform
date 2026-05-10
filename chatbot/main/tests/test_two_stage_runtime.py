"""TwoStageLlmPlanner runtime + planner-mode selection."""

from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query import (
    LlmPlanner,
    LlmPlannerError,
    QueryService,
    TwoStageLlmPlanner,
    make_planner_from_settings,
)


def _settings(mode: str = "single_stage", api_key: str | None = "x") -> Settings:
    return Settings(anthropic_api_key=api_key, llm_model="claude-test", llm_planner_mode=mode)


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed_run(engine, region_codes=(1100, 1200)) -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for idx, code in enumerate(region_codes):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                "region_code, region_name_cyr) "
                f"VALUES (1, 'f{idx}', 0, {code}, 'R')"
            )


# ---------------- TwoStageLlmPlanner ----------------


def test_two_stage_calls_provider_exactly_twice() -> None:
    seen_prompts: list[str] = []

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        seen_prompts.append(prompt)
        if "stage 1" in prompt:
            return json.dumps(
                {
                    "relevant_views": ["v_regions"],
                    "relevant_columns": ["population"],
                    "metric_keys": [],
                    "pattern": "top_n",
                }
            )
        # stage 2 returns final planner JSON
        return json.dumps(
            {
                "kind": "sql",
                "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
                "user_message": "OK.",
            }
        )

    planner = TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider)
    raw = planner.plan("Aholi soni bo'yicha eng yuqori 5 viloyat")
    assert len(seen_prompts) == 2
    # raw is the stage-2 JSON, untouched
    assert json.loads(raw)["kind"] == "sql"


def test_stage1_prompt_contains_schema_linking_output_schema() -> None:
    captured: list[str] = []

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        captured.append(prompt)
        if "stage 1" in prompt:
            return json.dumps({"relevant_views": ["v_regions"], "pattern": "top_n"})
        return json.dumps({"kind": "no_data", "sql": None, "user_message": "x"})

    TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider).plan("Q")
    stage1 = captured[0]
    for needle in (
        "stage 1",
        "relevant_views",
        "relevant_columns",
        "metric_keys",
        "pattern",
        "ambiguity_notes",
        "top_n",
    ):
        assert needle in stage1, needle


def test_stage2_prompt_uses_parsed_schema_link() -> None:
    captured: list[str] = []

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        captured.append(prompt)
        if "stage 1" in prompt:
            return json.dumps(
                {
                    "relevant_views": ["v_district_macro_highlights"],
                    "metric_keys": ["industry_volume_bln_uzs"],
                    "pattern": "macro_indicator",
                }
            )
        return json.dumps({"kind": "no_data", "sql": None, "user_message": "x"})

    TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider).plan(
        "industry_volume_bln_uzs eng yuqori"
    )
    stage2 = captured[1]
    # Stage-2 prompt must reflect the link.
    assert "stage 2" in stage2
    assert "v_district_macro_highlights" in stage2
    # The expanded full-detail catalog must NOT include unrelated views.
    detail_block = stage2[
        stage2.index("RELEVANT VIEWS (full column detail") : stage2.index("RELEVANT SQL EXAMPLES")
    ]
    assert "## v_district_macro_highlights" in detail_block
    assert "## v_mahalla_specializations" not in detail_block


def test_two_stage_provider_failure_at_stage1_raises() -> None:
    def boom_stage1(model: str, prompt: str, api_key: str) -> str:
        if "stage 1" in prompt:
            raise RuntimeError("stage1 timeout")
        return ""

    with pytest.raises(LlmPlannerError, match="stage1 provider failed"):
        TwoStageLlmPlanner(settings=_settings(), provider_call=boom_stage1).plan("Q")


def test_two_stage_invalid_stage1_json_raises() -> None:
    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        if "stage 1" in prompt:
            return "not json"
        return json.dumps({"kind": "no_data", "sql": None, "user_message": "x"})

    with pytest.raises(LlmPlannerError, match="stage1 invalid"):
        TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider).plan("Q")


def test_two_stage_stage1_empty_text_raises() -> None:
    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        return "" if "stage 1" in prompt else "ignored"

    with pytest.raises(LlmPlannerError, match="stage1 provider returned empty"):
        TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider).plan("Q")


def test_two_stage_stage2_empty_text_raises() -> None:
    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        if "stage 1" in prompt:
            return json.dumps({"relevant_views": ["v_regions"], "pattern": "top_n"})
        return ""

    with pytest.raises(LlmPlannerError, match="stage2 provider returned empty"):
        TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider).plan("Q")


def test_two_stage_missing_api_key_raises() -> None:
    planner = TwoStageLlmPlanner(
        settings=_settings(api_key=None),
        provider_call=lambda m, p, k: "should not be called",
    )
    with pytest.raises(LlmPlannerError, match="ANTHROPIC_API_KEY"):
        planner.plan("Q")


def test_two_stage_raw_passes_through_to_query_service() -> None:
    engine = _engine_with_views()
    _seed_run(engine, region_codes=(1100, 1200))

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        if "stage 1" in prompt:
            return json.dumps({"relevant_views": ["v_regions"], "pattern": "top_n"})
        return json.dumps(
            {
                "kind": "sql",
                "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
                "user_message": "Region kodlari.",
            }
        )

    planner = TwoStageLlmPlanner(settings=_settings(), provider_call=fake_provider)
    res = QueryService(engine, planner).ask("Region kodlari?")
    assert res.kind == "sql_result"
    assert res.row_count == 2
    assert tuple(r[0] for r in res.rows) == (1100, 1200)


# ---------------- mode selection ----------------


def test_make_planner_default_is_single_stage() -> None:
    planner = make_planner_from_settings(_settings(mode="single_stage"))
    assert isinstance(planner, LlmPlanner)
    assert not isinstance(planner, TwoStageLlmPlanner)


def test_make_planner_two_stage_returns_two_stage() -> None:
    planner = make_planner_from_settings(_settings(mode="two_stage"))
    assert isinstance(planner, TwoStageLlmPlanner)


def test_make_planner_unknown_mode_raises() -> None:
    with pytest.raises(LlmPlannerError, match="LLM_PLANNER_MODE"):
        make_planner_from_settings(_settings(mode="weird_mode"))


def test_make_planner_passes_provider_and_log_flag_through() -> None:
    seen: list[str] = []

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        seen.append(prompt)
        if "stage 1" in prompt:
            return json.dumps({"relevant_views": ["v_regions"], "pattern": "top_n"})
        return json.dumps({"kind": "no_data", "sql": None, "user_message": "x"})

    planner = make_planner_from_settings(_settings(mode="two_stage"), provider_call=fake_provider)
    assert isinstance(planner, TwoStageLlmPlanner)
    planner.plan("Q")
    assert len(seen) == 2
