"""Numeric profile orchestrator + JSON / Markdown writers."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.numeric_profile.collectors import (
    Collected,
    KpiAccumulator,
    MacroAccumulator,
    PeerAccumulator,
    collect,
)
from cerr_chatbot.numeric_profile.models import (
    EXPECTED_BASE_KPI_KEYS,
    DetailFieldProfile,
    KpiKeyProfile,
    MacroIndicatorProfile,
    NaturalKeyDiagnostics,
    NumericProfileReport,
    PeerFactorProfile,
)
from cerr_chatbot.numeric_profile.stats import NumericStats, ValueBag, compute_stats
from cerr_chatbot.sources import discover_region_files

LEVELS: tuple[str, ...] = ("region", "district", "mahalla")


def run_numeric_profile(settings: Settings | None = None) -> NumericProfileReport:
    cfg = settings or get_settings()
    files = discover_region_files(cfg)
    source_dir_abs = (
        cfg.cerr_source_dir
        if cfg.cerr_source_dir.is_absolute()
        else (Path.cwd() / cfg.cerr_source_dir).resolve()
    )

    collected = Collected()
    for rf in files:
        with rf.path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if isinstance(payload, dict):
            collect(payload, collected, file_name=rf.path.name)

    expected_per_level = {
        "region": collected.region_count,
        "district": collected.district_count,
        "mahalla": collected.mahalla_count,
    }

    detail_profiles = _detail_profiles(collected)
    kpi_profiles = _kpi_profiles(collected, expected_per_level)

    report = NumericProfileReport(
        run_at=datetime.now(UTC).isoformat(),
        source_dir=str(source_dir_abs),
        source_files=[f.path.name for f in files],
        entity_counts=expected_per_level,
        base_kpi_coverage=_base_coverage(collected),
        kpi_profiles=kpi_profiles,
        macro_indicator_profiles=_macro_profiles(collected, expected_per_level["district"]),
        macro_district_completeness={
            f"{rid[0]}#d{rid[1]}": n for rid, n in collected.macro_district_indicator_count.items()
        },
        peer_factor_profiles=_peer_profiles(collected),
        detail_field_profiles=detail_profiles,
        natural_key_diagnostics=_natural_key_diagnostics(collected),
        null_free_numeric_fields=_null_free_fields(kpi_profiles, detail_profiles),
    )
    report.high_risk_findings = _build_findings(report)
    return report


def _natural_key_diagnostics(c: Collected) -> NaturalKeyDiagnostics:
    def _dups(counter: Counter[Any], cap: int = 10) -> tuple[int, int, list[Any]]:
        unique = len(counter)
        dup_keys = [k for k, n in counter.items() if n > 1]
        examples = sorted(dup_keys, key=str)[:cap]
        return unique, len(dup_keys), examples

    rc_u, rc_d, rc_ex = _dups(c.region_code_counts)
    dc_u, dc_d, dc_ex = _dups(c.district_code_counts)
    st_u, st_d, st_ex = _dups(c.mahalla_stir_counts)
    ck_u, ck_d, ck_ex = _dups(c.mahalla_composite_key_counts)
    return NaturalKeyDiagnostics(
        region_code_unique_count=rc_u,
        region_code_duplicate_group_count=rc_d,
        region_code_duplicate_examples=list(rc_ex),
        district_code_unique_count=dc_u,
        district_code_duplicate_group_count=dc_d,
        district_code_duplicate_examples=list(dc_ex),
        mahalla_stir_unique_count=st_u,
        mahalla_stir_duplicate_group_count=st_d,
        mahalla_stir_duplicate_examples=list(st_ex),
        mahalla_composite_key_unique_count=ck_u,
        mahalla_composite_key_duplicate_group_count=ck_d,
        mahalla_composite_key_duplicate_examples=[list(t) for t in ck_ex],
    )


def _null_free_fields(
    kpi_profiles: list[KpiKeyProfile], detail_profiles: list[DetailFieldProfile]
) -> list[str]:
    out: list[str] = []
    for kp in kpi_profiles:
        if kp.value_stats.total > 0 and kp.value_stats.null_count == 0:
            out.append(f"kpi:{kp.level}:{kp.kpi_key}")
    for dp in detail_profiles:
        if dp.value_stats.total > 0 and dp.value_stats.null_count == 0:
            out.append(f"detail:{dp.group}:{dp.column_name}")
    return out


def _base_coverage(c: Collected) -> dict[str, dict[str, bool]]:
    out: dict[str, dict[str, bool]] = {}
    for level in LEVELS:
        out[level] = {key: ((level, key) in c.kpis) for key in EXPECTED_BASE_KPI_KEYS}
    return out


def _kpi_profiles(c: Collected, expected: dict[str, int]) -> list[KpiKeyProfile]:
    profiles: list[KpiKeyProfile] = []
    for (level, key), acc in sorted(c.kpis.items()):
        exp = expected.get(level, 0)
        row_count = acc.value.total()
        missing = max(exp - len(acc.seen_row_ids), 0)
        profiles.append(
            KpiKeyProfile(
                level=level,
                kpi_key=key,
                expected_entity_count=exp,
                row_count=row_count,
                missing_entity_count=missing,
                value_stats=compute_stats(acc.value),
                change_pct_stats=compute_stats(acc.change_pct),
                district_avg_stats=compute_stats(acc.district_avg),
                distinct_labels=sorted(acc.labels),
                distinct_formats=sorted(acc.formats),
                distinct_directions=sorted(acc.directions),
                distinct_source_table_names=sorted(acc.tables),
                distinct_source_column_names=sorted(acc.columns),
                distinct_compare_scopes=sorted({str(s) for s in acc.scopes}),
                distinct_provenance=sorted(acc.provenance),
            )
        )
    return profiles


def _macro_profiles(c: Collected, expected_districts: int) -> list[MacroIndicatorProfile]:
    profiles: list[MacroIndicatorProfile] = []
    for key, acc in sorted(c.macro.items()):
        ppd = acc.points_per_district
        district_row_count = len(acc.seen_district_row_ids)
        highlighted_seen = len(acc.highlighted_seen_row_ids)
        profiles.append(
            MacroIndicatorProfile(
                indicator_key=key,
                district_row_count=district_row_count,
                expected_district_count=expected_districts,
                missing_district_count=max(expected_districts - district_row_count, 0),
                distinct_labels=sorted(acc.labels),
                distinct_units=sorted(acc.units),
                distinct_directions=sorted(acc.directions),
                points_per_district_min=min(ppd) if ppd else 0,
                points_per_district_max=max(ppd) if ppd else 0,
                total_points=acc.total_points,
                highlighted_count=acc.highlighted_count,
                highlighted_missing_count=max(expected_districts - highlighted_seen, 0),
                highlighted_value_null_count=acc.highlighted_value_null_count,
                all_point_value_stats=compute_stats(acc.all_point_values),
                highlighted_value_stats=compute_stats(acc.highlighted_values),
            )
        )
    return profiles


def _peer_profiles(c: Collected) -> list[PeerFactorProfile]:
    profiles: list[PeerFactorProfile] = []
    for (polarity, key), acc in sorted(c.peer.items()):
        profiles.append(
            PeerFactorProfile(
                polarity=polarity,
                factor_key=key,
                row_count=acc.this_value.total(),
                this_value_stats=compute_stats(acc.this_value),
                district_avg_stats=compute_stats(acc.district_avg),
                percentile_stats=compute_stats(acc.percentile),
                peer_rank_min=min(acc.peer_ranks) if acc.peer_ranks else None,
                peer_rank_max=max(acc.peer_ranks) if acc.peer_ranks else None,
                peer_count_min=min(acc.peer_counts) if acc.peer_counts else None,
                peer_count_max=max(acc.peer_counts) if acc.peer_counts else None,
                distinct_labels=sorted(acc.labels),
                distinct_units=sorted(acc.units),
                distinct_directions=sorted(acc.directions),
                rank_exceeds_count=acc.rank_exceeds_count,
                percentile_out_of_range=acc.percentile_out_of_range,
            )
        )
    return profiles


def _detail_profiles(c: Collected) -> list[DetailFieldProfile]:
    profiles: list[DetailFieldProfile] = []
    for (group, column, json_path), bag in sorted(c.detail_bags.items()):
        profiles.append(
            DetailFieldProfile(
                group=group,
                column_name=column,
                json_path=json_path,
                value_stats=compute_stats(bag),
            )
        )
    return profiles


def _build_findings(report: NumericProfileReport) -> list[str]:
    findings: list[str] = []

    # Base KPI coverage gaps (KPI key entirely absent at a level).
    for level, cov in report.base_kpi_coverage.items():
        missing = [k for k, present in cov.items() if not present]
        if missing:
            findings.append(f"BASE_KPI_MISSING level={level} keys={missing}")

    # KPI value quality. Row-id based completeness is real (duplicate natural
    # keys do not contribute to missing_entity_count any more).
    for kp in report.kpi_profiles:
        if kp.value_stats.null_percent >= 50:
            findings.append(
                f"KPI_NULL_HEAVY level={kp.level} key={kp.kpi_key} "
                f"null_pct={kp.value_stats.null_percent}"
            )
        if kp.value_stats.bad_value_examples:
            findings.append(
                f"KPI_BAD_VALUES level={kp.level} key={kp.kpi_key} "
                f"examples={kp.value_stats.bad_value_examples[:3]}"
            )
        if kp.missing_entity_count > 0:
            findings.append(
                f"KPI_ROWS_MISSING level={kp.level} key={kp.kpi_key} "
                f"missing={kp.missing_entity_count}/{kp.expected_entity_count} "
                "(row-id based; not a duplicate-key artifact)"
            )

    # Macro completeness.
    for mp in report.macro_indicator_profiles:
        if mp.missing_district_count > 0:
            findings.append(
                f"MACRO_MISSING_DISTRICT_ROWS key={mp.indicator_key} "
                f"missing={mp.missing_district_count}/{mp.expected_district_count}"
            )
        if mp.highlighted_missing_count > 0:
            findings.append(
                f"MACRO_HIGHLIGHTED_MISSING key={mp.indicator_key} "
                f"missing={mp.highlighted_missing_count}/{mp.expected_district_count}"
            )
        if mp.highlighted_value_null_count > 0:
            findings.append(
                f"MACRO_HIGHLIGHTED_NULL key={mp.indicator_key} "
                f"null={mp.highlighted_value_null_count}/{mp.highlighted_count}"
            )

    # Peer anomalies.
    for pp in report.peer_factor_profiles:
        if pp.rank_exceeds_count > 0:
            findings.append(
                f"PEER_RANK_EXCEEDS_COUNT polarity={pp.polarity} key={pp.factor_key} "
                f"count={pp.rank_exceeds_count}"
            )
        if pp.percentile_out_of_range > 0:
            findings.append(
                f"PEER_PERCENTILE_OUT_OF_RANGE polarity={pp.polarity} key={pp.factor_key} "
                f"count={pp.percentile_out_of_range}"
            )

    # Detail null heavy or bad values.
    for dp in report.detail_field_profiles:
        if dp.value_stats.null_percent >= 80:
            findings.append(
                f"DETAIL_NULL_HEAVY column={dp.column_name} group={dp.group} "
                f"null_pct={dp.value_stats.null_percent}"
            )
        if dp.value_stats.bad_value_examples:
            findings.append(
                f"DETAIL_BAD_VALUES column={dp.column_name} group={dp.group} "
                f"examples={dp.value_stats.bad_value_examples[:3]}"
            )

    # Natural-key collisions (independent of completeness).
    nk = report.natural_key_diagnostics
    if nk.region_code_duplicate_group_count > 0:
        findings.append(
            f"REGION_CODE_COLLISION groups={nk.region_code_duplicate_group_count} "
            f"examples={nk.region_code_duplicate_examples[:5]}"
        )
    if nk.district_code_duplicate_group_count > 0:
        findings.append(
            f"DISTRICT_CODE_COLLISION groups={nk.district_code_duplicate_group_count} "
            f"examples={nk.district_code_duplicate_examples[:5]}"
        )
    if nk.mahalla_stir_duplicate_group_count > 0:
        findings.append(
            f"MAHALLA_STIR_COLLISION groups={nk.mahalla_stir_duplicate_group_count} "
            f"examples={nk.mahalla_stir_duplicate_examples[:5]}"
        )
    if nk.mahalla_composite_key_duplicate_group_count > 0:
        findings.append(
            "MAHALLA_COMPOSITE_KEY_COLLISION groups="
            f"{nk.mahalla_composite_key_duplicate_group_count} "
            f"examples={nk.mahalla_composite_key_duplicate_examples[:5]} "
            "(region_code, district_code, stir not unique)"
        )
    return findings


# ----- writers -----


def write_json(report: NumericProfileReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out_path = out_dir / f"numeric_profile_{stamp}.json"
    out_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return out_path


def write_markdown(report: NumericProfileReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out_path = out_dir / f"numeric_profile_{stamp}.md"
    out_path.write_text(_render_markdown(report), encoding="utf-8")
    return out_path


def _render_markdown(r: NumericProfileReport) -> str:
    out: list[str] = []
    out.append("# Numeric profile (Phase 2B2)")
    out.append("")
    out.append(f"- Run at: {r.run_at}")
    out.append(f"- Source dir: `{r.source_dir}`")
    out.append(f"- Source files: {len(r.source_files)}")
    out.append("- Entity counts: " + ", ".join(f"{k}={v}" for k, v in r.entity_counts.items()))
    out.append("")

    out.append("## Executive summary")
    out.append("")
    out.append(f"- KPI key profiles: {len(r.kpi_profiles)}")
    out.append(f"- Macro indicator profiles: {len(r.macro_indicator_profiles)}")
    out.append(f"- Peer factor profiles: {len(r.peer_factor_profiles)}")
    out.append(f"- Detail field profiles: {len(r.detail_field_profiles)}")
    out.append(f"- High-risk findings: {len(r.high_risk_findings)}")
    out.append("")

    out.append("## Highest-risk findings")
    out.append("")
    if r.high_risk_findings:
        for f in r.high_risk_findings:
            out.append(f"- {f}")
    else:
        out.append("_No high-risk findings._")
    out.append("")

    out.append("## Base KPI completeness")
    out.append("")
    out.append("| Level | " + " | ".join(EXPECTED_BASE_KPI_KEYS) + " |")
    out.append("|---|" + "|".join("---" for _ in EXPECTED_BASE_KPI_KEYS) + "|")
    for level, cov in r.base_kpi_coverage.items():
        out.append(
            f"| {level} | "
            + " | ".join("yes" if cov[k] else "**MISSING**" for k in EXPECTED_BASE_KPI_KEYS)
            + " |"
        )
    out.append("")

    out.append("## KPI value stats by level/key")
    out.append("")
    out.append(
        "| Level | KPI key | Rows | Missing entities | Null % | Min | p01 | Median | p99 | Max | Bad examples |"
    )
    out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for kp in r.kpi_profiles:
        s = kp.value_stats
        bad = ", ".join(repr(e) for e in s.bad_value_examples[:3]) or "-"
        out.append(
            f"| {kp.level} | `{kp.kpi_key}` | {kp.row_count} | "
            f"{kp.missing_entity_count}/{kp.expected_entity_count} | "
            f"{s.null_percent} | {_fmt(s.min)} | {_fmt(s.p01)} | {_fmt(s.median)} | "
            f"{_fmt(s.p99)} | {_fmt(s.max)} | {bad} |"
        )
    out.append("")

    out.append("## Macro indicator completeness + value stats")
    out.append("")
    out.append(
        "| Indicator key | District rows | Missing district rows | Total points | Highlighted | Highlighted missing | Highlighted null | All values null % | Highlighted median | Units |"
    )
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for mp in r.macro_indicator_profiles:
        units = ", ".join(mp.distinct_units) or "-"
        out.append(
            f"| `{mp.indicator_key}` | "
            f"{mp.district_row_count}/{mp.expected_district_count} | "
            f"{mp.missing_district_count} | {mp.total_points} | {mp.highlighted_count} | "
            f"{mp.highlighted_missing_count} | {mp.highlighted_value_null_count} | "
            f"{mp.all_point_value_stats.null_percent} | "
            f"{_fmt(mp.highlighted_value_stats.median)} | {units} |"
        )
    out.append("")

    out.append("## Natural-key diagnostics")
    out.append("")
    nk = r.natural_key_diagnostics
    out.append("| Key | Unique values | Duplicate groups | Examples |")
    out.append("|---|---:|---:|---|")
    out.append(
        f"| region_code | {nk.region_code_unique_count} | "
        f"{nk.region_code_duplicate_group_count} | "
        f"{nk.region_code_duplicate_examples[:5]} |"
    )
    out.append(
        f"| district_code | {nk.district_code_unique_count} | "
        f"{nk.district_code_duplicate_group_count} | "
        f"{nk.district_code_duplicate_examples[:5]} |"
    )
    out.append(
        f"| mahalla_stir | {nk.mahalla_stir_unique_count} | "
        f"{nk.mahalla_stir_duplicate_group_count} | "
        f"{nk.mahalla_stir_duplicate_examples[:5]} |"
    )
    out.append(
        f"| (region_code, district_code, stir) | "
        f"{nk.mahalla_composite_key_unique_count} | "
        f"{nk.mahalla_composite_key_duplicate_group_count} | "
        f"{nk.mahalla_composite_key_duplicate_examples[:3]} |"
    )
    out.append("")
    out.append(
        "Completeness counts above use stable source row identities, not these "
        "natural keys. A non-zero duplicate-group count means the natural key "
        "alone is unsafe for primary-key use; it does NOT mean rows are missing."
    )
    out.append("")

    out.append("## Peer factor stats")
    out.append("")
    out.append(
        "| Polarity | Factor key | Rows | this_value null % | district_avg null % | percentile null % | rank>count | pct out-of-range |"
    )
    out.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for pp in r.peer_factor_profiles:
        out.append(
            f"| {pp.polarity} | `{pp.factor_key}` | {pp.row_count} | "
            f"{pp.this_value_stats.null_percent} | {pp.district_avg_stats.null_percent} | "
            f"{pp.percentile_stats.null_percent} | {pp.rank_exceeds_count} | "
            f"{pp.percentile_out_of_range} |"
        )
    out.append("")

    out.append("## Mahalla detail numeric fields")
    out.append("")
    out.append(
        "| Group | Column | Total | Null % | Min | p01 | Median | p99 | Max | Negatives | Zeros | Bad |"
    )
    out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for dp in r.detail_field_profiles:
        s = dp.value_stats
        bad = ", ".join(repr(e) for e in s.bad_value_examples[:3]) or "-"
        out.append(
            f"| {dp.group} | `{dp.column_name}` | {s.total} | {s.null_percent} | "
            f"{_fmt(s.min)} | {_fmt(s.p01)} | {_fmt(s.median)} | {_fmt(s.p99)} | "
            f"{_fmt(s.max)} | {s.negative_count} | {s.zero_count} | {bad} |"
        )
    out.append("")

    out.append("## Observed null-free numeric fields")
    out.append("")
    if r.null_free_numeric_fields:
        out.append(
            "These fields had null_percent = 0.0 in the observed source. The "
            "serving schema may still choose nullable for raw-import tolerance, "
            "but these are candidates for stricter NOT NULL on derived/curated "
            "tables."
        )
        out.append("")
        for f in r.null_free_numeric_fields:
            out.append(f"- `{f}`")
    else:
        out.append("_No fully null-free numeric fields observed._")
    out.append("")

    out.append("## Recommended schema cautions")
    out.append("")
    out.append(
        "- **Use surrogate primary keys plus source lineage** "
        "(file_name + district_index + mahalla_index). Natural keys (region_code, "
        "district_code, mahalla_stir) are NOT unique in source and must not be "
        "primary keys on their own. See natural-key diagnostics."
    )
    out.append(
        "- **Treat KPI/detail columns as nullable in raw-import tables** "
        "(serving views may add NOT NULL where the profile shows null_percent = 0). "
        "Specific null-free fields are listed in the previous section."
    )
    out.append(
        "- **Treat KPIs with bad_value_examples as TEXT** (or quarantine non-numeric "
        "rows). On real source no bad values are observed, so a numeric type is safe."
    )
    out.append(
        "- **Macro indicator rows exist for every district row**, but the "
        "**highlighted (current-district) point may be missing**. Semantic views "
        "must LEFT JOIN (or otherwise nullable-join) the highlighted macro value "
        "onto districts, not the indicator row itself. The answer layer must "
        "explain a missing highlighted value rather than dropping the district "
        "from results."
    )
    out.append(
        "- **Range-check at view layer**, not at column constraint level (extreme "
        "values such as 32170 km of road exist in source)."
    )
    out.append("")

    return "\n".join(out)


def _fmt(v: float | None) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


# Re-exports for type checkers / future use
__all__ = [
    "Collected",
    "KpiAccumulator",
    "MacroAccumulator",
    "NumericStats",
    "PeerAccumulator",
    "ValueBag",
    "run_numeric_profile",
    "write_json",
    "write_markdown",
]
