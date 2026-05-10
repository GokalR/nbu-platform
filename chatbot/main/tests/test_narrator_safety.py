"""AST safe-eval, envelope parsing, and verify_calculation."""

from __future__ import annotations

import json

import pytest

from cerr_chatbot.query.narrator_safety import (
    DerivedCalc,
    EnvelopeParseError,
    extract_row_numbers,
    is_answer_grounded,
    parse_envelope,
    safe_eval_formula,
    verify_calculation,
)

# ---------- safe_eval_formula ----------


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("4000 - 3000", 1000.0),
        ("(4000 - 3000) / 3000 * 100", pytest.approx(33.3333, rel=1e-4)),
        ("4000 + 3000 + 1000", 8000.0),
        ("4000 / (4000 + 3000 + 1000) * 100", 50.0),
        ("-5 + 2", -3.0),
    ],
)
def test_safe_eval_basic_arithmetic(expr: str, expected) -> None:
    assert safe_eval_formula(expr) == expected


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('ls')",
        "abs(-5)",
        "x + 1",
        "4000 ** 2",
        "max(1, 2)",
        "(lambda: 1)()",
    ],
)
def test_safe_eval_rejects_unsafe(expr: str) -> None:
    with pytest.raises(ValueError):
        safe_eval_formula(expr)


def test_safe_eval_rejects_division_by_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        safe_eval_formula("1 / 0")


# ---------- parse_envelope ----------


def test_parse_envelope_basic() -> None:
    raw = json.dumps(
        {
            "answer": "A katta. 1000 farq.",
            "derived_calculations": [
                {
                    "output_value": "1000",
                    "formula": "4000 - 3000",
                    "input_values": [4000, 3000],
                }
            ],
        }
    )
    env = parse_envelope(raw)
    assert env.answer == "A katta. 1000 farq."
    assert len(env.derived) == 1
    assert env.derived[0].output_value == "1000"
    assert env.derived[0].input_values == (4000.0, 3000.0)


def test_parse_envelope_handles_code_fence() -> None:
    raw = '```json\n{"answer": "X 1.", "derived_calculations": []}\n```'
    env = parse_envelope(raw)
    assert env.answer == "X 1."


def test_parse_envelope_no_calcs_ok() -> None:
    env = parse_envelope('{"answer": "Plain", "derived_calculations": []}')
    assert env.derived == ()


def test_parse_envelope_drops_malformed_calcs() -> None:
    raw = json.dumps(
        {
            "answer": "A.",
            "derived_calculations": [
                {"output_value": "1"},  # missing formula
                {"formula": "1+1", "input_values": [1]},  # missing output
                {"output_value": "1", "formula": "1", "input_values": "nope"},
                {"output_value": "1", "formula": "1+1", "input_values": [1, 1]},
            ],
        }
    )
    env = parse_envelope(raw)
    assert len(env.derived) == 1


def test_parse_envelope_rejects_garbage() -> None:
    with pytest.raises(EnvelopeParseError):
        parse_envelope("not json at all")
    with pytest.raises(EnvelopeParseError):
        parse_envelope('{"answer": ""}')
    with pytest.raises(EnvelopeParseError):
        parse_envelope('{"derived_calculations": []}')


# ---------- verify_calculation ----------


_ROW_NUMS = {4000.0, 3000.0, 1000.0}


def test_verify_subtraction() -> None:
    c = DerivedCalc("1000", "4000 - 3000", (4000.0, 3000.0))
    assert verify_calculation(c, _ROW_NUMS) is True


def test_verify_percentage_with_scaffolding_constant() -> None:
    c = DerivedCalc("33.3", "(4000 - 3000) / 3000 * 100", (4000.0, 3000.0))
    assert verify_calculation(c, _ROW_NUMS) is True


def test_verify_total_share() -> None:
    c = DerivedCalc("50", "4000 / (4000 + 3000 + 1000) * 100", (4000.0, 3000.0, 1000.0))
    assert verify_calculation(c, _ROW_NUMS) is True


def test_verify_rejects_input_not_in_rows() -> None:
    c = DerivedCalc("1234", "5000 - 3766", (5000.0, 3766.0))
    assert verify_calculation(c, _ROW_NUMS) is False


def test_verify_rejects_unwhitelisted_constant() -> None:
    # 7 is not a scaffolding constant and not in inputs → reject.
    c = DerivedCalc("4007", "4000 + 7", (4000.0,))
    assert verify_calculation(c, _ROW_NUMS) is False


def test_verify_rejects_inconsistent_output() -> None:
    c = DerivedCalc("999", "4000 - 3000", (4000.0, 3000.0))
    assert verify_calculation(c, _ROW_NUMS) is False


def test_verify_rejects_division_by_zero() -> None:
    c = DerivedCalc("nan", "4000 / 0", (4000.0,))
    assert verify_calculation(c, _ROW_NUMS) is False


# ---------- extract_row_numbers ----------


def test_extract_row_numbers_handles_none_and_strings() -> None:
    rows = (("Andijon", 4000), (None, "1234.5"), ("X", None))
    nums = extract_row_numbers(rows)
    assert 4000.0 in nums
    assert 1234.5 in nums
    assert None not in nums  # type: ignore[comparison-overlap]


# ---------- is_answer_grounded ----------


def test_grounded_accepts_row_value() -> None:
    assert is_answer_grounded(
        "A: 4000 kishi.",
        row_numbers={4000.0, 3000.0},
        verified_outputs=set(),
        row_count=2,
    )


def test_grounded_accepts_verified_output() -> None:
    assert is_answer_grounded(
        "Farq 1000, ya'ni 33.3%.",
        row_numbers={4000.0, 3000.0},
        verified_outputs={1000.0, 33.3},
        row_count=2,
    )


def test_grounded_rejects_invented_number() -> None:
    assert not is_answer_grounded(
        "A: 9999 kishi.",
        row_numbers={4000.0, 3000.0},
        verified_outputs=set(),
        row_count=2,
    )


def test_grounded_allows_small_ordinals_for_rank_phrasing() -> None:
    # row_count=10 → ordinals 1..10 allowed even when not in rows.
    assert is_answer_grounded(
        "1-o'rin Toshkent. Top 3 ichida.",
        row_numbers={4000.0},
        verified_outputs=set(),
        row_count=10,
    )
