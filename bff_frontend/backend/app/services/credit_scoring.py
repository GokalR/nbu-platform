"""Pseudo credit scoring for SME applicants based on parsed Forms №1 and №2.

Computes 8 standard SME ratios, scores each as poor/ok/good (0/1/2 points),
sums the points and bins into a verdict: low / medium / high.

This is a pseudo-score for the platform UX — it surfaces obvious red flags
to the user before they walk into the bank, and gives the LLM useful
context for picking a credit product. It is NOT a replacement for the
bank's actual underwriting.
"""
from __future__ import annotations

from typing import Any


def _safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b


def _bin(value: float, poor_below: float, good_above: float) -> int:
    """0 = poor, 1 = ok, 2 = good. Higher is better."""
    if value < poor_below:
        return 0
    if value >= good_above:
        return 2
    return 1


def _bin_lower_better(value: float, good_below: float, poor_above: float) -> int:
    """0 = poor, 1 = ok, 2 = good. Lower is better (e.g. debt ratio)."""
    if value > poor_above:
        return 0
    if value <= good_below:
        return 2
    return 1


def compute_score(
    balance: dict,
    pnl: dict,
    baseline: dict | None = None,
    inputs: dict | None = None,
) -> dict[str, Any]:
    """Composite credit verdict combining:
      • 8 ratios from historical financials (Form №1 + Form №2)
      • 3 project-vs-history ratios when baseline+inputs are provided:
          - loanToRevenue: new loan size / current annual revenue
          - dscr: historical operating profit / new annual debt service
          - projectEquity: own contribution / total project value

    Returns:
      ratios: {<name>: {value, unit, benchmark, score, group}}
      points / maxPoints / percent / verdict ('low'|'medium'|'high')
      summary: 1-line natural language
    """
    revenue = pnl.get("revenue", 0)
    cogs = pnl.get("cogs", 0)
    gross_profit = revenue - cogs
    operating_profit = pnl.get("operatingProfit", 0)
    net_profit = pnl.get("netProfit", 0)

    total_assets = balance.get("totalAssets", 0)
    current_assets = balance.get("currentAssets", 0)
    inventory = balance.get("inventory", 0)
    current_liabilities = balance.get("currentLiabilities", 0)
    total_liabilities = balance.get("totalLiabilities", 0)
    equity = balance.get("equity", 0)

    # ---------- Historical ratios (group: 'historical') ----------
    gross_margin = _safe_div(gross_profit, revenue) * 100
    operating_margin = _safe_div(operating_profit, revenue) * 100
    net_margin = _safe_div(net_profit, revenue) * 100
    roa = _safe_div(net_profit, total_assets) * 100
    current_ratio = _safe_div(current_assets, current_liabilities)
    quick_ratio = _safe_div(current_assets - inventory, current_liabilities)
    debt_to_equity = _safe_div(total_liabilities, equity)
    asset_turnover = _safe_div(revenue, total_assets)

    ratios: dict[str, dict[str, Any]] = {
        "grossMargin": {
            "value": round(gross_margin, 1), "unit": "%", "group": "historical",
            "benchmark": "≥30% хорошо, 15–30% средне, <15% слабо",
            "score": _bin(gross_margin, 15, 30),
        },
        "operatingMargin": {
            "value": round(operating_margin, 1), "unit": "%", "group": "historical",
            "benchmark": "≥10% хорошо, 3–10% средне, <3% слабо",
            "score": _bin(operating_margin, 3, 10),
        },
        "netMargin": {
            "value": round(net_margin, 1), "unit": "%", "group": "historical",
            "benchmark": "≥7% хорошо, 1–7% средне, <1% слабо",
            "score": _bin(net_margin, 1, 7),
        },
        "roa": {
            "value": round(roa, 1), "unit": "%", "group": "historical",
            "benchmark": "≥8% хорошо, 2–8% средне, <2% слабо",
            "score": _bin(roa, 2, 8),
        },
        "currentRatio": {
            "value": round(current_ratio, 2), "unit": "x", "group": "historical",
            "benchmark": "≥1.5 хорошо, 1.0–1.5 средне, <1.0 слабо",
            "score": _bin(current_ratio, 1.0, 1.5),
        },
        "quickRatio": {
            "value": round(quick_ratio, 2), "unit": "x", "group": "historical",
            "benchmark": "≥1.0 хорошо, 0.6–1.0 средне, <0.6 слабо",
            "score": _bin(quick_ratio, 0.6, 1.0),
        },
        "debtToEquity": {
            "value": round(debt_to_equity, 2), "unit": "x", "group": "historical",
            "benchmark": "≤1.0 хорошо, 1.0–2.0 средне, >2.0 слабо",
            "score": _bin_lower_better(debt_to_equity, 1.0, 2.0),
        },
        "assetTurnover": {
            "value": round(asset_turnover, 2), "unit": "x", "group": "historical",
            "benchmark": "≥1.0 хорошо, 0.5–1.0 средне, <0.5 слабо",
            "score": _bin(asset_turnover, 0.5, 1.0),
        },
    }

    # ---------- Combined project-vs-history ratios (group: 'project') ----------
    if baseline and inputs:
        project = inputs.get("project") or {}
        loan_amount = float(project.get("loanAmount") or 0)
        own_contribution = float(project.get("ownContribution") or 0)
        total_value = float(project.get("totalValue") or 0) or (loan_amount + own_contribution)

        annual_loan_payment = (baseline.get("loan", {}).get("avgMonthlyPaymentFirst12m", 0) or 0) * 12

        # Loan-to-revenue: how big is the new loan compared to last year's sales?
        # Use a sentinel large number when historical revenue is 0 so the ratio
        # doesn't silently become 0 (which would falsely look "good").
        loan_to_rev = _safe_div(loan_amount, revenue) if revenue else 99.0
        ratios["loanToRevenue"] = {
            "value": round(loan_to_rev, 2), "unit": "x", "group": "project",
            "benchmark": "≤0.3 хорошо, 0.3–0.7 средне, >0.7 слабо",
            "score": _bin_lower_better(loan_to_rev, 0.3, 0.7),
        }

        # DSCR (Debt Service Coverage Ratio): can historical earnings cover
        # the new loan payment?
        dscr = _safe_div(operating_profit, annual_loan_payment) if annual_loan_payment else 0.0
        ratios["dscr"] = {
            "value": round(dscr, 2), "unit": "x", "group": "project",
            "benchmark": "≥1.3 хорошо, 1.0–1.3 средне, <1.0 слабо",
            "score": _bin(dscr, 1.0, 1.3),
        }

        # Skin in the game: how much of the project is financed from own funds?
        equity_pct = (_safe_div(own_contribution, total_value) * 100) if total_value else 0.0
        ratios["projectEquity"] = {
            "value": round(equity_pct, 1), "unit": "%", "group": "project",
            "benchmark": "≥30% хорошо, 15–30% средне, <15% слабо",
            "score": _bin(equity_pct, 15, 30),
        }

    points = sum(r["score"] for r in ratios.values())
    max_points = len(ratios) * 2

    pct = points / max_points if max_points else 0
    if pct >= 0.75:
        verdict = "high"
    elif pct >= 0.45:
        verdict = "medium"
    else:
        verdict = "low"

    # Edge case: empty reporting.
    if revenue == 0 and total_assets == 0:
        verdict = "low"
        summary = "Отчётность пустая: выручка и активы = 0. Скоринг невозможен — для оценки нужны фактические данные за отчётный период."
    else:
        summary = _build_summary(verdict, ratios, points, max_points)

    return {
        "ratios": ratios,
        "points": points,
        "maxPoints": max_points,
        "percent": round(pct * 100, 1),
        "verdict": verdict,
        "summary": summary,
    }


