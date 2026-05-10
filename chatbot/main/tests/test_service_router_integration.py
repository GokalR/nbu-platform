"""QueryService must short-circuit greetings/help/capability/oos.

Neither the planner nor the database is touched for these intents. The
generic placeholder for sql_result must replace the planner's prose.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query import QueryService
from cerr_chatbot.query.service import SQL_RESULT_GENERIC_INTRO


@dataclass
class FakePlanner:
    response: str = ""
    seen: list[str] = field(default_factory=list)

    def plan(self, q: str) -> str:
        self.seen.append(q)
        return self.response


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        conn.exec_driver_sql(
            "INSERT INTO regions (import_run_id, source_file, source_region_index, "
            "region_code, region_name_cyr) VALUES (1, 'f0', 0, 1100, 'Toshkent')"
        )


def test_greeting_skips_planner_and_db() -> None:
    planner = FakePlanner(response="should not be called")
    svc = QueryService(_engine_with_views(), planner)
    res = svc.ask("Salom")
    assert res.kind == "greeting"
    assert "Assalomu alaykum" in res.user_message
    assert planner.seen == []
    assert res.sql is None
    assert res.row_count == 0


def test_capability_skips_planner_and_db() -> None:
    planner = FakePlanner()
    svc = QueryService(_engine_with_views(), planner)
    res = svc.ask("Nimalarni so'rashim mumkin?")
    assert res.kind == "capability"
    assert planner.seen == []


def test_help_skips_planner_and_db() -> None:
    planner = FakePlanner()
    svc = QueryService(_engine_with_views(), planner)
    res = svc.ask("misol ber")
    assert res.kind == "help"
    assert planner.seen == []


def test_out_of_scope_skips_planner_and_db() -> None:
    planner = FakePlanner()
    svc = QueryService(_engine_with_views(), planner)
    res = svc.ask("Tashkentda bugun ob-havo qanday?")
    assert res.kind == "out_of_scope"
    assert planner.seen == []


def test_sql_result_user_message_is_generic_placeholder() -> None:
    """Planner-supplied user_message must NOT survive into sql_result."""
    engine = _engine_with_views()
    _seed(engine)
    raw = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions",
            "user_message": "Aholi soni 9999 deb topdim.",  # ungrounded — must be discarded
            "reasoning_notes": [],
        }
    )
    svc = QueryService(engine, FakePlanner(response=raw))
    res = svc.ask("region kodlari")
    assert res.kind == "sql_result"
    assert res.user_message == SQL_RESULT_GENERIC_INTRO
    assert "9999" not in res.user_message
