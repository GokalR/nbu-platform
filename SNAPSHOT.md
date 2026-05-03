# NBU Platform — текущее состояние (верификация)

> Этот файл — **факт-чек снэпшот** того, что реально есть в репо на момент
> последнего коммита. Каждая цифра/файл проверены grep'ом по исходникам.
> Для общего понимания см. `PROJECT.md`. Для архитектурных потоков см.
> `ARCHITECTURE.md`. Этот файл — «что фактически работает СЕЙЧАС».

Снимок на коммите: **`e207c24` Sidebar: admin nav link visible only to admin role**

---

## 1. Структура репо (top-level)

```
NBU-clean/
├── PROJECT.md          ← карта папок + общий обзор
├── ARCHITECTURE.md     ← архитектура и потоки данных
├── SNAPSHOT.md         ← этот файл (верифицированный снэпшот)
├── README.md
│
├── backend/            ← Railway target (Dockerfile + Procfile)
│   └── app/
│       ├── main.py             FastAPI entry, lifespan, CORS, роуты, /health/admin
│       ├── auth.py             JWT + bcrypt
│       ├── db_async.py         BaseAsync, async_session, get_db
│       ├── models_education.py User + Education tables
│       ├── models_gm.py        ★ 4 GM tables (AUTO-GEN, 51558 chars)
│       ├── seed_gm_data.py     ★ верифицированные значения для 3 городов
│       └── routes/
│           └── gm.py           ★ 5 endpoints /api/gm/*
│
├── frontend/           ← Cloudflare Pages target (Vite build)
│   └── src/
│       ├── locales/        ru.json + uz.json (1989/1989)
│       ├── data/goldenMart/
│       │   ├── citySchema.js      ★ AUTO-GEN, 21 секций × 208 attrs
│       │   ├── regionSchema.js    ★ AUTO-GEN, 20 секций × 169 attrs
│       │   ├── countrySchema.js   ★ AUTO-GEN, 17 секций × 188 attrs
│       │   ├── enums.js           7 enum-полей + helpers
│       │   ├── schemaPicker.js    schemaForLevel(level)
│       │   ├── loader.js          loadEntity() с fallback
│       │   └── qoqon.js           статичный fallback для Qoqon
│       ├── views/
│       │   ├── QoqonDashboard.vue          ★ публичный дашборд (Style A+B)
│       │   ├── QoqonGoldenMartDetail.vue   ★ детальная страница (21 раздел)
│       │   └── admin/
│       │       ├── GmAdminView.vue         ★ V1 (по годам)
│       │       └── GmAdminTableView.vue    ★ V2 (Excel-таблица)
│       └── components/
│           └── AppSidebar.vue              ★ ссылка для admin
│
└── goldenmarts/        ← Golden Mart pipeline
    ├── golden_mart_country.xlsx
    ├── golden_mart_region.xlsx
    ├── golden_mart_city.xlsx
    ├── GM_country.md / GM_region.md / GM_city.md   AUTO-GEN
    ├── _to_md.py                                   xlsx → MD
    ├── _md_to_schema_js.py                         MD → frontend JS
    ├── _md_to_sqlalchemy.py                        MD → backend Python
    ├── _translations_uz.json                       RU → UZ для подписей
    └── PIPELINE.md                                 pipeline docs
```

> ✅ **`frontend/backend/` удалён** — Railway деплоит ТОЛЬКО `backend/app/`.

---

## 2. Backend: что в `lifespan` запускается на каждом старте

Из `backend/app/main.py` строки 120-170, проверено:

```
1. Base.metadata.create_all (async)         ← создание/обновление GM + Education таблиц
2. BaseSync.metadata.create_all (sync)      ← Analytics таблицы
3. ensure_seed_admin()                      ← создаёт/обновляет админа
4. ensure_seed_entities()                   ← вставляет 9 entities (idempotent)
5. migrate_enum_values()                    ← конвертирует ru-text → enum-коды
6. seed_gm_data()                           ← вставляет верифицированные значения
                                              (ON CONFLICT DO NOTHING)
```

Все 6 шагов идемпотентны. Сидинг выполняется **в фоне** (asyncio.create_task) — не блокирует старт сервера.

