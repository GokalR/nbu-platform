"""Tests for Phase 5 semantic views. Sqlite engine + synthetic fixtures only."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base, ImportRun
from cerr_chatbot.db.views import (
    CREATE_VIEW_STATEMENTS,
    DROP_VIEW_STATEMENTS,
    VIEW_NAMES,
)
from cerr_chatbot.importer import run_import


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


def _kpi(key: str, value: object = 1) -> dict:
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
        "change_pct": None,
        "district_avg": None,
        "compare_scope": None,
    }


def _kpi_set(values: dict[str, float]) -> list[dict]:
    return [_kpi(k, v) for k, v in values.items()]


def _mahalla(stir: str, name: str = "M", **kpi_overrides: float) -> dict:
    base = {
        "population": 1000,
        "active_businesses": 10,
        "unemployed": 20,
        "rating_score": 50.0,
        "problem_loans": 1,
        "poor_families": 5,
    }
    base.update(kpi_overrides)
    return {
        "stir": stir,
        "name": name,
        "rating_score": base["rating_score"],
        "overview": {
            "header": {"title": name, "meta": []},
            "kpis": _kpi_set(base),
            "appeals": {
                "crime": 3,
                "divorce": None,
                "aid": 1,
                "employment": None,
                "gas": 2,
                "registry": None,
                "year": 2026,
                "period": "Q1",
            },
            "detail": {
                "infra": {
                    "road_km": 5.0,
                    "road_dirt_km": 1.0,
                    "road_asphalt_km": 4.0,
                    "no_water": 0,
                    "power_cuts": 0,
                    "power_hrs": "0",
                    "medical_km": 1.5,
                    "school": 2,
                    "sport": 1,
                    "kindergarten": 1,
                    "tomorqa_ha": 10.0,
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
                            "population": 500,
                            "percent": 25.0,
                        }
                    ],
                    "residual_percent": 75.0,
                    "total_known_percent": 25.0,
                },
                "crops": {
                    "seasons": [
                        {
                            "key": "main",
                            "label": "Main",
                            "crops_text": None,
                            "crops": [],
                            "total_area_ha": 2.0,
                            "homestead_area_ha": 1.0,
                            "household_count": 100,
                        }
                    ],
                    "total_homestead_area_sotikh": 100.0,
                },
                "subsidies": {
                    "year": 2026,
                    "data_date": "2026-04-01",
                    "programs": [
                        {
                            "label": "P1",
                            "applications": 1,
                            "required_amount_mln": 1.0,
                            "has_amount_source": True,
                        }
                    ],
                },
            },
            "peer_profile": {
                "peer_set": {"count": 5, "description": "x", "fallback_to_district": True},
                "indicator_count": 10,
                "total_indicators_considered": 12,
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
                        "percentile": 90.0,
                    }
                ],
                "weaknesses": [],
            },
        },
    }


def _district(code: int, name: str, mahallas: list[dict], **kpi_overrides: float) -> dict:
    base = {
        "population": 50000,
        "active_businesses": 500,
        "unemployed": 1000,
        "rating_score": 60.0,
        "problem_loans": 50,
        "poor_families": 200,
    }
    base.update(kpi_overrides)
    return {
        "code": code,
        "name": name,
        "mahalla_count": len(mahallas),
        "overview": {
            "header": {"title": name},
            "kpis": _kpi_set(base),
        },
        "macro": {
            "period": "Q1",
            "indicators": [
                {
                    "key": "ind_a",
                    "label": "A",
                    "unit": "u",
                    "direction": "up",
                    "points": [
                        {"district_name": name, "value": 7.0, "highlighted": True},
                        {"district_name": "Other", "value": 9.0, "highlighted": False},
                    ],
                },
                {
                    "key": "ind_b_missing_highlighted",
                    "label": "B",
                    "unit": "u",
                    "direction": "up",
                    "points": [
                        {"district_name": "Other", "value": 1.0, "highlighted": False},
                    ],
                },
            ],
        },
        "mahallas": mahallas,
    }


def _region_payload(region_code: int, districts: list[dict], **kpi_overrides: float) -> dict:
    base = {
        "population": 100000,
        "active_businesses": 1000,
        "unemployed": 2000,
        "rating_score": 70.0,
        "problem_loans": 100,
        "poor_families": 400,
    }
    base.update(kpi_overrides)
    return {
        "region_code": region_code,
        "region_name": f"R{region_code}",
        "generated_at": "2026-05-01T00:00:00",
        "districts_count": len(districts),
        "region_mahalla_count": sum(d["mahalla_count"] for d in districts),
        "region_overview": {
            "header": {"title": f"R{region_code}"},
            "kpis": _kpi_set(base),
        },
        "districts": districts,
    }


def _write(src: Path, region_code: int, payload: dict) -> Path:
    src.mkdir(exist_ok=True)
    p = src / f"cerr_region_{region_code}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _settings(src: Path) -> Settings:
    return Settings(cerr_source_dir=src)


def _count(engine, view: str) -> int:
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar_one()


def test_all_views_exist_after_upgrade() -> None:
    engine = _engine_with_views()
    insp = inspect(engine)
    found = set(insp.get_view_names())
    assert set(VIEW_NAMES).issubset(found), set(VIEW_NAMES) - found


def test_views_filter_to_latest_completed_run(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(1100, [_district(1100201, "D1", [_mahalla("100000001")])])
    _write(src, 1100, payload)
    engine = _engine_with_views()
    # Inject one OLDER completed run + one FAILED run that views must ignore.
    with Session(engine) as s:
        s.add_all(
            [
                ImportRun(
                    started_at=datetime.now(UTC),
                    completed_at=datetime.now(UTC),
                    source_dir="ignored_old",
                    source_file_count=0,
                    status="completed",
                ),
                ImportRun(
                    started_at=datetime.now(UTC),
                    source_dir="ignored_failed",
                    source_file_count=0,
                    status="failed",
                ),
            ]
        )
        s.commit()
    # Now run the real importer (creates the latest completed run).
    run_import(engine, _settings(src))

    # Each view should reflect ONLY the latest completed run.
    assert _count(engine, "v_latest_import_run") == 1
    assert _count(engine, "v_regions") == 1
    assert _count(engine, "v_districts") == 1
    assert _count(engine, "v_mahallas") == 1
    with engine.connect() as conn:
        row = conn.execute(text("SELECT source_dir FROM v_latest_import_run")).scalar_one()
        assert row != "ignored_old"
        assert row != "ignored_failed"


def test_kpi_pivot_at_each_level(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [_district(1100201, "D1", [_mahalla("100000001", population=2222)])],
        population=99999,
    )
    _write(src, 1100, payload)
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        r = conn.execute(text("SELECT population FROM v_regions")).scalar_one()
        d = conn.execute(text("SELECT population FROM v_districts")).scalar_one()
        m = conn.execute(text("SELECT population FROM v_mahallas")).scalar_one()
        assert r == 99999
        assert d == 50000
        assert m == 2222


def test_mahalla_rating_score_uses_kpi_not_raw_position(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    mahalla = _mahalla("100000001", rating_score=88.0)
    mahalla["rating_score"] = 777.0  # top-level raw source position/rank-like value
    payload = _region_payload(1100, [_district(1100201, "D1", [mahalla])])
    _write(src, 1100, payload)
    engine = _engine_with_views()
    run_import(engine, _settings(src))

    with engine.connect() as conn:
        row = conn.execute(text("SELECT rating_score, rating_position FROM v_mahallas")).one()
    assert row.rating_score == 88.0
    assert row.rating_position == 777.0


def test_duplicate_natural_keys_do_not_collapse_in_views(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    # Same district code + same mahalla STIR appear twice (one in each region).
    _write(
        src,
        1100,
        _region_payload(
            1100,
            [_district(9999999, "X", [_mahalla("100000001", "Same")])],
        ),
    )
    _write(
        src,
        1200,
        _region_payload(
            1200,
            [_district(9999999, "Y", [_mahalla("100000001", "Same")])],
        ),
    )
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    assert _count(engine, "v_districts") == 2
    assert _count(engine, "v_mahallas") == 2


def test_macro_highlights_view_keeps_missing_highlighted_rows(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(1100, [_district(1100201, "D1", [_mahalla("100000001")])]),
    )
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT indicator_key, highlighted_value_num, highlighted_missing_flag "
                "FROM v_district_macro_highlights ORDER BY indicator_key"
            )
        ).all()
    by_key = {r[0]: r for r in rows}
    assert "ind_b_missing_highlighted" in by_key
    # Missing-highlighted indicator survives, value NULL, flag truthy.
    assert by_key["ind_b_missing_highlighted"][1] is None
    assert by_key["ind_b_missing_highlighted"][2]
    # Real-highlighted indicator carries the value.
    assert by_key["ind_a"][1] == 7.0


def test_detail_views_preserve_order_columns(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(1100, [_district(1100201, "D1", [_mahalla("100000001")])]),
    )
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        for view, col in (
            ("v_mahalla_specializations", "item_order"),
            ("v_mahalla_crops", "season_order"),
            ("v_mahalla_subsidy_programs", "program_order"),
            ("v_mahalla_peer_factors", "factor_order"),
        ):
            cols = [row[1] for row in conn.execute(text(f"PRAGMA table_info({view})")).all()]
            assert col in cols, f"{view} missing {col}"


def test_no_raw_table_row_counts_change_after_views(tmp_path: Path) -> None:
    """Creating views must not insert/delete data."""
    src = tmp_path / "cerr_runs"
    _write(
        src,
        1100,
        _region_payload(1100, [_district(1100201, "D1", [_mahalla("100000001")])]),
    )
    engine_no_views = create_engine("sqlite://")
    Base.metadata.create_all(engine_no_views)
    run_import(engine_no_views, _settings(src))
    with engine_no_views.connect() as conn:
        before = {
            t: conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar_one()
            for t in ("regions", "districts", "mahallas", "entity_kpis")
        }

    engine_with_views = _engine_with_views()
    run_import(engine_with_views, _settings(src))
    with engine_with_views.connect() as conn:
        after = {
            t: conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar_one()
            for t in ("regions", "districts", "mahallas", "entity_kpis")
        }
    assert before == after


def test_drop_statements_round_trip() -> None:
    engine = _engine_with_views()
    with engine.begin() as conn:
        for stmt in DROP_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    insp = inspect(engine)
    assert not (set(VIEW_NAMES) & set(insp.get_view_names()))
