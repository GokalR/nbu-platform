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
    message_ru:  human-readable explanation in the requested `lang`
                 (field name retained for backward compat with old plans
                 in DB; the content is whatever language was requested)
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
    lang: str = "ru",
) -> list[dict[str, Any]]:
    """Run every check; return the list of flags raised.

    `lang` selects the language for human-readable `message_ru` strings.
    Defaults to Russian for backward compat with callers that haven't
    been updated.
    """
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
        result = check(inputs=inputs, baseline=baseline, benchmark=benchmark, lang=lang)
        if result is not None:
            flags.append(result)
    return flags


# ---------- individual checks ----------

def _check_revenue_per_employee(
    *, inputs: dict, baseline: dict, benchmark, lang: str
) -> dict | None:
    """#1 — Monthly revenue per employee outside the industry's plausible band."""
    headcount = (baseline.get("team") or {}).get("totalHeadcount", 0)
    revenue = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    if headcount <= 0 or revenue <= 0:
        return None
    rev_per_emp = revenue / headcount
    lo, hi = benchmark.rev_per_employee
    if lo <= rev_per_emp <= hi:
        return None
    severity = "high" if (rev_per_emp > hi * 2 or rev_per_emp < lo * 0.5) else "medium"
    industry_label = benchmark.label(lang)
    msg = _T[lang]["rev_per_employee"].format(
        value=_fmt(rev_per_emp), industry=industry_label,
        lo=_fmt(lo), hi=_fmt(hi),
    )
    return {
        "code": "revenue_per_employee_outside_band",
        "severity": severity,
        "message_ru": msg,
        "value": f"{_fmt(rev_per_emp)} UZS",
        "expected": f"{_fmt(lo)}–{_fmt(hi)} UZS",
    }


def _check_margin_too_high(
    *, inputs: dict, baseline: dict, benchmark, lang: str
) -> dict | None:
    """#2 — EBITDA margin more than 2× the industry median."""
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
    industry_label = benchmark.label(lang)
    msg = _T[lang]["margin_above_industry"].format(
        margin=f"{margin:.1f}",
        industry=industry_label,
        median=f"{benchmark.ebitda_margin_median:.0f}",
    )
    return {
        "code": "margin_above_industry",
        "severity": "high",
        "message_ru": msg,
        "value": f"{margin:.1f}%",
        "expected": f"≤{benchmark.ebitda_margin_median * 2:.0f}%",
    }


def _check_loan_to_revenue(
    *, inputs: dict, baseline: dict, benchmark, lang: str
) -> dict | None:
    """#3 — Loan amount > 1.5× annual revenue."""
    project = inputs.get("project") or {}
    loan = float(project.get("loanAmount") or 0)
    revenue = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    annual_revenue = revenue * 12
    if loan <= 0 or annual_revenue <= 0:
        return None
    ratio = loan / annual_revenue
    if ratio <= 1.5:
        return None
    msg = _T[lang]["loan_to_revenue_high"].format(
        loan=_fmt(loan), ratio=f"{ratio:.2f}",
    )
    return {
        "code": "loan_to_revenue_high",
        "severity": "medium",
        "message_ru": msg,
        "value": f"{ratio:.2f}x",
        "expected": "≤1.5x",
    }


def _check_salary_outliers(
    *, inputs: dict, baseline: dict, benchmark, lang: str
) -> dict | None:
    """#4 — Any team-row salary outside ±50% of the industry's salary band."""
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
    industry_label = benchmark.label(lang)
    listing = "; ".join(outliers[:3]) + ("; …" if len(outliers) > 3 else "")
    msg = _T[lang]["salary_outliers"].format(
        industry=industry_label, lo=_fmt(lo), hi=_fmt(hi), listing=listing,
    )
    return {
        "code": "salary_outliers",
        "severity": "medium",
        "message_ru": msg,
        "value": "; ".join(outliers[:3]),
        "expected": f"{_fmt(int(lo_band))}–{_fmt(int(hi_band))} UZS",
    }


# ---------- translation table ----------

_T = {
    "ru": {
        "rev_per_employee": (
            "Выручка на сотрудника {value} UZS/мес — вне типичного диапазона "
            "для отрасли «{industry}» ({lo}–{hi} UZS)."
        ),
        "margin_above_industry": (
            "EBITDA маржа {margin}% более чем вдвое превышает медиану отрасли "
            "«{industry}» ({median}%). Проверьте реалистичность объёмов "
            "продаж и цен."
        ),
        "loan_to_revenue_high": (
            "Кредит {loan} UZS превышает годовую выручку в {ratio} раза. "
            "Сроки окупаемости и обслуживания могут быть недооценены."
        ),
        "salary_outliers": (
            "Оклады вне рыночного диапазона для отрасли «{industry}» "
            "({lo}–{hi} UZS): {listing}."
        ),
    },
    "uz": {
        "rev_per_employee": (
            "Xodimga toʻgʻri keladigan daromad {value} UZS/oy — «{industry}» "
            "sohasi uchun tipik diapazondan tashqarida ({lo}–{hi} UZS)."
        ),
        "margin_above_industry": (
            "EBITDA marjasi {margin}% «{industry}» sohasining medianasini "
            "({median}%) ikki barobardan koʻpga oshirib yuboradi. Sotuv "
            "hajmlari va narxlarning realligini tekshiring."
        ),
        "loan_to_revenue_high": (
            "Kredit {loan} UZS yillik daromaddan {ratio} barobar koʻproq. "
            "Qaytarilish va xizmat qilish muddatlari kam baholangan boʻlishi mumkin."
        ),
        "salary_outliers": (
            "Ish haqlari «{industry}» sohasi uchun bozor diapazonidan "
            "tashqarida ({lo}–{hi} UZS): {listing}."
        ),
    },
}


def _fmt(n: float | int) -> str:
    return f"{int(n):,}".replace(",", " ")
