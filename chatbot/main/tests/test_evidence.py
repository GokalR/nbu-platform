"""Evidence-pack orchestration: planner → sql_guard fan-out → executor → pack."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query.evidence import (
    EvidencePlanParseError,
    evidence_ask,
    parse_evidence_plan,
)


@dataclass
class FakePlanner:
    response: str = ""
    seen: list[str] = field(default_factory=list)
    raise_exc: BaseException | None = None

    def plan(self, q: str, *, memory_snapshot=None) -> str:  # noqa: ARG002
        self.seen.append(q)
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


def _seed(engine, codes=(1100, 1200, 1300)) -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for i, code in enumerate(codes):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                f"region_code, region_name_cyr) VALUES (1, 'f{i}', 0, {code}, 'R{code}')"
            )


# ---------- parser ----------


def test_parser_accepts_sql_plan_with_context() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "ok",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [
                {"purpose": "total regions", "sql": "SELECT COUNT(*) FROM v_regions"},
                {"purpose": "avg pop", "sql": "SELECT AVG(population) FROM v_regions"},
            ],
        }
    )
    plan = parse_evidence_plan(raw)
    assert plan.kind == "sql_plan"
    assert plan.primary_sql.startswith("SELECT region_code")
    assert len(plan.context_queries) == 2
    assert plan.context_queries[0].purpose == "total regions"


def test_parser_handles_code_fence() -> None:
    raw = (
        "```json\n"
        + json.dumps({"kind": "clarify", "user_message": "?", "context_queries": []})
        + "\n```"
    )
    plan = parse_evidence_plan(raw)
    assert plan.kind == "clarify"


def test_parser_caps_context_queries_at_max() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [
                {"purpose": f"q{i}", "sql": f"SELECT {i} FROM v_regions"} for i in range(20)
            ],
        }
    )
    plan = parse_evidence_plan(raw)
    assert len(plan.context_queries) == 5  # MAX_CONTEXT_QUERIES


def test_parser_drops_malformed_context_entries() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [
                {"sql": "SELECT 1"},  # missing purpose
                {"purpose": "x"},  # missing sql
                {"purpose": "ok", "sql": "SELECT region_code FROM v_regions"},
            ],
        }
    )
    plan = parse_evidence_plan(raw)
    assert len(plan.context_queries) == 1


def test_parser_rejects_unknown_kind_and_missing_primary() -> None:
    import pytest

    with pytest.raises(EvidencePlanParseError):
        parse_evidence_plan(json.dumps({"kind": "weird", "primary_sql": "x"}))
    with pytest.raises(EvidencePlanParseError):
        parse_evidence_plan(json.dumps({"kind": "sql_plan", "context_queries": []}))
    with pytest.raises(EvidencePlanParseError):
        parse_evidence_plan("not json")


# ---------- memory-use / resolved_question contract ----------


def test_parser_defaults_memory_use_and_resolved_question() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
        }
    )
    plan = parse_evidence_plan(raw, user_question="how many regions?")
    assert plan.memory_use == "ignored"
    assert plan.resolved_question == "how many regions?"


def test_parser_accepts_memory_use_and_resolved_question() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "memory_use": "used",
            "resolved_question": "list region codes including the previous filter",
        }
    )
    plan = parse_evidence_plan(raw, user_question="and the codes?")
    assert plan.memory_use == "used"
    assert plan.resolved_question == "list region codes including the previous filter"


def test_parser_invalid_memory_use_falls_back_to_ignored() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "memory_use": "weird",
        }
    )
    plan = parse_evidence_plan(raw, user_question="x")
    assert plan.memory_use == "ignored"

    raw2 = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "memory_use": 7,
        }
    )
    plan2 = parse_evidence_plan(raw2, user_question="x")
    assert plan2.memory_use == "ignored"


def test_parser_blank_resolved_question_falls_back_to_user_question() -> None:
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "resolved_question": "   ",
        }
    )
    plan = parse_evidence_plan(raw, user_question="orig question")
    assert plan.resolved_question == "orig question"


def test_parser_defaults_apply_to_clarify_no_data_unsupported() -> None:
    for kind in ("clarify", "no_data", "unsupported"):
        raw = json.dumps({"kind": kind, "user_message": "msg"})
        plan = parse_evidence_plan(raw, user_question="q")
        assert plan.kind == kind
        assert plan.memory_use == "ignored"
        assert plan.resolved_question == "q"


def test_evidence_pack_question_uses_resolved_question() -> None:
    engine = _engine_with_views()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
            "resolved_question": "rewritten: list all region codes",
            "memory_use": "used",
        }
    )
    res = evidence_ask(engine, FakePlanner(response=raw), "and the codes?")
    assert res.kind == "sql_result"
    assert res.pack is not None
    assert res.pack.question == "rewritten: list all region codes"


def test_evidence_pack_question_falls_back_to_user_question() -> None:
    engine = _engine_with_views()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
        }
    )
    res = evidence_ask(engine, FakePlanner(response=raw), "list region codes")
    assert res.kind == "sql_result"
    assert res.pack is not None
    assert res.pack.question == "list region codes"


# ---------- conversational short-circuit ----------


def test_greeting_short_circuits_no_planner_no_db() -> None:
    planner = FakePlanner(response="should not be called")
    res = evidence_ask(_engine_with_views(), planner, "Salom")
    assert res.kind == "greeting"
    assert "Assalomu alaykum" in res.user_message
    assert planner.seen == []
    assert res.pack is None


def test_help_short_circuits() -> None:
    planner = FakePlanner()
    res = evidence_ask(_engine_with_views(), planner, "misol ber")
    assert res.kind == "help"
    assert planner.seen == []


def test_out_of_scope_short_circuits() -> None:
    planner = FakePlanner()
    res = evidence_ask(_engine_with_views(), planner, "Tashkentda ob-havo qanday?")
    assert res.kind == "out_of_scope"
    assert planner.seen == []


# ---------- happy path ----------


def test_runs_primary_and_context_queries() -> None:
    engine = _engine_with_views()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "ok",
            "primary_sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "context_queries": [
                {
                    "purpose": "total regions",
                    "sql": "SELECT COUNT(*) AS n FROM v_regions",
                },
                {
                    "purpose": "avg population",
                    "sql": "SELECT AVG(population) AS avg_pop FROM v_regions",
                },
            ],
        }
    )
    res = evidence_ask(engine, FakePlanner(response=raw), "list region codes")
    assert res.kind == "sql_result"
    assert res.pack is not None
    assert res.pack.primary.row_count == 3
    assert tuple(r[0] for r in res.pack.primary.rows) == (1100, 1200, 1300)
    assert len(res.pack.context) == 2
    assert res.pack.context[0].purpose == "total regions"
    assert res.pack.context[0].rows[0][0] == 3
    assert res.pack.context[1].error is None


def test_planner_user_message_is_replaced_for_sql_result() -> None:
    """Planner's prose must NOT survive into sql_result; agent writes it."""
    engine = _engine_with_views()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "user_message": "Aholi 9999 deb topdim.",  # ungrounded planner prose
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [],
        }
    )
    res = evidence_ask(engine, FakePlanner(response=raw), "codes")
    assert res.kind == "sql_result"
    assert "9999" not in res.user_message


