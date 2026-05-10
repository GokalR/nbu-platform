"""Phase 6C: QueryService orchestration. Fake planner, real executor."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query import QueryService, QueryServiceResult
from cerr_chatbot.query.service import SQL_RESULT_GENERIC_INTRO


@dataclass
class FakePlanner:
    response: str = ""
    seen_questions: list[str] = field(default_factory=list)
    raise_exc: BaseException | None = None

    def plan(self, user_question: str) -> str:
        self.seen_questions.append(user_question)
        if self.raise_exc is not None:
            raise self.raise_exc
        return self.response


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed_one_completed_run(engine, region_codes=(1100, 1200)) -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for idx, code in enumerate(region_codes):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                "region_code, region_name_cyr) "
                f"VALUES (1, 'f{idx}', 0, {code}, 'R{code}')"
            )


def _wrap(kind: str, **extra: object) -> str:
    body: dict = {"kind": kind, "sql": None, "user_message": "ok", "reasoning_notes": []}
    body.update(extra)
    return json.dumps(body)


# -------------------- happy path --------------------


def test_sql_planner_response_executes_and_returns_rows() -> None:
    engine = _engine_with_views()
    _seed_one_completed_run(engine)
    raw = _wrap(
        "sql",
        sql="SELECT region_code FROM v_regions ORDER BY region_code",
        user_message="Region codes.",
        reasoning_notes=["test"],
        expected_result_shape="codes",
    )
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("list region codes please")

    assert isinstance(res, QueryServiceResult)
    assert res.kind == "sql_result"
    assert res.row_count == 2
    assert tuple(r[0] for r in res.rows) == (1100, 1200)
    # Planner's factual prose is intentionally replaced with a generic intro
    # for sql_result; the AnswerNarrator writes the real prose from rows.
    assert res.user_message == SQL_RESULT_GENERIC_INTRO
    assert res.expected_result_shape == "codes"
    assert "v_regions" in res.sql


def test_planner_receives_user_question_verbatim() -> None:
    engine = _engine_with_views()
    fake = FakePlanner(response=_wrap("clarify", user_message="?"))
    QueryService(engine, fake).ask("how many mahallas in region 1730?")
    assert fake.seen_questions == ["how many mahallas in region 1730?"]


# -------------------- non-execute paths --------------------


def test_clarify_response_does_not_execute_db() -> None:
    engine = _engine_with_views()
    raw = _wrap("clarify", user_message="Which region or district?")
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("show me the data")
    assert res.kind == "clarify"
    assert res.row_count == 0
    assert res.rows == ()
    assert res.sql is None
    assert "Which region" in res.user_message


def test_no_data_response_does_not_execute_db() -> None:
    engine = _engine_with_views()
    raw = _wrap("no_data", user_message="GDP is not in the available views.")
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("what is the GDP of Tashkent?")
    assert res.kind == "no_data"
    assert res.rows == ()
    assert res.sql is None
    assert res.user_message == "GDP is not in the available views."


def test_refuse_response_maps_to_unsupported() -> None:
    engine = _engine_with_views()
    raw = _wrap("refuse", user_message="Write operations are not allowed.")
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("delete all rows")
    assert res.kind == "unsupported"
    assert res.sql is None
    assert "Write" in res.user_message


# -------------------- error paths --------------------


def test_malformed_planner_response_maps_to_planner_error() -> None:
    engine = _engine_with_views()
    svc = QueryService(engine, FakePlanner(response="{not json"))
    res = svc.ask("anything")
    assert res.kind == "planner_error"
    # Default fallback is Uzbek Latin; non-technical.
    assert "tushuntira olmadim" in res.user_message.lower()
    assert "json" not in res.user_message.lower()
    assert "traceback" not in res.user_message.lower()
    # Internal note keeps the technical detail for logs.
    assert any("PlannerParseError" in n for n in res.debug_notes)


def test_planner_sql_rejected_by_guard_maps_to_planner_error() -> None:
    engine = _engine_with_views()
    raw = _wrap(
        "sql",
        sql="SELECT * FROM v_regions",  # SELECT * blocked by sql_guard
        user_message="all regions",
    )
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("show everything")
    assert res.kind == "planner_error"
    assert "tushuntira olmadim" in res.user_message.lower()
    assert "select *" not in res.user_message.lower()  # internals hidden


def test_planner_crash_maps_to_planner_error() -> None:
    engine = _engine_with_views()
    fake = FakePlanner(raise_exc=RuntimeError("model timeout"))
    res = QueryService(engine, fake).ask("anything")
    assert res.kind == "planner_error"
    assert "model timeout" not in res.user_message
    assert any("model timeout" in n for n in res.debug_notes)


def test_executor_failure_maps_to_execution_error() -> None:
    """Drop the table the validated view targets, so executor blows up."""
    engine = _engine_with_views()
    _seed_one_completed_run(engine)
    # Break the view at the storage level: drop the underlying regions table.
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE regions")
    raw = _wrap(
        "sql",
        sql="SELECT region_code FROM v_regions",
        user_message="Codes.",
    )
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("codes")
    assert res.kind == "execution_error"
    assert "natijani ololmadim" in res.user_message.lower()
    assert "traceback" not in res.user_message.lower()
    assert "regions" not in res.user_message.lower()  # table name hidden


# -------------------- user-message hygiene --------------------


def test_user_messages_have_no_internal_terminology() -> None:
    """clarify / no_data / unsupported messages must be polite, non-technical."""
    forbidden = ("traceback", "exception", "sql_guard", "sqlalchemy", "kind=", "_flag")
    for kind, raw in (
        (
            "clarify",
            _wrap("clarify", user_message="Please specify region/district/mahalla and metric."),
        ),
        (
            "no_data",
            _wrap(
                "no_data",
                user_message="This metric is not available in the current semantic views.",
            ),
        ),
        (
            "refuse",
            _wrap(
                "refuse",
                user_message="I can answer from regional/district/mahalla statistics, but this is outside available data.",
            ),
        ),
    ):
        engine = _engine_with_views()
        svc = QueryService(engine, FakePlanner(response=raw))
        res = svc.ask("x")
        msg = res.user_message.lower()
        for bad in forbidden:
            assert bad not in msg, (kind, bad, msg)
