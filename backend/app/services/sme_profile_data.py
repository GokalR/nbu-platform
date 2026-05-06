"""SME Profile data layer: questions catalogue + Excel reference loaders.

- Questions: hardcoded sphere catalogue (was originally Excel-backed in the
  standalone platform; inlined here so we don't bundle questions.xlsx).
- Reference Excel files (read-only):
    * Руйхат-2 (1).xlsx  → INN/PINFL → client info lookup
    * Туман + МФЙ.xlsx   → viloyat → tuman → MFY cascade
  Both live in backend/data/sme_profile/. Руйхат-2 is gitignored (sensitive
  bank client data); the loader returns gracefully empty dicts when missing.
"""

from __future__ import annotations

import functools
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────
# backend/app/services/sme_profile_data.py → up 3 = backend/
_BACKEND_DIR = Path(__file__).parent.parent.parent
_DATA_DIR = _BACKEND_DIR / "data" / "sme_profile"

_RUYXAT_FILES = ("Руйхат-2 (1).xlsx", "Руйхат-2.xlsx")
_TUMAN_MFY_FILE = "Туман + МФЙ.xlsx"


def _find(filename: str) -> Optional[Path]:
    """Locate a reference Excel file. Honours SME_PROFILE_DATA_DIR env var
    so Railway/R2-mounted volumes can override the default."""
    candidates: List[Path] = []
    override = os.getenv("SME_PROFILE_DATA_DIR", "").strip()
    if override:
        candidates.append(Path(override) / filename)
    candidates.append(_DATA_DIR / filename)
    for p in candidates:
        if p.exists():
            return p
    return None


