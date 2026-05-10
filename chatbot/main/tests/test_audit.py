"""Tests for Phase 2A audit.

Synthetic minimal fixtures only — no dependency on the real ./cerr_runs/.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cerr_chatbot.audit import run_audit
from cerr_chatbot.audit.runner import write_report
from cerr_chatbot.config import Settings


def _mahalla(stir: str, name: str = "M") -> dict:
    return {"stir": stir, "name": name, "rating_score": 1.0}


def _district(code: int, mahallas: list[dict]) -> dict:
    return {
        "code": code,
        "name": f"D{code}",
        "mahalla_count": len(mahallas),
        "mahallas": mahallas,
    }


def _region(region_code: int, districts: list[dict], **overrides) -> dict:
    payload = {
        "region_code": region_code,
        "region_name": f"R{region_code}",
        "districts_count": len(districts),
        "region_mahalla_count": sum(d["mahalla_count"] for d in districts),
        "districts": districts,
    }
    payload.update(overrides)
    return payload


def _write_region(dir_: Path, region_code: int, payload: dict) -> Path:
    p = dir_ / f"cerr_region_{region_code}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _settings(source_dir: Path) -> Settings:
    return Settings(cerr_source_dir=source_dir)


def _codes(report) -> list[str]:
    return [i.code for i in report.issues]


@pytest.fixture
def clean_two_regions(tmp_path: Path) -> Path:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    _write_region(
        src,
        1100,
        _region(1100, [_district(1100201, [_mahalla("100000001"), _mahalla("100000002")])]),
    )
    _write_region(
        src,
        1200,
        _region(1200, [_district(1200201, [_mahalla("200000001")])]),
    )
    return src


def test_clean_minimal_source_has_no_critical(clean_two_regions: Path) -> None:
    # Only critical-severity matters for exit code; warning about expected
    # corpus totals (14/212/9088) is acceptable on a synthetic fixture.
    report = run_audit(_settings(clean_two_regions))
    crit = [i for i in report.issues if i.severity == "critical"]
    # Two-region fixture triggers REGION_FILE_COUNT_MISMATCH; allow that one.
    assert all(i.code == "REGION_FILE_COUNT_MISMATCH" for i in crit), [
        (i.code, i.message) for i in crit
    ]
    assert report.actual.regions == 2
    assert report.actual.districts == 2
    assert report.actual.mahallas == 3


def test_duplicate_region_code_detected(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    # Both files declare the same region_code — but filenames differ.
    _write_region(src, 1100, _region(1100, [_district(1100201, [_mahalla("100000001")])]))
    p2 = src / "cerr_region_1200.json"
    p2.write_text(
        json.dumps(_region(1100, [_district(1100202, [_mahalla("100000002")])])),
        encoding="utf-8",
    )
    report = run_audit(_settings(src))
    codes = _codes(report)
    assert "REGION_CODE_DUPLICATE" in codes
    assert "REGION_CODE_FILENAME_MISMATCH" in codes


def test_district_code_prefix_mismatch_detected(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    _write_region(
        src,
        1100,
        _region(1100, [_district(9999999, [_mahalla("100000001")])]),
    )
    report = run_audit(_settings(src))
    assert "DISTRICT_CODE_PREFIX_MISMATCH" in _codes(report)


def test_region_mahalla_count_mismatch_detected(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _region(1100, [_district(1100201, [_mahalla("100000001")])])
    payload["region_mahalla_count"] = 999  # lie
    _write_region(src, 1100, payload)
    report = run_audit(_settings(src))
    assert "REGION_MAHALLA_COUNT_MISMATCH" in _codes(report)


def test_district_mahalla_count_mismatch_detected(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    d = _district(1100201, [_mahalla("100000001")])
    d["mahalla_count"] = 42
    payload = _region(1100, [d])
    payload["region_mahalla_count"] = 1  # keep region-level honest
    _write_region(src, 1100, payload)
    report = run_audit(_settings(src))
    assert "DISTRICT_MAHALLA_COUNT_MISMATCH" in _codes(report)


def test_duplicate_district_code_across_regions(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    # Same district_code (1100201) appears in two different region files.
    # Prefix matches one region only; the other will also flag prefix mismatch.
    _write_region(src, 1100, _region(1100, [_district(1100201, [_mahalla("100000001")])]))
    _write_region(src, 1200, _region(1200, [_district(1100201, [_mahalla("100000002")])]))
    report = run_audit(_settings(src))
    dup = [i for i in report.issues if i.code == "DISTRICT_CODE_DUPLICATE_GLOBAL"]
    assert len(dup) == 1
    assert dup[0].district_code == 1100201
    assert "cerr_region_1100.json" in dup[0].message
    assert "cerr_region_1200.json" in dup[0].message


def test_duplicate_district_code_within_region_caught_by_global(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    payload = _region(
        1100,
        [
            _district(1100201, [_mahalla("100000001")]),
            _district(1100201, [_mahalla("100000002")]),
        ],
    )
    _write_region(src, 1100, payload)
    report = run_audit(_settings(src))
    dup = [i for i in report.issues if i.code == "DISTRICT_CODE_DUPLICATE_GLOBAL"]
    assert len(dup) == 1
    assert dup[0].district_code == 1100201
    # The old per-region code must no longer fire (no double-counting).
    assert not [i for i in report.issues if i.code == "DISTRICT_CODE_DUPLICATE"]


def test_duplicate_stir_detected(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    _write_region(
        src,
        1100,
        _region(1100, [_district(1100201, [_mahalla("100000001"), _mahalla("100000001")])]),
    )
    report = run_audit(_settings(src))
    dups = [i for i in report.issues if i.code == "MAHALLA_STIR_DUPLICATE"]
    assert len(dups) == 1
    assert dups[0].stir == "100000001"


def test_stir_format_warning(tmp_path: Path) -> None:
    src = tmp_path / "cerr_runs"
    src.mkdir()
    _write_region(
        src,
        1100,
        _region(1100, [_district(1100201, [_mahalla("ABC123")])]),
    )
    report = run_audit(_settings(src))
    fmt = [i for i in report.issues if i.code == "MAHALLA_STIR_FORMAT"]
    assert len(fmt) == 1
    assert fmt[0].severity == "warning"


def test_report_writes_json_file(clean_two_regions: Path, tmp_path: Path) -> None:
    report = run_audit(_settings(clean_two_regions))
    out = write_report(report, tmp_path / "audit_reports")
    assert out.exists()
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["actual"]["regions"] == 2
    assert "issue_counts" in parsed
    assert "per_region" in parsed
