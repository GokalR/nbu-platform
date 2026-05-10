"""Tests for Phase 2B2 numeric profiler. Synthetic fixtures only."""

from __future__ import annotations

import json
from pathlib import Path

from cerr_chatbot.config import Settings
from cerr_chatbot.numeric_profile import (
    ValueBag,
    compute_stats,
    run_numeric_profile,
    write_markdown,
)
from cerr_chatbot.numeric_profile.collectors import Collected, collect

# ------------------- stats unit tests -------------------


def test_compute_stats_basic_quantiles() -> None:
    bag = ValueBag()
    for v in range(1, 101):  # 1..100
        bag.add(v)
    s = compute_stats(bag)
    assert s.total == 100
    assert s.non_null_count == 100
    assert s.null_count == 0
    assert s.null_percent == 0.0
    assert s.min == 1.0
    assert s.max == 100.0
    assert s.median == 50.5
    assert s.p01 == 1.99
    assert s.p99 == 99.01
    assert s.zero_count == 0
    assert s.negative_count == 0


def test_compute_stats_handles_nulls_and_bad_values() -> None:
    bag = ValueBag()
    bag.add(None)
    bag.add(None)
    bag.add(10)
    bag.add(20)
    bag.add("oops")
    bag.add(True)  # bool excluded from numeric stream
    s = compute_stats(bag)
    assert s.total == 6
    assert s.null_count == 2
    assert s.null_percent == 33.33
    assert s.type_distribution == {"null": 2, "int": 2, "string": 1, "bool": 1}
    assert "oops" in s.bad_value_examples
    assert True in s.bad_value_examples
    assert s.median == 15.0


def test_compute_stats_empty_bag() -> None:
    s = compute_stats(ValueBag())
    assert s.total == 0
    assert s.min is None
    assert s.median is None


def test_compute_stats_negative_and_zero_counts() -> None:
    bag = ValueBag()
    for v in [-5, -1, 0, 0, 0, 7]:
        bag.add(v)
    s = compute_stats(bag)
    assert s.negative_count == 2
    assert s.zero_count == 3
    assert s.min == -5.0
    assert s.max == 7.0


# ------------------- collector + runner tests -------------------


def _kpi(key: str, value: object, change_pct: object = None, district_avg: object = None) -> dict:
    return {
        "key": key,
        "label": f"L_{key}",
        "table": "fact_base",
        "column": key,
        "format": "raw",
        "provenance": "live",
        "direction": "neu",
        "value": value,
        "error": None,
        "change_pct": change_pct,
        "district_avg": district_avg,
        "compare_scope": "district",
    }


def _build_region(region_code: int, district_code: int, mahallas: list[dict]) -> dict:
    return {
        "region_code": region_code,
        "region_name": f"R{region_code}",
        "districts_count": 1,
        "region_mahalla_count": len(mahallas),
        "region_overview": {
            "kpis": [_kpi("population", 100000)],
            "header": {},
        },
        "districts": [
            {
                "code": district_code,
                "name": "D",
                "mahalla_count": len(mahallas),
                "overview": {
                    "kpis": [_kpi("population", 50000), _kpi("rating_score", 60.0)],
                },
                "macro": {
                    "indicators": [
                        {
                            "key": "industry_volume_bln_uzs",
                            "label": "Industry",
                            "unit": "bln UZS",
                            "direction": "up",
                            "points": [
                                {"district_name": "D", "value": 100.0, "highlighted": True},
                                {"district_name": "X", "value": 200.0, "highlighted": False},
                            ],
                        }
                    ]
                },
                "mahallas": mahallas,
            }
        ],
    }


def _mahalla(stir: str, **detail: object) -> dict:
    overview = {
        "kpis": [
            _kpi("population", detail.get("population", 1000)),
            _kpi("rating_score", detail.get("rating", 50.0)),
        ],
        "appeals": {"crime": detail.get("crime", 0), "aid": detail.get("aid", 1)},
        "detail": {
            "infra": {"road_km": detail.get("road_km", 1.0)},
            "specialization": {
                "items": [
                    {
                        "slot": "main",
                        "households": detail.get("hh", 10),
                        "population": detail.get("pop", 50),
                        "percent": detail.get("share", 25.0),
                    }
                ],
                "residual_percent": detail.get("residual", 5.0),
                "total_known_percent": detail.get("known", 95.0),
            },
            "crops": {
                "seasons": [
                    {
                        "key": "main",
                        "total_area_ha": detail.get("area", 2.0),
                        "homestead_area_ha": detail.get("hs_ha", 1.0),
                        "household_count": detail.get("hh", 10),
                    }
                ],
                "total_homestead_area_sotikh": detail.get("hs_sotikh", 50.0),
            },
            "subsidies": {
                "programs": [
                    {
                        "label": "P1",
                        "applications": detail.get("apps", 1),
                        "required_amount_mln": detail.get("amt", 5.0),
                    }
                ]
            },
        },
        "peer_profile": {
            "strengths": [
                {
                    "key": "factor_a",
                    "label": "FA",
                    "unit": "u",
                    "direction": "up",
                    "this_value": detail.get("fa_this", 1.0),
                    "district_avg": detail.get("fa_avg", 0.5),
                    "peer_rank": detail.get("fa_rank", 1),
                    "peer_count": detail.get("fa_pcount", 5),
                    "percentile": detail.get("fa_pct", 90.0),
                }
            ],
            "weaknesses": [
                {
                    "key": "factor_b",
                    "label": "FB",
                    "unit": "u",
                    "direction": "down",
                    "this_value": detail.get("fb_this", 10.0),
                    "district_avg": detail.get("fb_avg", 5.0),
                    "peer_rank": detail.get("fb_rank", 5),
                    "peer_count": detail.get("fb_pcount", 5),
                    "percentile": detail.get("fb_pct", 10.0),
                }
            ],
        },
    }
    return {"stir": stir, "name": f"M{stir}", "rating_score": 50.0, "overview": overview}


