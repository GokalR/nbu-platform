# Resume Session

The "I just opened a new window — where was I?" cheat sheet. Read this first when picking up work.

---

## 1. Where am I?

```
c:\Users\User\Downloads\myfolder\NBU\Projects\nbu_ai_hub
```

GitHub: `GokalR/nbu-platform`. Branch: `main`.

```bash
git status                # what's changed since last commit
git log --oneline -10     # what landed recently
```

---

## 2. The 30-second mental model

- **One repo, multiple subprojects.** The main app lives in [bff_frontend/](bff_frontend/). Everything else is a satellite (CERR platform), migration source (sme_oprosnyk), or prototype.
- **Two backends deployed to Railway**: the main FastAPI app, and the Flask-based CERR mock platform.
- **One frontend on Cloudflare Pages**: Vue 3 SPA in `bff_frontend/frontend/`.
- **Two R2 buckets**: `nbu-cerr-data` (mahalla JSON), `nbu-edu-videos` (course videos).
- **One Postgres** on Railway, shared between async (education) and sync (analytics) engines.

Full picture in [README.md](README.md). Deployment specifics in [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 3. Run the main app locally

Two terminals:

### Terminal 1 — backend

```bash
cd bff_frontend/backend
python -m venv .venv
.venv\Scripts\activate              # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy or create .env (see template below)
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — frontend

```bash
cd bff_frontend/frontend
npm install
npm run dev                          # http://localhost:5173
```

### `bff_frontend/backend/.env` template

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nbu     # or Railway public proxy URL
APP_ENV=dev
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=dev-secret-change-me
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6-20250627
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
RAG_MODEL=gpt-5.1
VECTOR_STORE_ID=vs_...
LLM_PROVIDER=claude
VIDEO_BASE_URL=
CERR_DATA_ROOT=
```

### `bff_frontend/frontend/.env.local` template

```env
VITE_API_URL=http://localhost:8000
VITE_CERR_BUNDLE_URL=http://localhost:5000
VITE_YANDEX_MAPS_API_KEY=<yandex-key>
```

---

## 4. Run the CERR platform locally (optional)

Only needed when working on the `/regions-v2` (Mahallalar) view.

```bash
cd region_analytics_platform_template/platform
pip install -r requirements.txt

# Two options for data:
#   (a) Point at R2 (no local data needed):
export CERR_DATA_ROOT="https://cerr-data.devgokal.com"
#   (b) Use local data if you have it:
export CERR_DATA_ROOT="$PWD/../cerr_runs"

python server.py                     # http://localhost:5000
```

Then in the frontend, set `VITE_CERR_BUNDLE_URL=http://localhost:5000`.

---

## 5. Common tasks

### Push a code change

```bash
git status                                # check
git add <specific-files>
git commit -m "<imperative summary>"
git push origin main                      # triggers Railway + Pages auto-deploy
```

### Apply a SQL schema change

`create_all()` does NOT modify existing columns. ALTER manually:

```bash
psql "postgresql://postgres:<pwd>@<railway-proxy>:<port>/railway"
# then: ALTER TABLE ... / CREATE INDEX ...
```

Save the SQL next to the code change for reproducibility.

### Re-upload CERR data to R2

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
python upload_to_r2.py                    # idempotent, skips files already present
```

### Rotate an env var

- **Backend (Railway)**: dashboard → service → Variables → edit → service auto-redeploys.
- **Frontend (Pages)**: dashboard → Settings → Environment variables → edit → manually redeploy (Vite vars are baked in at build time).

---

## 6. Where each module lives

| You're working on… | Backend file(s) | Frontend file(s) |
|---|---|---|
| Education (courses, videos, quizzes) | `routes/auth_routes.py`, `courses.py`, `videos.py`, `progress.py`, `models_education.py` | `views/education/`, `services/eduApi.js`, `stores/eduAuth.js` |
| Regional Strategist (6-step wizard) | `routes/submissions.py`, `excel.py`, `analyze.py`, `services/claude_client.py`, `excel_parser.py`, `ratios.py`, `benchmarks.py` | `views/regionalStrategist/`, `services/rsApi.js`, `stores/regionalStrategist.js` |
| Districts / Analytics | `routes/analytics_ref.py`, `rs_ref.py` | `views/DistrictAnalyticsView.vue`, `HomeView.vue`, `components/FerganaMap.vue`, `UzbekistanMap.vue` |
| Mahallalar (CERR v2) | `routes/cerr.py` (proxy) | `views/regionsV2/` (iframes the CERR platform) |
| Golden Mart | `routes/gm.py`, `models_gm.py`, `seed_gm_data.py` | `views/QoqonGoldenMartDetail.vue`, `QoqonDashboard.vue` |
| Business Plan | `routes/business_plan.py`, `services/business_plan_*.py`, `services/docx_builder.py` | `views/businessPlan/` |
| SME Profile | `routes/sme_profile.py`, `services/sme_profile_data.py`, `models_sme_profile.py` | `views/smeProfile/` |
| AI Advisor (RAG) | `routes/regional_chat.py`, `services/regional_chat/` | `views/AiAdvisorView.vue` |

---

## 7. Recent commits — what's the latest context?

```bash
git log --oneline -20
```

Latest known work (May 2026): CERR bundle CSS polish, i18n rename "Анализ районов v2" → "Анализ махаллей", AI Advisor header tweaks.

---

## 8. Stuck? Read in this order

1. [README.md](README.md) — what each subproject is for.
2. [bff_frontend/README.md](bff_frontend/README.md) — main app architecture.
3. [DEPLOYMENT.md](DEPLOYMENT.md) — how things get to production.
4. The "Things that have bitten us" section in DEPLOYMENT.md — gotchas.
