"""Phase 6B: planner prompt + response parser. No real LLM call."""

from __future__ import annotations

import json

import pytest

from cerr_chatbot.query import (
    PlannerDecision,
    PlannerParseError,
    build_planner_prompt,
    parse_planner_response,
    validate,
)
from cerr_chatbot.query.planner_prompt import _SQL_EXAMPLES

# -------------------- prompt builder --------------------


def test_prompt_lists_all_views_in_catalog() -> None:
    p = build_planner_prompt("anything")
    for view in (
        "v_regions",
        "v_districts",
        "v_mahallas",
        "v_district_macro_highlights",
        "v_mahalla_infrastructure",
        "v_mahalla_appeals",
        "v_mahalla_specializations",
        "v_mahalla_crops",
        "v_mahalla_subsidy_programs",
        "v_mahalla_peer_factors",
        "v_data_quality_issues",
        "v_latest_import_run",
    ):
        assert f"## {view}" in p


def test_prompt_states_sql_is_not_mandatory() -> None:
    p = build_planner_prompt("anything")
    assert "SQL is NOT mandatory" in p
    assert '"clarify"' in p
    assert '"refuse"' in p
    assert '"no_data"' in p


def test_prompt_includes_safety_warnings() -> None:
    p = build_planner_prompt("anything")
    assert "NULL means source missing" in p or "NULL means source" in p
    assert "natural keys" in p.lower() or "natural-key" in p.lower() or "Never join by" in p
    assert "semantic views" in p.lower()
    # Surrogate ids called out as the only allowed join keys.
    assert "region_id" in p and "district_id" in p and "mahalla_id" in p
    # Refuse rules mention the dangerous verbs.
    assert "INSERT" in p and "DELETE" in p and "DROP" in p
    # Estimation explicitly forbidden.
    assert "estimate" in p.lower() or "guess" in p.lower()


def test_prompt_embeds_user_question() -> None:
    p = build_planner_prompt("how many mahallas in region 1100?")
    assert "how many mahallas in region 1100?" in p


def test_prompt_contains_planner_sql_cookbook() -> None:
    p = build_planner_prompt("anything")
    assert "HOW TO WRITE SQL FOR THIS DATABASE" in p
    assert "SQL COOKBOOK EXAMPLES" in p
    assert p.count("SQL EXAMPLE ") >= 20
    assert len(_SQL_EXAMPLES) >= 20


def test_prompt_explains_indicator_key_metrics_are_not_no_data() -> None:
    p = build_planner_prompt("industry_volume_bln_uzs")
    assert "indicator_key = '<metric_key>'" in p
    assert "industry_volume_bln_uzs" in p
    assert "export_volume_mln_usd" in p
    assert "Do NOT return no_data for a metric that exists as indicator_key" in p


def test_prompt_explains_peer_factor_patterns_are_not_no_data() -> None:
    p = build_planner_prompt("peer strengths")
    assert "v_mahalla_peer_factors" in p
    assert "factor_polarity = 'strength'" in p
    assert "factor_polarity = 'weakness'" in p
    assert "Do NOT return no_data for known factor_key" in p


def test_prompt_explains_data_quality_duplicate_patterns() -> None:
    p = build_planner_prompt("duplicates")
    assert "v_data_quality_issues" in p
    assert "MAHALLA_STIR_DUPLICATE" in p
    assert "DISTRICT_CODE_DUPLICATE_GLOBAL" in p


def test_prompt_tells_planner_to_select_useful_columns() -> None:
    p = build_planner_prompt("anything")
    assert "Select useful answer columns" in p
    assert "region_name_cyr" in p
    assert "district_name_cyr" in p
    assert "mahalla_name_cyr" in p


def test_all_sql_cookbook_examples_pass_sql_guard() -> None:
    for _title, sql in _SQL_EXAMPLES:
        validate(sql)


# -------------------- parser: accept paths --------------------


