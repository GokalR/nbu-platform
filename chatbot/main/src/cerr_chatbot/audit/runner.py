"""Phase 2A audit orchestrator.

Loads each region JSON with stdlib `json`. Region files are small enough to
fit in RAM (see source discovery output for actual sizes), so we avoid the
extra `ijson` dependency for now. If 2B profiling needs streaming, switch
then.

Runs structural checks, collects mahalla STIRs and district codes for
global uniqueness, and emits a single AuditReport.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cerr_chatbot.audit.checks import (
    check_district_code_global_uniqueness,
    check_global_stir_uniqueness,
    check_region_code_uniqueness,
    check_region_file,
)
from cerr_chatbot.audit.models import (
    ActualCounts,
    AuditReport,
    ExpectedCounts,
    Issue,
)
from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.sources import RegionFile, discover_region_files


def run_audit(settings: Settings | None = None) -> AuditReport:
    cfg = settings or get_settings()
    files = discover_region_files(cfg)

    source_dir_abs = (
        cfg.cerr_source_dir
        if cfg.cerr_source_dir.is_absolute()
        else (Path.cwd() / cfg.cerr_source_dir).resolve()
    )

    report = AuditReport(
        run_at=datetime.now(UTC).isoformat(),
        source_dir=str(source_dir_abs),
        source_files=[f.path.name for f in files],
        expected=ExpectedCounts(),
        actual=ActualCounts(region_files=len(files)),
    )

    issues: list[Issue] = []
    sink = issues.append

    if len(files) != report.expected.region_files:
        sink(
            Issue(
                severity="critical",
                code="REGION_FILE_COUNT_MISMATCH",
                message=(
                    f"expected {report.expected.region_files} region files, found {len(files)}"
                ),
            )
        )

    region_code_pairs: list[tuple[int | None, str]] = []
    stir_records: list[tuple[str, int | None, int | None, str]] = []
    district_records: list[tuple[int, int | None, str | None, str]] = []

    for rf in files:
        payload = _load_json(rf, sink)
        if payload is None:
            continue
        counts = check_region_file(
            file_name=rf.path.name,
            expected_region_id_from_name=rf.region_id,
            payload=payload,
            sink=sink,
        )
        report.per_region.append(counts)
        region_code_pairs.append((counts.region_code, rf.path.name))
        _collect_districts(payload, rf.path.name, district_records)
        _collect_stirs(payload, rf.path.name, stir_records)

    check_region_code_uniqueness(region_code_pairs, sink)
    check_district_code_global_uniqueness(district_records, sink)
    check_global_stir_uniqueness(stir_records, sink)

    report.actual.regions = sum(1 for r in report.per_region if r.region_code is not None)
    report.actual.districts = sum(r.actual_districts for r in report.per_region)
    report.actual.mahallas = sum(r.actual_mahallas for r in report.per_region)

    if report.actual.regions > 0 and report.actual.districts != report.expected.districts:
        sink(
            Issue(
                severity="warning",
                code="TOTAL_DISTRICTS_MISMATCH_EXPECTED",
                message=(
                    f"total districts={report.actual.districts} differs from "
                    f"expected {report.expected.districts}"
                ),
            )
        )
    if report.actual.regions > 0 and report.actual.mahallas != report.expected.mahallas:
        sink(
            Issue(
                severity="warning",
                code="TOTAL_MAHALLAS_MISMATCH_EXPECTED",
                message=(
                    f"total mahallas={report.actual.mahallas} differs from "
                    f"expected {report.expected.mahallas}"
                ),
            )
        )

    report.issues = issues
    report.finalize()
    return report


def write_report(report: AuditReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out_path = out_dir / f"audit_{stamp}.json"
    out_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return out_path


def _load_json(rf: RegionFile, sink: Any) -> dict[str, Any] | None:
    try:
        with rf.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sink(
            Issue(
                severity="critical",
                code="REGION_FILE_UNREADABLE",
                message=f"failed to read/parse {rf.path.name}: {exc}",
                source_file=rf.path.name,
            )
        )
        return None
    if not isinstance(data, dict):
        sink(
            Issue(
                severity="critical",
                code="REGION_FILE_NOT_OBJECT",
                message=f"{rf.path.name} top-level is not a JSON object",
                source_file=rf.path.name,
            )
        )
        return None
    return data


def _collect_districts(
    payload: dict[str, Any],
    file_name: str,
    out: list[tuple[int, int | None, str | None, str]],
) -> None:
    region_code_raw = payload.get("region_code")
    region_code = region_code_raw if isinstance(region_code_raw, int) else None
    districts = payload.get("districts")
    if not isinstance(districts, list):
        return
    for d in districts:
        if not isinstance(d, dict):
            continue
        code_raw = d.get("code")
        if not isinstance(code_raw, int):
            continue
        name_raw = d.get("name")
        name = name_raw if isinstance(name_raw, str) else None
        out.append((code_raw, region_code, name, file_name))


def _collect_stirs(
    payload: dict[str, Any],
    file_name: str,
    out: list[tuple[str, int | None, int | None, str]],
) -> None:
    region_code_raw = payload.get("region_code")
    region_code = region_code_raw if isinstance(region_code_raw, int) else None
    districts = payload.get("districts")
    if not isinstance(districts, list):
        return
    for d in districts:
        if not isinstance(d, dict):
            continue
        district_code_raw = d.get("code")
        district_code = district_code_raw if isinstance(district_code_raw, int) else None
        mahallas = d.get("mahallas")
        if not isinstance(mahallas, list):
            continue
        for m in mahallas:
            if not isinstance(m, dict):
                continue
            stir = m.get("stir")
            if isinstance(stir, str) and stir:
                out.append((stir, region_code, district_code, file_name))
