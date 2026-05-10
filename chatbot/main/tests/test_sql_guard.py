"""Tests for Phase 6A: sql_guard validator + executor."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS
from cerr_chatbot.query import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    SqlGuardError,
    execute,
    validate,
)


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


# ----------------------- validator: accept paths -----------------------


def test_valid_select_passes() -> None:
    v = validate("SELECT region_id, region_name_cyr FROM v_regions")
    assert v.referenced_views == ("v_regions",)
    assert v.limit_appended is True
    assert "LIMIT 100" in v.validated_sql.upper().replace("\n", " ")


def test_existing_limit_within_range_kept() -> None:
    v = validate("SELECT region_id FROM v_regions LIMIT 50")
    assert v.limit_appended is False
    assert "LIMIT 50" in v.validated_sql.upper()


def test_join_between_allowed_views_by_surrogate_id() -> None:
    sql = (
        "SELECT m.mahalla_id, d.district_id "
        "FROM v_mahallas m JOIN v_districts d ON d.district_id = m.district_id "
        "LIMIT 10"
    )
    v = validate(sql)
    assert "v_districts" in v.referenced_views
    assert "v_mahallas" in v.referenced_views


def test_cte_over_allowed_view_accepted() -> None:
    sql = (
        "WITH top_regions AS ("
        "  SELECT region_id, population FROM v_regions ORDER BY population DESC LIMIT 5"
        ") SELECT region_id, population FROM top_regions"
    )
    v = validate(sql)
    assert v.referenced_views == ("v_regions",)


def test_count_star_in_aggregate_is_allowed() -> None:
    v = validate("SELECT COUNT(*) FROM v_regions")
    assert v.referenced_views == ("v_regions",)


# ----------------------- validator: reject paths -----------------------


def test_select_star_rejected() -> None:
    with pytest.raises(SqlGuardError, match="SELECT \\*"):
        validate("SELECT * FROM v_regions")


def test_raw_table_rejected() -> None:
    with pytest.raises(SqlGuardError, match="not in allowed semantic catalog"):
        validate("SELECT region_id FROM regions LIMIT 1")


def test_unknown_view_rejected() -> None:
    with pytest.raises(SqlGuardError, match="not in allowed"):
        validate("SELECT 1 FROM v_does_not_exist")


def test_ddl_rejected() -> None:
    with pytest.raises(SqlGuardError, match="only SELECT"):
        validate("DROP TABLE regions")


def test_dml_rejected() -> None:
    with pytest.raises(SqlGuardError, match="only SELECT"):
        validate("DELETE FROM regions WHERE 1=1")


def test_insert_rejected() -> None:
    with pytest.raises(SqlGuardError, match="only SELECT"):
        validate("INSERT INTO v_regions (region_id) VALUES (1)")


def test_pragma_rejected() -> None:
    with pytest.raises(SqlGuardError):
        validate("PRAGMA table_info(regions)")


def test_multiple_statements_rejected() -> None:
    with pytest.raises(SqlGuardError, match="one statement"):
        validate("SELECT 1 FROM v_regions; SELECT 1 FROM v_regions")


def test_dash_comment_rejected() -> None:
    with pytest.raises(SqlGuardError, match="comments"):
        validate("SELECT region_id FROM v_regions -- sneaky\nLIMIT 1")


def test_block_comment_rejected() -> None:
    with pytest.raises(SqlGuardError, match="comments"):
        validate("SELECT region_id FROM v_regions /* sneaky */ LIMIT 1")


def test_limit_above_max_rejected() -> None:
    with pytest.raises(SqlGuardError, match=f"exceeds max {MAX_LIMIT}"):
        validate(f"SELECT region_id FROM v_regions LIMIT {MAX_LIMIT + 1}")


def test_limit_zero_rejected() -> None:
    with pytest.raises(SqlGuardError, match="LIMIT must be > 0"):
        validate("SELECT region_id FROM v_regions LIMIT 0")


def test_cte_touching_raw_table_rejected() -> None:
    sql = "WITH bad AS (SELECT region_id FROM regions) SELECT region_id FROM bad"
    with pytest.raises(SqlGuardError, match="not in allowed"):
        validate(sql)


def test_query_with_no_view_rejected() -> None:
    with pytest.raises(SqlGuardError):
        validate("SELECT 1")


def test_default_limit_constant_value() -> None:
    assert DEFAULT_LIMIT == 100
    assert MAX_LIMIT == 500


# ----------------------- executor -----------------------


def test_executor_runs_simple_select() -> None:
    engine = _engine_with_views()
    # Insert one ImportRun + Region so the latest-run filter has data.
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        conn.exec_driver_sql(
            "INSERT INTO regions "
            "(import_run_id, source_file, source_region_index, region_code, region_name_cyr, "
            " declared_district_count, declared_mahalla_count, actual_district_count, actual_mahalla_count) "
            "VALUES (1, 't', 0, 1100, 'R1', 1, 1, 1, 1)"
        )
    res = execute(engine, "SELECT region_id, region_code FROM v_regions")
    assert res.columns == ("region_id", "region_code")
    assert res.row_count == 1
    assert res.rows[0][1] == 1100
    assert res.limit_appended is True


def test_executor_returns_columns_and_rows_with_explicit_limit() -> None:
    engine = _engine_with_views()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        for idx, code in enumerate((1100, 1200)):
            conn.exec_driver_sql(
                "INSERT INTO regions "
                "(import_run_id, source_file, source_region_index, region_code, region_name_cyr) "
                f"VALUES (1, 'f{idx}', 0, {code}, 'R')"
            )
    res = execute(
        engine,
        "SELECT region_code FROM v_regions ORDER BY region_code LIMIT 5",
    )
    assert res.row_count == 2
    assert res.limit_appended is False
    assert tuple(r[0] for r in res.rows) == (1100, 1200)


def test_executor_blocks_dml_before_query() -> None:
    engine = _engine_with_views()
    # Pre-state: zero import_runs.
    with engine.connect() as conn:
        before = conn.exec_driver_sql("SELECT COUNT(*) FROM import_runs").scalar_one()
    assert before == 0

    with pytest.raises(SqlGuardError):
        execute(engine, "DELETE FROM import_runs")

    with engine.connect() as conn:
        after = conn.exec_driver_sql("SELECT COUNT(*) FROM import_runs").scalar_one()
    assert after == 0  # row count unchanged


def test_executor_blocks_dml_inside_view_string() -> None:
    """Even if the LLM tries to embed DML in the same string, validate() rejects."""
    engine = _engine_with_views()
    with pytest.raises(SqlGuardError, match="one statement"):
        execute(
            engine,
            "SELECT 1 FROM v_regions; DELETE FROM regions",
        )

    with pytest.raises(SqlGuardError):
        execute(engine, "DROP TABLE regions")


# ----------------------- Phase 6A.1: hardening -----------------------


def test_cross_join_rejected() -> None:
    with pytest.raises(SqlGuardError, match="CROSS JOIN"):
        validate("SELECT a.region_id FROM v_regions a CROSS JOIN v_districts b LIMIT 1")


def test_comma_join_rejected() -> None:
    with pytest.raises(SqlGuardError, match="ON or USING"):
        validate("SELECT a.region_id FROM v_regions a, v_districts b LIMIT 1")


def test_join_without_on_rejected() -> None:
    with pytest.raises(SqlGuardError, match="ON or USING"):
        validate("SELECT a.region_id FROM v_regions a JOIN v_districts b LIMIT 1")


def test_join_with_using_accepted() -> None:
    v = validate("SELECT a.region_id FROM v_regions a JOIN v_districts b USING (region_id) LIMIT 1")
    assert "v_regions" in v.referenced_views


def test_more_than_max_joins_rejected() -> None:
    sql = (
        "SELECT m.mahalla_id FROM v_mahallas m "
        "JOIN v_districts d1 ON d1.district_id = m.district_id "
        "JOIN v_regions r1 ON r1.region_id = m.region_id "
        "JOIN v_mahalla_infrastructure i ON i.mahalla_id = m.mahalla_id "
        "JOIN v_mahalla_appeals ap ON ap.mahalla_id = m.mahalla_id "
        "JOIN v_mahalla_crops c ON c.mahalla_id = m.mahalla_id "
        "LIMIT 1"
    )
    with pytest.raises(SqlGuardError, match="too many JOINs"):
        validate(sql)


def test_aggregate_functions_accepted() -> None:
    for q in (
        "SELECT SUM(population) FROM v_regions",
        "SELECT AVG(rating_score) FROM v_districts",
        "SELECT COUNT(*) FROM v_mahallas",
        "SELECT MIN(rating_score), MAX(rating_score), ROUND(AVG(rating_score), 2) FROM v_mahallas",
        "SELECT ROUND(CAST(AVG(population) AS NUMERIC), 2) AS avg_population FROM v_regions",
    ):
        validate(q)


def test_pg_sleep_rejected() -> None:
    with pytest.raises(SqlGuardError, match="function not allowed: pg_sleep"):
        validate("SELECT pg_sleep(1) FROM v_regions")


def test_random_function_rejected() -> None:
    with pytest.raises(SqlGuardError, match="function not allowed"):
        validate("SELECT random() FROM v_regions")


def test_sqlite_version_rejected() -> None:
    with pytest.raises(SqlGuardError, match="function not allowed"):
        validate("SELECT sqlite_version() FROM v_regions")


def test_load_extension_rejected() -> None:
    with pytest.raises(SqlGuardError, match="function not allowed"):
        validate("SELECT load_extension('evil') FROM v_regions")


def test_window_function_rejected() -> None:
    with pytest.raises(SqlGuardError, match="window functions"):
        validate("SELECT row_number() OVER () AS rn FROM v_regions")


def test_recursive_cte_rejected() -> None:
    with pytest.raises(SqlGuardError, match="RECURSIVE"):
        validate(
            "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM r) SELECT n FROM r LIMIT 5"
        )


def test_aggregate_query_executes_against_views() -> None:
    engine = _engine_with_views()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
        conn.exec_driver_sql(
            "INSERT INTO regions "
            "(import_run_id, source_file, source_region_index, region_code) "
            "VALUES (1, 'a', 0, 1100), (1, 'b', 0, 1200), (1, 'c', 0, 1300)"
        )
    res = execute(engine, "SELECT COUNT(*) AS n FROM v_regions")
    assert res.row_count == 1
    assert res.rows[0][0] == 3


# ----------------------- Phase 6A.2: column allowlist + surrogate joins -----------------------


def test_unknown_column_rejected_single_view() -> None:
    with pytest.raises(SqlGuardError, match="unknown column"):
        validate("SELECT made_up_column FROM v_regions")


def test_unknown_qualified_column_rejected() -> None:
    with pytest.raises(SqlGuardError, match="unknown column: v_regions.nope"):
        validate("SELECT r.nope FROM v_regions r")


def test_unqualified_column_in_one_view_query_accepted() -> None:
    v = validate("SELECT region_id, region_code, population FROM v_regions WHERE region_code > 1")
    assert v.referenced_views == ("v_regions",)


def test_ambiguous_unqualified_column_in_multi_view_rejected() -> None:
    sql = (
        "SELECT region_id "  # unqualified, ambiguous between m and d
        "FROM v_mahallas m JOIN v_districts d ON d.district_id = m.district_id"
    )
    with pytest.raises(SqlGuardError, match="unqualified column in multi-view"):
        validate(sql)


def test_aggregate_alias_used_in_order_by_accepted() -> None:
    v = validate("SELECT COUNT(*) AS n FROM v_mahallas ORDER BY n DESC")
    assert v.referenced_views == ("v_mahallas",)


def test_unknown_alias_rejected() -> None:
    with pytest.raises(SqlGuardError, match="unknown table alias"):
        validate("SELECT x.region_id FROM v_regions r")


def test_join_by_mahalla_id_accepted() -> None:
    v = validate(
        "SELECT m.mahalla_id, i.road_total_km "
        "FROM v_mahallas m JOIN v_mahalla_infrastructure i "
        "ON i.mahalla_id = m.mahalla_id"
    )
    assert "v_mahallas" in v.referenced_views


def test_join_by_district_id_accepted() -> None:
    v = validate(
        "SELECT m.mahalla_id, d.district_id "
        "FROM v_mahallas m JOIN v_districts d ON d.district_id = m.district_id"
    )
    assert "v_districts" in v.referenced_views


def test_join_by_mahalla_stir_rejected() -> None:
    with pytest.raises(SqlGuardError, match="JOIN ON column not allowed"):
        validate(
            "SELECT m.mahalla_id "
            "FROM v_mahallas m JOIN v_mahalla_appeals a "
            "ON a.mahalla_stir = m.mahalla_stir"
        )


def test_join_by_district_code_rejected() -> None:
    with pytest.raises(SqlGuardError, match="JOIN ON column not allowed"):
        validate(
            "SELECT m.mahalla_id "
            "FROM v_mahallas m JOIN v_districts d "
            "ON d.district_code = m.district_code"
        )


def test_join_by_name_rejected() -> None:
    with pytest.raises(SqlGuardError, match="JOIN ON column not allowed"):
        validate(
            "SELECT m.mahalla_id "
            "FROM v_mahallas m JOIN v_districts d "
            "ON d.district_name_cyr = m.district_name_cyr"
        )


def test_join_on_with_literal_rejected() -> None:
    with pytest.raises(SqlGuardError, match="compare two columns"):
        validate("SELECT m.mahalla_id FROM v_mahallas m JOIN v_districts d ON 1 = 1")


def test_using_district_id_accepted() -> None:
    v = validate("SELECT a.mahalla_id FROM v_mahallas a JOIN v_districts d USING (district_id)")
    assert "v_districts" in v.referenced_views


def test_using_mahalla_stir_rejected() -> None:
    with pytest.raises(SqlGuardError, match="USING column not allowed"):
        validate(
            "SELECT a.mahalla_id FROM v_mahallas a JOIN v_mahalla_appeals b USING (mahalla_stir)"
        )


def test_join_on_anded_surrogates_accepted() -> None:
    v = validate(
        "SELECT m.mahalla_id "
        "FROM v_mahallas m JOIN v_districts d "
        "ON d.district_id = m.district_id AND d.region_id = m.region_id"
    )
    assert v.referenced_views == ("v_districts", "v_mahallas")


# ----------------------- Phase 6A.3: CTE output validation -----------------------


def test_cte_referencing_inner_select_alias_accepted() -> None:
    sql = "WITH x AS (SELECT region_id FROM v_regions) SELECT x.region_id FROM x"
    v = validate(sql)
    assert "v_regions" in v.referenced_views


def test_cte_unknown_qualified_column_rejected() -> None:
    sql = "WITH x AS (SELECT region_id FROM v_regions) SELECT x.nope FROM x"
    with pytest.raises(SqlGuardError, match="unknown CTE column: x.nope"):
        validate(sql)


def test_cte_explicit_column_list_accepted() -> None:
    sql = "WITH x(a) AS (SELECT region_id FROM v_regions) SELECT x.a FROM x"
    v = validate(sql)
    assert v.referenced_views == ("v_regions",)


def test_cte_explicit_column_list_renames_inner_columns() -> None:
    sql = "WITH x(a) AS (SELECT region_id FROM v_regions) SELECT x.region_id FROM x"
    with pytest.raises(SqlGuardError, match="unknown CTE column: x.region_id"):
        validate(sql)


def test_cte_duplicate_exported_names_rejected() -> None:
    sql = "WITH x(a, a) AS (SELECT region_id, region_code FROM v_regions) SELECT x.a FROM x"
    with pytest.raises(SqlGuardError, match="duplicate column names"):
        validate(sql)


def test_cte_duplicate_inferred_names_rejected() -> None:
    """If two projections expose the same name, exports collide."""
    sql = "WITH x AS (SELECT region_id, region_id FROM v_regions) SELECT x.region_id FROM x"
    with pytest.raises(SqlGuardError, match="duplicate column names"):
        validate(sql)


def test_cte_body_touching_raw_table_still_rejected() -> None:
    sql = "WITH bad AS (SELECT region_id FROM regions) SELECT bad.region_id FROM bad"
    with pytest.raises(SqlGuardError, match="not in allowed"):
        validate(sql)


def test_cte_with_aggregate_alias_export_accepted() -> None:
    sql = (
        "WITH x AS (SELECT region_id, COUNT(*) AS n FROM v_regions GROUP BY region_id) "
        "SELECT x.region_id, x.n FROM x ORDER BY x.n DESC"
    )
    v = validate(sql)
    assert v.referenced_views == ("v_regions",)


def test_executor_passes_default_limit_through_render() -> None:
    engine = _engine_with_views()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO import_runs (started_at, source_dir, status) "
            "VALUES ('2026-05-10 00:00:00', 't', 'completed')"
        )
    res = execute(engine, "SELECT 1 AS one FROM v_regions")
    # LIMIT 100 was appended by the validator and reaches the engine.
    assert "LIMIT 100" in res.validated_sql.upper().replace("\n", " ")
