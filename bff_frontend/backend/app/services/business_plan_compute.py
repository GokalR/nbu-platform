"""Deterministic financial baseline for the SME Business Plan tool.

LLMs do arithmetic by token-prediction and routinely drop terms when
summing 4-5 line items (e.g. ФОТ = 8×5.5M + 3×4M + 1×6M + 1×7M = 69M, but
the model often returns 56M because it sums only the first two roles).

This module computes every deterministic figure server-side from the user's
wizard inputs and injects them into the prompt as AUTHORITATIVE values.
The LLM is told "use these exactly, don't recompute". After the LLM
returns, we cross-check and override its critical fields with our values
just in case it ignored the instruction.

Tariffs match the prompt: electricity 900 UZS/kWh, gas 1800 UZS/m³,
water+канализация 5500 UZS/m³ (Uzbekistan 2025 retail SME tariffs).
"""
from __future__ import annotations

from typing import Any

ELECTRICITY_UZS_PER_KWH = 900
GAS_UZS_PER_M3 = 1800
WATER_UZS_PER_M3 = 5500


def _annuity_payment(principal: float, monthly_rate: float, months: int) -> float:
    """Standard annuity formula. Returns 0 for degenerate inputs."""
    if principal <= 0 or months <= 0:
        return 0
    if monthly_rate <= 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)


def compute_baseline(inputs: dict[str, Any]) -> dict[str, Any]:
    """Compute every deterministic figure from the wizard payload.

    Returns a dict that's safe to inject into the prompt and to cross-check
    the LLM's output against. All currency values in UZS.
    """
    org = inputs.get("organization") or {}
    project = inputs.get("project") or {}
    team = inputs.get("team") or []
    products = inputs.get("products") or []
    utilities = inputs.get("utilities") or {}
    extras = utilities.get("extras") or []

    # ---------- Team / payroll ----------
    total_headcount = 0
    monthly_payroll = 0.0
    for row in team:
        cnt = float(row.get("count") or 0)
        sal = float(row.get("salary") or 0)
        total_headcount += int(cnt)
        monthly_payroll += cnt * sal
    annual_payroll = monthly_payroll * 12

    # ---------- Revenue ----------
    # UZS products contribute to monthly_revenue; non-UZS are listed
    # separately so the LLM can mention them but we don't pretend to
    # know FX rates here.
    monthly_revenue_uzs = 0.0
    fx_products = []
    for p in products:
        vol = float(p.get("monthlyVolume") or 0)
        price = float(p.get("price") or 0)
        currency = (p.get("currency") or "UZS").upper()
        if currency == "UZS":
            monthly_revenue_uzs += vol * price
        else:
            fx_products.append({
                "name": p.get("name") or "",
                "currency": currency,
                "monthlyAmount": vol * price,
            })

    # ---------- Utilities ----------
    elec_uzs = float(utilities.get("electricityKwh") or 0) * ELECTRICITY_UZS_PER_KWH
    gas_uzs = float(utilities.get("gasM3") or 0) * GAS_UZS_PER_M3
    water_uzs = float(utilities.get("waterM3") or 0) * WATER_UZS_PER_M3
    utilities_total = elec_uzs + gas_uzs + water_uzs

    extras_total = 0.0
    extras_breakdown = []
    for e in extras:
        amt = float(e.get("amount") or 0)
        name = (e.get("name") or "").strip()
        if name and amt > 0:
            extras_total += amt
            extras_breakdown.append({"name": name, "amount": amt})

    # ---------- Loan service ----------
    loan_amount = float(project.get("loanAmount") or 0)
    annual_rate_pct = float(project.get("interestRate") or 0)
    term_months = int(project.get("termMonths") or 0)
    grace_months = int(project.get("graceMonths") or 0)
    monthly_rate = (annual_rate_pct / 100) / 12

    grace_interest_only = loan_amount * monthly_rate
    post_grace_months = max(term_months - grace_months, 0)
    annuity_post_grace = _annuity_payment(loan_amount, monthly_rate, post_grace_months) \
        if post_grace_months > 0 else 0
    # 12-month average loan payment (used for monthly P&L baseline)
    avg_loan_12m = (
        grace_interest_only * min(grace_months, 12)
        + annuity_post_grace * max(12 - grace_months, 0)
    ) / 12 if term_months > 0 else 0

    # ---------- Monthly costs baseline ----------
    # We sum what we KNOW: payroll, utilities, extras, loan service.
    # Raw materials / rent etc. live in extras (free-form labels), so we
    # don't try to split them here — the LLM does that based on names.
    monthly_costs_during_grace = (
        monthly_payroll + utilities_total + extras_total + grace_interest_only
    )
    monthly_costs_post_grace = (
        monthly_payroll + utilities_total + extras_total + annuity_post_grace
    )
    monthly_costs_avg_12m = (
        monthly_payroll + utilities_total + extras_total + avg_loan_12m
    )

    monthly_profit_during_grace = monthly_revenue_uzs - monthly_costs_during_grace
    monthly_profit_post_grace = monthly_revenue_uzs - monthly_costs_post_grace
    monthly_profit_avg_12m = monthly_revenue_uzs - monthly_costs_avg_12m

    return {
        "team": {
            "totalHeadcount": total_headcount,
            "monthlyPayroll": round(monthly_payroll),
            "annualPayroll": round(annual_payroll),
        },
        "revenue": {
            "monthlyRevenueUzs": round(monthly_revenue_uzs),
            "annualRevenueUzs": round(monthly_revenue_uzs * 12),
            "fxProducts": fx_products,
        },
        "utilities": {
            "electricityUzs": round(elec_uzs),
            "gasUzs": round(gas_uzs),
            "waterUzs": round(water_uzs),
            "total": round(utilities_total),
            "tariffs": {
                "electricityPerKwh": ELECTRICITY_UZS_PER_KWH,
                "gasPerM3": GAS_UZS_PER_M3,
                "waterPerM3": WATER_UZS_PER_M3,
            },
        },
        "extras": {
            "total": round(extras_total),
            "breakdown": extras_breakdown,
        },
        "loan": {
            "principal": round(loan_amount),
            "annualRatePct": annual_rate_pct,
            "termMonths": term_months,
            "graceMonths": grace_months,
            "graceMonthlyPayment": round(grace_interest_only),
            "postGraceMonthlyPayment": round(annuity_post_grace),
            "avgMonthlyPaymentFirst12m": round(avg_loan_12m),
        },
        "monthlyCosts": {
            "duringGrace": round(monthly_costs_during_grace),
            "postGrace": round(monthly_costs_post_grace),
            "avg12m": round(monthly_costs_avg_12m),
            # Component breakdown — same composition as the LLM's
            # `monthlyCosts` schema field, using avg-12m for loan.
            "breakdown": {
                "payroll": round(monthly_payroll),
                "utilities": round(utilities_total),
                "extrasLabeled": round(extras_total),
                "loanPaymentAvg": round(avg_loan_12m),
            },
        },
        "monthlyProfit": {
            "duringGrace": round(monthly_profit_during_grace),
            "postGrace": round(monthly_profit_post_grace),
            "avg12m": round(monthly_profit_avg_12m),
        },
        "marginsAvg12m": {
            "grossMarginPct": _safe_pct(monthly_revenue_uzs - extras_total, monthly_revenue_uzs),
            "operatingMarginPct": _safe_pct(monthly_profit_avg_12m + avg_loan_12m, monthly_revenue_uzs),
            "netMarginPct": _safe_pct(monthly_profit_avg_12m, monthly_revenue_uzs),
        },
    }


