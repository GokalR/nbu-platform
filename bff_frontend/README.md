# bff_frontend — NBU AI Hub main app

The production application: a unified FastAPI backend and a Vue 3 SPA frontend.

> Top-level docs: [../README.md](../README.md), [../RESUME.md](../RESUME.md), [../DEPLOYMENT.md](../DEPLOYMENT.md).

---

## Layout

```
bff_frontend/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app, CORS, lifespan, route mounting
│   │   ├── config.py                   # pydantic-settings: env loading, URL converters
│   │   ├── db_async.py                 # async engine (asyncpg)  — education
│   │   ├── db_sync.py                  # sync engine (psycopg)   — analytics
│   │   ├── auth.py                     # JWT issuance + async-friendly current-user
│   │   ├── auth_sync.py                # JWT decode without DB roundtrip (sync routes)
│   │   ├── helpers.py
│   │   ├── schemas.py                  # Pydantic request/response shapes
│   │   ├── models_education.py         # Users, Courses, Videos, LearningContent, Enrollment, Progress
│   │   ├── models_analytics.py         # Submission, ExcelUpload, AnalysisResult
│   │   ├── models_analytics_ref.py     # district / city reference data
│   │   ├── models_rs_ref.py            # RS reference data
│   │   ├── models_gm.py                # Golden Mart
│   │   ├── models_business_plan.py     # business_plan_submissions
│   │   ├── models_sme_profile.py       # sme_profile_submissions
│   │   ├── seed_gm_data.py             # one-shot seed for Golden Mart
│   │   ├── routes/                     # one router per module — see table below
│   │   └── services/                   # business logic (Claude/OpenAI clients, Excel, ratios, RAG)
│   ├── data/                           # peer_benchmarks.json, rs_seed/, sme_profile/
│   ├── scripts/                        # build_cerr_manifest.py + helpers
│   ├── tests/                          # pytest
│   ├── seed.py                         # main seeder (education + analytics)
│   ├── seed_analytics.py
│   ├── seed_rs.py
│   ├── seed_rs_reference.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Procfile                        # web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
│   ├── railway.json                    # Railway: DOCKERFILE builder, /health check
│   ├── nixpacks.toml
│   ├── pytest.ini
│   ├── MIGRATIONS.md                   # SQL deltas applied since create_all()
│   └── .env                            # gitignored
│
└── frontend/
    ├── src/
    │   ├── main.js                     # Vue + Pinia + Router + i18n bootstrap
    │   ├── App.vue
    │   ├── router/                     # all routes, lazy-loaded views, layout guards
    │   ├── layouts/                    # DefaultLayout, EducationLayout, FinControlLayout, RegionalStrategistLayout, …
    │   ├── views/                      # one folder per module
    │   ├── components/                 # shared + module-specific
    │   ├── stores/                     # Pinia (eduAuth, regionalStrategist, …)
    │   ├── services/                   # API clients (api.js, eduApi.js, rsApi.js, …)
    │   ├── composables/
    │   ├── data/                       # static data files (districts, regions, products, …)
    │   ├── locales/                    # uz.json, ru.json
    │   ├── i18n/                       # vue-i18n config + per-step merges
    │   ├── assets/
    │   └── utils/
    ├── public/                         # GeoJSON, embedded Yandex map, sample Excels, logos
    ├── dist/                           # build output (gitignored)
    ├── newdesign/, nbu_design/         # source designs converted from React → Vue
    ├── package.json
    ├── vite.config.js                  # custom plugin injects VITE_YANDEX_MAPS_API_KEY
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    ├── .env.example                    # full template — copy to .env.local
    ├── .env.local                      # gitignored
    └── .env.production                 # baked into Pages build
```

---

## Backend modules

All routers are mounted in `app/main.py`. JWT-protected routes use `auth.py` (async) or `auth_sync.py` (sync); a few RS endpoints accept optional auth.

| Router file | Prefix | What it owns |
|---|---|---|
| `auth_routes.py` | `/api/auth` | Register, login, refresh |
| `courses.py` | `/api/courses` | List + detail (with `?lang=uz\|ru`) |
| `videos.py` | `/api/videos` | Video detail + LearningContent (quiz/flashcard/mindmap/test) |
| `enrollment.py` | `/api/courses/{id}/enroll` | Course enrollment |
| `progress.py` | `/api/progress` | Track completion + scores |
| `dashboard.py` | `/api/me` | User dashboard summary |
| `submissions.py` | `/api/rs/submissions` | Create / fetch RS submissions, `GET /submissions/my` for user history |
| `excel.py` | `/api/rs/submissions/{id}/uploads` | Upload + parse balance/PnL Excel |
| `analyze.py` | `/api/rs/submissions/{id}/analysis` | Trigger Claude analysis |
| `analytics_ref.py` | `/api/analytics-ref` | District / city / sector reference lookups |
| `rs_ref.py` | `/api/rs-ref` | RS reference (peer benchmarks, products, cities) |
| `gm.py` | `/api/gm` | Golden Mart Qoqon scenario |
| `business_plan.py` | `/api/business-plan` | LLM-generated plan + DOCX export, admin sub-router |
| `sme_profile.py` | `/api/sme-profile` | Bilingual questionnaire, admin sub-router |
| `regional_chat.py` | `/api/regional-chat` | AI Advisor (RAG via OpenAI File Search over 14 viloyats) |
| `cerr.py` | `/api/cerr` | Thin proxy → CERR Mahalla Analytics |

