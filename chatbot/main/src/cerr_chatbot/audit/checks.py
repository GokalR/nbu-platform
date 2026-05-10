"""Pure check functions for Phase 2A.

Each check takes already-parsed data and a sink callback that records issues.
No I/O, no logging - easy to unit-test.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any

from cerr_chatbot.audit.models import Issue, RegionCounts

IssueSink = Callable[[Issue], None]

STIR_RE = re.compile(r"^\d{9}$")


def check_region_file(
    *,
    file_name: str,
    expected_region_id_from_name: int,
    payload: dict[str, Any],
    sink: IssueSink,
) -> RegionCounts:
    """Run all per-region checks and return the per-region counts row.

    Mahalla STIR uniqueness across regions is handled by the runner
    (it needs the full corpus); this function only handles intra-region work.
    """
    region_code_raw = payload.get("region_code")
    region_code = region_code_raw if isinstance(region_code_raw, int) else None

    counts = RegionCounts(
        region_code=region_code,
        source_file=file_name,
        declared_districts=_int_or_none(payload.get("districts_count")),
        declared_mahallas=_int_or_none(payload.get("region_mahalla_count")),
    )

    if region_code is None:
        sink(
            Issue(
                severity="critical",
                code="REGION_CODE_MISSING",
                message=f"region_code missing or non-integer in {file_name}",
                source_file=file_name,
            )
        )
    elif region_code != expected_region_id_from_name:
        sink(
            Issue(
                severity="critical",
                code="REGION_CODE_FILENAME_MISMATCH",
                message=(
                    f"region_code={region_code} does not match filename "
                    f"id={expected_region_id_from_name}"
                ),
                region_code=region_code,
                source_file=file_name,
            )
        )

    districts = payload.get("districts")
    if not isinstance(districts, list):
        sink(
            Issue(
                severity="critical",
                code="DISTRICTS_FIELD_MISSING",
                message="districts field missing or not a list",
                region_code=region_code,
                source_file=file_name,
            )
        )
        districts = []

    counts.actual_districts = len(districts)

    if (
        counts.declared_districts is not None
        and counts.declared_districts != counts.actual_districts
    ):
        sink(
            Issue(
                severity="critical",
                code="DISTRICTS_COUNT_MISMATCH",
                message=(
                    f"districts_count={counts.declared_districts} but actual "
                    f"districts={counts.actual_districts}"
                ),
                region_code=region_code,
                source_file=file_name,
            )
        )

    seen_district_codes: set[int] = set()
    region_actual_mahallas = 0

    for d in districts:
        if not isinstance(d, dict):
            sink(
                Issue(
                    severity="critical",
                    code="DISTRICT_NOT_OBJECT",
                    message="district entry is not an object",
                    region_code=region_code,
                    source_file=file_name,
                )
            )
            continue
        region_actual_mahallas += _check_district(
            district=d,
            region_code=region_code,
            file_name=file_name,
            seen_codes=seen_district_codes,
            sink=sink,
        )

    counts.actual_mahallas = region_actual_mahallas

    if counts.declared_mahallas is not None and counts.declared_mahallas != counts.actual_mahallas:
        sink(
            Issue(
                severity="critical",
                code="REGION_MAHALLA_COUNT_MISMATCH",
                message=(
                    f"region_mahalla_count={counts.declared_mahallas} but actual "
                    f"mahallas={counts.actual_mahallas}"
                ),
                region_code=region_code,
                source_file=file_name,
            )
        )

    return counts


def _check_district(
    *,
    district: dict[str, Any],
    region_code: int | None,
    file_name: str,
    seen_codes: set[int],
    sink: IssueSink,
) -> int:
    code_raw = district.get("code")
    code = code_raw if isinstance(code_raw, int) else None

    if code is None:
        sink(
            Issue(
                severity="critical",
                code="DISTRICT_CODE_MISSING",
                message="district.code missing or non-integer",
                region_code=region_code,
                source_file=file_name,
            )
        )
    else:
        # Intra-region duplicates are also caught by the global uniqueness
        # check in the runner; tracking `seen_codes` here is kept only so
        # callers may use it for fast-path local lookups in the future.
        seen_codes.add(code)

        if region_code is not None and not str(code).startswith(str(region_code)):
            sink(
                Issue(
                    severity="critical",
                    code="DISTRICT_CODE_PREFIX_MISMATCH",
                    message=(f"district.code={code} does not start with region_code={region_code}"),
                    region_code=region_code,
                    district_code=code,
                    source_file=file_name,
                )
            )

    mahallas = district.get("mahallas")
    if not isinstance(mahallas, list):
        sink(
            Issue(
                severity="critical",
                code="DISTRICT_MAHALLAS_FIELD_MISSING",
                message="district.mahallas missing or not a list",
                region_code=region_code,
                district_code=code,
                source_file=file_name,
            )
        )
        mahallas = []

    declared = _int_or_none(district.get("mahalla_count"))
    actual = len(mahallas)

    if declared is not None and declared != actual:
        sink(
            Issue(
                severity="critical",
                code="DISTRICT_MAHALLA_COUNT_MISMATCH",
                message=(f"district.mahalla_count={declared} but actual mahallas={actual}"),
                region_code=region_code,
                district_code=code,
                source_file=file_name,
            )
        )

    for m in mahallas:
        if not isinstance(m, dict):
            sink(
                Issue(
                    severity="critical",
                    code="MAHALLA_NOT_OBJECT",
                    message="mahalla entry is not an object",
                    region_code=region_code,
                    district_code=code,
                    source_file=file_name,
                )
            )
            continue
        _check_mahalla(
            mahalla=m,
            region_code=region_code,
            district_code=code,
            file_name=file_name,
            sink=sink,
        )

    return actual


def _check_mahalla(
    *,
    mahalla: dict[str, Any],
    region_code: int | None,
    district_code: int | None,
    file_name: str,
    sink: IssueSink,
) -> None:
    stir = mahalla.get("stir")
    if stir is None or stir == "":
        sink(
            Issue(
                severity="critical",
                code="MAHALLA_STIR_MISSING",
                message="mahalla.stir missing or empty",
                region_code=region_code,
                district_code=district_code,
                source_file=file_name,
            )
        )
        return
    if not isinstance(stir, str):
        sink(
            Issue(
                severity="critical",
                code="MAHALLA_STIR_TYPE",
                message=f"mahalla.stir is not a string (got {type(stir).__name__})",
                region_code=region_code,
                district_code=district_code,
                stir=str(stir),
                source_file=file_name,
            )
        )
        return
    if not STIR_RE.match(stir):
        sink(
            Issue(
                severity="warning",
                code="MAHALLA_STIR_FORMAT",
                message=f"mahalla.stir={stir!r} does not match 9-digit format",
                region_code=region_code,
                district_code=district_code,
                stir=stir,
                source_file=file_name,
            )
        )


def check_region_code_uniqueness(
    region_codes: Iterable[tuple[int | None, str]],
    sink: IssueSink,
) -> None:
    seen: dict[int, list[str]] = {}
    for code, file_name in region_codes:
        if code is None:
            continue
        seen.setdefault(code, []).append(file_name)
    for code, files in seen.items():
        if len(files) > 1:
            sink(
                Issue(
                    severity="critical",
                    code="REGION_CODE_DUPLICATE",
                    message=f"region_code={code} appears in {len(files)} files: {files}",
                    region_code=code,
                )
            )


def check_district_code_global_uniqueness(
    district_records: Iterable[tuple[int, int | None, str | None, str]],
    sink: IssueSink,
) -> None:
    """district_records: (district_code, region_code, district_name, source_file).

    Reports duplicates across the entire corpus, including duplicates that
    happen to occur inside one region file. One critical issue per duplicate
    code group, with all occurrences described in the message.
    """
    seen: dict[int, list[tuple[int | None, str | None, str]]] = {}
    for code, region_code, district_name, file_name in district_records:
        seen.setdefault(code, []).append((region_code, district_name, file_name))
    for code, occurrences in seen.items():
        if len(occurrences) > 1:
            occ_strs = [f"region={r} name={n!r} file={f}" for r, n, f in occurrences]
            sink(
                Issue(
                    severity="critical",
                    code="DISTRICT_CODE_DUPLICATE_GLOBAL",
                    message=(
                        f"district_code={code} appears {len(occurrences)} times: "
                        + "; ".join(occ_strs)
                    ),
                    district_code=code,
                )
            )


def check_global_stir_uniqueness(
    stir_records: Iterable[tuple[str, int | None, int | None, str]],
    sink: IssueSink,
) -> None:
    """stir_records: (stir, region_code, district_code, source_file).

    Reports duplicates across the entire corpus. Each duplicate STIR yields
    one critical issue (we do not flood per-occurrence).
    """
    seen: dict[str, list[tuple[int | None, int | None, str]]] = {}
    for stir, region_code, district_code, file_name in stir_records:
        seen.setdefault(stir, []).append((region_code, district_code, file_name))
    for stir, occurrences in seen.items():
        if len(occurrences) > 1:
            files = sorted({o[2] for o in occurrences})
            sink(
                Issue(
                    severity="critical",
                    code="MAHALLA_STIR_DUPLICATE",
                    message=(f"stir={stir} appears {len(occurrences)} times across files: {files}"),
                    stir=stir,
                )
            )


def _int_or_none(v: Any) -> int | None:
    return v if isinstance(v, int) and not isinstance(v, bool) else None
