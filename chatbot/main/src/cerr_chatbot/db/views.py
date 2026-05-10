"""Phase 5 semantic SQL views.

Read-only curated layer over raw import tables. Every view filters to the
latest completed import_run_id so chatbot reads see one consistent snapshot.

This module is the source of truth for view DDL. The Alembic revision
imports `CREATE_VIEW_STATEMENTS` / `DROP_VIEW_STATEMENTS` and executes them
verbatim, so a single edit here updates production + tests.
"""

from __future__ import annotations

# Scalar subquery resolving to the latest completed import_run_id. Inlined
# (no CTE) for portability across SQLite and PostgreSQL.
LATEST_RUN_SUBQUERY = "(SELECT max(import_run_id) FROM import_runs WHERE status = 'completed')"

# Six base KPIs profiled in Phase 2B2 - present on every entity level.
_BASE_KPIS = (
    "population",
    "active_businesses",
    "unemployed",
    "rating_score",
    "problem_loans",
    "poor_families",
)


def _kpi_pivot(level: str, fk_col: str) -> str:
    cases = ",\n           ".join(
        f"MAX(CASE WHEN kpi_key = '{k}' THEN kpi_value_num END) AS {k}" for k in _BASE_KPIS
    )
    return f"""
SELECT {fk_col},
           {cases}
    FROM entity_kpis
    WHERE entity_level = '{level}'
      AND import_run_id = {LATEST_RUN_SUBQUERY}
    GROUP BY {fk_col}
""".strip()


VIEW_NAMES: tuple[str, ...] = (
    "v_latest_import_run",
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
)


def _v_latest_import_run() -> str:
    return f"""
SELECT import_run_id, started_at, completed_at, source_dir, source_file_count
FROM import_runs
WHERE import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_regions() -> str:
    pivot = _kpi_pivot("region", "region_id")
    return f"""
SELECT
    r.region_id,
    r.region_code,
    r.region_name_cyr,
    r.declared_district_count,
    r.actual_district_count,
    r.declared_mahalla_count,
    r.actual_mahalla_count,
    CASE
        WHEN r.declared_mahalla_count IS NULL
          OR r.actual_mahalla_count IS NULL THEN NULL
        WHEN r.declared_mahalla_count <> r.actual_mahalla_count THEN 1
        ELSE 0
    END AS mahalla_count_mismatch_flag,
    k.population,
    k.active_businesses,
    k.unemployed,
    k.rating_score,
    k.problem_loans,
    k.poor_families
FROM regions r
LEFT JOIN ({pivot}) k ON k.region_id = r.region_id
WHERE r.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_districts() -> str:
    pivot = _kpi_pivot("district", "district_id")
    return f"""
SELECT
    d.district_id,
    d.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    d.declared_mahalla_count,
    d.actual_mahalla_count,
    d.macro_period_label_cyr,
    k.population,
    k.active_businesses,
    k.unemployed,
    k.rating_score,
    k.problem_loans,
    k.poor_families
FROM districts d
LEFT JOIN regions r ON r.region_id = d.region_id
LEFT JOIN ({pivot}) k ON k.district_id = d.district_id
WHERE d.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahallas() -> str:
    pivot = _kpi_pivot("mahalla", "mahalla_id")
    return f"""
SELECT
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    m.rating_score AS rating_position,
    m.district_rank_text,
    m.region_rank_text,
    m.category_label_cyr,
    m.status_label_cyr,
    m.specialization_residual_percent,
    m.specialization_total_known_percent,
    m.crop_total_homestead_area_sotkah,
    m.peer_set_count,
    m.peer_set_description_cyr,
    m.peer_fallback_to_district_flag,
    m.peer_indicator_count,
    m.peer_total_indicators_considered,
    k.population,
    k.active_businesses,
    k.unemployed,
    k.rating_score,
    k.problem_loans,
    k.poor_families
FROM mahallas m
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
LEFT JOIN ({pivot}) k ON k.mahalla_id = m.mahalla_id
WHERE m.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_district_macro_highlights() -> str:
    return f"""
SELECT
    i.macro_indicator_id,
    d.district_id,
    d.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    i.indicator_key,
    i.indicator_label_cyr,
    i.indicator_unit,
    i.indicator_direction,
    i.period_label_cyr,
    i.highlighted_value_num,
    i.highlighted_missing_flag,
    i.highlighted_value_null_flag
FROM district_macro_indicators i
JOIN districts d ON d.district_id = i.district_id
LEFT JOIN regions r ON r.region_id = d.region_id
WHERE i.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahalla_infrastructure() -> str:
    return f"""
