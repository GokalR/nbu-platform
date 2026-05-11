"""Multi-query evidence pack orchestration.

The planner returns a primary SQL plus 0..MAX_CONTEXT_QUERIES context
queries (baselines, totals, peer averages, related metrics). Backend
validates every SQL through the existing `sql_guard.validate`, executes
the safe ones, and assembles an `EvidencePack` the answer agent can
reason over.

A failed context query does NOT block the primary answer; it is recorded
on the pack with `error=` so the answer agent can ignore it or mention
"context unavailable".

Source data is never modified. SQL guard, semantic catalog, and the
read-only executor remain authoritative; this layer only fans out and
gathers.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Protocol

if TYPE_CHECKING:
    from cerr_chatbot.query.session_memory import MemorySnapshot

from sqlalchemy import Engine

from cerr_chatbot.query.conversational_router import classify as classify_intent
from cerr_chatbot.query.executor import execute
from cerr_chatbot.query.service import SQL_RESULT_GENERIC_INTRO, ServiceKind
from cerr_chatbot.query.sql_guard import SqlGuardError, validate

log = logging.getLogger(__name__)

MAX_CONTEXT_QUERIES = 10

EvidenceKind = Literal["sql_plan", "clarify", "no_data", "unsupported"]
MemoryUse = Literal["used", "ignored", "unclear"]
_ALLOWED_MEMORY_USE: tuple[MemoryUse, ...] = ("used", "ignored", "unclear")
_DEFAULT_MEMORY_USE: MemoryUse = "ignored"


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceQueryResult:
    """One executed (or rejected) SQL: rows + columns or an error message."""

    purpose: str
    sql: str | None
    columns: tuple[str, ...] = ()
    rows: tuple[tuple[Any, ...], ...] = ()
    row_count: int = 0
    error: str | None = None


@dataclass(frozen=True)
class EvidencePack:
    """All evidence the answer agent gets to see for one user question."""

    question: str
    primary: EvidenceQueryResult
    context: tuple[EvidenceQueryResult, ...] = ()
    # Set when the planner had to make a real interpretive choice on a vague
    # question (e.g. "Andijon haqida" -> "I assumed you want a regional
    # overview"). Empty string when no assumption was needed. The narrator
    # surfaces this in the opening line so the user can refine.
    assumed_interpretation: str = ""


@dataclass(frozen=True)
class EvidenceServiceResult:
    kind: ServiceKind
    user_message: str
    pack: EvidencePack | None = None
    debug_notes: tuple[str, ...] = field(default_factory=tuple)


class EvidencePlanner(Protocol):
    def plan(
        self,
        user_question: str,
        *,
        memory_snapshot: MemorySnapshot | None = None,
    ) -> str: ...


# ---------------------------------------------------------------------------
# Plan parsing
# ---------------------------------------------------------------------------


class EvidencePlanParseError(ValueError):
    """The planner JSON envelope is missing fields or has an unknown kind."""


@dataclass(frozen=True)
class ParsedContextQuery:
    purpose: str
    sql: str


@dataclass(frozen=True)
class ParsedEvidencePlan:
    kind: EvidenceKind
    user_message: str
    primary_sql: str | None
    context_queries: tuple[ParsedContextQuery, ...]
    memory_use: MemoryUse = _DEFAULT_MEMORY_USE
    resolved_question: str = ""
    assumed_interpretation: str = ""


_ALLOWED_PLAN_KINDS = ("sql_plan", "clarify", "no_data", "unsupported")
_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_evidence_plan(text: str, *, user_question: str = "") -> ParsedEvidencePlan:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = _CODE_FENCE_RE.sub("", raw).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EvidencePlanParseError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise EvidencePlanParseError("envelope is not an object")
    kind = data.get("kind")
    if kind not in _ALLOWED_PLAN_KINDS:
        raise EvidencePlanParseError(f"kind must be one of {_ALLOWED_PLAN_KINDS}, got {kind!r}")
    user_message = data.get("user_message") or ""
    if not isinstance(user_message, str):
        user_message = ""

    primary_sql: str | None = None
    if kind == "sql_plan":
        primary = data.get("primary_sql")
        if not isinstance(primary, str) or not primary.strip():
            raise EvidencePlanParseError("'sql_plan' requires a non-empty 'primary_sql'")
        primary_sql = primary.strip()

    context_raw = data.get("context_queries") or []
    if not isinstance(context_raw, list):
        raise EvidencePlanParseError("'context_queries' must be a list")
    context: list[ParsedContextQuery] = []
    for entry in context_raw[:MAX_CONTEXT_QUERIES]:
        if not isinstance(entry, dict):
            continue
        sql = entry.get("sql")
        purpose = entry.get("purpose")
        if not isinstance(sql, str) or not sql.strip():
            continue
        if not isinstance(purpose, str) or not purpose.strip():
            continue
        context.append(ParsedContextQuery(purpose=purpose.strip(), sql=sql.strip()))

    memory_use_raw = data.get("memory_use")
    memory_use: MemoryUse = (
        memory_use_raw if memory_use_raw in _ALLOWED_MEMORY_USE else _DEFAULT_MEMORY_USE
    )

    resolved_raw = data.get("resolved_question")
    if isinstance(resolved_raw, str) and resolved_raw.strip():
        resolved_question = resolved_raw.strip()
    else:
        resolved_question = user_question

    interp_raw = data.get("assumed_interpretation")
    if isinstance(interp_raw, str) and interp_raw.strip():
        assumed_interpretation = interp_raw.strip()
    else:
        assumed_interpretation = ""

    return ParsedEvidencePlan(
        kind=kind,
        user_message=user_message,
        primary_sql=primary_sql,
        context_queries=tuple(context),
        memory_use=memory_use,
        resolved_question=resolved_question,
        assumed_interpretation=assumed_interpretation,
    )


# ---------------------------------------------------------------------------
# Service orchestration
# ---------------------------------------------------------------------------


_FALLBACK_PLANNER_ERROR = (
    "Savolni xavfsiz tushuntira olmadim. Iltimos, viloyat, tuman yoki "
    "mahalla nomini va kerakli ko'rsatkichni aniqroq yozing."
)
_FALLBACK_EXECUTION_ERROR = (
    "So'rovni tayyorladim, lekin natijani ololmadim. Iltimos, keyinroq "
    "qayta urinib ko'ring yoki savolni qayta tuzing."
)
_FALLBACK_CLARIFY = "Iltimos, viloyat/tuman/mahalla va ko'rsatkichni aniq ko'rsating."
_FALLBACK_UNSUPPORTED = (
    "Mavjud viloyat, tuman va mahalla statistikasi bo'yicha javob bera "
    "olaman, ammo bu so'rov hozirgi ma'lumotlardan tashqarida."
)
_FALLBACK_NO_DATA = "Bu ko'rsatkich hozirgi semantik ko'rinishlarda mavjud emas."

_CONVERSATIONAL = frozenset({"greeting", "capability", "help", "out_of_scope"})


def evidence_ask(
    engine: Engine,
    planner: EvidencePlanner,
    user_question: str,
    *,
    memory_snapshot: MemorySnapshot | None = None,
) -> EvidenceServiceResult:
    """Run the conversational router → planner → multi-SQL fan-out pipeline.

    `memory_snapshot` is forwarded to the planner only. Conversational
    short-circuits (greeting/help/capability/out_of_scope) never see memory.
    SQL guard, executor, and narrator never see memory either — the planner
    is the single component allowed to read prior conversation context.
    """
    intent = classify_intent(user_question)
    if intent.kind in _CONVERSATIONAL:
        return EvidenceServiceResult(
            kind=intent.kind,  # type: ignore[arg-type]
            user_message=intent.user_message,
        )

    try:
        raw = planner.plan(user_question, memory_snapshot=memory_snapshot)
    except Exception as exc:  # noqa: BLE001 - any planner crash is opaque
        return EvidenceServiceResult(
            kind="planner_error",
            user_message=_FALLBACK_PLANNER_ERROR,
            debug_notes=(f"planner raised {type(exc).__name__}: {exc}",),
        )

    try:
        plan = parse_evidence_plan(raw, user_question=user_question)
    except EvidencePlanParseError as exc:
        return EvidenceServiceResult(
            kind="planner_error",
            user_message=_FALLBACK_PLANNER_ERROR,
            debug_notes=(f"EvidencePlanParseError: {exc}",),
        )

    if plan.kind == "clarify":
        return EvidenceServiceResult(
            kind="clarify",
            user_message=plan.user_message or _FALLBACK_CLARIFY,
        )
    if plan.kind == "unsupported":
        return EvidenceServiceResult(
            kind="unsupported",
            user_message=plan.user_message or _FALLBACK_UNSUPPORTED,
        )
    if plan.kind == "no_data":
        return EvidenceServiceResult(
            kind="no_data",
            user_message=plan.user_message or _FALLBACK_NO_DATA,
        )

    # plan.kind == "sql_plan"
    assert plan.primary_sql is not None
    try:
        primary_validated = validate(plan.primary_sql)
    except SqlGuardError as exc:
        return EvidenceServiceResult(
            kind="planner_error",
            user_message=_FALLBACK_PLANNER_ERROR,
            debug_notes=(f"sql_guard rejected primary SQL: {exc}",),
        )
    try:
        qr = execute(engine, primary_validated.validated_sql)
    except Exception as exc:  # noqa: BLE001 - executor RuntimeError or other
        return EvidenceServiceResult(
            kind="execution_error",
            user_message=_FALLBACK_EXECUTION_ERROR,
            debug_notes=(f"primary {type(exc).__name__}: {exc}",),
        )

    primary_result = EvidenceQueryResult(
        purpose="primary",
        sql=qr.validated_sql,
        columns=qr.columns,
        rows=qr.rows,
        row_count=qr.row_count,
    )

    context_results = tuple(
        _run_context_query(engine, cq.purpose, cq.sql) for cq in plan.context_queries
    )

    pack = EvidencePack(
        question=plan.resolved_question or user_question,
        primary=primary_result,
        context=context_results,
        assumed_interpretation=plan.assumed_interpretation,
    )
    notes: list[str] = []
    if memory_snapshot is not None:
        notes.append("memory_snapshot=present")
    notes.append(f"memory_use={plan.memory_use}")
    if plan.resolved_question and plan.resolved_question != user_question:
        notes.append(f"resolved_question={plan.resolved_question}")
    if plan.assumed_interpretation:
        notes.append(f"assumed_interpretation={plan.assumed_interpretation}")
    return EvidenceServiceResult(
        kind="sql_result",
        user_message=SQL_RESULT_GENERIC_INTRO,
        pack=pack,
        debug_notes=tuple(notes),
    )


def _run_context_query(engine: Engine, purpose: str, sql: str) -> EvidenceQueryResult:
    try:
        v = validate(sql)
    except SqlGuardError as exc:
        return EvidenceQueryResult(purpose=purpose, sql=None, error=f"sql_guard: {exc}")
    try:
        qr = execute(engine, v.validated_sql)
    except Exception as exc:  # noqa: BLE001
        return EvidenceQueryResult(
            purpose=purpose, sql=v.validated_sql, error=f"{type(exc).__name__}: {exc}"
        )
    return EvidenceQueryResult(
        purpose=purpose,
        sql=qr.validated_sql,
        columns=qr.columns,
        rows=qr.rows,
        row_count=qr.row_count,
    )


__all__ = [
    "EvidenceKind",
    "EvidencePack",
    "EvidencePlanParseError",
    "EvidencePlanner",
    "EvidenceQueryResult",
    "EvidenceServiceResult",
    "MAX_CONTEXT_QUERIES",
    "MemoryUse",
    "ParsedContextQuery",
    "ParsedEvidencePlan",
    "evidence_ask",
    "parse_evidence_plan",
]
