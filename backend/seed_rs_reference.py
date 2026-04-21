"""Idempotent seed script for Regional Strategist reference tables.

Seeds: cities (enriched with macro context), city_districts, city_enterprises,
credit_products, and peer_benchmarks.

Reads from backend/data/rs_seed/*.json and backend/data/peer_benchmarks.json.

Usage: python seed_rs_reference.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db_sync import BaseSync, SessionLocal, engine_sync
from app.models_rs_ref import (
    City,
    CityDistrict,
    CityEnterprise,
    CreditProduct,
    PeerBenchmarkSet,
)

# Import other model modules so create_all sees every table.
import app.models_analytics  # noqa: F401
import app.models_analytics_ref  # noqa: F401
import app.models_rs_ref  # noqa: F401


DATA_DIR = Path(__file__).resolve().parent / "data"
SEED_DIR = DATA_DIR / "rs_seed"


def _load_json(path: Path):
    if not path.exists():
        print(f"  skip: {path} not found")
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def seed_cities(db, now):
    payload = _load_json(SEED_DIR / "cities.json")
    if not payload:
        return 0
    count = 0
    for city_id, info in payload.items():
        db.merge(
            City(
                id=city_id,
                name_ru=info["name_ru"],
                name_uz=info["name_uz"],
                level=info["level"],
                supported=info.get("supported", True),
                data_year=info.get("data_year", 2025),
                data=info["data"],
                created_at=now,
                updated_at=now,
            )
        )
        count += 1
    return count


def seed_districts(db, now):
    payload = _load_json(SEED_DIR / "fergana_districts.json")
    if not payload:
        return 0
    for row in payload:
        db.merge(
            CityDistrict(
                id=f"{row['city_id']}:{row['id']}",
                city_id=row["city_id"],
                name_ru=row["name_ru"],
                name_uz=row["name_uz"],
                sort_order=row.get("sort_order", 0),
                data=row["data"],
                created_at=now,
                updated_at=now,
            )
        )
    return len(payload)


def seed_enterprises(db, now):
    payload = _load_json(SEED_DIR / "fergana_enterprises.json")
    if not payload:
        return 0
    for row in payload:
        db.merge(
            CityEnterprise(
                id=row["id"],
                city_id=row["city_id"],
                sector=row["sector"],
                name=row["name"],
                district_id=row.get("district_id"),
                data=row["data"],
                created_at=now,
                updated_at=now,
            )
        )
    return len(payload)


def seed_credit_products(db, now):
    payload = _load_json(SEED_DIR / "credit_products.json")
    if not payload:
        return 0
    for row in payload:
        db.merge(
            CreditProduct(
                id=row["id"],
                tier=row["tier"],
                sort_order=row.get("sort_order", 0),
                data=row["data"],
                created_at=now,
                updated_at=now,
            )
        )
    return len(payload)


def seed_benchmarks(db, now):
    path = DATA_DIR / "peer_benchmarks.json"
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    db.merge(
        PeerBenchmarkSet(
            id="fergana_sme_2025",
            region="fergana",
            source=raw.get("source", ""),
            benchmarks=raw["benchmarks"],
            companies=raw.get("companies", []),
            created_at=now,
            updated_at=now,
        )
    )
    return 1


def seed():
    BaseSync.metadata.create_all(bind=engine_sync)
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        print("Seeding cities…")
        n = seed_cities(db, now)
        db.flush()
        print(f"  cities: {n}")

        print("Seeding city_districts…")
        n = seed_districts(db, now)
        db.flush()
        print(f"  city_districts: {n}")

        print("Seeding city_enterprises…")
        n = seed_enterprises(db, now)
        db.flush()
        print(f"  city_enterprises: {n}")

        print("Seeding credit_products…")
        n = seed_credit_products(db, now)
        db.flush()
        print(f"  credit_products: {n}")

        print("Seeding peer_benchmarks…")
        n = seed_benchmarks(db, now)
        db.flush()
        print(f"  peer_benchmarks: {n}")

        db.commit()
        print("Done.")
    except Exception as exc:
        db.rollback()
        print(f"Error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
