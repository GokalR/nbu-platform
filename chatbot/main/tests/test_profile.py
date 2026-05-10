"""Tests for Phase 2B1 profiler. Synthetic fixtures only."""

from __future__ import annotations

import json
from pathlib import Path

from cerr_chatbot.config import Settings
from cerr_chatbot.profile import lookup, run_profile, write_markdown
from cerr_chatbot.profile.walker import _PathStats, walk


def _agg() -> dict[str, _PathStats]:
    return {}


def test_walker_records_scalar_path() -> None:
    a = _agg()
    walk({"x": 5, "y": "abc"}, "root", a)
    assert a["root.x"].presence == 1
    assert a["root.x"].null == 0
    assert "int" in a["root.x"].types
    assert a["root.x"].examples == [5]
    assert "string" in a["root.y"].types


def test_walker_recurses_into_nested_object() -> None:
    a = _agg()
    walk({"outer": {"inner": 7}}, "root", a)
    assert "object" in a["root.outer"].types
    assert a["root.outer.inner"].presence == 1
    assert "int" in a["root.outer.inner"].types


def test_walker_array_uses_brackets() -> None:
    a = _agg()
    walk({"items": [{"k": "a"}, {"k": "b"}]}, "root", a)
    assert "array" in a["root.items"].types
    # Two array items merge into one canonical path with [] notation.
    assert a["root.items[]"].presence == 2
    assert a["root.items[].k"].presence == 2
    assert sorted(a["root.items[].k"].examples) == ["a", "b"]


def test_walker_counts_nulls_and_total_presence() -> None:
    a = _agg()
    walk({"x": None}, "root", a)
    walk({"x": 1}, "root", a)
    walk({"x": None}, "root", a)
    assert a["root.x"].presence == 3
    assert a["root.x"].null == 2
    assert "int" in a["root.x"].types
    assert "null" in a["root.x"].types


def test_walker_caps_examples_to_three_unique() -> None:
    a = _agg()
    for v in ["a", "b", "c", "d", "a"]:
        walk({"x": v}, "root", a)
    assert a["root.x"].examples == ["a", "b", "c"]


def test_walker_prunes_geo_subtree() -> None:
    a = _agg()
    walk({"districts": [{"geo": {"features": [{"deeply": "nested"}]}}]}, "region", a)
    # The .geo path is recorded …
    assert "region.districts[].geo" in a
    assert "object" in a["region.districts[].geo"].types
    # … but children of .geo are not.
    assert not any(p.startswith("region.districts[].geo.") for p in a)


def test_catalog_lookup_known_paths() -> None:
    assert lookup("region.region_code").column == "region_code"
    assert lookup("region.districts[].code").column == "district_code"
    assert lookup("region.districts[].mahallas[].stir").column == "mahalla_stir"
    assert (
        lookup("region.districts[].mahallas[].overview.detail.infra.road_km").column
        == "road_total_km"
    )
    assert (
        lookup("region.districts[].mahallas[].overview.appeals.crime").column
        == "crime_appeal_count"
    )


def _make_min_region(tmp_path: Path) -> Path:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = {
        "region_code": 1100,
        "region_name": "Test region",
        "region_mahalla_count": 1,
        "districts_count": 1,
        "region_overview": {
            "header": {"title": "T", "subtitle": "S", "breadcrumb": ["U"], "meta": []},
            "kpis": [
                {
                    "key": "population",
                    "label": "Pop",
                    "value": 10,
                    "change_pct": None,
                    "district_avg": None,
                }
            ],
        },
        "districts": [
            {
                "code": 1100201,
                "name": "D",
                "mahalla_count": 1,
                "geo": {"type": "FeatureCollection", "features": [{"x": 1}]},
                "mahallas": [
                    {
                        "stir": "100000001",
                        "name": "M",
                        "rating_score": 50.0,
                        "overview": {
                            "detail": {
                                "infra": {"road_km": 1.0},
                            },
                            "appeals": {"crime": 3, "year": 2026},
                        },
                    }
                ],
            }
        ],
    }
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    return src


def test_run_profile_assigns_proposed_columns(tmp_path: Path) -> None:
    src = _make_min_region(tmp_path)
    report = run_profile(Settings(cerr_source_dir=src))
    by_path = {fp.path: fp for fp in report.field_paths}
    assert by_path["region.region_code"].proposed_column_name == "region_code"
    assert by_path["region.districts[].code"].proposed_column_name == "district_code"
    assert by_path["region.districts[].mahallas[].stir"].proposed_column_name == "mahalla_stir"
    assert (
        by_path["region.districts[].mahallas[].overview.detail.infra.road_km"].proposed_column_name
        == "road_total_km"
    )
    assert (
        by_path["region.districts[].mahallas[].overview.appeals.crime"].proposed_column_name
        == "crime_appeal_count"
    )
    # geo subtree pruned
    assert not any(p.startswith("region.districts[].geo.") for p in by_path)


