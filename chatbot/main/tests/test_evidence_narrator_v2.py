"""Hardened evidence narrator: pre-formatted rows, derived metrics, hygiene."""

from __future__ import annotations

import json

from cerr_chatbot.config import Settings
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


def _primary(
    rows=(("Самарқанд вилояти", 4330143), ("Фарғона вилояти", 4204055)),
    columns=("region_name_cyr", "population"),
):
    return EvidenceQueryResult(
        purpose="primary",
        sql="SELECT region_name_cyr, population FROM v_regions LIMIT 100",
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )


def _pack(
    primary: EvidenceQueryResult | None = None,
    context: tuple[EvidenceQueryResult, ...] = (),
    question: str = "Top viloyatlar?",
) -> EvidencePack:
    return EvidencePack(
        question=question,
        primary=primary or _primary(),
        context=context,
    )


def _result(pack: EvidencePack) -> EvidenceServiceResult:
    return EvidenceServiceResult(kind="sql_result", user_message="Natijani topdim.", pack=pack)


def _envelope(text: str) -> str:
    return json.dumps({"answer_markdown": text})


# ---------- prompt now ships formatted numbers + metrics block ----------


def test_prompt_serializes_numbers_already_formatted() -> None:
    pack = _pack(primary=_primary(rows=(("Самарқанд вилояти", 67611.4667952569),)))
    prompt = build_evidence_prompt(pack)
    assert "67,611.47" in prompt  # formatted
    assert "67611.4667952569" not in prompt  # raw float never reaches LLM


def test_prompt_includes_pre_computed_metrics_block() -> None:
    pack = _pack(
        primary=_primary(
            rows=(
                ("Самарқанд вилояти", 4330143),
                ("Фарғона вилояти", 4204055),
                ("Қашқадарё вилояти", 3591291),
            )
        ),
        context=(
            EvidenceQueryResult(
                purpose="average population",
                sql="SELECT AVG(population) FROM v_regions",
                columns=("avg_pop",),
                rows=((2681526.7,),),
                row_count=1,
            ),
        ),
    )
    prompt = build_evidence_prompt(pack)
    assert "PRE-COMPUTED METRICS" in prompt
    assert "first_row_label: Самарқанд вилояти" in prompt
    assert "gap_first_to_second_abs: 126,088" in prompt
    assert "context.average_population: 2,681,526.7" in prompt


# ---------- the screenshot 3 regression: 187,826,735 must NOT pass ----------


def test_invented_grand_total_falls_back_to_table() -> None:
    pack = _pack(
        primary=_primary(
            rows=(
                ("Самарқанд вилояти", 4330143),
                ("Фарғона вилояти", 4204055),
                ("Қашқадарё вилояти", 3591291),
                ("Андижон вилояти", 3479657),
                ("Тошкент шаҳри", 3177589),
            )
        ),
    )
    bad = (
        "Бу 5 hududning jami aholisi 187,826,735 emas, balki hisob-kitobga ko'ra 187,826,735? Wait."
    )
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope(bad),
    )
    a = nar.narrate(_result(pack))
    # Both invented number AND scratchpad marker → fallback table.
    assert "187,826,735" not in a.text
    assert "Wait" not in a.text
    # Fallback table is also transliterated to Uzbek Latin server-side.
    assert "| Samarqand viloyati | 4,330,143 |" in a.text


# ---------- the screenshot 2 regression: rating_score leak must NOT pass ----


def test_snake_case_column_leak_falls_back() -> None:
    pack = _pack(
        primary=_primary(
            rows=(("Беруний", 0.0), ("Оқработ", 0.0)),
            columns=("mahalla_name_cyr", "rating_score"),
        ),
    )
    bad = "Eng past reytingli mahallalarda rating_score = 0.0."
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope(bad),
    )
    a = nar.narrate(_result(pack))
    # Narrator's invented prose with the snake_case leak is gone.
    assert "Eng past reytingli mahallalarda" not in a.text
    # Fallback markdown still serves the user the data table, with readable headers.
    assert "rating_score" not in a.text
    # Fallback table is transliterated server-side.
    assert "| Beruniy | 0 |" in a.text


# ---------- think-aloud markers always block ----------


def test_wait_marker_falls_back() -> None:
    pack = _pack()
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope("Wait, let me reconsider. Самарқанд: 4,330,143."),
    )
    a = nar.narrate(_result(pack))
    assert "Wait" not in a.text


def test_actually_marker_falls_back() -> None:
    pack = _pack()
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope("Actually, the answer is 4,330,143."),
    )
    a = nar.narrate(_result(pack))
    assert "Actually" not in a.text


# ---------- happy path: derived percentages from metrics are accepted ----------


def test_answer_quoting_pre_computed_metrics_passes_grounding() -> None:
    pack = _pack(
        primary=_primary(
            rows=(
                ("Самарқанд вилояти", 4330143),
                ("Фарғона вилояти", 4204055),
            )
        ),
    )
    # Самарқанд - Фарғона = 126,088 (matches gap_first_to_second_abs)
    good = (
        "Самарқанд вилояти eng katta — 4,330,143 kishi. Bu Фарғона вилоятидан 126,088 kishiga ko'p."
    )
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope(good),
    )
    a = nar.narrate(_result(pack))
    assert "126,088" in a.text
    # Cyrillic in LLM output is transliterated server-side.
    assert "Самарқанд" not in a.text
    assert "Samarqand viloyati" in a.text
    assert "Farg'ona" in a.text


def test_answer_with_context_baseline_pct_passes() -> None:
    primary = _primary(rows=(("Самарқанд вилояти", 4330143),))
    ctx = (
        EvidenceQueryResult(
            purpose="avg population",
            sql="SELECT AVG(population) FROM v_regions",
            columns=("avg_pop",),
            rows=((2681526.7,),),
            row_count=1,
        ),
    )
    pack = _pack(primary=primary, context=ctx)
    # cross-metric: first_vs_avg_population_pct_diff ≈ 61.5
    good = "Самарқанд вилояти o'rtachadan taxminan 61.5% yuqori (4,330,143 kishi)."
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope(good),
    )
    a = nar.narrate(_result(pack))
    assert "61.5%" in a.text
    assert "4,330,143" in a.text


# ---------- NULL preserved ----------


def test_null_marker_preserved() -> None:
    pack = _pack(primary=_primary(rows=(("Surxondaryo", None),)))
    nar = EvidenceLlmNarrator(
        settings=_llm_settings(),
        provider_call=lambda *_: _envelope("Surxondaryo aholisi: ma'lumot yo'q."),
    )
    a = nar.narrate(_result(pack))
    assert "ma'lumot yo'q" in a.text
