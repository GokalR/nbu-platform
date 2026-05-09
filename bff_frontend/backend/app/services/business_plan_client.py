"""LLM wrapper for SME Business Plan generation.

Provider-agnostic: picks Claude (Anthropic) or GPT (OpenAI) based on
LLM_PROVIDER env var.

**Slim-schema design.** The LLM only writes qualitative content
(narrative, risks, KPIs, milestones, recommended-product rationale).
Every number — payroll, revenue, costs, profit, margins, projection,
recommended-product rate/term/amount — is computed deterministically
server-side and merged into the final plan by `_assemble_full_plan`.

This cuts LLM output ~50% (60-90s → 30-45s on Sonnet 4.6) and removes a
whole class of hallucination risks: the LLM can no longer invent a
credit-product rate or disagree with our payroll math.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic

from ..config import get_settings

log = logging.getLogger(__name__)


# ============================================================================
# Slim system prompts — qualitative content only
# ============================================================================

SYSTEM_PROMPT_RU = """Ты — старший кредитный аналитик НБУ Узбекистана, специализирующийся на МСБ.

На вход получаешь JSON с данными анкеты предпринимателя плюс:
  • candidateProducts — 3 кредитных продукта НБУ; ты выбираешь 1-2 по их `id`
    и пишешь обоснование. РЕЙТЫ, СУММЫ, СРОКИ, ЦЕЛИ — берёт сервер из каталога,
    тебе их писать НЕ НАДО.
  • computedFinancials — фактические числа (выручка, расходы по категориям,
    прибыль, маржа, платёж по кредиту, ФОТ). Используй для контекста и для
    написания assessment-полей. В ответе не повторяй — сервер сам вставит.
  • computedCreditScore — детерминистический скоринг (verdict + ratios). Опирайся
    на него при формулировании рисков и actionableNextSteps.

Верни СТРОГО валидный JSON на русском, без markdown-обрамления и без комментариев.
Все числа — числа, не строки. Все суммы — в сумах (UZS) без форматирования.

СХЕМА ОТВЕТА (только качественные поля):

{
  "summary": "2-3 предложения: суть проекта + главный вывод о реалистичности",
  "executiveSummary": "1 абзац (4-6 предложений) — для руководителя банка. Опирайся на computedFinancials и computedCreditScore.",
  "marketContext": "1 абзац — контекст ниши в Узбекистане/регионе. БЕЗ конкретных денежных объёмов рынка, выручки конкурентов, долей рынка в %. Только качественные характеристики.",
  "operations": {
    "processFlow": ["3-5 пунктов: как идёт производство/услуга day-to-day"],
    "supplyChain": "1-2 предложения о ключевых поставщиках/сырье",
    "criticalDependencies": ["2-3 пункта — без чего бизнес встанет"]
  },
  "teamAssessment": "1-2 предложения — адекватен ли штат заявленным объёмам (опирайся на computedFinancials.team)",
  "financialsAssessment": "2-3 предложения — где маржа, где риск, что вызывает вопросы (используй computedFinancials и computedCreditScore.ratios)",
  "extrasCategorization": {
    "rent": <int>,
    "rawMaterials": <int>,
    "other": <int>
  },
  "milestones": {
    "first90Days":  ["3-5 конкретных задач — регистрация, монтаж оборудования, найм, первый запуск"],
    "first6Months": ["3-5 задач — выход на проектную мощность, маркетинг, первые продажи"],
    "first12Months":["3-5 задач — масштабирование, новые каналы, выход на безубыточность"]
  },
  "risks": [
    {"type": "market" | "operational" | "financial" | "regulatory",
     "description": "конкретный риск с привязкой к данным анкеты, ≤140 символов",
     "mitigation": "1 действие, ≤140 символов",
     "severity": "high" | "medium" | "low"}
  ],
  "kpis": [
    {"name": "Название показателя",
     "target": "Целевое значение с числом",
     "frequency": "ежедневно" | "еженедельно" | "ежемесячно" | "ежеквартально" | "ежегодно"}
  ],
  "recommendedProducts": [
    {
      "productId": "<id из candidateProducts>",
      "rationale": "2-3 предложения — почему именно этот продукт под эту заявку (со ссылкой на сумму/цель/срок)",
      "fitScore": 0-100
    }
  ],
  "actionableNextSteps": [
    "5-7 шагов, которые предпринимателю нужно сделать ПРЯМО СЕЙЧАС, чтобы прийти в банк готовым"
  ]
}

