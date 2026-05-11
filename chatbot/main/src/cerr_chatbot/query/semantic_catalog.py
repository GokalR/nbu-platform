"""Machine-readable catalog of semantic SQL views.

Source of truth for what an LLM (or any consumer) is allowed to read and how
to interpret each column. Mirrors the SQL DDL in `cerr_chatbot.db.views` and
the prose in `docs/SEMANTIC_VIEWS.md`. Tests assert all three stay aligned.

Hard rules surfaced via `GLOBAL_WARNINGS` and per-view `warnings`:
- Never join on natural keys (mahalla_stir, district_code, names).
- Always join on surrogate ids (mahalla_id, district_id, region_id).
- NULL means source missing/unavailable, never zero.
- Geo and AI insights are intentionally not exposed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

GLOBAL_WARNINGS: tuple[str, ...] = (
    "Do NOT join by mahalla_stir, district_code, or any name column.",
    "Always join via surrogate ids: mahalla_id, district_id, region_id.",
    "NULL means source missing/unavailable, NOT zero. Do not COALESCE to 0.",
    "AI insights and geometries are not exposed in this catalog.",
    "Every view filters to the latest completed import_run only.",
)


@dataclass(frozen=True)
class SemanticViewColumn:
    name: str
    description: str
    nullable: bool = True


@dataclass(frozen=True)
class SemanticView:
    name: str
    grain: str
    purpose: str
    columns: tuple[SemanticViewColumn, ...]
    join_keys: tuple[str, ...] = ()
    use_cases: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    examples: tuple[str, ...] = field(default_factory=tuple)


# Reusable column blocks ------------------------------------------------------

_KPI_COLS: tuple[SemanticViewColumn, ...] = (
    SemanticViewColumn("population", "Population KPI value (count of people)."),
    SemanticViewColumn("active_businesses", "Active business count KPI."),
    SemanticViewColumn("unemployed", "Unemployed person count KPI."),
    SemanticViewColumn(
        "rating_score",
        "Composite rating score KPI (0-100). May differ from raw column on mahallas.",
    ),
    SemanticViewColumn("problem_loans", "Problem-loans count KPI."),
    SemanticViewColumn("poor_families", "Poor-family count KPI."),
)

_LOC_COLS: tuple[SemanticViewColumn, ...] = (
    SemanticViewColumn(
        "region_code",
        "Source region code (4-digit OKTMO prefix). NOT unique - 0 dup groups but kept non-PK.",
    ),
    SemanticViewColumn("region_name_cyr", "Region display name in Cyrillic."),
    SemanticViewColumn(
        "district_code", "Source district code. NOT globally unique (3 dup groups)."
    ),
    SemanticViewColumn("district_name_cyr", "District display name in Cyrillic."),
    SemanticViewColumn(
        "mahalla_stir", "Mahalla 9-digit STIR. NOT globally unique (127 dup groups)."
    ),
    SemanticViewColumn("mahalla_name_cyr", "Mahalla display name in Cyrillic."),
)


# Views ----------------------------------------------------------------------

V_LATEST_IMPORT_RUN = SemanticView(
    name="v_latest_import_run",
    grain="exactly one row: the latest completed import_run",
    purpose="Inspect which import snapshot every other view is currently exposing.",
    columns=(
        SemanticViewColumn(
            "import_run_id", "Surrogate id of the latest completed run.", nullable=False
        ),
        SemanticViewColumn("started_at", "When the importer began.", nullable=False),
        SemanticViewColumn("completed_at", "When the importer finished. NULL if still running."),
        SemanticViewColumn("source_dir", "Source directory the run read from.", nullable=False),
        SemanticViewColumn("source_file_count", "Number of region JSON files discovered."),
    ),
    use_cases=("show snapshot timestamp", "diagnose stale data"),
    examples=("SELECT import_run_id, completed_at FROM v_latest_import_run;",),
)

V_REGIONS = SemanticView(
    name="v_regions",
    grain="one row per region in the latest completed run",
    purpose="Region-level entity row plus 6 base KPIs and a count-mismatch flag.",
    columns=(
        SemanticViewColumn("region_id", "Surrogate region id.", nullable=False),
        SemanticViewColumn("region_code", _LOC_COLS[0].description),
        SemanticViewColumn("region_name_cyr", _LOC_COLS[1].description),
        SemanticViewColumn("declared_district_count", "Districts count claimed by source."),
        SemanticViewColumn("actual_district_count", "Districts actually nested in source."),
        SemanticViewColumn("declared_mahalla_count", "Mahalla count claimed by source."),
        SemanticViewColumn("actual_mahalla_count", "Mahallas actually nested in source."),
        SemanticViewColumn(
            "mahalla_count_mismatch_flag",
            "Tri-state: 1 if declared <> actual, 0 if equal, NULL if either side unknown.",
        ),
        *_KPI_COLS,
    ),
    join_keys=("region_id",),
    use_cases=("rank regions by KPI", "show region overview", "flag declared vs actual mismatches"),
    warnings=("Do not assume mismatch = 0; treat NULL distinctly.",),
    examples=(
        "SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5;",
        "SELECT region_name_cyr, mahalla_count_mismatch_flag FROM v_regions WHERE mahalla_count_mismatch_flag = 1;",
    ),
)

V_DISTRICTS = SemanticView(
    name="v_districts",
    grain="one row per district in the latest completed run",
    purpose="District entity row joined with parent region + 6 base KPIs.",
    columns=(
        SemanticViewColumn("district_id", "Surrogate district id.", nullable=False),
        SemanticViewColumn("region_id", "Surrogate parent region id.", nullable=False),
        *_LOC_COLS[:4],  # region_code, region_name_cyr, district_code, district_name_cyr
        SemanticViewColumn(
            "declared_mahalla_count", "Mahalla count claimed by source for this district."
        ),
        SemanticViewColumn("actual_mahalla_count", "Mahallas actually nested under this district."),
        SemanticViewColumn(
            "macro_period_label_cyr", "Reporting period label from district macro block."
        ),
        *_KPI_COLS,
    ),
    join_keys=("district_id", "region_id"),
    use_cases=("rank districts within a region", "filter districts by KPI"),
    examples=(
        "SELECT district_name_cyr, rating_score FROM v_districts WHERE region_id = 1 ORDER BY rating_score DESC;",
    ),
)

V_MAHALLAS = SemanticView(
    name="v_mahallas",
    grain="one row per mahalla in the latest completed run",
    purpose="Mahalla entity row plus parents, summary scalars, and 6 base KPIs.",
    columns=(
        SemanticViewColumn("mahalla_id", "Surrogate mahalla id.", nullable=False),
        SemanticViewColumn("district_id", "Surrogate parent district id.", nullable=False),
        SemanticViewColumn("region_id", "Surrogate parent region id.", nullable=False),
        *_LOC_COLS,
        SemanticViewColumn(
            "rating_position",
            "Raw source position/rank-like value from the mahalla row. This is not the 0-100 KPI score.",
        ),
        SemanticViewColumn("district_rank_text", "Source-formatted district rank, e.g. '3/11'."),
        SemanticViewColumn("region_rank_text", "Source-formatted region rank, e.g. '35/304'."),
        SemanticViewColumn("category_label_cyr", "Mahalla category label in Cyrillic."),
        SemanticViewColumn(
            "status_label_cyr",
            "Status badge value lifted from header.meta where the label exactly equals the source word for 'status' (Cyrillic 'Статус').",
        ),
        SemanticViewColumn(
            "specialization_residual_percent",
            "Percent of population not in any listed specialization.",
        ),
        SemanticViewColumn(
            "specialization_total_known_percent",
            "Sum of share_percent across known specialization slots.",
        ),
        SemanticViewColumn(
            "crop_total_homestead_area_sotkah",
            "Total homestead area in sotkah (1 ha = 100 sotkah).",
        ),
        SemanticViewColumn("peer_set_count", "Number of peer mahallas considered."),
        SemanticViewColumn(
            "peer_set_description_cyr", "Free-form peer-set description in Cyrillic."
        ),
        SemanticViewColumn(
            "peer_fallback_to_district_flag",
            "True when peer selection fell back to whole district.",
        ),
        SemanticViewColumn("peer_indicator_count", "Indicators that produced a peer comparison."),
        SemanticViewColumn("peer_total_indicators_considered", "Indicators evaluated in total."),
        SemanticViewColumn("population", _KPI_COLS[0].description),
        SemanticViewColumn("active_businesses", _KPI_COLS[1].description),
        SemanticViewColumn("unemployed", _KPI_COLS[2].description),
        SemanticViewColumn("rating_score", _KPI_COLS[3].description),
        SemanticViewColumn("problem_loans", _KPI_COLS[4].description),
        SemanticViewColumn("poor_families", _KPI_COLS[5].description),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("rank mahallas", "filter by status/category", "join to detail views by mahalla_id"),
    warnings=(
        "For mahalla quality/reyting questions, use rating_score (0-100 KPI), not rating_position.",
    ),
    examples=(
        "SELECT mahalla_name_cyr, rating_score FROM v_mahallas WHERE region_id = 1 ORDER BY rating_score DESC LIMIT 10;",
        "SELECT mahalla_name_cyr, rating_position FROM v_mahallas ORDER BY rating_position ASC LIMIT 10;",
        "SELECT mahalla_name_cyr, status_label_cyr FROM v_mahallas WHERE category_label_cyr LIKE '1%';",
    ),
)

V_DISTRICT_MACRO_HIGHLIGHTS = SemanticView(
    name="v_district_macro_highlights",
    grain="one row per (district, macro indicator) in the latest completed run",
    purpose="District macro indicator with the highlighted (current-district) value pre-extracted.",
    columns=(
        SemanticViewColumn("macro_indicator_id", "Surrogate indicator row id.", nullable=False),
        SemanticViewColumn("district_id", "Surrogate parent district id.", nullable=False),
        SemanticViewColumn("region_id", "Surrogate parent region id.", nullable=False),
        *_LOC_COLS[:4],
        SemanticViewColumn(
            "indicator_key", "Stable indicator id, e.g. industry_volume_bln_uzs.", nullable=False
        ),
        SemanticViewColumn("indicator_label_cyr", "Indicator label in Cyrillic."),
        SemanticViewColumn(
            "indicator_unit",
            "Source unit string. Cyrillic in current data (e.g. billion UZS, percent, thousand UZS). Keep as-is.",
        ),
        SemanticViewColumn("indicator_direction", "Polarity: up/down/neu."),
        SemanticViewColumn(
            "period_label_cyr", "Reporting period label from parent district macro block."
        ),
        SemanticViewColumn(
            "highlighted_value_num",
            "Value of the source point flagged highlighted=true. NULL when missing or value-null.",
        ),
        SemanticViewColumn(
            "highlighted_missing_flag",
            "True when source had no point flagged highlighted=true.",
        ),
        SemanticViewColumn(
            "highlighted_value_null_flag",
            "True when highlighted point exists but its value is null/non-numeric.",
        ),
    ),
    join_keys=("district_id", "region_id"),
    use_cases=(
        "show macro indicators per district",
        "explain why a district has no current value (missing vs null)",
    ),
    warnings=(
        "Rows with highlighted_missing_flag=true are kept; do NOT filter them out blindly.",
        "highlighted_value_num is NEVER inferred from a non-highlighted point.",
    ),
    examples=(
        "SELECT district_name_cyr, indicator_key, highlighted_value_num "
        "FROM v_district_macro_highlights WHERE indicator_key = 'industry_volume_bln_uzs';",
    ),
)


def _flat_detail_columns(extras: tuple[SemanticViewColumn, ...]) -> tuple[SemanticViewColumn, ...]:
    base = (
        SemanticViewColumn("mahalla_id", "Surrogate parent mahalla id.", nullable=False),
        SemanticViewColumn("district_id", "Surrogate parent district id.", nullable=False),
        SemanticViewColumn("region_id", "Surrogate parent region id.", nullable=False),
        *_LOC_COLS,
    )
    return base + extras


V_MAHALLA_INFRASTRUCTURE = SemanticView(
    name="v_mahalla_infrastructure",
    grain="one row per mahalla infrastructure block in the latest completed run",
    purpose="Mahalla infrastructure scalars joined with parent identifiers.",
    columns=(
        SemanticViewColumn("infrastructure_row_id", "Surrogate row id.", nullable=False),
        *_flat_detail_columns(
            (
                SemanticViewColumn(
                    "road_total_km",
                    "Total road length, km. Source has extreme values; do not range-clip blindly.",
                ),
                SemanticViewColumn("road_dirt_km", "Dirt-road length, km."),
                SemanticViewColumn("road_asphalt_km", "Asphalt-road length, km."),
                SemanticViewColumn(
                    "households_without_drinking_water_count",
                    "Households without drinking water access.",
                ),
                SemanticViewColumn("power_outage_count", "Outage count in reporting period."),
                SemanticViewColumn(
                    "power_outage_hours_text",
                    "Free-form outage hours text. Parse before numeric use.",
                ),
                SemanticViewColumn(
                    "medical_facility_distance_km", "Distance to nearest medical facility, km."
                ),
                SemanticViewColumn("school_count", "Schools in the mahalla."),
                SemanticViewColumn("sports_facility_count", "Sports facilities in the mahalla."),
                SemanticViewColumn("kindergarten_count", "Kindergartens in the mahalla."),
                SemanticViewColumn(
                    "homestead_area_ha", "Total homestead (tomorqa) area, hectares."
                ),
            )
        ),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("rank mahallas by infra metric", "answer factual infra questions"),
)

V_MAHALLA_APPEALS = SemanticView(
    name="v_mahalla_appeals",
    grain="one row per mahalla appeals block in the latest completed run",
    purpose="Per-mahalla appeal counts by category for one reporting period.",
    columns=(
        SemanticViewColumn("appeal_row_id", "Surrogate row id.", nullable=False),
        *_flat_detail_columns(
            (
                SemanticViewColumn("crime_appeal_count", "Crime-related appeal count."),
                SemanticViewColumn(
                    "divorce_appeal_count", "Divorce-related appeal count. Often NULL."
                ),
                SemanticViewColumn("social_aid_appeal_count", "Social aid (yordam) appeal count."),
                SemanticViewColumn("employment_appeal_count", "Employment appeal count."),
                SemanticViewColumn("gas_appeal_count", "Gas-supply appeal count."),
                SemanticViewColumn(
                    "registry_appeal_count", "Civil-registry appeal count. Often NULL."
                ),
                SemanticViewColumn("appeals_year", "Reporting year."),
                SemanticViewColumn(
                    "appeals_period_label_cyr", "Reporting period label in Cyrillic."
                ),
            )
        ),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("show appeal volumes", "compare appeal categories across mahallas"),
)

V_MAHALLA_SPECIALIZATIONS = SemanticView(
    name="v_mahalla_specializations",
    grain="one row per (mahalla, specialization slot)",
    purpose="Specialization slots for each mahalla, in source order.",
    columns=(
        SemanticViewColumn("specialization_id", "Surrogate row id.", nullable=False),
        *_flat_detail_columns(
            (
                SemanticViewColumn(
                    "item_order", "Source order index within the mahalla.", nullable=False
                ),
                SemanticViewColumn("specialization_slot", "Slot key, e.g. main, add_2."),
                SemanticViewColumn("specialization_slot_label_cyr", "Slot label in Cyrillic."),
                SemanticViewColumn("specialization_type_cyr", "High-level specialization type."),
                SemanticViewColumn("specialization_direction_cyr", "Specialization sub-direction."),
                SemanticViewColumn("household_count", "Households engaged in this slot."),
                SemanticViewColumn("population_count", "Population engaged in this slot."),
                SemanticViewColumn("share_percent", "Share of total mahalla population, percent."),
            )
        ),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("answer 'what does mahalla X specialize in?'",),
)

V_MAHALLA_CROPS = SemanticView(
    name="v_mahalla_crops",
    grain="one row per (mahalla, crop season)",
    purpose="Crop season summary per mahalla, in source order.",
    columns=(
        SemanticViewColumn("crop_season_id", "Surrogate row id.", nullable=False),
        *_flat_detail_columns(
            (
                SemanticViewColumn(
                    "season_order", "Source order index within the mahalla.", nullable=False
                ),
                SemanticViewColumn("season_key", "Season key: main, repeat, winter_sown."),
                SemanticViewColumn("season_label_cyr", "Season label in Cyrillic."),
                SemanticViewColumn(
                    "crops_text_cyr", "Free-form crop list in Cyrillic. Often NULL."
                ),
                SemanticViewColumn(
                    "total_area_ha",
                    "Total cultivated area, hectares. 100% NULL in current source - confirm before use.",
                ),
                SemanticViewColumn("homestead_area_ha", "Homestead area for the season, hectares."),
                SemanticViewColumn("household_count", "Households cultivating in this season."),
            )
        ),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("answer 'how big is mahalla X homestead area in main season?'",),
    warnings=("crops_text_cyr and total_area_ha are mostly/entirely null in current source.",),
)

V_MAHALLA_SUBSIDY_PROGRAMS = SemanticView(
    name="v_mahalla_subsidy_programs",
    grain="one row per (mahalla, subsidy program)",
    purpose="Subsidy program enrollment per mahalla, in source order.",
    columns=(
        SemanticViewColumn("subsidy_program_id", "Surrogate row id.", nullable=False),
        *_flat_detail_columns(
            (
                SemanticViewColumn(
                    "program_order", "Source order within the mahalla.", nullable=False
                ),
                SemanticViewColumn("subsidy_program_label_cyr", "Program name in Cyrillic."),
                SemanticViewColumn(
                    "application_count",
                    "Applications submitted. ~80% NULL - treat NULL as unknown, not 0.",
                ),
                SemanticViewColumn(
                    "required_amount_mln_uzs",
                    "Requested subsidy amount in million UZS. ~84% NULL.",
                ),
                SemanticViewColumn(
                    "has_amount_source_flag",
                    "True when source supplies the requested amount.",
                ),
                SemanticViewColumn(
                    "subsidies_year", "Reporting year for the parent subsidies block."
                ),
                SemanticViewColumn("subsidies_data_date", "Source data date as ISO string."),
            )
        ),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("show subsidy uptake per program",),
    warnings=(
        "application_count and required_amount_mln_uzs are mostly NULL; do not COALESCE to 0.",
    ),
)

V_MAHALLA_PEER_FACTORS = SemanticView(
    name="v_mahalla_peer_factors",
    grain="one row per (mahalla, factor_polarity, factor_order)",
    purpose="Peer-comparison factors (strengths and weaknesses) for each mahalla.",
    columns=(
        SemanticViewColumn("peer_factor_id", "Surrogate row id.", nullable=False),
        *_flat_detail_columns(
            (
                SemanticViewColumn(
                    "factor_polarity",
                    "'strength' or 'weakness'.",
                    nullable=False,
                ),
                SemanticViewColumn("factor_order", "Source order within polarity.", nullable=False),
                SemanticViewColumn("factor_key", "Indicator id."),
                SemanticViewColumn("factor_label_cyr", "Indicator label in Cyrillic."),
                SemanticViewColumn("factor_unit", "Indicator unit string."),
                SemanticViewColumn("factor_direction", "Polarity hint up/down/neu."),
                SemanticViewColumn("entity_value_num", "Indicator value for this mahalla."),
                SemanticViewColumn(
                    "comparison_average_value", "Average over the comparison scope."
                ),
                SemanticViewColumn("peer_rank", "Rank within peer set, 1 = best on this polarity."),
                SemanticViewColumn("peer_count", "Peer set size."),
                SemanticViewColumn("percentile", "Percentile in peer set, 0-100, higher = better."),
            )
        ),
    ),
    join_keys=("mahalla_id", "district_id", "region_id"),
    use_cases=("explain why a mahalla scores high/low",),
)

V_DATA_QUALITY_ISSUES = SemanticView(
    name="v_data_quality_issues",
    grain="one row per data-quality issue raised during the latest completed run",
    purpose="Surface source-data problems so the answer layer can caveat numbers.",
    columns=(
        SemanticViewColumn("issue_id", "Surrogate id.", nullable=False),
        SemanticViewColumn("import_run_id", "Owning import run id.", nullable=False),
        SemanticViewColumn("severity", "critical / warning / info.", nullable=False),
        SemanticViewColumn(
            "issue_code", "Stable issue code (e.g. MAHALLA_STIR_DUPLICATE).", nullable=False
        ),
        SemanticViewColumn("message", "Human-readable issue description.", nullable=False),
        SemanticViewColumn("source_file", "Source file name when issue is file-scoped."),
        SemanticViewColumn("region_code", "Region code when applicable."),
        SemanticViewColumn("district_code", "District code when applicable."),
        SemanticViewColumn("mahalla_stir", "Mahalla STIR when applicable."),
        SemanticViewColumn("source_json_path", "JSON path within the source file."),
    ),
    use_cases=("count critical issues by code", "show duplicates by code"),
    warnings=(
        "natural keys (region_code/district_code/mahalla_stir) are NOT unique - issues may "
        "reference duplicates by design.",
    ),
    examples=("SELECT issue_code, COUNT(*) FROM v_data_quality_issues GROUP BY issue_code;",),
)


# ---------------------------------------------------------------------------
# Phase 2A: business directory views
# ---------------------------------------------------------------------------
#
# These views expose company registry + customs import data alongside the
# existing regional / district / mahalla geography. They use the same
# surrogate-id join contract (region_id, district_id, mahalla_id) so they
# JOIN cleanly against v_regions / v_districts / v_mahallas.
#
# OKED (industry classification) lives in v_companies as free-text labels —
# the source ships no numeric OKED code. Filter with LIKE on oked_label_uz
# or oked_label_ru.
#
# TN_VED (product classification) is a 10-digit code. v_tnved_categories is
# the HS-style dictionary. v_business_imports already joins the description
# in via tnved_description_ru so most queries don't need to touch the dict.

V_TNVED_CATEGORIES = SemanticView(
    name="v_tnved_categories",
    grain="one row per TN_VED product code in the latest business import",
    purpose="HS-style product classification dictionary. Use for chapter/heading lookups.",
    columns=(
        SemanticViewColumn("tnved_category_id", "Surrogate id.", nullable=False),
        SemanticViewColumn("tnved_code", "Full TN_VED code (10 digits as text).", nullable=False),
        SemanticViewColumn("chapter", "First 2 digits of the code (HS chapter)."),
        SemanticViewColumn("heading", "First 4 digits (HS heading)."),
        SemanticViewColumn("description_ru", "Russian description of the product code."),
    ),
    use_cases=("look up what a TN_VED code means", "group products by HS chapter"),
    examples=(
        "SELECT tnved_code, description_ru FROM v_tnved_categories "
        "WHERE chapter = '02' LIMIT 50",
    ),
)

V_COMPANIES = SemanticView(
    name="v_companies",
    grain="one row per registered Uzbek company (~167k rows)",
    purpose=(
        "Full business directory. Has region + district FK (resolved by name match), "
        "OKED industry label in both Russian and Uzbek, free-text address."
    ),
    columns=(
        SemanticViewColumn("company_id", "Surrogate company id.", nullable=False),
        SemanticViewColumn(
            "region_id", "Surrogate region id; NULL when geo resolution failed."
        ),
        SemanticViewColumn("district_id", "Surrogate district id; NULL when unresolved."),
        SemanticViewColumn("inn", "Company tax id; not strictly unique across branches."),
        SemanticViewColumn("client_code", "Internal client code from the source feed."),
        SemanticViewColumn("company_name", "Company name as stored in the source (mixed scripts)."),
        SemanticViewColumn(
            "client_type_cyr",
            "Cyrillic legal form, e.g. 'Индивидуальные предприниматели'.",
        ),
        SemanticViewColumn("address_raw", "Free-text address (mahalla-level granularity)."),
        SemanticViewColumn("country_name_cyr", "Country in Cyrillic, almost always 'Узбекистан'."),
        SemanticViewColumn(
            "region_name_raw_cyr", "Region name as it appears in the source (UPPER-CASE Cyrillic)."
        ),
        SemanticViewColumn(
            "district_name_raw_cyr",
            "District name as it appears in the source (UPPER-CASE Cyrillic).",
        ),
        SemanticViewColumn("region_name_cyr", "Region name from CERR geography (Title Case)."),
        SemanticViewColumn("district_name_cyr", "District name from CERR geography."),
        SemanticViewColumn(
            "oked_label_ru",
            "Russian OKED activity label, e.g. 'Розничная торговля в неспециализированных магазинах'. "
            "No numeric code in the source — use LIKE for category filters.",
        ),
        SemanticViewColumn(
            "oked_label_uz",
            "Uzbek OKED activity label, e.g. 'Чакана савдо'. Use LIKE for category filters.",
        ),
    ),
    join_keys=("region_id", "district_id"),
    use_cases=(
        "count companies in a region/district",
        "find companies in a specific industry via OKED label LIKE filter",
        "rank districts by company count for a given OKED",
    ),
    warnings=(
        "There is no numeric OKED code; filter with `oked_label_ru LIKE '%pattern%'` or `oked_label_uz LIKE ...`.",
        "region_id / district_id are NULL when the source name could not be matched to CERR geography.",
        "INN is not unique — one tax id can have multiple branch rows.",
    ),
    examples=(
        "SELECT region_name_cyr, COUNT(*) AS company_count FROM v_companies "
        "WHERE oked_label_ru LIKE '%ресторан%' GROUP BY region_name_cyr "
        "ORDER BY company_count DESC LIMIT 14",
        "SELECT company_name, district_name_cyr, oked_label_uz FROM v_companies "
        "WHERE region_name_cyr LIKE '%Фарғона%' AND oked_label_uz LIKE '%чакана%' LIMIT 50",
    ),
)

V_BUSINESS_IMPORTS = SemanticView(
    name="v_business_imports",
    grain="one row per TN_VED product line on an import declaration (~427k rows, 2024-2025)",
    purpose=(
        "Customs import line items. Each row ties one company (importer) to one TN_VED "
        "product code and a USD invoice value. Region/district/mahalla resolved from "
        "the source geo fields. Already joined to v_tnved_categories for description."
    ),
    columns=(
        SemanticViewColumn("business_import_id", "Surrogate id.", nullable=False),
        SemanticViewColumn("region_id", "Importer region surrogate id; NULL if unresolved."),
        SemanticViewColumn("district_id", "Importer district surrogate id; NULL if unresolved."),
        SemanticViewColumn("mahalla_id", "Importer mahalla surrogate id; NULL if unresolved."),
        SemanticViewColumn("inn", "Importer tax id."),
        SemanticViewColumn("company_name", "Importer name as on the declaration."),
        SemanticViewColumn("contract_number", "Customs contract identifier."),
        SemanticViewColumn("declaration_number", "Declaration sequence number."),
        SemanticViewColumn("declaration_date", "Declaration date (DATE)."),
        SemanticViewColumn("region_name_raw_cyr", "Importer region as on declaration (Cyrillic)."),
        SemanticViewColumn("district_name_raw_cyr", "Importer district as on declaration."),
        SemanticViewColumn("mahalla_name_raw_cyr", "Importer mahalla as on declaration."),
        SemanticViewColumn("region_name_cyr", "Importer region from CERR geography."),
        SemanticViewColumn("district_name_cyr", "Importer district from CERR geography."),
        SemanticViewColumn("mahalla_name_cyr", "Importer mahalla from CERR geography."),
        SemanticViewColumn("tnved_code", "TN_VED 10-digit code as text.", nullable=False),
        SemanticViewColumn("tnved_chapter", "First 2 digits of TN_VED code (HS chapter)."),
        SemanticViewColumn(
            "tnved_description_ru", "Russian product description joined from v_tnved_categories."
        ),
        SemanticViewColumn(
            "currency_code", "Numeric ISO currency code (e.g. '840' for USD, '978' for EUR)."
        ),
        SemanticViewColumn(
            "origin_country_code", "Numeric ISO country code of origin (e.g. '156' for China)."
        ),
        SemanticViewColumn("invoice_value_total", "Invoice total for the declaration."),
        SemanticViewColumn("invoice_value_item", "Invoice total for this line item."),
        SemanticViewColumn(
            "value_usd",
            "USD equivalent of the line item; THIS is the column to sum for import value.",
        ),
        SemanticViewColumn("exchange_rate", "Declaration-day exchange rate to UZS."),
        SemanticViewColumn(
            "item_description", "Free-text item description (very long; rarely useful for SQL)."
        ),
    ),
    join_keys=("region_id", "district_id", "mahalla_id"),
    use_cases=(
        "top importers by total USD value",
        "import volume per region/district",
        "what does company X import (by TN_VED chapter)",
        "which countries do imports originate from",
    ),
    warnings=(
        "Use value_usd for monetary aggregation; invoice_value_item is in source currency.",
        "tnved_chapter is a substring of tnved_code; either is fine for chapter filters.",
        "currency_code and origin_country_code are NUMERIC ISO codes stored as text.",
    ),
    examples=(
        "SELECT company_name, SUM(value_usd) AS total_usd FROM v_business_imports "
        "GROUP BY company_name ORDER BY total_usd DESC LIMIT 10",
        "SELECT region_name_cyr, SUM(value_usd) AS region_total_usd FROM v_business_imports "
        "WHERE tnved_chapter = '02' GROUP BY region_name_cyr ORDER BY region_total_usd DESC LIMIT 14",
    ),
)

V_BUSINESS_IMPORT_SUMMARIES = SemanticView(
    name="v_business_import_summaries",
    grain="one row per importer aggregated across 12 product categories (~2,959 rows)",
    purpose=(
        "Pre-aggregated per-importer totals over the 2024-2025 snapshot. Twelve category "
        "columns sum to total_import_usd. Use this for fast top-importer queries; for "
        "TN_VED-level detail use v_business_imports."
    ),
    columns=(
        SemanticViewColumn("business_import_summary_id", "Surrogate id.", nullable=False),
        SemanticViewColumn("inn", "Importer tax id."),
        SemanticViewColumn("company_name", "Importer name."),
        SemanticViewColumn("total_import_usd", "Total import value across all categories, USD."),
        SemanticViewColumn("value_machines_usd", "Machines and equipment, USD."),
        SemanticViewColumn("value_chemicals_usd", "Chemical products, USD."),
        SemanticViewColumn("value_misc_goods_usd", "Various finished goods, USD."),
        SemanticViewColumn("value_industrial_usd", "Industrial goods, USD."),
        SemanticViewColumn("value_animal_oils_usd", "Animal and vegetable oils, USD."),
        SemanticViewColumn("value_non_food_raw_usd", "Non-food raw materials except fuel, USD."),
        SemanticViewColumn("value_building_mats_usd", "Construction materials, USD."),
        SemanticViewColumn("value_food_products_usd", "Food products (excl. fruit/veg), USD."),
        SemanticViewColumn("value_fruit_veg_usd", "Fruit and vegetable products, USD."),
        SemanticViewColumn("value_mineral_fuel_usd", "Mineral fuel and oils, USD."),
        SemanticViewColumn("value_beverages_tobacco_usd", "Beverages and tobacco products, USD."),
        SemanticViewColumn("value_other_goods_usd", "Other goods, USD."),
    ),
    use_cases=(
        "top importers by total value",
        "top importers in a specific product category",
        "share-of-category for a company",
    ),
    warnings=(
        "Category columns are pre-aggregated by the source; do NOT also join "
        "v_business_imports and re-sum the same values.",
        "NULL in a category column means no import in that category; do not COALESCE to 0 unless explicitly asked.",
    ),
    examples=(
        "SELECT company_name, total_import_usd FROM v_business_import_summaries "
        "ORDER BY total_import_usd DESC LIMIT 10",
        "SELECT company_name, value_food_products_usd FROM v_business_import_summaries "
        "WHERE value_food_products_usd IS NOT NULL "
        "ORDER BY value_food_products_usd DESC LIMIT 10",
    ),
)

V_COMPANY_DENSITY_BY_DISTRICT = SemanticView(
    name="v_company_density_by_district",
    grain="one row per (district, oked_label) combination with company count",
    purpose=(
        "Pre-aggregated company count per district per industry. Use for "
        "'how many bakeries in district X' and gap analysis."
    ),
    columns=(
        SemanticViewColumn("region_id", "Region surrogate id.", nullable=False),
        SemanticViewColumn("district_id", "District surrogate id.", nullable=False),
        SemanticViewColumn("region_name_cyr", "Region name (CERR)."),
        SemanticViewColumn("district_name_cyr", "District name (CERR)."),
        SemanticViewColumn(
            "oked_label_uz", "Uzbek OKED activity label.", nullable=False
        ),
        SemanticViewColumn("oked_label_ru", "Russian OKED activity label."),
        SemanticViewColumn(
            "company_count", "Number of companies in this (district, oked) bucket.", nullable=False
        ),
    ),
    join_keys=("region_id", "district_id"),
    use_cases=(
        "find under-served industries per district",
        "rank districts by density of a specific industry",
    ),
    warnings=(
        "Only rows where region_id, district_id, and oked_label_uz are all non-NULL are aggregated.",
        "Use LIKE on oked_label_uz / oked_label_ru to find an industry; exact match is fragile.",
    ),
    examples=(
        "SELECT district_name_cyr, company_count FROM v_company_density_by_district "
        "WHERE oked_label_uz LIKE '%чакана%' ORDER BY company_count DESC LIMIT 20",
    ),
)


SEMANTIC_CATALOG: dict[str, SemanticView] = {
    v.name: v
    for v in (
        V_LATEST_IMPORT_RUN,
        V_REGIONS,
        V_DISTRICTS,
        V_MAHALLAS,
        V_DISTRICT_MACRO_HIGHLIGHTS,
        V_MAHALLA_INFRASTRUCTURE,
        V_MAHALLA_APPEALS,
        V_MAHALLA_SPECIALIZATIONS,
        V_MAHALLA_CROPS,
        V_MAHALLA_SUBSIDY_PROGRAMS,
        V_MAHALLA_PEER_FACTORS,
        V_DATA_QUALITY_ISSUES,
        V_TNVED_CATEGORIES,
        V_COMPANIES,
        V_BUSINESS_IMPORTS,
        V_BUSINESS_IMPORT_SUMMARIES,
        V_COMPANY_DENSITY_BY_DISTRICT,
    )
}
