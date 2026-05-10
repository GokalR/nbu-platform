"""Build a downloadable .docx of a generated business plan.

Renders text + tables natively (no embedded charts — those are HTML-only;
users who need charts can use the HTML download).
"""
from __future__ import annotations

from io import BytesIO
from typing import Any

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor


# ---------- shared label dictionaries (mirror standalonePlanHtml.js) ----------
L = {
    "ru": {
        "title": "Бизнес-план",
        "feasibility": "Оценка реалистичности проекта",
        "verdicts": {"high": "Высокая", "medium": "Средняя", "low": "Низкая"},
        "executive": "Резюме",
        "market": "Контекст рынка",
        "metrics": "Финансовые показатели",
        "monthlyRevenue": "Выручка / мес.",
        "monthlyCosts": "Расходы / мес.",
        "monthlyProfit": "Прибыль / мес.",
        "breakeven": "Точка безубыточности",
        "grossMargin": "Валовая маржа",
        "ebitda": "EBITDA маржа",
        "operations": "Операционная деятельность",
        "supplyChain": "Цепочка поставок",
        "criticalDeps": "Критические зависимости",
        "team": "Команда",
        "headcount": "Численность",
        "monthlyPayroll": "ФОТ / мес.",
        "annualPayroll": "ФОТ / год",
        "milestones": "Дорожная карта",
        "first90": "Первые 90 дней",
        "first6": "За 6 месяцев",
        "first12": "За 12 месяцев",
        "risks": "Риски",
        "kpis": "Ключевые показатели (KPI)",
        "products": "Рекомендуемые продукты НБУ",
        "nextSteps": "Что сделать перед визитом в банк",
        "creditScore": "Кредитный скоринг",
        "credit": {
            "verdicts": {
                "high": "Высокая кредитоспособность",
                "medium": "Средняя кредитоспособность",
                "low": "Низкая кредитоспособность",
            },
            "ratioNames": {
                "operatingMargin": "Операционная маржа",
                "netMargin": "Чистая маржа",
                "costToRevenue": "Расходы / выручка",
                "projectEquity": "Доля собственных в проекте",
                "loanToRevenue": "Кредит / годовая выручка",
                "dscr": "Покрытие платежей (DSCR)",
                "paybackYears": "Срок окупаемости",
                "businessAge": "Возраст бизнеса",
            },
            "methodology": (
                "Оценка рассчитана автоматически по 8 показателям из вашей анкеты в "
                "5 группах: прибыльность (операционная и чистая маржа), эффективность "
                "(расходы/выручка), структура капитала (доля собственных, кредит/выручка), "
                "обслуживание долга (DSCR, срок окупаемости), история бизнеса (возраст). "
                "Каждый показатель оценивается 0/1/2 балла, максимум — 16 баллов. "
                "Бэнды: ≥75% — высокая, ≥45% — средняя, <45% — низкая. "
                "Это самодиагностика на основе проектных данных, не решение банка."
            ),
        },
        "months": "мес.",
        "footer": "NBU AI Hub — Генератор бизнес-плана",
    },
    "uz": {
        "title": "Biznes-reja",
        "feasibility": "Loyiha amalga oshirish reytingi",
        "verdicts": {"high": "Yuqori", "medium": "Oʻrtacha", "low": "Past"},
        "executive": "Qisqacha xulosa",
        "market": "Bozor konteksti",
        "metrics": "Moliyaviy koʻrsatkichlar",
        "monthlyRevenue": "Oylik daromad",
        "monthlyCosts": "Oylik xarajat",
        "monthlyProfit": "Oylik foyda",
        "breakeven": "Tenglik nuqtasi",
        "grossMargin": "Yalpi marja",
        "ebitda": "EBITDA marja",
        "operations": "Ishlab chiqarish jarayoni",
        "supplyChain": "Yetkazib berish",
        "criticalDeps": "Asosiy bogʻliqliklar",
        "team": "Jamoa",
        "headcount": "Xodimlar soni",
        "monthlyPayroll": "Oylik ish haqi",
        "annualPayroll": "Yillik ish haqi",
        "milestones": "Reja qadamlari",
        "first90": "Birinchi 90 kun",
        "first6": "6 oy ichida",
        "first12": "12 oy ichida",
        "risks": "Xatarlar",
        "kpis": "Asosiy koʻrsatkichlar (KPI)",
        "products": "Tavsiya etilgan NBU kreditlari",
        "nextSteps": "Keyingi qadamlar — bankka tayyor borish uchun",
        "creditScore": "Kredit skoring",
        "credit": {
            "verdicts": {
                "high": "Yuqori kreditga layoqatlilik",
                "medium": "Oʻrtacha kreditga layoqatlilik",
                "low": "Past kreditga layoqatlilik",
            },
            "ratioNames": {
                "operatingMargin": "Operatsion marja",
                "netMargin": "Sof marja",
                "costToRevenue": "Xarajat / daromad",
                "projectEquity": "Loyihada oʻz ulush",
                "loanToRevenue": "Kredit / yillik daromad",
                "dscr": "Toʻlovlar qoplanishi (DSCR)",
                "paybackYears": "Qaytarilish muddati",
                "businessAge": "Biznes yoshi",
            },
            "methodology": (
                "Baho anketadagi 8 ta koʻrsatkich asosida 5 guruhda avtomatik "
                "hisoblangan: foydalilik (operatsion va sof marja), samaradorlik "
                "(xarajat/daromad), kapital tarkibi (oʻz ulush, kredit/daromad), "
                "qarz xizmati (DSCR, qaytarilish muddati), biznes tarixi (yosh). "
                "Har bir koʻrsatkich 0/1/2 ball bilan baholanadi, maksimum — 16 ball. "
                "Bandlar: ≥75% — yuqori, ≥45% — oʻrtacha, <45% — past. "
                "Bu loyiha maʼlumotlari boʻyicha oʻz-oʻzini diagnostika, bank qarori emas."
            ),
        },
        "months": "oy",
        "footer": "NBU AI Hub — Biznes-reja generatori",
    },
}


