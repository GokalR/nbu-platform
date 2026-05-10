"""Phase 5.1: catalog consistency + null-safe mismatch flag."""

from __future__ import annotations

import json
import re
from pathlib import Path

from sqlalchemy import create_engine, text

from cerr_chatbot.config import Settings
from cerr_chatbot.db import Base
from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS, VIEW_NAMES
from cerr_chatbot.importer import run_import
from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG


def _engine_with_views():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with e.begin() as conn:
        for stmt in CREATE_VIEW_STATEMENTS:
            conn.exec_driver_sql(stmt)
    return e


# ----- catalog consistency -----


def test_catalog_includes_all_views() -> None:
    assert set(SEMANTIC_CATALOG.keys()) == set(VIEW_NAMES)


def test_every_documented_view_exists_in_view_names() -> None:
    for name in SEMANTIC_CATALOG:
        assert name in VIEW_NAMES


def test_catalog_columns_exist_in_real_views() -> None:
    """Every column the catalog promises must actually be selectable from the view."""
    engine = _engine_with_views()
    missing: list[tuple[str, str]] = []
    with engine.connect() as conn:
        for view_name, view in SEMANTIC_CATALOG.items():
            actual_cols = {row[1] for row in conn.execute(text(f"PRAGMA table_info({view_name})"))}
            for col in view.columns:
                if col.name not in actual_cols:
                    missing.append((view_name, col.name))
    assert not missing, f"catalog references missing columns: {missing}"


def test_catalog_examples_are_sqlite_executable() -> None:
    """Run every catalog example against an empty schema so syntax errors fail fast."""
    engine = _engine_with_views()
    with engine.connect() as conn:
        for view in SEMANTIC_CATALOG.values():
            for example in view.examples:
                conn.execute(text(example))  # raises on bad SQL


# ----- null-safe mismatch flag -----


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


def _district(code: int, name: str, mahallas: list[dict]) -> dict:
    return {
        "code": code,
        "name": name,
        "mahalla_count": len(mahallas),
        "overview": {"header": {"title": name}, "kpis": [_kpi("population", 50000)]},
        "macro": {"period": "Q1", "indicators": []},
        "mahallas": mahallas,
    }


def _mahalla(stir: str) -> dict:
    return {
        "stir": stir,
        "name": "M",
        "rating_score": 50.0,
        "overview": {"header": {"title": "M", "meta": []}, "kpis": [_kpi("population", 1000)]},
    }


def _region_payload(code: int, districts: list[dict], declared_mahallas: int | None) -> dict:
    payload = {
        "region_code": code,
        "region_name": f"R{code}",
        "districts_count": len(districts),
        "region_mahalla_count": declared_mahallas,
        "region_overview": {"header": {"title": f"R{code}"}, "kpis": [_kpi("population", 100000)]},
        "districts": districts,
    }
    if declared_mahallas is None:
        payload.pop("region_mahalla_count")
    return payload


def _write(src: Path, code: int, payload: dict) -> Path:
    src.mkdir(exist_ok=True)
    p = src / f"cerr_region_{code}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _settings(src: Path) -> Settings:
    return Settings(cerr_source_dir=src)


def test_mismatch_flag_returns_null_when_declared_unknown(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [_district(1100201, "D", [_mahalla("100000001")])],
        declared_mahallas=None,
    )
    _write(src, 1100, payload)
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        flag = conn.execute(text("SELECT mahalla_count_mismatch_flag FROM v_regions")).scalar_one()
        assert flag is None  # NULL, not 0


def test_mismatch_flag_returns_null_when_actual_unknown(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    # Drop districts entirely so actual_*_count = NULL.
    payload = {
        "region_code": 1100,
        "region_name": "R1100",
        "region_mahalla_count": 5,
        "region_overview": {"header": {}, "kpis": []},
    }
    (src / "cerr_region_1100.json").write_text(json.dumps(payload), encoding="utf-8")
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        flag = conn.execute(text("SELECT mahalla_count_mismatch_flag FROM v_regions")).scalar_one()
        assert flag is None


def test_mismatch_flag_returns_one_when_counts_differ(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [_district(1100201, "D", [_mahalla("100000001")])],
        declared_mahallas=999,
    )
    _write(src, 1100, payload)
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        flag = conn.execute(text("SELECT mahalla_count_mismatch_flag FROM v_regions")).scalar_one()
        assert flag == 1


def test_mismatch_flag_returns_zero_when_counts_match(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    payload = _region_payload(
        1100,
        [_district(1100201, "D", [_mahalla("100000001")])],
        declared_mahallas=1,
    )
    _write(src, 1100, payload)
    engine = _engine_with_views()
    run_import(engine, _settings(src))
    with engine.connect() as conn:
        flag = conn.execute(text("SELECT mahalla_count_mismatch_flag FROM v_regions")).scalar_one()
        assert flag == 0


# ----- docs sanity -----


def test_semantic_views_doc_lists_every_view() -> None:
    text_doc = Path("docs/SEMANTIC_VIEWS.md").read_text(encoding="utf-8")
    for name in VIEW_NAMES:
        assert re.search(rf"^##\s+{re.escape(name)}\b", text_doc, re.MULTILINE), name


# Common mojibake fragments produced when UTF-8 Cyrillic is decoded as cp1251
# or similar. Hand-written catalog/docs must never contain these.
_MOJIBAKE_FRAGMENTS: tuple[str, ...] = (
    "РЎ",
    "РјР",
    "СЃС",
    "Р°С",
    "вЂ",
    "РІР",
    "РЅР",
    "РєР",
    "РѕР",
    "РіР",
)


def _has_mojibake(text: str) -> list[str]:
    return [m for m in _MOJIBAKE_FRAGMENTS if m in text]


def test_no_mojibake_in_semantic_catalog_module() -> None:
    text = Path("src/cerr_chatbot/query/semantic_catalog.py").read_text(encoding="utf-8")
    hits = _has_mojibake(text)
    assert not hits, f"mojibake fragments in semantic_catalog.py: {hits}"


def test_no_mojibake_in_semantic_views_doc() -> None:
    text = Path("docs/SEMANTIC_VIEWS.md").read_text(encoding="utf-8")
    hits = _has_mojibake(text)
    assert not hits, f"mojibake fragments in SEMANTIC_VIEWS.md: {hits}"


def test_no_mojibake_in_catalog_descriptions() -> None:
    """Per-column descriptions consumed by the LLM must be mojibake-free."""
    bad: list[tuple[str, str, list[str]]] = []
    for view_name, view in SEMANTIC_CATALOG.items():
        for col in view.columns:
            hits = _has_mojibake(col.description)
            if hits:
                bad.append((view_name, col.name, hits))
        for example in view.examples:
            hits = _has_mojibake(example)
            if hits:
                bad.append((view_name, "<example>", hits))
        for warn in view.warnings:
            hits = _has_mojibake(warn)
            if hits:
                bad.append((view_name, "<warning>", hits))
    assert not bad, f"mojibake in catalog content: {bad[:5]}"
