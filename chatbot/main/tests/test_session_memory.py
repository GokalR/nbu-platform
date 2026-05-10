"""Phase 2 session memory: in-process store + snapshot builder."""

from __future__ import annotations

from datetime import datetime

from cerr_chatbot.query.evidence import (
    EvidencePack,
    EvidenceQueryResult,
    EvidenceServiceResult,
)
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
    MemorySnapshot,
    build_snapshot_from_evidence_result,
)


def _snapshot(question: str = "q") -> MemorySnapshot:
    return MemorySnapshot(
        last_question=question,
        last_resolved_question=question,
        last_answer_type="sql_result",
        last_columns=("a",),
        last_row_count=1,
        last_result_summary="row_count=1; columns=a",
        created_at="2026-05-10T00:00:00+00:00",
    )


def _sql_result(
    columns: tuple[str, ...] = ("region_name_cyr", "population"),
    rows: tuple[tuple[object, ...], ...] = (("Toshkent", 3000000),),
) -> EvidenceServiceResult:
    primary = EvidenceQueryResult(
        purpose="primary",
        sql="SELECT region_name_cyr, population FROM v_regions",
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )
    return EvidenceServiceResult(
        kind="sql_result",
        user_message="ok",
        pack=EvidencePack(question="orig", primary=primary, context=()),
    )


# ---------- store ----------


def test_set_and_get_returns_snapshot() -> None:
    store = InMemorySessionMemoryStore()
    snap = _snapshot()
    store.set("s1", snap)
    assert store.get("s1") == snap


def test_get_missing_session_returns_none() -> None:
    store = InMemorySessionMemoryStore()
    assert store.get("nope") is None


def test_clear_removes_session() -> None:
    store = InMemorySessionMemoryStore()
    store.set("s1", _snapshot())
    store.clear("s1")
    assert store.get("s1") is None


def test_clear_missing_session_is_noop() -> None:
    store = InMemorySessionMemoryStore()
    store.clear("never-set")
    assert store.get("never-set") is None


def test_sessions_are_isolated() -> None:
    store = InMemorySessionMemoryStore()
    a = _snapshot("qa")
    b = _snapshot("qb")
    store.set("s1", a)
    store.set("s2", b)
    assert store.get("s1") == a
    assert store.get("s2") == b
    store.clear("s1")
    assert store.get("s1") is None
    assert store.get("s2") == b


def test_set_overwrites_previous_snapshot() -> None:
    store = InMemorySessionMemoryStore()
    store.set("s1", _snapshot("first"))
    store.set("s1", _snapshot("second"))
    got = store.get("s1")
    assert got is not None
    assert got.last_question == "second"


# ---------- snapshot builder ----------


def test_build_snapshot_for_sql_result() -> None:
    res = _sql_result()
    snap = build_snapshot_from_evidence_result(
        original_question="aholisi",
        resolved_question="Toshkent viloyati aholisi",
        result=res,
    )
    assert snap is not None
    assert snap.last_question == "aholisi"
    assert snap.last_resolved_question == "Toshkent viloyati aholisi"
    assert snap.last_answer_type == "sql_result"
    assert snap.last_columns == ("region_name_cyr", "population")
    assert snap.last_row_count == 1
    assert snap.last_result_summary == "row_count=1; columns=region_name_cyr,population"


def test_snapshot_does_not_include_sql_or_rows() -> None:
    res = _sql_result(rows=(("Toshkent", 3000000), ("Andijon", 3100000)))
    snap = build_snapshot_from_evidence_result(
        original_question="q", resolved_question="q", result=res
    )
    assert snap is not None
    fields = vars(snap)
    serialized = repr(fields)
    assert "SELECT" not in serialized
    assert "v_regions" not in serialized
    assert "Toshkent" not in serialized
    assert "3000000" not in serialized
    assert not any(name == "rows" for name in fields)
    assert not any(name == "sql" for name in fields)


def test_snapshot_uses_resolved_question() -> None:
    res = _sql_result()
    snap = build_snapshot_from_evidence_result(
        original_question="va aholisi?",
        resolved_question="Toshkent viloyatining aholisi",
        result=res,
    )
    assert snap is not None
    assert snap.last_resolved_question == "Toshkent viloyatining aholisi"
    assert snap.last_question == "va aholisi?"


def test_snapshot_created_at_is_iso_utc() -> None:
    res = _sql_result()
    snap = build_snapshot_from_evidence_result(
        original_question="q", resolved_question="q", result=res
    )
    assert snap is not None
    assert snap.created_at
    parsed = datetime.fromisoformat(snap.created_at)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None
    assert parsed.utcoffset().total_seconds() == 0  # type: ignore[union-attr]


def test_build_snapshot_for_clarify_pending_context() -> None:
    res = EvidenceServiceResult(
        kind="clarify",
        user_message="Samarqand bo'yicha qaysi ko'rsatkich kerak?",
    )
    snap = build_snapshot_from_evidence_result(
        original_question="Samarqand haqida ma'lumot ber",
        resolved_question="Samarqand haqida ma'lumot ber",
        result=res,
    )
    assert snap is not None
    assert snap.last_question == "Samarqand haqida ma'lumot ber"
    assert snap.last_resolved_question == "Samarqand haqida ma'lumot ber"
    assert snap.last_answer_type == "clarify"
    assert snap.last_columns == ()
    assert snap.last_row_count == 0
    assert "pending_clarification=true" in snap.last_result_summary
    assert "Samarqand bo'yicha" in snap.last_result_summary


def test_build_returns_none_for_non_memorable_kinds() -> None:
    for kind in (
        "no_data",
        "unsupported",
        "planner_error",
        "execution_error",
        "greeting",
        "help",
        "capability",
        "out_of_scope",
    ):
        res = EvidenceServiceResult(kind=kind, user_message="x")  # type: ignore[arg-type]
        snap = build_snapshot_from_evidence_result(
            original_question="q", resolved_question="q", result=res
        )
        assert snap is None, kind


def test_build_returns_none_when_pack_missing() -> None:
    res = EvidenceServiceResult(kind="sql_result", user_message="x", pack=None)
    snap = build_snapshot_from_evidence_result(
        original_question="q", resolved_question="q", result=res
    )
    assert snap is None


def test_snapshot_summary_handles_zero_rows_and_no_columns() -> None:
    res = _sql_result(columns=(), rows=())
    snap = build_snapshot_from_evidence_result(
        original_question="q", resolved_question="q", result=res
    )
    assert snap is not None
    assert snap.last_row_count == 0
    assert snap.last_columns == ()
    assert snap.last_result_summary == "row_count=0; columns="
