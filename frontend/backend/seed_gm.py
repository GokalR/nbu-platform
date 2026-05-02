"""Seed Golden Mart tables with verified Qoqon + Fergana viloyat data.

Phase A: insert just enough rows to prove the schema works end-to-end.
  - gm_entities: country, fergana region + 4 Fergana cities
  - gm_city: Qoqon 2021–2025 (sector totals from fergana/ PDFs)
  - gm_region: Fergana viloyat 2025 (real-growth indices, section 20)
  - gm_country: empty for now (no national-level data extracted yet)

Verification at the end: SELECT s2_2 FROM gm_city
                        WHERE entity_key='qoqon_city' AND year=2025
should return 9410.4 (industry, mlrd soʻm).

Run:
  cd frontend/backend
  python seed_gm.py
"""
from __future__ import annotations
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

import os
from auth import hash_password
from models import Base, User, engine, async_session
import gm_models  # registers tables  # noqa: F401
from gm_models import GmEntity, GmCity, GmRegion, GmCountry  # noqa: F401

# Default seed admin — override via env vars before running seed in prod
SEED_ADMIN_EMAIL = os.getenv('SEED_ADMIN_EMAIL', 'admin@nbu.uz')
SEED_ADMIN_PASSWORD = os.getenv('SEED_ADMIN_PASSWORD', 'admin12345')
SEED_ADMIN_NAME = os.getenv('SEED_ADMIN_NAME', 'NBU Admin')

log = logging.getLogger("seed_gm")
logging.basicConfig(level=logging.INFO, format="%(message)s")


# ─────────────────────────────────────────────────────────────────────
# Reference: entities (level / parent / display names)
# ─────────────────────────────────────────────────────────────────────
ENTITIES = [
    # Country
    {'key': 'uzbekistan', 'level': 'country', 'parent_key': None,
     'name_ru': 'Узбекистан',         'name_uz': 'Oʻzbekiston',          'iso_kind': None},
    # Regions (viloyats) — only Fergana for now
    {'key': 'fergana_region', 'level': 'region', 'parent_key': 'uzbekistan',
     'name_ru': 'Ферганская область',  'name_uz': 'Fargʻona viloyati',    'iso_kind': 'viloyat'},
    {'key': 'samarqand_region', 'level': 'region', 'parent_key': 'uzbekistan',
     'name_ru': 'Самаркандская область','name_uz': 'Samarqand viloyati',  'iso_kind': 'viloyat'},
    # Fergana viloyat cities (4 shaharlar)
    {'key': 'fargona_city',  'level': 'city', 'parent_key': 'fergana_region',
     'name_ru': 'г. Фергана',          'name_uz': 'Fargʻona shahri',      'iso_kind': 'shahar'},
    {'key': 'qoqon_city',    'level': 'city', 'parent_key': 'fergana_region',
     'name_ru': 'г. Коканд',           'name_uz': 'Qoʻqon shahri',        'iso_kind': 'shahar'},
    {'key': 'margilon_city', 'level': 'city', 'parent_key': 'fergana_region',
     'name_ru': 'г. Маргилан',         'name_uz': 'Margʻilon shahri',     'iso_kind': 'shahar'},
    {'key': 'quvasoy_city',  'level': 'city', 'parent_key': 'fergana_region',
     'name_ru': 'г. Кувасай',          'name_uz': 'Quvasoy shahri',       'iso_kind': 'shahar'},
]


