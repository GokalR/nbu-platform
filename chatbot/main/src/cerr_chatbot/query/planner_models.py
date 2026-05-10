"""LLM SQL planner decision model.

A planner produces one PlannerDecision per user question. SQL is one of four
possible outcomes; refusal and clarification are first-class. Downstream code
must handle every kind explicitly - never assume `sql` is always set.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DecisionKind = Literal["sql", "clarify", "refuse", "no_data"]


@dataclass(frozen=True)
class PlannerDecision:
    kind: DecisionKind
    sql: str | None
    user_message: str
    reasoning_notes: tuple[str, ...] = field(default_factory=tuple)
    expected_result_shape: str | None = None


__all__ = ["DecisionKind", "PlannerDecision"]