# ---------- helpers ----------

def _fmt(n: Any) -> str:
    try:
        return f"{int(n or 0):,}".replace(",", " ")
    except (TypeError, ValueError):
        return "0"


def _fmt_pct(n: Any) -> str:
    try:
        return f"{float(n or 0):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


# Simple "primary" colour for headings — matches the platform navy.
_PRIMARY = RGBColor(0x00, 0x3D, 0x7C)


def _heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.color.rgb = _PRIMARY
        run.font.name = "Calibri"


def _para(doc: Document, text: str, *, bold: bool = False, size: int = 11) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold


def _kv_table(doc: Document, rows: list[tuple[str, str]]) -> None:
    """Two-column key/value table for metrics blocks."""
    if not rows:
        return
    table = doc.add_table(rows=len(rows), cols=2)
    table.style = "Light Grid Accent 1"
    for i, (k, v) in enumerate(rows):
        c0, c1 = table.rows[i].cells
        c0.text = k
        c1.text = v
        for cell in (c0, c1):
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)


def _bullets(doc: Document, items: list[str]) -> None:
    for it in items or []:
        if it:
            doc.add_paragraph(str(it), style="List Bullet")


def _numbered(doc: Document, items: list[str]) -> None:
    for it in items or []:
        if it:
            doc.add_paragraph(str(it), style="List Number")


# ---------- builder ----------

