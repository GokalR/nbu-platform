"""
Business Questionnaire Platform — FastAPI Backend
Bilingual: Russian + Uzbek
Storage: Excel files (questions.xlsx, responses.xlsx)
External data: Руйхат-2 (1).xlsx, Туман + МФЙ.xlsx
"""

import functools
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent          # …/platform/backend/app
DATA_DIR = BASE_DIR / "data"
QUESTIONS_PATH = DATA_DIR / "questions.xlsx"
RESPONSES_PATH = DATA_DIR / "responses.xlsx"

DATA_DIR.mkdir(exist_ok=True)

# External data directory (set via env var or auto-detected)
_EXTERNAL_DATA_DIR = os.getenv("EXTERNAL_DATA_DIR", "")

def _find_external(filename: str) -> Optional[Path]:
    """Search for an external Excel file in several candidate locations."""
    candidates: List[Path] = []

    # 1) Explicit env var
    if _EXTERNAL_DATA_DIR:
        candidates.append(Path(_EXTERNAL_DATA_DIR) / filename)

    # 2) platform/ folder (same level as backend/) and NBU root
    #    BASE_DIR = platform/backend/app → up 2 = platform/ → up 3 = NBU/
    platform = BASE_DIR.parent.parent          # …/platform/
    nbu      = BASE_DIR.parent.parent.parent   # …/NBU/
    candidates.append(platform / filename)
    candidates.append(nbu / "платформа" / filename)
    candidates.append(nbu / filename)

    # 3) DATA_DIR itself (user may have copied the files here)
    candidates.append(DATA_DIR / filename)

    for p in candidates:
        if p.exists():
            return p
    return None


