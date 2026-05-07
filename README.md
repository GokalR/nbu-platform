# NBU AI Hub

Monorepo for the NBU bank AI Hub — a multi-module platform combining regional analytics, SME tools, education, and AI-driven business advisory.

> **Quick start for a new session?** Read [RESUME.md](RESUME.md).
> **Deploying anything?** Read [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Repository layout

```
nbu_ai_hub/
├── README.md              ← you are here
├── RESUME.md              ← how to pick up work in a new window
├── DEPLOYMENT.md          ← GitHub / Railway / Cloudflare Pages / R2 runbook
├── .gitignore
│
├── bff_frontend/          ★ MAIN APP — FastAPI backend + Vue 3 frontend
│   ├── backend/           FastAPI: education, analytics, RS, GM, BP, SME, AI Advisor
│   └── frontend/          Vue 3 SPA (Cloudflare Pages)
│
├── region_analytics_platform_template/   CERR Mahalla Analytics (Flask + Next.js bundle)
│   ├── platform/          Flask server + mirrored Next.js static bundle
│   └── cerr_runs/         1.4 GB scraped JSON (gitignored — lives in R2)
│
├── sme_oprosnyk/          Standalone questionnaire app (FastAPI + React)
│                          Source for SME Profile module being migrated into bff_frontend
│
├── sdk_excel/             Claude SDK Excel-analysis prototype
├── words_excels/          Business plan Word/Excel templates
├── detailed_map_city/     Fergana education-market map prototype
├── nbu_education/         Static asset placeholder
│
├── upload_to_r2.py        One-shot uploader: cerr_runs/ → R2 bucket nbu-cerr-data
├── convert_cyrillic_to_latin.py  / fix_apostrophes.py / fix_step5_cyrillic.py
│                          One-off i18n fixers (kept for re-runs if needed)
└── products.xlsx          NBU credit products reference data
```

`bff_frontend/` is the production app. Everything else is either a satellite service (CERR platform), a migration source (sme_oprosnyk), or a reference/prototype.

---

## What's inside `bff_frontend/`

### Backend modules (FastAPI, single deployable)

| Module | Routes prefix | Purpose |
|---|---|---|
| Education | `/api/auth`, `/api/courses`, `/api/videos`, `/api/progress`, `/api/me` | Video courses, quizzes, flashcards, mind maps, JWT auth |
| Analytics (Regional Strategist) | `/api/rs/*` | 6-step business viability wizard with Claude analysis |
| Analytics reference | `/api/analytics-ref`, `/api/rs-ref` | District / city / peer benchmark lookups |
| Golden Mart | `/api/gm/*` | Qoqon Golden Mart scenario module |
| Business Plan | `/api/business-plan/*` | LLM-generated business plan + DOCX export |
| SME Profile | `/api/sme-profile/*` | Bilingual questionnaire (migrated from `sme_oprosnyk/`) |
| AI Advisor | `/api/regional-chat/*` | RAG chatbot over 14 viloyats via OpenAI File Search |
| CERR proxy | `/api/cerr/*` | Thin proxy for CERR Mahalla Analytics |

### Frontend modules (Vue 3 SPA)

`Home / Analytics`, `Districts (v1 + v2/Mahallalar)`, `AI Advisor`, `Business Tools`, `Education`, `FinControl`, `Regional Strategist`, `Golden Mart`, `Business Plan`, `SME Profile`, plus admin views.

i18n: Uzbek Latin (`uz.json`) + Russian (`ru.json`).

---

## Deployment targets

| Service | Where it runs | Domain |
|---|---|---|
| `bff_frontend/backend` | Railway (Docker) | `*.up.railway.app` |
| `bff_frontend/frontend` | Cloudflare Pages | `nbu-platform.pages.dev` (custom domain optional) |
| `region_analytics_platform_template/platform` | Railway (separate service) | iframed by main app at `/regions-v2` |
| CERR scraped data | Cloudflare R2 bucket `nbu-cerr-data` | `cerr-data.devgokal.com` |
| Education videos | Cloudflare R2 | `nbu-videos.devgokal.com` (planned) |
| PostgreSQL | Railway addon | `postgres.railway.internal` |

GitHub repo: **`GokalR/nbu-platform`** (single remote, branch `main`).

See [DEPLOYMENT.md](DEPLOYMENT.md) for how to push, deploy, and rotate env vars.

---

## Conventions

- **Python**: 3.12, uvicorn, FastAPI. Backend env var loading via `pydantic-settings`. Always `.strip()` env vars (Railway sometimes appends `\n`).
- **Node**: Vue 3 + Vite 5, Tailwind 3, Pinia, vue-i18n. No TypeScript in `bff_frontend/frontend` (it's `.vue` + `.js`).
- **Database**: a single Postgres serves both async (education) and sync (analytics) engines. `models_*.py` modules register all tables; `create_all()` runs on startup but only adds NEW tables — schema changes require `ALTER TABLE`.
- **AI models**: Claude `claude-sonnet-4-6-20250627` (full ID required), OpenAI `gpt-4o` for Business Plan, `gpt-5.1` for AI Advisor (RAG via Vector Store).
- **Auth**: JWT in `localStorage` as `edu_token`. `auth_sync.py` decodes without DB roundtrip for the sync (analytics) routes.
- **bcrypt pinned** to `4.0.1` — passlib breaks on >=4.1.

---

## Per-subproject docs

- [bff_frontend/README.md](bff_frontend/README.md) — main app, run + deploy
- [region_analytics_platform_template/README.md](region_analytics_platform_template/README.md) — CERR platform
- [sme_oprosnyk/README.md](sme_oprosnyk/README.md) — questionnaire (migration source)