def build_docx(
    *,
    plan: dict[str, Any],
    inputs: dict[str, Any],
    credit_score: dict[str, Any] | None,
    lang: str = "ru",
) -> bytes:
    """Build a .docx and return raw bytes."""
    t = L.get(lang) or L["ru"]
    doc = Document()

    # Title block
    org = (inputs or {}).get("organization") or {}
    org_name = org.get("name") or t["title"]
    title = doc.add_heading(t["title"], level=0)
    for r in title.runs:
        r.font.color.rgb = _PRIMARY
    sub = doc.add_paragraph()
    sub_run = sub.add_run(org_name)
    sub_run.font.size = Pt(14)
    sub_run.font.bold = True

    meta_bits = []
    if org.get("mainActivity"):
        meta_bits.append(org["mainActivity"])
    if org.get("address"):
        meta_bits.append(org["address"])
    if org.get("inn"):
        meta_bits.append(f"ИНН: {org['inn']}")
    if meta_bits:
        m = doc.add_paragraph(" · ".join(meta_bits))
        for r in m.runs:
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Verdict
    verdict = plan.get("feasibilityVerdict", "medium")
    score = plan.get("feasibilityScore", 0)
    _heading(doc, f"{t['feasibility']}: {t['verdicts'].get(verdict, '')} — {score}/100", 1)
    if plan.get("summary"):
        _para(doc, plan["summary"])

    # Executive summary
    if plan.get("executiveSummary"):
        _heading(doc, t["executive"], 1)
        _para(doc, plan["executiveSummary"])

    # Market context
    if plan.get("marketContext"):
        _heading(doc, t["market"], 1)
        _para(doc, plan["marketContext"])

    # Metrics block
    f = plan.get("financials") or {}
    c = f.get("monthlyCosts") or {}
    metric_rows = [
        (t["monthlyRevenue"], f"{_fmt(f.get('monthlyRevenue'))} UZS"),
        (t["monthlyCosts"], f"{_fmt(c.get('total'))} UZS"),
        (t["monthlyProfit"], f"{_fmt(f.get('monthlyProfit'))} UZS"),
        (t["breakeven"], f"{f.get('breakevenMonths', '—')} {t['months']}"),
        (t["grossMargin"], _fmt_pct(f.get("grossMarginPct"))),
        (t["ebitda"], _fmt_pct(f.get("ebitdaMarginPct"))),
    ]
    _heading(doc, t["metrics"], 1)
    _kv_table(doc, metric_rows)

    if f.get("assessment"):
        doc.add_paragraph()
        _para(doc, f["assessment"])

    # Operations
    ops = plan.get("operations") or {}
    if any(ops.values()):
        _heading(doc, t["operations"], 1)
        if ops.get("processFlow"):
            _bullets(doc, ops["processFlow"])
        if ops.get("supplyChain"):
            _para(doc, f"{t['supplyChain']}: {ops['supplyChain']}")
        if ops.get("criticalDependencies"):
            _para(doc, t["criticalDeps"] + ":", bold=True)
            _bullets(doc, ops["criticalDependencies"])

    # Team
    team = plan.get("team") or {}
    if team:
        _heading(doc, t["team"], 1)
        _kv_table(doc, [
            (t["headcount"], str(team.get("totalHeadcount", 0))),
            (t["monthlyPayroll"], f"{_fmt(team.get('monthlyPayroll'))} UZS"),
            (t["annualPayroll"], f"{_fmt(team.get('annualPayroll'))} UZS"),
        ])
        if team.get("assessment"):
            _para(doc, team["assessment"])

    # Milestones
    ms = plan.get("milestones") or {}
    if any(ms.values()):
        _heading(doc, t["milestones"], 1)
        for key, label in (("first90Days", t["first90"]),
                           ("first6Months", t["first6"]),
                           ("first12Months", t["first12"])):
            if ms.get(key):
                _heading(doc, label, 2)
                _bullets(doc, ms[key])

    # Risks
    risks = plan.get("risks") or []
    if risks:
        _heading(doc, t["risks"], 1)
        for r in risks:
            line = f"[{r.get('severity', '').upper()}] {r.get('description', '')}"
            _para(doc, line, bold=True)
            if r.get("mitigation"):
                _para(doc, f"→ {r['mitigation']}")

    # KPIs
    kpis = plan.get("kpis") or []
    if kpis:
        _heading(doc, t["kpis"], 1)
        table = doc.add_table(rows=len(kpis) + 1, cols=3)
        table.style = "Light Grid Accent 1"
        h = table.rows[0].cells
        h[0].text, h[1].text, h[2].text = "Показатель", "Цель", "Периодичность"
        for i, k in enumerate(kpis, start=1):
            row = table.rows[i].cells
            row[0].text = str(k.get("name") or "")
            row[1].text = str(k.get("target") or "")
            row[2].text = str(k.get("frequency") or "")

    # Recommended NBU products
    rec = plan.get("recommendedProducts") or []
    if rec:
        _heading(doc, t["products"], 1)
        for p in rec:
            _heading(doc, str(p.get("name") or ""), 2)
            _kv_table(doc, [
                ("Ставка", str(p.get("rate") or "")),
                ("Срок", str(p.get("term") or "")),
                ("Сумма", str(p.get("amount") or "")),
                ("Цель", str(p.get("purpose") or "")),
            ])
            if p.get("rationale"):
                doc.add_paragraph()
                _para(doc, str(p["rationale"]))

    # Action steps
    steps = plan.get("actionableNextSteps") or []
    if steps:
        _heading(doc, t["nextSteps"], 1)
        _numbered(doc, steps)

    # Credit scoring (if computed)
    if credit_score:
        _heading(doc, t["creditScore"], 1)
        verdict = credit_score.get("verdict", "medium")
        verdict_label = t["credit"]["verdicts"].get(verdict, "")
        _para(
            doc,
            f"{verdict_label} — {credit_score.get('points', 0)}/{credit_score.get('maxPoints', 0)} "
            f"({credit_score.get('percent', 0)}%)",
            bold=True,
        )
        if credit_score.get("summary"):
            _para(doc, credit_score["summary"])

        # Methodology paragraph — explains how the score was computed so the
        # number doesn't read like an authoritative verdict.
        methodology = t["credit"].get("methodology")
        if methodology:
            doc.add_paragraph()
            _para(doc, methodology, size=10)

        ratios = credit_score.get("ratios") or {}
        if ratios:
            doc.add_paragraph()
            table = doc.add_table(rows=len(ratios) + 1, cols=3)
            table.style = "Light Grid Accent 1"
            h = table.rows[0].cells
            h[0].text, h[1].text, h[2].text = "Показатель", "Значение", "Норма"
            ratio_names = t["credit"]["ratioNames"]
            for i, (key, info) in enumerate(ratios.items(), start=1):
                row = table.rows[i].cells
                row[0].text = ratio_names.get(key, key)
                row[1].text = f"{info.get('value', '')}{info.get('unit', '')}"
                row[2].text = str(info.get("benchmark") or "")

    # Footer note
    doc.add_paragraph()
    f_para = doc.add_paragraph()
    f_run = f_para.add_run(t["footer"])
    f_run.font.size = Pt(9)
    f_run.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    f_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
