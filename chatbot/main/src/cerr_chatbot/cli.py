"""CLI for cerr-chatbot.

Subcommands:
  sources    List discovered cerr_region_*.json files.
  config     Print resolved (non-secret) settings.
  audit      Run Phase 2A critical source audit.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from cerr_chatbot import __version__
from cerr_chatbot.audit import run_audit, write_report
from cerr_chatbot.config import get_settings
from cerr_chatbot.numeric_profile import run_numeric_profile
from cerr_chatbot.numeric_profile import write_json as write_numeric_json
from cerr_chatbot.numeric_profile import write_markdown as write_numeric_md
from cerr_chatbot.profile import run_profile, write_json, write_markdown
from cerr_chatbot.sources import discover_region_files

# Heavy DB import deferred so non-DB CLI commands don't pay the cost.
if TYPE_CHECKING:
    from cerr_chatbot.query import Pipeline


def _cmd_sources(_args: argparse.Namespace) -> int:
    try:
        files = discover_region_files()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not files:
        print("No cerr_region_*.json files found.")
        return 1
    total = sum(f.size_bytes for f in files)
    print(f"Found {len(files)} region files ({total / 1_048_576:.1f} MiB total):")
    for f in files:
        print(f"  region_id={f.region_id:<6} {f.size_bytes / 1_048_576:7.1f} MiB  {f.path}")
    return 0


def _cmd_config(_args: argparse.Namespace) -> int:
    s = get_settings()
    print(f"app_env          = {s.app_env}")
    print(f"log_level        = {s.log_level}")
    print(f"cerr_source_dir  = {s.cerr_source_dir}")
    print(f"postgres_host    = {s.postgres_host}")
    print(f"postgres_port    = {s.postgres_port}")
    print(f"postgres_db      = {s.postgres_db}")
    print(f"postgres_user    = {s.postgres_user}")
    print(f"llm_provider     = {s.llm_provider}")
    print(f"llm_model        = {s.llm_model}")
    print(f"query_pipeline   = {s.query_pipeline_mode}")
    print(f"query_memory     = {s.query_memory_mode}")
    print(f"answer_narrator  = {s.answer_narrator_mode}")
    print(f"anthropic_api_key set = {bool(s.anthropic_api_key)}")
    print(f"openai_api_key set    = {bool(s.openai_api_key)}")
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    try:
        report = run_audit()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    out_path = write_report(report, args.out_dir)

    print("=== Source audit (Phase 2A) ===")
    print(f"source_dir : {report.source_dir}")
    print(f"run_at     : {report.run_at}")
    print(
        f"files      : actual={report.actual.region_files} expected={report.expected.region_files}"
    )
    print(f"regions    : actual={report.actual.regions} expected={report.expected.regions}")
    print(f"districts  : actual={report.actual.districts} expected={report.expected.districts}")
    print(f"mahallas   : actual={report.actual.mahallas} expected={report.expected.mahallas}")
    print(
        f"issues     : critical={report.issue_counts.get('critical', 0)} "
        f"warning={report.issue_counts.get('warning', 0)} "
        f"info={report.issue_counts.get('info', 0)}"
    )
    if report.issues:
        print("--- first 10 issues ---")
        for i in report.issues[:10]:
            loc = []
            if i.region_code is not None:
                loc.append(f"region={i.region_code}")
            if i.district_code is not None:
                loc.append(f"district={i.district_code}")
            if i.stir is not None:
                loc.append(f"stir={i.stir}")
            loc_s = " ".join(loc)
            print(f"  [{i.severity:<8}] {i.code}: {i.message} {loc_s}".rstrip())
        if len(report.issues) > 10:
            print(f"  ... and {len(report.issues) - 10} more (see report)")
    print(f"report     : {out_path}")
    return 1 if report.has_critical else 0


def _cmd_profile(args: argparse.Namespace) -> int:
    try:
        report = run_profile()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    json_path = write_json(report, args.out_dir)
    md_path = write_markdown(report, args.out_dir)

    print("=== Source profile (Phase 2B1) ===")
    print(f"source_dir       : {report.source_dir}")
    print(f"run_at           : {report.run_at}")
    print(
        f"entities         : files={report.entity_counts.region_files} "
        f"regions={report.entity_counts.regions} "
        f"districts={report.entity_counts.districts} "
        f"mahallas={report.entity_counts.mahallas}"
    )
    cov = report.catalog_coverage
    print(
        "catalog coverage : "
        f"observed={cov['observed_paths']} "
        f"cataloged_seen={cov['cataloged_observed']} "
        f"ignored_seen={cov['ignored_observed']} "
        f"important_uncataloged={cov['important_uncataloged']} "
        f"cataloged_unseen={cov['cataloged_unseen']}"
    )
    print(f"json report      : {json_path}")
    print(f"md report        : {md_path}")
    return 0


def _cmd_numeric_profile(args: argparse.Namespace) -> int:
    try:
        report = run_numeric_profile()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    json_path = write_numeric_json(report, args.out_dir)
    md_path = write_numeric_md(report, args.out_dir)

    print("=== Numeric profile (Phase 2B2) ===")
    print(f"source_dir       : {report.source_dir}")
    print(f"run_at           : {report.run_at}")
    print("entities         : " + ", ".join(f"{k}={v}" for k, v in report.entity_counts.items()))
    print(
        f"profiles         : kpi={len(report.kpi_profiles)} "
        f"macro={len(report.macro_indicator_profiles)} "
        f"peer={len(report.peer_factor_profiles)} "
        f"detail={len(report.detail_field_profiles)}"
    )
    print(f"high-risk        : {len(report.high_risk_findings)}")
    if report.high_risk_findings:
        print("--- first 10 findings ---")
        for f in report.high_risk_findings[:10]:
            print(f"  {f}")
        if len(report.high_risk_findings) > 10:
            print(f"  ... and {len(report.high_risk_findings) - 10} more (see report)")
    print(f"json report      : {json_path}")
    print(f"md report        : {md_path}")
    return 0


def _cmd_import_json(_args: argparse.Namespace) -> int:
    from cerr_chatbot.db.session import make_engine
    from cerr_chatbot.importer import run_import

    engine = make_engine()
    try:
        summary = run_import(engine)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: import failed: {exc}", file=sys.stderr)
        return 1

    print("=== JSON import (Phase 4A) ===")
    print(f"import_run_id : {summary.import_run_id}")
    print(f"status        : {summary.status}")
    print(f"files         : {summary.files}")
    print(f"regions       : {summary.regions}")
    print(f"districts     : {summary.districts}")
    print(f"mahallas      : {summary.mahallas}")
    print(f"entity_kpis   : {summary.entity_kpis}")
    print(f"macro indicators : {summary.district_macro_indicators}")
    print(f"macro points     : {summary.district_macro_points}")
    print(f"rating histogram : {summary.district_rating_histogram_rows}")
    print(f"infra rows       : {summary.mahalla_infrastructure_rows}")
    print(f"appeal rows      : {summary.mahalla_appeal_rows}")
    print(f"specialization rows : {summary.mahalla_specialization_rows}")
    print(f"crop rows        : {summary.mahalla_crop_rows}")
    print(f"subsidy program rows: {summary.mahalla_subsidy_program_rows}")
    print(f"peer factor rows : {summary.mahalla_peer_factor_rows}")
    print(f"issues total  : {summary.issues_total}")
    if summary.issues_by_severity:
        print("issues by severity:")
        for sev, n in sorted(summary.issues_by_severity.items()):
            print(f"  {sev:<10} {n}")
    if summary.issues_by_code:
        print("issues by code:")
        for code, n in sorted(summary.issues_by_code.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {n:>4}  {code}")
    return 0 if summary.status == "completed" else 1


def _build_runtime_pipeline() -> Pipeline:
    from cerr_chatbot.config import get_settings
    from cerr_chatbot.db.session import make_engine
    from cerr_chatbot.query import (
        make_evidence_planner_from_settings,
        make_pipeline_from_settings,
        make_planner_from_settings,
    )

    settings = get_settings()
    engine = make_engine()
    mode = (settings.query_pipeline_mode or "legacy").strip().lower()
    pipeline: Pipeline
    if mode == "evidence":
        ev_planner = make_evidence_planner_from_settings(settings)
        pipeline = make_pipeline_from_settings(
            engine,
            evidence_planner=ev_planner,
            settings=settings,
        )
    else:
        planner = make_planner_from_settings(settings)
        pipeline = make_pipeline_from_settings(
            engine,
            legacy_planner=planner,
            settings=settings,
        )
    return pipeline


def _cmd_eval_questions(args: argparse.Namespace) -> int:
    from cerr_chatbot.eval import (
        parse_questions_md,
        run_eval_with_pipeline,
        write_eval_json,
        write_eval_markdown,
    )

    cases = parse_questions_md(args.questions)
    if not cases:
        print(f"ERROR: no cases parsed from {args.questions}", file=sys.stderr)
        return 2

    pipeline = _build_runtime_pipeline()

    report = run_eval_with_pipeline(pipeline, cases)
    report.questions_path = str(args.questions)
    json_path = write_eval_json(report, args.out_dir)
    md_path = write_eval_markdown(report, args.out_dir)

    print("=== Eval (deterministic) ===")
    print(f"questions  : {args.questions}")
    print(f"total      : {report.total}")
    print(f"passed     : {report.passed}")
    print(f"failed     : {report.failed}")
    print(f"json report: {json_path}")
    print(f"md report  : {md_path}")
    return 0 if report.failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cerr",
        description="Regional analytics chatbot backend CLI",
    )
    p.add_argument("--version", action="version", version=f"cerr-chatbot {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("sources", help="List source region JSON files").set_defaults(func=_cmd_sources)
    sub.add_parser("config", help="Print resolved settings (no secrets)").set_defaults(
        func=_cmd_config
    )

    audit_p = sub.add_parser("audit", help="Run Phase 2A critical source audit")
    audit_p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("audit_reports"),
        help="Where to write the JSON report (default: ./audit_reports)",
    )
    audit_p.set_defaults(func=_cmd_audit)

    profile_p = sub.add_parser(
        "profile",
        help="Run Phase 2B1 JSON shape profile + future column naming catalog",
    )
    profile_p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("profile_reports"),
        help="Where to write the reports (default: ./profile_reports)",
    )
    profile_p.set_defaults(func=_cmd_profile)

    np_p = sub.add_parser(
        "numeric-profile",
        help="Run Phase 2B2 numeric profile (KPI/macro/peer/detail stats)",
    )
    np_p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("profile_reports"),
        help="Where to write the reports (default: ./profile_reports)",
    )
    np_p.set_defaults(func=_cmd_numeric_profile)

    imp_p = sub.add_parser(
        "import-json",
        help="Phase 4A: import entities + KPIs + data quality issues into PostgreSQL",
    )
    imp_p.set_defaults(func=_cmd_import_json)

    eval_p = sub.add_parser(
        "eval-questions",
        help="Run the deterministic question evaluation suite",
    )
    eval_p.add_argument(
        "--questions",
        type=Path,
        default=Path("questions_uz_latn.md"),
        help="Path to the questions markdown file (default: questions_uz_latn.md)",
    )
    eval_p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("eval_reports"),
        help="Where to write JSON and Markdown reports",
    )
    eval_p.set_defaults(func=_cmd_eval_questions)

    return p


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to cp1251 here; source data contains Cyrillic.
    # Reconfigure to UTF-8 with replacement so summaries never crash on print.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