def test_markdown_report_writes_with_section(tmp_path: Path) -> None:
    src = _make_min_region(tmp_path)
    report = run_profile(Settings(cerr_source_dir=src))
    out = write_markdown(report, tmp_path / "profile_reports")
    text = out.read_text(encoding="utf-8")
    assert "Recommended Future Column Names" in text
    assert "Important uncataloged paths" in text
    assert "Ignored paths" in text


# ---------- mojibake / catalog quality ----------

import re  # noqa: E402

from cerr_chatbot.profile.catalog import (  # noqa: E402
    COLUMN_CATALOG,
    IGNORED_PATHS,
)

# Common mojibake markers produced by reading UTF-8 Cyrillic as cp1251 or
# similar single-byte codecs. Hand-written English descriptions must never
# contain these; real source data examples may legitimately contain Cyrillic
# but never these specific Latin-Cyrillic transliteration artifacts.
_MOJIBAKE_PAT = re.compile(r"РјР°|С‡|вЂ|РІР|Р°Р|РЅР|РєР|РѕР|РіР")


def _has_mojibake(text: str) -> bool:
    return bool(_MOJIBAKE_PAT.search(text))


def test_catalog_descriptions_are_ascii_english() -> None:
    """Hand-written catalog descriptions must be ASCII to avoid encoding loss."""
    offenders: list[tuple[str, str]] = []
    for path, spec in COLUMN_CATALOG.items():
        try:
            spec.description.encode("ascii")
        except UnicodeEncodeError:
            offenders.append((path, spec.description))
    assert not offenders, f"non-ASCII catalog descriptions: {offenders[:5]}"


def test_ignored_path_reasons_are_ascii_english() -> None:
    offenders: list[tuple[str, str]] = []
    for path, reason in IGNORED_PATHS.items():
        try:
            reason.encode("ascii")
        except UnicodeEncodeError:
            offenders.append((path, reason))
    assert not offenders, f"non-ASCII ignored reasons: {offenders[:5]}"


def test_catalog_descriptions_have_no_mojibake() -> None:
    offenders = [
        (path, spec.description)
        for path, spec in COLUMN_CATALOG.items()
        if _has_mojibake(spec.description)
    ]
    assert not offenders, f"mojibake in catalog: {offenders[:5]}"


def test_required_kpi_metadata_paths_are_cataloged() -> None:
    required_district = [
        "region.districts[].overview.kpis[].label",
        "region.districts[].overview.kpis[].table",
        "region.districts[].overview.kpis[].column",
        "region.districts[].overview.kpis[].format",
        "region.districts[].overview.kpis[].provenance",
        "region.districts[].overview.kpis[].direction",
        "region.districts[].overview.kpis[].error",
        "region.districts[].overview.kpis[].compare_scope",
    ]
    required_mahalla = [
        p.replace("districts[].overview", "districts[].mahallas[].overview")
        for p in required_district
    ]
    missing = [p for p in required_district + required_mahalla if p not in COLUMN_CATALOG]
    assert not missing, missing


def test_required_peer_weakness_paths_are_cataloged() -> None:
    base = "region.districts[].mahallas[].overview.peer_profile.weaknesses[]"
    required = [
        f"{base}.key",
        f"{base}.label",
        f"{base}.unit",
        f"{base}.direction",
        f"{base}.this_value",
        f"{base}.district_avg",
        f"{base}.peer_rank",
        f"{base}.peer_count",
        f"{base}.percentile",
    ]
    missing = [p for p in required if p not in COLUMN_CATALOG]
    assert not missing, missing


def test_required_metadata_paths_are_cataloged() -> None:
    required = [
        "region.districts[].mahallas[].overview.code",
        "region.districts[].mahallas[].overview.detail.subsidies.year",
        "region.districts[].mahallas[].overview.detail.subsidies.data_date",
        "region.districts[].mahallas[].overview.detail.specialization.residual_percent",
        "region.districts[].mahallas[].overview.detail.specialization.total_known_percent",
        "region.districts[].mahallas[].overview.header.meta[].label",
        "region.districts[].mahallas[].overview.header.meta[].value",
        "region.districts[].mahallas[].overview.ai_insights.model",
        "region.districts[].mahallas[].overview.ai_insights.generated_at",
        "region.districts[].mahallas[].overview.ai_insights.pros[]",
        "region.districts[].mahallas[].overview.ai_insights.cons[]",
    ]
    missing = [p for p in required if p not in COLUMN_CATALOG]
    assert not missing, missing


def test_generated_markdown_catalog_section_has_no_mojibake(tmp_path: Path) -> None:
    src = _make_min_region(tmp_path)
    report = run_profile(Settings(cerr_source_dir=src))
    out = write_markdown(report, tmp_path / "profile_reports")
    text = out.read_text(encoding="utf-8")
    # Slice from the catalog section to the next H2 so we only inspect
    # hand-written descriptions, not source-data examples.
    start = text.index("## Recommended Future Column Names")
    end = text.index("## Important uncataloged paths")
    section = text[start:end]
    assert not _has_mojibake(section), "mojibake found in catalog section of MD report"
