"""Tests for source discovery. Use a tmp dir; never touch real cerr_runs/."""

from __future__ import annotations

from pathlib import Path

import pytest

from cerr_chatbot.config import Settings
from cerr_chatbot.sources import discover_region_files


def _make_settings(source_dir: Path) -> Settings:
    return Settings(cerr_source_dir=source_dir)


def test_discover_returns_sorted_region_files(tmp_path: Path) -> None:
    (tmp_path / "cerr_region_1730.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cerr_region_1703.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cerr_region_1718.json").write_text("{}", encoding="utf-8")
    (tmp_path / "README.md").write_text("ignore me", encoding="utf-8")
    (tmp_path / "cerr_region_bad.json").write_text("{}", encoding="utf-8")

    files = discover_region_files(_make_settings(tmp_path))

    assert [f.region_id for f in files] == [1703, 1718, 1730]
    assert all(f.size_bytes == 2 for f in files)


def test_discover_empty_dir_returns_empty_list(tmp_path: Path) -> None:
    assert discover_region_files(_make_settings(tmp_path)) == []


def test_discover_missing_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        discover_region_files(_make_settings(tmp_path / "does_not_exist"))
