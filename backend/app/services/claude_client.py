"""Thin wrapper around the Anthropic SDK."""
from __future__ import annotations
import json
from typing import Any

from anthropic import Anthropic

from ..config import get_settings

SYSTEM_PROMPT_RU = """Ты — аналитик МСБ-кредитования НБУ в Узбекистане. На вход получаешь:
  • профиль предпринимателя (возраст, опыт, регион, цель),
  • финансовые ответы из анкеты,
  • (опционально) извлечённые из Excel коэффициенты: маржа, ROA, текущая ликвидность и т.д.,
  • медианы по 4 компаниям-пирам (Фергана, 2025),
  • экономический контекст города/области — либо полные данные (пилотные: Фергана, Маргилан), либо объект {supported:false, note:"..."}.

Верни СТРОГО валидный JSON на русском (или узбекском, если указано) без markdown-обрамления:

{
  "verdict": "good" | "fair" | "weak",
  "summary": "2-3 предложения, конкретика по заявке",
  "strengths": ["3-5 пунктов, по сути ответов пользователя"],
  "weaknesses": ["3-5 пунктов"],
  "peerComparison": [
    {"metric": "Валовая маржа", "user": 0.42, "peerMedian": 0.38, "comment": "выше медианы"}
  ],
  "cityFit": "почему идея подходит/не подходит городу — 2-3 предложения с цифрами из city",
  "recommendedProduct": {"name": "…", "reason": "…"},
  "nextSteps": ["5 конкретных шагов в порядке приоритета"],
  "risks": ["3-5 рисков, релевантных данным пользователя"]
}

Правила:
  • Никогда не выдумывай цифры, не названные во входных данных.
  • Если peerComparison не передан из Excel — верни пустой массив.
  • Если city.supported == false — в cityFit честно скажи, что детальных данных по этому региону пока нет, и дай общую рекомендацию на основе профиля. Не выдумывай экономические показатели для неподдерживаемых регионов.
  • Длина каждого буллета ≤ 160 символов. Избегай общих фраз ("важно составить план") — привязывай к цифрам.
"""

SYSTEM_PROMPT_UZ = """Сен — Ўзбекистондаги НБУ МСБ кредит таҳлилчисисан. Кириш маълумотлари:
  • тадбиркор профили,
  • анкета молиявий жавоблари,
  • (ихтиёрий) Excel'дан чиқарилган коэффициентлар,
  • 4 та пир-компания медианлари (Фарғона, 2025),
  • шаҳар/вилоят иқтисодий контексти (пилот: Фарғона, Марғилон; бошқаси учун {supported:false}).

Фақат валид JSON қайтар (markdown эмас):
{
  "verdict": "good" | "fair" | "weak",
  "summary": "2-3 жумла",
  "strengths": ["3-5 пункт"],
  "weaknesses": ["3-5 пункт"],
  "peerComparison": [{"metric":"…","user":0.4,"peerMedian":0.38,"comment":"…"}],
  "cityFit": "2-3 жумла; city.supported==false бўлса, маълумот йўқлигини очиқ айт",
  "recommendedProduct": {"name":"…","reason":"…"},
  "nextSteps": ["5 қадам, устувор тартибда"],
  "risks": ["3-5 хатар"]
}

Қоидалар:
  • Кириш маълумотларида бўлмаган рақамларни ўйлаб топма.
  • Excel юкланмаган бўлса — peerComparison бўш массив.
  • city.supported==false бўлса, шу ҳудуд бўйича иқтисодий рақамларни ўйлаб топма.
  • Ҳар бир пункт ≤ 160 символ.
"""


def _system_prompt(lang: str) -> str:
    return SYSTEM_PROMPT_UZ if lang == "uz" else SYSTEM_PROMPT_RU


def build_user_message(context: dict[str, Any]) -> str:
    return "ВХОД:\n" + json.dumps(context, ensure_ascii=False, indent=2)


def analyze(context: dict[str, Any], lang: str = "ru", model: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    if not settings.anthropic_api_key_clean:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    client = Anthropic(api_key=settings.anthropic_api_key_clean)
    used_model = model or settings.anthropic_model_clean

    resp = client.messages.create(
        model=used_model,
        max_tokens=settings.anthropic_max_tokens,
        system=_system_prompt(lang),
        messages=[{"role": "user", "content": build_user_message(context)}],
    )

    text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(text_parts).strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].lstrip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude returned non-JSON: {e}. Raw: {raw[:500]}")

    usage = getattr(resp, "usage", None)
    return {
        "output": parsed,
        "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
        "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
        "model": used_model,
    }
