"""LLM wrapper for SME Business Plan generation.

Provider-agnostic: picks Claude (Anthropic) or GPT (OpenAI) based on
LLM_PROVIDER env var. Both call the same RU/UZ system prompt and return
the same JSON schema, so the route doesn't care which one ran.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic

from ..config import get_settings

log = logging.getLogger(__name__)


SYSTEM_PROMPT_RU = """Ты — старший кредитный аналитик НБУ Узбекистана, специализирующийся на МСБ.
На вход получаешь ОДИН JSON с данными анкеты предпринимателя:
  • organization — тип, ИНН, наименование, адрес, дата регистрации, основатель,
    основной вид деятельности, уставный фонд
  • project — цель, локация, собственные средства, сумма кредита, общая стоимость,
    срок (мес.), льготный период (мес.), ставка (%), время до запуска (мес.)
  • assets — основные средства за счёт кредита и за счёт собственных средств
  • products — линейка продуктов/услуг (название, объём в месяц, ед. изм., цена, валюта)
  • team — должности, кол-во, оклад
  • utilities — электричество (кВт·ч), газ (м³), вода (м³), прочие постоянные расходы
  • candidateProducts — 3 наиболее релевантных кредитных продукта НБУ. Выбери из них
    1-2 лучше всего подходящих, НЕ предлагай продукты вне этого списка.

Верни СТРОГО валидный JSON на русском без markdown-обрамления и без комментариев.
Все числовые поля — числа, не строки. Все суммы — в сумах (UZS) без форматирования
(1500000, не "1 500 000 сум").

Схема ответа:

{
  "feasibilityVerdict": "high" | "medium" | "low",
  "feasibilityScore": 0-100,
  "summary": "2-3 предложения: суть проекта + главный вывод о реалистичности",
  "executiveSummary": "1 абзац (4-6 предложений) — краткое описание для руководителя банка",
  "marketContext": "1 абзац — контекст рынка для этой ниши в Узбекистане/регионе с учётом локации проекта; без выдуманных цифр",
  "operations": {
    "processFlow": ["3-5 пунктов: как идёт производство/услуга day-to-day"],
    "supplyChain": "1-2 предложения о ключевых поставщиках/сырье",
    "criticalDependencies": ["2-3 пункта — без чего бизнес встанет"]
  },
  "team": {
    "totalHeadcount": <int>,
    "monthlyPayroll": <int>,
    "annualPayroll": <int>,
    "assessment": "1-2 предложения — адекватен ли штат заявленным объёмам"
  },
  "financials": {
    "monthlyRevenue": <int>,
    "monthlyCosts": {
      "payroll": <int>,
      "utilities": <int>,
      "rawMaterials": <int>,
      "loanPayment": <int>,
      "rent": <int>,
      "other": <int>,
      "total": <int>
    },
    "monthlyProfit": <int>,
    "annualProfit": <int>,
    "breakevenMonths": <int>,
    "grossMarginPct": <float, 0-100>,
    "ebitdaMarginPct": <float, 0-100>,
    "assessment": "2-3 предложения — где маржа, где риск, что вызывает вопросы"
  },
  "projection12m": [
    {"month": 1, "revenue": <int>, "costs": <int>, "profit": <int>}
  ],
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
    {"name": "Название показателя", "target": "Целевое значение с числом", "frequency": "ежедневно" | "еженедельно" | "ежемесячно"}
  ],
  "recommendedProducts": [
    {
      "name": "<точно из candidateProducts.name>",
      "rate": "<точно из candidateProducts.rate>",
      "term": "<точно из candidateProducts.term>",
      "amount": "<точно из candidateProducts.amount>",
      "purpose": "<точно из candidateProducts.purpose>",
      "rationale": "2-3 предложения — почему именно этот продукт под эту заявку (со ссылкой на сумму/цель/срок)",
      "fitScore": 0-100
    }
  ],
  "actionableNextSteps": [
    "5-7 шагов, которые предпринимателю нужно сделать ПРЯМО СЕЙЧАС, чтобы прийти в банк готовым"
  ]
}

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
1. Никогда не выдумывай числа, не указанные во входных данных. Если данных нет — пиши
   "недостаточно данных" в текстовых полях, 0 в числовых, и упоминай это в risks.
2. Все финансовые расчёты должны сходиться: monthlyCosts.total = сумма всех подкатегорий;
   monthlyProfit = monthlyRevenue - monthlyCosts.total.
3. loanPayment рассчитывается аннуитетом из project.loanAmount, project.interestRate,
   project.termMonths, с учётом project.graceMonths (в льготный период — только проценты).
4. utilities в сумах рассчитывай по тарифам Узбекистана 2025 г.: электричество ≈ 900 сум/кВт·ч,
   газ ≈ 1800 сум/м³, вода+канализация ≈ 5500 сум/м³.
5. Не предлагай кредитные продукты вне candidateProducts. Если ни один не подходит —
   recommendedProducts: [] и объясни в risks почему.