def _safe_pct(numer: float, denom: float) -> float:
    if denom <= 0:
        return 0.0
    return round((numer / denom) * 100, 1)


def reconcile_with_llm(llm_output: dict, baseline: dict) -> dict:
    """Override LLM-computed figures with our deterministic ones.

    The LLM's qualitative output (text, risks, KPIs, milestones,
    recommendedProducts) stays untouched — only the numbers we trust
    ourselves on get replaced. Adds an `_overrides` field listing what
    was changed, so admin can see when the LLM tried to disagree with
    the math.
    """
    if not isinstance(llm_output, dict):
        return llm_output

    overrides = []

    # Team
    if isinstance(llm_output.get("team"), dict):
        t = llm_output["team"]
        for k_llm, v_baseline in (
            ("totalHeadcount", baseline["team"]["totalHeadcount"]),
            ("monthlyPayroll", baseline["team"]["monthlyPayroll"]),
            ("annualPayroll", baseline["team"]["annualPayroll"]),
        ):
            old = t.get(k_llm)
            if old != v_baseline:
                overrides.append({"field": f"team.{k_llm}", "llm": old, "baseline": v_baseline})
                t[k_llm] = v_baseline

    # Financials — revenue, costs, profit, margins.
    if isinstance(llm_output.get("financials"), dict):
        f = llm_output["financials"]

        for k_llm, v_baseline in (
            ("monthlyRevenue", baseline["revenue"]["monthlyRevenueUzs"]),
            ("monthlyCosts.total", baseline["monthlyCosts"]["avg12m"]),
            ("monthlyProfit", baseline["monthlyProfit"]["avg12m"]),
            ("annualProfit", baseline["monthlyProfit"]["avg12m"] * 12),
        ):
            if "." in k_llm:
                parent_key, child_key = k_llm.split(".")
                parent = f.get(parent_key)
                if isinstance(parent, dict):
                    old = parent.get(child_key)
                    if old != v_baseline:
                        overrides.append({"field": f"financials.{k_llm}", "llm": old, "baseline": v_baseline})
                        parent[child_key] = v_baseline
            else:
                old = f.get(k_llm)
                if old != v_baseline:
                    overrides.append({"field": f"financials.{k_llm}", "llm": old, "baseline": v_baseline})
                    f[k_llm] = v_baseline

        # Force the breakdown's payroll, utilities, loan to baseline.
        # Leave rent/rawMaterials/other as the LLM split them (those come
        # from the free-form `extras` so we can't deterministically split).
        mc = f.get("monthlyCosts")
        if isinstance(mc, dict):
            for k_llm, v_baseline in (
                ("payroll", baseline["monthlyCosts"]["breakdown"]["payroll"]),
                ("utilities", baseline["monthlyCosts"]["breakdown"]["utilities"]),
                ("loanPayment", baseline["monthlyCosts"]["breakdown"]["loanPaymentAvg"]),
            ):
                old = mc.get(k_llm)
                if old != v_baseline:
                    overrides.append({"field": f"financials.monthlyCosts.{k_llm}", "llm": old, "baseline": v_baseline})
                    mc[k_llm] = v_baseline
            # Recompute total to match the breakdown after overrides.
            recomputed_total = sum(int(mc.get(k) or 0) for k in (
                "payroll", "utilities", "rawMaterials", "loanPayment", "rent", "other",
            ))
            if mc.get("total") != recomputed_total:
                overrides.append({"field": "financials.monthlyCosts.total(recomputed)",
                                  "llm": mc.get("total"), "baseline": recomputed_total})
                mc["total"] = recomputed_total

    if overrides:
        llm_output["_overrides"] = overrides
    return llm_output
