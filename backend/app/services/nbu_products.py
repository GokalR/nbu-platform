"""NBU SME credit-product catalog.

Extracted from products.xlsx (the bank's official SME product passports).
Used to filter and recommend appropriate credit products based on the
user's wizard inputs (loan amount, purpose, client type, collateral).

`select_candidates` returns the top 3 best-fitting products which are
passed into the Claude prompt; Claude then picks 1-2 to recommend with
reasoning.
"""

from __future__ import annotations
from typing import Any


# Each product mirrors a row from "Условия продуктов" sheet.
# `purpose_tags` and `category` are added for matching logic.
NBU_PRODUCTS: list[dict[str, Any]] = [
    # --- Облегчённые продукты (Light products) ---
    {
        "id": "express_lombard",
        "category": "light",
        "name": "Экспресс (Ломбардный)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "25%",
        "rate_pct": 25.0,
        "term": "до 5 лет",
        "term_max_months": 60,
        "grace_period": "Нет",
        "amount": "до 3,5 млрд сум (Облегчённый) / до 10 млрд сум (Стандартный)",
        "amount_max_uzs": 3_500_000_000,
        "collateral": ["realty", "vehicle"],
        "purpose": "Любые цели",
        "purpose_tags": ["any", "working_capital", "fixed_assets", "expansion"],
    },
    {
        "id": "imkoniyat",
        "category": "light",
        "name": "Доступный (Имконият)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "23%",
        "rate_pct": 23.0,
        "term": "оборотные до 1,5 лет / основные до 3 лет",
        "term_max_months": 36,
        "grace_period": "до 6 месяцев",
        "amount": "до 150 млн сум (первый) / до 500 млн сум (повторный)",
        "amount_max_uzs": 500_000_000,
        "collateral": ["insurance"],
        "purpose": "На оборотные или основные средства",
        "purpose_tags": ["working_capital", "fixed_assets"],
    },
    {
        "id": "overdraft_light",
        "category": "light",
        "name": "Овердрафт (Облегчённый)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "23%",
        "rate_pct": 23.0,
        "term": "до 1 года",
        "term_max_months": 12,
        "grace_period": "Нет",
        "amount": "до 1 млрд сум",
        "amount_max_uzs": 1_000_000_000,
        "collateral": ["insurance"],
        "purpose": "Любые цели",
        "purpose_tags": ["any", "working_capital"],
    },
    {
        "id": "easy_start",
        "category": "light",
        "name": "Лёгкий старт",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "24%",
        "rate_pct": 24.0,
        "term": "оборотные до 1,5 лет / основные до 3 лет",
        "term_max_months": 36,
        "grace_period": "до 6 месяцев",
        "amount": "до 300 млн сум",
        "amount_max_uzs": 300_000_000,
        "collateral": ["realty", "vehicle", "insurance_partial"],
        "purpose": "На оборотные или основные средства",
        "purpose_tags": ["working_capital", "fixed_assets", "startup"],
    },
    {
        "id": "tezkor",
        "category": "light",
        "name": "Тезкор (Кредит наличными)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "26%",
        "rate_pct": 26.0,
        "term": "до 1,5 лет",
        "term_max_months": 18,
        "grace_period": "до 3 месяцев",
        "amount": "до 1,5 млрд сум",
        "amount_max_uzs": 1_500_000_000,
        "collateral": ["realty", "vehicle"],
        "purpose": "Любые цели",
        "purpose_tags": ["any", "working_capital"],
    },
    {
        "id": "auto_loan",
        "category": "light",
        "name": "Автокредит",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "23%-24%",
        "rate_pct": 23.5,
        "term": "оборотные до 1,5 лет / основные до 3 лет",
        "term_max_months": 36,
        "grace_period": "до 6 месяцев",
        "amount": "до 3,5 млрд сум",
        "amount_max_uzs": 3_500_000_000,
        "collateral": ["vehicle_purchased"],
        "purpose": "Покупка лёгкого автотранспорта и малотоннажных грузовиков",
        "purpose_tags": ["vehicle", "fixed_assets"],
    },
    {
        "id": "rasshiryaisya",
        "category": "light",
        "name": "Расширяйся (Оборотные средства)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "23%-25% (1г-23%, 2г-24%, 3г-25%)",
        "rate_pct": 24.0,
        "term": "до 1,5 лет / до 3 лет ГКС",
        "term_max_months": 36,
        "grace_period": "до 3 месяцев",
        "amount": "до 3,5 млрд сум",
        "amount_max_uzs": 3_500_000_000,
        "collateral": ["realty", "vehicle", "insurance_partial"],
        "purpose": "Пополнение оборотных средств",
        "purpose_tags": ["working_capital", "expansion"],
    },
    {
        "id": "razvivaisya",
        "category": "light",
        "name": "Развивайся (Основные средства)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "23%",
        "rate_pct": 23.0,
        "term": "до 4 лет",
        "term_max_months": 48,
        "grace_period": "до 3 месяцев",
        "amount": "до 3,5 млрд сум",
        "amount_max_uzs": 3_500_000_000,
        "collateral": ["realty", "vehicle", "insurance_partial"],
        "purpose": "Покупка основных средств",
        "purpose_tags": ["fixed_assets", "expansion", "equipment"],
    },
    {
        "id": "biz_mortgage",
        "category": "light",
        "name": "Бизнес ипотека",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "23%-26,5%",
        "rate_pct": 24.75,
        "term": "до 15 лет",
        "term_max_months": 180,
        "grace_period": "Нет",
        "amount": "до 3,5 млрд сум (Облегчённый) / до 10 млрд сум (Стандартный)",
        "amount_max_uzs": 3_500_000_000,
        "collateral": ["realty_purchased"],
        "purpose": "Покупка коммерческой недвижимости от застройщиков",
        "purpose_tags": ["realty", "fixed_assets"],
    },
    # --- Стандартные продукты (Standard products) ---
    {
        "id": "working_capital_std",
        "category": "standard",
        "name": "Оборотный кредит",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "21%-22% (1г-21%, >1г-22%)",
        "rate_pct": 21.5,
        "term": "не ограничено",
        "term_max_months": None,
        "grace_period": "не ограничено",
        "amount": "не ограничено",
        "amount_max_uzs": None,
        "collateral": ["any_legal"],
        "purpose": "Пополнение оборотных средств",
        "purpose_tags": ["working_capital", "expansion"],
    },
    {
        "id": "investment_std",
        "category": "standard",
        "name": "Инвестиционный кредит",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "22%",
        "rate_pct": 22.0,
        "term": "не ограничено",
        "term_max_months": None,
        "grace_period": "не ограничено",
        "amount": "не ограничено",
        "amount_max_uzs": None,
        "collateral": ["any_legal"],
        "purpose": "Покупка основных средств",
        "purpose_tags": ["fixed_assets", "equipment", "expansion"],
    },
    {
        "id": "overdraft_std",
        "category": "standard",
        "name": "Овердрафт (Стандартный)",
        "client_types": ["legal_entity", "individual"],
        "currency": "UZS",
        "rate": "22%",
        "rate_pct": 22.0,
        "term": "до 1 года",
        "term_max_months": 12,
        "grace_period": "до 10 месяцев",
        "amount": "не ограничено",
        "amount_max_uzs": None,
        "collateral": ["any_legal"],
        "purpose": "Любые цели",
        "purpose_tags": ["any", "working_capital"],
    },
]