def _make_source(tmp_path: Path) -> Path:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _build_region(
        1100,
        1100201,
        [
            _mahalla("100000001", crime=2, road_km=1.0),
            _mahalla("100000002", crime=None, road_km=None),
            _mahalla("100000003", crime=4, road_km=3.0),
        ],
    )
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    return src


def test_run_collects_levels_and_kpis(tmp_path: Path) -> None:
    src = _make_source(tmp_path)
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    assert report.entity_counts == {"region": 1, "district": 1, "mahalla": 3}

    by_key = {(p.level, p.kpi_key): p for p in report.kpi_profiles}
    region_pop = by_key[("region", "population")]
    assert region_pop.row_count == 1
    assert region_pop.value_stats.median == 100000.0
    assert region_pop.distinct_compare_scopes == ["district"]

    mah_pop = by_key[("mahalla", "population")]
    assert mah_pop.row_count == 3
    assert mah_pop.value_stats.null_count == 0
    assert mah_pop.expected_entity_count == 3
    assert mah_pop.missing_entity_count == 0


def test_base_kpi_coverage_flags_missing(tmp_path: Path) -> None:
    src = _make_source(tmp_path)
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    cov = report.base_kpi_coverage
    # Fixture only ships population + rating_score; the rest must be flagged.
    assert cov["mahalla"]["population"] is True
    assert cov["mahalla"]["rating_score"] is True
    assert cov["mahalla"]["active_businesses"] is False
    assert any("BASE_KPI_MISSING" in f for f in report.high_risk_findings)


def test_duplicate_stir_does_not_create_kpi_missing(tmp_path: Path) -> None:
    """Two mahalla rows sharing the same STIR must both count toward completeness."""
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _build_region(
        1100,
        1100201,
        [
            _mahalla("100000001", population=1000),
            _mahalla("100000001", population=2000),  # same STIR, different row
            _mahalla("100000002", population=3000),
        ],
    )
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    by = {(p.level, p.kpi_key): p for p in report.kpi_profiles}
    pop = by[("mahalla", "population")]
    assert pop.expected_entity_count == 3
    assert pop.row_count == 3
    assert pop.missing_entity_count == 0
    nk = report.natural_key_diagnostics
    assert nk.mahalla_stir_unique_count == 2
    assert nk.mahalla_stir_duplicate_group_count == 1
    assert nk.mahalla_stir_duplicate_examples == ["100000001"]
    assert any("MAHALLA_STIR_COLLISION" in f for f in report.high_risk_findings)
    assert not any("KPI_ROWS_MISSING" in f for f in report.high_risk_findings)


def test_duplicate_district_code_does_not_create_macro_missing(tmp_path: Path) -> None:
    """Two district rows sharing district_code must both count for macro coverage."""
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = {
        "region_code": 1100,
        "region_name": "R",
        "districts_count": 2,
        "region_mahalla_count": 0,
        "region_overview": {"kpis": [], "header": {}},
        "districts": [
            {
                "code": 1100201,
                "name": "D1",
                "mahalla_count": 0,
                "overview": {"kpis": []},
                "macro": {
                    "indicators": [
                        {
                            "key": "industry_volume_bln_uzs",
                            "label": "I",
                            "unit": "u",
                            "direction": "up",
                            "points": [{"district_name": "D1", "value": 10.0, "highlighted": True}],
                        }
                    ]
                },
                "mahallas": [],
            },
            {
                "code": 1100201,  # duplicate code
                "name": "D2",
                "mahalla_count": 0,
                "overview": {"kpis": []},
                "macro": {
                    "indicators": [
                        {
                            "key": "industry_volume_bln_uzs",
                            "label": "I",
                            "unit": "u",
                            "direction": "up",
                            "points": [{"district_name": "D2", "value": 20.0, "highlighted": True}],
                        }
                    ]
                },
                "mahallas": [],
            },
        ],
    }
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    macro = {p.indicator_key: p for p in report.macro_indicator_profiles}
    ind = macro["industry_volume_bln_uzs"]
    assert ind.expected_district_count == 2
    assert ind.district_row_count == 2
    assert ind.missing_district_count == 0
    assert ind.highlighted_count == 2
    assert ind.highlighted_missing_count == 0
    nk = report.natural_key_diagnostics
    assert nk.district_code_unique_count == 1
    assert nk.district_code_duplicate_group_count == 1
    assert any("DISTRICT_CODE_COLLISION" in f for f in report.high_risk_findings)
    assert not any("MACRO_MISSING_DISTRICT_ROWS" in f for f in report.high_risk_findings)


