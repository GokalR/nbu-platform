"""LLM evidence narrator: trusts reasoning, only soft safety."""

from __future__ import annotations

import json

from cerr_chatbot.config import Settings
from cerr_chatbot.query.answer import NULL_DISPLAY
from cerr_chatbot.query.evidence import (
    EvidencePack,
    EvidenceQueryResult,
    EvidenceServiceResult,
)
from cerr_chatbot.query.evidence_narrator import (
    EvidenceLlmNarrator,
    build_evidence_prompt,
)


def _llm_settings() -> Settings:
    return Settings(
        anthropic_api_key="test-key",
        llm_provider="anthropic",
        llm_model="claude-test",
    )


def _pack(
    rows=(("Andijon", 1234), ("Fargona", 5678)),
    columns=("region_name_cyr", "population"),
    question="Top viloyatlar?",
    context: tuple[EvidenceQueryResult, ...] = (),
) -> EvidencePack:
    primary = EvidenceQueryResult(
        purpose="primary",
        sql="SELECT region_name_cyr, population FROM v_regions LIMIT 100",
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )
    return EvidencePack(question=question, primary=primary, context=context)


def _result(pack: EvidencePack) -> EvidenceServiceResult:
    return EvidenceServiceResult(kind="sql_result", user_message="Natijani topdim.", pack=pack)


# ---------- prompt construction ----------


def test_prompt_contains_primary_and_context_blocks() -> None:
    ctx = (
        EvidenceQueryResult(
            purpose="avg population",
            sql="SELECT AVG(population) FROM v_regions",
            columns=("avg_pop",),
            rows=((3456,),),
            row_count=1,
        ),
        EvidenceQueryResult(
            purpose="total regions",
            sql="SELECT COUNT(*) FROM v_regions",
            columns=("n",),
            rows=((14,),),
            row_count=1,
        ),
    )
    prompt = build_evidence_prompt(_pack(context=ctx))
    assert "Top viloyatlar?" in prompt
    assert "## primary" in prompt
    assert "Andijon" in prompt
    # Numbers are pre-formatted before they reach the LLM.
    assert "1,234" in prompt
    assert "## avg population" in prompt
    assert "3,456" in prompt
    assert "## total regions" in prompt
    assert "NEVER mention SQL" in prompt
    assert '"answer_markdown"' in prompt
    # Pre-computed metrics block is now part of the prompt contract.
    assert "PRE-COMPUTED METRICS" in prompt


def test_prompt_requires_cyrillic_names_transliterated_to_uzbek_latin() -> None:
    prompt = build_evidence_prompt(
        _pack(rows=(("Самарқанд вилояти", 1234),), question="Aholi qancha?")
    )

    assert "transliterate" in prompt
    assert "Do not show" in prompt
    assert "Cyrillic names" in prompt
    assert "Samarqand" in prompt
    assert "viloyati" in prompt
    assert "Marg'ilon shahri" in prompt
    assert "Source entity names stay in Cyrillic" not in prompt


def test_prompt_marks_unavailable_context_query() -> None:
    ctx = (EvidenceQueryResult(purpose="bad", sql=None, error="sql_guard: SELECT * blocked"),)
    prompt = build_evidence_prompt(_pack(context=ctx))
    assert "## bad" in prompt
    assert "(unavailable" in prompt


# ---------- happy path: reasoning is trusted ----------


def test_narrator_accepts_pre_computed_metrics() -> None:
    """The narrator may quote any number from PRE-COMPUTED METRICS — gap,
    pct-diff, ratio — but cannot invent values not in evidence/metrics."""
    captured: dict[str, str] = {}

    def fake(model: str, prompt: str, api_key: str) -> str:
        captured["prompt"] = prompt
        # gap_first_to_second_abs == |1234 - 5678| == 4,444 (pre-formatted)
        return "Andijon (1,234) va Fargona (5,678) viloyatlari taqqoslandi. Farqi 4,444 kishi."

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert "1,234" in a.text
    assert "5,678" in a.text
    assert "4,444" in a.text  # derived gap from PRE-COMPUTED METRICS
    assert "Andijon" in captured["prompt"]


def test_narrator_unwraps_json_text_envelope() -> None:
    def fake(*_):
        return json.dumps(
            {"text": ("Andijon (1234) va Fargona (5678) taqqoslandi. Fargona ancha yuqori.")}
        )

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert a.text.startswith("Andijon")
    assert '{"text"' not in a.text
    assert "1234" in a.text


def test_narrator_unwraps_json_output_envelope() -> None:
    def fake(*_):
        return json.dumps({"output": "Andijon (1234) va Fargona (5678) taqqoslandi."})

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert a.text == "Andijon (1234) va Fargona (5678) taqqoslandi."
    assert '{"output"' not in a.text


def test_narrator_unwraps_answer_markdown_contract() -> None:
    def fake(*_):
        return json.dumps({"answer_markdown": "**Andijon**: 1234."})

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert a.text == "**Andijon**: 1234."


