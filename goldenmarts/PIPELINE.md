# Golden Mart pipeline

The Golden Mart schema flows from one source of truth — the three Excel
files in this folder — through several auto-generated artifacts that the
frontend and backend consume.

```
goldenmarts/
  golden_mart_country.xlsx  ─┐
  golden_mart_region.xlsx   ─┼── source of truth (admins edit these)
  golden_mart_city.xlsx     ─┘
        │
        │  python goldenmarts/_to_md.py
        ▼
  GM_country.md   GM_region.md   GM_city.md
        │
        ├── python goldenmarts/_md_to_schema_js.py
        │       ▼
        │   frontend/src/data/goldenMart/citySchema.js   (frontend)
        │
        └── python goldenmarts/_md_to_sqlalchemy.py
                ▼
            backend/app/models_gm.py                 (backend)
```

## Tables

Defined in `backend/app/models_gm.py` (auto-generated):

| Table         | Rows                  | Columns                |
|---------------|-----------------------|------------------------|
| `gm_entities` | ~20 entities          | `key`, `level`, `parent_key`, `name_ru`, `name_uz`, ...|
| `gm_country`  | 6 (1 entity × 6 years)| 188 GM fields + meta   |
| `gm_region`   | 12 (2 × 6 years)      | 169 GM fields + meta   |
| `gm_city`     | 24 (4 × 6 years)      | 208 GM fields + meta   |

Each data table has `(entity_key, year)` as composite primary key. Field
columns are positional: `s{section}_{index}` (e.g. `s2_2` is section 2,
field 2 = Промышленность – объём for the city table).

## Workflow when an admin edits the Excel

```bash
PYTHONIOENCODING=utf-8 python goldenmarts/_to_md.py             # xlsx → md
PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_schema_js.py   # md → frontend JS
PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_sqlalchemy.py  # md → backend SQLAlchemy
cd backend && python -m app.seed_gm                             # (or rely on lifespan auto-seed)
```

Backend `Base.metadata.create_all` (in `main.py` lifespan) handles new
tables / new columns automatically on next FastAPI startup.

## Phase A status (commit dafe835 → ?)

✅ Tables defined (gm_entities + 3 wide value tables)
✅ Seed script populates Qoqon 2021–2025 + Fergana viloyat 2025
✅ Schema regen pipeline documented and idempotent
🔲 API endpoints (Phase B): `GET /api/gm/{level}/{entity_key}/{year}`
🔲 Frontend swap (Phase C): read from API instead of qoqon.js
🔲 Admin UI (Phase D): /admin/golden-mart with edit forms

## Verification

After `seed_gm.py` runs, `SELECT s2_2 FROM gm_city WHERE entity_key='qoqon_city' AND year=2025`
should return `9410.4` (Qoqon industry total 2025, mlrd soʻm).
