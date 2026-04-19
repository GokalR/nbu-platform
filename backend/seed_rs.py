"""Idempotent seed script for Regional Strategist reference tables (cities + peer_benchmarks).

Usage: python seed_rs.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Allow running from backend/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db_sync import SessionLocal, engine_sync
from app.models_rs_ref import City, PeerBenchmarkSet
from app.db_sync import BaseSync

# Also import analytics models so create_all creates all tables
import app.models_analytics_ref  # noqa: F401
import app.models_rs_ref  # noqa: F401
import app.models_analytics  # noqa: F401


# ── City data (from backend/app/services/cities.py) ─────────────────

CITIES = {
    "fergana": {
        "name_ru": "Ферганская область",
        "name_uz": "Фарғона вилояти",
        "level": "province",
        "supported": True,
        "data": {
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
                {"country": "Иран", "usdK": 40002.6, "trend": 82.1},
                {"country": "Беларусь", "usdK": 5884.4, "trend": 28.7},
            ],
            "topSectors": [
                {"key": "textile", "nameRu": "Текстиль", "blnUzs": 12338.1},
                {"key": "chemistry", "nameRu": "Химия", "blnUzs": 5354.4},
                {"key": "apparel", "nameRu": "Одежда", "blnUzs": 2841.3},
                {"key": "oilRefining", "nameRu": "Нефтепереработка", "blnUzs": 2290.9},
                {"key": "food", "nameRu": "Пищевая", "blnUzs": 2061.2},
                {"key": "leather", "nameRu": "Кожа и изделия", "blnUzs": 1338.3},
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
    },
    "margilan": {
        "name_ru": "Маргилан",
        "name_uz": "Марғилон",
        "level": "city",
        "supported": True,
        "data": {
            "province": "Ферганская обл.",
            "populationK": 261.9,
            "areaKm2": 52,
            "mahallas": 50,
            "industryBlnUzs": 2459,
            "industryGrowthPct": 71,
            "industryShareOfProvincePct": 4.9,
            "exportsBlnUzs": 450,
            "exportsGrowthPct": 202,
            "tourismAnnual": 380000,
            "smeSharePct": 97,
            "nplPct": 4.6,
            "activeEnterprises": 2787,
            "activeIp": 7143,
            "ipSuspendedSharePct": 43.1,
            "creditPlan2026BlnUzs": 1500,
            "creditPlan2026Jobs": 3614,
            "topSectors": [
                {"key": "textile", "nameRu": "Текстиль (атлас, трикотаж)", "blnUzs": 1320},
                {"key": "apparel", "nameRu": "Швейная", "blnUzs": 430},
                {"key": "food", "nameRu": "Пищевая", "blnUzs": 260},
                {"key": "services", "nameRu": "Услуги и туризм", "blnUzs": 180},
            ],
            "economyStructure": [
                {"key": "retail", "nameRu": "Розница и опт", "pct": 38.2},
                {"key": "services", "nameRu": "Услуги и туризм", "pct": 23.8},
                {"key": "industry", "nameRu": "Промышленность", "pct": 19.4},
                {"key": "construction", "nameRu": "Строительство", "pct": 12.1},
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
    },
}


def seed():
    BaseSync.metadata.create_all(bind=engine_sync)
    db = SessionLocal()
    now = datetime.utcnow()

    try:
        # Seed cities
        for city_id, info in CITIES.items():
            city = City(
                id=city_id,
                name_ru=info["name_ru"],
                name_uz=info["name_uz"],
                level=info["level"],
                supported=info["supported"],
                data_year=2025,
                data=info["data"],
                created_at=now,
                updated_at=now,
            )
            db.merge(city)
        db.flush()
        print(f"Seeded {len(CITIES)} cities: {', '.join(CITIES.keys())}")

        # Seed peer benchmarks from JSON file
        json_path = Path(__file__).resolve().parent / "data" / "peer_benchmarks.json"
        if json_path.exists():
            with json_path.open(encoding="utf-8") as f:
                raw = json.load(f)
            bm = PeerBenchmarkSet(
                id="fergana_sme_2025",
                region="fergana",
                source=raw.get("source", ""),
                benchmarks=raw["benchmarks"],
                companies=raw.get("companies", []),
                created_at=now,
                updated_at=now,
            )
            db.merge(bm)
            print("Seeded 1 benchmark set: fergana_sme_2025")
        else:
            print(f"Warning: {json_path} not found, skipping benchmarks")

        db.commit()
        print("Done.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
