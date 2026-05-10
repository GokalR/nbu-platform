"""Scorer's required / optional-derived / forbidden three-way model."""

from __future__ import annotations

from cerr_chatbot.eval.scorer import score_case


def test_extra_derived_numbers_in_actual_do_not_fail() -> None:
    """Analyst-style derived insight (33.3%) is not in expected; must not fail."""
    expected = "A: 4000, B: 3000."
    actual = "A: 4000. B: 3000. A B dan 1000 ga, ya'ni 33.3% ko'p."
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_required_source_fact_still_required() -> None:
    expected = "A: 4000, B: 3000."
    actual = "A: 4000."  # 3000 missing
    passed, reasons = score_case(expected, "sql_result", actual)
    assert not passed
    assert any("3000" in r for r in reasons)


def test_forbidden_fact_blocks() -> None:
    expected = "A: 4000."
    actual = "A: 4000. Aholi soni o'sha viloyatda 9999 ga yetdi."
    passed, reasons = score_case(
        expected,
        "sql_result",
        actual,
        forbidden_facts=("9999",),
    )
    assert not passed
    assert any("forbidden" in r and "9999" in r for r in reasons)


def test_forbidden_fact_absent_passes() -> None:
    expected = "A: 4000."
    actual = "A: 4000. Top-1 sifatida ajralib turadi."
    passed, _ = score_case(
        expected,
        "sql_result",
        actual,
        forbidden_facts=("9999",),
    )
    assert passed