---

## 3. Таблицы в Railway Postgres (после первого старта)

### Auth
- `users` — id, email, password_hash, **role**, full_name, ...

### Golden Mart (4 таблицы)
| Таблица | Колонок данных | _uz колонок | Сидится |
|---|---|---|---|
| `gm_entities` | 9 (key, level, parent_key, name_ru, name_uz, ...) | — | 9 строк автоматически |
| `gm_country` | 188 + meta | (часть из 35 _uz total) | 0 строк сейчас |
| `gm_region` | 169 + meta | (часть из 35) | 1 строка (fergana_region 2025) |
| `gm_city` | 208 + meta | (часть из 35) | 18 строк (3 города × 6 лет) |

**Всего `_uz` колонок в трёх таблицах: 35** (для free-form текстовых полей, чтобы хранить и ru, и uz).

### Education / Analytics (для других модулей платформы)
- `users`, `courses`, `videos`, `learning_content`, `enrollments`, `progress`
- `analytics_*`, `rs_*`

---

## 4. API endpoints — реально зарегистрированные

### `/api/gm/*` — Golden Mart
Из `backend/app/routes/gm.py`, проверено:
- `GET  /api/gm/entities`               public, optional `?level=`
- `GET  /api/gm/data/{level}/{key}`     public, all years
- `GET  /api/gm/data/{level}/{key}/{year}` public, single year
- `PUT  /api/gm/data/{level}/{key}/{year}` **admin role required**
- `GET  /api/gm/coverage/{level}/{key}` public, fill stats

### Health
- `GET /health` — общий health (status, env, model, anthropicConfigured)
- `GET /api/health` — `{status: "ok"}`
- `GET /api/health/admin` — диагностический (показывает существует ли seed-admin)

### Auth (Education)
- `POST /api/auth/login`
- `POST /api/auth/register`
- `GET  /api/auth/me`

### Прочее
- `/api/courses/*`, `/api/videos/*`, `/api/me/dashboard` — Education
- `/api/rs/*` — Regional Strategist + Analytics

Полный список auto-genered → откроешь `/docs` на Railway.

---

## 5. Auto-seed entities (ровно 9 штук)

Из `ensure_seed_entities()`, проверено:

| key | level | parent | name_ru | name_uz |
|---|---|---|---|---|
| uzbekistan | country | — | Узбекистан | Oʻzbekiston |
| fergana_region | region | uzbekistan | Ферганская область | Fargʻona viloyati |
| samarqand_region | region | uzbekistan | Самаркандская область | Samarqand viloyati |
| fargona_city | city | fergana_region | г. Фергана | Fargʻona shahri |
| qoqon_city | city | fergana_region | г. Коканд | Qoʻqon shahri |
| margilon_city | city | fergana_region | г. Маргилан | Margʻilon shahri |
| quvasoy_city | city | fergana_region | г. Кувасай | Quvasoy shahri |
| samarqand_city | city | samarqand_region | г. Самарканд | Samarqand shahri |
| kattaqorgon_city | city | samarqand_region | г. Каттакурган | Kattaqoʻrgʻon shahri |

---

## 6. Auto-seed данных (что пишется в gm_city / gm_region)

Из `seed_gm_data.py`:

### Qoqon city — 6 строк (2021..2026)
- Identity: `s1_1='Коканд'` (RU), `s1_1_uz='Qoʻqon'` (UZ), `s1_2='city'`, `s1_3='no'`, `s1_4=60`, `s1_5=56`
- Population (s1_6): `[256_400, 259_700, 303_600, 308_100, 313_600, 319_600]`
- Births (s11_7, s9_5): `[5783, 6561, 7976, 7654, 6923]` (2021..2025)
- Deaths (s11_8, s9_6): `[1565, 1249, 1499, 1490, 1513]`
- Sectors 2021..2025: industry/services/trade/construction/agri/invest (s2_2..s2_7)
- Age structure 2025 (s1_12..s1_28): 17 брекетов

### Fergana city — 6 строк
- `s1_1='Фергана'`, `s1_1_uz='Fargʻona'`, `s1_2='city'`, `s1_3='yes'`, `s1_4=110`, `s1_5=74`
- Аналогично 6 секторов + население + рождения/смерти + age 2025