def _build_summary(verdict: str, ratios: dict, points: int, max_points: int) -> str:
    weak = [k for k, v in ratios.items() if v["score"] == 0]
    strong = [k for k, v in ratios.items() if v["score"] == 2]

    if verdict == "high":
        return (
            f"Высокая кредитоспособность ({points}/{max_points}). "
            f"Сильные показатели: {', '.join(_pretty(s) for s in strong[:3])}. "
            f"Заявка имеет высокие шансы на одобрение."
        )
    if verdict == "medium":
        weak_str = (
            f" Слабые места: {', '.join(_pretty(w) for w in weak[:3])}." if weak else ""
        )
        return (
            f"Средняя кредитоспособность ({points}/{max_points}).{weak_str} "
            f"Заявка реалистична, но банк может запросить дополнительные обеспечения или гарантии."
        )
    return (
        f"Низкая кредитоспособность ({points}/{max_points}). "
        f"Слабые показатели: {', '.join(_pretty(w) for w in weak[:3]) or 'недостаточно данных'}. "
        f"Перед обращением в банк рекомендуется улучшить ликвидность или сократить долговую нагрузку."
    )


_PRETTY = {
    "grossMargin": "валовая маржа",
    "operatingMargin": "операционная маржа",
    "netMargin": "чистая маржа",
    "roa": "ROA",
    "currentRatio": "текущая ликвидность",
    "quickRatio": "быстрая ликвидность",
    "debtToEquity": "долг/капитал",
    "assetTurnover": "оборачиваемость активов",
    "loanToRevenue": "кредит/выручка",
    "dscr": "покрытие платежей (DSCR)",
    "projectEquity": "доля собственных в проекте",
    "costToRevenue": "расходы/выручка",
    "paybackYears": "срок окупаемости",
    "businessAge": "возраст бизнеса",
}