# ─────────────────────────────────────────────────────────────────────
# Qoqon city — verified yearly data 2021..2025 from fergana/ PDFs
# Field map: see frontend/src/data/goldenMart/citySchema.js
# ─────────────────────────────────────────────────────────────────────
# §2 sector volumes (mlrd soʻm) — keys s2_2..s2_7 in citySchema (ВТП is s2_1, null)
QOQON_SECTORS = {
    's2_2': [4340.0, 5602.6, 5886.6, 6264.5, 9410.4],  # Промышленность
    's2_3': [2486.1, 3176.2, 3625.2, 4917.6, 6371.1],  # Услуги
    's2_4': [3451.4, 4077.2, 4986.1, 5713.8, 6589.0],  # Розничная торговля
    's2_5': [ 516.6,  647.4,  770.4,  912.0, 1075.1],  # Строительство
    's2_6': [ 240.6,  233.2,  330.5,  322.1,  382.1],  # Сельское хозяйство
    's2_7': [ 997.9, 1032.3, 1591.5, 1956.6, 4111.2],  # Инвестиции
}
# §1 population (chel.) — yearly: 2021..2026
QOQON_POPULATION = [256_400, 259_700, 303_600, 308_100, 313_600, 319_600]
# §11 vital counts — births / deaths, 2021..2025
QOQON_BIRTHS = [5783, 6561, 7976, 7654, 6923]
QOQON_DEATHS = [1565, 1249, 1499, 1490, 1513]
# §1 age structure (1 yanvar 2025 only)
QOQON_AGE_2025 = {
    's1_12': 22968, 's1_13': 19575, 's1_14': 10777, 's1_15': 43560,
    's1_16': 10769, 's1_17':  9845, 's1_18': 21293, 's1_19': 22670,
    's1_20': 26460, 's1_21': 24048, 's1_22': 39225, 's1_23': 27839,
    's1_24': 22468, 's1_25':  6323, 's1_26':  3533, 's1_27':  1361,
    's1_28':   883,
}
# §1 summary buckets 2025
QOQON_AGE_BUCKETS_2025 = {
    's1_9':  96_880,   # 0–14
    's1_10': 204_617,  # 15–64
    's1_11': 12_100,   # 65+
}

# Fergana viloyat — §20 real-growth indices 2025 (% constant prices)
FERGANA_REAL_GROWTH_2025 = {
    's20_1': 107.3,  # Промышленность
    's20_2': 108.6,  # Услуги
    's20_3': 111.1,  # Розничная торговля
    's20_4': 117.4,  # Строительство
    's20_5': 105.4,  # Сельское хозяйство
    's20_6': 108.1,  # ВРП
}


# ─────────────────────────────────────────────────────────────────────
# Builders
# ─────────────────────────────────────────────────────────────────────
def build_qoqon_rows():
    """Return a list of dicts, one per (entity_key, year) for Qoqon."""
    rows = []
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    for i, year in enumerate(years):
        row = {
            'entity_key': 'qoqon_city',
            'region_key': 'fergana_region',
            'year': year,
            # Static identity (same every year)
            's1_1': 'Qoʻqon',
            's1_2': 'Город',
            's1_3': 'Нет',
            's1_4': 60,                  # km² (constant)
            's1_5': 56,                  # mahallas (constant)
            's1_6': QOQON_POPULATION[i] if i < len(QOQON_POPULATION) else None,
        }
        # Yearly sector volumes (only 2021..2025; 2026 is plan, leave null)
        if i < 5:
            for key, series in QOQON_SECTORS.items():
                row[key] = series[i]
            row['s11_7'] = QOQON_BIRTHS[i]
            row['s11_8'] = QOQON_DEATHS[i]
            # Mirror in §9 (template duplicates these)
            row['s9_5'] = QOQON_BIRTHS[i]
            row['s9_6'] = QOQON_DEATHS[i]
        # Age structure — only 2025
        if year == 2025:
            row.update(QOQON_AGE_2025)
            row.update(QOQON_AGE_BUCKETS_2025)
        rows.append(row)
    return rows


def build_fergana_region_rows():
    """Fergana viloyat — for now just §20 real-growth in 2025."""
    return [{
        'entity_key': 'fergana_region',
        'year': 2025,
        's1_1': 'Фергана',
        **FERGANA_REAL_GROWTH_2025,
    }]


