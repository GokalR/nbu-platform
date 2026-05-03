# NBU Platform — project guide

This file is the single source of truth for understanding what this repo
is, where things live, and how the pieces connect. Read it first when
opening a new Claude session — it exists so you don't have to re-discover
the layout by grepping.

---

## What this is

NBU regional analytics platform for the National Bank of Uzbekistan.
Three things bundled into one Vue + FastAPI app:

1. **Education** — courses, videos, quizzes, flashcards (`/education`)
2. **Analytics** — Fergana / Samarkand viloyat dashboards (`/districts`)
3. **Golden Mart** — unified template for city/region/country data
   that admins fill via a web form, and the public dashboards read live
   from Postgres. Schema-driven, bilingual.

Plus the Regional Strategist tool (`/tools/regional-strategist`) and
FinControl (`/tools/fincontrol`) — both pre-existing.

## Production URLs

| | URL | What |
|---|---|---|
| Frontend | `https://nbu-platform.pages.dev` | Vue 3 build, deployed by Cloudflare Pages on every push to `main` |
| Backend | `https://nbu-platform-production.up.railway.app` | FastAPI, deployed by Railway on every push to `main` |
| Backend health | `/api/health` and `/api/health/admin` | Sanity checks |
| Backend Swagger | `/docs` | Auto-generated API docs — ALWAYS check this if endpoints seem missing |
| GitHub | `https://github.com/GokalR/nbu-platform` | `main` is the production branch |

## ⚠ Critical layout fact

**Railway deploys from `./backend/`, NOT from `./frontend/backend/`.**

The `Dockerfile`, `Procfile`, and `railway.json` all live in `./backend/`,
and Procfile says `web: uvicorn app.main:app`. Anything you change in
`./backend/app/` ships to Railway. The folder `./frontend/backend/` was
deleted — it was an older copy that confused things for hours of dev
time. **Do not recreate it.**

Cloudflare Pages deploys from `./frontend/` (Vite build output).
Cloudflare doesn't touch the backend.

---

## Repository map

```
NBU-clean/
├── PROJECT.md                          ← you are here
├── README.md
│
├── backend/                            ← Railway target (Dockerfile, Procfile here)
│   ├── Dockerfile
│   ├── Procfile                        web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
│   ├── railway.json                    health check at /health
│   ├── nixpacks.toml
│   ├── requirements.txt
│   ├── seed.py / seed_analytics.py / seed_rs.py
│   └── app/
│       ├── main.py                     FastAPI entry — lifespan, CORS, routes, /health/admin
│       ├── config.py                   settings via env
│       ├── auth.py                     JWT + bcrypt helpers
│       ├── db_async.py                 async engine + BaseAsync + async_session + get_db
│       ├── db_sync.py                  sync engine + BaseSync (analytics)
│       ├── models_education.py         User, Course, Video, Enrollment, Progress
│       ├── models_analytics.py         analytics models
│       ├── models_analytics_ref.py     analytics reference models
│       ├── models_rs_ref.py            regional strategist reference models
│       ├── models_gm.py                ★ Golden Mart tables (AUTO-GENERATED, do not hand-edit)
│       └── routes/
│           ├── auth_routes.py          /api/auth/*
│           ├── courses.py / videos.py / enrollment.py / progress.py / dashboard.py
│           ├── analyze.py / excel.py / submissions.py
│           ├── analytics_ref.py / rs_ref.py
│           └── gm.py                   ★ Golden Mart endpoints /api/gm/*
│
├── frontend/                           ← Cloudflare Pages target
│   ├── package.json
│   ├── vite.config.js
│   ├── public/_redirects               SPA fallback /:path([^.]*) → /index.html
│   ├── .env.production                 VITE_BACKEND_URL=https://nbu-platform-production.up.railway.app
│   └── src/
│       ├── App.vue / main.js / router/index.js
│       ├── locales/
│       │   ├── ru.json                 ★ ALWAYS keep parity with uz.json
│       │   └── uz.json
│       ├── data/
│       │   ├── districts.js            Fergana 19 entities
│       │   ├── samarqand.js            Samarkand entries
│       │   ├── districtAnalytics.js    REAL_DATA per district + buildDistrictAnalytics()
│       │   └── goldenMart/
│       │       ├── citySchema.js       ★ AUTO-GENERATED 21-section city schema
│       │       ├── regionSchema.js     ★ AUTO-GENERATED 20-section region schema
│       │       ├── countrySchema.js    ★ AUTO-GENERATED 17-section country schema
│       │       ├── schemaPicker.js     schemaForLevel('city'|'region'|'country')
│       │       ├── loader.js           loadEntity(level, key) — API + static fallback
│       │       └── qoqon.js            Qoqon static fallback values
│       ├── services/
│       │   ├── eduApi.js               wraps /api/* — auto-prepends VITE_BACKEND_URL in prod
│       │   └── rsApi.js
│       └── views/
│           ├── DistrictAnalyticsView.vue       main map + drill-down
│           ├── QoqonDashboard.vue              ★ Qoqon redesigned overview (Style A + B toggle)
│           ├── QoqonGoldenMartDetail.vue       ★ all 21 sections, 6 thematic tabs
│           └── admin/
│               └── GmAdminView.vue             ★ /admin/golden-mart — fill values per (entity, year, field)
│
├── goldenmarts/                        ← Golden Mart pipeline
│   ├── golden_mart_country.xlsx        ★ source of truth (admins edit these)
│   ├── golden_mart_region.xlsx
│   ├── golden_mart_city.xlsx
│   ├── GM_country.md / GM_region.md / GM_city.md   AUTO-GENERATED human spec
│   ├── _to_md.py                       xlsx → MD
│   ├── _md_to_schema_js.py             MD → frontend JS schemas
│   ├── _md_to_sqlalchemy.py            MD → backend SQLAlchemy models
│   ├── _translations_uz.json           RU → UZ translation dict for schema labels
│   ├── _extend_schema.py               one-shot Excel extender (already run)
│   ├── PIPELINE.md                     pipeline docs
│   └── qoqon_data.json                 (placeholder if needed later)
│
├── fergana/                            verified PDF data (farstat.uz, Jan-Dec 2025)
│   ├── промышленность/  услуги/  внутреняя торговля/
│   ├── инвестиции/  строительство/  Сельское хозяйство/
│   ├── демографические_данные/  внешнеэкономическая_деятельность/
│   └── ВРП/                            real-growth indices (used for region anchor)
│
├── fergana_city/                       legacy design canvas (reference)
└── samarkand/                          (similar reference data folder)
```

