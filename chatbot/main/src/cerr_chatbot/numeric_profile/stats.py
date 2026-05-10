"""Numeric statistics primitives.

ValueBag accumulates raw observations including non-numeric ones; compute_stats
turns a bag into a NumericStats summary. Pure functions, no I/O.
"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


class NumericStats(BaseModel):
    total: int = 0
    non_null_count: int = 0
    null_count: int = 0
    null_percent: float = 0.0
    type_distribution: dict[str, int] = Field(default_factory=dict)
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    p01: float | None = None
    p99: float | None = None
    negative_count: int = 0
    zero_count: int = 0
    bad_value_examples: list[Any] = Field(default_factory=list)


@dataclass
class ValueBag:
    values: list[float] = field(default_factory=list)
    null_count: int = 0
    type_counts: Counter[str] = field(default_factory=Counter)
    bad_examples: list[Any] = field(default_factory=list)
    bad_example_cap: int = 5

    def add(self, raw: Any) -> None:
        self.type_counts[_type_name(raw)] += 1
        if raw is None:
            self.null_count += 1
            return
        # bool is a subclass of int; treat as non-numeric for KPI value fields.
        if isinstance(raw, bool):
            self._record_bad(raw)
            return
        if isinstance(raw, (int, float)):
            self.values.append(float(raw))
            return
        self._record_bad(raw)

    def total(self) -> int:
        return sum(self.type_counts.values())

    def _record_bad(self, raw: Any) -> None:
        if len(self.bad_examples) < self.bad_example_cap and raw not in self.bad_examples:
            self.bad_examples.append(raw)


def compute_stats(bag: ValueBag) -> NumericStats:
    total = bag.total()
    null_count = bag.null_count
    non_null_count = total - null_count
    null_percent = (null_count / total * 100.0) if total > 0 else 0.0

    s = NumericStats(
        total=total,
        non_null_count=non_null_count,
        null_count=null_count,
        null_percent=round(null_percent, 2),
        type_distribution=dict(bag.type_counts),
        bad_value_examples=list(bag.bad_examples),
    )

    vals = bag.values
    if not vals:
        return s

    s.min = min(vals)
    s.max = max(vals)
    s.mean = round(statistics.fmean(vals), 6)
    s.median = round(statistics.median(vals), 6)
    s.p01 = round(_quantile(vals, 0.01), 6)
    s.p99 = round(_quantile(vals, 0.99), 6)
    s.negative_count = sum(1 for v in vals if v < 0)
    s.zero_count = sum(1 for v in vals if v == 0)
    return s


def _quantile(values: list[float], q: float) -> float:
    """Linear-interpolated quantile. q in [0, 1]. Single-value safe."""
    if len(values) == 1:
        return values[0]
    sorted_vals = sorted(values)
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * frac


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    return type(value).__name__
