"""Planner prompt: STRONG defaults steer ambiguous metric questions to
sql_plan; clarify user_message must never leak column names."""

from __future__ import annotations

from cerr_chatbot.query.evidence_planner import build_evidence_planner_prompt


def test_strong_defaults_block_present_for_common_metrics() -> None:
    p = build_evidence_planner_prompt("Andijon viloyatining tumanlar bo'yicha eng yuqori reyting o'rnini aytin")
    assert "STRONG defaults to AVOID clarify" in p
    # Each common KPI must have an explicit anti-clarify default.
    assert "reyting" in p and "rating_score" in p
    assert "aholi" in p and "population" in p
    assert "biznes" in p and "active_businesses" in p
    assert "ishsiz" in p and "unemployed" in p


def test_clarify_user_message_hygiene_rules_present() -> None:
    p = build_evidence_planner_prompt("x")
    assert "user_message hygiene for clarify" in p
    # The hygiene block forbids column names + snake_case + SQL terms.
    assert "MUST NOT mention any column name" in p
    assert "snake_case identifier" in p


def test_clarify_anti_pattern_example_shown() -> None:
    """The few-shot must include a WRONG clarify message that surfaces
    `rating_score` / `district_rank_text`, so the model is explicitly
    taught not to do this."""
    p = build_evidence_planner_prompt("x")
    assert "WRONG clarify message" in p
    assert "rating_score" in p
    assert "district_rank_text" in p


def test_district_ranking_few_shot_uses_sql_plan_not_clarify() -> None:
    """The new EXAMPLE D0 must show the rating-by-district question routed
    to sql_plan with rating_score + region_rank_text in the SELECT."""
    p = build_evidence_planner_prompt("x")
    assert "EXAMPLE D0" in p
    assert "rating_score" in p
    assert "region_rank_text" in p
    # And it must use sql_plan, not clarify.
    # Crude but effective: the kind: sql_plan line follows the example header.
    idx = p.index("EXAMPLE D0")
    snippet = p[idx : idx + 600]
    assert '"kind": "sql_plan"' in snippet


def test_user_question_pasted_verbatim() -> None:
    q = "Andijon viloyatining tumanlar bo'yicha eng yuqori reyting o'rnini aytin"
    p = build_evidence_planner_prompt(q)
    assert q in p