### Services

| File | Purpose |
|---|---|
| `claude_client.py` | Anthropic API client for RS analysis |
| `business_plan_client.py` | LLM dispatcher (claude / openai) for business plans |
| `business_plan_compute.py` | Numerical computations underpinning the plan |
| `excel_parser.py`, `excel_parser_msb.py` | Balance + PnL Excel → structured JSON |
| `ratios.py` | Liquidity, profitability, leverage, efficiency ratios |
| `benchmarks.py` | Compare ratios against `data/peer_benchmarks.json` |
| `credit_scoring.py` | Score breakdown for RS step 5 |
| `cities.py`, `nbu_products.py` | Reference lookups |
| `cerr_data.py` | CERR data accessor |
| `docx_builder.py` | Word document export for Business Plan |
| `regional_chat/` (subpackage) | RAG orchestrator: ingest, prompts, router, registry, single-region MD store |
| `sme_profile_data.py` | SME profile data loaders (incl. Tuman+MFY lookup) |

### Database

One Postgres, two engines:

- **Async (asyncpg)** — education tables (`models_education.py`)
- **Sync (psycopg)** — analytics tables (`models_analytics.py` and the rest)

`create_all()` runs on app startup but **only creates new tables**. Schema changes require explicit `ALTER TABLE` (track them in `MIGRATIONS.md`).

---

## Frontend modules

Routes are lazy-loaded; layouts wrap each section.

| Module | Views | Layout |
|---|---|---|
| Home / Districts / AI Advisor / Business Tools | `HomeView`, `DistrictAnalyticsView`, `AiAdvisorView`, `BusinessToolsView` | `DefaultLayout` |
| Mahallalar (Districts v2) | `views/regionsV2/*` (iframes CERR platform) | `DefaultLayout` |
| Education | `views/education/*` (Courses, Detail, Learning, Dashboard, Login) | `EducationLayout` |
| FinControl | `views/fincontrol/*` (10 views: Dashboard, Accounts, Cashflow, PnL, Planning, AI, …) | `FinControlLayout` |
| Regional Strategist | `views/regionalStrategist/*` (Step0–Step5 wizard) | `RegionalStrategistLayout` |
| Golden Mart | `QoqonDashboard.vue`, `QoqonGoldenMartDetail.vue` | `DefaultLayout` |
| Business Plan | `views/businessPlan/*` | (own) |
| SME Profile | `views/smeProfile/*` | (own) |
| Admin | `views/admin/*` | (own) |

i18n: `src/locales/uz.json` (Uzbek Latin, ~75 KB), `src/locales/ru.json` (Russian, ~97 KB). RS step views additionally merge per-step i18n files at component level.

---

## Local development

```bash
# Backend
cd bff_frontend/backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
# create .env (see ../RESUME.md for template)
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd bff_frontend/frontend
npm install
cp .env.example .env.local        # set VITE_API_URL=http://localhost:8000
npm run dev                       # http://localhost:5173
```

For the Mahallalar (`/regions-v2`) view also run the CERR platform — see [../region_analytics_platform_template/README.md](../region_analytics_platform_template/README.md).

### Tests

```bash
cd bff_frontend/backend && pytest
cd bff_frontend/frontend && npm run test
```

---

## Seeding

```bash
cd bff_frontend/backend
python seed.py                    # education courses, videos, learning content
python seed_analytics.py          # analytics reference + peer benchmarks
python seed_rs.py                 # Regional Strategist demo data
python seed_rs_reference.py       # RS reference (cities, products, …)
# Golden Mart: imported automatically via seed_gm_data.py on startup
```

---

## Deployment

See [../DEPLOYMENT.md](../DEPLOYMENT.md). TL;DR:

- `git push origin main` → Railway redeploys backend + Cloudflare Pages rebuilds frontend.
- Backend root dir on Railway: `bff_frontend/backend/`. Frontend root dir on Pages: `bff_frontend/frontend/`.
- Railway uses the Dockerfile (Python 3.12 + uvicorn). Pages uses Node 20 + `npm run build`.

---

## Module-by-module gotchas

- **Regional Strategist**: `auth_sync.get_current_user_id()` is **optional auth** — it adds `submissions.user_id` for logged-in users without forcing login. The `submissions.user_id` column was added later via ALTER (see `MIGRATIONS.md`).
- **Business Plan**: `LLM_PROVIDER` env toggle picks Claude vs OpenAI. RS always uses Claude regardless.
- **AI Advisor**: needs a populated OpenAI Vector Store (`VECTOR_STORE_ID` env). Single-region MD files live in `services/regional_chat/rag_single/`.
- **CERR data**: not in this repo. The platform service reads from R2 (`CERR_DATA_ROOT=https://cerr-data.devgokal.com`) or a local `cerr_runs/` if you've downloaded it.
- **Yandex Maps key**: injected at Vite build time via the `rs-yandex-key` plugin in `vite.config.js`. Rotating the key requires a Pages rebuild.
