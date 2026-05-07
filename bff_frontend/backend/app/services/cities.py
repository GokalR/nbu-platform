"""City/region context used to ground Claude's analysis."""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

PILOT_IDS = ("fergana", "margilan")

CITIES: dict[str, dict] = {
    "fergana": {
        "id": "fergana",
        "supported": True,
        "level": "province",
        "nameRu": "Ферганская область",
        "nameUz": "Фарғона вилояти",
        "populationK": 4223,
        "areaKm2": 6760,
        "districts": 19,
        "mahallas": 1248,
        "industryBlnUzs": 45896.1,
        "industryGrowthPct": 104.3,
        "investmentsBlnUzs": 19955,
        "investmentsGrowthPct": 29.4,
        "exportsTopPartners": [
            {"country": "Афганистан", "usdK": 53084.9, "trend": 14.6},
            {"country": "Иран",       "usdK": 40002.6, "trend": 82.1},
            {"country": "Беларусь",   "usdK": 5884.4,  "trend": 28.7},
        ],
        "topSectors": [
            {"key": "textile",     "nameRu": "Текстиль",          "blnUzs": 12338.1},
            {"key": "chemistry",   "nameRu": "Химия",             "blnUzs": 5354.4},
            {"key": "apparel",     "nameRu": "Одежда",            "blnUzs": 2841.3},
            {"key": "oilRefining", "nameRu": "Нефтепереработка",  "blnUzs": 2290.9},
            {"key": "food",        "nameRu": "Пищевая",           "blnUzs": 2061.2},
            {"key": "leather",     "nameRu": "Кожа и изделия",    "blnUzs": 1338.3},
        ],
        "strengths": [
            "Крупнейшая промышленная база региона (45,9 трлн сум)",
            "Развитый текстильный и химический кластер",
            "Растущий экспорт в Афганистан и Иран",
        ],
        "challenges": [
            "Неравномерное распределение — 4,9% vs 24,6% между туманами",
            "Зависимость от импорта сырья из Кореи и Индии",
        ],
        "recommendedSectors": ["textiles", "food", "services", "agriculture"],
    },
    "margilan": {
        "id": "margilan",
        "supported": True,
        "level": "city",
        "nameRu": "Маргилан",
        "nameUz": "Марғилон",
        "province": "Ферганская обл.",
        "populationK": 261.9,
        "areaKm2": 52,
        "mahallas": 50,
        "industryBlnUzs": 2459,
        "industryGrowthPct": 71,
        "industryShareOfProvincePct": 4.9,
        "exportsBlnUzs": 450,
        "exportsGrowthPct": 202,
        "tourismAnnual": 380_000,
        "smeSharePct": 97,
        "nplPct": 4.6,
        "activeEnterprises": 2787,
        "activeIp": 7143,
        "ipSuspendedSharePct": 43.1,
        "creditPlan2026BlnUzs": 1500,
        "creditPlan2026Jobs": 3614,
        "topSectors": [
            {"key": "textile",  "nameRu": "Текстиль (атлас, трикотаж)", "blnUzs": 1320},
            {"key": "apparel",  "nameRu": "Швейная",                     "blnUzs": 430},
            {"key": "food",     "nameRu": "Пищевая",                     "blnUzs": 260},
            {"key": "services", "nameRu": "Услуги и туризм",             "blnUzs": 180},
        ],
        "economyStructure": [
            {"key": "retail",       "nameRu": "Розница и опт",     "pct": 38.2},
            {"key": "services",     "nameRu": "Услуги и туризм",   "pct": 23.8},
            {"key": "industry",     "nameRu": "Промышленность",    "pct": 19.4},
            {"key": "construction", "nameRu": "Строительство",     "pct": 12.1},
        ],
        "strengths": [
            "Рекордный экспорт 450 млрд сум (+202%) — атлас, трикотаж, фрукты",
            "Туризм: 380 тыс. гостей в год, 42 объекта",
            "97% экономики — МСБ, низкий порог входа",
            "План NBU: 1,5 трлн сум новых кредитов (×5,6) и 3 614 рабочих мест",
        ],
        "challenges": [
            "43,1% ИП в приостановке — низкая рентабельность розницы",
            "Промпроизводство на душу в 4× ниже Ферганы",
            '"Спящий" бизнес + теневая экономика ~37% активности',
        ],
        "recommendedSectors": ["textiles", "services", "food", "tourism"],
    },
}


def _unsupported(hinted_name: str | None) -> dict:
    return {
        "id": None,
        "supported": False,
        "hintedName": hinted_name,
        "nameRu": hinted_name or "Регион",
        "note": "Детальные данные по этому региону пока недоступны. Пилотные города: Фергана, Маргилан.",
    }


def _from_db(city_id: str, db: Session | None) -> dict | None:
    """Try to load city from DB. Returns None if not found or db unavailable."""
    if db is None:
        return None
    try:
        from ..models_rs_ref import City
        row = db.get(City, city_id)
        if row:
            result = dict(row.data) if row.data else {}
            result.update(id=row.id, supported=row.supported, level=row.level,
                          nameRu=row.name_ru, nameUz=row.name_uz)
            return result
    except Exception as e:
        log.warning("DB city lookup failed for '%s': %s", city_id, e)
    return None


def resolve(city_id: str | None, profile: dict | None = None, db: Session | None = None) -> dict:
    # Try DB first, then hardcoded fallback
    if city_id:
        db_result = _from_db(city_id, db)
        if db_result:
            return db_result
        if city_id in CITIES:
            return CITIES[city_id]

    probe_parts = [str((profile or {}).get(k) or "") for k in ("hudud", "viloyat", "mahalla")]
    probe = " ".join(probe_parts).lower()

    if any(m in probe for m in ("marg", "марғ", "марг")):
        return _from_db("margilan", db) or CITIES["margilan"]
    if any(m in probe for m in ("farg", "фарғ", "ферг", "фарг")):
        return _from_db("fergana", db) or CITIES["fergana"]

    label = next((p for p in probe_parts if p.strip()), None)
    return _unsupported(label)