# ─────────────────────────────────────────────────────────────────────
# Insert helpers — use ON CONFLICT DO UPDATE so reseeding is idempotent
# ─────────────────────────────────────────────────────────────────────
async def upsert_entity(session, e):
    stmt = pg_insert(GmEntity).values(**e).on_conflict_do_update(
        index_elements=['key'], set_=e,
    )
    await session.execute(stmt)


async def upsert_city_row(session, row):
    pk = {'entity_key': row['entity_key'], 'year': row['year']}
    update = {k: v for k, v in row.items() if k not in pk}
    stmt = pg_insert(GmCity).values(**row).on_conflict_do_update(
        index_elements=list(pk.keys()), set_=update,
    )
    await session.execute(stmt)


async def upsert_region_row(session, row):
    pk = {'entity_key': row['entity_key'], 'year': row['year']}
    update = {k: v for k, v in row.items() if k not in pk}
    stmt = pg_insert(GmRegion).values(**row).on_conflict_do_update(
        index_elements=list(pk.keys()), set_=update,
    )
    await session.execute(stmt)


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
async def ensure_admin(session) -> None:
    """Create or promote the default admin user (idempotent)."""
    from sqlalchemy import select as _sel
    result = await session.execute(_sel(User).where(User.email == SEED_ADMIN_EMAIL))
    user = result.scalar_one_or_none()
    if user is None:
        session.add(User(
            email=SEED_ADMIN_EMAIL,
            password_hash=hash_password(SEED_ADMIN_PASSWORD),
            full_name=SEED_ADMIN_NAME,
            role='admin',
        ))
        log.info("Created admin user %s (role=admin).", SEED_ADMIN_EMAIL)
    else:
        if user.role != 'admin':
            user.role = 'admin'
            log.info("Promoted existing user %s to admin.", SEED_ADMIN_EMAIL)
        else:
            log.info("Admin user %s already exists.", SEED_ADMIN_EMAIL)


async def seed():
    # Ensure tables exist (idempotent)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Tables ensured.")

    async with async_session() as session:
        # Default admin user (login credentials shown at the end)
        await ensure_admin(session)

        # Entities
        for e in ENTITIES:
            await upsert_entity(session, e)
        log.info("Inserted/updated %d entities.", len(ENTITIES))

        # City — Qoqon 2021..2026
        qoqon_rows = build_qoqon_rows()
        for row in qoqon_rows:
            await upsert_city_row(session, row)
        log.info("Inserted/updated %d gm_city rows for Qoqon.", len(qoqon_rows))

        # Region — Fergana viloyat
        region_rows = build_fergana_region_rows()
        for row in region_rows:
            await upsert_region_row(session, row)
        log.info("Inserted/updated %d gm_region rows for Fergana.", len(region_rows))

        await session.commit()

        # Verification
        result = await session.execute(
            select(GmCity.s2_2).where(
                GmCity.entity_key == 'qoqon_city',
                GmCity.year == 2025,
            )
        )
        industry_2025 = result.scalar_one_or_none()
        log.info("Verification: gm_city[qoqon_city, 2025].s2_2 = %s (expected 9410.4)", industry_2025)
        assert industry_2025 is not None and abs(float(industry_2025) - 9410.4) < 0.01, \
            f"Expected 9410.4, got {industry_2025}"

        result = await session.execute(
            select(GmRegion.s20_4).where(
                GmRegion.entity_key == 'fergana_region',
                GmRegion.year == 2025,
            )
        )
        construction_real = result.scalar_one_or_none()
        log.info("Verification: gm_region[fergana_region, 2025].s20_4 = %s (expected 117.3)", construction_real)

    await engine.dispose()
    log.info("Done.")
    log.info("")
    log.info("=" * 60)
    log.info("ADMIN LOGIN — for /admin/golden-mart")
    log.info("  email:    %s", SEED_ADMIN_EMAIL)
    log.info("  password: %s", SEED_ADMIN_PASSWORD)
    log.info("(override with SEED_ADMIN_EMAIL / SEED_ADMIN_PASSWORD env vars)")
    log.info("=" * 60)


if __name__ == '__main__':
    asyncio.run(seed())