def _wrap(kind: str, **extra: object) -> str:
    body: dict = {"kind": kind, "sql": None, "user_message": "ok", "reasoning_notes": []}
    body.update(extra)
    return json.dumps(body)


def test_clear_numeric_question_yields_sql_decision_validated() -> None:
    raw = _wrap(
        "sql",
        sql="SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5",
        user_message="Top 5 regions by population.",
        reasoning_notes=["population is on v_regions"],
        expected_result_shape="5 rows",
    )
    d = parse_planner_response(raw)
    assert isinstance(d, PlannerDecision)
    assert d.kind == "sql"
    assert d.sql is not None
    assert "v_regions" in d.sql
    assert d.expected_result_shape == "5 rows"


def test_clarify_decision_parsed() -> None:
    raw = _wrap(
        "clarify",
        user_message="Which region?",
        reasoning_notes=["entity ambiguous"],
    )
    d = parse_planner_response(raw)
    assert d.kind == "clarify"
    assert d.sql is None
    assert d.user_message == "Which region?"


def test_refuse_decision_parsed() -> None:
    raw = _wrap(
        "refuse",
        user_message="Write operations are not allowed.",
        reasoning_notes=["delete refused"],
    )
    d = parse_planner_response(raw)
    assert d.kind == "refuse"
    assert d.sql is None


def test_no_data_decision_parsed() -> None:
    raw = _wrap(
        "no_data",
        user_message="GDP not in catalog.",
        reasoning_notes=["no GDP column"],
    )
    d = parse_planner_response(raw)
    assert d.kind == "no_data"
    assert d.sql is None


# -------------------- parser: reject paths --------------------


def test_malformed_json_rejected() -> None:
    with pytest.raises(PlannerParseError, match="not valid JSON"):
        parse_planner_response("{not json")


def test_empty_response_rejected() -> None:
    with pytest.raises(PlannerParseError, match="empty"):
        parse_planner_response("")


def test_unknown_kind_rejected() -> None:
    with pytest.raises(PlannerParseError, match="unknown kind"):
        parse_planner_response('{"kind": "magic", "sql": null, "user_message": "x"}')


def test_missing_user_message_rejected() -> None:
    with pytest.raises(PlannerParseError, match="user_message"):
        parse_planner_response('{"kind": "clarify", "sql": null, "user_message": ""}')


def test_kind_sql_with_null_sql_rejected() -> None:
    raw = _wrap("sql", sql=None, user_message="x")
    with pytest.raises(PlannerParseError, match="non-empty sql"):
        parse_planner_response(raw)


def test_non_sql_kind_with_sql_string_rejected() -> None:
    raw = _wrap("clarify", sql="SELECT 1 FROM v_regions", user_message="x")
    with pytest.raises(PlannerParseError, match="must have sql=null"):
        parse_planner_response(raw)


def test_planner_sql_using_natural_key_join_rejected() -> None:
    """Planner output joining by district_code is killed by sql_guard."""
    raw = _wrap(
        "sql",
        sql=(
            "SELECT m.mahalla_id "
            "FROM v_mahallas m JOIN v_districts d ON d.district_code = m.district_code"
        ),
        user_message="x",
    )
    with pytest.raises(PlannerParseError, match="JOIN ON column not allowed"):
        parse_planner_response(raw)


def test_planner_sql_with_unknown_column_rejected() -> None:
    raw = _wrap(
        "sql",
        sql="SELECT made_up_column FROM v_regions",
        user_message="x",
    )
    with pytest.raises(PlannerParseError, match="unknown column"):
        parse_planner_response(raw)


def test_planner_sql_select_star_rejected() -> None:
    raw = _wrap("sql", sql="SELECT * FROM v_regions", user_message="x")
    with pytest.raises(PlannerParseError, match="SELECT \\*"):
        parse_planner_response(raw)


def test_planner_sql_dml_rejected_via_guard() -> None:
    raw = _wrap("sql", sql="DROP TABLE regions", user_message="x")
    with pytest.raises(PlannerParseError, match="only SELECT"):
        parse_planner_response(raw)


