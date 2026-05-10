"""Phase 6C orchestration: conversational router -> planner -> validator -> executor.

`QueryService.ask` is the only public entry point. It composes:
1. conversational router (greeting/help/capability/out-of-scope short-circuit)
2. injected planner (returns raw LLM JSON text)
3. `parse_planner_response` (which already calls `sql_guard.validate`)
4. `executor.execute` (only when kind=="sql")

Failure modes are mapped to user-safe outcomes; raw exception text is kept
in `debug_notes`, never in `user_message`.

For successful `sql_result` outcomes the planner's `user_message` is replaced
with a generic placeholder. Final factual prose is the AnswerNarrator's job
once SQL rows are available; the planner has no factual grounding yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from sqlalchemy import Engine

from cerr_chatbot.query.conversational_router import classify as classify_intent
from cerr_chatbot.query.executor import execute
from cerr_chatbot.query.planner_models import PlannerDecision
from cerr_chatbot.query.planner_parser import (
    PlannerParseError,
    parse_planner_response,
)

ServiceKind = Literal[
    "sql_result",
    "clarify",
    "unsupported",
    "no_data",
    "planner_error",
    "execution_error",
    "greeting",
    "capability",
    "help",
    "out_of_scope",
]

# Conversational kinds answered locally without DB or planner.
_CONVERSATIONAL_KINDS: frozenset[str] = frozenset(
    {"greeting", "capability", "help", "out_of_scope"}
)

# User-facing copy. Default language is Uzbek Latin. Polite, generic, no
# internal terminology. Strings here are last-resort fallbacks; the planner
# is expected to provide its own user_message when possible.
_FALLBACK_PLANNER_ERROR = (
    "Savolni xavfsiz tushuntira olmadim. Iltimos, viloyat, tuman yoki "
    "mahalla nomini va kerakli ko'rsatkichni aniqroq yozing."
)
_FALLBACK_EXECUTION_ERROR = (
    "So'rovni tayyorladim, lekin natijani ololmadim. Iltimos, keyinroq "
    "qayta urinib ko'ring yoki savolni qayta tuzing."
)
_FALLBACK_UNSUPPORTED = (
    "Mavjud viloyat, tuman va mahalla statistikasi bo'yicha javob bera "
    "olaman, ammo bu so'rov hozirgi ma'lumotlardan tashqarida."
)
_FALLBACK_NO_DATA = "Bu ko'rsatkich hozirgi semantik ko'rinishlarda mavjud emas."
_FALLBACK_CLARIFY = "Iltimos, viloyat/tuman/mahalla va ko'rsatkichni aniq ko'rsating."

# Generic placeholder for sql_result. The factual answer is produced by the
# AnswerNarrator (or deterministic composer) once rows are available.
SQL_RESULT_GENERIC_INTRO = "Natijani topdim."


class Planner(Protocol):
    def plan(self, user_question: str) -> str: ...


@dataclass(frozen=True)
class QueryServiceResult:
    kind: ServiceKind
    user_message: str
    sql: str | None = None
    columns: tuple[str, ...] = ()
    rows: tuple[tuple[Any, ...], ...] = ()
    row_count: int = 0
    expected_result_shape: str | None = None
    debug_notes: tuple[str, ...] = field(default_factory=tuple)
    user_question: str = ""


class QueryService:
    def __init__(self, engine: Engine, planner: Planner) -> None:
        self._engine = engine
        self._planner = planner

    def ask(self, user_question: str) -> QueryServiceResult:
        # 0) conversational router — short-circuit greetings/help/capability/oos
        #    so they never touch DB or LLM planner.
        intent = classify_intent(user_question)
        if intent.kind in _CONVERSATIONAL_KINDS:
            return QueryServiceResult(
                kind=intent.kind,  # type: ignore[arg-type]
                user_message=intent.user_message,
                user_question=user_question,
            )

        # 1) plan
        try:
            raw = self._planner.plan(user_question)
        except Exception as exc:  # noqa: BLE001 - any planner crash is opaque to user
            return QueryServiceResult(
                kind="planner_error",
                user_message=_FALLBACK_PLANNER_ERROR,
                debug_notes=(f"planner raised {type(exc).__name__}: {exc}",),
                user_question=user_question,
            )

        # 2) parse + validate (parse_planner_response runs sql_guard for kind=sql)
        try:
            decision: PlannerDecision = parse_planner_response(raw)
        except PlannerParseError as exc:
            return QueryServiceResult(
                kind="planner_error",
                user_message=_FALLBACK_PLANNER_ERROR,
                debug_notes=(f"PlannerParseError: {exc}",),
                user_question=user_question,
            )

        # 3) dispatch by kind
        if decision.kind == "clarify":
            return QueryServiceResult(
                kind="clarify",
                user_message=decision.user_message or _FALLBACK_CLARIFY,
                expected_result_shape=decision.expected_result_shape,
                debug_notes=decision.reasoning_notes,
                user_question=user_question,
            )

        if decision.kind == "refuse":
            return QueryServiceResult(
                kind="unsupported",
                user_message=decision.user_message or _FALLBACK_UNSUPPORTED,
                expected_result_shape=decision.expected_result_shape,
                debug_notes=decision.reasoning_notes,
                user_question=user_question,
            )

        if decision.kind == "no_data":
            return QueryServiceResult(
                kind="no_data",
                user_message=decision.user_message or _FALLBACK_NO_DATA,
                expected_result_shape=decision.expected_result_shape,
                debug_notes=decision.reasoning_notes,
                user_question=user_question,
            )

        # decision.kind == "sql"
        assert decision.sql is not None  # parse_planner_response guarantees this

        try:
            qr = execute(self._engine, decision.sql)
        except Exception as exc:  # noqa: BLE001 - executor RuntimeError or other
            return QueryServiceResult(
                kind="execution_error",
                user_message=_FALLBACK_EXECUTION_ERROR,
                sql=decision.sql,
                debug_notes=(f"{type(exc).__name__}: {exc}",) + decision.reasoning_notes,
                user_question=user_question,
            )

        # Planner-supplied user_message is intentionally discarded for
        # sql_result. Planner has no SQL output yet, so any prose it writes
        # would be ungrounded. Final answer is composed by the narrator
        # downstream from `qr.rows`.
        return QueryServiceResult(
            kind="sql_result",
            user_message=SQL_RESULT_GENERIC_INTRO,
            sql=qr.validated_sql,
            columns=qr.columns,
            rows=qr.rows,
            row_count=qr.row_count,
            expected_result_shape=decision.expected_result_shape,
            debug_notes=decision.reasoning_notes,
            user_question=user_question,
        )


__all__ = [
    "Planner",
    "QueryService",
    "QueryServiceResult",
    "SQL_RESULT_GENERIC_INTRO",
    "ServiceKind",
]