def test_narrator_unwraps_fenced_json_answer_envelope() -> None:
    def fake(*_):
        return "```json\n" + json.dumps({"answer": "Andijon: 1234."}) + "\n```"

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert a.text == "Andijon: 1234."


def test_narrator_scratchpad_tail_triggers_full_fallback() -> None:
    """Earlier we trimmed scratchpad tails; now any marker hard-fallbacks.

    Reason: when the model goes into 'wait/let me compute' mode, the prefix
    is almost always wrong too (the screenshot 3 incident). Better to ship
    the deterministic table than half-broken prose."""

    def fake(*_):
        return (
            "Andijon (1234) va Fargona (5678) ko'rsatildi. "
            "Fargona yuqoriroq. Wait incorrect. Need sum. Let's compute..."
        )

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert "Wait" not in a.text
    assert "Need sum" not in a.text
    # Hard fallback → deterministic table.
    assert "| Andijon | 1,234 |" in a.text


def test_narrator_scratchpad_only_falls_back() -> None:
    def fake(*_):
        return "Wait incorrect. Need sum. Let's compute first."

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert "Wait incorrect" not in a.text
    assert "| Andijon | 1,234 |" in a.text


def test_narrator_passes_context_evidence_to_llm() -> None:
    seen: dict[str, str] = {}

    def fake(model: str, prompt: str, api_key: str) -> str:
        seen["prompt"] = prompt
        return "Andijon eng yuqori (1,234), bu o'rtacha (3,456) dan past."

    ctx = (
        EvidenceQueryResult(
            purpose="avg population",
            sql="SELECT AVG(population) FROM v_regions",
            columns=("avg_pop",),
            rows=((3456,),),
            row_count=1,
        ),
    )
    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack(context=ctx)))
    # Numbers reach the LLM already formatted with thousands separators.
    assert "3,456" in seen["prompt"]
    assert "3,456" in a.text


# ---------- soft NULL→0 check ----------


def test_null_marker_preserved_when_llm_emits_it() -> None:
    rows = (("Surxondaryo", None),)

    def fake(*_):
        return f"Surxondaryo aholisi: {NULL_DISPLAY}."

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack(rows=rows)))
    assert NULL_DISPLAY in a.text


def test_null_to_zero_no_longer_triggers_automatic_fallback() -> None:
    """NULL → ma'lumot yo'q is now a PROMPT rule only. We do not trigger an
    automatic fallback when the LLM still emits `0`. Tradeoff: tighter
    advisory, but no quality wall on the narrator's reasoning."""
    rows = (("Surxondaryo", None),)
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: "Surxondaryo aholisi: 0.",
    )
    a = nar.narrate(_result(_pack(rows=rows)))
    # Narrator output is preserved verbatim (after transliteration).
    assert a.text == "Surxondaryo aholisi: 0."
    # No deterministic fallback table.
    assert "Qaytarilgan qatorlar" not in a.text


# ---------- internal-term hard fallback ----------


def test_internal_term_leak_falls_back_to_deterministic() -> None:
    def fake(*_):
        return "Andijon: 1234. Source: sql_guard view."

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack()))
    assert "sql_guard" not in a.text.lower()
    assert "| Andijon | 1,234 |" in a.text


# ---------- non-sql_result paths ----------


def test_conversational_kinds_pass_through_unchanged() -> None:
    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=lambda *_: "x")
    res = EvidenceServiceResult(kind="greeting", user_message="Assalomu alaykum.")
    a = nar.narrate(res)
    assert a.text == "Assalomu alaykum."
    assert a.kind == "greeting"


def test_no_api_key_falls_back_to_deterministic() -> None:
    cfg = Settings(
        anthropic_api_key=None,
        openai_api_key=None,
        llm_provider="anthropic",
        llm_model="claude-test",
    )
    nar = EvidenceLlmNarrator(settings=cfg, provider_call=lambda *_: "irrelevant")
    a = nar.narrate(_result(_pack()))
    assert "| Andijon | 1,234 |" in a.text


# ---------- source values not modified ----------


def test_source_value_passed_verbatim_when_llm_repeats_it() -> None:
    rows = (("Toshkent", 3110987),)

    def fake(*_):
        return "Toshkent aholisi 3110987 kishi."

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack(rows=rows)))
    assert "3110987" in a.text


# ---------- Cyrillic source names ----------


def test_cyrillic_source_names_transliterated_to_latin() -> None:
    """Server-side transliteration runs after the LLM reply: Cyrillic in
    the model output is converted to Uzbek Latin before reaching the user.
    Numbers and Latin tokens pass through unchanged."""
    rows = (("Самарқанд", 4012345),)

    def fake(*_):
        return "Самарқанд viloyatida 4012345 kishi yashaydi va eng katta hisoblanadi."

    nar = EvidenceLlmNarrator(settings=_llm_settings(), provider_call=fake)
    a = nar.narrate(_result(_pack(rows=rows)))
    assert "Самарқанд" not in a.text
    assert "Samarqand viloyatida" in a.text
    assert "4012345" in a.text
