"""Chatbot-friendly scorer for eval cases.

Goal: judge fact correctness, not table cosmetics. The chatbot is allowed
to drop helper columns (e.g. `region_code`) as long as the named entity
and the metric value still survive in the answer.

Required-fact extraction:
- Prose lines: every numeric token is a required fact.
- Markdown tables: every numeric cell EXCEPT cells under a column whose
  header is `rank` (case-insensitive) or whose values form a pure ascending
  1..N sequence.
- Numbers normalized so `123` and `123.0` count as the same fact.
- Multiplicity preserved: a value appearing N times is required N times.

Pass criteria:
- `service_kind == 'sql_result'` whenever the expected answer carries
  required facts.
- Every required fact appears in the actual answer text (after the same
  numeric normalization).
- Expected null markers (`ma'lumot yo'q`) appear at least as many times in
  the actual text - NULL must never silently become `0`.

This file does NOT enforce "answer invents numbers not in SQL result". The
service ensures actual numbers come from the executed SQL output, so any
extra numeric tokens in actual prose come from the executor's own report
text (e.g. row count, sql limit) which is harmless. Future passes can
cross-check actual numbers against `result.rows`.
"""

from __future__ import annotations

import re
from collections import Counter

NUMERIC_RE = re.compile(r"-?\d+(?:\.\d+)?")
_NULL_MARKERS: tuple[str, ...] = ("ma'lumot yo'q",)


def _normalize_num(s: str) -> str:
    """`123.0` -> `123`, `1.50` -> `1.5`, etc. Stable, parser-friendly."""
    try:
        f = float(s)
    except ValueError:
        return s
    if f.is_integer():
        return str(int(f))
    # Trim trailing zeros while keeping the decimal portion meaningful.
    return f"{f:.10f}".rstrip("0").rstrip(".")


def _is_separator_row(cells: list[str]) -> bool:
    return all(set(c) <= set("-: ") and c.strip("-: ") == "" for c in cells)


def _is_rank_column(values: list[str]) -> bool:
    """Heuristic: column is a rank if values are a strict 1..N sequence."""
    if not values:
        return False
    try:
        nums = [int(_normalize_num(v.strip())) for v in values]
    except ValueError:
        return False
    return nums == list(range(1, len(nums) + 1))


def _parse_table_rows(table_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Split the markdown table into headers and data rows."""
    headers: list[str] = []
    data_rows: list[list[str]] = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not headers:
            headers = cells
            continue
        if _is_separator_row(cells):
            continue
        data_rows.append(cells)
    return headers, data_rows


def _extract_required_facts(expected: str) -> Counter[str]:
    """Required-fact counts.

    Tables and prose are extracted separately, then merged per-token using
    `max(prose, table)`. Rationale: when the same fact is stated in prose AND
    in a table cell (e.g. "All 10 below have rating_score = 1.0" plus a 10-row
    table where rating_score = 1.0), an additive merge would demand 11
    occurrences in the actual answer; the chatbot will repeat each table value
    only once. We therefore require the larger of the two sources rather than
    their sum.
    """
    table_facts: list[str] = []
    prose_facts: list[str] = []
    table_buffer: list[str] = []

    def flush_table() -> None:
        if not table_buffer:
            return
        headers, rows = _parse_table_rows(table_buffer)
        col_count = max((len(r) for r in rows), default=0)
        rank_cols: set[int] = set()
        for col_idx in range(col_count):
            if col_idx < len(headers) and headers[col_idx].strip().lower() == "rank":
                rank_cols.add(col_idx)
                continue
            column_values = [r[col_idx] for r in rows if col_idx < len(r)]
            if _is_rank_column(column_values):
                rank_cols.add(col_idx)
        for row in rows:
            for col_idx, cell in enumerate(row):
                if col_idx in rank_cols:
                    continue
                for n in NUMERIC_RE.findall(cell):
                    table_facts.append(_normalize_num(n))
        table_buffer.clear()

    for raw in expected.splitlines():
        stripped = raw.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_buffer.append(stripped)
            continue
        flush_table()
        for n in NUMERIC_RE.findall(raw):
            prose_facts.append(_normalize_num(n))
    flush_table()

    table_counter = Counter(table_facts)
    prose_counter = Counter(prose_facts)
    merged: Counter[str] = Counter()
    for tok in set(table_counter) | set(prose_counter):
        merged[tok] = max(table_counter[tok], prose_counter[tok])
    return merged


def _normalized_actual_numbers(actual: str) -> Counter[str]:
    return Counter(_normalize_num(n) for n in NUMERIC_RE.findall(actual))


def score_case(
    expected_answer: str,
    service_kind: str,
    actual_answer_text: str,
    *,
    forbidden_facts: tuple[str, ...] = (),
) -> tuple[bool, list[str]]:
    """Three-way numeric scoring.

    - REQUIRED facts: every numeric token in `expected_answer` (excluding
      rank columns) must appear in `actual_answer_text`.
    - OPTIONAL derived facts: extra numeric tokens in `actual_answer_text`
      that are not in `expected_answer` do NOT fail. Narrator-side safety
      verifies they are derivable; the scorer leaves them alone so analyst-
      style insights (deltas, percentages, totals) are not punished.
    - FORBIDDEN facts: any token in `forbidden_facts` that appears in
      `actual_answer_text` is a failure. Use this to lock out invented
      numbers a regression should never reintroduce.
    """
    reasons: list[str] = []
    required = _extract_required_facts(expected_answer)

    if service_kind != "sql_result":
        if required:
            reasons.append(
                f"service kind={service_kind!r}; expected numeric facts were not delivered"
            )
            return False, reasons
        if service_kind in {"planner_error", "execution_error"}:
            reasons.append(f"service kind={service_kind!r}")
            return False, reasons
        return True, reasons

    actual_nums = _normalized_actual_numbers(actual_answer_text)
    for tok, n in required.items():
        got = actual_nums.get(tok, 0)
        if got < n:
            reasons.append(f"required fact {tok!r} appears {n}x in expected but {got}x in actual")

    for raw in forbidden_facts:
        tok = _normalize_num(raw)
        if actual_nums.get(tok, 0) > 0:
            reasons.append(f"forbidden fact {raw!r} appears in actual answer")

    for marker in _NULL_MARKERS:
        exp = expected_answer.count(marker)
        if exp == 0:
            continue
        act = actual_answer_text.count(marker)
        if act < exp:
            reasons.append(
                f"null marker {marker!r}: expected {exp}, actual {act} (NULL must not become 0)"
            )

    return not reasons, reasons


__all__ = [
    "NUMERIC_RE",
    "score_case",
]
