"""Seed verified Golden Mart values into Railway Postgres on backend startup.

Called from main.py lifespan after gm_entities is ensured. Idempotent:
uses INSERT ... ON CONFLICT DO NOTHING so admin edits via the panel
don't get clobbered on later redeploys. To re-import (overwrite local
edits), run a separate manual reset script.

What we seed:
  - gm_city/qoqon_city: 6 rows (2021..2026) with sector totals, population,
    vital counts, age structure 2025, identity fields (mahallas, area, etc.)
  - gm_city/fargona_city: same shape, Fergana shahri verified values
  - gm_city/margilon_city: same shape, Margʻilon shahri values
  - gm_region/fergana_region: 2025 row with real-growth indices (§20)

Source of values: verified rows from fergana/-folder PDFs (farstat.uz
Jan-Dec 2025 preliminary), same numbers that frontend qoqon.js carries.
"""
from __future__ import annotations
import logging

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db_async import async_session, engine_async
from . import models_gm as gm

log = logging.getLogger("seed_gm_data")


# ────────────────────────────────────────────────────────────────────
# QOQON CITY — verified yearly data 2021..2025 from fergana/-PDFs
# ────────────────────────────────────────────────────────────────────
QOQON_YEARLY_SECTORS = {
    # field_key: [2021, 2022, 2023, 2024, 2025] (mlrd soʻm)
    's2_2': [4340.0, 5602.6, 5886.6, 6264.5, 9410.4],  # Промышленность
    's2_3': [2486.1, 3176.2, 3625.2, 4917.6, 6371.1],  # Услуги
    's2_4': [3451.4, 4077.2, 4986.1, 5713.8, 6589.0],  # Розничная торговля
    's2_5': [ 516.6,  647.4,  770.4,  912.0, 1075.1],  # Строительство
    's2_6': [ 240.6,  233.2,  330.5,  322.1,  382.1],  # Сельское хозяйство
    's2_7': [ 997.9, 1032.3, 1591.5, 1956.6, 4111.2],  # Инвестиции
}
# §1 population (chel., 1 yanvar each year): 2021..2026
QOQON_POPULATION = [256_400, 259_700, 303_600, 308_100, 313_600, 319_600]
# §11 absolute vital counts (also mirrored in §9)
QOQON_BIRTHS = [5783, 6561, 7976, 7654, 6923]
QOQON_DEATHS = [1565, 1249, 1499, 1490, 1513]
# §1 age structure — 1 yanvar 2025 snapshot only
QOQON_AGE_2025 = {
    's1_12': 22968, 's1_13': 19575, 's1_14': 10777, 's1_15': 43560,
    's1_16': 10769, 's1_17':  9845, 's1_18': 21293, 's1_19': 22670,
    's1_20': 26460, 's1_21': 24048, 's1_22': 39225, 's1_23': 27839,
    's1_24': 22468, 's1_25':  6323, 's1_26':  3533, 's1_27':  1361,
    's1_28':   883,
}

# Identity fields — same every year for Qoqon.
#  • Enum fields (s1_2, s1_3) store language-agnostic codes; UI translates.
#  • Free-form text (s1_1 Название) is bilingual — both s1_1 (RU) + s1_1_uz (UZ).
QOQON_IDENTITY = {
    's1_1':    'Коканд',  # Название (RU)
    's1_1_uz': 'Qoʻqon',  # Название (UZ)
    's1_2': 'city',       # Тип объекта → enum
    's1_3': 'no',         # Админ. центр → enum
    's1_4': 60,           # Площадь, km²
    's1_5': 56,           # Махаллей
}


# ────────────────────────────────────────────────────────────────────
# FERGANA SHAHRI — verified
# ────────────────────────────────────────────────────────────────────
FERGANA_YEARLY_SECTORS = {
    's2_2': [7075.5, 6935.4, 10296.9, 11303.3, 12666.6],
    's2_3': [4387.5, 5574.6,  6744.2,  9299.6, 12191.0],
    's2_4': [2897.4, 3603.3,  4603.2,  5396.3,  6562.8],
    's2_5': [1742.5, 2463.6,  2928.6,  2872.2,  3276.6],
    's2_6': [ 587.3,  654.8,   754.6,   833.1,  1020.3],
    's2_7': [3139.8, 4077.4,  4976.4,  5183.2,  7128.4],
}
FERGANA_POPULATION = [293_500, 299_200, 314_500, 321_800, 328_400, 335_100]
FERGANA_BIRTHS = [6291, 6893, 7373, 6871, 6226]
FERGANA_DEATHS = [1751, 1901, 1740, 1750, 1786]
FERGANA_IDENTITY = {
    's1_1':    'Фергана',
    's1_1_uz': 'Fargʻona',
    's1_2': 'city',
    's1_3': 'yes',
    's1_4': 110,
    's1_5': 74,
}
FERGANA_AGE_2025 = {
    's1_12': 20784, 's1_13': 17391, 's1_14': 9615, 's1_15': 40235,
    's1_16': 10515, 's1_17':  8374, 's1_18': 22037, 's1_19': 28537,
    's1_20': 32224, 's1_21': 28005, 's1_22': 41543, 's1_23': 32395,
    's1_24': 25517, 's1_25':  6073, 's1_26':  3312, 's1_27':   869,
    's1_28':   983,
}


