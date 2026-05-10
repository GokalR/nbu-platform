"""Plausibility checks for SME credit-scoring v2.

These four checks feed criterion #4 ("Реалистичность") of the v2 score:
zero flags → 20 points, one flag → 15, two → 10, three → 5, four+ → 0.

The goal is to catch projections that look numerically fine but don't
survive a sanity check against industry norms. The classic example is
the bakery template: 28% net margin on commodity bread is implausible
even if the math checks out, and that should cost points.

Each check returns either None (passed) or a flag dict with:
    code:        stable id, e.g. "revenue_per_employee_high"
    severity:    "high" | "medium" — for UI emphasis only
    message_ru:  human-readable explanation
    value:       the offending number (formatted)
    expected:    what was expected (formatted)
"""
from __future__ import annotations

from typing import Any

from . import industry_benchmarks


def run_all_checks(
    *,
    inputs: dict[str, Any],
    baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run every check; return the list of flags raised."""
    org = inputs.get("organization") or {}
    benchmark = industry_benchmarks.classify(
        org.get("mainActivity"),
        category_hint=org.get("industryCategory"),
    )
    checks = [
        _check_revenue_per_employee,
        _check_margin_too_high,
        _check_loan_to_revenue,
        _check_salary_outliers,
    ]
    flags: list[dict[str, Any]] = []
    for check in checks:
        result = check(inputs=inputs, baseline=baseline, benchmark=benchmark)
        if result is not None:
            flags.append(result)
    return flags


# ---------- individual checks ----------

def _check_revenue_per_employee(
    *, inputs: dict, baseline: dict, benchmark
) -> dict | None:
    """#1 — Monthly revenue per employee outside the industry's plausible band.

    Catches projections where revenue is wildly disproportionate to staff:
    e.g. claiming 300M UZS/month from a 3-person team in a category where
    median is ~12M/employee. Could indicate inflated revenue OR understaffed
    operations — either way, worth flagging.
    """
    headcount = (baseline.get("team") or {}).get("totalHeadcount", 0)
    revenue = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    if headcount <= 0 or revenue <= 0:
        return None  # other checks/gates handle these
    rev_per_emp = revenue / headcount
    lo, hi = benchmark.rev_per_employee
    if lo <= rev_per_emp <= hi:
        return None
    severity = "high" if (rev_per_emp > hi * 2 or rev_per_emp < lo * 0.5) else "medium"
    return {
        "code": "revenue_per_employee_outside_band",
        "severity": severity,
        "message_ru": (
            f"Выручка на сотрудника {_fmt(rev_per_emp)} UZS/мес — вне типичного "
            f"диапазона для отрасли «{benchmark.label_ru}» "
            f"({_fmt(lo)}–{_fmt(hi)} UZS)."
        ),
        "value": f"{_fmt(rev_per_emp)} UZS",
        "expected": f"{_fmt(lo)}–{_fmt(hi)} UZS",
    }


def _check_margin_too_high(
    *, inputs: dict, baseline: dict, benchmark
) -> dict | None:
    """#2 — EBITDA margin more than 2x the industry median.

    Solves the bakery case directly: bakery industry median EBITDA ~10%,
    so 28% margin is 2.8x median → flagged. Real projections rarely
    sustain margins this far above industry norms.
    """
    revenue = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    if revenue <= 0:
        return None
    op_costs = (baseline.get("monthlyCosts") or {}).get("operating", 0)
    if op_costs == 0:
        # Fallback for older baselines that don't yet expose `operating`
        op_costs = ((baseline.get("team") or {}).get("monthlyPayroll", 0)
                    + (baseline.get("utilities") or {}).get("total", 0)
                    + (baseline.get("extras") or {}).get("total", 0)
                    + (baseline.get("taxes") or {}).get("monthlyTotal", 0))
    ebitda = revenue - op_costs
    margin = ebitda / revenue * 100
    if margin <= benchmark.ebitda_margin_median * 2:
        return None
    return {
        "code": "margin_above_industry",
        "severity": "high",
        "message_ru": (
            f"EBITDA маржа {margin:.1f}% более чем вдвое превышает медиану отрасли "
            f"«{benchmark.label_ru}» ({benchmark.ebitda_margin_median:.0f}%). "
            f"Проверьте реалистичность объёмов продаж и цен."
        ),
        "value": f"{margin:.1f}%",
        "expected": f"≤{benchmark.ebitda_margin_median * 2:.0f}%",
    }


def _check_loan_to_revenue(
    *, inputs: dict, baseline: dict, benchmark
) -> dict | None:
    """#3 — Loan amount > 1.5× annual revenue.

    A loan of this magnitude relative to projected sales is unusually
    large; either the entrepreneur is overestimating capital needs or
    underestimating revenue.
    """
    project = inputs.get("project") or {}
    loan = float(project.get("loanAmount") or 0)
    revenue = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    annual_revenue = revenue * 12
    if loan <= 0 or annual_revenue <= 0:
        return None
    ratio = loan / annual_revenue
    if ratio <= 1.5:
        return None
    return {
        "code": "loan_to_revenue_high",
        "severity": "medium",
        "message_ru": (
            f"Кредит {_fmt(loan)} UZS превышает годовую выручку в {ratio:.2f} раза. "
            f"Сроки окупаемости и обслуживания могут быть недооценены."
        ),
        "value": f"{ratio:.2f}x",
        "expected": "≤1.5x",
    }


def _check_salary_outliers(
    *, inputs: dict, baseline: dict, benchmark
) -> dict | None:
    """#4 — Any team-row salary outside ±50% of the industry's salary band.

    Off-band salaries inflate (or deflate) the cost structure unrealistically
    and distort margin / DSCR calculations.
    """
    team = inputs.get("team") or []
    lo, hi = benchmark.salary_range
    lo_band = lo * 0.5
    hi_band = hi * 1.5
    outliers: list[str] = []
    for row in team:
        sal = float(row.get("salary") or 0)
        cnt = int(row.get("count") or 0)
        role = (row.get("role") or "").strip() or "—"
        if cnt <= 0 or sal <= 0:
            continue
        if sal < lo_band or sal > hi_band:
            outliers.append(f"«{role}» {_fmt(sal)} UZS")
    if not outliers:
        return None
    return {
        "code": "salary_outliers",
        "severity": "medium",
        "message_ru": (
            f"Оклады вне рыночного диапазона для отрасли «{benchmark.label_ru}» "
            f"({_fmt(lo)}–{_fmt(hi)} UZS): {'; '.join(outliers[:3])}"
            f"{'; …' if len(outliers) > 3 else ''}."
        ),
        "value": "; ".join(outliers[:3]),
        "expected": f"{_fmt(int(lo_band))}–{_fmt(int(hi_band))} UZS",
    }


def _fmt(n: float | int) -> str:
    return f"{int(n):,}".replace(",", " ")
