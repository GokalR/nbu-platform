"""Profile orchestrator. Walks each region file, joins results to the catalog,
emits JSON + Markdown reports.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.profile.catalog import (
    COLUMN_CATALOG,
    IGNORED_PATHS,
    ignored_reason,
    is_ignored,
    lookup,
)
from cerr_chatbot.profile.models import (
    EntityCounts,
    FieldProfile,
    ProfileReport,
)
from cerr_chatbot.profile.walker import Aggregator, _PathStats, walk
from cerr_chatbot.sources import discover_region_files


def run_profile(settings: Settings | None = None) -> ProfileReport:
    cfg = settings or get_settings()
    files = discover_region_files(cfg)

    source_dir_abs = (
        cfg.cerr_source_dir
        if cfg.cerr_source_dir.is_absolute()
        else (Path.cwd() / cfg.cerr_source_dir).resolve()
    )

    agg: Aggregator = {}
    counts = EntityCounts(region_files=len(files))

    for rf in files:
        with rf.path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if not isinstance(payload, dict):
            continue
        counts.regions += 1
        districts = payload.get("districts")
        if isinstance(districts, list):
            counts.districts += len(districts)
            for d in districts:
                if isinstance(d, dict):
                    mahallas = d.get("mahallas")
                    if isinstance(mahallas, list):
                        counts.mahallas += sum(1 for m in mahallas if isinstance(m, dict))
        walk(payload, "region", agg)

    field_paths = _agg_to_profiles(agg)
    coverage = _coverage_stats(agg)

    return ProfileReport(
        run_at=datetime.now(UTC).isoformat(),
        source_dir=str(source_dir_abs),
        source_files=[f.path.name for f in files],
        entity_counts=counts,
        field_paths=field_paths,
        catalog_coverage=coverage,
    )


def _agg_to_profiles(agg: Aggregator) -> list[FieldProfile]:
    profiles: list[FieldProfile] = []
    for path, stats in sorted(agg.items()):
        spec = lookup(path)
        notes: list[str] = []
        # Multi-type warnings (excluding null which is a valid co-type)
        non_null_types = sorted(t for t in stats.types if t != "null")
        if len(non_null_types) > 1:
            notes.append(f"mixed non-null types: {non_null_types}")
        ignored = is_ignored(path)
        profiles.append(
            FieldProfile(
                path=path,
                observed_types=sorted(stats.types),
                presence_count=stats.presence,
                null_count=stats.null,
                example_values=list(stats.examples),
                proposed_column_name=spec.column if spec else None,
                proposed_table_group=spec.table_group if spec else None,
                semantic_description=spec.description if spec else None,
                is_ignored=ignored,
                ignored_reason=ignored_reason(path) if ignored else None,
                notes_or_warnings=notes,
            )
        )
    return profiles


def _coverage_stats(agg: Aggregator) -> dict[str, int]:
    observed = set(agg.keys())
    cataloged = set(COLUMN_CATALOG.keys())
    ignored = set(IGNORED_PATHS.keys())
    important_uncataloged = observed - cataloged - ignored
    return {
        "observed_paths": len(observed),
        "cataloged_paths_total": len(cataloged),
        "ignored_paths_total": len(ignored),
        "cataloged_observed": len(observed & cataloged),
        "ignored_observed": len(observed & ignored),
        "important_uncataloged": len(important_uncataloged),
        "cataloged_unseen": len(cataloged - observed),
        "ignored_unseen": len(ignored - observed),
    }


def write_json(report: ProfileReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out_path = out_dir / f"profile_{stamp}.json"
    out_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return out_path


def write_markdown(report: ProfileReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out_path = out_dir / f"profile_{stamp}.md"
    out_path.write_text(_render_markdown(report), encoding="utf-8")
    return out_path


def _render_markdown(report: ProfileReport) -> str:
    lines: list[str] = []
    lines.append("# Source profile (Phase 2B1)")
    lines.append("")
    lines.append(f"- **Run at:** {report.run_at}")
    lines.append(f"- **Source dir:** `{report.source_dir}`")
    lines.append(f"- **Source files:** {len(report.source_files)}")
    lines.append("")
    lines.append("## Entity counts")
    lines.append("")
    lines.append("| Entity | Count |")
    lines.append("|---|---:|")
    lines.append(f"| region files | {report.entity_counts.region_files} |")
    lines.append(f"| regions      | {report.entity_counts.regions} |")
    lines.append(f"| districts    | {report.entity_counts.districts} |")
    lines.append(f"| mahallas     | {report.entity_counts.mahallas} |")
    lines.append("")
    lines.append("## Catalog coverage")
    lines.append("")
    for k, v in report.catalog_coverage.items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")

    lines.append("## Recommended Future Column Names")
    lines.append("")
    lines.append(
        "Grouped by future table or semantic view. Generated from observed paths "
        "joined to `catalog.py`."
    )
    lines.append("")
    grouped: dict[str, list[FieldProfile]] = {}
    important_uncataloged: list[FieldProfile] = []
    ignored: list[FieldProfile] = []
    for fp in report.field_paths:
        if fp.proposed_table_group:
            grouped.setdefault(fp.proposed_table_group, []).append(fp)
        elif fp.is_ignored:
            ignored.append(fp)
        else:
            important_uncataloged.append(fp)

    for group in sorted(grouped.keys()):
        lines.append(f"### `{group}`")
        lines.append("")
        lines.append("| Proposed column | JSON path | Types | Presence | Null | Description |")
        lines.append("|---|---|---|---:|---:|---|")
        for fp in grouped[group]:
            col = fp.proposed_column_name or "-"
            types = ",".join(fp.observed_types) or "-"
            desc = (fp.semantic_description or "").replace("|", "\\|")
            path = fp.path.replace("|", "\\|")
            lines.append(
                f"| `{col}` | `{path}` | {types} | {fp.presence_count} | {fp.null_count} | {desc} |"
            )
        lines.append("")

    lines.append("## Important uncataloged paths")
    lines.append("")
    lines.append(
        "Observed in source data, not in `COLUMN_CATALOG`, not in `IGNORED_PATHS`. "
        "Each entry is a real coverage gap that should be classified before schema "
        "design."
    )
    lines.append("")
    if important_uncataloged:
        lines.append("| Path | Types | Presence | Null | Examples |")
        lines.append("|---|---|---:|---:|---|")
        for fp in important_uncataloged:
            types = ",".join(fp.observed_types) or "-"
            ex = ", ".join(_short_repr(e) for e in fp.example_values) or "-"
            ex = ex.replace("|", "\\|")
            path = fp.path.replace("|", "\\|")
            lines.append(f"| `{path}` | {types} | {fp.presence_count} | {fp.null_count} | {ex} |")
    else:
        lines.append("_None - every observed path is either cataloged or explicitly ignored._")
    lines.append("")

    lines.append("## Ignored paths (intentionally not persisted)")
    lines.append("")
    lines.append(
        "Container objects, UI presentation payloads, and other paths declared in "
        "`IGNORED_PATHS` with a reason."
    )
    lines.append("")
    if ignored:
        lines.append("| Path | Reason |")
        lines.append("|---|---|")
        for fp in ignored:
            reason = (fp.ignored_reason or "").replace("|", "\\|")
            path = fp.path.replace("|", "\\|")
            lines.append(f"| `{path}` | {reason} |")
    lines.append("")

    lines.append("## All observed paths (raw)")
    lines.append("")
    lines.append("| Path | Types | Presence | Null | Examples |")
    lines.append("|---|---|---:|---:|---|")
    for fp in report.field_paths:
        types = ",".join(fp.observed_types) or "-"
        ex = ", ".join(_short_repr(e) for e in fp.example_values) or "-"
        ex = ex.replace("|", "\\|")
        path = fp.path.replace("|", "\\|")
        lines.append(f"| `{path}` | {types} | {fp.presence_count} | {fp.null_count} | {ex} |")
    lines.append("")
    return "\n".join(lines)


def _short_repr(v: object) -> str:
    if isinstance(v, str):
        return repr(v)
    return str(v)


# Re-export for type checkers / future use
__all__ = ["run_profile", "write_json", "write_markdown", "_PathStats"]
