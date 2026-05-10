"""Two-stage planner: schema linker + SQL prompt + example bank."""

from __future__ import annotations

import json

import pytest

from cerr_chatbot.query import (
    EXAMPLES,
    SchemaLink,
    SchemaLinkParseError,
    build_planner_prompt,
    build_schema_linking_prompt,
    build_sql_prompt,
    parse_schema_linking_response,
    select_examples,
    validate,
)
from cerr_chatbot.query.example_bank import (
    TAG_APPEALS,
    TAG_DUPLICATE,
    TAG_GROUP_BY_REGION,
    TAG_MACRO_INDICATOR,
    TAG_SPECIALIZATION,
    TAG_TOP_N,
)

# -------------------- example bank: every SQL must pass guard --------------------


def test_every_example_passes_sql_guard() -> None:
    for ex in EXAMPLES:
        try:
            validate(ex.sql)
        except Exception as exc:  # noqa: BLE001
            raise AssertionError(f"{ex.title!r} failed sql_guard: {exc}\n{ex.sql}") from exc


def test_every_example_uses_only_known_views() -> None:
    from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG

    for ex in EXAMPLES:
        for v in ex.views:
            assert v in SEMANTIC_CATALOG, f"{ex.title} declares unknown view {v}"


# -------------------- selector behavior --------------------


def test_duplicate_question_returns_duplicate_examples() -> None:
    picks = select_examples(
        "Takrorlanuvchi mahalla STIR namunalarini ko'rsating",
        relevant_views=("v_data_quality_issues",),
        pattern=TAG_DUPLICATE,
        k=5,
    )
    titles = " | ".join(p.title for p in picks)
    assert any("duplicate" in p.title.lower() or TAG_DUPLICATE in p.tags for p in picks), titles


def test_macro_indicator_question_returns_macro_examples() -> None:
    picks = select_examples(
        "industry_volume_bln_uzs bo'yicha eng yuqori 10 tuman",
        relevant_views=("v_district_macro_highlights",),
        pattern=TAG_MACRO_INDICATOR,
        k=5,
    )
    assert any(TAG_MACRO_INDICATOR in p.tags for p in picks), picks


def test_specialization_question_returns_specialization_examples() -> None:
    picks = select_examples(
        "Qaysi specialization_type_cyr eng ko'p uchraydi?",
        relevant_views=("v_mahalla_specializations",),
        pattern="distribution",
        k=5,
    )
    assert any(TAG_SPECIALIZATION in p.tags for p in picks), picks


def test_appeals_by_region_example_uses_group_by_region_only() -> None:
    picks = select_examples(
        "Qaysi viloyatlarda crime_appeal_count yig'indisi eng katta?",
        relevant_views=("v_mahalla_appeals",),
        pattern=TAG_GROUP_BY_REGION,
        k=5,
    )
    appeals = [p for p in picks if TAG_APPEALS in p.tags]
    assert appeals, "expected at least one appeals example"
    region_grouped = [p for p in appeals if TAG_GROUP_BY_REGION in p.tags]
    assert region_grouped, "expected a region-only-grouped example"
    for p in region_grouped:
        # Region-only grouping must NOT also include district in GROUP BY.
        before_after = p.sql.split("GROUP BY", 1)
        assert len(before_after) == 2
        after_group_by = before_after[1]
        assert "district_name_cyr" not in after_group_by, p.sql


def test_top_n_question_picks_top_n_examples() -> None:
    picks = select_examples(
        "Eng yuqori 5 viloyat aholi soni bo'yicha",
        relevant_views=("v_regions",),
        pattern=TAG_TOP_N,
        k=5,
    )
    assert any(TAG_TOP_N in p.tags for p in picks)


def test_selector_returns_k_examples_even_without_signals() -> None:
    picks = select_examples("totally unrelated random text", relevant_views=(), k=4)
    assert len(picks) == 4


# -------------------- schema linker prompt --------------------


def test_schema_linker_prompt_is_compact() -> None:
    p = build_schema_linking_prompt("Aholi soni bo'yicha eng yuqori 5 viloyat")
    # Compact = significantly smaller than the legacy single-pass prompt.
    legacy = build_planner_prompt("Aholi soni bo'yicha eng yuqori 5 viloyat")
    assert len(p) < len(legacy) // 2
    # Mentions the JSON schema fields and pattern enum.
    for needle in (
        "relevant_views",
        "relevant_columns",
        "metric_keys",
        "pattern",
        "ambiguity_notes",
        "top_n",
        "macro_indicator",
        "industry_volume_bln_uzs",
        "MAHALLA_STIR_DUPLICATE",
    ):
        assert needle in p, needle


