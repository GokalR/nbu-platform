"""Deterministic metric/column resolver + stage-2 prompt augmentation."""

from __future__ import annotations

from cerr_chatbot.query import (
    EXAMPLES,
    METRIC_TO_VIEW,
    SchemaLink,
    augment_schema_link,
    build_sql_prompt,
    resolve,
    validate,
)

# ----- column-to-view mapping -----


def test_road_total_km_maps_to_infrastructure() -> None:
    hint = resolve("Qaysi 10 mahalla road_total_km bo'yicha eng katta?")
    assert "v_mahalla_infrastructure" in hint.forced_views
    assert "road_total_km" in hint.forced_columns


def test_road_asphalt_km_maps_to_infrastructure() -> None:
    hint = resolve("road_asphalt_km bo'yicha top 10")
    assert "v_mahalla_infrastructure" in hint.forced_views
    assert "road_asphalt_km" in hint.forced_columns


def test_medical_facility_distance_km_maps_to_infrastructure() -> None:
    hint = resolve("medical_facility_distance_km bo'yicha eng uzoq 10 mahalla")
    assert "v_mahalla_infrastructure" in hint.forced_views


def test_crop_total_homestead_area_sotkah_maps_to_v_mahallas_and_forbids_derivation() -> None:
    hint = resolve("Qaysi 10 mahallada crop_total_homestead_area_sotkah eng yuqori?")
    assert "v_mahallas" in hint.forced_views
    assert any("homestead_area_ha * 10" in f for f in hint.forbidden_calculations)


def test_metric_to_view_authoritative_table() -> None:
    """Sanity: every mapping points to a view in the catalog."""
    from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG

    for col, view in METRIC_TO_VIEW.items():
        assert view in SEMANTIC_CATALOG, f"{col} maps to unknown view {view}"


# ----- intent / issue-code routing -----


def test_duplicate_district_code_routes_to_dq_view_and_issue_code() -> None:
    hint = resolve("Qaysi district_code takrorlanadi?")
    assert "v_data_quality_issues" in hint.forced_views
    assert "DISTRICT_CODE_DUPLICATE_GLOBAL" in hint.issue_codes


def test_duplicate_stir_count_routes_to_dq_view_and_issue_code() -> None:
    hint = resolve("Nechta mahalla STIR qiymati bir martadan ko'p uchraydi?")
    assert "v_data_quality_issues" in hint.forced_views
    assert "MAHALLA_STIR_DUPLICATE" in hint.issue_codes


def test_data_quality_total_request_includes_total_note() -> None:
    hint = resolve("Joriy importda jami nechta data quality muammosi bor?")
    assert "v_data_quality_issues" in hint.forced_views
    assert any("total_issues" in n for n in hint.extra_notes)


def test_region_mahalla_count_mismatch_routes_to_v_regions() -> None:
    hint = resolve("Qaysi viloyatlarda mahalla soni mos kelmaydi?")
    assert "v_regions" in hint.forced_views


# ----- pattern + limit detection -----


def test_distribution_question_forces_limit_100() -> None:
    hint = resolve("Har bir specialization_type_cyr toifasida nechta mahalla bor?")
    assert hint.pattern_hint == "distribution"
    assert hint.limit_hint == 100


def test_top_n_question_picks_explicit_n() -> None:
    hint = resolve("Eng yuqori 10 mahalla aholi soni bo'yicha")
    assert hint.pattern_hint == "top_n"
    assert hint.limit_hint == 10


def test_sample_question_picks_explicit_n() -> None:
    hint = resolve("STIR-ning 5 ta namunasini ko'rsating")
    assert hint.pattern_hint in ("sample", "duplicate")
    assert hint.limit_hint == 5


# ----- augment_schema_link merges hint into link -----


def test_augment_adds_forced_views_to_link() -> None:
    link = SchemaLink(relevant_views=("v_mahallas",), pattern="top_n")
    hint = resolve("road_total_km bo'yicha top 10")
    merged = augment_schema_link(link, hint)
    assert "v_mahalla_infrastructure" in merged.relevant_views
    assert "v_mahallas" in merged.relevant_views  # original kept


def test_augment_only_overrides_pattern_when_unknown() -> None:
    link = SchemaLink(pattern="sample")
    hint = resolve("har bir toifa")  # would suggest distribution
    merged = augment_schema_link(link, hint)
    assert merged.pattern == "sample"  # explicit stage-1 wins

    link2 = SchemaLink(pattern="unknown")
    merged2 = augment_schema_link(link2, hint)
    assert merged2.pattern == "distribution"


def test_augment_pushes_issue_codes_into_metric_keys() -> None:
    link = SchemaLink()
    hint = resolve("Nechta mahalla STIR qiymati takror?")
    merged = augment_schema_link(link, hint)
    assert "MAHALLA_STIR_DUPLICATE" in merged.metric_keys


# ----- build_sql_prompt picks up resolver overrides automatically -----


def _sql_block(prompt: str) -> str:
    start = prompt.index("RELEVANT VIEWS (full column detail")
    end = prompt.index("RELEVANT SQL EXAMPLES")
    return prompt[start:end]


def test_sql_prompt_includes_resolver_forced_views_even_if_link_misses_them() -> None:
    # Stage 1 wrongly picked v_mahallas; resolver must add v_mahalla_infrastructure.
    link = SchemaLink(relevant_views=("v_mahallas",), pattern="top_n")
    p = build_sql_prompt("road_total_km bo'yicha eng katta 10 mahalla", link)
    block = _sql_block(p)
    assert "## v_mahalla_infrastructure" in block
    # Resolver block surfaces the override.
    assert "RESOLVER OVERRIDES" in p
    assert "v_mahalla_infrastructure" in p


def test_sql_prompt_explicitly_forbids_moving_columns_between_views() -> None:
    p = build_sql_prompt("road_total_km bo'yicha eng katta", SchemaLink())
    assert "NEVER move a column to another view" in p
    assert "v_mahallas does not have those columns" in p


def test_sql_prompt_forbids_derived_calculation_when_source_column_exists() -> None:
    p = build_sql_prompt(
        "Qaysi 10 mahallada crop_total_homestead_area_sotkah eng yuqori?",
        SchemaLink(),
    )
    assert "NEVER calculate a source column that already exists" in p
    assert "homestead_area_ha * 10" in p


def test_sql_prompt_passes_issue_code_for_duplicate_questions() -> None:
    p = build_sql_prompt(
        "Nechta mahalla STIR qiymati bir martadan ko'p uchraydi?",
        SchemaLink(),
    )
    assert "MAHALLA_STIR_DUPLICATE" in p
    block = _sql_block(p)
    assert "## v_data_quality_issues" in block


def test_sql_prompt_distribution_question_carries_limit_hint() -> None:
    p = build_sql_prompt(
        "Har bir specialization_type_cyr toifasida nechta mahalla bor?",
        SchemaLink(),
    )
    assert "limit_hint            : 100" in p
    assert "distribution" in p


def test_sql_prompt_top_n_question_carries_explicit_n() -> None:
    p = build_sql_prompt(
        "Eng yuqori 10 mahalla aholi soni bo'yicha",
        SchemaLink(),
    )
    assert "limit_hint            : 10" in p


# ----- example bank still passes guard -----


def test_every_example_still_passes_sql_guard() -> None:
    for ex in EXAMPLES:
        try:
            validate(ex.sql)
        except Exception as exc:  # noqa: BLE001
            raise AssertionError(f"{ex.title!r} failed: {exc}\n{ex.sql}") from exc
