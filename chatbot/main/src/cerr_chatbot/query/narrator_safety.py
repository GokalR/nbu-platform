"""Verify the LLM narrator's derived calculations against source rows.

The narrator V2 returns a JSON envelope:

    {
      "answer": "Uzbek Latin prose...",
      "derived_calculations": [
        {
          "output_value": "33.3",
          "formula": "(4000 - 3000) / 3000 * 100",
          "input_values": [4000, 3000]
        }
      ]
    }

This module:

1. Parses the envelope.
2. For each calc, validates that:
   - every value in `input_values` matches a numeric token from the row data
     (within tolerance);
   - the formula uses only `+`, `-`, `*`, `/`, parentheses and unary signs;
   - any literal in the formula is either present in `input_values` or in a
     small whitelist of scaffolding constants (0, 1, 2, 10, 100, 1000) used
     for percentages, halves, and per-mille;
   - `output_value` matches the value that the formula evaluates to (within
     tolerance).
3. Builds the set of allowed numeric tokens for the final answer:
   `row values ∪ verified outputs ∪ {row_count} ∪ ordinals 1..row_count`.
4. Rejects the answer if any numeric token in it falls outside that set.

When the envelope cannot be parsed or any number in the answer is unverified,
callers fall back to the deterministic markdown composer instead of shipping
the unsafe text.
"""

from __future__ import annotations

import ast
import json
import math
import re
from collections.abc import Iterable
from dataclasses import dataclass

# Whitelisted scaffolding constants. Allow 100 (percent), 1000 (per-mille),
# small multipliers commonly used to compute halves / shares / ratios.
_ALLOWED_FORMULA_CONSTANTS: tuple[float, ...] = (0.0, 1.0, 2.0, 10.0, 100.0, 1000.0)

# Matches plain `1234`, `1234.56`, European `12,5`, and grouped `1,234,567.89`.
_NUMERIC_RE = re.compile(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:[.,]\d+)?")
_THOUSANDS_RE = re.compile(r"^-?\d{1,3}(?:,\d{3})+(?:\.\d+)?$")
_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


@dataclass(frozen=True)
class DerivedCalc:
    output_value: str
    formula: str
    input_values: tuple[float, ...]


@dataclass(frozen=True)
class NarratorEnvelope:
    answer: str
    derived: tuple[DerivedCalc, ...]


class EnvelopeParseError(ValueError):
    """Returned when the LLM text is not a valid narrator JSON envelope."""


# ---------------------------------------------------------------------------
# Envelope parsing
# ---------------------------------------------------------------------------


def parse_envelope(text: str) -> NarratorEnvelope:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = _CODE_FENCE_RE.sub("", raw).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EnvelopeParseError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise EnvelopeParseError("envelope is not an object")
    answer = data.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise EnvelopeParseError("missing 'answer' string")
    raw_calcs = data.get("derived_calculations") or []
    if not isinstance(raw_calcs, list):
        raise EnvelopeParseError("'derived_calculations' must be a list")

    calcs: list[DerivedCalc] = []
    for entry in raw_calcs:
        if not isinstance(entry, dict):
            continue
        out = entry.get("output_value")
        formula = entry.get("formula")
        inputs = entry.get("input_values")
        if not isinstance(out, (str, int, float)):
            continue
        if not isinstance(formula, str) or not formula.strip():
            continue
        if not isinstance(inputs, list):
            continue
        try:
            input_floats = tuple(float(x) for x in inputs)
        except (TypeError, ValueError):
            continue
        calcs.append(DerivedCalc(str(out), formula, input_floats))
    return NarratorEnvelope(answer=answer.strip(), derived=tuple(calcs))


# ---------------------------------------------------------------------------
# Safe arithmetic evaluation
# ---------------------------------------------------------------------------


def safe_eval_formula(expr: str) -> float:
    """Evaluate a tightly restricted arithmetic expression.

    Allowed: numeric literals, parentheses, unary +/-, binary + - * /.
    Anything else (names, function calls, attribute access, comparisons)
    raises ValueError.
    """
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _eval_node(node.operand)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("division by zero in derived formula")
            return left / right
    raise ValueError(f"unsupported expression node: {type(node).__name__}")


