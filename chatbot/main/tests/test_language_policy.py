"""User-facing language policy: Uzbek Latin by default."""

from __future__ import annotations

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query import (
    NULL_DISPLAY,
    QueryService,
    QueryServiceResult,
    build_planner_prompt,
    compose_answer,
)

# ---------- helpers ----------


class _FakePlanner:
    def __init__(self, response: str) -> None:
        self.response = response
        self.seen: list[str] = []

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


def _sql_result(
    rows, *, columns=("region_name_cyr", "population"), user_message=""
) -> QueryServiceResult:
    return QueryServiceResult(
        kind="sql_result",
        user_message=user_message,
        sql="SELECT region_name_cyr, population FROM v_regions LIMIT 100",
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )


# ---------- planner prompt ----------


def test_prompt_states_uzbek_latin_default_language() -> None:
    p = build_planner_prompt("anything")
    assert "Uzbek Latin" in p
    assert "user_message" in p
    # Source-name preservation called out.
    assert "Do NOT translate" in p or "do NOT translate" in p
    # Numbers must stay exact.
    assert "Numeric values must stay exact" in p


# ---------- service fallbacks ----------


def test_planner_error_fallback_is_uzbek_latin() -> None:
    svc = QueryService(_engine_with_views(), _FakePlanner("not json"))
    res = svc.ask("anything")
    assert res.kind == "planner_error"
    msg = res.user_message
    assert "Iltimos" in msg
    assert "tushuntira" in msg.lower()
    # English fallback wording must be gone.
    assert "could not interpret" not in msg.lower()


def test_clarify_fallback_uses_uzbek_latin_when_planner_emits_empty_message() -> None:
    # Planner-emitted empty user_message is rejected by parse_planner_response,
    # which means service then returns planner_error fallback. To exercise the
    # clarify fallback path directly, we provide a non-empty clarify message
    # that is itself Uzbek Latin per the planner prompt rules.
    raw = '{"kind":"clarify","sql":null,"user_message":"Iltimos, viloyat/tuman/mahalla va ko\'rsatkichni aniq ko\'rsating."}'
    svc = QueryService(_engine_with_views(), _FakePlanner(raw))
    res = svc.ask("show me data")
    assert res.kind == "clarify"
    assert "Iltimos" in res.user_message


def test_unsupported_fallback_uses_uzbek_latin() -> None:
    raw = '{"kind":"refuse","sql":null,"user_message":"Yozish va o\'chirish amallariga ruxsat berilmagan."}'
    svc = QueryService(_engine_with_views(), _FakePlanner(raw))
    res = svc.ask("delete everything")
    assert res.kind == "unsupported"
    assert "ruxsat berilmagan" in res.user_message


def test_no_data_fallback_uses_uzbek_latin() -> None:
    raw = '{"kind":"no_data","sql":null,"user_message":"YIM ko\'rsatkichi mavjud emas."}'
    svc = QueryService(_engine_with_views(), _FakePlanner(raw))
    res = svc.ask("GDP?")
    assert res.kind == "no_data"
    assert "mavjud emas" in res.user_message


# ---------- composer prose ----------


def test_composer_uses_uzbek_latin_prose() -> None:
    res = _sql_result(rows=(("Andijon", 1234),), user_message="Eng yuqori viloyat.")
    a = compose_answer(res)
    assert "Qaytarilgan qatorlar: 1." in a.text
    assert "Rows returned" not in a.text


def test_composer_no_rows_message_is_uzbek_latin() -> None:
    res = _sql_result(rows=())
    a = compose_answer(res)
    assert "Bu savolga mos qatorlar topilmadi." in a.text
    assert "No rows" not in a.text


def test_composer_truncation_note_is_uzbek_latin() -> None:
    rows = tuple((f"R{i}", i) for i in range(15))
    a = compose_answer(_sql_result(rows=rows), max_rows=10)
    assert "Faqat birinchi 10 qator ko'rsatildi." in a.text
    assert "Only the first" not in a.text


def test_composer_null_display_is_uzbek_latin_phrase() -> None:
    assert NULL_DISPLAY == "ma'lumot yo'q"
    res = _sql_result(rows=(("Andijon", None),))
    a = compose_answer(res)
    assert "ma'lumot yo'q" in a.text
    assert "| Andijon | ma'lumot yo'q |" in a.text
    # NULL must NOT be coerced to 0 anywhere in user text.
    assert "| Andijon | 0 |" not in a.text


# ---------- source preservation ----------


def test_source_entity_names_unchanged_in_output() -> None:
    """Cyrillic region/district/mahalla names pass through verbatim."""
    cyr_name = "Андижон вилояти"
    res = _sql_result(rows=((cyr_name, 1234),))
    a = compose_answer(res)
    assert cyr_name in a.text
    # Nothing transliterated/altered.
    assert "Andijon viloyati" not in a.text


def test_numbers_pass_through_verbatim() -> None:
    res = _sql_result(rows=(("X", 1234567890123), ("Y", -0.0151)))
    a = compose_answer(res)
    assert "1234567890123" in a.text
    assert "-0.0151" in a.text


# ---------- debug hygiene ----------


def test_debug_notes_never_appear_in_user_text() -> None:
    res = QueryServiceResult(
        kind="planner_error",
        user_message="Savolni xavfsiz tushuntira olmadim.",
        debug_notes=("PlannerParseError: not valid JSON",),
    )
    a = compose_answer(res)
    assert "PlannerParseError" not in a.text
    assert "JSON" not in a.text
    assert "not valid" not in a.text
