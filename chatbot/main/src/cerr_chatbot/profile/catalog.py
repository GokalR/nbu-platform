"""Future SQL column naming catalog.

Maps canonical JSON paths (rooted at `region`) to a proposed SQL column name,
the future table or semantic view that will hold it, and a one-line semantic
description aimed at the LLM SQL agent.

Paths use `[]` for arrays. Keys absent from `COLUMN_CATALOG` AND absent from
`IGNORED_PATHS` are reported as uncataloged so the engineer sees real gaps.

Naming rules followed here:
- snake_case English column names.
- Unit suffixes when meaningful: _km, _ha, _percent, _mln_uzs, _bln_uzs.
- _count for integer cardinalities; _text for free Cyrillic strings.
- Codes named explicitly: region_code, district_code, mahalla_stir.
- Cyrillic-name fields suffixed _name_cyr / _label_cyr.
- Generic value_num is allowed only on EAV-style KPI/indicator tables.

All descriptions in this file MUST be ASCII-only English. Cyrillic example
values belong in source data, never in catalog descriptions, to eliminate
mojibake risk on Windows consoles and in mixed-encoding pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnSpec:
    column: str
    table_group: str
    description: str


# Reusable semantic descriptions for the KPI EAV (region/district/mahalla
# share the exact shape; we mention the row level in each spec).
_KPI_KEY = "Stable KPI identifier (e.g. population, active_business)."
_KPI_LABEL = "Human KPI label in source language (Cyrillic)."
_KPI_TABLE = "Source fact table the KPI was pulled from."
_KPI_COLUMN = "Source column name within source_table_name."
_KPI_FORMAT = "Display format hint (thousands, percent, money, etc.)."
_KPI_PROVENANCE = "Source provenance flag (e.g. live, computed, missing)."
_KPI_DIRECTION = "Polarity hint: up (higher better), down (lower better), neu (neutral)."
_KPI_VALUE = "Numeric KPI value for the entity row."
_KPI_ERROR = "Error string when the KPI could not be computed; null otherwise."
_KPI_CHANGE = "Percent change vs previous reporting period for this KPI."
_KPI_AVG = "Average of this KPI across the comparison scope (despite the name)."
_KPI_SCOPE = "Scope used for district_average_value (e.g. district, region, country)."


def _kpi(prefix: str) -> dict[str, ColumnSpec]:
    """Generate the 12-field EAV mapping for a kpis[] array under prefix."""
    return {
        f"{prefix}.key": ColumnSpec("kpi_key", "entity_kpis", _KPI_KEY),
        f"{prefix}.label": ColumnSpec("kpi_label_cyr", "entity_kpis", _KPI_LABEL),
        f"{prefix}.table": ColumnSpec("source_table_name", "entity_kpis", _KPI_TABLE),
        f"{prefix}.column": ColumnSpec("source_column_name", "entity_kpis", _KPI_COLUMN),
        f"{prefix}.format": ColumnSpec("kpi_format", "entity_kpis", _KPI_FORMAT),
        f"{prefix}.provenance": ColumnSpec("kpi_provenance", "entity_kpis", _KPI_PROVENANCE),
        f"{prefix}.direction": ColumnSpec("kpi_direction", "entity_kpis", _KPI_DIRECTION),
        f"{prefix}.value": ColumnSpec("kpi_value_num", "entity_kpis", _KPI_VALUE),
        f"{prefix}.error": ColumnSpec("kpi_error_text", "entity_kpis", _KPI_ERROR),
        f"{prefix}.change_pct": ColumnSpec("change_percent", "entity_kpis", _KPI_CHANGE),
        f"{prefix}.district_avg": ColumnSpec("district_average_value", "entity_kpis", _KPI_AVG),
        f"{prefix}.compare_scope": ColumnSpec("compare_scope", "entity_kpis", _KPI_SCOPE),
    }


def _peer_factor(prefix: str, polarity: str) -> dict[str, ColumnSpec]:
    """Generate the peer-factor mapping for strengths[] or weaknesses[]."""
    return {
        f"{prefix}.key": ColumnSpec(
            "factor_key",
            "mahalla_peer_factors",
            f"Indicator id ({polarity} side).",
        ),
        f"{prefix}.label": ColumnSpec(
            "factor_label_cyr",
            "mahalla_peer_factors",
            f"Indicator label in Cyrillic ({polarity} side).",
        ),
        f"{prefix}.unit": ColumnSpec(
            "factor_unit",
            "mahalla_peer_factors",
            f"Indicator unit (Cyrillic) ({polarity} side).",
        ),
        f"{prefix}.direction": ColumnSpec(
            "factor_direction",
            "mahalla_peer_factors",
            f"Polarity hint up/down/neu ({polarity} side).",
        ),
        f"{prefix}.this_value": ColumnSpec(
            "entity_value_num",
            "mahalla_peer_factors",
            f"Indicator value for this mahalla ({polarity} side).",
        ),
        f"{prefix}.district_avg": ColumnSpec(
            "comparison_average_value",
            "mahalla_peer_factors",
            f"Average of the indicator across the comparison scope ({polarity} side).",
        ),
        f"{prefix}.peer_rank": ColumnSpec(
            "peer_rank",
            "mahalla_peer_factors",
            f"Rank within peer set, 1 = best on this polarity ({polarity} side).",
        ),
        f"{prefix}.peer_count": ColumnSpec(
            "peer_count",
            "mahalla_peer_factors",
            f"Peer set size ({polarity} side).",
        ),
        f"{prefix}.percentile": ColumnSpec(
            "percentile",
            "mahalla_peer_factors",
            f"Percentile within peer set, 0-100, higher = better on this polarity ({polarity} side).",
        ),
    }


COLUMN_CATALOG: dict[str, ColumnSpec] = {
    # ---------------- regions ----------------
    "region.region_code": ColumnSpec(
        "region_code", "regions", "Region code (4-digit OKTMO prefix)."
    ),
    "region.region_name": ColumnSpec(
        "region_name_cyr", "regions", "Region display name in Cyrillic."
    ),
    "region.region_mahalla_count": ColumnSpec(
        "declared_mahalla_count",
        "regions",
        "Source-declared mahalla count for the region (may differ from actual; see audit).",
    ),
    "region.districts_count": ColumnSpec(
        "declared_district_count",
        "regions",
        "Source-declared district count for the region.",
    ),
    "region.mahallas_scraped": ColumnSpec(
        "mahallas_scraped_count",
        "regions",
        "Number of mahallas the source pipeline successfully scraped.",
    ),
    "region.mahallas_skipped": ColumnSpec(
        "mahallas_skipped_flag",
        "regions",
        "True when the source pipeline skipped mahallas for this region.",
    ),
    "region.geo_skipped": ColumnSpec(
        "geo_skipped_flag",
        "regions",
        "True when geometry collection was skipped for this region.",
    ),
    "region.generated_at": ColumnSpec(
        "source_generated_at",
        "regions",
        "Timestamp when the source JSON was generated.",
    ),
    "region.region_geo": ColumnSpec(
        "region_geometry",
        "region_geometries",
        "Region-level GeoJSON FeatureCollection. Stored verbatim (jsonb/geometry).",
    ),
    "region.region_overview.code": ColumnSpec(
        "region_code_text",
        "regions",
        "Region code echoed inside region_overview as a string.",
    ),
    "region.region_overview.level": ColumnSpec(
        "overview_level",
        "regions",
        "Echoed entity level marker (region/district/mahalla).",
    ),
    "region.region_overview.ai_insights_status": ColumnSpec(
        "ai_insights_status",
        "regions",
        "AI generation status for the region (typically 'unavailable').",
    ),
    "region.region_overview.header.title": ColumnSpec(
        "region_title_cyr", "regions", "Region UI title in Cyrillic."
    ),
    "region.region_overview.header.subtitle": ColumnSpec(
        "region_subtitle_cyr",
        "regions",
        "Region UI subtitle (e.g. 'N districts, M mahallas').",
    ),
    # region kpis (EAV)
    **_kpi("region.region_overview.kpis[]"),
    # ---------------- districts ----------------
    "region.districts[].code": ColumnSpec(
        "district_code", "districts", "District OKTMO code (7 digits, prefix = region_code)."
    ),
    "region.districts[].name": ColumnSpec(
        "district_name_cyr", "districts", "District display name in Cyrillic."
    ),
    "region.districts[].mahalla_count": ColumnSpec(
        "declared_mahalla_count",
        "districts",
        "Source-declared mahalla count for the district.",
    ),
    "region.districts[].overview.code": ColumnSpec(
        "district_code_text",
        "districts",
        "District code echoed inside overview as a string.",
    ),
    "region.districts[].overview.level": ColumnSpec(
        "overview_level",
        "districts",
        "Echoed entity level marker (region/district/mahalla).",
    ),
    "region.districts[].overview.ai_insights_status": ColumnSpec(
        "ai_insights_status",
        "districts",
        "AI generation status for the district.",
    ),
    "region.districts[].overview.header.title": ColumnSpec(
        "district_title_cyr", "districts", "District UI title in Cyrillic."
    ),
    "region.districts[].overview.header.subtitle": ColumnSpec(
        "district_subtitle_cyr", "districts", "District UI subtitle in Cyrillic."
    ),
    # district kpis (EAV)
    **_kpi("region.districts[].overview.kpis[]"),
    # rating histogram
    "region.districts[].overview.rating_histogram[].bucket": ColumnSpec(
        "rating_bucket_label_cyr",
        "district_rating_histogram",
        "Rating bucket label in Cyrillic.",
    ),
    "region.districts[].overview.rating_histogram[].count": ColumnSpec(
        "mahalla_count",
        "district_rating_histogram",
        "Number of mahallas in this rating bucket.",
    ),
    # macro
    "region.districts[].macro.district_oktmo": ColumnSpec(
        "district_oktmo",
        "districts",
        "OKTMO code echoed inside macro block; should equal districts.code.",
    ),
    "region.districts[].macro.district_name": ColumnSpec(
        "district_name_cyr", "districts", "District name echoed inside macro block."
    ),
    "region.districts[].macro.region_name": ColumnSpec(
        "region_name_cyr", "districts", "Region name echoed inside macro block."
    ),
    "region.districts[].macro.period": ColumnSpec(
        "period_label_cyr",
        "districts",
        "Reporting period label in Cyrillic.",
    ),
    "region.districts[].macro.indicators[].key": ColumnSpec(
        "indicator_key",
        "district_macro_indicators",
        "Stable macro indicator identifier (e.g. industry_volume_bln_uzs).",
    ),
    "region.districts[].macro.indicators[].label": ColumnSpec(
        "indicator_label_cyr",
        "district_macro_indicators",
        "Human macro indicator label in Cyrillic.",
    ),
    "region.districts[].macro.indicators[].unit": ColumnSpec(
        "indicator_unit",
        "district_macro_indicators",
        "Unit of measure (Cyrillic), parsed from key/label.",
    ),
    "region.districts[].macro.indicators[].direction": ColumnSpec(
        "indicator_direction",
        "district_macro_indicators",
        "Polarity hint up/down/neu.",
    ),
    "region.districts[].macro.indicators[].points[].district_name": ColumnSpec(
        "district_name_cyr",
        "district_macro_points",
        "District the data point belongs to (Cyrillic name).",
    ),
    "region.districts[].macro.indicators[].points[].value": ColumnSpec(
        "indicator_value_num",
        "district_macro_points",
        "Numeric value of the indicator for the district.",
    ),
    "region.districts[].macro.indicators[].points[].highlighted": ColumnSpec(
        "is_highlighted",
        "district_macro_points",
        "True when the data point is the current district being viewed.",
    ),
    # geo
    "region.districts[].geo": ColumnSpec(
        "district_geometry",
        "district_geometries",
        "District-level GeoJSON FeatureCollection (per-mahalla polygons). Stored verbatim.",
    ),
    # ---------------- mahallas ----------------
    "region.districts[].mahallas[].stir": ColumnSpec(
        "mahalla_stir",
        "mahallas",
        "Mahalla STIR (9-digit tax id); not globally unique (use composite key).",
    ),
    "region.districts[].mahallas[].name": ColumnSpec(
        "mahalla_name_cyr", "mahallas", "Mahalla display name in Cyrillic."
    ),
    "region.districts[].mahallas[].rating_score": ColumnSpec(
        "rating_score", "mahallas", "Composite mahalla rating score (0-100)."
    ),
    "region.districts[].mahallas[].overview.code": ColumnSpec(
        "mahalla_code_text",
        "mahallas",
        "Mahalla code echoed inside overview as a string (matches stir).",
    ),
    "region.districts[].mahallas[].overview.level": ColumnSpec(
        "overview_level",
        "mahallas",
        "Echoed entity level marker (region/district/mahalla).",
    ),
    "region.districts[].mahallas[].overview.ai_insights_status": ColumnSpec(
        "ai_insights_status",
        "mahallas",
        "Mirror of ai_insights.status.",
    ),
    "region.districts[].mahallas[].overview.header.title": ColumnSpec(
        "mahalla_title_cyr", "mahallas", "Mahalla UI title in Cyrillic."
    ),
    "region.districts[].mahallas[].overview.header.subtitle": ColumnSpec(
        "mahalla_subtitle_cyr",
        "mahallas",
        "Mahalla UI subtitle in Cyrillic ('district, region').",
    ),
    "region.districts[].mahallas[].overview.header.district_rank": ColumnSpec(
        "district_rank_text",
        "mahallas",
        "Mahalla rank within district as 'k/N' string.",
    ),
    "region.districts[].mahallas[].overview.header.region_rank": ColumnSpec(
        "region_rank_text",
        "mahallas",
        "Mahalla rank within region as 'k/N' string.",
    ),
    "region.districts[].mahallas[].overview.header.category": ColumnSpec(
        "category_label_cyr",
        "mahallas",
        "Mahalla category label in Cyrillic.",
    ),
    # header.meta is a list of {label, value} pairs for UI badges.
    "region.districts[].mahallas[].overview.header.meta[].label": ColumnSpec(
        "meta_label_cyr",
        "mahalla_header_meta",
        "Badge label in Cyrillic (e.g. STIR, status).",
    ),
    "region.districts[].mahallas[].overview.header.meta[].value": ColumnSpec(
        "meta_value_text",
        "mahalla_header_meta",
        "Badge value as free-form text.",
    ),
    # mahalla kpis (EAV)
    **_kpi("region.districts[].mahallas[].overview.kpis[]"),
    # specialization
    "region.districts[].mahallas[].overview.detail.specialization.items[].slot": ColumnSpec(
        "specialization_slot",
        "mahalla_specializations",
        "Slot key (main, add_2, add_3, etc.).",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.items[].slot_label": ColumnSpec(
        "specialization_slot_label_cyr",
        "mahalla_specializations",
        "Slot label in Cyrillic.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.items[].type": ColumnSpec(
        "specialization_type_cyr",
        "mahalla_specializations",
        "High-level specialization type in Cyrillic.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.items[].direction": ColumnSpec(
        "specialization_direction_cyr",
        "mahalla_specializations",
        "Specialization sub-direction in Cyrillic.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.items[].households": ColumnSpec(
        "household_count",
        "mahalla_specializations",
        "Households engaged in this specialization slot.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.items[].population": ColumnSpec(
        "population_count",
        "mahalla_specializations",
        "Population engaged in this specialization slot.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.items[].percent": ColumnSpec(
        "share_percent",
        "mahalla_specializations",
        "Share of total mahalla population in this slot, percent.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.residual_percent": ColumnSpec(
        "specialization_residual_percent",
        "mahallas",
        "Percent of population not covered by any listed specialization slot.",
    ),
    "region.districts[].mahallas[].overview.detail.specialization.total_known_percent": ColumnSpec(
        "specialization_total_known_percent",
        "mahallas",
        "Sum of share_percent across known specialization slots.",
    ),
    # crops
    "region.districts[].mahallas[].overview.detail.crops.seasons[].key": ColumnSpec(
        "season_key",
        "mahalla_crops",
        "Season key (main, repeat, winter_sown).",
    ),
    "region.districts[].mahallas[].overview.detail.crops.seasons[].label": ColumnSpec(
        "season_label_cyr",
        "mahalla_crops",
        "Season label in Cyrillic.",
    ),
    "region.districts[].mahallas[].overview.detail.crops.seasons[].crops_text": ColumnSpec(
        "crops_text_cyr",
        "mahalla_crops",
        "Free-form crop list in Cyrillic, nullable.",
    ),
    "region.districts[].mahallas[].overview.detail.crops.seasons[].total_area_ha": ColumnSpec(
        "total_area_ha",
        "mahalla_crops",
        "Total cultivated area for the season, hectares.",
    ),
    "region.districts[].mahallas[].overview.detail.crops.seasons[].homestead_area_ha": ColumnSpec(
        "homestead_area_ha",
        "mahalla_crops",
        "Homestead (tomorqa) area for the season, hectares.",
    ),
    "region.districts[].mahallas[].overview.detail.crops.seasons[].household_count": ColumnSpec(
        "household_count",
        "mahalla_crops",
        "Households cultivating in this season.",
    ),
    "region.districts[].mahallas[].overview.detail.crops.total_homestead_area_sotikh": ColumnSpec(
        "crop_total_homestead_area_sotkah",
        "mahallas",
        "Total homestead area in sotkah (1 ha = 100 sotkah). Source key: ...sotikh.",
    ),
    # subsidies
    "region.districts[].mahallas[].overview.detail.subsidies.programs[].label": ColumnSpec(
        "subsidy_program_label_cyr",
        "mahalla_subsidy_programs",
        "Subsidy program name in Cyrillic.",
    ),
    "region.districts[].mahallas[].overview.detail.subsidies.programs[].applications": ColumnSpec(
        "application_count",
        "mahalla_subsidy_programs",
        "Number of applications submitted for this program.",
    ),
    "region.districts[].mahallas[].overview.detail.subsidies.programs[].required_amount_mln": ColumnSpec(
        "required_amount_mln_uzs",
        "mahalla_subsidy_programs",
        "Requested subsidy amount in million UZS.",
    ),
    "region.districts[].mahallas[].overview.detail.subsidies.programs[].has_amount_source": ColumnSpec(
        "has_amount_source_flag",
        "mahalla_subsidy_programs",
        "True when the source supplies the requested amount.",
    ),
    "region.districts[].mahallas[].overview.detail.subsidies.year": ColumnSpec(
        "subsidies_year",
        "mahallas",
        "Reporting year for the subsidies block.",
    ),
    "region.districts[].mahallas[].overview.detail.subsidies.data_date": ColumnSpec(
        "subsidies_data_date",
        "mahallas",
        "Source data date (ISO yyyy-mm-dd) for the subsidies block.",
    ),
    # infra
    "region.districts[].mahallas[].overview.detail.infra.road_km": ColumnSpec(
        "road_total_km", "mahalla_infrastructure", "Total road length in the mahalla, km."
    ),
    "region.districts[].mahallas[].overview.detail.infra.road_dirt_km": ColumnSpec(
        "road_dirt_km", "mahalla_infrastructure", "Dirt-road length, km."
    ),
    "region.districts[].mahallas[].overview.detail.infra.road_asphalt_km": ColumnSpec(
        "road_asphalt_km", "mahalla_infrastructure", "Asphalt-road length, km."
    ),
    "region.districts[].mahallas[].overview.detail.infra.no_water": ColumnSpec(
        "households_without_drinking_water_count",
        "mahalla_infrastructure",
        "Households without drinking water access.",
    ),
    "region.districts[].mahallas[].overview.detail.infra.power_cuts": ColumnSpec(
        "power_outage_count",
        "mahalla_infrastructure",
        "Number of power outages in the reporting period.",
    ),
    "region.districts[].mahallas[].overview.detail.infra.power_hrs": ColumnSpec(
        "power_outage_hours_text",
        "mahalla_infrastructure",
        "Power-outage duration, free-form text (mostly digits, parse before use).",
    ),
    "region.districts[].mahallas[].overview.detail.infra.medical_km": ColumnSpec(
        "medical_facility_distance_km",
        "mahalla_infrastructure",
        "Distance to nearest medical facility, km.",
    ),
    "region.districts[].mahallas[].overview.detail.infra.school": ColumnSpec(
        "school_count", "mahalla_infrastructure", "Number of schools in the mahalla."
    ),
    "region.districts[].mahallas[].overview.detail.infra.sport": ColumnSpec(
        "sports_facility_count",
        "mahalla_infrastructure",
        "Number of sports facilities in the mahalla.",
    ),
    "region.districts[].mahallas[].overview.detail.infra.kindergarten": ColumnSpec(
        "kindergarten_count",
        "mahalla_infrastructure",
        "Number of kindergartens in the mahalla.",
    ),
    "region.districts[].mahallas[].overview.detail.infra.tomorqa_ha": ColumnSpec(
        "homestead_area_ha",
        "mahalla_infrastructure",
        "Total homestead (tomorqa) area, hectares.",
    ),
    # appeals
    "region.districts[].mahallas[].overview.appeals.crime": ColumnSpec(
        "crime_appeal_count", "mahalla_appeals", "Crime-related appeal count."
    ),
    "region.districts[].mahallas[].overview.appeals.divorce": ColumnSpec(
        "divorce_appeal_count", "mahalla_appeals", "Divorce-related appeal count."
    ),
    "region.districts[].mahallas[].overview.appeals.aid": ColumnSpec(
        "social_aid_appeal_count",
        "mahalla_appeals",
        "Social aid appeal count.",
    ),
    "region.districts[].mahallas[].overview.appeals.employment": ColumnSpec(
        "employment_appeal_count", "mahalla_appeals", "Employment appeal count."
    ),
    "region.districts[].mahallas[].overview.appeals.gas": ColumnSpec(
        "gas_appeal_count", "mahalla_appeals", "Gas-supply appeal count."
    ),
    "region.districts[].mahallas[].overview.appeals.registry": ColumnSpec(
        "registry_appeal_count", "mahalla_appeals", "Civil-registry appeal count."
    ),
    "region.districts[].mahallas[].overview.appeals.year": ColumnSpec(
        "appeals_year", "mahalla_appeals", "Reporting year for the appeal counts."
    ),
    "region.districts[].mahallas[].overview.appeals.period": ColumnSpec(
        "appeals_period_label_cyr",
        "mahalla_appeals",
        "Reporting period label in Cyrillic.",
    ),
    # peer profile
    "region.districts[].mahallas[].overview.peer_profile.peer_set.count": ColumnSpec(
        "peer_set_count",
        "mahallas",
        "Number of peer mahallas considered for this mahalla.",
    ),
    "region.districts[].mahallas[].overview.peer_profile.peer_set.description": ColumnSpec(
        "peer_set_description_cyr",
        "mahallas",
        "Free-form description of the peer set in Cyrillic.",
    ),
    "region.districts[].mahallas[].overview.peer_profile.peer_set.fallback_to_district": ColumnSpec(
        "peer_fallback_to_district_flag",
        "mahallas",
        "True when peer selection fell back to the whole district.",
    ),
    "region.districts[].mahallas[].overview.peer_profile.indicator_count": ColumnSpec(
        "peer_indicator_count",
        "mahallas",
        "Indicators that produced a peer comparison for this mahalla.",
    ),
    "region.districts[].mahallas[].overview.peer_profile.total_indicators_considered": ColumnSpec(
        "peer_total_indicators_considered",
        "mahallas",
        "Indicators evaluated in total (denominator vs peer_indicator_count).",
    ),
    # strengths + weaknesses share the same shape; use factor_polarity at import.
    **_peer_factor("region.districts[].mahallas[].overview.peer_profile.strengths[]", "strength"),
    **_peer_factor("region.districts[].mahallas[].overview.peer_profile.weaknesses[]", "weakness"),
    # ai_insights - never aggregate; treated as narrative.
    # Source has a double wrapper: mahalla.ai_insights.ai_insights.{...}
    # plus a sibling .ai_insights.status. Same content mirrored under
    # mahalla.overview.ai_insights.
    "region.districts[].mahallas[].ai_insights.status": ColumnSpec(
        "ai_insights_status",
        "mahallas",
        "AI generation status (ready, unavailable, etc.).",
    ),
    "region.districts[].mahallas[].ai_insights.ai_insights.pros[]": ColumnSpec(
        "ai_pro_text",
        "entity_ai_insights",
        "One LLM-generated positive bullet; not authoritative for numbers.",
    ),
    "region.districts[].mahallas[].ai_insights.ai_insights.cons[]": ColumnSpec(
        "ai_con_text",
        "entity_ai_insights",
        "One LLM-generated negative bullet; not authoritative for numbers.",
    ),
    "region.districts[].mahallas[].ai_insights.ai_insights.model": ColumnSpec(
        "ai_model_name", "entity_ai_insights", "Model identifier that generated the narrative."
    ),
    "region.districts[].mahallas[].ai_insights.ai_insights.generated_at": ColumnSpec(
        "ai_generated_at", "entity_ai_insights", "Timestamp the narrative was generated."
    ),
    # mirrored copy under overview.ai_insights - same shape, same names.
    "region.districts[].mahallas[].overview.ai_insights.pros[]": ColumnSpec(
        "ai_pro_text",
        "entity_ai_insights",
        "Mirror of ai_insights.ai_insights.pros[].",
    ),
    "region.districts[].mahallas[].overview.ai_insights.cons[]": ColumnSpec(
        "ai_con_text",
        "entity_ai_insights",
        "Mirror of ai_insights.ai_insights.cons[].",
    ),
    "region.districts[].mahallas[].overview.ai_insights.model": ColumnSpec(
        "ai_model_name",
        "entity_ai_insights",
        "Mirror of ai_insights.ai_insights.model.",
    ),
    "region.districts[].mahallas[].overview.ai_insights.generated_at": ColumnSpec(
        "ai_generated_at",
        "entity_ai_insights",
        "Mirror of ai_insights.ai_insights.generated_at.",
    ),
}


# Paths intentionally NOT mapped to SQL columns. Each entry is the canonical
# path -> reason, surfaced in the report so reviewers see the omission is
# deliberate (not a coverage gap).
IGNORED_PATHS: dict[str, str] = {
    # Top-level container objects/arrays - structural only.
    "region": "Top-level region object (one row per region file).",
    "region.districts": "Container array for districts.",
    "region.districts[]": "Container object for one district row.",
    "region.districts[].mahallas": "Container array for mahallas.",
    "region.districts[].mahallas[]": "Container object for one mahalla row.",
    "region.districts[].overview": "Container object holding district overview block.",
    "region.districts[].overview.kpis": "Container array for district KPIs.",
    "region.districts[].overview.kpis[]": "Container object for one district KPI row.",
    "region.districts[].overview.rating_histogram": "Container array for rating buckets.",
    "region.districts[].overview.rating_histogram[]": "Container object for one rating bucket.",
    "region.districts[].overview.header": "Container object for district UI header.",
    "region.districts[].macro": "Container object for district macro block.",
    "region.districts[].macro.indicators": "Container array for macro indicators.",
    "region.districts[].macro.indicators[]": "Container object for one indicator.",
    "region.districts[].macro.indicators[].points": "Container array for indicator points.",
    "region.districts[].macro.indicators[].points[]": "Container object for one indicator point.",
    "region.districts[].mahallas[].overview": "Container object holding mahalla overview block.",
    "region.districts[].mahallas[].overview.kpis": "Container array for mahalla KPIs.",
    "region.districts[].mahallas[].overview.kpis[]": "Container object for one mahalla KPI row.",
    "region.districts[].mahallas[].overview.header": "Container object for mahalla UI header.",
    "region.districts[].mahallas[].overview.header.meta": "Container array of header badges.",
    "region.districts[].mahallas[].overview.header.meta[]": "Container object for one header badge.",
    "region.districts[].mahallas[].overview.detail": "Container object grouping mahalla detail blocks.",
    "region.districts[].mahallas[].overview.detail.specialization": "Container object for specialization block.",
    "region.districts[].mahallas[].overview.detail.specialization.items": "Container array for specialization slots.",
    "region.districts[].mahallas[].overview.detail.specialization.items[]": "Container object for one specialization slot.",
    "region.districts[].mahallas[].overview.detail.crops": "Container object for crops block.",
    "region.districts[].mahallas[].overview.detail.crops.seasons": "Container array for crop seasons.",
    "region.districts[].mahallas[].overview.detail.crops.seasons[]": "Container object for one crop season.",
    "region.districts[].mahallas[].overview.detail.subsidies": "Container object for subsidies block.",
    "region.districts[].mahallas[].overview.detail.subsidies.programs": "Container array for subsidy programs.",
    "region.districts[].mahallas[].overview.detail.subsidies.programs[]": "Container object for one subsidy program.",
    "region.districts[].mahallas[].overview.detail.infra": "Container object for infrastructure block (fields are the columns).",
    "region.districts[].mahallas[].overview.appeals": "Container object for appeals block (fields are the columns).",
    "region.districts[].mahallas[].overview.peer_profile": "Container object for peer-profile block.",
    "region.districts[].mahallas[].overview.peer_profile.peer_set": "Container object for peer set metadata.",
    "region.districts[].mahallas[].overview.peer_profile.strengths": "Container array for strength factors.",
    "region.districts[].mahallas[].overview.peer_profile.strengths[]": "Container object for one strength factor.",
    "region.districts[].mahallas[].overview.peer_profile.weaknesses": "Container array for weakness factors.",
    "region.districts[].mahallas[].overview.peer_profile.weaknesses[]": "Container object for one weakness factor.",
    "region.region_overview": "Container object holding region overview block.",
    "region.region_overview.header": "Container object for region UI header.",
    "region.region_overview.kpis": "Container array for region KPIs.",
    "region.region_overview.kpis[]": "Container object for one region KPI row.",
    "region.districts[].mahallas[].ai_insights": "Container object wrapping AI insights (legacy double wrapper).",
    "region.districts[].mahallas[].ai_insights.ai_insights": "Inner wrapper around AI insights content.",
    "region.districts[].mahallas[].overview.ai_insights": "Mirrored AI insights container.",
    # Pure UI presentation, never persisted to SQL.
    "region.region_overview.header.breadcrumb": "UI breadcrumb array, presentation only.",
    "region.region_overview.header.breadcrumb[]": "UI breadcrumb crumb, presentation only.",
    "region.region_overview.header.meta": "Empty UI badge list at region level.",
    "region.districts[].overview.header.breadcrumb": "UI breadcrumb array, presentation only.",
    "region.districts[].overview.header.breadcrumb[]": "UI breadcrumb crumb, presentation only.",
    "region.districts[].overview.header.meta": "Empty UI badge list at district level.",
    "region.districts[].mahallas[].overview.header.breadcrumb": "UI breadcrumb array, presentation only.",
    "region.districts[].mahallas[].overview.header.breadcrumb[]": "UI breadcrumb crumb, presentation only.",
    "region.region_overview.chart": "Region UI chart block, presentation only.",
    "region.region_overview.chart.type": "Chart type hint, presentation only.",
    "region.region_overview.chart.title": "Chart title in Cyrillic, presentation only.",
    "region.region_overview.chart.data": "Chart data array, presentation only.",
    "region.region_overview.chart.data[]": "Chart data point, presentation only.",
    "region.region_overview.chart.data[].name": "Chart bar label in Cyrillic, presentation only.",
    "region.region_overview.chart.data[].value": "Chart bar value, presentation only.",
    "region.districts[].overview.chart": "District UI chart block, presentation only.",
    "region.districts[].overview.chart.type": "Chart type hint, presentation only.",
    "region.districts[].overview.chart.title": "Chart title in Cyrillic, presentation only.",
    "region.districts[].overview.chart.data": "Chart data array, presentation only.",
    "region.districts[].overview.chart.data[]": "Chart data point, presentation only.",
    "region.districts[].overview.chart.data[].name": "Chart bar label in Cyrillic, presentation only.",
    "region.districts[].overview.chart.data[].value": "Chart bar value, presentation only.",
    "region.districts[].mahallas[].overview.chart": "Mahalla UI chart block, presentation only.",
    # Specialization icons are emoji glyphs for UI; not persisted.
    "region.districts[].mahallas[].overview.detail.specialization.items[].icon": "Emoji icon, presentation only.",
    # Peer radar visualization payload, presentation only.
    "region.districts[].mahallas[].overview.peer_profile.radar": "Radar-chart payload (presentation only).",
    # Always-null fields at region/district level (peer/detail/ai_insights only
    # populated at mahalla level).
    "region.region_overview.ai_insights": "AI insights block, always null at region level.",
    "region.region_overview.detail": "Detail block, always null at region level.",
    "region.region_overview.peer_profile": "Peer profile block, always null at region level.",
    "region.districts[].overview.ai_insights": "AI insights block, always null at district level.",
    "region.districts[].overview.detail": "Detail block, always null at district level.",
    "region.districts[].overview.peer_profile": "Peer profile block, always null at district level.",
    # Parent array containers whose [] children are already cataloged.
    "region.districts[].mahallas[].ai_insights.ai_insights.pros": "Container array; pros[] elements are cataloged.",
    "region.districts[].mahallas[].ai_insights.ai_insights.cons": "Container array; cons[] elements are cataloged.",
    "region.districts[].mahallas[].overview.ai_insights.pros": "Container array; pros[] elements are cataloged.",
    "region.districts[].mahallas[].overview.ai_insights.cons": "Container array; cons[] elements are cataloged.",
    # Empty crops sub-array nested inside crops.seasons[]; child shape unknown
    # in current data and orthogonal to crops_text/total_area_ha. Revisit if a
    # non-empty example shows up.
    "region.districts[].mahallas[].overview.detail.crops.seasons[].crops": "Container array; observed empty in current data.",
}


def lookup(path: str) -> ColumnSpec | None:
    return COLUMN_CATALOG.get(path)


def is_ignored(path: str) -> bool:
    return path in IGNORED_PATHS


def ignored_reason(path: str) -> str | None:
    return IGNORED_PATHS.get(path)
