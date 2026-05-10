"""Parse LLM JSON output into a PlannerDecision.

If kind=='sql', the SQL is immediately validated through sql_guard. Validation
failures are surfaced as PlannerParseError so the caller can request a retry
or refuse to answer.
"""

from __future__ import annotations

import json
from typing import Any

from cerr_chatbot.query.planner_models import PlannerDecision
from cerr_chatbot.query.sql_guard import SqlGuardError, validate

ALLOWED_KINDS: frozenset[str] = frozenset({"sql", "clarify", "refuse", "no_data"})


class PlannerParseError(ValueError):
    """LLM output could not be turned into a valid PlannerDecision."""


def parse_planner_response(text: str) -> PlannerDecision:
    if not isinstance(text, str) or not text.strip():
        raise PlannerParseError("empty planner response")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PlannerParseError(f"response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise PlannerParseError("planner response must be a JSON object")

    kind = data.get("kind")
    if kind not in ALLOWED_KINDS:
        raise PlannerParseError(f"unknown kind: {kind!r}")

    user_message = data.get("user_message")
    if not isinstance(user_message, str) or not user_message.strip():
        raise PlannerParseError("user_message must be a non-empty string")

    sql = data.get("sql")
    if kind == "sql":
        if not isinstance(sql, str) or not sql.strip():
            raise PlannerParseError("kind=sql requires a non-empty sql string")
        # Validate immediately. If sql_guard rejects, escalate as a parse error
        # so the caller can fall back to clarify/refuse.
        try:
            validated = validate(sql)
        except SqlGuardError as exc:
            raise PlannerParseError(f"sql_guard rejected planner SQL: {exc}") from exc
        sql = validated.validated_sql
    else:
        if sql not in (None, ""):
            raise PlannerParseError(f"kind={kind} must have sql=null (got {sql!r})")
        sql = None

    notes = _coerce_notes(data.get("reasoning_notes"))
    shape = data.get("expected_result_shape")
    if shape is not None and not isinstance(shape, str):
        raise PlannerParseError("expected_result_shape must be string or null")

    return PlannerDecision(
        kind=kind,
        sql=sql,
        user_message=user_message,
        reasoning_notes=notes,
        expected_result_shape=shape,
    )


def _coerce_notes(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise PlannerParseError("reasoning_notes must be a list of strings or absent")
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise PlannerParseError("reasoning_notes entries must be strings")
        out.append(item)
    return tuple(out)


__all__ = ["ALLOWED_KINDS", "PlannerParseError", "parse_planner_response"]