КРИТИЧЕСКИЕ ПРАВИЛА:
1. Не выдумывай числа, которых нет во входных данных. В marketContext — никаких объёмов рынка
   в денежном выражении, никаких долей рынка в %, никаких темпов роста с цифрой. Качественно.
2. extrasCategorization: rent + rawMaterials + other должно равняться computedFinancials.extrasTotal.
   Распредели computedFinancials.extrasBreakdown по категориям (мука/сырьё → rawMaterials,
   аренда → rent, остальное → other).
3. recommendedProducts: только productId из candidateProducts. 1-2 продукта максимум.
   Если ни один не подходит по логике — пустой массив [] и опиши причину в risks.
4. risks — 4-6 объектов. Каждый обязан ссылаться на конкретное поле/число из computedFinancials
   или computedCreditScore.ratios. Никаких общих фраз ("важно следить за расходами").
5. kpis — 4-6 объектов. Целевые значения с числами.
6. Длина: executiveSummary ≤ 600 символов, marketContext ≤ 500, summary ≤ 300.
7. Тон — деловой, концентрированный, без воды.
"""


SYSTEM_PROMPT_UZ = """Сен — Ўзбекистон НБУнинг МСБ кредит таҳлили бўйича катта мутахассисисан.

Кириш JSON да тадбиркор анкетаси ҳамда:
  • candidateProducts — 3 та НБУ кредит маҳсулоти; сен 1-2 тасини `id` бўйича танлайсан
    ва асос ёзасан. СТАВКА, СУММА, МУДДАТ, МАҚСАД — серверда каталогдан олинади, сенга
    уларни ёзиш керак ЭМАС.
  • computedFinancials — серверда ҳисобланган рақамлар (даромад, харажат, фойда,
    маржа, ФОТ, кредит тўлови). Контекст учун ишлат, жавобда такрорлама.
  • computedCreditScore — детерминистик скоринг (verdict + ratios). Хатарларни ва
    actionableNextSteps ни шу асосда ёз.

ФАҚАТ валид JSON қайтар (ўзбек тилида, markdown эмас, изоҳсиз). Барча сонлар — сон,
сатр эмас. Барча суммалар — сўмда (UZS) форматсиз.

ЖАВОБ СХЕМАСИ (фақат сифат майдонлари):

{
  "summary": "2-3 жумла: лойиҳа моҳияти + реалистиклик",
  "executiveSummary": "1 абзац (4-6 жумла) — банк раҳбари учун. computedFinancials ва computedCreditScore га таян.",
  "marketContext": "1 абзац — соҳа контексти. Бозор ҳажми сўмда, рақобатчи даромадлари, бозор улуши % да — ЁЗМА. Фақат сифат хусусиятлари.",
  "operations": {
    "processFlow": ["3-5 пункт"],
    "supplyChain": "1-2 жумла",
    "criticalDependencies": ["2-3 пункт"]
  },
  "teamAssessment": "1-2 жумла",
  "financialsAssessment": "2-3 жумла",
  "extrasCategorization": {"rent": <int>, "rawMaterials": <int>, "other": <int>},
  "milestones": {
    "first90Days": ["3-5 вазифа"],
    "first6Months": ["3-5 вазифа"],
    "first12Months": ["3-5 вазифа"]
  },
  "risks": [
    {"type":"market"|"operational"|"financial"|"regulatory",
     "description":"≤140 белги","mitigation":"≤140 белги",
     "severity":"high"|"medium"|"low"}
  ],
  "kpis": [
    {"name":"...","target":"рақамли мақсад",
     "frequency":"кунлик"|"ҳафталик"|"ойлик"|"чораклик"|"йиллик"}
  ],
  "recommendedProducts": [
    {"productId":"<id>","rationale":"2-3 жумла","fitScore":0-100}
  ],
  "actionableNextSteps": ["5-7 қадам"]
}

ҚАТЪИЙ ҚОИДАЛАР:
1. Кириш маълумотларида бўлмаган рақамларни ўйлаб топма. marketContext да — пул билан
   бозор ҳажми, рақобатчи даромадлари, фоиз бўйича бозор улуши ЁК.
