"""EvidenceLlmPlanner adapter: provider call, prompt content, error paths."""

from __future__ import annotations

import pytest

from cerr_chatbot.config import Settings
from cerr_chatbot.query.evidence_planner import (
    EvidenceLlmPlanner,
    build_evidence_planner_prompt,
)
from cerr_chatbot.query.llm_planner import LlmPlannerError


def _settings_with_key() -> Settings:
    return Settings(
        anthropic_api_key="test-key",
        llm_provider="anthropic",
        llm_model="claude-test",
    )


# ---------- prompt content ----------


def test_prompt_includes_catalog_guard_rules_and_few_shot() -> None:
    p = build_evidence_planner_prompt("Top viloyatlar?")
    # Catalog content
    assert "v_regions" in p
    assert "v_mahallas" in p
    # SQL guard / refuse rules surfaced
    assert "REFUSE" in p
    # Context-query policy + few-shot
    assert "context_queries" in p
    assert "primary_sql" in p
    assert "EXAMPLE A" in p
    assert "0 to 5" in p or "0..N" in p
    # User question pasted verbatim
    assert "Top viloyatlar?" in p


def test_prompt_teaches_postgres_safe_aggregate_rounding() -> None:
    p = build_evidence_planner_prompt("Qaysi viloyatda aholi eng ko'p?")
    assert "ROUND(CAST(AVG(metric) AS NUMERIC), 2)" in p
    assert "Never write ROUND(AVG(metric), 2)" in p
    assert "ROUND(CAST(AVG(population) AS NUMERIC), 1)" in p
    assert "ROUND(AVG(population), 1)" not in p


def test_prompt_does_not_dictate_default_language_to_planner() -> None:
    """Final-answer language belongs to the narrator. Planner just plans.

    The only allowed mention of Uzbek Latin in the planner prompt is the
    clarify-message hygiene rule: when the planner DOES emit a clarify
    message, it must be plain Uzbek (not column names) so non-technical
    users understand it. That is one targeted exception, not a default.
    """
    p = build_evidence_planner_prompt("salom")
    # No "Default language" directive for the final answer.
    assert "Default language" not in p
    # Uzbek Latin only appears inside the narrow clarify-hygiene block.
    occurrences = p.count("Uzbek Latin")
    assert occurrences == 1, f"expected 1 occurrence, got {occurrences}"
    assert "user_message hygiene for clarify" in p


# ---------- provider call ----------


def test_planner_calls_provider_once_and_returns_raw_text() -> None:
    calls: list[tuple[str, str]] = []

    def fake(model: str, prompt: str, api_key: str) -> str:
        calls.append((model, api_key))
        return '{"kind":"sql_plan","primary_sql":"SELECT region_code FROM v_regions"}'

    pl = EvidenceLlmPlanner(settings=_settings_with_key(), provider_call=fake)
    raw = pl.plan("Top viloyatlar?")
    assert calls == [("claude-test", "test-key")]
    assert raw.startswith("{")
    assert "primary_sql" in raw


def test_planner_does_not_parse_or_validate_json() -> None:
    """Adapter is a thin wrapper; downstream parses + sql_guards."""

    def fake(*_):
        return "this is not json but the planner returns it anyway"

    pl = EvidenceLlmPlanner(settings=_settings_with_key(), provider_call=fake)
    raw = pl.plan("x")
    assert "this is not json" in raw


# ---------- error paths ----------


def test_no_api_key_raises_planner_error() -> None:
    cfg = Settings(
        anthropic_api_key=None,
        openai_api_key=None,
        llm_provider="anthropic",
        llm_model="claude-test",
    )
    pl = EvidenceLlmPlanner(settings=cfg, provider_call=lambda *_: "irrelevant")
    with pytest.raises(LlmPlannerError):
        pl.plan("x")


def test_provider_exception_wrapped() -> None:
    def fake(*_):
        raise RuntimeError("network down")

    pl = EvidenceLlmPlanner(settings=_settings_with_key(), provider_call=fake)
    with pytest.raises(LlmPlannerError) as exc:
        pl.plan("x")
    assert "network down" in str(exc.value)


def test_empty_provider_text_raises() -> None:
    pl = EvidenceLlmPlanner(settings=_settings_with_key(), provider_call=lambda *_: "")
    with pytest.raises(LlmPlannerError):
        pl.plan("x")


def test_no_db_or_sql_execution_inside_planner() -> None:
    """Adapter must not expose any DB-related attribute on its surface."""
    pl = EvidenceLlmPlanner()
    for attr in ("_engine", "engine", "execute", "executor", "db", "session"):
        assert not hasattr(pl, attr), attr


# ---------- factory + no-key fallback safety in the pipeline ----------


def test_pipeline_no_key_falls_back_safely_via_narrator() -> None:
    """Even if planner errors out, the upstream evidence_ask handles it
    cleanly. This test simulates the no-key case via planner crash."""
    from cerr_chatbot.query.evidence import evidence_ask

    cfg = Settings(
        anthropic_api_key=None,
        openai_api_key=None,
        llm_provider="anthropic",
        llm_model="claude-test",
    )
    pl = EvidenceLlmPlanner(settings=cfg)
    from sqlalchemy import create_engine

    from cerr_chatbot.db import Base
    from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)

    res = evidence_ask(engine, pl, "Top viloyatlar?")
    assert res.kind == "planner_error"
    # No internal traceback or API key leaks in the user-facing message:
    assert "test-key" not in res.user_message
    assert "Traceback" not in res.user_message