### Margilan city — 6 строк
- `s1_1='Маргилан'`, `s1_1_uz='Margʻilon'`, `s1_2='city'`, `s1_3='no'`, `s1_4=52`, `s1_5=50`
- Аналогично

### Fergana region — 1 строка (2025)
- `s1_1='Фергана'` + `s20_1..s20_6` (real-growth indices)

**ON CONFLICT DO NOTHING** — повторные деплои не перезатрут админские правки.

---

## 7. Frontend routes (включая админ)

Из `router/index.js`, проверено:
- `/login`, `/`, `/districts`, `/ai`, `/tools`, `/education`
- `/education/courses/:id`, `/education/courses/:courseId/learn/:videoId`
- `/tools/fincontrol/*` (10 роутов)
- `/tools/regional-strategist/*` (3 роута)
- **`/admin/golden-mart`** → `GmAdminView.vue` (V1 по годам), `meta.requiresAdmin: true`
- **`/admin/golden-mart/table`** → `GmAdminTableView.vue` (V2 Excel), `meta.requiresAdmin: true`

---

## 8. Sidebar — кнопка для админа

Из `AppSidebar.vue`, проверено:
- Базовые ссылки: Главная, Анализ районов, AI Советник (disabled), Бизнес AI, NBU Education
- **Админ-ссылка**: «Админ панель» с золотым `[ADMIN]` бэйджем — рендерится только если `auth.user?.role === 'admin'`
- Реактивно: разлогинишься — пропадёт; залогинишься админом — появится
- i18n: `nav.admin` = «Админ панель» / «Admin panel»

---

## 9. i18n — namespace size

Парность RU/UZ: **1989 / 1989** (✅ нет расхождений)

| Namespace | Кол-во ключей |
|---|---|
| `qoqon.*` | 93 |
| `gmAdmin.*` | 18 |
| `gmEnum.*` | 8 |
| `district.aiAnalysis.*` | 202 |

---

## 10. Enum-поля (хранятся как коды, переводятся в UI)

В sync между frontend и backend, проверено:

| field key | значения | i18n group |
|---|---|---|
| `s1_2` (Тип объекта) | city, tuman | gmEnum.objectType |
| `s1_3` (Админ. центр области) | yes, no | gmEnum.yesNo |
| `s21_2`, `s21_5`, `s21_8`, `s21_11`, `s21_14` (Приоритеты проблем) | high, medium, low | gmEnum.priority |

В админке для этих полей рендерится `<select>` с локализованными опциями.

---

## 11. Free-form текстовые поля → парные `_uz` колонки

Codegen `_md_to_sqlalchemy.py` для полей с `unit='текст'` (НЕ enum) автоматически генерирует:
```python
s1_1    = Column(Text, nullable=True)  # Название (текст)
s1_1_uz = Column(Text, nullable=True)  # Название (UZ)
```

**Всего 35 пар колонок** в трёх GM таблицах. Админ-форма рендерит два input'а рядом для этих полей.

---

## 12. Статичные fallback в loader.js

Если API отвечает пустой массив или падает, фронт переключается на статический JS:

```js
const STATIC_FALLBACKS = {
  city: {
    qoqon_city: () => import('./qoqon.js').then(m => m.QOQON_GM),
  },
}
```

**Только Qoqon имеет статичный fallback.** Для остальных entities — пустой объект (`source: 'empty'`). Это нормально, потому что данные тянутся с API.

---

## 13. Pipeline — codegen

Все три скрипта в `goldenmarts/`:

| Скрипт | In | Out | Что делает |
|---|---|---|---|
| `_to_md.py` | `golden_mart_*.xlsx` | `GM_*.md` | xlsx → markdown спека |
| `_md_to_schema_js.py` | `GM_*.md` + `_translations_uz.json` | 3 frontend схемы | Schema constants для UI |
| `_md_to_sqlalchemy.py` | `GM_*.md` + ENUM_FIELDS | `backend/app/models_gm.py` | SQLAlchemy модели |

Запуск всех трёх:
```bash
PYTHONIOENCODING=utf-8 python goldenmarts/_to_md.py
PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_schema_js.py
PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_sqlalchemy.py
```

