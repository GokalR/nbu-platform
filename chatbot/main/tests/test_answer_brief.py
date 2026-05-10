"""AnswerBrief classifier + narrator prompt integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cerr_chatbot.query.answer_brief import (
    AnswerBrief,
    build_answer_brief,
    render_brief_for_prompt,
)
from cerr_chatbot.query.evidence import EvidencePack, EvidenceQueryResult
from cerr_chatbot.query.evidence_narrator import build_evidence_prompt


@dataclass
class _StubResult:
    rows: tuple = ()
    row_count: int = 0
    columns: tuple = ()
    error: str | None = None
    purpose: str = "primary"
    sql: str | None = None


def _primary(row_count: int) -> _StubResult:
    rows: tuple = tuple((f"R{i}", i) for i in range(row_count))
    return _StubResult(
        rows=rows,
        row_count=row_count,
        columns=("name", "value"),
        purpose="primary",
        sql="SELECT name, value FROM v_x",
    )


# ---------- classification ----------


def test_exact_lookup_one_row_count_question() -> None:
    q = (
        "Qoraqalpog'iston Respublikasi Amudaryo tumanida mahallalar soni va "
        "kambag'al oilalar soni qancha?"
    )
    brief = build_answer_brief(q, _primary(1))
    assert brief.answer_type == "exact_lookup"


def test_exact_lookup_blocks_only_useless_single_row_artefacts() -> None:
    """Brief is advisory now: only the truly useless single-row artefacts
    are forbidden. Ratios / density / interpretation / context comparison
    are encouraged for richer answers."""
    brief = build_answer_brief("Toshkent shahri aholi soni qancha?", _primary(1))
    forbidden = set(brief.forbidden_insight_modes)
    assert "100_percent_of_shown_result" in forbidden
    assert "highest_and_lowest_are_the_same" in forbidden
    assert "gap_is_zero" in forbidden
    # Ranking against rows not returned stays forbidden — narrator should
    # not invent peers — but share/comparison/ratio are now ALLOWED.
    assert "ranking_against_rows_that_were_not_returned" in forbidden

    allowed = set(brief.allowed_insight_modes)
    # The user explicitly asked for richer answers: density / ratio /
    # interpretation / context comparison must be on the menu.
    assert "ratio_between_returned_values" in allowed
    assert "density_per_unit_using_returned_values" in allowed
    assert "practical_interpretation" in allowed
    assert "comparison_to_context_if_context_rows_exist" in allowed


def test_top_n_ranking_classification() -> None:
    q = "Qoraqalpog'iston Respublikasida ishsizlar soni eng ko'p 5 hudud qaysi?"
    brief = build_answer_brief(q, _primary(5))
    assert brief.answer_type == "top_n_ranking"
    allowed = set(brief.allowed_insight_modes)
    assert "gap_first_to_second" in allowed
    assert "share_of_total_if_context_has_total" in allowed
    assert "concentration_if_top_n_sum_available" in allowed


def test_top_n_with_only_one_row_falls_to_exact_lookup() -> None:
    """`eng yuqori` keyword present, but only 1 row → no ranking to discuss."""
    brief = build_answer_brief("Eng yuqori aholi qaysi viloyatda?", _primary(1))
    assert brief.answer_type == "exact_lookup"


def test_data_quality_classification() -> None:
    brief = build_answer_brief(
        "Ma'lumotlarda takror STIR bormi?",
        _primary(3),
    )
    assert brief.answer_type == "data_quality"
    forbidden = set(brief.forbidden_insight_modes)
    assert "claim_issues_fixed" in forbidden
    assert "deduping_language" in forbidden


def test_no_rows_classification() -> None:
    brief = build_answer_brief(
        "Marg'ilon shahridagi Yoyilma mahallasining kuchli tomonlari",
        _primary(0),
    )
    assert brief.answer_type == "no_rows"
    allowed = set(brief.allowed_insight_modes)
    assert "say_no_data_found" in allowed
    forbidden = set(brief.forbidden_insight_modes)
    assert "ranking" in forbidden
    assert "invented_alternatives" in forbidden


def test_entity_profile_classification() -> None:
    brief = build_answer_brief(
        "Yoyilma mahallasining kuchli tomonlari",
        _primary(8),
    )
    assert brief.answer_type == "entity_profile"
    allowed = set(brief.allowed_insight_modes)
    assert "strongest_signals" in allowed
    assert "missing_values_note" in allowed


def test_distribution_classification() -> None:
    brief = build_answer_brief(
        "Har bir specialization toifasida nechta mahalla bor?",
        _primary(7),
    )
    assert brief.answer_type == "distribution"
    allowed = set(brief.allowed_insight_modes)
    assert "category_counts" in allowed
    assert "largest_category" in allowed


def test_comparison_classification() -> None:
    brief = build_answer_brief(
        "Andijon viloyati va Farg'ona viloyati aholisi farqi qancha?",
        _primary(2),
    )
    assert brief.answer_type == "comparison"
    allowed = set(brief.allowed_insight_modes)
    assert "difference" in allowed
    assert "percent_difference" in allowed


def test_generic_fallback() -> None:
    """Vague analytical question, no specific keywords, multi-row result."""
    brief = build_answer_brief(
        "Viloyatlarning iqtisodiy ko'rsatkichlarini ko'rib chiqing",
        _primary(10),
    )
    # No `qancha`/`nechta` keyword present, no ranking/comparison/etc keyword,
    # so fallback to generic_analytical.
    assert brief.answer_type == "generic_analytical"


# ---------- narrator prompt integration ----------


def _pack(question: str, primary: _StubResult) -> EvidencePack:
    real_primary = EvidenceQueryResult(
        purpose=primary.purpose,
        sql=primary.sql,
        columns=primary.columns,
        rows=primary.rows,
        row_count=primary.row_count,
    )
    return EvidencePack(question=question, primary=real_primary, context=())


def _ctx(purpose: str, value: Any) -> EvidenceQueryResult:
    return EvidenceQueryResult(
        purpose=purpose,
        sql=f"SELECT {purpose} FROM v_x",
        columns=("v",),
        rows=((value,),),
        row_count=1,
    )


def test_prompt_contains_answer_brief_section_for_exact_lookup() -> None:
    pack = _pack(
        "Toshkent shahri aholi soni qancha?",
        _primary(1),
    )
    prompt = build_evidence_prompt(pack)
    assert "ANSWER BRIEF" in prompt
    assert "answer_type: exact_lookup" in prompt
    # Brief is advisory now; the only hard exclusions are the useless
    # single-row artefacts. Their wording must be visible to the model.
    assert "100% of shown" in prompt
    assert "highest" in prompt and "lowest are the same" in prompt
    assert "gap is 0" in prompt


def test_prompt_contains_top_n_ranking_permissions() -> None:
    pack = _pack(
        "Qoraqalpog'istonda ishsizlar soni eng ko'p 5 hudud qaysi?",
        _primary(5),
    )
    prompt = build_evidence_prompt(pack)
    assert "answer_type: top_n_ranking" in prompt
    # Allowed insight modes appear so the LLM knows what is fair game.
    assert "gap_first_to_second" in prompt
    assert "share_of_total_if_context_has_total" in prompt
    # Brief is advisory: insight policy must encourage reasoning, not gate it.
    assert "Reason from the evidence" in prompt
    assert "advisory" in prompt


def test_prompt_contains_no_rows_branch_for_empty_primary() -> None:
    pack = _pack("Yoyilma mahallasining kuchli tomonlari", _primary(0))
    prompt = build_evidence_prompt(pack)
    assert "answer_type: no_rows" in prompt
    assert "say_no_data_found" in prompt
    # No-rows case: ranking must be in forbidden list.
    assert "forbidden_insight_modes" in prompt
    assert "ranking" in prompt


def test_prompt_still_includes_hard_hygiene_rules() -> None:
    """ANSWER BRIEF additions must not displace the hard hygiene rules."""
    pack = _pack("Toshkent shahri aholi soni qancha?", _primary(1))
    prompt = build_evidence_prompt(pack)
    # NULL → ma'lumot yo'q rule still present.
    assert "Never use 0 for a missing value" in prompt or "NEVER use 0" in prompt
    # Snake-case ban still present.
    assert "snake_case identifiers" in prompt
    # No-internals rule still present.
    assert "NEVER mention SQL" in prompt
    # Transliteration rule still present.
    assert "transliterate" in prompt


# ---------- render_brief_for_prompt ----------


def test_render_brief_emits_all_fields() -> None:
    brief = AnswerBrief(
        answer_type="generic_analytical",
        user_goal="Test",
        allowed_insight_modes=("a", "b"),
        forbidden_insight_modes=("c",),
        style_rules=("rule1", "rule2"),
        reason="testing",
    )
    out = render_brief_for_prompt(brief)
    assert "answer_type: generic_analytical" in out
    assert "user_goal: Test" in out
    assert "allowed_insight_modes: a, b" in out
    assert "forbidden_insight_modes: c" in out
    assert "* rule1" in out
    assert "* rule2" in out
    assert "reason: testing" in out


def test_render_brief_handles_empty_collections() -> None:
    brief = AnswerBrief(answer_type="no_rows", user_goal="x")
    out = render_brief_for_prompt(brief)
    assert "allowed_insight_modes: (none)" in out
    assert "forbidden_insight_modes: (none)" in out
    assert "* (none)" in out
