"""End-to-end LlmNarrator with derived-calc envelope.

All LLM calls are stubbed. Verifies:
  1. Derived percentages/totals from envelope are accepted.
  2. Source numbers are not rewritten by the safety layer.
  3. NULL stays as `ma'lumot yo'q`, never 0.
  4. Invented numbers fall back to deterministic.
  5. Final answer is richer than the raw markdown table.
  6. Cyrillic source names pass through unchanged.
"""

from __future__ import annotations

import json

from cerr_chatbot.config import Settings
from cerr_chatbot.query.answer import NULL_DISPLAY
from cerr_chatbot.query.narrator import LlmNarrator
from cerr_chatbot.query.service import (
    SQL_RESULT_GENERIC_INTRO,
    QueryServiceResult,
)


def _settings_with_llm() -> Settings:
    return Settings(
        anthropic_api_key="test-key",
        llm_provider="anthropic",
        llm_model="claude-test",
        answer_narrator_mode="llm",
    )


def _result(rows, columns=("region_name_cyr", "population"), question="Top viloyatlar"):
    return QueryServiceResult(
        kind="sql_result",
        user_message=SQL_RESULT_GENERIC_INTRO,
        sql="SELECT region_name_cyr, population FROM v_regions LIMIT 100",
        columns=columns,
        rows=rows,
        row_count=len(rows),
        user_question=question,
    )


def _envelope(answer: str, derived: list[dict]) -> str:
    return json.dumps({"answer": answer, "derived_calculations": derived})


# 1. Derived percentage from rows is accepted.
def test_derived_percentage_accepted() -> None:
    rows = (("A", 4000), ("B", 3000), ("C", 1000))
    payload = _envelope(
        "A eng katta: 4000 kishi. B dan 1000 kishiga, ya'ni 33.3% ko'p.",
        [
            {"output_value": "1000", "formula": "4000 - 3000", "input_values": [4000, 3000]},
            {
                "output_value": "33.3",
                "formula": "(4000 - 3000) / 3000 * 100",
                "input_values": [4000, 3000],
            },
        ],
    )
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    assert "33.3" in a.text
    assert "1000" in a.text
    assert "4000" in a.text


# 2. Source numbers are not changed by safety layer.
def test_source_numbers_pass_through_verbatim() -> None:
    rows = (("Toshkent", 3110987),)
    payload = _envelope(
        "Toshkent aholisi 3110987 kishi.",
        [],
    )
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    assert "3110987" in a.text


# 3. NULL is rendered as marker, never as 0.
def test_null_stays_as_missing_marker() -> None:
    rows = (("Surxondaryo", None),)
    payload = _envelope(
        f"Surxondaryo aholisi: {NULL_DISPLAY}.",
        [],
    )
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    assert NULL_DISPLAY in a.text
    # Make sure no stray " 0 " token slipped in.
    assert " 0 " not in f" {a.text} "


# 4. Invented unrelated number triggers deterministic fallback.
def test_invented_number_triggers_fallback() -> None:
    rows = (("A", 4000), ("B", 3000))
    payload = _envelope("A iqtisodi 9999 birlik.", [])
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    # Fallback emits the deterministic markdown table; 9999 must not appear.
    assert "9999" not in a.text
    assert "| A | 4000 |" in a.text


# 4b. A derived calc whose output does NOT match its formula must not
#    legitimize the number it claims; the answer falls back.
def test_inconsistent_derived_calc_does_not_legitimize_number() -> None:
    rows = (("A", 4000), ("B", 3000))
    payload = _envelope(
        "A: 50% ko'p.",
        # 50 is the wrong output for (4000-3000)/3000*100 (~33.3) → calc fails.
        [
            {
                "output_value": "50",
                "formula": "(4000 - 3000) / 3000 * 100",
                "input_values": [4000, 3000],
            }
        ],
    )
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    assert "50%" not in a.text
    assert "| A | 4000 |" in a.text  # deterministic fallback table


# 5. Final answer is richer than the raw table.
def test_envelope_answer_richer_than_raw_table() -> None:
    rows = (("A", 4000), ("B", 3000), ("C", 1000))
    payload = _envelope(
        "A eng yuqori (4000), B (3000) dan 1000 ga ko'p, C (1000) eng past.",
        [{"output_value": "1000", "formula": "4000 - 3000", "input_values": [4000, 3000]}],
    )
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    # No raw markdown table envelope produced by deterministic composer:
    assert "| region_name_cyr | population |" not in a.text
    # Has analyst-style prose with comparison wording:
    assert "ko'p" in a.text or "past" in a.text
    # Numbers preserved exactly.
    for n in ("4000", "3000", "1000"):
        assert n in a.text


# 6. Cyrillic source names pass through unchanged.
def test_cyrillic_names_unchanged() -> None:
    rows = (("Самарқанд", 4012345),)
    payload = _envelope("Самарқанд viloyatida 4012345 kishi yashaydi.", [])
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    assert "Самарқанд" in a.text
    assert "4012345" in a.text


# 7. Plain-text replies (no envelope) still work for back-compat —
#    strict v1 path requires every number to be a row value.
def test_plain_text_fallback_path_still_strict() -> None:
    rows = (("A", 4000),)
    nar = LlmNarrator(
        settings=_settings_with_llm(),
        provider_call=lambda *_: "A viloyatida 4000 kishi yashaydi.",
    )
    a = nar.narrate(_result(rows))
    assert "4000" in a.text


def test_plain_text_with_invented_number_falls_back() -> None:
    rows = (("A", 4000),)
    nar = LlmNarrator(
        settings=_settings_with_llm(),
        provider_call=lambda *_: "A viloyatida 9999 kishi yashaydi.",
    )
    a = nar.narrate(_result(rows))
    assert "9999" not in a.text
    assert "| A | 4000 |" in a.text


# 8. Internal-term leak in envelope still triggers fallback.
def test_envelope_with_internal_terms_falls_back() -> None:
    rows = (("A", 4000),)
    payload = _envelope("A: 4000. Source: sql_guard view.", [])
    nar = LlmNarrator(settings=_settings_with_llm(), provider_call=lambda *_: payload)
    a = nar.narrate(_result(rows))
    assert "sql_guard" not in a.text.lower()
    assert "| A | 4000 |" in a.text


# 9. Prompt instructs LLM to return JSON envelope.
def test_prompt_asks_for_envelope_with_few_shot() -> None:
    from cerr_chatbot.query.narrator import build_narrator_prompt

    p = build_narrator_prompt(_result((("A", 4000),)))
    assert "derived_calculations" in p
    assert "input_values" in p
    assert "33.3" in p  # few-shot example
    assert "ma'lumot yo'q" in p
