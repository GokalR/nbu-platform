"""AnswerNarrator (deterministic + LLM) tests.

The LLM provider is always stubbed; no real network call.
"""

from __future__ import annotations

from cerr_chatbot.config import Settings
from cerr_chatbot.query.narrator import (
    DeterministicNarrator,
    LlmNarrator,
    build_narrator_prompt,
    make_narrator_from_settings,
)
from cerr_chatbot.query.service import (
    SQL_RESULT_GENERIC_INTRO,
    QueryServiceResult,
)


def _sql_result(
    rows=(("Andijon", 1234), ("Fargona", 5678)),
    columns=("region_name_cyr", "population"),
    user_question="Qaysi viloyatda aholi ko'p?",
):
    return QueryServiceResult(
        kind="sql_result",
        user_message=SQL_RESULT_GENERIC_INTRO,
        sql="SELECT region_name_cyr, population FROM v_regions LIMIT 100",
        columns=columns,
        rows=rows,
        row_count=len(rows),
        user_question=user_question,
    )


# ---------- prompt construction ----------


def test_prompt_includes_rows_user_question_and_rules() -> None:
    res = _sql_result()
    p = build_narrator_prompt(res)
    assert "Qaysi viloyatda aholi ko'p?" in p
    assert "Andijon" in p
    assert "1234" in p
    assert "Uzbek Latin" in p
    assert "ma'lumot yo'q" in p
    # SQL is included only as hidden internal context.
    assert "INTERNAL CONTEXT" in p
    assert "v_regions" in p


def test_prompt_marks_extra_rows_as_truncated() -> None:
    rows = tuple((f"R{i}", i) for i in range(75))
    res = _sql_result(rows=rows)
    p = build_narrator_prompt(res, max_rows=50)
    assert "first 50 of 75 rows" in p


# ---------- deterministic narrator ----------


def test_deterministic_narrator_matches_compose_answer() -> None:
    res = _sql_result()
    a = DeterministicNarrator().narrate(res)
    assert a.kind == "sql_result"
    assert "| Andijon | 1234 |" in a.text


def test_deterministic_narrator_handles_conversational_kinds() -> None:
    greeting = QueryServiceResult(
        kind="greeting",
        user_message="Assalomu alaykum.",
        user_question="Salom",
    )
    a = DeterministicNarrator().narrate(greeting)
    assert a.kind == "greeting"
    assert a.text == "Assalomu alaykum."


# ---------- LLM narrator with stub provider ----------


def _settings_with_llm() -> Settings:
    return Settings(
        anthropic_api_key="test-key",
        llm_provider="anthropic",
        llm_model="claude-test",
        answer_narrator_mode="llm",
    )


def test_llm_narrator_returns_provider_text_when_safe() -> None:
    seen: dict[str, str] = {}

    def fake(model: str, prompt: str, api_key: str) -> str:
        seen["model"] = model
        seen["api_key"] = api_key
        return "Andijon viloyatida aholi soni 1234, Fargona viloyatida esa 5678."

    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=fake)
    a = nar.narrate(_sql_result())
    assert "Andijon" in a.text
    assert "1234" in a.text
    assert seen["api_key"] == "test-key"
    assert seen["model"] == "claude-test"


def test_llm_narrator_falls_back_when_output_invents_numbers() -> None:
    def fake(model: str, prompt: str, api_key: str) -> str:
        # 9999 is NOT in the result rows; safety check must reject.
        return "Aholi soni 9999 bo'ldi."

    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=fake)
    a = nar.narrate(_sql_result())
    # Falls back to deterministic markdown table.
    assert "| Andijon | 1234 |" in a.text


def test_llm_narrator_falls_back_when_output_leaks_internal_terms() -> None:
    def fake(model: str, prompt: str, api_key: str) -> str:
        return "Andijon: 1234, Fargona: 5678. Source: sql_guard view."

    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=fake)
    a = nar.narrate(_sql_result())
    assert "sql_guard" not in a.text.lower()
    assert "| Andijon | 1234 |" in a.text


def test_llm_narrator_falls_back_when_no_api_key() -> None:
    cfg = Settings(
        anthropic_api_key=None,
        openai_api_key=None,
        llm_provider="anthropic",
        llm_model="claude-test",
        answer_narrator_mode="llm",
    )
    nar = LlmNarrator(settings=cfg, provider_call=lambda *_: "irrelevant")
    a = nar.narrate(_sql_result())
    assert "| Andijon | 1234 |" in a.text


def test_llm_narrator_does_not_call_provider_for_conversational_kinds() -> None:
    calls = []

    def fake(*a):
        calls.append(a)
        return "should never be called"

    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=fake)
    res = QueryServiceResult(
        kind="greeting",
        user_message="Assalomu alaykum.",
        user_question="Salom",
    )
    a = nar.narrate(res)
    assert calls == []
    assert a.text == "Assalomu alaykum."


def test_llm_narrator_cannot_run_sql() -> None:
    """LlmNarrator only knows how to call a `ProviderCall` stub. It exposes
    no DB engine, no executor import, no SQL hook anywhere on its surface.
    """
    nar = LlmNarrator(settings=_settings_with_llm())
    for attr in ("_engine", "engine", "execute", "executor", "db", "session"):
        assert not hasattr(nar, attr), attr


# ---------- factory ----------


def test_factory_returns_deterministic_when_mode_default() -> None:
    nar = make_narrator_from_settings(Settings())
    assert isinstance(nar, DeterministicNarrator)


def test_factory_returns_llm_when_mode_is_llm() -> None:
    nar = make_narrator_from_settings(_settings_with_llm())
    assert isinstance(nar, LlmNarrator)