---

## The Golden Mart pipeline

The single source of truth for the GM schema is the three Excel files in
`goldenmarts/`. Everything else is auto-generated:

```
                  golden_mart_*.xlsx
                  (admin edits these)
                          │
                  ┌───────┴───────┐
                  │ _to_md.py     │  python goldenmarts/_to_md.py
                  ▼               
              GM_*.md              
                  │
        ┌─────────┼──────────────────────────┐
        │                                    │
 _md_to_schema_js.py             _md_to_sqlalchemy.py
   ▼                                ▼
 frontend/src/data/goldenMart/  backend/app/models_gm.py
   citySchema.js                  (4 SQLAlchemy tables)
   regionSchema.js
   countrySchema.js
   (with bilingual labels via _translations_uz.json)
        │                                    │
        ▼                                    ▼
 schemaPicker.js                       Picked up by lifespan
        │                              create_all() on startup
        ▼                                    │
 GmAdminView.vue                             ▼
 QoqonGoldenMartDetail.vue            Postgres tables in Railway
 QoqonDashboard.vue                          │
        ▲                                    │
        │  loader.js  ◄──────  /api/gm/data/{level}/{key}
        └──────────────  fetched live from Railway DB
```

### To add a new field to a level

1. Edit the corresponding `golden_mart_*.xlsx` (insert row in the right section)
2. Run all three codegen scripts:
   ```bash
   PYTHONIOENCODING=utf-8 python goldenmarts/_to_md.py
   PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_schema_js.py
   PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_sqlalchemy.py
   ```