def test_macro_highlighted_missing_detected(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = {
        "region_code": 1100,
        "region_name": "R",
        "districts_count": 2,
        "region_mahalla_count": 0,
        "region_overview": {"kpis": [], "header": {}},
        "districts": [
            {
                "code": 1100201,
                "name": "D1",
                "mahalla_count": 0,
                "overview": {"kpis": []},
                "macro": {
                    "indicators": [
                        {
                            "key": "ind_a",
                            "label": "A",
                            "unit": "u",
                            "direction": "up",
                            "points": [{"district_name": "D1", "value": 5.0, "highlighted": True}],
                        }
                    ]
                },
                "mahallas": [],
            },
            {
                "code": 1100202,
                "name": "D2",
                "mahalla_count": 0,
                "overview": {"kpis": []},
                "macro": {
                    "indicators": [
                        {
                            "key": "ind_a",
                            "label": "A",
                            "unit": "u",
                            "direction": "up",
                            # Indicator present, but no point flagged highlighted.
                            "points": [{"district_name": "D2", "value": 7.0, "highlighted": False}],
                        }
                    ]
                },
                "mahallas": [],
            },
        ],
    }
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    macro = {p.indicator_key: p for p in report.macro_indicator_profiles}
    ind = macro["ind_a"]
    assert ind.district_row_count == 2
    assert ind.missing_district_count == 0
    assert ind.highlighted_count == 1
    assert ind.highlighted_missing_count == 1
    assert any("MACRO_HIGHLIGHTED_MISSING" in f for f in report.high_risk_findings)


def test_natural_key_collision_diagnostics(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _build_region(
        1100,
        1100201,
        [
            _mahalla("100000001"),
            _mahalla("100000001"),  # dup STIR within region/district
        ],
    )
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    nk = report.natural_key_diagnostics
    assert nk.mahalla_composite_key_unique_count == 1
    assert nk.mahalla_composite_key_duplicate_group_count == 1
    assert any("MAHALLA_COMPOSITE_KEY_COLLISION" in f for f in report.high_risk_findings)


def test_null_free_field_listing(tmp_path: Path) -> None:
    src = _make_source(tmp_path)
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    # population at every level is null-free in the fixture.
    assert "kpi:mahalla:population" in report.null_free_numeric_fields
    assert "kpi:district:population" in report.null_free_numeric_fields


def test_macro_highlighted_value_stats(tmp_path: Path) -> None:
    src = _make_source(tmp_path)
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    macro = {p.indicator_key: p for p in report.macro_indicator_profiles}
    ind = macro["industry_volume_bln_uzs"]
    assert ind.total_points == 2
    assert ind.highlighted_count == 1
    assert ind.highlighted_value_stats.median == 100.0
    assert ind.all_point_value_stats.median == 150.0


def test_peer_rank_validation(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    bad_mah = _mahalla("100000001", fa_rank=99, fa_pcount=5, fb_pct=200.0)
    payload = _build_region(1100, 1100201, [bad_mah])
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    by = {(p.polarity, p.factor_key): p for p in report.peer_factor_profiles}
    assert by[("strengths", "factor_a")].rank_exceeds_count == 1
    assert by[("weaknesses", "factor_b")].percentile_out_of_range == 1
    assert any("PEER_RANK_EXCEEDS_COUNT" in f for f in report.high_risk_findings)
    assert any("PEER_PERCENTILE_OUT_OF_RANGE" in f for f in report.high_risk_findings)


def test_detail_numeric_field_profiling(tmp_path: Path) -> None:
    src = _make_source(tmp_path)
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    by = {(p.group, p.column_name): p for p in report.detail_field_profiles}
    road = by[("mahalla_infrastructure", "road_total_km")]
    assert road.value_stats.total == 3
    assert road.value_stats.null_count == 1
    crime = by[("mahalla_appeals", "crime_appeal_count")]
    assert crime.value_stats.null_count == 1
    assert crime.value_stats.median == 3.0


def test_collector_skips_non_dict_entries() -> None:
    c = Collected()
    collect(
        {
            "region_code": 1,
            "districts": [None, {"code": 1, "name": "x", "mahalla_count": 0, "mahallas": []}],
        },
        c,
    )
    assert c.region_count == 1
    assert c.district_count == 1
    assert c.mahalla_count == 0


def test_markdown_report_writes(tmp_path: Path) -> None:
    src = _make_source(tmp_path)
    report = run_numeric_profile(Settings(cerr_source_dir=src))
    out = write_markdown(report, tmp_path / "profile_reports")
    text = out.read_text(encoding="utf-8")
    assert "Numeric profile" in text
    assert "Base KPI completeness" in text
    assert "Macro indicator completeness" in text
    assert "Mahalla detail numeric fields" in text