def _formula_constants(expr: str) -> list[float]:
    tree = ast.parse(expr, mode="eval")
    out: list[float] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            out.append(float(node.value))
    return out


# ---------------------------------------------------------------------------
# Numeric matching helpers
# ---------------------------------------------------------------------------


def _close(a: float, b: float, *, rel: float = 1e-4, abs_: float = 0.5) -> bool:
    """Numeric tolerance for matching declared/computed/source values.

    Tight by design: typical rounding of derived percentages from many
    decimals to 1 decimal stays inside `abs_=0.5`, while integer source
    values like 999 vs 1000 are correctly rejected as different.
    """
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def _any_close(value: float, candidates: Iterable[float]) -> bool:
    return any(_close(value, c) for c in candidates)


def normalize_token(s: str) -> float | None:
    """Parse a numeric token in any of the formats produced by the formatter.

    - `"1,234,567.89"` → 1234567.89 (commas as thousand separators)
    - `"1234.5"`        → 1234.5
    - `"12,5"`          → 12.5 (European decimal, single comma, no dot)
    """
    if _THOUSANDS_RE.match(s):
        cleaned = s.replace(",", "")
    elif "," in s and "." not in s and s.count(",") == 1:
        cleaned = s.replace(",", ".")
    else:
        cleaned = s
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_row_numbers(rows: Iterable[Iterable[object]]) -> set[float]:
    """All numeric tokens drawn from the SQL result rows."""
    out: set[float] = set()
    for row in rows:
        for cell in row:
            if cell is None:
                continue
            text = str(cell)
            for tok in _NUMERIC_RE.findall(text):
                v = normalize_token(tok)
                if v is not None and not (math.isnan(v) or math.isinf(v)):
                    out.add(v)
    return out


# ---------------------------------------------------------------------------
# Calculation verification
# ---------------------------------------------------------------------------


def verify_calculation(calc: DerivedCalc, row_numbers: set[float]) -> bool:
    """True if the derived calc is internally consistent and grounded.

    All `input_values` must trace back to a row value (modulo tolerance);
    every literal in the formula must be either an input value or a
    whitelisted constant; the formula must evaluate to `output_value` within
    tolerance.
    """
    for inp in calc.input_values:
        if math.isnan(inp) or math.isinf(inp):
            return False
        if not _any_close(inp, row_numbers):
            return False
    try:
        constants = _formula_constants(calc.formula)
    except SyntaxError:
        return False
    for c in constants:
        if _any_close(c, calc.input_values) or _any_close(c, _ALLOWED_FORMULA_CONSTANTS):
            continue
        return False
    try:
        computed = safe_eval_formula(calc.formula)
    except (ValueError, ZeroDivisionError, SyntaxError):
        return False
    declared = normalize_token(str(calc.output_value))
    if declared is None:
        return False
    return _close(computed, declared)


# ---------------------------------------------------------------------------
# Final answer grounding
# ---------------------------------------------------------------------------


def is_answer_grounded(
    answer_text: str,
    *,
    row_numbers: set[float],
    verified_outputs: set[float],
    row_count: int,
) -> bool:
    """True if every numeric token in `answer_text` is grounded.

    Allowed tokens: row values, verified derived outputs, the row count, and
    small ordinal integers up to `row_count` (so phrasing like "1-o'rin",
    "Top 3" stays legal even when the rank itself is not in the rows).
    """
    allowed: set[float] = set(row_numbers) | set(verified_outputs)
    allowed.add(float(row_count))
    upper = max(row_count, 1) + 1
    for i in range(1, upper):
        allowed.add(float(i))
    for tok in _NUMERIC_RE.findall(answer_text):
        v = normalize_token(tok)
        if v is None:
            return False
        if not _any_close(v, allowed):
            return False
    return True


__all__ = [
    "DerivedCalc",
    "EnvelopeParseError",
    "NarratorEnvelope",
    "extract_row_numbers",
    "is_answer_grounded",
    "normalize_token",
    "parse_envelope",
    "safe_eval_formula",
    "verify_calculation",
]