# ────────────────────────────────────────────────────────────────────
# MARGILON SHAHRI — verified
# ────────────────────────────────────────────────────────────────────
MARGILAN_YEARLY_SECTORS = {
    's2_2': [1440.0, 1419.9, 1660.3, 1931.0, 2458.9],
    's2_3': [1234.1, 1522.5, 1915.5, 2704.6, 3534.5],
    's2_4': [2919.5, 3474.6, 4239.7, 4794.3, 5677.8],
    's2_5': [1123.1, 1087.6, 1385.5, 1470.6, 1793.1],
    's2_6': [ 372.3,  407.8,  497.6,  549.0,  620.6],
    's2_7': [ 834.8,  480.5,  797.2,  674.2, 1280.9],
}
MARGILAN_POPULATION = [238_900, 242_500, 246_700, 253_500, 257_900, 261_900]
MARGILAN_BIRTHS = [5917, 6493, 6570, 6417, 5917]
MARGILAN_DEATHS = [1241, 1195, 1191, 1093, 1160]
MARGILAN_IDENTITY = {
    's1_1':    'Маргилан',
    's1_1_uz': 'Margʻilon',
    's1_2': 'city',
    's1_3': 'no',
    's1_4': 52,
    's1_5': 50,
}
MARGILAN_AGE_2025 = {
    's1_12': 19432, 's1_13': 17101, 's1_14': 10777, 's1_15': 35668,
    's1_16': 10769, 's1_17':  9845, 's1_18': 21293, 's1_19': 22670,
    's1_20': 26460, 's1_21': 24048, 's1_22': 39225, 's1_23': 27839,
    's1_24': 22468, 's1_25':  6323, 's1_26':  3533, 's1_27':  1361,
    's1_28':   883,
}


# ────────────────────────────────────────────────────────────────────
# FERGANA REGION — §20 real-growth indices 2025 (% constant prices)
# ────────────────────────────────────────────────────────────────────
FERGANA_REGION_2025 = {
    's1_1': 'Фергана',
    's20_1': 107.3,  # Промышленность – реальный рост
    's20_2': 108.6,  # Услуги
    's20_3': 111.1,  # Розничная торговля
    's20_4': 117.4,  # Строительство
    's20_5': 105.4,  # Сельское хозяйство
    's20_6': 108.1,  # ВРП
}


def _build_city_rows(entity_key, region_key, identity, sectors, population, births, deaths, age_2025):
    """Build per-year rows for a city. INSERT ON CONFLICT DO NOTHING — keep
    admin edits intact on subsequent deploys.
    """
    rows = []
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    for i, year in enumerate(years):
        row = {
            'entity_key': entity_key,
            'region_key': region_key,
            'year': year,
            **identity,
            's1_6': population[i] if i < len(population) else None,
        }
        if i < 5:  # 2021..2025 inclusive (sectors + vital counts)
            for key, series in sectors.items():
                row[key] = series[i]
            row['s11_7'] = births[i]
            row['s11_8'] = deaths[i]
            row['s9_5'] = births[i]   # mirrored in §9
            row['s9_6'] = deaths[i]
        if year == 2025:
            row.update(age_2025)
        rows.append(row)
    return rows


async def sync_gm_columns():
    """For each gm_* table, ALTER ADD any model column that's missing in the
    live Postgres schema.

    Required because create_all() only creates whole tables — it never adds
    columns to existing ones. When the bilingual _uz columns (35 of them)
    were introduced to the model after the first Railway deploy, the live
    tables stayed on the old schema, causing every SELECT * to fail with
    'column ... does not exist'. This migration brings the live schema up
    to whatever the model declares. Idempotent (ADD COLUMN IF NOT EXISTS).
    """
    added = 0
    async with engine_async.begin() as conn:
        for model in (gm.GmCountry, gm.GmRegion, gm.GmCity, gm.GmEntity):
            table_name = model.__tablename__
            result = await conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = :tn"
                ),
                {"tn": table_name},
            )
            existing = {row[0] for row in result}
            for col in model.__table__.columns:
                if col.name in existing:
                    continue
                col_type = col.type.compile(dialect=conn.dialect)
                ddl = (
                    f'ALTER TABLE {table_name} '
                    f'ADD COLUMN IF NOT EXISTS "{col.name}" {col_type}'
                )
                await conn.execute(text(ddl))
                added += 1
                log.info(
                    "[sync_gm_columns] +%s.%s (%s)", table_name, col.name, col_type
                )
    if added:
        log.info("[startup] sync_gm_columns: %d columns added to live schema", added)
    else:
        log.info("[startup] sync_gm_columns: live schema matches model")


