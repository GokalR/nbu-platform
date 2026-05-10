"""Planner prompt loosens clarify; favors sql_plan with LIKE search."""

from __future__ import annotations

from cerr_chatbot.query.evidence_planner import build_evidence_planner_prompt


def _prompt() -> str:
    # Question content does not affect the rendered policy block — any
    # question reaches the same rules section.
    return build_evidence_planner_prompt(
        "Marg'ilon shahridagi Yoyilma mahallasining kuchli tomonlari"
    )


def test_prompt_documents_prefer_sql_plan_default() -> None:
    p = _prompt()
    assert "PREFER sql_plan" in p
    assert "This is the DEFAULT" in p


def test_prompt_lists_explicit_clarify_conditions_only() -> None:
    p = _prompt()
    # Clarify is now LAST RESORT. The three (and only three) acceptable
    # clarify reasons must still be enumerated.
    assert "LAST RESORT" in p
    assert "(a)" in p and "metric that does not exist" in p
    assert "(b)" in p and "no metric is" in p
    assert "(c)" in p and "multiple distinct entity types" in p.lower()
    # Anti-pattern: do not clarify on mixed-script place name.
    # (Wording wraps across lines in the prompt; check fragments.)
    assert "NEVER" in p and "clarify spelling" in p


def test_prompt_explains_like_name_matching_strategy() -> None:
    p = _prompt()
    assert "LIKE" in p
    assert "region_name_cyr" in p
    assert "district_name_cyr" in p
    assert "mahalla_name_cyr" in p
    # JOINs still go through surrogate ids.
    assert "Do NOT JOIN on" in p
    # 0 rows → answer no rows, do not clarify.
    assert "0 rows" in p
    assert "pre-emptively clarify" in p.lower()


def test_prompt_documents_strengths_pattern_with_peer_factors_view() -> None:
    p = _prompt()
    assert "v_mahalla_peer_factors" in p
    assert "factor_polarity = 'strength'" in p
    assert "factor_polarity = 'weakness'" in p
    assert "factor_label_cyr" in p
    assert "percentile" in p
    assert "factor_order" in p


def test_few_shot_includes_marg_yoyilma_strengths_example() -> None:
    p = _prompt()
    # Latin fragments stemmed to Cyrillic LIKE patterns.
    assert "Йойилма" in p
    assert "Ёйилма" in p
    assert "Марғ" in p and "Марг" in p
    # Joins via surrogate id, not via name.
    assert "ON m.mahalla_id = p.mahalla_id" in p


def test_few_shot_clarify_example_remains_for_truly_vague_questions() -> None:
    p = _prompt()
    # The "vague kuchli tomonlari" example must still exist as the clarify
    # branch (no entity, no metric).
    assert "EXAMPLE E - clarify" in p
    assert "joy nomini kiriting" in p


def test_user_question_pasted_verbatim() -> None:
    p = build_evidence_planner_prompt("Marg'ilon shahridagi Yoyilma mahallasining kuchli tomonlari")
    assert "Marg'ilon shahridagi Yoyilma mahallasining kuchli tomonlari" in p
