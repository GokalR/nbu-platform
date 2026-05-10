"""Eval runner: parser, scorer, end-to-end with stub planner."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.eval import (
    EvalCase,
    parse_questions_md,
    run_eval,
    score_case,
    write_eval_json,
    write_eval_markdown,
)
from cerr_chatbot.query import QueryService

# -------- parser --------


def test_parser_extracts_thirty_cases() -> None:
    cases = parse_questions_md("questions_uz_latn.md")
    assert len(cases) == 30
    assert cases[0].case_number == 1
    assert cases[-1].case_number == 30


def test_parser_preserves_expected_answer_block_with_table() -> None:
    cases = parse_questions_md("questions_uz_latn.md")
    by_num = {c.case_number: c for c in cases}
    case2 = by_num[2]
    # Table headers + Cyrillic source name preserved.
    assert "region_code" in case2.expected_answer
    assert "Андижон вилояти" in case2.expected_answer
    assert "879" in case2.expected_answer


def test_parser_handles_minimal_synthetic_md(tmp_path: Path) -> None:
    p = tmp_path / "qs.md"
    p.write_text(
        "# Header\n\n"
        "## 1. T1\n\n**Question:** Q1\n\n**Expected answer:** 42\n\n"
        "## 2. T2\n\n**Question:** Q2\n\n**Expected answer:**\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )
    cases = parse_questions_md(p)
    assert len(cases) == 2
    assert cases[0].title == "T1"
    assert cases[0].question == "Q1"
    assert "42" in cases[0].expected_answer
    assert "| 1 | 2 |" in cases[1].expected_answer


# -------- scorer --------


def test_scorer_passes_when_all_numeric_tokens_present() -> None:
    expected = "Total: 138. Population 4330143."
    actual = "Qaytarilgan qatorlar: 1.\n\n| pop |\n|---|\n| 4330143 |\n\nJami: 138."
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_fails_on_missing_numeric_token() -> None:
    expected = "Population 4330143."
    actual = "Qaytarilgan qatorlar: 0.\n"
    passed, reasons = score_case(expected, "sql_result", actual)
    assert not passed
    assert any("4330143" in r for r in reasons)


def test_scorer_fails_when_kind_is_not_sql_for_numeric_question() -> None:
    expected = "138 ta muammo."
    actual = "Iltimos, viloyatni aniqlashtiring."
    for k in ("clarify", "no_data", "unsupported", "planner_error", "execution_error"):
        passed, reasons = score_case(expected, k, actual)
        assert not passed, k


def test_scorer_detects_null_marker_swapped_for_zero() -> None:
    expected = "Andijon: ma'lumot yo'q. 1234 jami."
    # Actual hides the missing value as 0 - must fail.
    actual = "| Andijon | 0 |\n| jami | 1234 |\n"
    passed, reasons = score_case(expected, "sql_result", actual)
    assert not passed
    assert any("ma'lumot yo'q" in r for r in reasons)


def test_scorer_passes_when_null_marker_preserved() -> None:
    expected = "Andijon: ma'lumot yo'q. 1234 jami."
    actual = "| Andijon | ma'lumot yo'q |\n| jami | 1234 |\n"
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_requires_duplicate_token_multiplicity() -> None:
    expected = "5 ta. 5 ta. 5 ta."  # token "5" expected 3x
    actual = "5 ta."
    passed, reasons = score_case(expected, "sql_result", actual)
    assert not passed


def test_scorer_ignores_rank_column_in_table() -> None:
    expected = (
        "| rank | region_name_cyr | population |\n"
        "|---:|---|---:|\n"
        "| 1 | Andijon | 4330143 |\n"
        "| 2 | Fargona | 4204055 |\n"
    )
    actual = (
        "| region_name_cyr | population |\n"
        "|---|---:|\n"
        "| Andijon | 4330143 |\n"
        "| Fargona | 4204055 |\n"
    )
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_ignores_implicit_rank_sequence_without_header() -> None:
    expected = (
        "| n | region | metric |\n"
        "|---:|---|---:|\n"
        "| 1 | A | 100 |\n"
        "| 2 | B | 200 |\n"
        "| 3 | C | 300 |\n"
    )
    actual = "| region | metric |\n|---|---:|\n| A | 100 |\n| B | 200 |\n| C | 300 |\n"
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_normalizes_int_and_float() -> None:
    expected = "rating 1.0, count 50."
    actual = "Rating: 1; count 50.0."
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_table_followed_by_prose_extracts_both() -> None:
    expected = "| rank | val |\n|---:|---:|\n| 1 | 999 |\n\nJami: 138."
    actual = "ok 999 ... 138 muammo"
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


# -------- end-to-end runner with stub planners --------


@dataclass
class _StubPlanner:
    """Returns canned JSON for matched questions; otherwise refuse."""

    rules: list[tuple[str, str]] = field(default_factory=list)

    def plan(self, q: str) -> str:
        for needle, response in self.rules:
            if needle in q:
                return response
        return '{"kind":"refuse","sql":null,"user_message":"Yo\'q"}'


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _seed_run(engine, region_codes=(1100, 1200)) -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for idx, code in enumerate(region_codes):
            conn.exec_driver_sql(
                "INSERT INTO regions (import_run_id, source_file, source_region_index, "
                "region_code, region_name_cyr) "
                f"VALUES (1, 'f{idx}', 0, {code}, 'R')"
            )


def test_eval_runner_marks_matching_sql_result_as_passed() -> None:
    engine = _engine_with_views()
    _seed_run(engine, region_codes=(1100, 1200))
    sql_response = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "user_message": "Region kodlari.",
        }
    )
    planner = _StubPlanner(rules=[("kodlari", sql_response)])
    service = QueryService(engine, planner)
    cases = [
        EvalCase(
            case_number=1,
            title="codes",
            question="Region kodlari?",
            expected_answer="Kodlari: 1100 va 1200.",
        )
    ]
    report = run_eval(service, cases)
    assert report.total == 1
    assert report.passed == 1
    assert report.failed == 0
    assert report.cases[0].service_kind == "sql_result"
    assert report.cases[0].row_count == 2


def test_eval_runner_marks_missing_token_as_failed() -> None:
    engine = _engine_with_views()
    _seed_run(engine, region_codes=(1100,))  # only one region
    sql_response = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions",
            "user_message": "Region kodlari.",
        }
    )
    planner = _StubPlanner(rules=[("kodlari", sql_response)])
    service = QueryService(engine, planner)
    cases = [
        EvalCase(
            case_number=1,
            title="codes",
            question="Region kodlari?",
            expected_answer="Kodlari: 1100 va 1200.",  # 1200 will be missing
        )
    ]
    report = run_eval(service, cases)
    assert report.failed == 1
    assert any("1200" in r for r in report.cases[0].failure_reasons)


def test_eval_runner_marks_clarify_for_numeric_expected_as_failed() -> None:
    engine = _engine_with_views()
    planner = _StubPlanner(
        rules=[("?", '{"kind":"clarify","sql":null,"user_message":"Aniqlashtiring"}')]
    )
    service = QueryService(engine, planner)
    cases = [
        EvalCase(1, "n", "Nechta?", "138 ta."),
    ]
    report = run_eval(service, cases)
    assert report.failed == 1
    assert "clarify" in report.cases[0].failure_reasons[0]


def test_eval_runner_writes_json_and_md_reports(tmp_path: Path) -> None:
    engine = _engine_with_views()
    _seed_run(engine)
    sql_response = json.dumps(
        {
            "kind": "sql",
            "sql": "SELECT region_code FROM v_regions ORDER BY region_code",
            "user_message": "ok",
        }
    )
    planner = _StubPlanner(rules=[("kodlari", sql_response)])
    service = QueryService(engine, planner)
    cases = [EvalCase(1, "t", "Region kodlari?", "1100, 1200")]
    report = run_eval(service, cases)
    report.questions_path = "synthetic"

    json_path = write_eval_json(report, tmp_path / "eval_reports")
    md_path = write_eval_markdown(report, tmp_path / "eval_reports")

    assert json_path.exists()
    assert md_path.exists()
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    assert parsed["total"] == 1
    assert parsed["cases"][0]["passed"] is True
    md = md_path.read_text(encoding="utf-8")
    assert "PASS" in md
    assert "**Question:** Region kodlari?" in md


def test_eval_runner_uses_stub_planner_no_network() -> None:
    """Sanity: stub planner is the only path; no LlmPlanner instantiated."""
    engine = _engine_with_views()
    seen: list[str] = []

    @dataclass
    class _CountingPlanner:
        def plan(self, q: str) -> str:
            seen.append(q)
            return '{"kind":"refuse","sql":null,"user_message":"Yo\'q"}'

    service = QueryService(engine, _CountingPlanner())
    cases = [EvalCase(1, "t", "Q1", "no numbers"), EvalCase(2, "t", "Q2", "no numbers")]
    run_eval(service, cases)
    assert seen == ["Q1", "Q2"]


# -------- Phase 6E.2: scorer max(prose, table) merge --------


def test_scorer_does_not_double_count_when_prose_repeats_table_fact() -> None:
    """Prose-stated fact that also appears in table cells must not be counted twice."""
    expected = (
        "All 10 below have rating_score = 1.0.\n\n"
        "| region | rating_score |\n"
        "|---|---:|\n"
        "| A | 1.0 |\n| B | 1.0 |\n| C | 1.0 |\n| D | 1.0 |\n| E | 1.0 |\n"
        "| F | 1.0 |\n| G | 1.0 |\n| H | 1.0 |\n| I | 1.0 |\n| J | 1.0 |\n"
    )
    actual = (
        "Quyidagi 10 mahallaning rating_score = 1.0.\n\n"
        "| region | rating_score |\n"
        "|---|---:|\n"
        "| A | 1.0 |\n| B | 1.0 |\n| C | 1.0 |\n| D | 1.0 |\n| E | 1.0 |\n"
        "| F | 1.0 |\n| G | 1.0 |\n| H | 1.0 |\n| I | 1.0 |\n| J | 1.0 |\n"
    )
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_table_count_overrides_prose_count_when_table_has_more() -> None:
    """Prose says token once; table has it 5 times; required = max(1, 5) = 5."""
    expected = "Note: 138 ta jami.\n\n| n |\n|---:|\n| 138 |\n| 138 |\n| 138 |\n| 138 |\n| 138 |\n"
    actual = "jami 138; 138 138 138 138"
    passed, reasons = score_case(expected, "sql_result", actual)
    assert passed, reasons


def test_scorer_still_fails_when_prose_count_exceeds_actual_without_table() -> None:
    """Plain prose duplicates with no table still required at full count."""
    expected = "5 ta. 5 ta. 5 ta."
    actual = "5 ta."
    passed, reasons = score_case(expected, "sql_result", actual)
    assert not passed