2. extrasCategorization: rent + rawMaterials + other = computedFinancials.extrasTotal.
3. recommendedProducts: фақат candidateProducts даги productId. 1-2 та максимум.
4. risks — 4-6 объект. Ҳар бири computedFinancials/computedCreditScore.ratios даги аниқ
   рақамга ишора қилсин.
5. kpis — 4-6 объект. Рақамли мақсад.
6. Узунлик: executiveSummary ≤ 600 белги, marketContext ≤ 500, summary ≤ 300.
"""


def _system_prompt(lang: str) -> str:
    return SYSTEM_PROMPT_UZ if (lang or "uz").lower() == "uz" else SYSTEM_PROMPT_RU


def _build_user_message(payload: dict[str, Any]) -> str:
    return "ВХОД:\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def _extract_json(raw: str) -> dict | None:
    s = raw.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(s[start : end + 1])
    except json.JSONDecodeError:
        return None


# ============================================================================
# Public entry point
# ============================================================================

def generate_business_plan(
    *,
    inputs: dict[str, Any],
    candidate_products: list[dict],
    lang: str = "uz",
    model: str | None = None,
    provider: str | None = None,
    historical_financials: dict | None = None,
    baseline: dict | None = None,
) -> dict[str, Any]:
    """Generate a business plan.

    The LLM produces a slim qualitative-only JSON; this function then
    assembles the full plan structure (with deterministic numbers, hydrated
    products, synthesized projection) and returns it.

    Returns {output, input_tokens, output_tokens, model, provider, baseline}.
    """
    from . import business_plan_compute as bpc
    from . import business_plan_validation as bpv

    settings = get_settings()
    used_provider = (provider or settings.llm_provider_clean).lower()

    if baseline is None:
        baseline = bpc.compute_baseline(inputs)

    # Build a compact context payload — only what's needed for the LLM to
    # write good qualitative output. We DO NOT ask the LLM to repeat back
    # the numbers; the prompt explicitly forbids it.
    prompt_payload = {
        "organization": inputs.get("organization"),
        "project": inputs.get("project"),
        "products": inputs.get("products"),
        "team": inputs.get("team"),
        "utilities": inputs.get("utilities"),
        "lang": lang,
        # Slim catalog view — id is what the LLM picks; rest is for context.
        "candidateProducts": [
            {"id": c["id"], "name": c["name"], "category": c.get("category", ""),
             "purpose": c.get("purpose", ""), "rate": c.get("rate", ""),
             "term": c.get("term", ""), "amount": c.get("amount", "")}
            for c in candidate_products
        ],
        "computedFinancials": {
            "monthlyRevenueUzs": baseline["revenue"]["monthlyRevenueUzs"],
            "annualRevenueUzs": baseline["revenue"]["annualRevenueUzs"],
            "monthlyPayroll": baseline["team"]["monthlyPayroll"],
            "totalHeadcount": baseline["team"]["totalHeadcount"],
            "utilitiesTotal": baseline["utilities"]["total"],
            "extrasTotal": baseline["extras"]["total"],
            "extrasBreakdown": baseline["extras"]["breakdown"],
            "loanAvgMonthlyPayment12m": baseline["loan"]["avgMonthlyPaymentFirst12m"],
            "monthlyCostsAvg12m": baseline["monthlyCosts"]["avg12m"],
            "monthlyProfitAvg12m": baseline["monthlyProfit"]["avg12m"],
            "marginsAvg12m": baseline["marginsAvg12m"],
        },
    }
    if historical_financials:
        prompt_payload["historicalFinancials"] = historical_financials
        # Make the credit score visible to the LLM for risk/next-steps grounding.
        score = historical_financials.get("score") or {}
        prompt_payload["computedCreditScore"] = {
            "verdict": score.get("verdict"),
            "percent": score.get("percent"),
            "ratios": {k: {"value": v.get("value"), "unit": v.get("unit"),
                           "score": v.get("score")}
                       for k, v in (score.get("ratios") or {}).items()},
        }

    system = _system_prompt(lang)
    user_msg = _build_user_message(prompt_payload)

    if used_provider == "openai":
        result = _call_openai(system=system, user_msg=user_msg, model=model, settings=settings)
    else:
        result = _call_claude(system=system, user_msg=user_msg, model=model, settings=settings)

    # Assemble the full plan structure from slim LLM output + deterministic
    # baseline + catalog. The downstream output validator runs on this.
    credit_score = (historical_financials or {}).get("score") or {}
    result["output"] = _assemble_full_plan(
        slim=result["output"],
        baseline=baseline,
        credit_score=credit_score,
        candidates=candidate_products,
        project=inputs.get("project") or {},
    )
    result["baseline"] = baseline
    return result


# ============================================================================
# Plan assembly — slim LLM output + deterministic data → full plan
# ============================================================================

def _assemble_full_plan(
    *,
    slim: dict[str, Any],
    baseline: dict[str, Any],
    credit_score: dict[str, Any],
    candidates: list[dict[str, Any]],
    project: dict[str, Any],
) -> dict[str, Any]:
    """Merge the slim LLM output with deterministic figures into the full
    plan shape that the frontend / validator / DOCX builder expect.

    Numbers come from baseline. Recommended products are hydrated from the
    catalog (LLM only chose IDs). Projection is synthesized from baseline.
    Credit score drives feasibilityVerdict / feasibilityScore.

    The output validator will further enforce enums and length caps.
    """
    from . import business_plan_validation as bpv

    if not isinstance(slim, dict):
        slim = {}

    # Catalog lookup for hydrating recommended products
    catalog_by_id = {c["id"]: c for c in candidates if "id" in c}

    rec_products: list[dict[str, Any]] = []
    for r in slim.get("recommendedProducts") or []:
        if not isinstance(r, dict):
            continue
        src = catalog_by_id.get(r.get("productId"))
        if not src:
            continue
        rec_products.append({
            "name": src.get("name", ""),
            "rate": src.get("rate", ""),
            "term": src.get("term", ""),
            "amount": src.get("amount", ""),
            "purpose": src.get("purpose", ""),
            "rationale": str(r.get("rationale", ""))[:500],
            "fitScore": _clamp_int(r.get("fitScore"), 0, 100, default=50),
        })

    # Extras categorization — clamp sum to baseline.extras.total
    extras_total = int(baseline["extras"]["total"])
    cat = slim.get("extrasCategorization") or {}
    rent = max(0, _to_int(cat.get("rent"), 0))
    raw_materials = max(0, _to_int(cat.get("rawMaterials"), 0))
    other = max(0, _to_int(cat.get("other"), 0))
    cat_sum = rent + raw_materials + other
    if extras_total > 0 and cat_sum != extras_total:
        # Soft-correct: scale to baseline total. Validator will further
        # downgrade to a single bucket if the proportions are absurd.
        if cat_sum > 0:
            scale = extras_total / cat_sum
            rent = round(rent * scale)
            raw_materials = round(raw_materials * scale)
            other = extras_total - rent - raw_materials  # absorbs rounding
        else:
            other = extras_total

    margins = baseline["marginsAvg12m"]
    proj = bpv.synthesize_projection_12m(baseline, project)
    breakeven = bpv._compute_breakeven_months(proj)

    return {
        # Verdict — always from deterministic credit scoring
        "feasibilityVerdict": credit_score.get("verdict", "low"),
        "feasibilityScore": int(credit_score.get("percent", 0)),

        # Narrative — from LLM
        "summary": str(slim.get("summary") or "")[:300],
        "executiveSummary": str(slim.get("executiveSummary") or "")[:600],
        "marketContext": str(slim.get("marketContext") or "")[:500],
        "operations": {
            "processFlow": [str(s) for s in (slim.get("operations") or {}).get("processFlow") or []],
            "supplyChain": str((slim.get("operations") or {}).get("supplyChain") or ""),
            "criticalDependencies": [
                str(s) for s in (slim.get("operations") or {}).get("criticalDependencies") or []
            ],
        },

        # Team — numbers from baseline, assessment from LLM
        "team": {
            "totalHeadcount": baseline["team"]["totalHeadcount"],
            "monthlyPayroll": baseline["team"]["monthlyPayroll"],
            "annualPayroll": baseline["team"]["annualPayroll"],
            "assessment": str(slim.get("teamAssessment") or "")[:300],
        },

        # Financials — numbers from baseline, assessment from LLM, extras split from LLM
        "financials": {
            "monthlyRevenue": baseline["revenue"]["monthlyRevenueUzs"],
            "monthlyCosts": {
                "payroll": baseline["monthlyCosts"]["breakdown"]["payroll"],
                "utilities": baseline["monthlyCosts"]["breakdown"]["utilities"],
                "loanPayment": baseline["monthlyCosts"]["breakdown"]["loanPaymentAvg"],
                "rent": rent,
                "rawMaterials": raw_materials,
                "other": other,
                "total": baseline["monthlyCosts"]["avg12m"],
            },
            "monthlyProfit": baseline["monthlyProfit"]["avg12m"],
            "annualProfit": baseline["monthlyProfit"]["avg12m"] * 12,
            "breakevenMonths": breakeven,
            "grossMarginPct": float(margins["grossMarginPct"]),
            "ebitdaMarginPct": float(margins["operatingMarginPct"]),
            "assessment": str(slim.get("financialsAssessment") or "")[:300],
        },

        # Synthesized
        "projection12m": proj,

        # From LLM (validator will enforce enums / length caps next)
        "milestones": {
            "first90Days": [str(s) for s in (slim.get("milestones") or {}).get("first90Days") or []],
            "first6Months": [str(s) for s in (slim.get("milestones") or {}).get("first6Months") or []],
            "first12Months": [str(s) for s in (slim.get("milestones") or {}).get("first12Months") or []],
        },
        "risks": slim.get("risks") or [],
        "kpis": slim.get("kpis") or [],
        "actionableNextSteps": [str(s) for s in slim.get("actionableNextSteps") or []],

        # Hydrated from catalog
        "recommendedProducts": rec_products,
    }


def _to_int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _clamp_int(v: Any, lo: int, hi: int, default: int = 0) -> int:
    n = _to_int(v, default)
    return max(lo, min(hi, n))


# ============================================================================
# Provider-specific calls
# ============================================================================

def _call_claude(*, system: str, user_msg: str, model: str | None, settings) -> dict[str, Any]:
    if not settings.anthropic_api_key_clean:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    client = Anthropic(api_key=settings.anthropic_api_key_clean)
    used_model = model or settings.anthropic_model_clean

    # Slim schema fits comfortably in 4500 tokens; keep 6000 as headroom.
    resp = client.messages.create(
        model=used_model,
        max_tokens=6000,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )

    text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(text_parts).strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].lstrip()

    parsed = _extract_json(raw)
    if parsed is None:
        log.error(
            "Claude returned unparseable business plan (stop_reason=%s, len=%d). Raw[:1000]: %s",
            getattr(resp, "stop_reason", None), len(raw), raw[:1000],
        )
        stop = getattr(resp, "stop_reason", "")
        hint = " (output truncated — increase max_tokens)" if stop == "max_tokens" else ""
        raise RuntimeError(f"Claude returned non-JSON{hint}. First 200 chars: {raw[:200]!r}")

    usage = getattr(resp, "usage", None)
    return {
        "output": parsed,
        "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
        "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
        "model": used_model,
        "provider": "claude",
    }


def _call_openai(*, system: str, user_msg: str, model: str | None, settings) -> dict[str, Any]:
    if not settings.openai_api_key_clean:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key_clean)
    used_model = model or settings.openai_model_clean

    resp = client.chat.completions.create(
        model=used_model,
        max_tokens=6000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    )

    choice = resp.choices[0]
    raw = (choice.message.content or "").strip()
    finish_reason = choice.finish_reason

    parsed = _extract_json(raw)
    if parsed is None:
        log.error(
            "OpenAI returned unparseable business plan (finish_reason=%s, len=%d). Raw[:1000]: %s",
            finish_reason, len(raw), raw[:1000],
        )
        hint = " (output truncated — increase max_tokens)" if finish_reason == "length" else ""
        raise RuntimeError(f"OpenAI returned non-JSON{hint}. First 200 chars: {raw[:200]!r}")

    usage = getattr(resp, "usage", None)
    return {
        "output": parsed,
        "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
        "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        "model": used_model,
        "provider": "openai",
    }