# ── App & CORS ─────────────────────────────────────────────────────────────────
app = FastAPI(title="Business Questionnaire API", version="1.1.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ───────────────────────────────────────────────────────────
class ClientInfo(BaseModel):
    """Auto-filled from Руйхат-2 lookup."""
    company_name: str = ""
    director: str = ""
    reg_address: str = ""
    phone: str = ""
    turnover_debit: str = ""
    turnover_credit: str = ""
    turnover_all: str = ""
    shareholders_count: str = ""
    accountant: str = ""
    activity_type: str = ""
    sal_sum: str = ""


class GeneralFormData(BaseModel):
    """Full Опросник general info submitted by the user."""
    company_name: str = ""
    inn: str = ""
    reg_address: str = ""
    charter_type: str = ""
    founders_count: int = 1
    founders: List[str] = []
    director: str = ""
    phone: str = ""
    activity_type: str = ""
    turnover_all: str = ""
    turnover_debit: str = ""
    turnover_credit: str = ""
    shareholders_count: str = ""
    accountant: str = ""
    sal_sum: str = ""
    related_companies_count: int = 0
    related_companies_inns: List[str] = []
    credits_count: int = 0
    credit_amount: str = ""
    sphere_count: int = 1


class AnswerItem(BaseModel):
    question_id: str
    question_text_ru: str
    question_text_uz: str
    answer: str


class SphereSubmission(BaseModel):
    sphere_number: int
    category_id: str
    category_name_ru: str
    category_name_uz: str
    answers: List[AnswerItem]


class SubmissionRequest(BaseModel):
    pinfl_or_inn: str
    sphere_count: int
    spheres: List[SphereSubmission]
    client_info: Optional[ClientInfo] = None
    general_form: Optional[GeneralFormData] = None

    @validator("pinfl_or_inn")
    def validate_pinfl(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("PINFL/INN must not be empty")
        return v.strip()

    @validator("sphere_count")
    def validate_sphere_count(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("sphere_count must be between 1 and 10")
        return v


# ── Value cleaner (handles NaN, "nan", 0, "0") ────────────────────────────────
def _clean(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return ""
    s = str(val).strip()
    if s.lower() in ("nan", "none", "0", ""):
        return ""
    return s


# ── External data loaders (cached for the process lifetime) ───────────────────
@functools.lru_cache(maxsize=1)
def _load_address_data() -> Dict[str, Dict[str, List[str]]]:
    """Returns {viloyat: {tuman: [mfy_list]}} from Туман + МФЙ.xlsx."""
    path = _find_external("Туман + МФЙ.xlsx")
    if not path:
        return {}
    try:
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
        print(f"[address] Failed to load: {exc}")
        return {}


@functools.lru_cache(maxsize=1)
def _load_client_db() -> Dict[str, Dict[str, str]]:
    """Returns {INN: ClientInfo fields} from Руйхат-2 with all relevant columns."""
    path = _find_external("Руйхат-2 (1).xlsx") or _find_external("Руйхат-2.xlsx")
    if not path:
        return {}
    try:
        needed = {
            "INN", "CLIENT_NAME", "DIRECTOR_NAME", "ADDRESS",
            "PHONE", "MOBILE_PHONE",
            "TURNOVER_DEBIT", "TURNOVER_CREDIT", "TURNOVER_ALL",
            "CNT_FL", "ACCOUNTER_CHIEF_NAME", "SAL_SUM", "OKED.1",
        }
        df = pd.read_excel(path, usecols=lambda c: c in needed)
        df = df.dropna(subset=["INN"])

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

            def _num(attr: str) -> str:
                v = _clean(getattr(row, attr, None))
                if not v:
                    return ""
                # format large numbers with spaces
                try:
                    return "{:,.0f}".format(float(v)).replace(",", " ")
                except Exception:
                    return v

            result[inn] = {
                "company_name":     _clean(getattr(row, "CLIENT_NAME", None)),
                "director":         _clean(getattr(row, "DIRECTOR_NAME", None)),
                "reg_address":      _clean(getattr(row, "ADDRESS", None)),
                "phone":            phone,
                "turnover_debit":   _num("TURNOVER_DEBIT"),
                "turnover_credit":  _num("TURNOVER_CREDIT"),
                "turnover_all":     _num("TURNOVER_ALL"),
                "shareholders_count": _clean(getattr(row, "CNT_FL", None)).rstrip(".0") or "",
                "accountant":       _clean(getattr(row, "ACCOUNTER_CHIEF_NAME", None)),
                "activity_type":    _clean(getattr(row, "OKED.1", None)),
                "sal_sum":          _num("SAL_SUM"),
            }
        return result
    except Exception as exc:
        print(f"[client_db] Failed to load: {exc}")
        return {}


# ── Default questions rows ─────────────────────────────────────────────────────
def _default_rows() -> List[tuple]:
    return [
        # ── Торговое направление / Савдо йўналиши ──────────────────────────────
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "employees_count", "Количество действующих сотрудников", "Фаол ходимлар сони",
         "number", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "activity_type", "Вид деятельности", "Фаолият тури",
         "select",
         "Розничная торговля;Оптовая торговля;Оба вида",
         "Чакана савдо;Улгуржи савдо;Иккаласи ҳам"),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "related_companies_count", "Количество связанных компаний", "Боғлиқ компаниялар сони",
         "number", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "related_company_inn", "Наименование и ИНН связанной компании", "Боғлиқ компания номи ва ИНН",
         "text", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "purchased_goods", "Наименование закупаемых товаров", "Харид қилинадиган товарлар номи",
         "textarea", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "purchase_address", "Адрес закупки товаров", "Товар харид манзили",
         "text", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "financial_problems", "Финансовые затруднения", "Молиявий қийинчиликлар",
         "checkbox",
         "Недостаток оборотных средств;Высокие налоги;Проблемы с кредитованием;Инфляция;Колебания курса валют",
         "Айланма маблағлар етишмаслиги;Юқори солиқлар;Кредитлашдаги муаммолар;Инфляция;Валюта курси ўзгариши"),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "problems_description", "Опишите проблемы подробнее", "Муаммоларни батафсил тавсифланг",
         "textarea", "", ""),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "solutions", "Предложения по решению проблем", "Муаммоларни ҳал қилиш бўйича таклифлар",
         "checkbox",
         "Снижение налоговой нагрузки;Льготное кредитование;Субсидии;Обучение персонала;Цифровизация",
         "Солиқ юкини камайтириш;Имтиёзли кредитлаш;Субсидиялар;Ходимларни ўқитиш;Рақамлаштириш"),
        ("trade", "Торговое направление", "Савдо йўналиши", "ShoppingBag",
         "solutions_comment", "Комментарии к предложениям", "Таклифларга изоҳ",
         "textarea", "", ""),

        # ── Медицинское направление / Тиббиёт йўналиши ────────────────────────
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "employees_count", "Количество действующих сотрудников", "Фаол ходимлар сони",
         "number", "", ""),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "activity_type", "Вид медицинской деятельности", "Тиббий фаолият тури",
         "select",
         "Клиника;Аптека;Лаборатория;Стоматология;Другое",
         "Клиника;Дорихона;Лаборатория;Стоматология;Бошқа"),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "license_available", "Наличие лицензии", "Лицензия мавжудлиги",
         "radio",
         "Да;Нет;В процессе оформления",
         "Ҳа;Йўқ;Расмийлаштириш жараёнида"),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "equipment_problems", "Проблемы с оборудованием", "Жиҳозлар билан муаммолар",
         "checkbox",
         "Устаревшее оборудование;Нехватка запчастей;Высокая стоимость;Сложность обслуживания",
         "Эскирган жиҳозлар;Эҳтиёт қисмлар етишмаслиги;Юқори нарх;Техник хизмат қийинчилиги"),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "financial_problems", "Финансовые затруднения", "Молиявий қийинчиликлар",
         "checkbox",
         "Недостаток оборотных средств;Высокие налоги;Проблемы с кредитованием;Инфляция",
         "Айланма маблағлар етишмаслиги;Юқори солиқлар;Кредитлашдаги муаммолар;Инфляция"),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "problems_description", "Опишите проблемы подробнее", "Муаммоларни батафсил тавсифланг",
         "textarea", "", ""),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "solutions", "Предложения по решению проблем", "Муаммоларни ҳал қилиш бўйича таклифлар",
         "checkbox",
         "Снижение налоговой нагрузки;Льготное кредитование;Субсидии;Обучение персонала",
         "Солиқ юкини камайтириш;Имтиёзли кредитлаш;Субсидиялар;Ходимларни ўқитиш"),
        ("medical", "Медицинское направление", "Тиббиёт йўналиши", "Stethoscope",
         "solutions_comment", "Комментарии к предложениям", "Таклифларга изоҳ",
         "textarea", "", ""),

        # ── Розничная торговля / Чакана савдо ─────────────────────────────────
        ("retail", "Розничная торговля", "Чакана савдо", "ShoppingCart",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("retail", "Розничная торговля", "Чакана савдо", "ShoppingCart",
         "employees_count", "Количество сотрудников", "Ходимлар сони",
         "number", "", ""),
        ("retail", "Розничная торговля", "Чакана савдо", "ShoppingCart",
         "product_type", "Вид товара", "Товар тури",
         "select",
         "Продукты питания;Одежда/обувь;Электроника;Стройматериалы;Другое",
         "Озиқ-овқат;Кийим/пойафзал;Электроника;Қурилиш материаллари;Бошқа"),
        ("retail", "Розничная торговля", "Чакана савдо", "ShoppingCart",
         "problems_description", "Основные проблемы бизнеса", "Бизнесдаги асосий муаммолар",
         "textarea", "", ""),

        # ── Услуги / Хизматлар ─────────────────────────────────────────────────
        ("services", "Услуги", "Хизматлар", "Briefcase",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("services", "Услуги", "Хизматлар", "Briefcase",
         "employees_count", "Количество сотрудников", "Ходимлар сони",
         "number", "", ""),
        ("services", "Услуги", "Хизматлар", "Briefcase",
         "service_type", "Вид услуг", "Хизмат тури",
         "text", "", ""),
        ("services", "Услуги", "Хизматлар", "Briefcase",
         "problems_description", "Основные проблемы", "Асосий муаммолар",
         "textarea", "", ""),

        # ── Общественное питание / Жамоат овқатланиши ─────────────────────────
        ("food", "Общественное питание", "Жамоат овқатланиши", "Utensils",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("food", "Общественное питание", "Жамоат овқатланиши", "Utensils",
         "employees_count", "Количество сотрудников", "Ходимлар сони",
         "number", "", ""),
        ("food", "Общественное питание", "Жамоат овқатланиши", "Utensils",
         "cuisine_type", "Вид кухни", "Ошхона тури",
         "select",
         "Узбекская;Европейская;Фастфуд;Смешанная;Другое",
         "Ўзбек;Европа;Fastfood;Аралаш;Бошқа"),
        ("food", "Общественное питание", "Жамоат овқатланиши", "Utensils",
         "problems_description", "Основные проблемы", "Асосий муаммолар",
         "textarea", "", ""),

        # ── Строительство / Қурилиш ────────────────────────────────────────────
        ("construction", "Строительство", "Қурилиш", "HardHat",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("construction", "Строительство", "Қурилиш", "HardHat",
         "employees_count", "Количество сотрудников", "Ходимлар сони",
         "number", "", ""),
        ("construction", "Строительство", "Қурилиш", "HardHat",
         "construction_type", "Вид строительства", "Қурилиш тури",
         "select",
         "Жилое строительство;Коммерческое;Промышленное;Ремонт",
         "Турар-жой қурилиши;Тижорат;Саноат;Таъмир"),
        ("construction", "Строительство", "Қурилиш", "HardHat",
         "problems_description", "Основные проблемы", "Асосий муаммолар",
         "textarea", "", ""),

        # ── Сельское хозяйство / Қишлоқ хўжалиги ─────────────────────────────
        ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "Wheat",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "Wheat",
         "land_area", "Площадь земли (га)", "Ер майдони (га)",
         "number", "", ""),
        ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "Wheat",
         "crop_type", "Вид культуры / животноводства", "Экин / чорвачилик тури",
         "text", "", ""),
        ("agriculture", "Сельское хозяйство", "Қишлоқ хўжалиги", "Wheat",
         "problems_description", "Основные проблемы", "Асосий муаммолар",
         "textarea", "", ""),

        # ── Логистика / Логистика ──────────────────────────────────────────────
        ("logistics", "Логистика", "Логистика", "Truck",
         "activity_address", "Адрес деятельности", "Фаолият манзили",
         "address_cascade", "", ""),
        ("logistics", "Логистика", "Логистика", "Truck",
         "fleet_size", "Количество транспортных средств", "Транспорт воситалари сони",
         "number", "", ""),
        ("logistics", "Логистика", "Логистика", "Truck",
         "transport_type", "Вид транспорта", "Транспорт тури",
         "select",
         "Грузовой;Пассажирский;Смешанный",
         "Юк;Йўловчи;Аралаш"),
        ("logistics", "Логистика", "Логистика", "Truck",
         "problems_description", "Основные проблемы", "Асосий муаммолар",
         "textarea", "", ""),
    ]


def ensure_questions() -> None:
    if QUESTIONS_PATH.exists():
        return
    df = pd.DataFrame(
        _default_rows(),
        columns=[
            "category_id", "category_ru", "category_uz", "category_icon",
            "question_id", "question_text_ru", "question_text_uz",
            "question_type", "options_ru", "options_uz",
        ],
    )
    df.to_excel(QUESTIONS_PATH, index=False)


# ── Question loader ───────────────────────────────────────────────────────────
def load_questions() -> List[Dict[str, Any]]:
    ensure_questions()
    df = pd.read_excel(QUESTIONS_PATH, dtype=str).fillna("")

    categories: Dict[str, Any] = {}
    for _, row in df.iterrows():
        cat_id = str(row["category_id"]).strip()
        if not cat_id:
            continue
        if cat_id not in categories:
            categories[cat_id] = {
                "id": cat_id,
                "name": {"ru": row["category_ru"], "uz": row["category_uz"]},
                "icon": row.get("category_icon", "Briefcase"),
                "questions": [],
            }
        opts_ru = [o.strip() for o in str(row["options_ru"]).split(";") if o.strip()]
        opts_uz = [o.strip() for o in str(row["options_uz"]).split(";") if o.strip()]
        categories[cat_id]["questions"].append({
            "id": row["question_id"],
            "text": {"ru": row["question_text_ru"], "uz": row["question_text_uz"]},
            "type": row["question_type"],
            "options": {"ru": opts_ru, "uz": opts_uz},
        })
    return list(categories.values())


# ── Submission saver ──────────────────────────────────────────────────────────
def save_submission(data: SubmissionRequest) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ci = data.client_info or ClientInfo()
    rows = []

    for sphere in data.spheres:
        for ans in sphere.answers:
            rows.append({
                "created_at":         ts,
                "pinfl_or_inn":       data.pinfl_or_inn,
                # From Руйхат-2
                "company_name":       ci.company_name,
                "director":           ci.director,
                "accountant":         ci.accountant,
                "reg_address":        ci.reg_address,
                "phone":              ci.phone,
                "activity_type":      ci.activity_type,
                "turnover_all":       ci.turnover_all,
                "turnover_debit":     ci.turnover_debit,
                "turnover_credit":    ci.turnover_credit,
                "sal_sum":            ci.sal_sum,
                "shareholders_count": ci.shareholders_count,
                # Sphere answer
                "sphere_count":       data.sphere_count,
                "sphere_number":      sphere.sphere_number,
                "category_id":        sphere.category_id,
                "category_ru":        sphere.category_name_ru,
                "category_uz":        sphere.category_name_uz,
                "question_id":        ans.question_id,
                "question_text_ru":   ans.question_text_ru,
                "question_text_uz":   ans.question_text_uz,
                "answer":             ans.answer,
            })

    new_df = pd.DataFrame(rows)
    if RESPONSES_PATH.exists():
        existing = pd.read_excel(RESPONSES_PATH)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_excel(RESPONSES_PATH, index=False)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/questions")
def get_questions() -> Dict[str, Any]:
    try:
        return {"categories": load_questions()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/lookup")
def lookup(q: str = Query(..., description="PINFL or INN")) -> Dict[str, Any]:
    """Lookup client data by PINFL/INN from Руйхат-2 Excel file."""
    db = _load_client_db()
    key = q.strip()
    # Strip .0 suffix in case INN was stored as float
    if key.endswith(".0"):
        key = key[:-2]
    record = db.get(key)
    if not record:
        return {"found": False}
    return {"found": True, **record}


@app.get("/address/viloyats")
def get_viloyats() -> Dict[str, Any]:
    """Return sorted list of all viloyats (regions)."""
    data = _load_address_data()
    if not data:
        return {"viloyats": [], "source_found": False}
    return {"viloyats": sorted(data.keys()), "source_found": True}


@app.get("/address/tumans")
def get_tumans(viloyat: str = Query(...)) -> Dict[str, Any]:
    """Return sorted list of tumans (districts) for a given viloyat."""
    data = _load_address_data()
    tumans = sorted(data.get(viloyat, {}).keys())
    return {"tumans": tumans}


@app.get("/address/mfy")
def get_mfy(
    viloyat: str = Query(...),
    tuman: str = Query(...),
) -> Dict[str, Any]:
    """Return sorted list of MFY for a given viloyat+tuman."""
    data = _load_address_data()
    mfy = sorted(data.get(viloyat, {}).get(tuman, []))
    return {"mfy": mfy}


@app.post("/submissions")
def submit(data: SubmissionRequest) -> Dict[str, Any]:
    try:
        available = {c["id"] for c in load_questions()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Cannot load questions: " + str(exc))

    for sphere in data.spheres:
        if sphere.category_id not in available:
            raise HTTPException(
                status_code=400,
                detail=f"Category '{sphere.category_id}' not found",
            )

    try:
        save_submission(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Cannot save: " + str(exc))

    return {"status": "saved", "pinfl_or_inn": data.pinfl_or_inn}


@app.get("/download-responses")
def download_responses() -> FileResponse:
    if not RESPONSES_PATH.exists():
        raise HTTPException(status_code=404, detail="No responses yet")
    return FileResponse(
        path=str(RESPONSES_PATH),
        filename="responses.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