SELECT
    x.infrastructure_row_id,
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    x.road_total_km,
    x.road_dirt_km,
    x.road_asphalt_km,
    x.households_without_drinking_water_count,
    x.power_outage_count,
    x.power_outage_hours_text,
    x.medical_facility_distance_km,
    x.school_count,
    x.sports_facility_count,
    x.kindergarten_count,
    x.homestead_area_ha
FROM mahalla_infrastructure x
JOIN mahallas m ON m.mahalla_id = x.mahalla_id
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
WHERE x.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahalla_appeals() -> str:
    return f"""
SELECT
    x.appeal_row_id,
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    x.crime_appeal_count,
    x.divorce_appeal_count,
    x.social_aid_appeal_count,
    x.employment_appeal_count,
    x.gas_appeal_count,
    x.registry_appeal_count,
    x.appeals_year,
    x.appeals_period_label_cyr
FROM mahalla_appeals x
JOIN mahallas m ON m.mahalla_id = x.mahalla_id
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
WHERE x.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahalla_specializations() -> str:
    return f"""
SELECT
    x.specialization_id,
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    x.item_order,
    x.specialization_slot,
    x.specialization_slot_label_cyr,
    x.specialization_type_cyr,
    x.specialization_direction_cyr,
    x.household_count,
    x.population_count,
    x.share_percent
FROM mahalla_specializations x
JOIN mahallas m ON m.mahalla_id = x.mahalla_id
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
WHERE x.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahalla_crops() -> str:
    return f"""
SELECT
    x.crop_season_id,
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    x.season_order,
    x.season_key,
    x.season_label_cyr,
    x.crops_text_cyr,
    x.total_area_ha,
    x.homestead_area_ha,
    x.household_count
FROM mahalla_crops x
JOIN mahallas m ON m.mahalla_id = x.mahalla_id
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
WHERE x.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahalla_subsidy_programs() -> str:
    return f"""
SELECT
    x.subsidy_program_id,
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    x.program_order,
    x.subsidy_program_label_cyr,
    x.application_count,
    x.required_amount_mln_uzs,
    x.has_amount_source_flag,
    x.subsidies_year,
    x.subsidies_data_date
FROM mahalla_subsidy_programs x
JOIN mahallas m ON m.mahalla_id = x.mahalla_id
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
WHERE x.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_mahalla_peer_factors() -> str:
    return f"""
SELECT
    x.peer_factor_id,
    m.mahalla_id,
    m.district_id,
    m.region_id,
    r.region_code,
    r.region_name_cyr,
    d.district_code,
    d.district_name_cyr,
    m.mahalla_stir,
    m.mahalla_name_cyr,
    x.factor_polarity,
    x.factor_order,
    x.factor_key,
    x.factor_label_cyr,
    x.factor_unit,
    x.factor_direction,
    x.entity_value_num,
    x.comparison_average_value,
    x.peer_rank,
    x.peer_count,
    x.percentile
FROM mahalla_peer_factors x
JOIN mahallas m ON m.mahalla_id = x.mahalla_id
LEFT JOIN regions r ON r.region_id = m.region_id
LEFT JOIN districts d ON d.district_id = m.district_id
WHERE x.import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


def _v_data_quality_issues() -> str:
    return f"""
SELECT
    issue_id,
    import_run_id,
    severity,
    issue_code,
    message,
    source_file,
    region_code,
    district_code,
    mahalla_stir,
    source_json_path
FROM data_quality_issues
WHERE import_run_id = {LATEST_RUN_SUBQUERY}
""".strip()


VIEW_BODIES: dict[str, str] = {
    "v_latest_import_run": _v_latest_import_run(),
    "v_regions": _v_regions(),
    "v_districts": _v_districts(),
    "v_mahallas": _v_mahallas(),
    "v_district_macro_highlights": _v_district_macro_highlights(),
    "v_mahalla_infrastructure": _v_mahalla_infrastructure(),
    "v_mahalla_appeals": _v_mahalla_appeals(),
    "v_mahalla_specializations": _v_mahalla_specializations(),
    "v_mahalla_crops": _v_mahalla_crops(),
    "v_mahalla_subsidy_programs": _v_mahalla_subsidy_programs(),
    "v_mahalla_peer_factors": _v_mahalla_peer_factors(),
    "v_data_quality_issues": _v_data_quality_issues(),
}

CREATE_VIEW_STATEMENTS: list[str] = [
    f"CREATE VIEW {name} AS {VIEW_BODIES[name]}" for name in VIEW_NAMES
]

# Drop in reverse order; safe with IF EXISTS so re-runs do not fail.
DROP_VIEW_STATEMENTS: list[str] = [f"DROP VIEW IF EXISTS {name}" for name in reversed(VIEW_NAMES)]