def _classify_purpose(assets_credit: list[dict], project_purpose: str) -> set[str]:
    """Infer purpose tags from the wizard inputs."""
    tags: set[str] = set()
    if assets_credit:
        # User wants assets financed by credit → fixed assets / equipment
        tags.add("fixed_assets")
        tags.add("equipment")
        # Heuristic: vehicle keyword in any asset name
        for a in assets_credit:
            n = (a.get("name") or "").lower()
            if any(k in n for k in ["avto", "авто", "mashina", "машин", "transport", "транспорт"]):
                tags.add("vehicle")
            if any(k in n for k in ["binoy", "недвиж", "помещ", "obyekt", "ofis", "офис"]):
                tags.add("realty")
    p = (project_purpose or "").lower()
    if any(k in p for k in ["yangi", "ochish", "новое", "открыти", "запуск", "start"]):
        tags.add("startup")
    if not tags:
        tags.add("working_capital")
    return tags


def select_candidates(
    *,
    loan_amount_uzs: float,
    term_months: int,
    client_type: str,           # "legal_entity" or "individual"
    assets_credit: list[dict],  # rows from wizard step 4 (credit-financed)
    project_purpose: str = "",
    top_n: int = 3,
) -> list[dict]:
    """Score products against user inputs, return top_n candidates.

    Scoring:
      +30 if amount fits within product limit
      +20 per matching purpose tag (capped at +40)
      +15 if term fits within product term_max_months
      +10 if client_type supported
      +5  if "light" category and loan ≤ 3.5 bn (light products are easier to get)
      -100 if client_type not supported (effectively excluded)
    """
    target_tags = _classify_purpose(assets_credit, project_purpose)

    scored: list[tuple[float, dict]] = []
    for p in NBU_PRODUCTS:
        if client_type not in p["client_types"]:
            continue

        score = 10.0  # base, since client_type already supported

        if p["amount_max_uzs"] is None or loan_amount_uzs <= p["amount_max_uzs"]:
            score += 30.0
        else:
            # Loan exceeds light product cap — penalise but don't exclude
            score -= 20.0

        if p["term_max_months"] is None or term_months <= p["term_max_months"]:
            score += 15.0
        else:
            score -= 15.0

        tag_overlap = len(target_tags & set(p["purpose_tags"]))
        score += min(tag_overlap * 20.0, 40.0)

        if p["category"] == "light" and loan_amount_uzs <= 3_500_000_000:
            score += 5.0

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [_public_view(p) for _, p in scored[:top_n]]


def _public_view(p: dict) -> dict:
    """Strip internal fields before sending to Claude / frontend."""
    return {
        "id": p["id"],
        "name": p["name"],
        "category": p["category"],
        "rate": p["rate"],
        "term": p["term"],
        "grace_period": p["grace_period"],
        "amount": p["amount"],
        "collateral": p["collateral"],
        "purpose": p["purpose"],
        "currency": p["currency"],
    }
