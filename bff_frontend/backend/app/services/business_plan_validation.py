"""Validity layer for SME Business Plan generation.

Two responsibilities:

1. **Input gate** — runs before the LLM call. Refuses to generate when the
   wizard payload contains values that can't produce a meaningful plan
   (revenue=0, math contradictions, out-of-range rates, etc). Saves a
   60-90s LLM call on garbage in, garbage out.

2. **Output validator** — runs after the LLM call. Strips or replaces any
   field we can't trust:
     • `recommendedProducts` — drop hallucinated IDs, hydrate the rest from
       our authoritative NBU catalog (so rate/term/amount are never wrong).
     • `feasibilityVerdict` / `feasibilityScore` — overwritten with the
       deterministic `creditScore` values; the LLM is too optimistic.
     • `projection12m` — replaced with a deterministic ramp if the shape
       is broken.
     • `risks` / `kpis` — enforce enum + length rules.
     • `extras` categorization — must sum to baseline.extras.total; if
       not, fall back to a single "other" bucket.
     • `marketContext` — blanked if it contains quantitative market
       claims we can't verify.

The principle: if we're not sure a value is right, we don't display it.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any

# ---------- limits used by the input gate ----------

_INTEREST_RATE_MIN = 5.0
_INTEREST_RATE_MAX = 60.0
_TERM_MONTHS_MIN = 1
_TERM_MONTHS_MAX = 360
_SALARY_MIN_UZS = 500_000
_SALARY_MAX_UZS = 200_000_000     # hard block above this
_SALARY_WARN_UZS = 50_000_000     # warning threshold
_TOTAL_REVENUE_MAX_UZS = 100_000_000_000_000   # 100 trillion sanity ceiling

# ---------- output validator enums ----------

_RISK_TYPES = {"market", "operational", "financial", "regulatory"}
_RISK_SEVERITY = {"high", "medium", "low"}
_KPI_FREQUENCY_RU = {"ежедневно", "еженедельно", "ежемесячно", "ежеквартально", "ежегодно"}
_KPI_FREQUENCY_UZ = {"kunlik", "haftalik", "oylik", "choraklik", "yillik",
                     "кунлик", "ҳафталик", "ойлик", "чораклик", "йиллик"}
_KPI_FREQUENCY_ALLOWED = _KPI_FREQUENCY_RU | _KPI_FREQUENCY_UZ

# Quantitative claim detector: "<number>(.<number>)? (трлн|млрд|млн|тыс|сум|UZS|%)"
# Heuristic but conservative — any sentence with a number+unit gets the field flagged.
_QUANT_CLAIM_RE = re.compile(
    r"\d[\d\s.,]*\s*(?:трлн|млрд|млн|тыс|trln|mlrd|mln|сум|сўм|so'm|UZS|%|долл|usd)",
    re.IGNORECASE,
)


# ============================================================================
# Input gate
# ============================================================================

def validate_inputs(
    inputs: dict[str, Any],
    baseline: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return (errors, warnings).

    errors → 422; the route refuses to call the LLM.
    warnings → allowed through, but added to the plan as system-generated
    risks so the user sees them.
    """
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    project = inputs.get("project") or {}
    org = inputs.get("organization") or {}
    products = inputs.get("products") or []
    team = inputs.get("team") or []

    # ---------- Project / financing math ----------
    loan = float(project.get("loanAmount") or 0)
    own = float(project.get("ownContribution") or 0)
    total = float(project.get("totalValue") or 0)
    term_m = int(project.get("termMonths") or 0)
    grace_m = int(project.get("graceMonths") or 0)
    rate = float(project.get("interestRate") or 0)

    if loan <= 0:
        errors.append({"field": "project.loanAmount",
                       "message": "Сумма кредита должна быть больше 0"})

    if total > 0 and abs((loan + own) - total) / total > 0.01:
        errors.append({"field": "project.totalValue",
                       "message": "Общая стоимость проекта должна равняться "
                                  "сумме собственного взноса и кредита"})

    if term_m < _TERM_MONTHS_MIN or term_m > _TERM_MONTHS_MAX:
        errors.append({"field": "project.termMonths",
                       "message": f"Срок должен быть от {_TERM_MONTHS_MIN} "
                                  f"до {_TERM_MONTHS_MAX} месяцев"})

    if grace_m >= term_m and term_m > 0:
        errors.append({"field": "project.graceMonths",
                       "message": "Льготный период не может быть больше или "
                                  "равен сроку кредита"})

    if rate < _INTEREST_RATE_MIN or rate > _INTEREST_RATE_MAX:
        errors.append({"field": "project.interestRate",
                       "message": f"Ставка должна быть в диапазоне "
                                  f"{_INTEREST_RATE_MIN}–{_INTEREST_RATE_MAX}%"})

    # ---------- Organization ----------
    founded = (org.get("foundedDate") or "").strip()
    if founded:
        try:
            y, m, d = (int(x) for x in founded.split("-")[:3])
            if date(y, m, d) > date.today():
                errors.append({"field": "organization.foundedDate",
                               "message": "Дата регистрации не может быть в будущем"})
        except (ValueError, AttributeError):
            errors.append({"field": "organization.foundedDate",
                           "message": "Неверный формат даты регистрации"})

    # ---------- Revenue ----------
    monthly_revenue_uzs = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    if monthly_revenue_uzs <= 0:
        errors.append({"field": "products",
                       "message": "Месячная выручка в UZS равна 0 — заполните "
                                  "раздел «Продукты/Услуги» с ценами в UZS"})
    elif monthly_revenue_uzs > _TOTAL_REVENUE_MAX_UZS:
        errors.append({"field": "products",
                       "message": "Сумма выручки выглядит неправдоподобно — "
                                  "проверьте объёмы и цены"})

    # FX products → warning
    fx_products = (baseline.get("revenue") or {}).get("fxProducts") or []
    if fx_products:
        warnings.append({"field": "products",
                         "message": "Часть выручки указана в иностранной валюте — "
                                    "в расчётах учтена только UZS-часть"})

    # ---------- Team / salaries ----------
    for i, row in enumerate(team):
        sal = float(row.get("salary") or 0)
        cnt = int(row.get("count") or 0)
        role = (row.get("role") or "").strip()
        if cnt > 0 and sal > 0:
            if sal < _SALARY_MIN_UZS:
                errors.append({"field": f"team[{i}].salary",
                               "message": f"Оклад «{role}» меньше минимума "
                                          f"({_SALARY_MIN_UZS:,} UZS)"})
            elif sal > _SALARY_MAX_UZS:
                errors.append({"field": f"team[{i}].salary",
                               "message": f"Оклад «{role}» превышает разумный "
                                          f"максимум ({_SALARY_MAX_UZS:,} UZS)"})
            elif sal > _SALARY_WARN_UZS:
                warnings.append({"field": f"team[{i}].salary",
                                 "message": f"Высокий оклад для «{role}» — "
                                            f"проверьте корректность"})

    # ---------- Catalog fit ----------
    if not candidates:
        errors.append({"field": "project",
                       "message": "Под параметры заявки в каталоге продуктов "
                                  "ничего не подходит — обратитесь в отделение НБУ"})

    # ---------- Loss-making project (warning only, makes plan still useful) ----------
    monthly_profit = (baseline.get("monthlyProfit") or {}).get("avg12m", 0)
    if monthly_profit < 0:
        warnings.append({"field": "financials",
                         "message": "Расчётная прибыль отрицательна на протяжении "
                                    "первого года — проект убыточен в текущих параметрах"})

    # ---------- Loan won't be repaid in term ----------
    avg_loan_pmt = (baseline.get("loan") or {}).get("avgMonthlyPaymentFirst12m", 0)
    annual_net = (monthly_profit + avg_loan_pmt) * 12  # operating, before debt service
    if annual_net > 0 and term_m > 0:
        payback_years = loan / annual_net
        if payback_years > term_m / 12:
            warnings.append({"field": "project",
                             "message": f"Расчётный срок окупаемости "
                                        f"({payback_years:.1f} лет) превышает срок "
                                        f"кредита ({term_m / 12:.1f} лет)"})

    return errors, warnings


