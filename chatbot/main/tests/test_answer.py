"""Phase 6D: deterministic answer composer."""

from __future__ import annotations

from cerr_chatbot.query import (
    NULL_DISPLAY,
    Answer,
    QueryServiceResult,
    compose_answer,
)


def _sql_result(
    rows: tuple[tuple[object, ...], ...],
    *,
    columns: tuple[str, ...] = ("region_name_cyr", "population"),
    user_message: str = "Top regions by population.",
    sql: str | None = "SELECT region_name_cyr, population FROM v_regions LIMIT 100",
) -> QueryServiceResult:
    return QueryServiceResult(
        kind="sql_result",
        user_message=user_message,
        sql=sql,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        debug_notes=("internal trace must not leak",),
    )


def test_sql_result_with_two_rows_renders_table() -> None:
    res = _sql_result(
        rows=(("Andijon", 1234), ("Fargona", 5678)),
    )
    a = compose_answer(res)
    assert isinstance(a, Answer)
    assert a.kind == "sql_result"
    assert "Top regions by population." in a.text
    assert "Qaytarilgan qatorlar: 2." in a.text
    assert "| region_name_cyr | population |" in a.text
    assert "| Andijon | 1234 |" in a.text
    assert "| Fargona | 5678 |" in a.text


def test_none_values_render_as_missing() -> None:
    res = _sql_result(rows=(("Andijon", None), (None, 5678)))
    a = compose_answer(res)
    assert f"| Andijon | {NULL_DISPLAY} |" in a.text
    assert f"| {NULL_DISPLAY} | 5678 |" in a.text


def test_truncation_note_when_row_count_exceeds_max() -> None:
    rows = tuple((f"R{i}", i) for i in range(15))
    res = _sql_result(rows=rows)
    a = compose_answer(res, max_rows=10)
    assert a.row_count == 15
    # Only 10 data rows should appear in the markdown body.
    assert a.text.count("\n| R") == 10
    assert "Faqat birinchi 10 qator ko'rsatildi." in a.text


def test_empty_sql_result_says_no_rows_found() -> None:
    res = _sql_result(rows=())
    a = compose_answer(res)
    assert a.row_count == 0
    assert "Bu savolga mos qatorlar topilmadi." in a.text
    assert "| region_name_cyr | population |" not in a.text


def test_clarify_returns_user_message_only() -> None:
    res = QueryServiceResult(
        kind="clarify",
        user_message="Please specify region/district/mahalla and metric.",
        debug_notes=("metric ambiguous",),
    )
    a = compose_answer(res)
    assert a.kind == "clarify"
    assert a.text == "Please specify region/district/mahalla and metric."
    assert "metric ambiguous" not in a.text


def test_no_data_returns_user_message_only() -> None:
    res = QueryServiceResult(
        kind="no_data",
        user_message="This metric is not available in the current semantic views.",
        debug_notes=("no GDP column",),
    )
    a = compose_answer(res)
    assert a.kind == "no_data"
    assert "not available" in a.text
    assert "no GDP column" not in a.text


def test_unsupported_returns_user_message_only() -> None:
    res = QueryServiceResult(
        kind="unsupported",
        user_message="I can answer regional statistics but this is outside available data.",
    )
    a = compose_answer(res)
    assert a.kind == "unsupported"
    assert "outside available data" in a.text


def test_planner_error_returns_user_message_only_no_internals() -> None:
    res = QueryServiceResult(
        kind="planner_error",
        user_message="I could not interpret that question safely.",
        debug_notes=("PlannerParseError: not valid JSON",),
    )
    a = compose_answer(res)
    assert a.kind == "planner_error"
    assert "could not interpret" in a.text.lower()
    for forbidden in ("PlannerParseError", "JSON", "traceback", "sql_guard"):
        assert forbidden not in a.text


def test_execution_error_returns_user_message_only_no_internals() -> None:
    res = QueryServiceResult(
        kind="execution_error",
        user_message="I prepared a query but could not retrieve the result.",
        sql="SELECT region_code FROM v_regions LIMIT 100",
        debug_notes=("RuntimeError: no such table: regions",),
    )
    a = compose_answer(res)
    assert a.kind == "execution_error"
    assert "could not retrieve" in a.text.lower()
    for forbidden in ("RuntimeError", "no such table", "regions"):
        assert forbidden not in a.text
    # SQL is exposed only via metadata, not body text.
    assert a.sql == "SELECT region_code FROM v_regions LIMIT 100"
    assert "SELECT" not in a.text


def test_numbers_preserved_verbatim() -> None:
    res = _sql_result(rows=(("X", 1234567890123), ("Y", 0.123456789), ("Z", -0.0151)))
    a = compose_answer(res)
    assert "1234567890123" in a.text
    assert "0.123456789" in a.text
    assert "-0.0151" in a.text


def test_pipe_in_cell_value_escaped() -> None:
    res = _sql_result(rows=(("a|b", 1),))
    a = compose_answer(res)
    assert "a\\|b" in a.text
