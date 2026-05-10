"""Pre-format numbers and pre-compute analytical metrics for the narrator.

Why this exists: the LLM cannot reliably round, sum, or share-percent under
load. If we ship raw `67611.4667952569` to the prompt, the model echoes it
verbatim or attempts mental math and hallucinates contradictions. So we
*format every numeric cell* before serialization and *pre-compute* the
analytical numbers a narrator typically wants (top vs second gap, share,
ratio, comparison vs context baselines). The narrator then quotes from a
fixed menu of pre-computed strings instead of doing arithmetic.

Public API:

- `format_number(value)` → human-readable string with thousands separators
  and ≤2 decimals (no trailing zeros).
- `format_cell(value)` → `format_number` for numeric cells, value otherwise.
- `format_rows(rows)` → tuple of tuples with every numeric cell formatted.
- `compute_derived_metrics(primary, context)` → flat dict
  `{name: formatted_value}` of pre-computed analytical numbers, including
  cross-metrics that combine the primary's first row with each scalar
  context query (`first_vs_<purpose>_ratio`, `first_vs_<purpose>_pct_diff`,
  `share_first_of_<purpose>_pct`).

This module does not call the LLM and does not hit the database. It is
pure transformation over the already-fetched evidence rows.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from decimal import Decimal
from typing import Any

# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------


def _is_number(x: Any) -> bool:
    if x is None or isinstance(x, bool):
        return False
    return isinstance(x, (int, float, Decimal))


def _to_float(x: Any) -> float | None:
    if not _is_number(x):
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def format_number(value: Any, *, max_decimals: int = 2) -> str:
    """Human-readable numeric formatting.

    `1234567` → `"1,234,567"`. `67611.4667952569` → `"67,611.47"`.
    `1234.5` → `"1,234.5"`. `0` → `"0"`. NaN/Inf → str(value).
    Non-numeric values are stringified unchanged.
    """
    f = _to_float(value)
    if f is None:
        return "" if value is None else str(value)
    if abs(f) >= 1 and f == int(f):
        return f"{int(f):,}"
    if abs(f) < 1 and f == 0:
        return "0"
    s = f"{f:,.{max_decimals}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def format_cell(value: Any) -> Any:
    if value is None:
        return None
    if _is_number(value):
        return format_number(value)
    return value


def format_rows(rows: Iterable[Iterable[Any]]) -> tuple[tuple[Any, ...], ...]:
    return tuple(tuple(format_cell(c) for c in row) for row in rows)


# ---------------------------------------------------------------------------
# Derived analytical metrics
# ---------------------------------------------------------------------------


def _rightmost_numeric_column(
    columns: tuple[str, ...], rows: tuple[tuple[Any, ...], ...]
) -> int | None:
    if not rows or not columns:
        return None
    for idx in range(len(columns) - 1, -1, -1):
        if any(_is_number(row[idx]) for row in rows):
            return idx
    return None


def _safe_key(purpose: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", (purpose or "").lower()).strip("_")
    return (cleaned or "context")[:40]


def compute_derived_metrics(primary: Any, context: Iterable[Any] = ()) -> dict[str, Any]:
    """Pre-compute analytical numbers from primary rows + scalar context.

    `primary` and each entry of `context` follow the EvidenceQueryResult
    shape (`columns`, `rows`, `row_count`, `error`, `purpose`). The function
    discovers the value column as the rightmost numeric column. The label
    column is the first non-value column, used to name the first row.

    Outputs are pre-formatted strings; numbers in the answer should match
    these tokens character-for-character so the grounding check passes.
    """
    metrics: dict[str, Any] = {}
    if not getattr(primary, "rows", None) or not getattr(primary, "columns", None):
        return metrics
    val_idx = _rightmost_numeric_column(primary.columns, primary.rows)
    if val_idx is None:
        return metrics

    value_pairs: list[tuple[tuple[Any, ...], float | None]] = [
        (row, _to_float(row[val_idx])) for row in primary.rows
    ]
    present_pairs: list[tuple[tuple[Any, ...], float]] = [
        (row, value) for row, value in value_pairs if value is not None
    ]
    if not present_pairs:
        return metrics
    present: list[float] = [value for _, value in present_pairs]

    # Pick a label column: first column that is not the value column.
    label_idx = next(
        (i for i in range(len(primary.columns)) if i != val_idx),
        None,
    )

    n = len(present)
    min_val = min(present)
    max_val = max(present)
    sum_shown = sum(present)
    avg_shown = sum_shown / n

    metrics["shown_count"] = primary.row_count
    metrics["rows_with_value"] = n
    metrics["rows_with_null_value"] = len(value_pairs) - n
    metrics["min_value_in_shown"] = format_number(min_val)
    metrics["max_value_in_shown"] = format_number(max_val)
    metrics["sum_shown"] = format_number(sum_shown)
    metrics["avg_shown"] = format_number(avg_shown)
    metrics["dispersion_range_shown"] = format_number(max_val - min_val)
    metrics["all_values_equal"] = len(set(present)) == 1
    metrics["rows_at_max_value"] = sum(1 for v in present if v == max_val)
    metrics["rows_at_min_value"] = sum(1 for v in present if v == min_val)

    first_row, first = present_pairs[0]
    metrics["first_row_value"] = format_number(first)
    if label_idx is not None and first_row[label_idx] is not None:
        metrics["first_row_label"] = str(first_row[label_idx])

    last_row, last = present_pairs[-1]
    metrics["last_row_value"] = format_number(last)
    if label_idx is not None and last_row[label_idx] is not None:
        metrics["last_row_label"] = str(last_row[label_idx])

    if n >= 2:
        _, second = present_pairs[1]
        metrics["second_row_value"] = format_number(second)
        metrics["gap_first_to_second_abs"] = format_number(abs(first - second))
        if second != 0:
            metrics["ratio_first_to_second"] = format_number(first / second)
            metrics["pct_diff_first_to_second"] = format_number((first - second) / second * 100)
        metrics["gap_first_to_last_abs"] = format_number(abs(first - last))
        if last != 0 and last != first:
            metrics["ratio_first_to_last"] = format_number(first / last)
            metrics["pct_diff_first_to_last"] = format_number((first - last) / last * 100)

    if sum_shown:
        metrics["share_first_of_shown_pct"] = format_number(first / sum_shown * 100)
        metrics["share_last_of_shown_pct"] = format_number(last / sum_shown * 100)
        if n >= 3:
            top3 = sum(present[:3])
            metrics["share_top3_of_shown_pct"] = format_number(top3 / sum_shown * 100)

    if n >= 2:
        metrics["rows_above_avg_shown"] = sum(1 for v in present if v > avg_shown)
        metrics["rows_below_avg_shown"] = sum(1 for v in present if v < avg_shown)

    # Concentration: most-frequent label across the shown rows (catches
    # "3 of 10 lowest are in Surxondaryo" style observations).
    if label_idx is not None and n >= 2:
        from collections import Counter

        labels = [str(row[label_idx]) for row, _ in present_pairs if row[label_idx] is not None]
        if labels:
            top_label, top_count = Counter(labels).most_common(1)[0]
            if top_count >= 2:
                metrics["most_frequent_label"] = top_label
                metrics["most_frequent_label_count"] = top_count

    # Pull scalar context values + cross-metrics.
    for ctx in context or ():
        if getattr(ctx, "error", None):
            continue
        if getattr(ctx, "row_count", 0) != 1 or not ctx.rows or not ctx.columns:
            continue
        cell = ctx.rows[0][-1]
        baseline = _to_float(cell)
        if baseline is None:
            continue
        key = _safe_key(getattr(ctx, "purpose", ""))
        metrics[f"context.{key}"] = format_number(baseline)
        if baseline != 0 and _allows_cross_metric(getattr(ctx, "purpose", "")):
            metrics[f"first_vs_{key}_ratio"] = format_number(first / baseline)
            metrics[f"first_vs_{key}_pct_diff"] = format_number((first - baseline) / baseline * 100)
        if (
            baseline > 0
            and 0 <= first <= baseline
            and _allows_share_metric(getattr(ctx, "purpose", ""))
        ):
            metrics[f"share_first_of_{key}_pct"] = format_number(first / baseline * 100)

    return metrics


def _allows_cross_metric(purpose: str) -> bool:
    p = (purpose or "").lower()
    return any(word in p for word in ("avg", "average", "baseline", "mean", "median"))


def _allows_share_metric(purpose: str) -> bool:
    p = (purpose or "").lower()
    return any(word in p for word in ("total", "sum", "jami"))


__all__ = [
    "compute_derived_metrics",
    "format_cell",
    "format_number",
    "format_rows",
]
