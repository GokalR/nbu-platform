"""Phase 6E: LlmPlanner adapter. No real network call."""

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
)


def _settings_with_key(key: str | None = "x") -> Settings:
    return Settings(anthropic_api_key=key, llm_model="claude-test")


def _openai_settings_with_key(key: str | None = "openai-key") -> Settings:
    return Settings(
        llm_provider="openai",
        openai_api_key=key,
        anthropic_api_key=None,
        llm_model="gpt-test",
    )


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


def test_returns_raw_provider_text() -> None:
    captured: dict[str, object] = {}

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        captured["model"] = model
        captured["prompt"] = prompt
        captured["api_key"] = api_key
        return '{"kind": "clarify", "sql": null, "user_message": "?"}'

    planner = LlmPlanner(settings=_settings_with_key(), provider_call=fake_provider)
    raw = planner.plan("how many mahallas in Andijon?")
    assert raw == '{"kind": "clarify", "sql": null, "user_message": "?"}'
    assert captured["model"] == "claude-test"
    assert captured["api_key"] == "x"


def test_build_planner_prompt_called_with_exact_user_question() -> None:
    seen_prompts: list[str] = []

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        seen_prompts.append(prompt)
        return '{"kind": "clarify", "sql": null, "user_message": "?"}'

    planner = LlmPlanner(settings=_settings_with_key(), provider_call=fake_provider)
    planner.plan("EXACT QUESTION 12345")
    assert len(seen_prompts) == 1
    assert "EXACT QUESTION 12345" in seen_prompts[0]


def test_missing_api_key_raises() -> None:
    planner = LlmPlanner(
        settings=_settings_with_key(key=None),
        provider_call=lambda m, p, k: "should not be called",
    )
    with pytest.raises(LlmPlannerError, match="ANTHROPIC_API_KEY"):
        planner.plan("anything")


def test_openai_provider_uses_openai_key_and_model() -> None:
    captured: dict[str, object] = {}

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        captured["model"] = model
        captured["prompt"] = prompt
        captured["api_key"] = api_key
        return '{"kind": "clarify", "sql": null, "user_message": "?"}'

    planner = LlmPlanner(settings=_openai_settings_with_key(), provider_call=fake_provider)
    planner.plan("OpenAI exact question")

    assert captured["model"] == "gpt-test"
    assert captured["api_key"] == "openai-key"
    assert "OpenAI exact question" in str(captured["prompt"])


def test_openai_missing_api_key_raises() -> None:
    planner = LlmPlanner(
        settings=_openai_settings_with_key(key=None),
        provider_call=lambda m, p, k: "should not be called",
    )
    with pytest.raises(LlmPlannerError, match="OPENAI_API_KEY"):
        planner.plan("anything")


def test_openai_rejects_default_anthropic_model_name() -> None:
    planner = LlmPlanner(
        settings=Settings(
            llm_provider="openai",
            openai_api_key="x",
            llm_model="claude-opus-4-7",
        ),
        provider_call=lambda m, p, k: "should not be called",
    )
    with pytest.raises(LlmPlannerError, match="OpenAI provider requires"):
        planner.plan("anything")


def test_unknown_llm_provider_raises() -> None:
    planner = LlmPlanner(
        settings=Settings(
            llm_provider="other",
            anthropic_api_key="x",
            openai_api_key="y",
            llm_model="model",
        ),
        provider_call=lambda m, p, k: "should not be called",
    )
    with pytest.raises(LlmPlannerError, match="Unsupported LLM_PROVIDER"):
        planner.plan("anything")


def test_provider_exception_wrapped_as_llm_planner_error() -> None:
    def boom(model: str, prompt: str, api_key: str) -> str:
        raise TimeoutError("provider went away")

    planner = LlmPlanner(settings=_settings_with_key(), provider_call=boom)
    with pytest.raises(LlmPlannerError, match="provider went away"):
        planner.plan("x")


def test_provider_returning_empty_text_raises() -> None:
    planner = LlmPlanner(
        settings=_settings_with_key(),
        provider_call=lambda m, p, k: "   ",
    )
    with pytest.raises(LlmPlannerError, match="empty text"):
        planner.plan("x")


def test_no_db_connection_used_inside_planner() -> None:
    """Sanity: plan() does not import or open any SQLAlchemy connection."""
    seen_args: list[tuple[str, str, str]] = []

    def fake_provider(model: str, prompt: str, api_key: str) -> str:
        seen_args.append((model, prompt[:30], api_key))
        return '{"kind": "no_data", "sql": null, "user_message": "x"}'

    planner = LlmPlanner(settings=_settings_with_key(), provider_call=fake_provider)
    raw = planner.plan("anything")
    # The planner must have a non-empty response and made exactly one provider
    # call, never opening a DB connection.
    assert raw
    assert len(seen_args) == 1


def test_query_service_with_llm_planner_end_to_end_executes_safely() -> None:
    engine = _engine_with_views()
    _seed_run(engine)
    sql_response = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "user_message": "Region codes.",
            "reasoning_notes": ["test"],
            "expected_result_shape": "codes",
        }
    )
    planner = LlmPlanner(
        settings=_settings_with_key(),
        provider_call=lambda m, p, k: sql_response,
    )
    res = QueryService(engine, planner).ask("list region codes")
    assert res.kind == "sql_result"
    assert res.row_count == 2
    assert tuple(r[0] for r in res.rows) == (1100, 1200)


def test_query_service_with_llm_planner_propagates_provider_failure_as_planner_error() -> None:
    engine = _engine_with_views()

    def boom(model: str, prompt: str, api_key: str) -> str:
        raise RuntimeError("model 5xx")

    planner = LlmPlanner(settings=_settings_with_key(), provider_call=boom)
    res = QueryService(engine, planner).ask("anything")
    assert res.kind == "planner_error"
    assert "model 5xx" not in res.user_message  # internals hidden from user
    assert any("model 5xx" in n for n in res.debug_notes)


def test_default_log_level_does_not_dump_full_prompt() -> None:
    import io
    import logging

    target = logging.getLogger("cerr_chatbot.query.llm_planner")
    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setLevel(logging.INFO)
    prior_level = target.level
    prior_disabled = target.disabled
    target.disabled = False  # alembic fileConfig may have disabled it earlier
    target.addHandler(handler)
    target.setLevel(logging.INFO)
    try:
        planner = LlmPlanner(
            settings=_settings_with_key(),
            provider_call=lambda m, p, k: '{"kind":"clarify","sql":null,"user_message":"?"}',
        )
        planner.plan("SECRET USER QUESTION 9999")
    finally:
        target.removeHandler(handler)
        target.setLevel(prior_level)
        target.disabled = prior_disabled
    full = buf.getvalue()
    assert "SECRET USER QUESTION 9999" not in full
    assert "planner prompt built" in full
