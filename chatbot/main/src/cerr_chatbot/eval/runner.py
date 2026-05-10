"""Run an injected QueryService over a list of EvalCases and write reports."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cerr_chatbot.eval.parser import EvalCase
from cerr_chatbot.eval.scorer import score_case
from cerr_chatbot.eval.style import merge_style_issues, style_issues
from cerr_chatbot.query.narrator import DeterministicNarrator, Narrator
from cerr_chatbot.query.pipeline import Pipeline
from cerr_chatbot.query.service import QueryService


@dataclass
class EvalCaseResult:
    case_number: int
    title: str
    question: str
    service_kind: str
    passed: bool
    expected_answer: str
    actual_answer: str
    sql: str | None
    row_count: int
    failure_reasons: list[str] = field(default_factory=list)
    debug_notes: list[str] = field(default_factory=list)


@dataclass
class EvalReport:
    run_at: str
    questions_path: str
    total: int
    passed: int
    failed: int
    cases: list[EvalCaseResult] = field(default_factory=list)


def run_eval(
    service: QueryService,
    cases: list[EvalCase],
    *,
    narrator: Narrator | None = None,
    enforce_style: bool = False,
) -> EvalReport:
    """Run eval cases through the service+narrator and score them.

    Style issues are always recorded in `failure_reasons` (prefixed with
    `style:`) so the report surfaces them. They only flip `passed` to False
    when `enforce_style=True`, keeping the existing deterministic fact
    scorer as the default pass/fail signal.
    """
    nar = narrator or DeterministicNarrator()
    results: list[EvalCaseResult] = []
    for case in cases:
        sr = service.ask(case.question)
        ans = nar.narrate(sr)
        passed, reasons = score_case(case.expected_answer, sr.kind, ans.text)
        s_issues = style_issues(ans.text, service_kind=sr.kind, user_question=case.question)
        if s_issues:
            reasons = merge_style_issues(reasons, s_issues)
            if enforce_style:
                passed = False
        results.append(
            EvalCaseResult(
                case_number=case.case_number,
                title=case.title,
                question=case.question,
                service_kind=sr.kind,
                passed=passed,
                expected_answer=case.expected_answer,
                actual_answer=ans.text,
                sql=sr.sql,
                row_count=sr.row_count,
                failure_reasons=reasons,
                debug_notes=list(sr.debug_notes),
            )
        )
    passed_count = sum(1 for r in results if r.passed)
    return EvalReport(
        run_at=datetime.now(UTC).isoformat(),
        questions_path="",  # filled by caller if needed
        total=len(results),
        passed=passed_count,
        failed=len(results) - passed_count,
        cases=results,
    )


def run_eval_with_pipeline(
    pipeline: Pipeline,
    cases: list[EvalCase],
    *,
    enforce_style: bool = False,
) -> EvalReport:
    """Run cases through any `Pipeline` (legacy or evidence) and score them.

    Pipelines return a uniform dict so this loop does not care which one is
    in use; the eval contract (required facts + style issues) stays the same.
    """
    results: list[EvalCaseResult] = []
    for case in cases:
        # session_id=None keeps every eval case isolated: even when the
        # injected pipeline carries a memory_store, no snapshot is written
        # and no prior turn can leak into the next case's planner prompt.
        out = pipeline.answer(case.question, max_rows=10, session_id=None)
        kind = str(out.get("kind", ""))
        text = str(out.get("answer", ""))
        passed, reasons = score_case(case.expected_answer, kind, text)
        s_issues = style_issues(text, service_kind=kind, user_question=case.question)
        if s_issues:
            reasons = merge_style_issues(reasons, s_issues)
            if enforce_style:
                passed = False
        results.append(
            EvalCaseResult(
                case_number=case.case_number,
                title=case.title,
                question=case.question,
                service_kind=kind,
                passed=passed,
                expected_answer=case.expected_answer,
                actual_answer=text,
                sql=out.get("sql"),
                row_count=int(out.get("row_count") or 0),
                failure_reasons=reasons,
                debug_notes=list(out.get("debug_notes") or []),
            )
        )
    passed_count = sum(1 for r in results if r.passed)
    return EvalReport(
        run_at=datetime.now(UTC).isoformat(),
        questions_path="",
        total=len(results),
        passed=passed_count,
        failed=len(results) - passed_count,
        cases=results,
    )


def write_eval_json(report: EvalReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out = out_dir / f"eval_{stamp}.json"
    out.write_text(json.dumps(_to_jsonable(report), indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def write_eval_markdown(report: EvalReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.run_at.replace(":", "-").replace("+00:00", "Z")
    out = out_dir / f"eval_{stamp}.md"
    out.write_text(_render_md(report), encoding="utf-8")
    return out


def _to_jsonable(report: EvalReport) -> dict[str, Any]:
    return {
        "run_at": report.run_at,
        "questions_path": report.questions_path,
        "total": report.total,
        "passed": report.passed,
        "failed": report.failed,
        "cases": [
            {
                "case_number": c.case_number,
                "title": c.title,
                "question": c.question,
                "service_kind": c.service_kind,
                "passed": c.passed,
                "expected_answer": c.expected_answer,
                "actual_answer": c.actual_answer,
                "sql": c.sql,
                "row_count": c.row_count,
                "failure_reasons": c.failure_reasons,
                "debug_notes": c.debug_notes,
            }
            for c in report.cases
        ],
    }


def _render_md(report: EvalReport) -> str:
    out: list[str] = []
    out.append("# Eval report")
    out.append("")
    out.append(f"- Run at: {report.run_at}")
    out.append(f"- Questions file: `{report.questions_path or '<unspecified>'}`")
    out.append(f"- Total: {report.total}")
    out.append(f"- Passed: {report.passed}")
    out.append(f"- Failed: {report.failed}")
    out.append("")
    for c in report.cases:
        status = "PASS" if c.passed else "FAIL"
        out.append(f"## {c.case_number}. {c.title} - {status}")
        out.append("")
        out.append(f"**Service kind:** {c.service_kind}")
        out.append(f"**Row count:** {c.row_count}")
        out.append("")
        out.append(f"**Question:** {c.question}")
        out.append("")
        if c.failure_reasons:
            out.append("**Failure reasons:**")
            for r in c.failure_reasons:
                out.append(f"- {r}")
            out.append("")
        if c.sql:
            out.append("**SQL:**")
            out.append("```sql")
            out.append(c.sql)
            out.append("```")
            out.append("")
        out.append("**Expected answer:**")
        out.append("")
        out.append(c.expected_answer)
        out.append("")
        out.append("**Actual answer:**")
        out.append("")
        out.append(c.actual_answer)
        out.append("")
    return "\n".join(out)


__all__ = [
    "EvalCaseResult",
    "EvalReport",
    "run_eval",
    "run_eval_with_pipeline",
    "write_eval_json",
    "write_eval_markdown",
]
