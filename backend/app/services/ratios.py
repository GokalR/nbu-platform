"""Converts parsed Uzbek Form 1 + Form 2 code maps into financial ratios."""
from __future__ import annotations


def _safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return a / b


def compute(form1: dict[str, float] | None, form2: dict[str, float] | None) -> dict:
    form1 = form1 or {}
    form2 = form2 or {}
    g = lambda d, k: d.get(k) or 0.0

    revenue        = g(form2, "010")
    cogs           = g(form2, "020")
    gross_profit   = g(form2, "030")
    sell_exp       = g(form2, "050")
    admin_exp      = g(form2, "060")
    op_profit      = g(form2, "100")
    interest_exp   = g(form2, "180")
    pretax_profit  = g(form2, "240")
    net_profit     = form2.get("270") or form2.get("260") or form2.get("250") or pretax_profit

    fixed_assets   = g(form1, "012")
    inventory      = g(form1, "140")
    receivables    = g(form1, "210")
    cash           = g(form1, "320")
    current_assets = g(form1, "390")
    total_assets   = g(form1, "400")
    equity         = g(form1, "480")
    lt_liab        = g(form1, "490")
    lt_bank_loans  = g(form1, "570")
    st_liab        = g(form1, "600")
    st_bank_loans  = g(form1, "730")
    total_liab     = g(form1, "770")
    total_debt     = lt_bank_loans + (form1.get("580") or 0) + st_bank_loans + (form1.get("740") or 0)

    absolutes = {
        "revenue": revenue,
        "grossProfit": gross_profit,
        "operatingProfit": op_profit,
        "netProfit": net_profit,
        "totalAssets": total_assets,
        "equity": equity,
        "totalLiabilities": total_liab,
        "totalDebt": total_debt,
        "currentAssets": current_assets,
        "currentLiabilities": st_liab,
        "inventory": inventory,
        "receivables": receivables,
        "cash": cash,
        "interestExpense": interest_exp,
    }

    ratios = {
        "grossMargin":      _safe_div(gross_profit, revenue),
        "operatingMargin":  _safe_div(op_profit, revenue),
        "netMargin":        _safe_div(net_profit, revenue),
        "roa":              _safe_div(net_profit, total_assets),
        "roe":              _safe_div(net_profit, equity),
        "currentRatio":     _safe_div(current_assets, st_liab),
        "quickRatio":       _safe_div(current_assets - inventory, st_liab),
        "debtToEquity":     _safe_div(total_debt, equity),
        "debtToAssets":     _safe_div(total_debt, total_assets),
        "assetTurnover":    _safe_div(revenue, total_assets),
        "inventoryTurn":    _safe_div(cogs, inventory),
        "interestCoverage": _safe_div(op_profit, interest_exp),
    }

    return {"absolutes": absolutes, "ratios": ratios}