3. (Optional) Add the new label to `goldenmarts/_translations_uz.json`
4. Commit + push → Railway redeploys → `Base.metadata.create_all()` adds the new column to existing tables (Postgres `CREATE TABLE IF NOT EXISTS` is idempotent; `ALTER TABLE ADD COLUMN` is NOT auto-run, so for existing tables you'd need a migration; for an empty/test DB it just works)

---

## Database

**Postgres on Railway**, accessed via async SQLAlchemy from the backend.

`backend/app/db_async.py` exposes `BaseAsync` (declarative base), `engine_async`,
`async_session`, `get_db()` (FastAPI dep). All Golden Mart tables register with
this base.

Tables in DB (after lifespan runs):

| Table | Cols | Purpose |
|---|---|---|
| `users` | id, email, password_hash, full_name, **role**, ... | auth (admin role gates GM writes) |
| `courses`, `videos`, `learning_content`, `enrollments`, `progress` | — | Education |
| `gm_entities` | key, level, parent_key, name_ru, name_uz, iso_kind, active | lookup |
| `gm_country` | entity_key, year, ~188 GM fields, updated_by | country-level data |
| `gm_region`  | entity_key, year, ~169 GM fields, updated_by | region-level data |
| `gm_city`    | entity_key, region_key, year, ~208 GM fields, updated_by | city-level data |

Each GM data row = one (entity, year). Admin edits write to these.

Field columns are positional: `s{section_n}_{index}` (e.g. `s2_2` =
section 2 (Экономика – объёмы), field 2 (Промышленность – объём) on
the city table).

---

## Admin login

**Auto-seeded on every backend startup** by `ensure_seed_admin()` in
`backend/app/main.py` lifespan.

| Default | Override via Railway env var |
|---|---|
| email = `admin@nbu.uz` | `SEED_ADMIN_EMAIL` |
| password = `admin12345` | `SEED_ADMIN_PASSWORD` |
| name = `NBU Admin` | `SEED_ADMIN_NAME` |

On every backend restart, the user is **created if missing**, **promoted
to admin if role differs**, and the **password is reset to the env value
every time**. So Railway env vars are the single source of truth — change
them, the next request authenticates against the new password.

To check what's actually in DB: hit `/api/health/admin`. Returns
`{ user_found, user_email, user_role, ... }` without exposing hashes.

---

## API endpoints — Golden Mart

All under `/api/gm` (registered in `backend/app/routes/gm.py`):

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/gm/entities?level=city` | public | list entities |
| GET | `/api/gm/data/{level}/{key}` | public | all years for an entity |
| GET | `/api/gm/data/{level}/{key}/{year}` | public | single-year row |
| PUT | `/api/gm/data/{level}/{key}/{year}` | **admin role** | upsert values for that (entity, year) |
| GET | `/api/gm/coverage/{level}/{key}` | public | filled/total stats |

PUT body: `{ "values": { "s1_1": "Qoʻqon", "s2_2": 9410.4, ... } }`
Only fields whose key matches a column on the model are written.

Also: `/api/health/admin` returns the seed-admin status. `/docs` shows
all routes auto.

---

## Frontend ↔ Backend wiring

`frontend/src/services/eduApi.js` wraps fetches:

```js
const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '')
function resolve(url) {
  if (!url.startsWith('/api') && !url.startsWith('/health')) return url
  return BACKEND_URL ? BACKEND_URL + url : url
}
```

In dev: `VITE_BACKEND_URL` is empty → relative `/api/*` → Vite proxy to `localhost:8000`.
In prod: `VITE_BACKEND_URL=https://nbu-platform-production.up.railway.app` →
direct fetch to Railway.

CORS: backend `main.py` allows `http://localhost:5173`, `http://localhost:3000`,
`https://nbu-platform.pages.dev`, plus regex `https://.*\.nbu-platform\.pages\.dev`
for preview deploys.

`frontend/public/_redirects` only has `/:path([^.]*) /index.html 200`
(SPA fallback). The previous `/api/*` and `/health` redirects to Railway
were rejected by Cloudflare Pages and are removed — direct fetches replace them.

---

## i18n setup

Two locale files: `frontend/src/locales/ru.json` and `uz.json`.

**Keep them in parity** — every key in one must exist in the other.
Current count: ~1979 keys each. To verify:

```bash
python -c "
import json
ru = json.load(open('frontend/src/locales/ru.json', encoding='utf-8'))
uz = json.load(open('frontend/src/locales/uz.json', encoding='utf-8'))
def f(d, p=''):
    out=[]
    for k,v in d.items():
        x = f'{p}.{k}' if p else k
        if isinstance(v, dict): out += f(v, x)
        elif isinstance(v, list):
            for i, e in enumerate(v):
                if isinstance(e, dict): out += f(e, f'{x}[{i}]')
                else: out.append(f'{x}[{i}]')
        else: out.append(x)
    return out
print(f'ru: {len(set(f(ru)))}  uz: {len(set(f(uz)))}  diff: {len(set(f(ru))^set(f(uz)))}')
"
```

GM schema field labels are bilingual via `goldenmarts/_translations_uz.json`
(RU → UZ dict). Codegen embeds `labelUz` into each schema entry; views
pick `locale === 'uz' ? attr.labelUz : attr.label`.

---

## Common workflows

### Run locally (dev)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000  # runs lifespan, creates tables, seeds admin

# Frontend
cd frontend
npm install
npm run dev                                  # Vite at http://localhost:5173
```

### Add a city to the platform
1. Add row to `frontend/src/data/districts.js` (or `samarqand.js`)
2. Add an entity to `gm_entities` (via DB or expand seed/lifespan)
3. Allow it in `frontend/src/views/DistrictAnalyticsView.vue` → `AVAILABLE_DISTRICTS` set
4. Optional: build a redesigned dashboard like `QoqonDashboard.vue`

### Edit values via admin panel
1. Go to `/login`, sign in with `admin@nbu.uz` / `admin12345`
2. Navigate to `/admin/golden-mart`
3. Pick level → entity → year → tab → fill fields → click save
4. PUT to `/api/gm/data/{level}/{key}/{year}` writes to Railway Postgres
5. Public dashboard fetches updated values on next mount via `loader.js`

### Make a new commit reach production
1. `git push origin main`
2. Cloudflare Pages and Railway both auto-deploy on push
3. Wait ~1-2 min, refresh
4. To verify Railway picked it up: hit `/docs` and look for any new endpoints
5. To verify the build commit: Railway → Deployments tab → see git SHA

---

## Status snapshot (last updated 2026-05-03)

✅ Done
- 21-section Golden Mart schema (city), 20 (region), 17 (country)
- Auto-generation pipeline (xlsx → MD → JS schema → SQLAlchemy models)
- 4 DB tables (gm_entities + 3 wide value tables, ~600 columns total)
- API endpoints for read/write (with admin-role gate on writes)
- Admin panel UI with year tabs + 6 thematic tabs
- Schema-driven detail page with coverage indicators
- Redesigned Qoqon overview (Style A glassmorphism + Style B Fergana-brief)
- Bilingual: admin chrome + dashboard sections + 200+ field labels
- Auto-seed admin on every Railway startup, env vars as source of truth
- Public dashboards read from API with static qoqon.js fallback
- ~16% Qoqon GM coverage seeded from fergana/-PDFs

🔲 Pending
- More cities besides Qoqon get the redesigned dashboard
- More years backfilled per city/region (mostly empty for Margilan/Fergana)
- Per-cell metadata (verified flag, source attribution, audit history) — deliberately deferred
- Frontend role-guard for `/admin/golden-mart` (currently any logged-in user can open the page; backend rejects writes with 403)
- Per-section sparklines / inline charts within admin form
- "Подробные данные" detail view for Margilan / Fergana / other cities

🐛 Known gotchas
- ERR_CONNECTION_RESET on `*.pages.dev` from some Russian/CIS networks — works on mobile data, fix is custom domain
- `frontend/backend/` was deleted; if you see references to it in old commit messages or docs, that's stale
- Schema unit literals in JS comparisons (`'текст'`, `'%'`, `'‰'`) stay Russian — they match the GM template `unit` metadata, not user-facing copy

---

## Recent decisions (architectural)

- **One row per (entity, year)** in GM tables, not one row per cell. Trade-off: per-cell metadata (verified, source, history) requires a parallel skinny audit table. Deferred for now (option A from the design discussion).
- **Three separate value tables** (`gm_country`, `gm_region`, `gm_city`) instead of one big union — different fields per level mean a unified table would be ⅔ NULL.
- **Positional field keys** (`s1_1`, `s2_2`, ...) — stable across regenerations, decouple labels from storage.
- **Schema codegen lives in Python**, not Node — to share between JS frontend and Python backend.
- **Static JS fallback** in loader.js — public dashboards never fully break if API is down.
- **Auto-seed always resets admin password** from env on startup — convenience for sandbox/demo. For prod, change to create-only.

---

## When in doubt

1. Check `/docs` for what endpoints actually exist on Railway right now.
2. Check `/api/health/admin` for the actual admin user state in DB.
3. Check Railway → Deployments → Build Logs / Deploy Logs for `[startup]` messages.
4. Don't touch `frontend/backend/` — it's deleted.
5. Don't hand-edit `models_gm.py`, `citySchema.js`, `regionSchema.js`, `countrySchema.js`, or `GM_*.md` — they're auto-generated. Edit the Excel and re-run the codegen scripts.