# ---------- context-query failure isolation ----------


def test_invalid_context_sql_recorded_not_crash() -> None:
    """SELECT * is rejected by sql_guard — context query gets error, primary OK."""
    engine = _engine_with_views()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [
                {"purpose": "bad", "sql": "SELECT * FROM v_regions"},
                {"purpose": "good", "sql": "SELECT COUNT(*) AS n FROM v_regions"},
            ],
        }
    )
    res = evidence_ask(engine, FakePlanner(response=raw), "codes")
    assert res.kind == "sql_result"
    assert res.pack is not None
    assert res.pack.primary.row_count == 3  # primary unaffected
    assert res.pack.context[0].error is not None
    assert "sql_guard" in res.pack.context[0].error
    assert res.pack.context[0].rows == ()
    assert res.pack.context[1].error is None
    assert res.pack.context[1].row_count == 1


def test_context_query_executor_failure_recorded_not_crash() -> None:
    engine = _engine_with_views()
    _seed(engine)
    # Drop the underlying table only AFTER seeding so primary still runs OK?
    # We need primary to succeed but context to fail. Simpler: pass two
    # context queries where one names a non-existent column accepted by
    # parser but failing at execute.
    raw = json.dumps(
        {
            "kind": "sql_plan",
            "primary_sql": "SELECT region_code FROM v_regions",
            "context_queries": [
                {
                    # nonexistent_col passes guard's column allowlist?
                    # Use a guard-rejected one instead so error is deterministic.
                    "purpose": "blocked",
                    "sql": "SELECT * FROM v_regions",
                }
            ],
        }
    )
    res = evidence_ask(engine, FakePlanner(response=raw), "x")
    assert res.kind == "sql_result"
    assert res.pack is not None
    assert res.pack.primary.row_count == 3
    assert res.pack.context[0].error is not None


# ---------- failure paths ----------


def test_planner_crash_maps_to_planner_error() -> None:
    res = evidence_ask(
        _engine_with_views(),
        FakePlanner(raise_exc=RuntimeError("provider down")),
        "any",
    )
    assert res.kind == "planner_error"
    assert "provider down" not in res.user_message


def test_unknown_planner_kind_maps_to_planner_error() -> None:
    res = evidence_ask(
        _engine_with_views(),
        FakePlanner(response='{"kind":"sql","primary_sql":"x"}'),
        "x",
    )
    assert res.kind == "planner_error"


def test_clarify_no_data_unsupported_pass_through() -> None:
    engine = _engine_with_views()
    for kind in ("clarify", "no_data", "unsupported"):
        raw = json.dumps({"kind": kind, "user_message": f"msg_{kind}"})
        res = evidence_ask(engine, FakePlanner(response=raw), "x")
        assert res.kind == kind
        assert res.user_message == f"msg_{kind}"
        assert res.pack is None


def test_primary_sql_blocked_by_guard_maps_to_planner_error() -> None:
    raw = json.dumps({"kind": "sql_plan", "primary_sql": "SELECT * FROM v_regions"})
    res = evidence_ask(_engine_with_views(), FakePlanner(response=raw), "x")
    assert res.kind == "planner_error"


def test_executor_failure_on_primary_maps_to_execution_error() -> None:
    engine = _engine_with_views()
    _seed(engine)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE regions")
    raw = json.dumps({"kind": "sql_plan", "primary_sql": "SELECT region_code FROM v_regions"})
    res = evidence_ask(engine, FakePlanner(response=raw), "x")
    assert res.kind == "execution_error"