# ── Value cleaner (handles NaN, "nan", 0, "0") ────────────────────────────
def _clean(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return ""
    s = str(val).strip()
    if s.lower() in ("nan", "none", "0", ""):
        return ""
    return s


# ── Address cascade (виlоят → туман → МФЙ) ────────────────────────────────
@functools.lru_cache(maxsize=1)
def load_address_data() -> Dict[str, Dict[str, List[str]]]:
    """Returns {viloyat: {tuman: [mfy_list]}} from Туман + МФЙ.xlsx."""
    path = _find(_TUMAN_MFY_FILE)
    if not path:
        return {}
    try:
        import pandas as pd  # local import — pandas is heavy
        df = pd.read_excel(path, sheet_name="МФЙ", header=2, usecols=[2, 3, 4])
        df.columns = ["viloyat", "tuman", "mfy"]
        df["viloyat"] = df["viloyat"].ffill()
        df["tuman"] = df["tuman"].ffill()
        df = df.dropna(subset=["mfy"])
        df = df[df["mfy"].astype(str).str.strip().str.len() > 0]
        df = df[df["mfy"].astype(str).str.strip().str.lower() != "nan"]

        result: Dict[str, Dict[str, List[str]]] = {}
        for row in df.itertuples(index=False):
            v = _clean(row.viloyat)
            t = _clean(row.tuman)
            m = _clean(row.mfy)
            if v and t and m:
                result.setdefault(v, {}).setdefault(t, []).append(m)
        return result
    except Exception as exc:
        print(f"[sme_profile.address] load failed: {exc}")
        return {}


# ── Client lookup (Руйхат-2) ──────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def load_client_db() -> Dict[str, Dict[str, str]]:
    """Returns {INN: ClientInfo fields} from Руйхат-2."""
    path: Optional[Path] = None
    for fname in _RUYXAT_FILES:
        path = _find(fname)
        if path:
            break
    if not path:
        return {}

    try:
        import pandas as pd
        needed = {
            "INN", "CLIENT_NAME", "DIRECTOR_NAME", "ADDRESS",
            "PHONE", "MOBILE_PHONE",
            "TURNOVER_DEBIT", "TURNOVER_CREDIT", "TURNOVER_ALL",
            "CNT_FL", "ACCOUNTER_CHIEF_NAME", "SAL_SUM", "OKED.1",
        }
        df = pd.read_excel(path, usecols=lambda c: c in needed)
        df = df.dropna(subset=["INN"])

        def _num(row, attr: str) -> str:
            v = _clean(getattr(row, attr, None))
            if not v:
                return ""
            try:
                return "{:,.0f}".format(float(v)).replace(",", " ")
            except Exception:
                return v

        result: Dict[str, Dict[str, str]] = {}
        for row in df.itertuples(index=False):
            inn = _clean(getattr(row, "INN", None))
            if not inn:
                continue
            if inn.endswith(".0"):
                inn = inn[:-2]
            if not inn:
                continue

            phone = _clean(getattr(row, "PHONE", None))
            if not phone:
                phone = _clean(getattr(row, "MOBILE_PHONE", None))

            shareholders = _clean(getattr(row, "CNT_FL", None))
            if shareholders.endswith(".0"):
                shareholders = shareholders[:-2]

            result[inn] = {
                "company_name":       _clean(getattr(row, "CLIENT_NAME", None)),
                "director":           _clean(getattr(row, "DIRECTOR_NAME", None)),
                "reg_address":        _clean(getattr(row, "ADDRESS", None)),
                "phone":              phone,
                "turnover_debit":     _num(row, "TURNOVER_DEBIT"),
                "turnover_credit":    _num(row, "TURNOVER_CREDIT"),
                "turnover_all":       _num(row, "TURNOVER_ALL"),
                "shareholders_count": shareholders,
                "accountant":         _clean(getattr(row, "ACCOUNTER_CHIEF_NAME", None)),
                "activity_type":      _clean(getattr(row, "OKED.1", None)),
                "sal_sum":            _num(row, "SAL_SUM"),
            }
        return result
    except Exception as exc:
        print(f"[sme_profile.client_db] load failed: {exc}")
        return {}


# ── Question catalogue (sphere-by-sphere) ─────────────────────────────────
# Tuple shape:
# (cat_id, cat_ru, cat_uz, icon, q_id, q_ru, q_uz, q_type, opts_ru, opts_uz)
#
# Icons map to Google Material Symbols (the platform's <AppIcon> uses
# material-symbols-outlined). Keep this list in sync with the steps UI.
_ROWS: List[tuple] = [
    # ── Торговое направление / Савдо йўналиши ──────────────────────────
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "employees_count", "Количество действующих сотрудников", "Фаол ходимлар сони",
     "number", "", ""),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "activity_type", "Вид деятельности", "Фаолият тури",
     "select",
     "Розничная торговля;Оптовая торговля;Оба вида",
     "Чакана савдо;Улгуржи савдо;Иккаласи ҳам"),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "related_companies_count", "Количество связанных компаний", "Боғлиқ компаниялар сони",
     "number", "", ""),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "purchased_goods", "Наименование закупаемых товаров", "Харид қилинадиган товарлар номи",
     "textarea", "", ""),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "purchase_address", "Адрес закупки товаров", "Товар харид манзили",
     "text", "", ""),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "financial_problems", "Финансовые затруднения", "Молиявий қийинчиликлар",
     "checkbox",
     "Недостаток оборотных средств;Высокие налоги;Проблемы с кредитованием;Инфляция;Колебания курса валют",
     "Айланма маблағлар етишмаслиги;Юқори солиқлар;Кредитлашдаги муаммолар;Инфляция;Валюта курси ўзгариши"),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "problems_description", "Опишите проблемы подробнее", "Муаммоларни батафсил тавсифланг",
     "textarea", "", ""),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "solutions", "Предложения по решению проблем", "Муаммоларни ҳал қилиш бўйича таклифлар",
     "checkbox",
     "Снижение налоговой нагрузки;Льготное кредитование;Субсидии;Обучение персонала;Цифровизация",
     "Солиқ юкини камайтириш;Имтиёзли кредитлаш;Субсидиялар;Ходимларни ўқитиш;Рақамлаштириш"),
    ("trade", "Торговое направление", "Савдо йўналиши", "shopping_bag",
     "solutions_comment", "Комментарии к предложениям", "Таклифларга изоҳ",
     "textarea", "", ""),

    # ── Медицинское направление / Тиббиёт йўналиши ────────────────────
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "employees_count", "Количество действующих сотрудников", "Фаол ходимлар сони",
     "number", "", ""),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "activity_type", "Вид медицинской деятельности", "Тиббий фаолият тури",
     "select",
     "Клиника;Аптека;Лаборатория;Стоматология;Другое",
     "Клиника;Дорихона;Лаборатория;Стоматология;Бошқа"),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "license_available", "Наличие лицензии", "Лицензия мавжудлиги",
     "radio",
     "Да;Нет;В процессе оформления",
     "Ҳа;Йўқ;Расмийлаштириш жараёнида"),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "equipment_problems", "Проблемы с оборудованием", "Жиҳозлар билан муаммолар",
     "checkbox",
     "Устаревшее оборудование;Нехватка запчастей;Высокая стоимость;Сложность обслуживания",
     "Эскирган жиҳозлар;Эҳтиёт қисмлар етишмаслиги;Юқори нарх;Техник хизмат қийинчилиги"),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "financial_problems", "Финансовые затруднения", "Молиявий қийинчиликлар",
     "checkbox",
     "Недостаток оборотных средств;Высокие налоги;Проблемы с кредитованием;Инфляция",
     "Айланма маблағлар етишмаслиги;Юқори солиқлар;Кредитлашдаги муаммолар;Инфляция"),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "problems_description", "Опишите проблемы подробнее", "Муаммоларни батафсил тавсифланг",
     "textarea", "", ""),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "solutions", "Предложения по решению проблем", "Муаммоларни ҳал қилиш бўйича таклифлар",
     "checkbox",
     "Снижение налоговой нагрузки;Льготное кредитование;Субсидии;Обучение персонала",
     "Солиқ юкини камайтириш;Имтиёзли кредитлаш;Субсидиялар;Ходимларни ўқитиш"),
    ("medical", "Медицинское направление", "Тиббиёт йўналиши", "medical_services",
     "solutions_comment", "Комментарии к предложениям", "Таклифларга изоҳ",
     "textarea", "", ""),

    # ── Розничная торговля / Чакана савдо ─────────────────────────────
    ("retail", "Розничная торговля", "Чакана савдо", "shopping_cart",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("retail", "Розничная торговля", "Чакана савдо", "shopping_cart",
     "employees_count", "Количество сотрудников", "Ходимлар сони",
     "number", "", ""),
    ("retail", "Розничная торговля", "Чакана савдо", "shopping_cart",
     "product_type", "Вид товара", "Товар тури",
     "select",
     "Продукты питания;Одежда/обувь;Электроника;Стройматериалы;Другое",
     "Озиқ-овқат;Кийим/пойафзал;Электроника;Қурилиш материаллари;Бошқа"),
    ("retail", "Розничная торговля", "Чакана савдо", "shopping_cart",
     "problems_description", "Основные проблемы бизнеса", "Бизнесдаги асосий муаммолар",
     "textarea", "", ""),

    # ── Услуги / Хизматлар ─────────────────────────────────────────────
    ("services", "Услуги", "Хизматлар", "business_center",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("services", "Услуги", "Хизматлар", "business_center",
     "employees_count", "Количество сотрудников", "Ходимлар сони",
     "number", "", ""),
    ("services", "Услуги", "Хизматлар", "business_center",
     "service_type", "Вид услуг", "Хизмат тури",
     "text", "", ""),
    ("services", "Услуги", "Хизматлар", "business_center",
     "problems_description", "Основные проблемы", "Асосий муаммолар",
     "textarea", "", ""),

    # ── Общественное питание / Жамоат овқатланиши ─────────────────────
    ("food", "Общественное питание", "Жамоат овқатланиши", "restaurant",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("food", "Общественное питание", "Жамоат овқатланиши", "restaurant",
     "employees_count", "Количество сотрудников", "Ходимлар сони",
     "number", "", ""),
    ("food", "Общественное питание", "Жамоат овқатланиши", "restaurant",
     "cuisine_type", "Вид кухни", "Ошхона тури",
     "select",
     "Узбекская;Европейская;Фастфуд;Смешанная;Другое",
     "Ўзбек;Европа;Fastfood;Аралаш;Бошқа"),
    ("food", "Общественное питание", "Жамоат овқатланиши", "restaurant",
     "problems_description", "Основные проблемы", "Асосий муаммолар",
     "textarea", "", ""),

    # ── Строительство / Қурилиш ────────────────────────────────────────
    ("construction", "Строительство", "Қурилиш", "engineering",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("construction", "Строительство", "Қурилиш", "engineering",
     "employees_count", "Количество сотрудников", "Ходимлар сони",
     "number", "", ""),
    ("construction", "Строительство", "Қурилиш", "engineering",
     "construction_type", "Вид строительства", "Қурилиш тури",
     "select",
     "Жилое строительство;Коммерческое;Промышленное;Ремонт",
     "Турар-жой қурилиши;Тижорат;Саноат;Таъмир"),
    ("construction", "Строительство", "Қурилиш", "engineering",
     "problems_description", "Основные проблемы", "Асосий муаммолар",
     "textarea", "", ""),

    # ── Сельское хозяйство / Қишлоқ хўжалиги ─────────────────────────
    ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "agriculture",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "agriculture",
     "land_area", "Площадь земли (га)", "Ер майдони (га)",
     "number", "", ""),
    ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "agriculture",
     "crop_type", "Вид культуры / животноводства", "Экин / чорвачилик тури",
     "text", "", ""),
    ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "agriculture",
     "problems_description", "Основные проблемы", "Асосий муаммолар",
     "textarea", "", ""),

    # ── Логистика / Логистика ──────────────────────────────────────────
    ("logistics", "Логистика", "Логистика", "local_shipping",
     "activity_address", "Адрес деятельности", "Фаолият манзили",
     "address_cascade", "", ""),
    ("logistics", "Логистика", "Логистика", "local_shipping",
     "fleet_size", "Количество транспортных средств", "Транспорт воситалари сони",
     "number", "", ""),
    ("logistics", "Логистика", "Логистика", "local_shipping",
     "transport_type", "Вид транспорта", "Транспорт тури",
     "select",
     "Грузовой;Пассажирский;Смешанный",
     "Юк;Йўловчи;Аралаш"),
    ("logistics", "Логистика", "Логистика", "local_shipping",
     "problems_description", "Основные проблемы", "Асосий муаммолар",
     "textarea", "", ""),
]


def load_questions() -> List[Dict[str, Any]]:
    """Group _ROWS into the categories shape the frontend expects."""
    categories: Dict[str, Any] = {}
    for (
        cat_id, cat_ru, cat_uz, icon,
        q_id, q_ru, q_uz, q_type, opts_ru, opts_uz,
    ) in _ROWS:
        if cat_id not in categories:
            categories[cat_id] = {
                "id": cat_id,
                "name": {"ru": cat_ru, "uz": cat_uz},
                "icon": icon,
                "questions": [],
            }
        categories[cat_id]["questions"].append({
            "id": q_id,
            "text": {"ru": q_ru, "uz": q_uz},
            "type": q_type,
            "options": {
                "ru": [o.strip() for o in opts_ru.split(";") if o.strip()],
                "uz": [o.strip() for o in opts_uz.split(";") if o.strip()],
            },
        })
    return list(categories.values())