def test_reasoning_notes_must_be_list_of_strings() -> None:
    raw = _wrap("clarify", user_message="x", reasoning_notes="oops")
    with pytest.raises(PlannerParseError, match="must be a list"):
        parse_planner_response(raw)
    raw = _wrap("clarify", user_message="x", reasoning_notes=[1, 2])
    with pytest.raises(PlannerParseError, match="entries must be strings"):
        parse_planner_response(raw)


# -------------------- Phase 6E.2 post-eval targeted SQL pattern coverage --------------------


def _example_by_substring(needle: str) -> str:
    for _, sql in _SQL_EXAMPLES:
        if needle in sql:
            return sql
    raise AssertionError(f"no SQL example contains substring: {needle!r}")


def test_duplicate_stir_sample_example_uses_order_by_mahalla_stir() -> None:
    sample_examples = [
        s for _, s in _SQL_EXAMPLES if "MAHALLA_STIR_DUPLICATE" in s and "LIMIT 5" in s
    ]
    assert sample_examples
    for s in sample_examples:
        assert "ORDER BY mahalla_stir" in s, s


def test_macro_missing_example_includes_total_districts_scalar_subquery() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "highlighted_missing_flag" in s]
    assert matches
    assert any("(SELECT COUNT(*) FROM v_districts) AS total_districts" in s for s in matches)


def test_road_extreme_example_includes_road_asphalt_km() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "ORDER BY road_total_km DESC" in s]
    assert matches
    assert any("road_asphalt_km" in s for s in matches), matches


def test_crime_appeals_example_groups_by_region_only() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "SUM(crime_appeal_count)" in s]
    assert matches
    for s in matches:
        assert "GROUP BY region_name_cyr" in s, s
        assert "district_name_cyr" not in s.split("GROUP BY", 1)[1]


def test_specialization_type_example_uses_limit_100_not_1() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "GROUP BY specialization_type_cyr" in s]
    assert matches
    for s in matches:
        assert "LIMIT 100" in s, s
        assert not s.rstrip().endswith("LIMIT 1"), s


def test_specialization_direction_example_uses_limit_10_with_rows_count() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "GROUP BY specialization_direction_cyr" in s]
    assert matches
    for s in matches:
        assert "COUNT(*) AS rows" in s, s
        assert "LIMIT 10" in s, s


def test_subsidy_example_includes_rows_and_null_application_rows() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "subsidy_program_label_cyr" in s and "GROUP BY" in s]
    assert matches
    for s in matches:
        assert "COUNT(*) AS rows" in s, s
        assert "null_application_rows" in s, s


def test_data_quality_example_includes_total_issues_scalar_subquery() -> None:
    matches = [
        s
        for _, s in _SQL_EXAMPLES
        if ("GROUP BY q.issue_code" in s) or ("GROUP BY issue_code" in s)
    ]
    assert matches
    assert any("(SELECT COUNT(*) FROM v_data_quality_issues) AS total_issues" in s for s in matches)


def test_crop_missing_example_includes_negative_homestead_count() -> None:
    matches = [s for _, s in _SQL_EXAMPLES if "missing_total_area_rows" in s]
    assert matches
    for s in matches:
        assert "negative_homestead_area_count" in s, s


def test_writing_guide_lists_grouping_top_n_and_missing_rules() -> None:
    p = build_planner_prompt("anything")
    assert "GROUPING RULES" in p
    assert "GROUP BY region_name_cyr ONLY" in p
    assert "TOP-N AND DISTRIBUTION LIMITS" in p
    assert "do not use limit 1" in p.lower()
    assert "SAMPLE / EXAMPLE QUERIES" in p
    assert "stable ORDER BY" in p
    assert "MISSING / NULL / NEGATIVE QUESTIONS" in p
    assert "ma'lumot yo'q" in p


# `test_all_sql_cookbook_examples_pass_sql_guard` is defined earlier; targeted
# pattern tests above cover the post-eval fixes.
