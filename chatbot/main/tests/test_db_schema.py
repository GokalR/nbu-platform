"""Metadata + Alembic baseline checks. No real DB needed; sqlite is enough."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from cerr_chatbot.db import Base

REQUIRED_TABLES = frozenset(
    {
        "import_runs",
        "source_region_files",
        "data_quality_issues",
        "regions",
        "districts",
        "mahallas",
        "entity_kpis",
        "district_macro_indicators",
        "district_macro_points",
        "district_rating_histogram",
        "mahalla_infrastructure",
        "mahalla_appeals",
        "mahalla_specializations",
        "mahalla_crops",
        "mahalla_subsidy_programs",
        "mahalla_peer_factors",
        "entity_ai_insights",
        "region_geometries",
        "district_geometries",
    }
)


@pytest.fixture(scope="module")
def in_memory_db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine


def test_all_required_tables_present(in_memory_db) -> None:
    found = set(Base.metadata.tables)
    missing = REQUIRED_TABLES - found
    assert not missing, missing


def test_every_table_has_single_column_surrogate_pk(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    for table_name in REQUIRED_TABLES:
        pk = insp.get_pk_constraint(table_name)
        cols = pk["constrained_columns"]
        assert len(cols) == 1, f"{table_name} PK is not single column: {cols}"
        # PK column ends with `_id` (surrogate convention).
        assert cols[0].endswith("_id"), f"{table_name} PK is not surrogate: {cols}"


def test_no_unique_on_district_code(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    for uq in insp.get_unique_constraints("districts"):
        assert uq["column_names"] != ["district_code"], (
            "district_code must NOT be unique - source has 3 duplicate groups"
        )


def test_no_unique_on_mahalla_stir(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    for uq in insp.get_unique_constraints("mahallas"):
        assert uq["column_names"] != ["mahalla_stir"], (
            "mahalla_stir must NOT be unique - source has 127 duplicate groups"
        )
        # Composite (region_code, district_code, stir) also not unique.
        assert uq["column_names"] != ["region_code", "district_code", "mahalla_stir"]


def _has_unique(in_memory_db, table: str, expected_cols: list[str]) -> bool:
    insp = inspect(in_memory_db)
    return any(uq["column_names"] == expected_cols for uq in insp.get_unique_constraints(table))


def test_lineage_uniqueness_for_districts(in_memory_db) -> None:
    assert _has_unique(
        in_memory_db,
        "districts",
        ["import_run_id", "source_file", "source_district_index"],
    )


def test_lineage_uniqueness_for_mahallas(in_memory_db) -> None:
    assert _has_unique(
        in_memory_db,
        "mahallas",
        [
            "import_run_id",
            "source_file",
            "source_district_index",
            "source_mahalla_index",
        ],
    )


def test_lineage_uniqueness_for_source_region_files(in_memory_db) -> None:
    assert _has_unique(in_memory_db, "source_region_files", ["import_run_id", "source_file"])


def test_data_quality_issues_table_columns(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    cols = {c["name"] for c in insp.get_columns("data_quality_issues")}
    required = {
        "issue_id",
        "import_run_id",
        "severity",
        "issue_code",
        "message",
        "source_file",
        "region_code",
        "district_code",
        "mahalla_stir",
        "source_json_path",
        "details_json",
    }
    assert required.issubset(cols), required - cols


def test_entity_kpis_supports_all_three_levels(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    cols = {c["name"] for c in insp.get_columns("entity_kpis")}
    # Three nullable level FKs - importer fills exactly one per row.
    assert {"region_id", "district_id", "mahalla_id"}.issubset(cols)
    # entity_level discriminator column exists.
    assert "entity_level" in cols


def test_alembic_baseline_migration_present_and_loadable() -> None:
    versions = Path("alembic/versions")
    files = sorted(p for p in versions.glob("*.py") if p.name != "__init__.py")
    assert files, "no alembic migration found in alembic/versions/"
    # Each file declares a revision and an upgrade() function.
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert "revision: str" in text or "revision =" in text
        assert "def upgrade()" in text
        assert "def downgrade()" in text


def test_alembic_baseline_runs_on_sqlite(tmp_path: Path) -> None:
    """Run the real migration end-to-end: upgrade head + downgrade base."""
    from alembic import command
    from alembic.config import Config

    db = tmp_path / "scratch.db"
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db}")
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")


# ---------- Phase 3 hardening checks ----------

TABLES_WITH_IMPORT_RUN_ID = (
    "source_region_files",
    "regions",
    "districts",
    "mahallas",
    "entity_kpis",
    "district_macro_indicators",
    "district_macro_points",
    "district_rating_histogram",
    "mahalla_infrastructure",
    "mahalla_appeals",
    "mahalla_specializations",
    "mahalla_crops",
    "mahalla_subsidy_programs",
    "mahalla_peer_factors",
    "entity_ai_insights",
    "region_geometries",
    "district_geometries",
    "data_quality_issues",
)


def _has_index_on(in_memory_db, table: str, col: str) -> bool:
    insp = inspect(in_memory_db)
    return any(ix["column_names"] == [col] for ix in insp.get_indexes(table))


def _has_index_starting_with(in_memory_db, table: str, col: str) -> bool:
    insp = inspect(in_memory_db)
    for ix in insp.get_indexes(table):
        if ix["column_names"] and ix["column_names"][0] == col:
            return True
    for uq in insp.get_unique_constraints(table):
        if uq["column_names"] and uq["column_names"][0] == col:
            return True
    return False


def test_district_macro_points_has_import_run_id_column_fk_index(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    cols = {c["name"] for c in insp.get_columns("district_macro_points")}
    assert "import_run_id" in cols
    fks = insp.get_foreign_keys("district_macro_points")
    assert any(
        fk["referred_table"] == "import_runs" and fk["constrained_columns"] == ["import_run_id"]
        for fk in fks
    ), "district_macro_points needs FK on import_run_id -> import_runs"
    assert _has_index_on(in_memory_db, "district_macro_points", "import_run_id")


def test_every_import_run_id_table_has_an_index(in_memory_db) -> None:
    missing: list[str] = []
    for table in TABLES_WITH_IMPORT_RUN_ID:
        if not _has_index_starting_with(in_memory_db, table, "import_run_id"):
            missing.append(table)
    assert not missing, f"tables missing import_run_id index: {missing}"


def test_entity_ai_insights_has_all_fk_indexes(in_memory_db) -> None:
    for col in ("mahalla_id", "district_id", "region_id", "import_run_id"):
        assert _has_index_on(in_memory_db, "entity_ai_insights", col), col


def test_natural_keys_still_not_unique(in_memory_db) -> None:
    insp = inspect(in_memory_db)
    forbidden = (
        ("regions", ["region_code"]),
        ("districts", ["district_code"]),
        ("mahallas", ["mahalla_stir"]),
        ("mahallas", ["region_code", "district_code", "mahalla_stir"]),
    )
    for table, cols in forbidden:
        for uq in insp.get_unique_constraints(table):
            assert uq["column_names"] != cols, f"{table} must not have UNIQUE on {cols}"