async def migrate_enum_values():
    """Convert legacy Russian/Uzbek text in enum-typed columns to language-
    agnostic codes. Idempotent: rows already on codes are no-op.

    Touches s1_2 (тип объекта), s1_3 (админ. центр), and s21_*Priority on
    gm_city and gm_region. Country has neither column type; skip.
    """
    from sqlalchemy import update, or_

    # (column, RU/UZ value → code)
    REPLACEMENTS = {
        # Тип объекта
        gm.GmCity.s1_2: {
            'Город': 'city', 'Shahar': 'city', 'shahar': 'city',
            'Туман': 'tuman', 'Tuman': 'tuman', 'tuman': 'tuman',
        },
        # Админ. центр области (yes/no)
        gm.GmCity.s1_3: {
            'Да': 'yes', 'Ha': 'yes', 'ha': 'yes',
            'Нет': 'no', 'Yoʻq': 'no', 'No': 'no',
        },
    }
    # Priority columns on city: s21_2, s21_5, s21_8, s21_11, s21_14
    PRIORITY_COLS = ['s21_2', 's21_5', 's21_8', 's21_11', 's21_14']
    PRIORITY_MAP = {
        'Высокий': 'high', 'Yuqori': 'high', 'выс': 'high', 'high': 'high',
        'Средний': 'medium', 'Oʻrta': 'medium', 'oʻrta': 'medium', 'ср': 'medium',
        'Низкий': 'low', 'Past': 'low', 'past': 'low', 'низ': 'low',
    }

    total_updated = 0
    async with async_session() as session:
        for col, mapping in REPLACEMENTS.items():
            for ru_or_uz, code in mapping.items():
                stmt = update(gm.GmCity).where(col == ru_or_uz).values({col.key: code})
                result = await session.execute(stmt)
                total_updated += result.rowcount

        for col_name in PRIORITY_COLS:
            col = getattr(gm.GmCity, col_name)
            for ru_or_uz, code in PRIORITY_MAP.items():
                stmt = update(gm.GmCity).where(col == ru_or_uz).values({col_name: code})
                result = await session.execute(stmt)
                total_updated += result.rowcount

        await session.commit()

    if total_updated > 0:
        log.info("[startup] enum migration: %d cells converted to codes", total_updated)
    else:
        log.info("[startup] enum migration: nothing to convert (already on codes)")


async def seed_gm_data():
    """Insert verified data for Qoqon, Fergana, Margilan + Fergana region.
    Uses ON CONFLICT DO NOTHING so admin edits don't get clobbered on
    redeploy. To force-overwrite, delete the rows manually first.
    """
    qoqon_rows    = _build_city_rows('qoqon_city',    'fergana_region', QOQON_IDENTITY,    QOQON_YEARLY_SECTORS,    QOQON_POPULATION,    QOQON_BIRTHS,    QOQON_DEATHS,    QOQON_AGE_2025)
    fergana_rows  = _build_city_rows('fargona_city',  'fergana_region', FERGANA_IDENTITY,  FERGANA_YEARLY_SECTORS,  FERGANA_POPULATION,  FERGANA_BIRTHS,  FERGANA_DEATHS,  FERGANA_AGE_2025)
    margilan_rows = _build_city_rows('margilon_city', 'fergana_region', MARGILAN_IDENTITY, MARGILAN_YEARLY_SECTORS, MARGILAN_POPULATION, MARGILAN_BIRTHS, MARGILAN_DEATHS, MARGILAN_AGE_2025)

    region_row = {'entity_key': 'fergana_region', 'year': 2025, **FERGANA_REGION_2025}

    inserted_city = 0
    inserted_region = 0

    async with async_session() as session:
        for row in qoqon_rows + fergana_rows + margilan_rows:
            stmt = pg_insert(gm.GmCity).values(**row).on_conflict_do_nothing(
                index_elements=['entity_key', 'year'],
            )
            result = await session.execute(stmt)
            if result.rowcount > 0:
                inserted_city += 1

        stmt = pg_insert(gm.GmRegion).values(**region_row).on_conflict_do_nothing(
            index_elements=['entity_key', 'year'],
        )
        result = await session.execute(stmt)
        if result.rowcount > 0:
            inserted_region += 1

        await session.commit()

    log.info(
        "[startup] gm data seeded: %d city rows + %d region rows new (existing rows preserved)",
        inserted_city, inserted_region,
    )
