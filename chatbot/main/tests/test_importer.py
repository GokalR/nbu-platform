"""Tests for Phase 4A importer. Synthetic fixtures + sqlite engine only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cerr_chatbot.config import Settings
from cerr_chatbot.db import (
    Base,
    DataQualityIssue,
    District,
    DistrictMacroIndicator,
    DistrictMacroPoint,
    DistrictRatingHistogram,
    EntityKpi,
    ImportRun,
    Mahalla,
    MahallaAppealRow,
    MahallaCropSeason,
    MahallaInfrastructureRow,
    MahallaPeerFactor,
    MahallaSpecializationItem,
    MahallaSubsidyProgram,
    Region,
    SourceRegionFile,
)
from cerr_chatbot.importer import run_import


def _engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    return e


def _kpi(key: str, value: object = 1, **extra: object) -> dict:
    base = {
        "key": key,
        "label": f"L_{key}",
        "table": "fact_base",
        "column": key,
        "format": "raw",
        "provenance": "live",
        "direction": "neu",
        "value": value,
        "error": None,
        "change_pct": None,
        "district_avg": None,
        "compare_scope": None,
    }
    base.update(extra)
    return base


def _mahalla(stir: str | None, name: str = "M") -> dict:
    return {
        "stir": stir,
        "name": name,
        "rating_score": 50.0,
        "overview": {
            "code": stir or "",
            "header": {
                "title": name,
                "district_rank": "1/10",
                "region_rank": "10/100",
                "category": "1",
                "meta": [],
            },
            "kpis": [_kpi("population", 1000)],
        },
    }


def _district(code: int | None, name: str, mahallas: list[dict]) -> dict:
    return {
        "code": code,
        "name": name,
        "mahalla_count": len(mahallas),
        "overview": {
            "header": {"title": name},
            "kpis": [_kpi("population", 50000)],
        },
        "macro": {"period": "Q1", "indicators": []},
        "mahallas": mahallas,
    }


def _region_payload(region_code: int, districts: list[dict]) -> dict:
    return {
        "region_code": region_code,
        "region_name": f"R{region_code}",
        "generated_at": "2026-05-01T00:00:00",
        "districts_count": len(districts),
        "region_mahalla_count": sum(d["mahalla_count"] for d in districts),
        "region_overview": {
            "header": {"title": f"R{region_code}"},
            "kpis": [_kpi("population", 100000)],
        },
        "districts": districts,
    }


def _write(src: Path, region_code: int, payload: dict) -> Path:
    src.mkdir(exist_ok=True)
    p = src / f"cerr_region_{region_code}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _settings(src_dir: Path) -> Settings:
    return Settings(cerr_source_dir=src_dir)


# ----- happy path -----


def test_import_inserts_entities_and_kpis(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(
            1100,
            [
                _district(1100201, "D1", [_mahalla("100000001"), _mahalla("100000002")]),
                _district(1100202, "D2", [_mahalla("100000003")]),
            ],
        ),
    )
    engine = _engine()
    summary = run_import(engine, _settings(src))

    assert summary.status == "completed"
    assert summary.files == 1
    assert summary.regions == 1
    assert summary.districts == 2
    assert summary.mahallas == 3
    # 1 region kpi + 2 district kpis + 3 mahalla kpis
    assert summary.entity_kpis == 6

    with Session(engine) as s:
        run = s.execute(select(ImportRun)).scalar_one()
        assert run.status == "completed"
        assert run.completed_at is not None
        assert s.execute(select(SourceRegionFile)).scalars().all()
        assert s.execute(select(Region)).scalar_one().region_code == 1100

        # Hierarchy linked by surrogate IDs only.
        regions = s.execute(select(Region)).scalars().all()
        districts = s.execute(select(District)).scalars().all()
        mahallas = s.execute(select(Mahalla)).scalars().all()
        assert all(d.region_id == regions[0].region_id for d in districts)
        d_by_code = {d.district_code: d for d in districts}
        for m in mahallas:
            # Parent surrogate matches the source-nested district.
            assert m.region_id == regions[0].region_id
            assert m.district_id in {d.district_id for d in districts}
            # district_code carried as a column equals parent's district_code.
            assert m.district_code == d_by_code[m.district_code].district_code


# ----- duplicate natural keys must NOT be merged -----


def test_duplicate_district_code_in_two_regions_remains_two_rows(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(src, 1100, _region_payload(1100, [_district(9999999, "X", [])]))
    _write(src, 1200, _region_payload(1200, [_district(9999999, "Y", [])]))
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.districts == 2
    with Session(engine) as s:
        rows = s.execute(select(District).where(District.district_code == 9999999)).scalars().all()
        assert len(rows) == 2
        assert {r.district_name_cyr for r in rows} == {"X", "Y"}
        assert len({r.region_id for r in rows}) == 2


def test_duplicate_mahalla_stir_remains_two_rows(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(
            1100,
            [_district(1100201, "D1", [_mahalla("100000001"), _mahalla("100000001")])],
        ),
    )
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.mahallas == 2
    with Session(engine) as s:
        rows = s.execute(select(Mahalla).where(Mahalla.mahalla_stir == "100000001")).scalars().all()
        assert len(rows) == 2
        # Distinct surrogate IDs and distinct source ordering.
        assert len({r.mahalla_id for r in rows}) == 2
        assert {r.source_mahalla_index for r in rows} == {0, 1}


def test_same_mahalla_name_in_different_districts_stays_separate(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(
            1100,
            [
                _district(1100201, "D1", [_mahalla("100000001", "Same")]),
                _district(1100202, "D2", [_mahalla("100000002", "Same")]),
            ],
        ),
    )
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.mahallas == 2
    with Session(engine) as s:
        rows = s.execute(select(Mahalla).where(Mahalla.mahalla_name_cyr == "Same")).scalars().all()
        assert len(rows) == 2
        assert {r.district_id for r in rows} == {
            d.district_id for d in s.execute(select(District)).scalars().all()
        }


# ----- KPI fidelity -----


def test_kpi_missing_null_error_values_stored_as_is(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [
                    {
                        "stir": "100000001",
                        "name": "M",
                        "rating_score": None,
                        "overview": {
                            "header": {},
                            "kpis": [
                                _kpi("population", None),
                                _kpi("rating_score", 60.0, error="upstream_error"),
                                _kpi(
                                    "active_businesses",
                                    -5,
                                    change_pct=-99.9,
                                    district_avg=None,
                                ),
                            ],
                        },
                    }
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.entity_kpis == 5  # 1 region + 1 district + 3 mahalla
    with Session(engine) as s:
        m_kpis = (
            s.execute(select(EntityKpi).where(EntityKpi.entity_level == "mahalla")).scalars().all()
        )
        by_key = {k.kpi_key: k for k in m_kpis}
        assert by_key["population"].kpi_value_num is None
        assert by_key["rating_score"].kpi_error_text == "upstream_error"
        assert by_key["rating_score"].kpi_value_num == 60.0
        assert by_key["active_businesses"].kpi_value_num == -5.0
        assert by_key["active_businesses"].change_percent == -99.9
        assert by_key["active_businesses"].district_average_value is None


# ----- exactly-one entity FK -----


def test_kpi_rows_have_exactly_one_entity_fk(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])]),
    )
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        for k in s.execute(select(EntityKpi)).scalars().all():
            filled = sum(1 for v in (k.region_id, k.district_id, k.mahalla_id) if v is not None)
            assert filled == 1, (k.entity_level, k.region_id, k.district_id, k.mahalla_id)


# ----- audit issues persisted, no entity mutation -----


def test_audit_issues_persisted_without_mutating_entities(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    # Declared mahalla count lies; importer must not "fix" it.
    payload = _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])])
    payload["region_mahalla_count"] = 999
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    with Session(engine) as s:
        region = s.execute(select(Region)).scalar_one()
        assert region.declared_mahalla_count == 999
        assert region.actual_mahalla_count == 1
        issues = s.execute(select(DataQualityIssue)).scalars().all()
        codes = {i.issue_code for i in issues}
        assert "REGION_MAHALLA_COUNT_MISMATCH" in codes
    assert summary.issues_total > 0
    assert summary.issues_by_code.get("REGION_MAHALLA_COUNT_MISMATCH", 0) >= 1


# ----- failure path: no completed partial run -----


def test_source_file_count_populated(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(src, 1100, _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])]))
    _write(src, 1200, _region_payload(1200, [_district(1200201, "D", [_mahalla("200000001")])]))
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        run = s.execute(select(ImportRun)).scalar_one()
        assert run.source_file_count == 2
        assert run.status == "completed"


def test_file_sha256_hashes_original_bytes(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])])
    p = src / "cerr_region_1100.json"
    # Compact JSON.
    p.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    e1 = _engine()
    run_import(e1, _settings(src))
    with Session(e1) as s:
        sha_compact = s.execute(select(SourceRegionFile)).scalar_one().file_sha256
        size_compact = s.execute(select(SourceRegionFile)).scalar_one().file_size_bytes

    # Same JSON content, formatted differently => different bytes => different hash.
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    e2 = _engine()
    run_import(e2, _settings(src))
    with Session(e2) as s:
        sha_pretty = s.execute(select(SourceRegionFile)).scalar_one().file_sha256
        size_pretty = s.execute(select(SourceRegionFile)).scalar_one().file_size_bytes

    assert sha_compact != sha_pretty
    assert size_compact != size_pretty


def test_empty_districts_list_actual_mahalla_count_is_zero(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(src, 1100, _region_payload(1100, []))
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        region = s.execute(select(Region)).scalar_one()
        assert region.actual_district_count == 0
        assert region.actual_mahalla_count == 0


def test_missing_districts_field_actual_counts_null(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _region_payload(1100, [])
    payload.pop("districts")  # source shape lacks districts entirely
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        region = s.execute(select(Region)).scalar_one()
        assert region.actual_district_count is None
        assert region.actual_mahalla_count is None


def test_critical_dq_issues_still_allow_completed(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])])
    payload["region_mahalla_count"] = 999  # triggers critical
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.status == "completed"
    assert summary.issues_total > 0
    with Session(engine) as s:
        run = s.execute(select(ImportRun)).scalar_one()
        assert run.status == "completed"
        assert run.completed_at is not None


def test_audit_failure_marks_run_failed(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "cerr_runs"
    _write(src, 1100, _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])]))
    engine = _engine()
    from cerr_chatbot.importer import runner as runner_mod

    def boom(_cfg):
        raise RuntimeError("audit blew up")

    monkeypatch.setattr(runner_mod, "run_audit", boom)
    with pytest.raises(RuntimeError):
        run_import(engine, _settings(src))
    with Session(engine) as s:
        run = s.execute(select(ImportRun)).scalar_one()
        assert run.status == "failed"
        assert run.completed_at is None
        assert "audit blew up" in (run.notes or "")


def test_issue_persistence_failure_marks_run_failed(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "cerr_runs"
    _write(src, 1100, _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])]))
    engine = _engine()

    # Force the issue-persistence Session to fail by patching DataQualityIssue
    # to a constructor that raises on first instantiation. This happens after
    # entities/KPIs already committed - run must end in "failed".
    from cerr_chatbot.importer import runner as runner_mod

    class _Boom:
        def __init__(self, *_a, **_kw):
            raise RuntimeError("issue persistence blew up")

    # Need at least one issue to trigger - lie about region_mahalla_count.
    _write(
        src,
        1100,
        {
            **_region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])]),
            "region_mahalla_count": 999,
        },
    )
    monkeypatch.setattr(runner_mod, "DataQualityIssue", _Boom)
    with pytest.raises(RuntimeError):
        run_import(engine, _settings(src))
    with Session(engine) as s:
        run = s.execute(select(ImportRun)).scalar_one()
        assert run.status == "failed"
        assert run.completed_at is None


# ----- Phase 4B: macro indicators + points + rating histogram -----


def _district_with_macro(
    code: int,
    name: str,
    indicators: list[dict],
    rating_histogram: list[dict] | None = None,
    mahallas: list[dict] | None = None,
) -> dict:
    overview: dict = {"header": {"title": name}, "kpis": []}
    if rating_histogram is not None:
        overview["rating_histogram"] = rating_histogram
    return {
        "code": code,
        "name": name,
        "mahalla_count": len(mahallas or []),
        "overview": overview,
        "macro": {"period": "Q1", "indicators": indicators},
        "mahallas": mahallas or [],
    }


def _indicator(
    key: str,
    points: list[dict],
    label: str = "L",
    unit: str = "u",
    direction: str = "up",
) -> dict:
    return {
        "key": key,
        "label": label,
        "unit": unit,
        "direction": direction,
        "points": points,
    }


def test_macro_indicator_and_points_imported(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district_with_macro(
                1100201,
                "D1",
                [
                    _indicator(
                        "ind_a",
                        [
                            {"district_name": "Other", "value": 10.0, "highlighted": False},
                            {"district_name": "D1", "value": 7.5, "highlighted": True},
                        ],
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))

    assert summary.district_macro_indicators == 1
    assert summary.district_macro_points == 2
    with Session(engine) as s:
        ind = s.execute(select(DistrictMacroIndicator)).scalar_one()
        assert ind.indicator_key == "ind_a"
        assert ind.indicator_unit == "u"
        assert ind.indicator_direction == "up"
        assert ind.period_label_cyr == "Q1"
        # Highlighted picked from highlighted=true point only.
        assert ind.highlighted_value_num == 7.5
        assert ind.highlighted_missing_flag is False
        assert ind.highlighted_value_null_flag is False
        # Point order preserved from source.
        pts = (
            s.execute(select(DistrictMacroPoint).order_by(DistrictMacroPoint.point_order))
            .scalars()
            .all()
        )
        assert [p.point_order for p in pts] == [0, 1]
        assert [p.point_district_name_cyr for p in pts] == ["Other", "D1"]
        assert [p.point_value_num for p in pts] == [10.0, 7.5]
        assert [p.is_highlighted for p in pts] == [False, True]


def test_missing_highlighted_sets_flag_and_null_value(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district_with_macro(
                1100201,
                "D1",
                [
                    _indicator(
                        "ind_b",
                        [
                            {"district_name": "Other1", "value": 1.0, "highlighted": False},
                            {"district_name": "D1", "value": 99.0, "highlighted": False},
                        ],
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    with Session(engine) as s:
        ind = s.execute(select(DistrictMacroIndicator)).scalar_one()
        # No highlighted=true source point => never look up by district_name.
        assert ind.highlighted_value_num is None
        assert ind.highlighted_missing_flag is True
        assert ind.highlighted_value_null_flag is False
        # All source points still inserted regardless of missing highlighted.
        assert summary.district_macro_points == 2
        pts = s.execute(select(DistrictMacroPoint)).scalars().all()
        assert {p.point_district_name_cyr for p in pts} == {"Other1", "D1"}


def test_highlighted_point_with_null_value_sets_null_flag(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district_with_macro(
                1100201,
                "D1",
                [
                    _indicator(
                        "ind_c",
                        [
                            {"district_name": "D1", "value": None, "highlighted": True},
                            {"district_name": "Other", "value": 5.0, "highlighted": False},
                        ],
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        ind = s.execute(select(DistrictMacroIndicator)).scalar_one()
        assert ind.highlighted_value_num is None
        assert ind.highlighted_missing_flag is False
        assert ind.highlighted_value_null_flag is True


def test_highlighted_point_with_non_numeric_value_sets_null_flag(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district_with_macro(
                1100201,
                "D1",
                [
                    _indicator(
                        "ind_d",
                        [{"district_name": "D1", "value": "n/a", "highlighted": True}],
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        ind = s.execute(select(DistrictMacroIndicator)).scalar_one()
        assert ind.highlighted_value_num is None
        assert ind.highlighted_value_null_flag is True
        # Source non-numeric value persisted as NULL on point side too,
        # but the row itself still inserts (raw fidelity preserved by
        # point_district_name_cyr + is_highlighted).
        pt = s.execute(select(DistrictMacroPoint)).scalar_one()
        assert pt.point_value_num is None
        assert pt.is_highlighted is True


def test_district_name_in_macro_point_does_not_attach_data_to_district(
    tmp_path: Path,
) -> None:
    """Point with district_name='D2' inside D1's macro stays in D1's macro."""
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district_with_macro(
                1100201,
                "D1",
                [
                    _indicator(
                        "ind_e",
                        [{"district_name": "D2", "value": 10.0, "highlighted": True}],
                    )
                ],
            ),
            _district_with_macro(1100202, "D2", []),
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        d1 = s.execute(select(District).where(District.district_name_cyr == "D1")).scalar_one()
        d2 = s.execute(select(District).where(District.district_name_cyr == "D2")).scalar_one()
        # All macro indicators belong to D1 (parent by source nesting), not D2.
        inds = s.execute(select(DistrictMacroIndicator)).scalars().all()
        assert len(inds) == 1
        assert inds[0].district_id == d1.district_id
        # D2 has no macro indicators despite the point bearing its name.
        d2_inds = (
            s.execute(
                select(DistrictMacroIndicator).where(
                    DistrictMacroIndicator.district_id == d2.district_id
                )
            )
            .scalars()
            .all()
        )
        assert d2_inds == []
        # The point itself is preserved verbatim under D1's indicator.
        pts = s.execute(select(DistrictMacroPoint)).scalars().all()
        assert len(pts) == 1
        assert pts[0].point_district_name_cyr == "D2"
        assert pts[0].is_highlighted is True


def test_rating_histogram_source_order_preserved(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    histogram = [
        {"bucket": "Top 10%", "count": 3},
        {"bucket": "Mid", "count": 7},
        {"bucket": "Bottom", "count": 1},
    ]
    payload = _region_payload(
        1100,
        [_district_with_macro(1100201, "D1", [], rating_histogram=histogram)],
    )
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.district_rating_histogram_rows == 3
    with Session(engine) as s:
        rows = (
            s.execute(
                select(DistrictRatingHistogram).order_by(DistrictRatingHistogram.bucket_order)
            )
            .scalars()
            .all()
        )
        assert [r.bucket_order for r in rows] == [0, 1, 2]
        assert [r.rating_bucket_label_cyr for r in rows] == ["Top 10%", "Mid", "Bottom"]
        assert [r.mahalla_count for r in rows] == [3, 7, 1]


def test_duplicate_district_code_does_not_merge_macro(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(
            1100,
            [
                _district_with_macro(
                    9999999,
                    "X",
                    [
                        _indicator(
                            "ind_a", [{"district_name": "X", "value": 1.0, "highlighted": True}]
                        )
                    ],
                ),
            ],
        ),
    )
    _write(
        src,
        1200,
        _region_payload(
            1200,
            [
                _district_with_macro(
                    9999999,
                    "Y",
                    [
                        _indicator(
                            "ind_a", [{"district_name": "Y", "value": 2.0, "highlighted": True}]
                        )
                    ],
                ),
            ],
        ),
    )
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.districts == 2
    assert summary.district_macro_indicators == 2
    with Session(engine) as s:
        inds = s.execute(select(DistrictMacroIndicator)).scalars().all()
        # Distinct district_id parents despite shared district_code.
        assert len({i.district_id for i in inds}) == 2
        assert sorted(i.highlighted_value_num for i in inds) == [1.0, 2.0]


# ----- Phase 4C.0: mahalla summary columns -----


def _mahalla_with_detail(
    stir: str,
    name: str = "M",
    *,
    meta: list[dict] | None = None,
    residual: object = None,
    total_known: object = None,
    crop_sotikh: object = None,
) -> dict:
    overview: dict = {
        "header": {"title": name, "meta": meta if meta is not None else []},
        "kpis": [_kpi("population", 1000)],
        "detail": {
            "specialization": {
                "items": [],
                "residual_percent": residual,
                "total_known_percent": total_known,
            },
            "crops": {"seasons": [], "total_homestead_area_sotikh": crop_sotikh},
        },
    }
    return {"stir": stir, "name": name, "rating_score": 50.0, "overview": overview}


def test_status_label_cyr_copied_from_meta(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [
                    _mahalla_with_detail(
                        "100000001",
                        meta=[
                            {"label": "STIR", "value": "100000001"},
                            {"label": "Статус", "value": "Оғир маҳалла"},
                        ],
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.status_label_cyr == "Оғир маҳалла"


def test_status_label_cyr_null_when_meta_absent(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [
                    _mahalla_with_detail(
                        "100000001",
                        meta=[{"label": "STIR", "value": "100000001"}],
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        assert s.execute(select(Mahalla)).scalar_one().status_label_cyr is None


def test_specialization_and_crop_summary_copied_as_is(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [
                    _mahalla_with_detail(
                        "100000001",
                        residual=22.47,
                        total_known=77.53,
                        crop_sotikh=42.771229,
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.specialization_residual_percent == 22.47
        assert m.specialization_total_known_percent == 77.53
        assert m.crop_total_homestead_area_sotkah == 42.771229


def test_suspicious_total_known_over_100_stored_as_is(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [_mahalla_with_detail("100000001", residual=0.0, total_known=100.01)],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.specialization_total_known_percent == 100.01
        assert m.specialization_residual_percent == 0.0


# ----- Phase 4C: mahalla details -----


def _full_detail_mahalla() -> dict:
    return {
        "stir": "100000001",
        "name": "M",
        "rating_score": 50.0,
        "overview": {
            "header": {"title": "M", "meta": []},
            "kpis": [_kpi("population", 1000)],
            "appeals": {
                "crime": 2,
                "divorce": None,
                "aid": 5,
                "employment": 1,
                "gas": 0,
                "registry": None,
                "year": 2026,
                "period": "Q1",
            },
            "detail": {
                "infra": {
                    "road_km": 32170,  # suspicious extreme: kept as-is
                    "road_dirt_km": 0.0,
                    "road_asphalt_km": 32170,
                    "no_water": 0,
                    "power_cuts": 1,
                    "power_hrs": "2",  # text-only
                    "medical_km": 1.5,
                    "school": 2,
                    "sport": 1,
                    "kindergarten": 3,
                    "tomorqa_ha": 75917.0,
                },
                "specialization": {
                    "items": [
                        {
                            "slot": "main",
                            "slot_label": "Main",
                            "type": "T",
                            "direction": "D",
                            "icon": "X",
                            "households": 100,
                            "population": 500.5,
                            "percent": 25.0,
                        },
                        {
                            "slot": "add_2",
                            "slot_label": "A2",
                            "type": "T2",
                            "direction": "D2",
                            "icon": "Y",
                            "households": 50,
                            "population": 200,
                            "percent": 12.5,
                        },
                    ],
                    "residual_percent": 62.5,
                    "total_known_percent": 100.01,  # suspicious >100, kept
                },
                "crops": {
                    "seasons": [
                        {
                            "key": "main",
                            "label": "Main season",
                            "crops_text": None,
                            "crops": [{"name": "wheat"}],
                            "total_area_ha": None,
                            "homestead_area_ha": -0.0151,  # negative, kept
                            "household_count": 100,
                        },
                        {
                            "key": "repeat",
                            "label": "Repeat",
                            "crops_text": None,
                            "crops": [],
                            "total_area_ha": None,
                            "homestead_area_ha": 5.0,
                            "household_count": 50,
                        },
                    ],
                    "total_homestead_area_sotikh": 50.0,
                },
                "subsidies": {
                    "year": 2026,
                    "data_date": "2026-04-08",
                    "programs": [
                        {
                            "label": "P1",
                            "applications": None,
                            "required_amount_mln": None,
                            "has_amount_source": True,
                        },
                        {
                            "label": "P2",
                            "applications": 3,
                            "required_amount_mln": 4.5,
                            "has_amount_source": "yes",  # non-bool -> NULL
                        },
                    ],
                },
            },
            "peer_profile": {
                "strengths": [
                    {
                        "key": "fa",
                        "label": "FA",
                        "unit": "u",
                        "direction": "up",
                        "this_value": 1.0,
                        "district_avg": 0.5,
                        "peer_rank": 1,
                        "peer_count": 5,
                        "percentile": 95.0,
                    },
                    {
                        "key": "fb",
                        "label": "FB",
                        "unit": "u",
                        "direction": "up",
                        "this_value": 2.0,
                        "district_avg": 1.0,
                        "peer_rank": 2,
                        "peer_count": 5,
                        "percentile": 85.0,
                    },
                ],
                "weaknesses": [
                    {
                        "key": "fc",
                        "label": "FC",
                        "unit": "u",
                        "direction": "down",
                        "this_value": 9.0,
                        "district_avg": 5.0,
                        "peer_rank": 5,
                        "peer_count": 5,
                        "percentile": 10.0,
                    }
                ],
            },
        },
    }


def test_all_six_detail_groups_imported(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [_district(1100201, "D", [_full_detail_mahalla()])],
    )
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))

    assert summary.mahalla_infrastructure_rows == 1
    assert summary.mahalla_appeal_rows == 1
    assert summary.mahalla_specialization_rows == 2
    assert summary.mahalla_crop_rows == 2
    assert summary.mahalla_subsidy_program_rows == 2
    assert summary.mahalla_peer_factor_rows == 3

    with Session(engine) as s:
        infra = s.execute(select(MahallaInfrastructureRow)).scalar_one()
        # Suspicious values preserved as-is.
        assert infra.road_total_km == 32170
        assert infra.road_asphalt_km == 32170
        assert infra.homestead_area_ha == 75917.0
        # power_hrs is a string, not parsed.
        assert isinstance(infra.power_outage_hours_text, str)
        assert infra.power_outage_hours_text == "2"

        ap = s.execute(select(MahallaAppealRow)).scalar_one()
        assert ap.crime_appeal_count == 2
        assert ap.divorce_appeal_count is None  # null preserved
        assert ap.social_aid_appeal_count == 5
        assert ap.appeals_year == 2026
        assert ap.appeals_period_label_cyr == "Q1"

        # Specialization order preserved.
        spec = (
            s.execute(
                select(MahallaSpecializationItem).order_by(MahallaSpecializationItem.item_order)
            )
            .scalars()
            .all()
        )
        assert [x.item_order for x in spec] == [0, 1]
        assert [x.specialization_slot for x in spec] == ["main", "add_2"]
        assert spec[0].population_count == 500.5

        # Crops order preserved + raw_crops_json keeps source season verbatim.
        crops = (
            s.execute(select(MahallaCropSeason).order_by(MahallaCropSeason.season_order))
            .scalars()
            .all()
        )
        assert [c.season_order for c in crops] == [0, 1]
        assert crops[0].homestead_area_ha == -0.0151  # negative kept
        assert crops[0].total_area_ha is None
        assert crops[0].crops_text_cyr is None
        assert crops[0].raw_crops_json["crops"] == [{"name": "wheat"}]

        # Subsidies: parent year/data_date copied per row; non-bool flag -> NULL.
        progs = (
            s.execute(select(MahallaSubsidyProgram).order_by(MahallaSubsidyProgram.program_order))
            .scalars()
            .all()
        )
        assert [p.program_order for p in progs] == [0, 1]
        assert progs[0].subsidy_program_label_cyr == "P1"
        assert progs[0].application_count is None
        assert progs[0].required_amount_mln_uzs is None
        assert progs[0].has_amount_source_flag is True
        assert progs[1].has_amount_source_flag is None  # "yes" string -> NULL
        for p in progs:
            assert p.subsidies_year == 2026
            assert p.subsidies_data_date == "2026-04-08"

        # Peer factors: split by polarity, orders preserved per polarity.
        factors = (
            s.execute(
                select(MahallaPeerFactor).order_by(
                    MahallaPeerFactor.factor_polarity, MahallaPeerFactor.factor_order
                )
            )
            .scalars()
            .all()
        )
        strengths = [f for f in factors if f.factor_polarity == "strength"]
        weaknesses = [f for f in factors if f.factor_polarity == "weakness"]
        assert [f.factor_order for f in strengths] == [0, 1]
        assert [f.factor_order for f in weaknesses] == [0]
        assert strengths[0].factor_key == "fa"
        assert strengths[0].entity_value_num == 1.0
        assert strengths[0].comparison_average_value == 0.5
        assert strengths[0].percentile == 95.0
        assert weaknesses[0].peer_rank == 5
        assert weaknesses[0].peer_count == 5

        # Mahalla 4C.0 summary columns also populated by 4A flow.
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.specialization_total_known_percent == 100.01


def test_missing_detail_blocks_create_no_rows(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    bare = {
        "stir": "100000001",
        "name": "M",
        "rating_score": 50.0,
        "overview": {"header": {}, "kpis": []},
    }
    payload = _region_payload(1100, [_district(1100201, "D", [bare])])
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.mahalla_infrastructure_rows == 0
    assert summary.mahalla_appeal_rows == 0
    assert summary.mahalla_specialization_rows == 0
    assert summary.mahalla_crop_rows == 0
    assert summary.mahalla_subsidy_program_rows == 0
    assert summary.mahalla_peer_factor_rows == 0
    with Session(engine) as s:
        for model in (
            MahallaInfrastructureRow,
            MahallaAppealRow,
            MahallaSpecializationItem,
            MahallaCropSeason,
            MahallaSubsidyProgram,
            MahallaPeerFactor,
        ):
            assert s.execute(select(model)).scalars().all() == []


def test_duplicate_stir_does_not_merge_details(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    m1 = _full_detail_mahalla()
    m2 = _full_detail_mahalla()  # same STIR
    m2["overview"]["detail"]["infra"]["road_km"] = 5
    payload = _region_payload(1100, [_district(1100201, "D", [m1, m2])])
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.mahallas == 2
    # All detail counts double.
    assert summary.mahalla_infrastructure_rows == 2
    assert summary.mahalla_appeal_rows == 2
    assert summary.mahalla_specialization_rows == 4
    assert summary.mahalla_crop_rows == 4
    assert summary.mahalla_subsidy_program_rows == 4
    assert summary.mahalla_peer_factor_rows == 6
    with Session(engine) as s:
        infras = s.execute(select(MahallaInfrastructureRow)).scalars().all()
        assert len(infras) == 2
        assert {i.mahalla_id for i in infras} == {
            m.mahalla_id for m in s.execute(select(Mahalla)).scalars().all()
        }
        # Different source values survive on each row.
        assert sorted(i.road_total_km or 0 for i in infras) == [5.0, 32170.0]


# ----- Phase 4C.1: peer_profile metadata on mahallas -----


def _mahalla_with_peer_meta(stir: str, peer_profile: object) -> dict:
    return {
        "stir": stir,
        "name": "M",
        "rating_score": 50.0,
        "overview": {
            "header": {"title": "M", "meta": []},
            "kpis": [_kpi("population", 1000)],
            "peer_profile": peer_profile,
        },
    }


def test_peer_metadata_copied_as_is(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [
                    _mahalla_with_peer_meta(
                        "100000001",
                        {
                            "peer_set": {
                                "count": 11,
                                "description": "D tumani (11 mahallalar)",
                                "fallback_to_district": True,
                            },
                            "indicator_count": 25,
                            "total_indicators_considered": 31,
                            "strengths": [],
                            "weaknesses": [],
                        },
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.peer_set_count == 11
        assert m.peer_set_description_cyr == "D tumani (11 mahallalar)"
        assert m.peer_fallback_to_district_flag is True
        assert m.peer_indicator_count == 25
        assert m.peer_total_indicators_considered == 31


def test_missing_peer_profile_leaves_columns_null(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [_district(1100201, "D", [_mahalla_with_peer_meta("100000001", None)])],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.peer_set_count is None
        assert m.peer_set_description_cyr is None
        assert m.peer_fallback_to_district_flag is None
        assert m.peer_indicator_count is None
        assert m.peer_total_indicators_considered is None


def test_non_bool_fallback_to_district_becomes_null(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [
            _district(
                1100201,
                "D",
                [
                    _mahalla_with_peer_meta(
                        "100000001",
                        {
                            "peer_set": {
                                "count": 5,
                                "description": "x",
                                "fallback_to_district": "yes",  # non-bool
                            }
                        },
                    )
                ],
            )
        ],
    )
    _write(src, 1100, payload)
    engine = _engine()
    run_import(engine, _settings(src))
    with Session(engine) as s:
        m = s.execute(select(Mahalla)).scalar_one()
        assert m.peer_fallback_to_district_flag is None  # NOT False
        assert m.peer_set_count == 5


def test_duplicate_stir_does_not_merge_peer_metadata(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    m1 = _mahalla_with_peer_meta(
        "100000001",
        {"peer_set": {"count": 5, "description": "A", "fallback_to_district": True}},
    )
    m2 = _mahalla_with_peer_meta(
        "100000001",  # same STIR
        {"peer_set": {"count": 11, "description": "B", "fallback_to_district": False}},
    )
    payload = _region_payload(1100, [_district(1100201, "D", [m1, m2])])
    _write(src, 1100, payload)
    engine = _engine()
    summary = run_import(engine, _settings(src))
    assert summary.mahallas == 2
    with Session(engine) as s:
        rows = (
            s.execute(
                select(Mahalla)
                .where(Mahalla.mahalla_stir == "100000001")
                .order_by(Mahalla.source_mahalla_index)
            )
            .scalars()
            .all()
        )
        assert len(rows) == 2
        assert [r.peer_set_count for r in rows] == [5, 11]
        assert [r.peer_set_description_cyr for r in rows] == ["A", "B"]
        assert [r.peer_fallback_to_district_flag for r in rows] == [True, False]


def test_failed_import_marks_run_failed(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "cerr_runs"
    _write(src, 1100, _region_payload(1100, [_district(1100201, "D", [_mahalla("100000001")])]))
    engine = _engine()

    # Inject a failure inside _import_one_file.
    from cerr_chatbot.importer import runner as runner_mod

    def boom(*_args, **_kwargs):
        raise RuntimeError("simulated importer crash")

    monkeypatch.setattr(runner_mod, "_import_one_file", boom)
    with pytest.raises(RuntimeError):
        run_import(engine, _settings(src))

    with Session(engine) as s:
        runs = s.execute(select(ImportRun)).scalars().all()
        assert len(runs) == 1
        assert runs[0].status == "failed"
        assert runs[0].completed_at is None
        assert "RuntimeError" in (runs[0].notes or "")
