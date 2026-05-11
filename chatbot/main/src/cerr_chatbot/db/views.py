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


# ---------------------------------------------------------------------------
# Phase 2A: business directory views
# ---------------------------------------------------------------------------
#
# Business imports use status='completed_business' on their import_runs row so
# the CERR latest-run subquery (status='completed') keeps pointing at the CERR
# snapshot. Each business view filters to the latest business run.

BUSINESS_LATEST_RUN_SUBQUERY = (
    "(SELECT max(import_run_id) FROM import_runs WHERE status = 'completed_business')"
)


def _v_companies() -> str:
    return f"""
SELECT
    c.company_id,
    c.region_id,
    c.district_id,
    c.inn,
    c.client_code,
    c.company_name,
    c.client_type_cyr,
    c.address_raw,
    c.country_name_cyr,
    c.region_name_raw_cyr,
    c.district_name_raw_cyr,
    r.region_name_cyr,
    d.district_name_cyr,
    c.oked_label_ru,
    c.oked_label_uz
FROM business_companies c
LEFT JOIN regions r ON r.region_id = c.region_id
LEFT JOIN districts d ON d.district_id = c.district_id
WHERE c.import_run_id = {BUSINESS_LATEST_RUN_SUBQUERY}
""".strip()


def _v_tnved_categories() -> str:
    return f"""
SELECT
    t.tnved_category_id,
    t.tnved_code,
    t.chapter,
    t.heading,
    t.description_ru
FROM tnved_categories t
WHERE t.import_run_id = {BUSINESS_LATEST_RUN_SUBQUERY}
""".strip()


def _v_business_imports() -> str:
    return f"""
SELECT
    bi.business_import_id,
    bi.region_id,
    bi.district_id,
    bi.mahalla_id,
    bi.inn,
    bi.company_name,
    bi.contract_number,
    bi.declaration_number,
    bi.declaration_date,
    bi.region_name_raw_cyr,
    bi.district_name_raw_cyr,
    bi.mahalla_name_raw_cyr,
    r.region_name_cyr,
    d.district_name_cyr,
    m.mahalla_name_cyr,
    bi.tnved_code,
    bi.tnved_chapter,
    t.description_ru AS tnved_description_ru,
    bi.currency_code,
    bi.origin_country_code,
    bi.invoice_value_total,
    bi.invoice_value_item,
    bi.value_usd,
    bi.exchange_rate,
    bi.item_description
FROM business_imports bi
LEFT JOIN regions r ON r.region_id = bi.region_id
LEFT JOIN districts d ON d.district_id = bi.district_id
LEFT JOIN mahallas m ON m.mahalla_id = bi.mahalla_id
LEFT JOIN tnved_categories t
       ON t.tnved_code = bi.tnved_code
      AND t.import_run_id = {BUSINESS_LATEST_RUN_SUBQUERY}
WHERE bi.import_run_id = {BUSINESS_LATEST_RUN_SUBQUERY}
""".strip()


def _v_business_import_summaries() -> str:
    return f"""
SELECT
    s.business_import_summary_id,
    s.inn,
    s.company_name,
    s.total_import_usd,
    s.value_machines_usd,
    s.value_chemicals_usd,
    s.value_misc_goods_usd,
    s.value_industrial_usd,
    s.value_animal_oils_usd,
    s.value_non_food_raw_usd,
    s.value_building_mats_usd,
    s.value_food_products_usd,
    s.value_fruit_veg_usd,
    s.value_mineral_fuel_usd,
    s.value_beverages_tobacco_usd,
    s.value_other_goods_usd
FROM business_import_summaries s
WHERE s.import_run_id = {BUSINESS_LATEST_RUN_SUBQUERY}
""".strip()


def _v_company_density_by_district() -> str:
    """Pre-aggregated rollup: company count per (district, OKED label).

    Avoids GROUP BY in chatbot SQL for the most common business-density
    queries ('how many restaurants per district', 'company gap analysis').
    Materialised as a view (re-evaluated on read), not a real materialized view,
    so it always reflects the latest business import.
    """
    return f"""
SELECT
    c.region_id,
    c.district_id,
    r.region_name_cyr,
    d.district_name_cyr,
    c.oked_label_uz,
    c.oked_label_ru,
    COUNT(*) AS company_count
FROM business_companies c
LEFT JOIN regions r ON r.region_id = c.region_id
LEFT JOIN districts d ON d.district_id = c.district_id
WHERE c.import_run_id = {BUSINESS_LATEST_RUN_SUBQUERY}
  AND c.region_id IS NOT NULL
  AND c.district_id IS NOT NULL
  AND c.oked_label_uz IS NOT NULL
GROUP BY c.region_id, c.district_id, r.region_name_cyr, d.district_name_cyr,
         c.oked_label_uz, c.oked_label_ru
""".strip()


BUSINESS_VIEW_NAMES: tuple[str, ...] = (
    "v_tnved_categories",
    "v_companies",
    "v_business_imports",
    "v_business_import_summaries",
    "v_company_density_by_district",
)

BUSINESS_VIEW_BODIES: dict[str, str] = {
    "v_tnved_categories": _v_tnved_categories(),
    "v_companies": _v_companies(),
    "v_business_imports": _v_business_imports(),
    "v_business_import_summaries": _v_business_import_summaries(),
    "v_company_density_by_district": _v_company_density_by_district(),
}

BUSINESS_CREATE_VIEW_STATEMENTS: list[str] = [
    f"CREATE VIEW {name} AS {BUSINESS_VIEW_BODIES[name]}" for name in BUSINESS_VIEW_NAMES
]

BUSINESS_DROP_VIEW_STATEMENTS: list[str] = [
    f"DROP VIEW IF EXISTS {name}" for name in reversed(BUSINESS_VIEW_NAMES)
]
