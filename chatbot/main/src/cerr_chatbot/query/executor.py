"""Read-only SQL executor.

Validates SQL via `sql_guard.validate`, then runs it against the engine inside
a transaction marked read-only when the dialect supports it. Returns columns
and rows as plain Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from cerr_chatbot.query.sql_guard import ValidatedSql, validate

# Dialects we know support `SET TRANSACTION READ ONLY` (or equivalent).
_READONLY_DIALECTS = {"postgresql"}


@dataclass(frozen=True)
class QueryResult:
    validated_sql: str
    referenced_views: tuple[str, ...]
    limit_appended: bool
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    row_count: int


def execute(engine: Engine, sql: str) -> QueryResult:
    validated: ValidatedSql = validate(sql)
    return _run(engine, validated)


def _run(engine: Engine, validated: ValidatedSql) -> QueryResult:
    dialect_name = engine.dialect.name
    try:
        with engine.connect() as conn:
            if dialect_name in _READONLY_DIALECTS:
                # PostgreSQL: open explicit transaction and pin read-only +
                # statement timeout. SET LOCAL is auto-reverted at COMMIT.
                with conn.begin():
                    conn.execute(text("SET TRANSACTION READ ONLY"))
                    conn.execute(text("SET LOCAL statement_timeout = '5000ms'"))
                    cursor = conn.execute(text(validated.validated_sql))
                    cols = tuple(cursor.keys())
                    rows = tuple(tuple(r) for r in cursor.fetchall())
            else:
                # SQLite (and other dialects): validation already blocked DML.
                cursor = conn.execute(text(validated.validated_sql))
                cols = tuple(cursor.keys())
                rows = tuple(tuple(r) for r in cursor.fetchall())
    except SQLAlchemyError as exc:
        raise RuntimeError(f"query execution failed: {exc}") from exc

    return QueryResult(
        validated_sql=validated.validated_sql,
        referenced_views=validated.referenced_views,
        limit_appended=validated.limit_appended,
        columns=cols,
        rows=rows,
        row_count=len(rows),
    )


__all__ = ["QueryResult", "execute"]