---

## 14. Production credentials

### Default admin (auto-seed)
```
email:    admin@nbu.uz
password: admin12345
```

Override через Railway env vars:
- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`
- `SEED_ADMIN_NAME`

Поведение `ensure_seed_admin()` (`main.py:91-118`):
- Если юзера нет → создаёт с role='admin', паролем из env
- Если есть → синкает role='admin' и пароль из env (env vars — единственный источник правды)

### URLs
- Frontend: `https://nbu-platform.pages.dev`
- Backend: `https://nbu-platform-production.up.railway.app`
- Swagger: `/docs`
- Health: `/api/health`, `/api/health/admin`

---

## 15. Recent commits (последние 15)

```
e207c24  Sidebar: admin nav link visible only to admin role
fcc727d  ARCHITECTURE.md + bilingual storage for free-form text fields
ad01dfc  Enum-typed GM fields: language-agnostic codes + auto-translate
acf3b0c  Auto-seed verified Qoqon/Fergana/Margilan data into Railway DB
c3a5b8c  Admin V2 — Excel table view (years as columns)
1745e8c  Auto-seed GM entities on backend startup
3839c87  Delete dead frontend/backend/ + add PROJECT.md guide
e6d508f  Port Golden Mart backend to the REAL Railway backend (backend/app/)
0d300b8  Add /api/health/admin debug endpoint
67b8151  ensure_seed_admin always resets password from env on startup
7a67fb7  Full bilingual Qoqon dashboard + auto-seed admin on Railway
73d1a75  Bilingual hero panel (Style A + B) + fix виловати + drop redundant row
b31b4a8  Style B KPI tiles: dual-row labelled chips (YoY + 5-year)
1f5bbd9  Fix Cloudflare deploy + add seed admin user
21cbe17  Real bilingual: RU/UZ labels for all sections + 200+ fields
```

---

## 16. Status — verified

### ✅ Точно работает (проверено в исходниках)
- 4 GM таблицы определены и регистрируются в `Base.metadata`
- 5 GM endpoints зарегистрированы и привязаны к моделям
- 9 entities авто-сидятся idempotently
- 18 строк gm_city + 1 строка gm_region авто-сидятся (ON CONFLICT DO NOTHING)
- Admin auto-seed на каждом старте + миграция enum значений
- Schema codegen pipeline (xlsx → md → JS + Python)
- Frontend admin V1 (по годам) + V2 (Excel) с переключателем
- Sidebar admin-link визивел только для role='admin'
- Билингвал: 1989 ключей в обоих локалях, никаких diff
- 35 `_uz` колонок для free-form текстов
- 7 enum-полей с языко-независимыми кодами
- Public dashboard (Qoqon) — Style A glassmorphism + Style B Fergana-brief
- Loader API → fallback на статический qoqon.js

### 🔲 Pending (честно)
- Только **Qoqon** имеет статичный fallback в loader.js — Fergana/Margilan публичные дашборды используют старую `districtAnalytics.js` (не GM)
- В `gm_country` (Узбекистан) **0 строк** — национальные данные не извлечены
- В `gm_region` только **1 строка** (Fergana 2025 с real-growth) — остальные годы пустые
- Per-cell metadata (verified flag, source, history) — отложено по выбору пользователя (option A)
- Frontend role-guard для `/admin/golden-mart`: backend возвращает 403 на write без admin role, но любой залогиненый юзер может ОТКРЫТЬ страницу (там просто 401/403 на save)
- UI добавления нового entity (нового города) — нет. Сейчас редактирование только существующих 9.
- UI удаления годовой строки или entity — нет. Только обнуление полей через clear → save.

### 🐛 Известные ограничения
- ERR_CONNECTION_RESET на `*.pages.dev` из некоторых сетей CIS — обходится VPN или custom domain
- Cloudflare `_redirects` не может прокси-rewrite на Railway — поэтому фронт зовёт Railway напрямую через `VITE_BACKEND_URL`
- При смене Excel-схемы Postgres не делает auto-ALTER на существующие таблицы. Для production-БД с данными нужна ручная миграция (для свежей пустой DB всё ок).
