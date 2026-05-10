"""Phase 6D: deterministic answer composer.

Turns a `QueryServiceResult` into an `Answer` ready for the user. Pure
function, no I/O, no LLM.

Language policy:
- Composer prose is Uzbek Latin by default.
- Source entity names (region, district, mahalla, indicator labels) and
  numeric values are passed through unchanged.
- NULL is rendered as the Uzbek Latin missing-value phrase, not 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cerr_chatbot.query.service import QueryServiceResult, ServiceKind

NULL_DISPLAY = "ma'lumot yo'q"
_ROWS_RETURNED_PREFIX = "Qaytarilgan qatorlar"
_NO_ROWS_TEXT = "Bu savolga mos qatorlar topilmadi."


def _truncation_note(max_rows: int) -> str:
    return f"Faqat birinchi {max_rows} qator ko'rsatildi."


@dataclass(frozen=True)
class Answer:
    text: str
    kind: ServiceKind
    sql: str | None
    row_count: int
    columns: tuple[str, ...]


def compose_answer(result: QueryServiceResult, max_rows: int = 10) -> Answer:
    if result.kind != "sql_result":
        # clarify / no_data / unsupported / planner_error / execution_error.
        return Answer(
            text=result.user_message,
            kind=result.kind,
            sql=result.sql,
            row_count=result.row_count,
            columns=result.columns,
        )

    parts: list[str] = []
    intro = (result.user_message or "").strip()
    if intro:
        parts.append(intro)

    if result.row_count == 0:
        parts.append(_NO_ROWS_TEXT)
    else:
        rendered_rows = list(result.rows[:max_rows])
        parts.append(f"{_ROWS_RETURNED_PREFIX}: {result.row_count}.")
        parts.append(_render_markdown_table(result.columns, rendered_rows))
        if result.row_count > max_rows:
            parts.append(_truncation_note(max_rows))

    return Answer(
        text="\n\n".join(parts),
        kind=result.kind,
        sql=result.sql,
        row_count=result.row_count,
        columns=result.columns,
    )


def _render_markdown_table(columns: tuple[str, ...], rows: list[tuple[Any, ...]]) -> str:
    if not columns:
        return ""
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(_format_cell(c) for c in row) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def _format_cell(value: Any) -> str:
    if value is None:
        return NULL_DISPLAY
    s = str(value)
    # Escape pipe so markdown table rendering stays sane.
    return s.replace("|", "\\|")


__all__ = ["Answer", "NULL_DISPLAY", "compose_answer"]
