"""Phase 4A importer orchestrator.

Single import run. Walks JSON files in source-order, inserts:
- source_region_files
- regions, districts, mahallas (linked by surrogate IDs from JSON nesting,
  never by natural keys)
- entity_kpis (region/district/mahalla KPIs)
- data_quality_issues (from existing audit module)

Hierarchy is built from JSON nesting only. Natural keys are stored as columns
but never used to look up parents. Source values are copied as-is.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from cerr_chatbot.audit import run_audit
from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.db import (
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
from cerr_chatbot.importer.summary import ImportSummary
from cerr_chatbot.sources import discover_region_files

_REGION_FILE_ID_RE = re.compile(r"^cerr_region_(?P<id>\d+)\.json$")

# Cyrillic label used by the source for the status badge inside header.meta[].
# Stored as a constant (not inlined) so search/replace stays unambiguous.
_STATUS_META_LABEL = "Статус"  # "Статус"


def run_import(engine: Engine, settings: Settings | None = None) -> ImportSummary:
    cfg = settings or get_settings()
    summary = ImportSummary()

    started_at = datetime.now(UTC)
    run = ImportRun(
        started_at=started_at,
        source_dir=str(cfg.cerr_source_dir),
        status="running",
    )

    # Phase 1: open run row.
    with Session(engine, expire_on_commit=False) as s:
        s.add(run)
        s.commit()
        summary.import_run_id = run.import_run_id

    # Phase 2: discover + insert entities + KPIs.
    try:
        files = discover_region_files(cfg)
        summary.files = len(files)

        with Session(engine, expire_on_commit=False) as s:
            db_run = s.get(ImportRun, run.import_run_id)
            if db_run is not None:
                db_run.source_file_count = len(files)
                s.commit()

        with Session(engine, expire_on_commit=False) as s:
            for rf in files:
                payload = _load_payload(rf.path)
                _import_one_file(
                    s,
                    run_id=run.import_run_id,
                    file_path=rf.path,
                    payload=payload,
                    summary=summary,
                )
            s.commit()

        # Phase 3: audit + persist data_quality_issues. A crash here is
        # treated as importer failure: we cannot guarantee Phase 4A finished.
        # "Critical issues exist" is NOT a failure.
        report = run_audit(cfg)
        with Session(engine, expire_on_commit=False) as s:
            severities: list[str] = []
            codes: list[str] = []
            for issue in report.issues:
                s.add(
                    DataQualityIssue(
                        import_run_id=run.import_run_id,
                        severity=issue.severity,
                        issue_code=issue.code,
                        message=issue.message,
                        source_file=issue.source_file,
                        region_code=issue.region_code,
                        district_code=issue.district_code,
                        mahalla_stir=issue.stir,
                        source_json_path=None,
                        details_json=None,
                    )
                )
                severities.append(issue.severity)
                codes.append(issue.code)
            s.commit()
            summary.add_issues(severities, codes)
    except Exception as exc:  # noqa: BLE001 - re-classify, mark failed, re-raise
        with Session(engine, expire_on_commit=False) as s:
            db_run = s.get(ImportRun, run.import_run_id)
            if db_run is not None:
                db_run.status = "failed"
                db_run.notes = f"{type(exc).__name__}: {exc}"
                # completed_at intentionally left NULL
                s.commit()
        summary.status = "failed"
        summary.error_message = f"{type(exc).__name__}: {exc}"
        raise

    # Phase 4: mark completed only after entities + KPIs + audit + issues all OK.
    with Session(engine, expire_on_commit=False) as s:
        db_run = s.get(ImportRun, run.import_run_id)
        if db_run is not None:
            db_run.completed_at = datetime.now(UTC)
            db_run.status = "completed"
            s.commit()
    summary.status = "completed"
    return summary


def _import_one_file(
    s: Session,
    *,
    run_id: int,
    file_path: Path,
    payload: dict[str, Any],
    summary: ImportSummary,
) -> None:
    file_name = file_path.name
    region_code_from_filename = _region_code_from_filename(file_name)
    file_sha256 = _hash_file_bytes(file_path)
    file_size = file_path.stat().st_size

    s.add(
        SourceRegionFile(
            import_run_id=run_id,
            source_file=file_name,
            region_code_from_filename=region_code_from_filename,
            file_size_bytes=file_size,
            file_sha256=file_sha256,
        )
    )

    region_overview = payload.get("region_overview") if isinstance(payload, dict) else None
    region_header = region_overview.get("header") if isinstance(region_overview, dict) else None

    districts = payload.get("districts") if isinstance(payload, dict) else None
    # Empty list is a real, observed shape: actual = 0. Only NULL when source
    # shape is missing/non-list (importer cannot count what isn't there).
    actual_district_count: int | None
    actual_mahalla_count: int | None
    if isinstance(districts, list):
        actual_district_count = sum(1 for d in districts if isinstance(d, dict))
        mahalla_total = 0
        for d in districts:
            if isinstance(d, dict):
                ms = d.get("mahallas")
                if isinstance(ms, list):
                    mahalla_total += sum(1 for m in ms if isinstance(m, dict))
        actual_mahalla_count = mahalla_total
    else:
        actual_district_count = None
        actual_mahalla_count = None

    region = Region(
        import_run_id=run_id,
        source_file=file_name,
        source_region_index=0,
        region_code=_int_or_none(payload.get("region_code")),
        region_name_cyr=_str_or_none(payload.get("region_name")),
        declared_district_count=_int_or_none(payload.get("districts_count")),
        declared_mahalla_count=_int_or_none(payload.get("region_mahalla_count")),
        actual_district_count=actual_district_count,
        actual_mahalla_count=actual_mahalla_count,
        source_generated_at=_parse_iso(payload.get("generated_at")),
        raw_header_json=region_header if isinstance(region_header, dict) else None,
        raw_overview_json=region_overview if isinstance(region_overview, dict) else None,
    )
    s.add(region)
    s.flush()  # populate region.region_id for child FKs
    summary.regions += 1

    _import_kpis(
        s,
        run_id=run_id,
        overview=region_overview,
        level="region",
        region_id=region.region_id,
        district_id=None,
        mahalla_id=None,
        summary=summary,
    )

    if not isinstance(districts, list):
        return

    for d_idx, d in enumerate(districts):
        if not isinstance(d, dict):
            continue
        _import_district(
            s,
            run_id=run_id,
            file_name=file_name,
            region=region,
            district_index=d_idx,
            district_node=d,
            summary=summary,
        )


def _import_district(
    s: Session,
    *,
    run_id: int,
    file_name: str,
    region: Region,
    district_index: int,
    district_node: dict[str, Any],
    summary: ImportSummary,
) -> None:
    overview = district_node.get("overview")
    macro = district_node.get("macro")
    mahallas = district_node.get("mahallas")
    actual_mahalla_count = (
        sum(1 for m in mahallas if isinstance(m, dict)) if isinstance(mahallas, list) else None
    )

    district = District(
        region_id=region.region_id,
        import_run_id=run_id,
        source_file=file_name,
        source_district_index=district_index,
        region_code=region.region_code,
        district_code=_int_or_none(district_node.get("code")),
        district_name_cyr=_str_or_none(district_node.get("name")),
        declared_mahalla_count=_int_or_none(district_node.get("mahalla_count")),
        actual_mahalla_count=actual_mahalla_count,
        macro_period_label_cyr=_str_or_none(
            macro.get("period") if isinstance(macro, dict) else None
        ),
        raw_overview_json=overview if isinstance(overview, dict) else None,
        raw_macro_json=macro if isinstance(macro, dict) else None,
    )
    s.add(district)
    s.flush()
    summary.districts += 1

    _import_kpis(
        s,
        run_id=run_id,
        overview=overview,
        level="district",
        region_id=None,
        district_id=district.district_id,
        mahalla_id=None,
        summary=summary,
    )
    _import_macro(s, run_id=run_id, district=district, macro=macro, summary=summary)
    _import_rating_histogram(
        s, run_id=run_id, district=district, overview=overview, summary=summary
    )

    if not isinstance(mahallas, list):
        return

    for m_idx, m in enumerate(mahallas):
        if not isinstance(m, dict):
            continue
        _import_mahalla(
            s,
            run_id=run_id,
            file_name=file_name,
            region=region,
            district=district,
            mahalla_index=m_idx,
            mahalla_node=m,
            summary=summary,
        )


def _import_mahalla(
    s: Session,
    *,
    run_id: int,
    file_name: str,
    region: Region,
    district: District,
    mahalla_index: int,
    mahalla_node: dict[str, Any],
    summary: ImportSummary,
) -> None:
    overview = mahalla_node.get("overview")
    header = overview.get("header") if isinstance(overview, dict) else None

    district_rank = header.get("district_rank") if isinstance(header, dict) else None
    region_rank = header.get("region_rank") if isinstance(header, dict) else None
    category = header.get("category") if isinstance(header, dict) else None

    detail = overview.get("detail") if isinstance(overview, dict) else None
    specialization = detail.get("specialization") if isinstance(detail, dict) else None
    crops = detail.get("crops") if isinstance(detail, dict) else None
    peer_profile = overview.get("peer_profile") if isinstance(overview, dict) else None
    peer_set = peer_profile.get("peer_set") if isinstance(peer_profile, dict) else None
    fallback_raw = peer_set.get("fallback_to_district") if isinstance(peer_set, dict) else None

    mahalla = Mahalla(
        district_id=district.district_id,
        region_id=region.region_id,
        import_run_id=run_id,
        source_file=file_name,
        source_district_index=district.source_district_index,
        source_mahalla_index=mahalla_index,
        region_code=region.region_code,
        district_code=district.district_code,
        mahalla_stir=_str_or_none(mahalla_node.get("stir")),
        mahalla_name_cyr=_str_or_none(mahalla_node.get("name")),
        rating_score=_float_or_none(mahalla_node.get("rating_score")),
        district_rank_text=_str_or_none(district_rank),
        region_rank_text=_str_or_none(region_rank),
        category_label_cyr=_str_or_none(category),
        status_label_cyr=_extract_meta_value(header, _STATUS_META_LABEL),
        specialization_residual_percent=_float_or_none(
            specialization.get("residual_percent") if isinstance(specialization, dict) else None
        ),
        specialization_total_known_percent=_float_or_none(
            specialization.get("total_known_percent") if isinstance(specialization, dict) else None
        ),
        crop_total_homestead_area_sotkah=_float_or_none(
            crops.get("total_homestead_area_sotikh") if isinstance(crops, dict) else None
        ),
        peer_set_count=_int_or_none(peer_set.get("count") if isinstance(peer_set, dict) else None),
        peer_set_description_cyr=_str_or_none(
            peer_set.get("description") if isinstance(peer_set, dict) else None
        ),
        peer_fallback_to_district_flag=fallback_raw if isinstance(fallback_raw, bool) else None,
        peer_indicator_count=_int_or_none(
            peer_profile.get("indicator_count") if isinstance(peer_profile, dict) else None
        ),
        peer_total_indicators_considered=_int_or_none(
            peer_profile.get("total_indicators_considered")
            if isinstance(peer_profile, dict)
            else None
        ),
        raw_header_json=header if isinstance(header, dict) else None,
        raw_overview_json=overview if isinstance(overview, dict) else None,
    )
    s.add(mahalla)
    s.flush()
    summary.mahallas += 1

    _import_kpis(
        s,
        run_id=run_id,
        overview=overview,
        level="mahalla",
        region_id=None,
        district_id=None,
        mahalla_id=mahalla.mahalla_id,
        summary=summary,
    )
    _import_mahalla_details(
        s,
        run_id=run_id,
        mahalla_id=mahalla.mahalla_id,
        overview=overview,
        summary=summary,
    )


def _import_mahalla_details(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    overview: Any,
    summary: ImportSummary,
) -> None:
    """Insert all six mahalla detail groups for one parent mahalla.

    Every helper returns silently when its source block is missing or not the
    expected shape. Missing source = no row inserted. Never invents data.
    """
    if not isinstance(overview, dict):
        return
    detail = overview.get("detail")
    appeals = overview.get("appeals")
    peer_profile = overview.get("peer_profile")

    if isinstance(detail, dict):
        infra = detail.get("infra")
        if isinstance(infra, dict):
            _import_infra(s, run_id=run_id, mahalla_id=mahalla_id, infra=infra, summary=summary)

        specialization = detail.get("specialization")
        if isinstance(specialization, dict):
            _import_specializations(
                s,
                run_id=run_id,
                mahalla_id=mahalla_id,
                specialization=specialization,
                summary=summary,
            )

        crops = detail.get("crops")
        if isinstance(crops, dict):
            _import_crops(s, run_id=run_id, mahalla_id=mahalla_id, crops=crops, summary=summary)

        subsidies = detail.get("subsidies")
        if isinstance(subsidies, dict):
            _import_subsidies(
                s, run_id=run_id, mahalla_id=mahalla_id, subsidies=subsidies, summary=summary
            )

    if isinstance(appeals, dict):
        _import_appeals(s, run_id=run_id, mahalla_id=mahalla_id, appeals=appeals, summary=summary)

    if isinstance(peer_profile, dict):
        _import_peer_factors(
            s,
            run_id=run_id,
            mahalla_id=mahalla_id,
            peer_profile=peer_profile,
            summary=summary,
        )


def _import_infra(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    infra: dict[str, Any],
    summary: ImportSummary,
) -> None:
    s.add(
        MahallaInfrastructureRow(
            mahalla_id=mahalla_id,
            import_run_id=run_id,
            road_total_km=_float_or_none(infra.get("road_km")),
            road_dirt_km=_float_or_none(infra.get("road_dirt_km")),
            road_asphalt_km=_float_or_none(infra.get("road_asphalt_km")),
            households_without_drinking_water_count=_int_or_none(infra.get("no_water")),
            power_outage_count=_int_or_none(infra.get("power_cuts")),
            # power_hrs is free-form text in source ("0", "2 soat", etc.).
            # Store verbatim string only; never coerce to numeric.
            power_outage_hours_text=_str_or_none(infra.get("power_hrs")),
            medical_facility_distance_km=_float_or_none(infra.get("medical_km")),
            school_count=_int_or_none(infra.get("school")),
            sports_facility_count=_int_or_none(infra.get("sport")),
            kindergarten_count=_int_or_none(infra.get("kindergarten")),
            homestead_area_ha=_float_or_none(infra.get("tomorqa_ha")),
        )
    )
    summary.mahalla_infrastructure_rows += 1


def _import_appeals(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    appeals: dict[str, Any],
    summary: ImportSummary,
) -> None:
    s.add(
        MahallaAppealRow(
            mahalla_id=mahalla_id,
            import_run_id=run_id,
            crime_appeal_count=_int_or_none(appeals.get("crime")),
            divorce_appeal_count=_int_or_none(appeals.get("divorce")),
            social_aid_appeal_count=_int_or_none(appeals.get("aid")),
            employment_appeal_count=_int_or_none(appeals.get("employment")),
            gas_appeal_count=_int_or_none(appeals.get("gas")),
            registry_appeal_count=_int_or_none(appeals.get("registry")),
            appeals_year=_int_or_none(appeals.get("year")),
            appeals_period_label_cyr=_str_or_none(appeals.get("period")),
        )
    )
    summary.mahalla_appeal_rows += 1


def _import_specializations(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    specialization: dict[str, Any],
    summary: ImportSummary,
) -> None:
    items = specialization.get("items")
    if not isinstance(items, list):
        return
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        s.add(
            MahallaSpecializationItem(
                mahalla_id=mahalla_id,
                import_run_id=run_id,
                item_order=idx,
                specialization_slot=_str_or_none(item.get("slot")),
                specialization_slot_label_cyr=_str_or_none(item.get("slot_label")),
                specialization_type_cyr=_str_or_none(item.get("type")),
                specialization_direction_cyr=_str_or_none(item.get("direction")),
                household_count=_float_or_none(item.get("households")),
                population_count=_float_or_none(item.get("population")),
                share_percent=_float_or_none(item.get("percent")),
            )
        )
        summary.mahalla_specialization_rows += 1


def _import_crops(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    crops: dict[str, Any],
    summary: ImportSummary,
) -> None:
    seasons = crops.get("seasons")
    if not isinstance(seasons, list):
        return
    for idx, season in enumerate(seasons):
        if not isinstance(season, dict):
            continue
        s.add(
            MahallaCropSeason(
                mahalla_id=mahalla_id,
                import_run_id=run_id,
                season_order=idx,
                season_key=_str_or_none(season.get("key")),
                season_label_cyr=_str_or_none(season.get("label")),
                crops_text_cyr=_str_or_none(season.get("crops_text")),
                total_area_ha=_float_or_none(season.get("total_area_ha")),
                homestead_area_ha=_float_or_none(season.get("homestead_area_ha")),
                household_count=_int_or_none(season.get("household_count")),
                # Preserve full season dict (incl. crops[]) verbatim instead of
                # parsing crops[] into a separate table this phase.
                raw_crops_json=season,
            )
        )
        summary.mahalla_crop_rows += 1


def _import_subsidies(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    subsidies: dict[str, Any],
    summary: ImportSummary,
) -> None:
    programs = subsidies.get("programs")
    if not isinstance(programs, list):
        return
    parent_year = _int_or_none(subsidies.get("year"))
    parent_data_date = _str_or_none(subsidies.get("data_date"))
    for idx, program in enumerate(programs):
        if not isinstance(program, dict):
            continue
        has_amount = program.get("has_amount_source")
        s.add(
            MahallaSubsidyProgram(
                mahalla_id=mahalla_id,
                import_run_id=run_id,
                program_order=idx,
                subsidy_program_label_cyr=_str_or_none(program.get("label")),
                application_count=_float_or_none(program.get("applications")),
                required_amount_mln_uzs=_float_or_none(program.get("required_amount_mln")),
                has_amount_source_flag=has_amount if isinstance(has_amount, bool) else None,
                subsidies_year=parent_year,
                subsidies_data_date=parent_data_date,
            )
        )
        summary.mahalla_subsidy_program_rows += 1


def _import_peer_factors(
    s: Session,
    *,
    run_id: int,
    mahalla_id: int,
    peer_profile: dict[str, Any],
    summary: ImportSummary,
) -> None:
    for polarity_key, polarity_value in (("strengths", "strength"), ("weaknesses", "weakness")):
        items = peer_profile.get(polarity_key)
        if not isinstance(items, list):
            continue
        for idx, factor in enumerate(items):
            if not isinstance(factor, dict):
                continue
            s.add(
                MahallaPeerFactor(
                    mahalla_id=mahalla_id,
                    import_run_id=run_id,
                    factor_polarity=polarity_value,
                    factor_order=idx,
                    factor_key=_str_or_none(factor.get("key")),
                    factor_label_cyr=_str_or_none(factor.get("label")),
                    factor_unit=_str_or_none(factor.get("unit")),
                    factor_direction=_str_or_none(factor.get("direction")),
                    entity_value_num=_float_or_none(factor.get("this_value")),
                    comparison_average_value=_float_or_none(factor.get("district_avg")),
                    peer_rank=_int_or_none(factor.get("peer_rank")),
                    peer_count=_int_or_none(factor.get("peer_count")),
                    percentile=_float_or_none(factor.get("percentile")),
                )
            )
            summary.mahalla_peer_factor_rows += 1


def _import_macro(
    s: Session,
    *,
    run_id: int,
    district: District,
    macro: Any,
    summary: ImportSummary,
) -> None:
    if not isinstance(macro, dict):
        return
    indicators = macro.get("indicators")
    if not isinstance(indicators, list):
        return
    for ind in indicators:
        if not isinstance(ind, dict):
            continue
        key = ind.get("key")
        if not isinstance(key, str):
            continue

        raw_points = ind.get("points")
        points: list[Any] = raw_points if isinstance(raw_points, list) else []
        # Highlighted derivation: the indicator row's highlighted_value_num is
        # populated ONLY from a source point with highlighted=true. We never
        # match by district_name to compensate for a missing flag - that would
        # synthesize identity the source did not assert.
        highlighted_points = [
            p for p in points if isinstance(p, dict) and p.get("highlighted") is True
        ]
        highlighted_missing = len(highlighted_points) == 0
        highlighted_value_num: float | None = None
        highlighted_value_null = False
        if highlighted_points:
            # If the source flagged multiple points highlighted (shouldn't
            # happen, but observed counts in 2B2 show single highlighted per
            # district), take the first in source order. The full list is
            # preserved verbatim in district_macro_points anyway.
            first = highlighted_points[0]
            raw_val = first.get("value")
            highlighted_value_num = _float_or_none(raw_val)
            if highlighted_value_num is None:
                highlighted_value_null = True

        indicator_row = DistrictMacroIndicator(
            district_id=district.district_id,
            import_run_id=run_id,
            indicator_key=key,
            indicator_label_cyr=_str_or_none(ind.get("label")),
            indicator_unit=_str_or_none(ind.get("unit")),
            indicator_direction=_str_or_none(ind.get("direction")),
            period_label_cyr=district.macro_period_label_cyr,
            highlighted_value_num=highlighted_value_num,
            highlighted_missing_flag=highlighted_missing,
            highlighted_value_null_flag=highlighted_value_null,
        )
        s.add(indicator_row)
        s.flush()
        summary.district_macro_indicators += 1

        for p_idx, p in enumerate(points):
            if not isinstance(p, dict):
                continue
            s.add(
                DistrictMacroPoint(
                    macro_indicator_id=indicator_row.macro_indicator_id,
                    import_run_id=run_id,
                    point_order=p_idx,
                    point_district_name_cyr=_str_or_none(p.get("district_name")),
                    point_value_num=_float_or_none(p.get("value")),
                    is_highlighted=p.get("highlighted") is True,
                )
            )
            summary.district_macro_points += 1


def _import_rating_histogram(
    s: Session,
    *,
    run_id: int,
    district: District,
    overview: Any,
    summary: ImportSummary,
) -> None:
    if not isinstance(overview, dict):
        return
    buckets = overview.get("rating_histogram")
    if not isinstance(buckets, list):
        return
    for b_idx, b in enumerate(buckets):
        if not isinstance(b, dict):
            continue
        s.add(
            DistrictRatingHistogram(
                district_id=district.district_id,
                import_run_id=run_id,
                bucket_order=b_idx,
                rating_bucket_label_cyr=_str_or_none(b.get("bucket")),
                mahalla_count=_int_or_none(b.get("count")),
            )
        )
        summary.district_rating_histogram_rows += 1


def _import_kpis(
    s: Session,
    *,
    run_id: int,
    overview: Any,
    level: str,
    region_id: int | None,
    district_id: int | None,
    mahalla_id: int | None,
    summary: ImportSummary,
) -> None:
    if not isinstance(overview, dict):
        return
    kpis = overview.get("kpis")
    if not isinstance(kpis, list):
        return
    for k in kpis:
        if not isinstance(k, dict):
            continue
        key = k.get("key")
        if not isinstance(key, str):
            continue
        s.add(
            EntityKpi(
                import_run_id=run_id,
                entity_level=level,
                region_id=region_id,
                district_id=district_id,
                mahalla_id=mahalla_id,
                kpi_key=key,
                kpi_label_cyr=_str_or_none(k.get("label")),
                source_table_name=_str_or_none(k.get("table")),
                source_column_name=_str_or_none(k.get("column")),
                kpi_format=_str_or_none(k.get("format")),
                kpi_provenance=_str_or_none(k.get("provenance")),
                kpi_direction=_str_or_none(k.get("direction")),
                kpi_value_num=_float_or_none(k.get("value")),
                kpi_error_text=_str_or_none(k.get("error")),
                change_percent=_float_or_none(k.get("change_pct")),
                district_average_value=_float_or_none(k.get("district_avg")),
                compare_scope=_str_or_none(k.get("compare_scope")),
            )
        )
        summary.entity_kpis += 1


# ----- helpers -----


def _load_payload(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"top-level of {path.name} is not a JSON object")
    return data


def _hash_file_bytes(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _region_code_from_filename(file_name: str) -> int | None:
    m = _REGION_FILE_ID_RE.match(file_name)
    return int(m.group("id")) if m else None


def _str_or_none(v: Any) -> str | None:
    return v if isinstance(v, str) else None


def _int_or_none(v: Any) -> int | None:
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def _float_or_none(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def _extract_meta_value(header: Any, label: str) -> str | None:
    """Return the value of header.meta[] item where item.label == label.

    Source-fidelity: copies the value as-is. Returns None when the label is
    absent or the value is not a string. Never invents a value.
    """
    if not isinstance(header, dict):
        return None
    meta = header.get("meta")
    if not isinstance(meta, list):
        return None
    for item in meta:
        if not isinstance(item, dict):
            continue
        if item.get("label") == label:
            v = item.get("value")
            return v if isinstance(v, str) else None
    return None


def _parse_iso(v: Any) -> datetime | None:
    if not isinstance(v, str):
        return None
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        return None