def test_schema_linker_parse_accepts_valid_json() -> None:
    raw = json.dumps(
        {
            "relevant_views": ["v_regions"],
            "relevant_columns": ["population", "region_name_cyr"],
            "metric_keys": [],
            "pattern": "top_n",
            "ambiguity_notes": [],
        }
    )
    link = parse_schema_linking_response(raw)
    assert link.relevant_views == ("v_regions",)
    assert link.pattern == "top_n"


def test_schema_linker_parse_drops_unknown_views() -> None:
    raw = json.dumps(
        {
            "relevant_views": ["v_regions", "v_does_not_exist"],
            "relevant_columns": [],
            "metric_keys": [],
            "pattern": "top_n",
        }
    )
    link = parse_schema_linking_response(raw)
    assert link.relevant_views == ("v_regions",)


def test_schema_linker_parse_rejects_unknown_pattern() -> None:
    raw = json.dumps(
        {
            "relevant_views": ["v_regions"],
            "pattern": "magic",
        }
    )
    with pytest.raises(SchemaLinkParseError, match="pattern"):
        parse_schema_linking_response(raw)


def test_schema_linker_parse_rejects_malformed_json() -> None:
    with pytest.raises(SchemaLinkParseError):
        parse_schema_linking_response("not json")


# -------------------- stage-2 SQL prompt --------------------


def test_sql_prompt_is_compact_versus_legacy() -> None:
    link = SchemaLink(relevant_views=("v_regions",), pattern="top_n")
    p = build_sql_prompt("Aholi soni bo'yicha eng yuqori 5 viloyat", link)
    legacy = build_planner_prompt("Aholi soni bo'yicha eng yuqori 5 viloyat")
    # Stage-2 should be significantly smaller than the legacy one-shot prompt.
    assert len(p) < len(legacy) // 2


def test_sql_prompt_contains_only_relevant_views_in_full_detail() -> None:
    link = SchemaLink(relevant_views=("v_regions",), pattern="top_n")
    p = build_sql_prompt("Aholi soni bo'yicha eng yuqori 5 viloyat", link)
    # The full-detail catalog block lives between known anchors.
    start = p.index("RELEVANT VIEWS (full column detail")
    end = p.index("RELEVANT SQL EXAMPLES")
    catalog_block = p[start:end]
    assert "## v_regions" in catalog_block
    # Detail views NOT mentioned by stage 1 should not be expanded fully.
    for hidden in ("## v_mahallas", "## v_district_macro_highlights", "## v_data_quality_issues"):
        assert hidden not in catalog_block, hidden


def test_sql_prompt_includes_few_relevant_examples() -> None:
    link = SchemaLink(relevant_views=("v_regions",), pattern="top_n")
    p = build_sql_prompt("Aholi soni bo'yicha eng yuqori 5 viloyat", link, k_examples=5)
    # Exactly k example headers in the SQL examples block.
    examples_section = p[p.index("RELEVANT SQL EXAMPLES") :]
    headers = [line for line in examples_section.splitlines() if line.startswith("EXAMPLE ")]
    assert len(headers) == 5


def test_sql_prompt_macro_picks_macro_examples() -> None:
    link = SchemaLink(
        relevant_views=("v_district_macro_highlights",),
        metric_keys=("industry_volume_bln_uzs",),
        pattern="macro_indicator",
    )
    p = build_sql_prompt("industry_volume_bln_uzs bo'yicha eng yuqori 10 tuman", link, k_examples=5)
    examples_section = p[p.index("RELEVANT SQL EXAMPLES") :]
    assert "indicator_key" in examples_section
    # Macro indicator example must reference the named key in some form.
    assert "industry_volume_bln_uzs" in examples_section or "macro" in examples_section.lower()


def test_sql_prompt_no_link_falls_back_to_full_catalog() -> None:
    link = SchemaLink()  # nothing linked
    p = build_sql_prompt("anything", link)
    catalog_block = p[
        p.index("RELEVANT VIEWS (full column detail") : p.index("RELEVANT SQL EXAMPLES")
    ]
    # Without a link, stage 2 falls back to listing every view to be safe.
    for view in (
        "## v_regions",
        "## v_districts",
        "## v_mahallas",
        "## v_district_macro_highlights",
        "## v_data_quality_issues",
    ):
        assert view in catalog_block, view


def test_sql_prompt_repeats_hard_safety_rules() -> None:
    link = SchemaLink(relevant_views=("v_mahallas",), pattern="top_n")
    p = build_sql_prompt("test", link)
    for needle in (
        "SELECT only",
        "SELECT *",
        "natural keys",
        "surrogate ids",
        "ma'lumot yo'q",
        "GROUP BY region_name_cyr ONLY",
    ):
        assert needle in p, needle
