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


def compute_score(balance: dict, pnl: dict) -> dict[str, Any]:
    """Returns a structured score breakdown:
      ratios: {<name>: {value, score, label, benchmark}}
      points: int
      maxPoints: int
      verdict: 'low' | 'medium' | 'high'
      summary: str (1-line natural-language)
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

    # ---------- Ratios ----------
    gross_margin = _safe_div(gross_profit, revenue) * 100  # %
    operating_margin = _safe_div(operating_profit, revenue) * 100
    net_margin = _safe_div(net_profit, revenue) * 100
    roa = _safe_div(net_profit, total_assets) * 100
    current_ratio = _safe_div(current_assets, current_liabilities)
    quick_ratio = _safe_div(current_assets - inventory, current_liabilities)
    debt_to_equity = _safe_div(total_liabilities, equity)
    debt_ratio = _safe_div(total_liabilities, total_assets)
    asset_turnover = _safe_div(revenue, total_assets)

    # ---------- Score each ratio ----------
    ratios = {
        "grossMargin": {
            "value": round(gross_margin, 1),
            "unit": "%",
            "benchmark": "≥30% хорошо, 15–30% средне, <15% слабо",
            "score": _bin(gross_margin, 15, 30),
        },
        "operatingMargin": {
            "value": round(operating_margin, 1),
            "unit": "%",
            "benchmark": "≥10% хорошо, 3–10% средне, <3% слабо",
            "score": _bin(operating_margin, 3, 10),
        },
        "netMargin": {
            "value": round(net_margin, 1),
            "unit": "%",
            "benchmark": "≥7% хорошо, 1–7% средне, <1% слабо",
            "score": _bin(net_margin, 1, 7),
        },
        "roa": {
            "value": round(roa, 1),
            "unit": "%",
            "benchmark": "≥8% хорошо, 2–8% средне, <2% слабо",
            "score": _bin(roa, 2, 8),
        },
        "currentRatio": {
            "value": round(current_ratio, 2),
            "unit": "x",
            "benchmark": "≥1.5 хорошо, 1.0–1.5 средне, <1.0 слабо",
            "score": _bin(current_ratio, 1.0, 1.5),
        },
        "quickRatio": {
            "value": round(quick_ratio, 2),
            "unit": "x",
            "benchmark": "≥1.0 хорошо, 0.6–1.0 средне, <0.6 слабо",
            "score": _bin(quick_ratio, 0.6, 1.0),
        },
        "debtToEquity": {
            "value": round(debt_to_equity, 2),
            "unit": "x",
            "benchmark": "≤1.0 хорошо, 1.0–2.0 средне, >2.0 слабо",
            "score": _bin_lower_better(debt_to_equity, 1.0, 2.0),
        },
        "assetTurnover": {
            "value": round(asset_turnover, 2),
            "unit": "x",
            "benchmark": "≥1.0 хорошо, 0.5–1.0 средне, <0.5 слабо",
            "score": _bin(asset_turnover, 0.5, 1.0),
        },
    }

    points = sum(r["score"] for r in ratios.values())
    max_points = len(ratios) * 2  # 16

    # Verdict bins: high ≥75% of max, medium ≥45%, low otherwise.
    pct = points / max_points if max_points else 0
    if pct >= 0.75:
        verdict = "high"
    elif pct >= 0.45:
        verdict = "medium"
    else:
        verdict = "low"

    # Edge case: if revenue is zero, the company is non-operational —
    # all profitability ratios will be 0 (poor) which is misleading.
    # Mark verdict as 'low' explicitly with a clearer reason.
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
}


def _pretty(k: str) -> str:
    return _PRETTY.get(k, k)
