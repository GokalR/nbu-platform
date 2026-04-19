"""Idempotent seed script for analytics reference tables (regions + region_data).

Seeds: 1 national + 14 regions + 19 Fergana districts + region_data entries.
Usage: python seed_analytics.py
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db_sync import SessionLocal, engine_sync, BaseSync
from app.models_analytics_ref import Region, RegionData

# Also import other models so create_all creates all tables
import app.models_rs_ref  # noqa: F401
import app.models_analytics  # noqa: F401


# ── National KPIs ────────────────────────────────────────────────────

NATIONAL = {
    "id": "uz",
    "name_ru": "Узбекистан",
    "name_uz": "Oʻzbekiston",
    "level": "national",
    "population_k": 36800,
    "area_km2": 448978,
    "kpis": {
        "population": "36.8 mln",
        "gdpGrowth": "6.5%",
        "gdpDelta": "+6.5%",
        "exports": "$24.4 mlrd",
        "mahallas": 9344,
        "bars": {"industry": 80, "agriculture": 65, "services": 60},
        "employment": {"employed": 85, "selfEmployed": 60, "education": 35},
        "bank": {"credits": 78, "newBusiness": 62, "exporters": 52},
    },
}

# ── 14 Regions (from frontend/src/data/regions.js) ──────────────────

REGIONS = {
    "karakalpakstan": {
        "name_ru": "Каракалпакстан", "name_uz": "Qoraqalpogʻiston",
        "population_k": 1950, "area_km2": 166590,
        "kpis": {
            "population": "1.95 mln", "populationRaw": 1.95, "districts": 16, "area": "166,590 km²",
            "gdpGrowth": "6.4%", "gdpDelta": "+6.4%", "exports": "$0.6 mlrd", "mahallas": 1108,
            "bars": {"industry": 65, "agriculture": 80, "services": 30},
            "employment": {"employed": 70, "selfEmployed": 55, "education": 22},
            "bank": {"credits": 60, "newBusiness": 42, "exporters": 28},
        },
    },
    "khorezm": {
        "name_ru": "Хорезм", "name_uz": "Xorazm",
        "population_k": 1950, "area_km2": 6464,
        "kpis": {
            "population": "1.95 mln", "populationRaw": 1.95, "districts": 11, "area": "6,464 km²",
            "gdpGrowth": "7.1%", "gdpDelta": "+7.1%", "exports": "$0.4 mlrd", "mahallas": 768,
            "bars": {"industry": 55, "agriculture": 88, "services": 38},
            "employment": {"employed": 78, "selfEmployed": 60, "education": 25},
            "bank": {"credits": 58, "newBusiness": 40, "exporters": 22},
        },
    },
    "navoiy": {
        "name_ru": "Навоий", "name_uz": "Navoiy",
        "population_k": 1050, "area_km2": 110990,
        "kpis": {
            "population": "1.05 mln", "populationRaw": 1.05, "districts": 8, "area": "110,990 km²",
            "gdpGrowth": "9.2%", "gdpDelta": "+9.2%", "exports": "$2.4 mlrd", "mahallas": 412,
            "bars": {"industry": 95, "agriculture": 35, "services": 50},
            "employment": {"employed": 82, "selfEmployed": 45, "education": 30},
            "bank": {"credits": 88, "newBusiness": 58, "exporters": 72},
        },
    },
    "bukhara": {
        "name_ru": "Бухара", "name_uz": "Buxoro",
        "population_k": 1980, "area_km2": 40328,
        "kpis": {
            "population": "1.98 mln", "populationRaw": 1.98, "districts": 11, "area": "40,328 km²",
            "gdpGrowth": "7.8%", "gdpDelta": "+7.8%", "exports": "$0.9 mlrd", "mahallas": 982,
            "bars": {"industry": 70, "agriculture": 75, "services": 60},
            "employment": {"employed": 80, "selfEmployed": 62, "education": 33},
            "bank": {"credits": 70, "newBusiness": 50, "exporters": 38},
        },
    },
    "samarqand": {
        "name_ru": "Самарканд", "name_uz": "Samarqand",
        "population_k": 4070, "area_km2": 16773,
        "kpis": {
            "population": "4.07 mln", "populationRaw": 4.07, "districts": 14, "area": "16,773 km²",
            "gdpGrowth": "8.3%", "gdpDelta": "+8.3%", "exports": "$1.1 mlrd", "mahallas": 1568,
            "bars": {"industry": 78, "agriculture": 80, "services": 65},
            "employment": {"employed": 88, "selfEmployed": 70, "education": 42},
            "bank": {"credits": 82, "newBusiness": 65, "exporters": 45},
        },
    },
    "qashqadaryo": {
        "name_ru": "Кашкадарья", "name_uz": "Qashqadaryo",
        "population_k": 3450, "area_km2": 28568,
        "kpis": {
            "population": "3.45 mln", "populationRaw": 3.45, "districts": 14, "area": "28,568 km²",
            "gdpGrowth": "7.5%", "gdpDelta": "+7.5%", "exports": "$1.8 mlrd", "mahallas": 1342,
            "bars": {"industry": 92, "agriculture": 65, "services": 40},
            "employment": {"employed": 80, "selfEmployed": 60, "education": 30},
            "bank": {"credits": 75, "newBusiness": 50, "exporters": 60},
        },
    },
    "surxondaryo": {
        "name_ru": "Сурхандарья", "name_uz": "Surxondaryo",
        "population_k": 2740, "area_km2": 20099,
        "kpis": {
            "population": "2.74 mln", "populationRaw": 2.74, "districts": 14, "area": "20,099 km²",
            "gdpGrowth": "7.0%", "gdpDelta": "+7.0%", "exports": "$0.5 mlrd", "mahallas": 1042,
            "bars": {"industry": 50, "agriculture": 90, "services": 35},
            "employment": {"employed": 75, "selfEmployed": 68, "education": 28},
            "bank": {"credits": 60, "newBusiness": 42, "exporters": 25},
        },
    },
    "jizzax": {
        "name_ru": "Джизак", "name_uz": "Jizzax",
        "population_k": 1450, "area_km2": 21179,
        "kpis": {
            "population": "1.45 mln", "populationRaw": 1.45, "districts": 12, "area": "21,179 km²",
            "gdpGrowth": "8.1%", "gdpDelta": "+8.1%", "exports": "$0.7 mlrd", "mahallas": 632,
            "bars": {"industry": 60, "agriculture": 78, "services": 38},
            "employment": {"employed": 78, "selfEmployed": 58, "education": 32},
            "bank": {"credits": 65, "newBusiness": 48, "exporters": 35},
        },
    },
    "sirdaryo": {
        "name_ru": "Сырдарья", "name_uz": "Sirdaryo",
        "population_k": 880, "area_km2": 4276,
        "kpis": {
            "population": "0.88 mln", "populationRaw": 0.88, "districts": 9, "area": "4,276 km²",
            "gdpGrowth": "8.5%", "gdpDelta": "+8.5%", "exports": "$0.4 mlrd", "mahallas": 388,
            "bars": {"industry": 65, "agriculture": 80, "services": 42},
            "employment": {"employed": 80, "selfEmployed": 55, "education": 28},
            "bank": {"credits": 60, "newBusiness": 38, "exporters": 30},
        },
    },
    "tashkent_region": {
        "name_ru": "Ташкентская область", "name_uz": "Toshkent viloyati",
        "population_k": 3060, "area_km2": 15258,
        "kpis": {
            "population": "3.06 mln", "populationRaw": 3.06, "districts": 15, "area": "15,258 km²",
            "gdpGrowth": "9.5%", "gdpDelta": "+9.5%", "exports": "$2.8 mlrd", "mahallas": 1184,
            "bars": {"industry": 88, "agriculture": 60, "services": 75},
            "employment": {"employed": 90, "selfEmployed": 65, "education": 50},
            "bank": {"credits": 90, "newBusiness": 75, "exporters": 70},
        },
    },
    "tashkent_city": {
        "name_ru": "Ташкент", "name_uz": "Toshkent shahri",
        "population_k": 2930, "area_km2": 335,
        "kpis": {
            "population": "2.93 mln", "populationRaw": 2.93, "districts": 12, "area": "335 km²",
            "gdpGrowth": "10.4%", "gdpDelta": "+10.4%", "exports": "$3.5 mlrd", "mahallas": 524,
            "bars": {"industry": 75, "agriculture": 12, "services": 95},
            "employment": {"employed": 95, "selfEmployed": 60, "education": 70},
            "bank": {"credits": 98, "newBusiness": 92, "exporters": 85},
        },
    },
    "namangan": {
        "name_ru": "Наманган", "name_uz": "Namangan",
        "population_k": 2970, "area_km2": 7440,
        "kpis": {
            "population": "2.97 mln", "populationRaw": 2.97, "districts": 11, "area": "7,440 km²",
            "gdpGrowth": "8.0%", "gdpDelta": "+8.0%", "exports": "$0.8 mlrd", "mahallas": 1118,
            "bars": {"industry": 72, "agriculture": 75, "services": 50},
            "employment": {"employed": 85, "selfEmployed": 70, "education": 38},
            "bank": {"credits": 72, "newBusiness": 60, "exporters": 40},
        },
    },
    "andijan": {
        "name_ru": "Андижан", "name_uz": "Andijon",
        "population_k": 3270, "area_km2": 4303,
        "kpis": {
            "population": "3.27 mln", "populationRaw": 3.27, "districts": 14, "area": "4,303 km²",
            "gdpGrowth": "8.6%", "gdpDelta": "+8.6%", "exports": "$1.4 mlrd", "mahallas": 1244,
            "bars": {"industry": 85, "agriculture": 70, "services": 55},
            "employment": {"employed": 88, "selfEmployed": 72, "education": 42},
            "bank": {"credits": 80, "newBusiness": 68, "exporters": 58},
        },
    },
    "fergana": {
        "name_ru": "Ферганская область", "name_uz": "Fargʻona viloyati",
        "population_k": 3920, "area_km2": 6760,
        "kpis": {
            "population": "3.92 mln", "populationRaw": 3.92, "districts": 15, "cities": 4,
            "area": "6,760 km²",
            "gdpGrowth": "8.7%", "gdpDelta": "+8.7%", "exports": "$1.2 mlrd", "mahallas": 1486,
            "bars": {"industry": 85, "agriculture": 70, "services": 45},
            "employment": {"employed": 92, "selfEmployed": 65, "education": 30},
            "bank": {"credits": 78, "newBusiness": 55, "exporters": 40},
        },
    },
}

# ── 19 Fergana districts (from frontend/src/data/districts.js) ───────

FERGANA_DISTRICTS = [
    {"key": "fargona_city",  "kind": "city",     "population_k": 335.1, "area_km2": 110,  "name_ru": "Фергана",       "name_uz": "Fargʻona shahri"},
    {"key": "margilon_city", "kind": "city",     "population_k": 261.9, "area_km2": 52,   "name_ru": "Маргилан",      "name_uz": "Margʻilon shahri"},
    {"key": "qoqon_city",    "kind": "city",     "population_k": 319.6, "area_km2": 60,   "name_ru": "Коканд",        "name_uz": "Qoʻqon shahri"},
    {"key": "quvasoy_city",  "kind": "city",     "population_k": 104.8, "area_km2": 260,  "name_ru": "Кувасай",       "name_uz": "Quvasoy shahri"},
    {"key": "oltiariq",      "kind": "district", "population_k": 237.3, "area_km2": 630,  "name_ru": "Олтиарик",      "name_uz": "Oltiariq"},
    {"key": "beshariq",      "kind": "district", "population_k": 198.2, "area_km2": 770,  "name_ru": "Бешарик",       "name_uz": "Beshariq"},
    {"key": "bogdod",        "kind": "district", "population_k": 197.5, "area_km2": 340,  "name_ru": "Багдад",        "name_uz": "Bogʻdod"},
    {"key": "buvayda",       "kind": "district", "population_k": 182.3, "area_km2": 280,  "name_ru": "Бувайда",       "name_uz": "Buvayda"},
    {"key": "dangara",       "kind": "district", "population_k": 175.0, "area_km2": 430,  "name_ru": "Дангара",       "name_uz": "Dangara"},
    {"key": "farhona",       "kind": "district", "population_k": 274.5, "area_km2": 590,  "name_ru": "Фурхона",       "name_uz": "Farhona"},
    {"key": "furqat",        "kind": "district", "population_k": 109.3, "area_km2": 310,  "name_ru": "Фуркат",        "name_uz": "Furqat"},
    {"key": "qoshtepa",      "kind": "district", "population_k": 217.8, "area_km2": 370,  "name_ru": "Кўштепа",       "name_uz": "Qoʻshtepa"},
    {"key": "quva",          "kind": "district", "population_k": 296.8, "area_km2": 440,  "name_ru": "Кува",          "name_uz": "Quva"},
    {"key": "rishton",       "kind": "district", "population_k": 210.6, "area_km2": 310,  "name_ru": "Риштан",        "name_uz": "Rishton"},
    {"key": "sox",           "kind": "district", "population_k": 75.3,  "area_km2": 220,  "name_ru": "Сох",           "name_uz": "Sox"},
    {"key": "toshloq",       "kind": "district", "population_k": 178.4, "area_km2": 240,  "name_ru": "Тошлок",        "name_uz": "Toshloq"},
    {"key": "uchkoprik",     "kind": "district", "population_k": 189.5, "area_km2": 270,  "name_ru": "Учкуприк",      "name_uz": "Uchkoʻprik"},
    {"key": "ozbekiston",    "kind": "district", "population_k": 205.1, "area_km2": 670,  "name_ru": "Узбекистан",    "name_uz": "Oʻzbekiston"},
    {"key": "yozyovon",      "kind": "district", "population_k": 167.2, "area_km2": 410,  "name_ru": "Язъяван",       "name_uz": "Yozyovon"},
]

# ── District profiles (from districtAnalytics.js PROFILE) ───────────

PROFILES = {
    "fargona_city":  {"industry": 42, "agri": 8, "services": 32, "trade": 18, "growth": 9.8, "infra": 0.92, "tourism": 0.8, "textile": 0.6, "enclave": False},
    "margilon_city": {"industry": 19.4, "agri": 6.5, "services": 23.8, "trade": 38.2, "growth": 9.1, "infra": 0.86, "tourism": 0.9, "textile": 1.0, "enclave": False},
    "qoqon_city":    {"industry": 40, "agri": 6, "services": 30, "trade": 24, "growth": 8.9, "infra": 0.88, "tourism": 0.8, "textile": 0.5, "enclave": False},
    "quvasoy_city":  {"industry": 64, "agri": 6, "services": 18, "trade": 12, "growth": 8.2, "infra": 0.78, "tourism": 0.3, "textile": 0.2, "enclave": False},
    "oltiariq":      {"industry": 28, "agri": 48, "services": 14, "trade": 10, "growth": 7.8, "infra": 0.58, "tourism": 0.2, "textile": 0.3, "enclave": False},
    "beshariq":      {"industry": 24, "agri": 52, "services": 14, "trade": 10, "growth": 7.2, "infra": 0.55, "tourism": 0.1, "textile": 0.2, "enclave": False},
    "bogdod":        {"industry": 22, "agri": 56, "services": 12, "trade": 10, "growth": 6.9, "infra": 0.52, "tourism": 0.1, "textile": 0.2, "enclave": False},
    "buvayda":       {"industry": 22, "agri": 58, "services": 12, "trade": 8, "growth": 6.8, "infra": 0.50, "tourism": 0.1, "textile": 0.2, "enclave": False},
    "dangara":       {"industry": 26, "agri": 50, "services": 14, "trade": 10, "growth": 7.1, "infra": 0.55, "tourism": 0.2, "textile": 0.4, "enclave": False},
    "farhona":       {"industry": 34, "agri": 40, "services": 16, "trade": 10, "growth": 8.0, "infra": 0.68, "tourism": 0.3, "textile": 0.4, "enclave": False},
    "furqat":        {"industry": 20, "agri": 60, "services": 12, "trade": 8, "growth": 6.5, "infra": 0.48, "tourism": 0.1, "textile": 0.2, "enclave": False},
    "qoshtepa":      {"industry": 32, "agri": 44, "services": 14, "trade": 10, "growth": 7.5, "infra": 0.60, "tourism": 0.2, "textile": 0.3, "enclave": False},
    "quva":          {"industry": 30, "agri": 46, "services": 14, "trade": 10, "growth": 7.6, "infra": 0.62, "tourism": 0.4, "textile": 0.4, "enclave": False},
    "rishton":       {"industry": 34, "agri": 42, "services": 14, "trade": 10, "growth": 7.4, "infra": 0.60, "tourism": 0.9, "textile": 0.3, "enclave": False},
    "sox":           {"industry": 16, "agri": 64, "services": 12, "trade": 8, "growth": 5.8, "infra": 0.38, "tourism": 0.1, "textile": 0.1, "enclave": True},
    "toshloq":       {"industry": 28, "agri": 48, "services": 14, "trade": 10, "growth": 7.3, "infra": 0.58, "tourism": 0.2, "textile": 0.3, "enclave": False},
    "uchkoprik":     {"industry": 26, "agri": 50, "services": 14, "trade": 10, "growth": 7.0, "infra": 0.55, "tourism": 0.1, "textile": 0.2, "enclave": False},
    "ozbekiston":    {"industry": 30, "agri": 46, "services": 14, "trade": 10, "growth": 7.5, "infra": 0.60, "tourism": 0.2, "textile": 0.3, "enclave": False},
    "yozyovon":      {"industry": 24, "agri": 54, "services": 12, "trade": 10, "growth": 6.9, "infra": 0.52, "tourism": 0.1, "textile": 0.2, "enclave": False},
}

# ── REAL_DATA for pilot districts (from districtAnalytics.js) ────────

REAL_DATA = {
    "fargona_city": {
        "populationK": 335.1, "area": 110,
        "industryBln": 8587, "investBln": 4077, "grpBln": 12678,
        "servicesBln": 12317, "tradeBln": 6630, "constructionBln": 3310,
        "avgSalary": 5200, "unemployment": 4.2, "unemploymentStart": 8.5,
        "mahallas": 82, "constructionGrowth": 142.2,
        "tourism": {"visitors": 200, "objects": 28},
        "perCapita": {"industry": 38187, "invest": 21491, "services": 36753, "trade": 19785, "construction": 9878},
        "benchmark": {"industry": 11186, "invest": 4726, "services": 11400, "trade": 9380, "construction": 5100},
        "fiveYear": {
            "industry": [5900, 6200, 6700, 8587, 9016],
            "export": [210, 280, 350, 420, 580],
            "import": [920, 960, 1010, 1050, 980],
            "construction": [132.3, 105.5, 109.1, 142.2, 115.0],
            "migration": [180, 310, 850, 2100, 620],
            "enterprises": [6800, 7200, 7500, 7800, 8100],
            "unemployment": [8.5, 7.2, 6.0, 5.0, 4.2],
            "investments": [2100, 2500, 3200, 4077, 4500],
        },
        "sectors": [
            {"key": "industry", "pct": 25.3}, {"key": "services", "pct": 28.9},
            {"key": "trade", "pct": 24.5}, {"key": "construction", "pct": 12.3},
            {"key": "agri", "pct": 4.5}, {"key": "other", "pct": 4.5},
        ],
        "investSources": [
            {"key": "enterprises", "pct": 38.0}, {"key": "foreign", "pct": 22.0},
            {"key": "govBudget", "pct": 18.0}, {"key": "bankCredits", "pct": 14.0},
            {"key": "population", "pct": 8.0},
        ],
        "entities": {"active": 8100, "inactive": 1200, "opened": 420, "closed": 180, "ie": 5400, "ooo": 1800, "farmer": 450, "other": 450},
        "population": {"workingAge": 180000, "abroad": 4200, "naturalIncrease": 6800},
        "infra": {"water": 95, "sewage": 72, "gas": 98, "roads": 82},
        "topMahallas": ["Markaziy", "Yangi hayot", "Istiqlol", "Bunyodkor", "Do'stlik"],
    },
    "margilon_city": {
        "populationK": 261.9, "area": 52,
        "industryBln": 2459, "investBln": 1281, "grpBln": 5725,
        "servicesBln": 3564, "tradeBln": 5722, "constructionBln": 1807,
        "avgSalary": 3974, "unemployment": 5.8, "unemploymentStart": 9.5,
        "mahallas": 50, "households": 46580, "constructionGrowth": 118.8,
        "tourism": {"visitors": 380, "objects": 42},
        "perCapita": {"industry": 9461, "invest": 4928, "services": 13599, "trade": 21846, "construction": 6899},
        "benchmark": {"industry": 38187, "invest": 21491, "services": 36753, "trade": 19785, "construction": 9878},
        "fiveYear": {
            "industry": [1440, 1554, 1683, 2079, 2459],
            "export": [149, 191, 260, 213, 450],
            "import": [777, 790, 800, 817, 745],
            "construction": [121.9, 88.9, 110.2, 102.7, 118.8],
            "migration": [253, 630, 1772, 6240, 1180],
            "enterprises": [4928, 4200, 3500, 3100, 2787],
            "unemployment": [9.5, 9.0, 7.8, 6.5, 5.8],
            "investments": [780, 910, 1574, 700, 1281],
        },
        "sectors": [
            {"key": "trade", "pct": 38.2}, {"key": "services", "pct": 23.8},
            {"key": "industry", "pct": 19.4}, {"key": "construction", "pct": 12.1},
            {"key": "other", "pct": 6.5},
        ],
        "investSources": [
            {"key": "foreign", "pct": 44.3}, {"key": "enterprises", "pct": 19.1},
            {"key": "govBudget", "pct": 16.0}, {"key": "population", "pct": 13.9},
            {"key": "restoration", "pct": 6.7},
        ],
        "entities": {"active": 2787, "inactive": 3080, "opened": 350, "closed": 752, "ie": 7143, "ooo": 562, "farmer": 84, "other": 120},
        "population": {"workingAge": 140164, "abroad": 15574, "naturalIncrease": 4757, "pensioners": 28315, "migrationBalance": -687},
        "infra": {"water": 99, "sewage": 62, "gas": 89, "roads": 75},
        "topMahallas": ["Kashkar", "Pichoqchi", "Turaqu'rg'on", "Yuksalish", "Go'riavval"],
        "nplRate": 4.6, "socialRegistry": 2602, "socialRegistryPct": 4.2,
        "unregisteredSelfEmployed": 2682, "informalEconomy": 37,
    },
}

# ── Fergana context (from fergana-context.js) ────────────────────────

FERGANA_CONTEXT = {
    "hero": {
        "population": {"value": 4223.0, "unit": "tis. chel.", "year": 2026, "label": {"ru": "Naselenie", "uz": "Aholi"}},
        "industry": {"value": 45896.1, "unit": "mlrd sum", "year": 2024, "delta": "+104.3%", "label": {"ru": "Promishlennost", "uz": "Sanoat hajmi"}},
        "investments": {"value": 19955.0, "unit": "mlrd sum", "year": 2023, "delta": "+29.4%", "label": {"ru": "Investitsii", "uz": "Investitsiyalar"}},
        "area": {"value": 6.76, "unit": "tis. km²", "label": {"ru": "Ploshad", "uz": "Hudud"}},
    },
    "demographics": {"totalK": 4223.0, "urbanK": 2394.9, "ruralK": 1828.2, "urbanShare": 56.7, "marriages2025": 28896, "marriagesCity": 15239, "marriagesVillage": 13657},
    "economy": {
        "industryMlrd2024": 45896.1, "industryGrowth2024": 104.3, "industryPerCapitaK2024": 11185.8,
        "manufacturingGrowth2023": 104.0, "miningGrowth2023": 214.9,
        "investmentsMlrd2023": 19955.0, "investmentGrowth2023": 29.4,
        "ownFundsShare": 61.6, "foreignInvestShare": 12.3, "constructionGrowth2024": 103.9,
    },
    "trade": {"exportIranK": 40002.6, "exportAfghanK": 53084.9, "importKoreaK": 25603.0, "importGermanyK": 24003.7},
    "geography": {"districts": 15, "cities": 9, "villages": 1000, "areaKKm2": 6.76},
    "highlights": {
        "ru": [
            "4,223 тыс. человек населения региона (56.7% — городское)",
            "Промышленность 2024: 45,896 млрд сум (+104.3% за год)",
            "Инвестиции 2023: 19,955 млрд сум (+29.4%)",
            "Обрабатывающая промышленность выросла на 104% в 2023",
            "Площадь региона: 6.76 тыс. км², 15 районов + 4 города",
            "Экспорт в Афганистан: $53 млн, в Иран: $40 млн (2023)",
            "61.6% инвестиций финансируются собственными средствами предприятий",
            "Рост строительства в 2024 — 103.9%",
            "855 текстильных предприятий (stat.uz, Jan-Oct 2021)",
            "Ферганская долина — ключевой текстильный и агропромышленный кластер",
        ],
        "uz": [
            "Regionda 4,223 ming aholi (56.7% — shaharda)",
            "Sanoat 2024: 45,896 mlrd soʻm (+104.3%)",
            "Investitsiyalar 2023: 19,955 mlrd soʻm (+29.4%)",
            "Qayta ishlovchi sanoat 2023 yilda 104% ga oʻsdi",
            "Hudud: 6.76 ming km², 15 tuman + 4 shahar",
            "Eksport: Afgʻoniston $53 mln, Eron $40 mln (2023)",
            "Investitsiyalarning 61.6% — korxonalar oʻz mablagʻlari",
            "2024 yilda qurilish oʻsishi — 103.9%",
            "855 toʻqimachilik korxonasi (stat.uz, 2021)",
            "Fargʻona vodiysi — asosiy toʻqimachilik va agrosanoat klasteri",
        ],
    },
}

# ── Fergana enterprises (from fergana-enterprises.js) ────────────────

FERGANA_ENTERPRISES = {
    "companies": [
        {"name": "Маргиланская шёлковая фабрика", "districtId": "margilon", "type": "production", "workers": 15000, "detail": "22 млн м² шёлка в год"},
        {"name": "Yodgorlik Silk Factory", "districtId": "margilon", "type": "craft", "workers": 2000, "detail": "250 000 м² шёлка ручным способом"},
        {"name": "Global Textile LLC", "districtId": "fargona", "type": "production", "workers": 5000, "detail": "62 000 т трикотажа, контракт с Kiabi"},
        {"name": "Innovative Apparel", "districtId": "qoshtepa", "type": "fdi", "workers": 3500, "detail": "$15 млн FDI (Шри-Ланка), H&M"},
        {"name": "Маргиланский центр ремёсел", "districtId": "margilon", "type": "craft", "workers": 600, "detail": "200+ видов атласа и адраса"},
    ],
    "subsectors": [
        {"name": "Шёлк (атлас, адрас)", "share": 28, "color": "#059669"},
        {"name": "Трикотаж и одежда", "share": 35, "color": "#2957A2"},
        {"name": "Хлопкопереработка", "share": 22, "color": "#D7B56D"},
        {"name": "Ковры и домтекстиль", "share": 15, "color": "#7688A1"},
    ],
}


def seed():
    BaseSync.metadata.create_all(bind=engine_sync)
    db = SessionLocal()
    now = datetime.utcnow()

    try:
        # 1. National row
        db.merge(Region(
            id=NATIONAL["id"], name_ru=NATIONAL["name_ru"], name_uz=NATIONAL["name_uz"],
            level=NATIONAL["level"], population_k=NATIONAL["population_k"],
            area_km2=NATIONAL["area_km2"], status="active", data_year=2025,
            kpis=NATIONAL["kpis"], created_at=now, updated_at=now,
        ))
        print("Seeded national row: uz")

        # 2. 14 regions
        for region_id, info in REGIONS.items():
            db.merge(Region(
                id=region_id, name_ru=info["name_ru"], name_uz=info["name_uz"],
                level="region", parent_id="uz",
                population_k=info["population_k"], area_km2=info["area_km2"],
                status="active", data_year=2025, kpis=info["kpis"],
                created_at=now, updated_at=now,
            ))
        print(f"Seeded {len(REGIONS)} regions")

        # 3. 19 Fergana districts
        for d in FERGANA_DISTRICTS:
            db.merge(Region(
                id=d["key"], name_ru=d["name_ru"], name_uz=d["name_uz"],
                level=d["kind"], kind=d["kind"], parent_id="fergana",
                population_k=d["population_k"], area_km2=d["area_km2"],
                status="active", data_year=2025,
                created_at=now, updated_at=now,
            ))
        print(f"Seeded {len(FERGANA_DISTRICTS)} Fergana districts")

        db.flush()

        # 4. Region data: Fergana context + enterprises
        existing = db.query(RegionData).filter_by(region_id="fergana", data_year=2025).first()
        if existing:
            existing.context = FERGANA_CONTEXT
            existing.enterprises = FERGANA_ENTERPRISES
            existing.updated_at = now
        else:
            db.add(RegionData(
                region_id="fergana", data_year=2025,
                context=FERGANA_CONTEXT, enterprises=FERGANA_ENTERPRISES,
                created_at=now, updated_at=now,
            ))
        print("Seeded Fergana region_data (context + enterprises)")

        # 5. Region data: district profiles + analytics
        for d in FERGANA_DISTRICTS:
            key = d["key"]
            profile = PROFILES.get(key)
            analytics = REAL_DATA.get(key)

            existing = db.query(RegionData).filter_by(region_id=key, data_year=2025).first()
            if existing:
                existing.profile = profile
                existing.analytics = analytics
                existing.updated_at = now
            else:
                db.add(RegionData(
                    region_id=key, data_year=2025,
                    profile=profile, analytics=analytics,
                    created_at=now, updated_at=now,
                ))
        print(f"Seeded {len(FERGANA_DISTRICTS)} district region_data entries")

        db.commit()
        total_regions = 1 + len(REGIONS) + len(FERGANA_DISTRICTS)
        total_data = 1 + len(FERGANA_DISTRICTS)
        print(f"\nDone. Total: {total_regions} regions, {total_data} region_data entries")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
