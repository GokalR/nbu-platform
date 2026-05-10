"""Profile result models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cerr_chatbot.numeric_profile.stats import NumericStats

EXPECTED_BASE_KPI_KEYS: tuple[str, ...] = (
    "population",
    "active_businesses",
    "unemployed",
    "rating_score",
    "problem_loans",
    "poor_families",
)


class KpiKeyProfile(BaseModel):
    level: str
    kpi_key: str
    expected_entity_count: int
    row_count: int
    missing_entity_count: int
    value_stats: NumericStats
    change_pct_stats: NumericStats
    district_avg_stats: NumericStats
    distinct_labels: list[str] = Field(default_factory=list)
    distinct_formats: list[str] = Field(default_factory=list)
    distinct_directions: list[str] = Field(default_factory=list)
    distinct_source_table_names: list[str] = Field(default_factory=list)
    distinct_source_column_names: list[str] = Field(default_factory=list)
    distinct_compare_scopes: list[Any] = Field(default_factory=list)
    distinct_provenance: list[str] = Field(default_factory=list)


class MacroIndicatorProfile(BaseModel):
    indicator_key: str
    district_row_count: int
    expected_district_count: int
    missing_district_count: int
    distinct_labels: list[str] = Field(default_factory=list)
    distinct_units: list[str] = Field(default_factory=list)
    distinct_directions: list[str] = Field(default_factory=list)
    points_per_district_min: int = 0
    points_per_district_max: int = 0
    total_points: int = 0
    highlighted_count: int = 0
    highlighted_missing_count: int = 0
    highlighted_value_null_count: int = 0
    all_point_value_stats: NumericStats
    highlighted_value_stats: NumericStats


class NaturalKeyDiagnostics(BaseModel):
    region_code_unique_count: int = 0
    region_code_duplicate_group_count: int = 0
    region_code_duplicate_examples: list[int] = Field(default_factory=list)
    district_code_unique_count: int = 0
    district_code_duplicate_group_count: int = 0
    district_code_duplicate_examples: list[int] = Field(default_factory=list)
    mahalla_stir_unique_count: int = 0
    mahalla_stir_duplicate_group_count: int = 0
    mahalla_stir_duplicate_examples: list[str] = Field(default_factory=list)
    mahalla_composite_key_unique_count: int = 0
    mahalla_composite_key_duplicate_group_count: int = 0
    mahalla_composite_key_duplicate_examples: list[Any] = Field(default_factory=list)


class PeerFactorProfile(BaseModel):
    polarity: str
    factor_key: str
    row_count: int
    this_value_stats: NumericStats
    district_avg_stats: NumericStats
    percentile_stats: NumericStats
    peer_rank_min: int | None = None
    peer_rank_max: int | None = None
    peer_count_min: int | None = None
    peer_count_max: int | None = None
    distinct_labels: list[str] = Field(default_factory=list)
    distinct_units: list[str] = Field(default_factory=list)
    distinct_directions: list[str] = Field(default_factory=list)
    rank_exceeds_count: int = 0
    percentile_out_of_range: int = 0


class DetailFieldProfile(BaseModel):
    group: str
    column_name: str
    json_path: str
    value_stats: NumericStats


class MacroDistrictCompleteness(BaseModel):
    district_code: int
    indicator_count: int


class NumericProfileReport(BaseModel):
    run_at: str
    source_dir: str
    source_files: list[str] = Field(default_factory=list)
    entity_counts: dict[str, int] = Field(default_factory=dict)
    base_kpi_coverage: dict[str, dict[str, bool]] = Field(default_factory=dict)
    kpi_profiles: list[KpiKeyProfile] = Field(default_factory=list)
    macro_indicator_profiles: list[MacroIndicatorProfile] = Field(default_factory=list)
    macro_district_completeness: dict[str, int] = Field(default_factory=dict)
    peer_factor_profiles: list[PeerFactorProfile] = Field(default_factory=list)
    detail_field_profiles: list[DetailFieldProfile] = Field(default_factory=list)
    natural_key_diagnostics: NaturalKeyDiagnostics = Field(default_factory=NaturalKeyDiagnostics)
    null_free_numeric_fields: list[str] = Field(default_factory=list)
    high_risk_findings: list[str] = Field(default_factory=list)