6. projection12m обязан содержать ровно 12 объектов; первые startupMonths — выручка ≤ 30%
   от проектной, далее линейный или плавный выход на проектную мощность.
7. Каждое утверждение в assessment / rationale / risks должно ссылаться на конкретное
   поле или число из ввода. Никаких общих фраз ("важно следить за расходами").
8. Тон — деловой, концентрированный, без воды. Каждое поле имеет вес.
9. Длина: executiveSummary ≤ 600 символов, marketContext ≤ 500, summary ≤ 300,
   каждый assessment ≤ 300.
10. risks — 4-6 объектов. kpis — 4-6 объектов. recommendedProducts — 1-2 объекта.
"""


SYSTEM_PROMPT_UZ = """Сен — Ўзбекистон НБУнинг МСБ кредит таҳлили бўйича катта мутахассисисан.
Кириш — ОДНОҚ JSON, тадбиркор анкетаси:
  • organization — тури, ИНН, номи, манзили, рўйхатдан ўтган сана, асосчи,
    асосий фаолият тури, устав фонди
  • project — мақсад, локация, ўз маблағи, кредит миқдори, умумий қиймати,
    муддат (ой), имтиёзли давр (ой), ставка (%), ишга тушиш муддати (ой)
  • assets — кредит ҳисобидан ва ўз ҳисобидан асосий воситалар
  • products — маҳсулот/хизмат рўйхати (номи, ойлик ҳажми, ўлчов бирлиги, нархи, валюта)
  • team — лавозим, сони, ойлик иш ҳақи
  • utilities — электр (кВт·соат), газ (м³), сув (м³), қўшимча доимий харажатлар
  • candidateProducts — 3 та энг мос НБУ кредит маҳсулоти. Шулардан 1-2 тасини танла,
    рўйхатдан ташқари маҳсулот таклиф қилма.

ФАҚАТ валид JSON қайтар (ўзбек тилида, markdown эмас, изоҳсиз). Барча сонли майдонлар —
сон, сатр эмас. Барча суммалар — сўмда (UZS) форматсиз (1500000, "1 500 000 сўм" эмас).

Жавоб схемаси:

{
  "feasibilityVerdict": "high" | "medium" | "low",
  "feasibilityScore": 0-100,
  "summary": "2-3 жумла: лойиҳа моҳияти + реалистиклик хулосаси",
  "executiveSummary": "1 абзац (4-6 жумла) — банк раҳбари учун қисқа баён",
  "marketContext": "1 абзац — Ўзбекистон/минтақадаги бу соҳа учун бозор контексти; ўйлаб топилган рақамлар йўқ",
  "operations": {
    "processFlow": ["3-5 пункт: ишлаб чиқариш/хизмат қандай олиб борилади"],
    "supplyChain": "1-2 жумла — асосий етказиб берувчилар/хом ашё ҳақида",
    "criticalDependencies": ["2-3 пункт — нимасиз бизнес тўхтайди"]
  },
  "team": {
    "totalHeadcount": <int>,
    "monthlyPayroll": <int>,
    "annualPayroll": <int>,
    "assessment": "1-2 жумла — штат ҳажмга мосми"
  },
  "financials": {
    "monthlyRevenue": <int>,
    "monthlyCosts": {
      "payroll": <int>, "utilities": <int>, "rawMaterials": <int>,
      "loanPayment": <int>, "rent": <int>, "other": <int>, "total": <int>
    },
    "monthlyProfit": <int>,
    "annualProfit": <int>,
    "breakevenMonths": <int>,
    "grossMarginPct": <float>,
    "ebitdaMarginPct": <float>,
    "assessment": "2-3 жумла — маржа, хатар, шубҳали жойлар"
  },
  "projection12m": [{"month":1,"revenue":<int>,"costs":<int>,"profit":<int>}],
  "milestones": {
    "first90Days":  ["3-5 аниқ вазифа — рўйхатдан ўтиш, ускуна ўрнатиш, ишга олиш, биринчи ишга тушириш"],
    "first6Months": ["3-5 вазифа — лойиҳавий қувватга чиқиш, маркетинг, илк сотувлар"],
    "first12Months":["3-5 вазифа — кенгайиш, янги каналлар, тенгдошлик нуқтасига чиқиш"]
  },
  "risks": [
    {"type":"market"|"operational"|"financial"|"regulatory",
     "description":"анкета маълумотига боғланган аниқ хатар, ≤140 белги",
     "mitigation":"1 ҳаракат, ≤140 белги",
     "severity":"high"|"medium"|"low"}
  ],
  "kpis": [
    {"name":"Кўрсаткич номи","target":"Рақамли мақсадли қиймат","frequency":"кунлик"|"ҳафталик"|"ойлик"}
  ],
  "recommendedProducts": [
    {
      "name":"<candidateProducts.name дан айнан>",
      "rate":"<candidateProducts.rate дан айнан>",
      "term":"<candidateProducts.term дан айнан>",
      "amount":"<candidateProducts.amount дан айнан>",
      "purpose":"<candidateProducts.purpose дан айнан>",
      "rationale":"2-3 жумла — нега айнан шу маҳсулот мос (сумма/мақсад/муддатга боғлаб)",
      "fitScore":0-100
    }
  ],
  "actionableNextSteps":[
    "5-7 қадам — тадбиркор банкка тайёр келиш учун ҲОЗИРОҚ нима қилиши керак"
  ]
}