# ============================================================================
# Wizard-only scoring (no Excel) — used in current product flow.
# ============================================================================

def compute_wizard_score(inputs: dict, baseline: dict) -> dict[str, Any]:
    """Pseudo credit verdict computed purely from the wizard inputs +
    deterministic baseline. No historical statements required.

    8 ratios across 4 groups, max 16 points. Bins:
      ≥75% = high, ≥45% = medium, otherwise low.
    """
    project = inputs.get("project") or {}
    organization = inputs.get("organization") or {}

    monthly_revenue = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    annual_revenue = monthly_revenue * 12

    # Operating costs = payroll + utilities + free-form extras (rent / materials / …)
    payroll = (baseline.get("team") or {}).get("monthlyPayroll", 0)
    util = (baseline.get("utilities") or {}).get("total", 0)
    extras_total = (baseline.get("extras") or {}).get("total", 0)
    monthly_op_costs = payroll + util + extras_total

    avg_loan_pmt = (baseline.get("loan") or {}).get("avgMonthlyPaymentFirst12m", 0)
    annual_loan_payment = avg_loan_pmt * 12

    monthly_total_costs = monthly_op_costs + avg_loan_pmt
    monthly_op_profit = monthly_revenue - monthly_op_costs
    monthly_net_profit = monthly_revenue - monthly_total_costs

    loan_amount = float(project.get("loanAmount") or 0)
    own_contribution = float(project.get("ownContribution") or 0)
    total_value = float(project.get("totalValue") or 0) or (loan_amount + own_contribution)

    # ---------- Ratios ----------
    # 1. Operating margin (before loan service)
    op_margin = _safe_div(monthly_op_profit, monthly_revenue) * 100

    # 2. Net margin (after loan service)
    net_margin = _safe_div(monthly_net_profit, monthly_revenue) * 100

    # 3. Cost-to-revenue (lower better)
    cost_ratio = _safe_div(monthly_total_costs, monthly_revenue) * 100

    # 4. Project equity ratio
    equity_pct = _safe_div(own_contribution, total_value) * 100

    # 5. Loan-to-annual-revenue (lower better)
    loan_to_rev = _safe_div(loan_amount, annual_revenue) if annual_revenue else 99.0

    # 6. DSCR (debt service coverage)
    dscr = _safe_div(monthly_op_profit * 12, annual_loan_payment) if annual_loan_payment else 0.0

    # 7. Payback period (years) — lower better
    annual_net_profit = monthly_net_profit * 12
    payback_years = _safe_div(loan_amount, annual_net_profit) if annual_net_profit > 0 else 99.0

    # 8. Business age in years (from foundedDate)
    business_age_years = _years_since(organization.get("foundedDate"))

    ratios: dict[str, dict[str, Any]] = {
        "operatingMargin": {
            "value": round(op_margin, 1), "unit": "%", "group": "profitability",
            "benchmark": "≥15% хорошо, 5–15% средне, <5% слабо",
            "score": _bin(op_margin, 5, 15),
        },
        "netMargin": {
            "value": round(net_margin, 1), "unit": "%", "group": "profitability",
            "benchmark": "≥7% хорошо, 1–7% средне, <1% слабо",
            "score": _bin(net_margin, 1, 7),
        },
        "costToRevenue": {
            "value": round(cost_ratio, 1), "unit": "%", "group": "efficiency",
            "benchmark": "≤70% хорошо, 70–90% средне, >90% слабо",
            "score": _bin_lower_better(cost_ratio, 70, 90),
        },
        "projectEquity": {
            "value": round(equity_pct, 1), "unit": "%", "group": "structure",
            "benchmark": "≥30% хорошо, 15–30% средне, <15% слабо",
            "score": _bin(equity_pct, 15, 30),
        },
        "loanToRevenue": {
            "value": round(loan_to_rev, 2), "unit": "x", "group": "structure",
            "benchmark": "≤0.5 хорошо, 0.5–1.5 средне, >1.5 слабо",
            "score": _bin_lower_better(loan_to_rev, 0.5, 1.5),
        },
        "dscr": {
            "value": round(dscr, 2), "unit": "x", "group": "debtCapacity",
            "benchmark": "≥1.3 хорошо, 1.0–1.3 средне, <1.0 слабо",
            "score": _bin(dscr, 1.0, 1.3),
        },
        "paybackYears": {
            "value": round(payback_years, 1), "unit": "лет", "group": "debtCapacity",
            "benchmark": "≤3 года хорошо, 3–7 лет средне, >7 слабо",
            "score": _bin_lower_better(payback_years, 3, 7),
        },
        "businessAge": {
            "value": round(business_age_years, 1), "unit": "лет", "group": "trackRecord",
            "benchmark": "≥3 года хорошо, 1–3 года средне, <1 года слабо",
            "score": _bin(business_age_years, 1, 3),
        },
    }

    points = sum(r["score"] for r in ratios.values())
    max_points = len(ratios) * 2

    pct = points / max_points if max_points else 0
    if pct >= 0.75:
        verdict = "high"
    elif pct >= 0.45:
        verdict = "medium"
    else:
        verdict = "low"

    # Edge case: revenue = 0 → all profitability ratios are 0, verdict
    # would be "low" but for the wrong reason. Flag explicitly.
    if monthly_revenue == 0:
        verdict = "low"
        summary = (
            "Скоринг невозможен: проектная выручка равна нулю. "
            "Заполните раздел «Продукт/Услуга» в анкете."
        )
    else:
        summary = _build_summary(verdict, ratios, points, max_points)

    return {
        "ratios": ratios,
        "points": points,
        "maxPoints": max_points,
        "percent": round(pct * 100, 1),
        "verdict": verdict,
        "summary": summary,
    }


def _years_since(date_str: str | None) -> float:
    """Years between foundedDate (ISO string YYYY-MM-DD) and now."""
    if not date_str:
        return 0.0
    from datetime import date
    try:
        y, m, d = (int(x) for x in date_str.split("-")[:3])
        founded = date(y, m, d)
    except (ValueError, AttributeError):
        return 0.0
    today = date.today()
    return (today - founded).days / 365.25


def _pretty(k: str) -> str:
    return _PRETTY.get(k, k)