# ============================================================================
# Output validator
# ============================================================================

def validate_and_clean(
    llm_output: dict[str, Any],
    *,
    candidates: list[dict[str, Any]],
    baseline: dict[str, Any],
    credit_score: dict[str, Any],
    inputs: dict[str, Any],
    warnings: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Filter / replace LLM output so every displayed field is trustworthy.

    Mutates and returns `llm_output`. Adds `_validity` metadata so the
    frontend can reflect what was filtered.
    """
    if not isinstance(llm_output, dict):
        # LLM returned garbage — synthesize a minimal honest skeleton.
        return _empty_plan(baseline, credit_score, inputs)

    flags: dict[str, Any] = {}

    # ---------- Verdict / score: always come from credit scoring ----------
    llm_output["feasibilityVerdict"] = credit_score.get("verdict", "low")
    llm_output["feasibilityScore"] = int(credit_score.get("percent", 0))

    # ---------- recommendedProducts: hydrate from catalog, drop hallucinations ----------
    catalog_by_id = {c["id"]: c for c in candidates if "id" in c}
    catalog_by_name = {c["name"]: c for c in candidates if "name" in c}

    cleaned_products: list[dict[str, Any]] = []
    for r in llm_output.get("recommendedProducts") or []:
        if not isinstance(r, dict):
            continue
        src = (catalog_by_id.get(r.get("productId"))
               or catalog_by_name.get(r.get("name")))
        if not src:
            continue  # hallucinated ID/name → drop
        cleaned_products.append({
            "name": src.get("name", ""),
            "rate": src.get("rate", ""),
            "term": src.get("term", ""),
            "amount": src.get("amount", ""),
            "purpose": src.get("purpose", ""),
            "rationale": str(r.get("rationale", ""))[:500],
            "fitScore": _clamp(_to_int(r.get("fitScore"), 50), 0, 100),
        })
    llm_output["recommendedProducts"] = cleaned_products
    if not cleaned_products:
        flags["noProductMatch"] = True

    # ---------- projection12m: validate shape, synth on failure ----------
    proj = llm_output.get("projection12m")
    if not _is_valid_projection(proj):
        llm_output["projection12m"] = synthesize_projection_12m(
            baseline, inputs.get("project") or {}
        )
        flags["projectionSource"] = "synthesized"
    else:
        # Even when valid, normalize numbers (some LLMs emit strings).
        llm_output["projection12m"] = [
            {"month": int(p["month"]),
             "revenue": _to_int(p.get("revenue"), 0),
             "costs": _to_int(p.get("costs"), 0),
             "profit": _to_int(p.get("profit"), 0)}
            for p in proj
        ]

    # ---------- breakevenMonths: derive from projection ----------
    fin = llm_output.setdefault("financials", {})
    fin["breakevenMonths"] = _compute_breakeven_months(llm_output["projection12m"])

    # ---------- ebitdaMarginPct: from baseline math ----------
    margins = baseline.get("marginsAvg12m") or {}
    fin["ebitdaMarginPct"] = float(margins.get("operatingMarginPct", 0))
    fin["grossMarginPct"] = float(margins.get("grossMarginPct", 0))

    # ---------- extras categorization sanity ----------
    extras_total = (baseline.get("extras") or {}).get("total", 0)
    mc = fin.get("monthlyCosts") or {}
    cat_sum = (_to_int(mc.get("rent"), 0)
               + _to_int(mc.get("rawMaterials"), 0)
               + _to_int(mc.get("other"), 0))
    if extras_total > 0 and abs(cat_sum - extras_total) / max(extras_total, 1) > 0.05:
        # Categorization off by >5% — fall back to lump bucket
        mc["rent"] = 0
        mc["rawMaterials"] = 0
        mc["other"] = int(extras_total)
        flags["extrasFallback"] = True

    # ---------- risks: enforce enums + lengths ----------
    raw_risks = llm_output.get("risks") or []
    cleaned_risks = []
    for r in raw_risks:
        if not isinstance(r, dict):
            continue
        rtype = r.get("type")
        sev = r.get("severity")
        desc = (r.get("description") or "").strip()
        mit = (r.get("mitigation") or "").strip()
        if rtype not in _RISK_TYPES or sev not in _RISK_SEVERITY:
            continue
        if not desc or not mit:
            continue
        cleaned_risks.append({
            "type": rtype,
            "severity": sev,
            "description": desc[:140],
            "mitigation": mit[:140],
        })
    # Append warning-derived risks so the user sees them prominently.
    for w in warnings or []:
        cleaned_risks.append({
            "type": "financial",
            "severity": "high",
            "description": w["message"][:140],
            "mitigation": "Уточните параметры в анкете или обсудите с менеджером НБУ",
        })
    llm_output["risks"] = cleaned_risks

    # ---------- kpis: enforce frequency enum + length ----------
    raw_kpis = llm_output.get("kpis") or []
    cleaned_kpis = []
    for k in raw_kpis:
        if not isinstance(k, dict):
            continue
        name = (k.get("name") or "").strip()
        target = (k.get("target") or "").strip()
        freq = (k.get("frequency") or "").strip().lower()
        if not name or not target:
            continue
        if freq not in _KPI_FREQUENCY_ALLOWED:
            freq = "ежемесячно" if any("ежемес" in f for f in _KPI_FREQUENCY_RU) else "oylik"
        cleaned_kpis.append({
            "name": name[:80],
            "target": target[:80],
            "frequency": freq,
        })
    llm_output["kpis"] = cleaned_kpis

    # ---------- marketContext: blank on unverifiable quant claims ----------
    mc_text = (llm_output.get("marketContext") or "").strip()
    if mc_text and _QUANT_CLAIM_RE.search(mc_text):
        llm_output["marketContext"] = ""
        flags["marketContextBlanked"] = True

    # ---------- length caps on free text ----------
    for field, cap in (("summary", 300),
                       ("executiveSummary", 600),
                       ("marketContext", 500)):
        v = llm_output.get(field)
        if isinstance(v, str) and len(v) > cap:
            llm_output[field] = v[:cap].rstrip()

    # ---------- attach validity metadata ----------
    if flags:
        llm_output["_validity"] = flags
    return llm_output


# ============================================================================
# Helpers
# ============================================================================

def synthesize_projection_12m(
    baseline: dict[str, Any],
    project: dict[str, Any],
) -> list[dict[str, int]]:
    """Build a deterministic 12-month ramp from the baseline.

    Revenue ramps from 30% to 100% of monthly target across `startupMonths`
    months, then stays flat. Variable costs scale with revenue (50%–100%);
    fixed costs (payroll, utilities, extras) stay constant. Loan service
    follows grace → annuity transition.
    """
    target_rev = (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0)
    fixed = ((baseline.get("team") or {}).get("monthlyPayroll", 0)
             + (baseline.get("utilities") or {}).get("total", 0)
             + (baseline.get("extras") or {}).get("total", 0))
    grace_m = int(project.get("graceMonths") or 0)
    grace_pmt = (baseline.get("loan") or {}).get("graceMonthlyPayment", 0)
    post_pmt = (baseline.get("loan") or {}).get("postGraceMonthlyPayment", 0)
    startup = max(int(project.get("startupMonths") or 3), 1)

    out: list[dict[str, int]] = []
    for m in range(1, 13):
        ramp = min(0.30 + 0.70 * (m - 1) / startup, 1.0)
        rev = round(target_rev * ramp)
        loan_pmt = grace_pmt if m <= grace_m else post_pmt
        # Fixed costs scale 50%-100% with ramp (production not at full capacity yet)
        var_factor = 0.5 + 0.5 * ramp
        costs = round(fixed * var_factor + loan_pmt)
        out.append({
            "month": m,
            "revenue": rev,
            "costs": costs,
            "profit": rev - costs,
        })
    return out


def _is_valid_projection(proj: Any) -> bool:
    if not isinstance(proj, list) or len(proj) != 12:
        return False
    seen_months: set[int] = set()
    for p in proj:
        if not isinstance(p, dict):
            return False
        m = p.get("month")
        if not isinstance(m, int) or m < 1 or m > 12 or m in seen_months:
            return False
        seen_months.add(m)
        for k in ("revenue", "costs", "profit"):
            v = p.get(k)
            if not isinstance(v, (int, float)):
                return False
    return True


def _compute_breakeven_months(projection: list[dict[str, Any]]) -> int | None:
    """Cumulative profit crossing 0. None if it never breaks even within 12m."""
    cum = 0
    for p in projection:
        cum += int(p.get("profit") or 0)
        if cum >= 0:
            return int(p.get("month") or 0)
    return None


def _empty_plan(
    baseline: dict[str, Any],
    credit_score: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    """Skeleton plan when the LLM output was unparseable. Honest fallback —
    deterministic numbers only, no narrative."""
    proj = synthesize_projection_12m(baseline, inputs.get("project") or {})
    margins = baseline.get("marginsAvg12m") or {}
    return {
        "feasibilityVerdict": credit_score.get("verdict", "low"),
        "feasibilityScore": int(credit_score.get("percent", 0)),
        "summary": "",
        "executiveSummary": "",
        "marketContext": "",
        "operations": {"processFlow": [], "supplyChain": "", "criticalDependencies": []},
        "team": {**(baseline.get("team") or {}), "assessment": ""},
        "financials": {
            "monthlyRevenue": (baseline.get("revenue") or {}).get("monthlyRevenueUzs", 0),
            "monthlyCosts": {
                "payroll": (baseline.get("monthlyCosts") or {}).get("breakdown", {}).get("payroll", 0),
                "utilities": (baseline.get("monthlyCosts") or {}).get("breakdown", {}).get("utilities", 0),
                "loanPayment": (baseline.get("monthlyCosts") or {}).get("breakdown", {}).get("loanPaymentAvg", 0),
                "rawMaterials": 0,
                "rent": 0,
                "other": (baseline.get("extras") or {}).get("total", 0),
                "total": (baseline.get("monthlyCosts") or {}).get("avg12m", 0),
            },
            "monthlyProfit": (baseline.get("monthlyProfit") or {}).get("avg12m", 0),
            "annualProfit": (baseline.get("monthlyProfit") or {}).get("avg12m", 0) * 12,
            "breakevenMonths": _compute_breakeven_months(proj),
            "grossMarginPct": float(margins.get("grossMarginPct", 0)),
            "ebitdaMarginPct": float(margins.get("operatingMarginPct", 0)),
            "assessment": "",
        },
        "projection12m": proj,
        "milestones": {"first90Days": [], "first6Months": [], "first12Months": []},
        "risks": [],
        "kpis": [],
        "recommendedProducts": [],
        "actionableNextSteps": [],
        "_validity": {"llmOutputUnusable": True, "projectionSource": "synthesized"},
    }


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def _to_int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default