ҚАТЪИЙ ҚОИДАЛАР:
1. Кириш маълумотларида бўлмаган рақамларни ўйлаб топма. Маълумот етишмаса —
   матнли майдонларда "маълумот етарли эмас", сонли майдонларда 0, ва risks га ёз.
2. Молиявий ҳисоблар тўғри келсин: monthlyCosts.total = барча кичик категориялар
   йиғиндиси; monthlyProfit = monthlyRevenue - monthlyCosts.total.
3. loanPayment — project.loanAmount, project.interestRate, project.termMonths
   асосида аннуитет билан, project.graceMonths инобатга олиниб (имтиёзли даврда
   фақат фоизлар).
4. utilities — Ўзбекистон 2025 тарифлари: электр ≈ 900 сўм/кВт·соат, газ ≈ 1800
   сўм/м³, сув+канализация ≈ 5500 сўм/м³.
5. candidateProducts дан ташқари маҳсулот таклиф қилма. Ҳеч бири мос келмаса —
   recommendedProducts: [] ва risks да сабабини ёз.
6. projection12m айнан 12 объект; биринчи startupMonths — даромад ≤ лойиҳавий
   қувватнинг 30%, кейин аста-секин чиқиш.
7. assessment / rationale / risks даги ҳар бир жумла кириш маълумотидаги аниқ
   майдон ёки рақамга боғлансин. "Маркетинг муҳим" каби умумий иборалар йўқ.
8. Услуб — иш услуби, ёрқин, сувсиз. Ҳар бир майдон зарур.
9. Узунлик: executiveSummary ≤ 600 белги, marketContext ≤ 500, summary ≤ 300,
   ҳар бир assessment ≤ 300.
10. risks — 4-6 объект. kpis — 4-6 объект. recommendedProducts — 1-2 объект.
"""


def _system_prompt(lang: str) -> str:
    return SYSTEM_PROMPT_UZ if (lang or "uz").lower() == "uz" else SYSTEM_PROMPT_RU


def _build_user_message(payload: dict[str, Any]) -> str:
    return "ВХОД:\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def _extract_json(raw: str) -> dict | None:
    """Best-effort JSON extraction: try strict parse first, then locate the
    outermost {...} block in case Claude wrapped output in prose despite
    instructions. Returns None on total failure.
    """
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


def generate_business_plan(
    *,
    inputs: dict[str, Any],
    candidate_products: list[dict],
    lang: str = "uz",
    model: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    """Generate a business plan via the configured LLM provider.

    Returns {output, input_tokens, output_tokens, model, provider}.
    Raises RuntimeError on config or parse failure (caller logs/persists).
    """
    settings = get_settings()
    used_provider = (provider or settings.llm_provider_clean).lower()

    prompt_payload = {**inputs, "candidateProducts": candidate_products, "lang": lang}
    system = _system_prompt(lang)
    user_msg = _build_user_message(prompt_payload)

    if used_provider == "openai":
        return _call_openai(system=system, user_msg=user_msg, lang=lang, model=model, settings=settings)
    return _call_claude(system=system, user_msg=user_msg, lang=lang, model=model, settings=settings)


def _call_claude(*, system: str, user_msg: str, lang: str, model: str | None, settings) -> dict[str, Any]:
    if not settings.anthropic_api_key_clean:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    client = Anthropic(api_key=settings.anthropic_api_key_clean)
    used_model = model or settings.anthropic_model_clean

    resp = client.messages.create(
        model=used_model,
        # 8000 — full plan with 12-month projection + risks + KPIs is ~5-6k
        # tokens, so 4k truncated mid-JSON and broke parsing.
        max_tokens=8000,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )

    text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(text_parts).strip()

    # Strip accidental markdown fences
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


def _call_openai(*, system: str, user_msg: str, lang: str, model: str | None, settings) -> dict[str, Any]:
    """Same prompt, same JSON schema — but via OpenAI Chat Completions.

    Uses response_format={'type': 'json_object'} so the model is forced to
    return valid JSON. Requires the prompt to mention JSON (it does).
    """
    if not settings.openai_api_key_clean:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    # Imported lazily so deploys without OpenAI installed don't break Claude path.
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key_clean)
    used_model = model or settings.openai_model_clean

    resp = client.chat.completions.create(
        model=used_model,
        max_tokens=8000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    )

    choice = resp.choices[0]
    raw = (choice.message.content or "").strip()
    finish_reason = choice.finish_reason  # 'stop', 'length', etc.

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
