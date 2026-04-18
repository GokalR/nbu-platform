# NBU Platform — Technical Documentation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 3 SPA Frontend                   │
│   Cloudflare Pages · nbu-testing.devgokal.com           │
│                                                         │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────────┐  │
│  │ Education   │ │ FinControl │ │ Regional Strategist │  │
│  │ Module      │ │ Module     │ │ Module              │  │
│  └────────────┘ └────────────┘ └─────────────────────┘  │
│                                                         │
│  _redirects proxy: /api/* → Railway                     │
└──────────────────────┬──────────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │   Unified FastAPI     │
           │   Railway Service     │
           │                       │
           │  Async engine (asyncpg)  ← Education routes
           │  Sync engine (psycopg)   ← Analytics routes
           └───────────┬───────────┘
                       │
                PostgreSQL (Railway)
           6 education + 3 analytics tables
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3.5, Vite 5, Tailwind CSS 3, Pinia, vue-i18n, Chart.js |
| Backend (Education) | FastAPI, SQLAlchemy (async), asyncpg, PostgreSQL |
| Backend (Analytics) | FastAPI, SQLAlchemy (sync), psycopg, Anthropic Claude API |
| Hosting | Cloudflare Pages (frontend), Railway (backend + PostgreSQL), Cloudflare R2 (videos) |
| Languages | Uzbek Latin (uz), Russian (ru) |

---

## 1. Frontend (`frontend/`)

### Modules

| Module | Views | Components | Description |
|--------|-------|------------|-------------|
| **Home / Analytics** | `HomeView`, `DistrictAnalyticsView`, `AiAdvisorView`, `BusinessToolsView` | `FerganaMap`, `UzbekistanMap`, `KpiCard`, `StatCard`, `MapPanel` | NBU regional analytics dashboard with interactive SVG maps |
| **Education** | `EduCoursesView`, `EduCourseDetailView`, `EduLearningView`, `EduDashboardView`, `EduLoginView` | `EduVideoPlayer`, `EduQuiz`, `EduFlashcards`, `EduMindMap`, `EduTest` | Video courses with quizzes, flashcards, mind maps, tests |
| **FinControl** | 10 views (Dashboard, Accounts, Cashflow, PnL, Planning, AI, etc.) | `FcChart`, `FcHeader`, `FcSidebar`, `FcSparkline` | Financial management tool |
| **Regional Strategist** | `RsHomeView`, `RsBusinessTestView`, 6 step views (Step0–Step5) | 22 components (`RsIcon`, `RsExcelUpload`, `RsClaudeAnalysis`, `RsFerganaHeatmap`, etc.) | 6-step business viability wizard with AI analysis |

### Key Files

| Path | Purpose |
|------|---------|
| `src/router/index.js` | All routes, lazy-loaded views, layout guards |
| `src/stores/regionalStrategist.js` | RS wizard state: steps, profile, finance, results |
| `src/stores/eduAuth.js` | JWT auth state for education platform |
| `src/services/rsApi.js` | RS backend calls (submissions, excel upload, analysis) |
| `src/services/eduApi.js` | Education backend calls (courses, videos, enrollment) |
| `src/locales/uz.json` (75 KB) | Uzbek Latin translations |
| `src/locales/ru.json` (97 KB) | Russian translations |

### Layouts

| Layout | Used By |
|--------|---------|
| `DefaultLayout.vue` | Home, Districts, AI Advisor, Business Tools |
| `EducationLayout.vue` | All `/education/*` routes |
| `FinControlLayout.vue` | All `/fincontrol/*` routes |
| `RegionalStrategistLayout.vue` | All `/tools/regional-strategist/*` routes |

### Components

**Global (14):**
`AppIcon`, `AppSidebar`, `AppTopBar`, `DistrictList`, `FerganaMap`, `KpiCard`, `LanguageSwitcher`, `MapPanel`, `PageHeader`, `ProgressBar`, `RegionDropdown`, `RegionInfoBar`, `StatCard`, `UzbekistanMap`

**Education (5):**
`EduFlashcards`, `EduMindMap`, `EduQuiz`, `EduTest`, `EduVideoPlayer`

**FinControl (4):**
`FcChart`, `FcHeader`, `FcSidebar`, `FcSparkline`

**Regional Strategist (22):**
`RsClaudeAnalysis`, `RsDataTable`, `RsExcelUpload`, `RsFerganaHeatmap`, `RsFieldHelper`, `RsFieldLabel`, `RsHeader`, `RsIcon`, `RsInputSummary`, `RsInsightBox`, `RsKpiCard`, `RsMargilanHeatmap`, `RsRecommendationCard`, `RsScoreBreakdown`, `RsScoreRing`, `RsScoringCriteria`, `RsSectionLabel`, `RsSelectField`, `RsStatusTag`, `RsStepProgress`, `RsTextField`, `rs-utils.js`

### Static Assets

| Asset | Location |
|-------|----------|
| Fergana districts GeoJSON | `public/fergana-districts.geojson` |
| Uzbekistan regions GeoJSON | `public/uzbekistan-regions.geojson` |
| Yandex Maps education map | `public/maps/fergana-education/index.html` + `map_data.generated.js` |
| Sample Excel files | `public/samples/ERKIN_PARVOZ_balance.xlsx`, `ERKIN_PARVOZ_pnl.xlsx` |
| Video thumbnails | `public/thumbnails/digital-culture-bank.png` |
| NBU logo | `public/nbu_logo.png`, `public/logos/nbu-mark.png` |

### Data Files

| File | Purpose |
|------|---------|
| `src/data/districts.js` | Fergana district metadata (population, area) |
| `src/data/districtAnalytics.js` | Per-district analytics data |
| `src/data/regions.js` | Uzbekistan region list |
| `src/data/regionAnalytics.js` | Per-region analytics |
| `src/data/regionColors.js` | Map color palette |
| `src/data/fincontrol.js` | FinControl demo data |
| `src/data/regionalStrategist/*.js` | Cities, credit products, demo seeds, Fergana context, enterprise data, scoring logic, peer benchmarks |

---

## 2. Backend — Education (`frontend/backend/`)

**Stack:** FastAPI + SQLAlchemy (async) + asyncpg + PostgreSQL

### Database Models (6 tables)

| Model | Key Fields |
|-------|------------|
| **User** | id, email, hashed_password, full_name, role |
| **Course** | id, title_uz, title_ru, description, thumbnail_url, order |
| **Video** | id, course_id, title_uz, title_ru, video_url, duration, order |
| **LearningContent** | id, video_id, content_type (quiz/flashcard/mindmap/test), content_json |
| **Enrollment** | id, user_id, course_id, enrolled_at |
| **Progress** | id, user_id, video_id, completed, score, last_position |

### API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/register` | POST | No | User registration |
| `/api/auth/login` | POST | No | JWT login |
| `/api/courses` | GET | No | List all courses (with `?lang=uz\|ru`) |
| `/api/courses/{id}` | GET | No | Course detail with videos |
| `/api/videos/{id}` | GET | No | Video detail with learning content |
| `/api/courses/{id}/enroll` | POST | JWT | Enroll in course |
| `/api/progress` | GET/POST | JWT | Track video completion & scores |
| `/api/me` | GET | JWT | User dashboard data |

### Files

```
frontend/backend/
├── main.py              # FastAPI app, CORS, lifespan
├── models.py            # SQLAlchemy async models (6 tables)
├── auth.py              # JWT token creation & verification
├── config.py            # Settings (DATABASE_URL, SECRET_KEY, VIDEO_BASE_URL)
├── seed.py              # Database seeder (courses, videos, learning content)
├── requirements.txt
├── .env
└── routes/
    ├── auth_routes.py   # /api/auth/*
    ├── courses.py       # /api/courses/*
    ├── videos.py        # /api/videos/*
    ├── enrollment.py    # /api/courses/{id}/enroll
    ├── progress.py      # /api/progress
    └── dashboard.py     # /api/me
```

---

## 3. Backend — Analytics (`backend/app/`)

**Stack:** FastAPI + SQLAlchemy (sync) + psycopg + Anthropic Claude API

### Database Models (3 tables)

| Model | Key Fields |
|-------|------------|
| **Submission** | id, business_name, business_direction, city, district, created_at |
| **ExcelUpload** | id, submission_id, file_type (balance/pnl), original_name, parsed_json |
| **AnalysisResult** | id, submission_id, analysis_json, model_used, created_at |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rs/submissions` | POST | Create new analysis submission |
| `/api/rs/submissions/{id}` | GET | Get submission with uploads & results |
| `/api/rs/submissions/{id}/uploads` | POST | Upload & parse Excel (balance/pnl) |
| `/api/rs/submissions/{id}/analysis` | POST | Run Claude AI analysis |

### Services

| Service | Purpose |
|---------|---------|
| `claude_client.py` | Sends financial data to Claude API, receives structured JSON analysis |
| `excel_parser.py` | Parses balance sheet & PnL Excel files into structured JSON |
| `ratios.py` | Calculates financial ratios (liquidity, profitability, leverage, efficiency) |
| `benchmarks.py` | Compares calculated ratios against peer data from `peer_benchmarks.json` |

### Files

```
backend/
├── app/
│   ├── main.py              # Unified FastAPI (mounts education + analytics routes)
│   ├── config.py            # Settings (DATABASE_URL, ANTHROPIC_API_KEY, etc.)
│   ├── db_async.py          # Async engine for education
│   ├── db_sync.py           # Sync engine for analytics
│   ├── auth.py              # JWT authentication
│   ├── models_education.py  # Education ORM models
│   ├── models_analytics.py  # Analytics ORM models
│   ├── schemas.py           # Pydantic schemas (Submission, Upload, Analysis)
│   ├── routes/
│   │   ├── auth_routes.py   # /api/auth/*
│   │   ├── courses.py       # /api/courses/*
│   │   ├── videos.py        # /api/videos/*
│   │   ├── enrollment.py    # /api/courses/{id}/enroll
│   │   ├── progress.py      # /api/progress
│   │   ├── dashboard.py     # /api/me
│   │   ├── submissions.py   # /api/rs/submissions
│   │   ├── excel.py         # /api/rs/submissions/{id}/uploads
│   │   └── analyze.py       # /api/rs/submissions/{id}/analysis
│   ├── services/
│   │   ├── claude_client.py
│   │   ├── excel_parser.py
│   │   ├── ratios.py
│   │   └── benchmarks.py
│   └── data/
│       └── peer_benchmarks.json
├── seed.py
├── requirements.txt
├── Dockerfile
├── Procfile
├── railway.json
└── nixpacks.toml
```

### Dependencies

```
fastapi >= 0.115.0
uvicorn >= 0.30.0
sqlalchemy[asyncio] >= 2.0.0
asyncpg >= 0.29.0
psycopg[binary] >= 3.1.0
python-jose[cryptography] >= 3.3.0
passlib[bcrypt] >= 1.7.0
anthropic >= 0.39.0
openpyxl >= 3.1.0
python-multipart >= 0.0.9
pydantic-settings >= 2.0.0
python-dotenv >= 1.0.0
```

---

## 4. Deployment

### Railway (Backend)

| Config | Value |
|--------|-------|
| Root directory | `backend/` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Database | Railway PostgreSQL addon (auto `DATABASE_URL`) |

**Environment Variables:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Auto-provided by Railway PostgreSQL addon |
| `APP_ENV` | `production` |
| `CORS_ORIGINS` | `https://nbu-testing.devgokal.com` |
| `ANTHROPIC_API_KEY` | Claude API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` |
| `SECRET_KEY` | JWT signing key |
| `VIDEO_BASE_URL` | `https://videos.nbu-testing.devgokal.com` |

### Cloudflare Pages (Frontend)

| Config | Value |
|--------|-------|
| Root directory | `frontend/` |
| Build command | `npm run build` |
| Output | `dist/` |
| Domain | `nbu-testing.devgokal.com` |

**`_redirects` file proxies API calls:**
```
/api/*   https://RAILWAY_URL/api/:splat   200
/health  https://RAILWAY_URL/health       200
/*       /index.html                      200
```

### Cloudflare R2 (Videos)

| Config | Value |
|--------|-------|
| Bucket | `nbu-edu-videos` |
| Domain | `videos.nbu-testing.devgokal.com` |
| Content | 12 MP4 episodes (~802 MB) + thumbnails |

---

## 5. Regional Strategist — Data Flow

```
Step 0: Select path (new business / existing)
    ↓
Step 1: Business profile (name, direction, city, district)
    ↓
Step 2: Upload Excel files (balance + PnL)
         → POST /api/rs/submissions
         → POST /api/rs/submissions/{id}/uploads
    ↓
Step 3: Coaching screen (preparation tips)
    ↓
Step 4: AI analysis
         → POST /api/rs/submissions/{id}/analysis
         Backend pipeline:
           parse Excel → calculate ratios → compare benchmarks
           → Claude API prompt → structured JSON result
    ↓
Step 5: Results dashboard
         - Score ring + breakdown
         - Recommendations + risk cards
         - Fergana heatmap (education centers)
         - Interactive Yandex Map (zones, recommendations, existing places)
```

---

## 6. i18n Architecture

All user-facing text uses `vue-i18n` with two locales:

| Locale | File | Size | Script |
|--------|------|------|--------|
| `uz` | `src/locales/uz.json` | 75 KB | Uzbek Latin (with `ʻ` U+02BB apostrophes) |
| `ru` | `src/locales/ru.json` | 97 KB | Russian Cyrillic |

Language switching via `LanguageSwitcher` component in the sidebar. Regional Strategist steps have additional per-step i18n files (`rs-step1-i18n.js`, `rs-step2-i18n.js`, `rs-step5-i18n.js`) merged at component level.

---

## 7. Interactive Maps

### Fergana SVG Map (`FerganaMap.vue`)
- Renders `fergana-districts.geojson` as interactive SVG paths
- Click to select district, hover for tooltip (population, area)
- Visual center algorithm for label placement
- Color-coded: cities (navy) vs districts (light blue)

### Yandex Maps Education Map (`public/maps/fergana-education/`)
- Embedded via iframe in Step 5 results
- Shows education centers, bookstores, stationery stores on Yandex Maps
- 3 recommendation zones (gap/mid/hot) as colored circles
- Custom marker icons with category labels (MARKAZ, KITOB, KANS, etc.)
- Heatmap overlay for business density visualization

### Uzbekistan SVG Map (`UzbekistanMap.vue`)
- Full country map for region selection on home dashboard

---

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

### Education Backend
```bash
cd frontend/backend
pip install -r requirements.txt
# Set DATABASE_URL in .env
python seed.py       # Seed database
uvicorn main:app --reload --port 8000
```

### Analytics Backend
```bash
cd backend
pip install -r requirements.txt
# Set DATABASE_URL, ANTHROPIC_API_KEY in .env
python seed.py       # Seed database
uvicorn app.main:app --reload --port 8000
```

### Environment Files

| File | Purpose |
|------|---------|
| `frontend/.env.local` | Dev: `VITE_API_URL=` (empty, uses Vite proxy) |
| `frontend/.env.production` | Prod: `VITE_API_URL=/api/rs` |
| `frontend/backend/.env` | Education backend: `DATABASE_URL`, `SECRET_KEY` |

---

## Project Structure

```
NBU-clean/
├── README.md
├── .gitignore
│
├── frontend/                      # Vue 3 SPA
│   ├── public/
│   │   ├── maps/fergana-education/  # Yandex Maps HTML
│   │   ├── samples/                 # Demo Excel files
│   │   ├── thumbnails/              # Course thumbnails
│   │   ├── logos/                    # NBU branding
│   │   ├── fergana-districts.geojson
│   │   ├── uzbekistan-regions.geojson
│   │   └── _redirects               # Cloudflare Pages routing
│   ├── src/
│   │   ├── components/              # 45 Vue components
│   │   ├── views/                   # 20+ view pages
│   │   ├── layouts/                 # 4 layout wrappers
│   │   ├── router/                  # Route definitions
│   │   ├── stores/                  # Pinia stores
│   │   ├── services/                # API clients
│   │   ├── composables/             # Vue composables
│   │   ├── data/                    # Static data files
│   │   ├── locales/                 # uz.json, ru.json
│   │   ├── i18n/                    # i18n configuration
│   │   └── App.vue
│   ├── backend/                     # Education FastAPI
│   │   ├── routes/                  # 6 route files
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   └── seed.py
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.*
│
├── backend/                         # Unified FastAPI (deploy)
│   ├── app/
│   │   ├── routes/                  # 9 route files
│   │   ├── services/                # 4 service files
│   │   ├── data/                    # peer_benchmarks.json
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db_async.py
│   │   ├── db_sync.py
│   │   ├── models_education.py
│   │   ├── models_analytics.py
│   │   ├── schemas.py
│   │   └── auth.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Procfile
│   ├── railway.json
│   └── nixpacks.toml
│
└── detailed_map_city/               # Map data generation
    ├── map_data.generated.js
    └── *.json                       # Raw place data
```
