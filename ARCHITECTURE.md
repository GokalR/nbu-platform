# NBU Platform — архитектура и потоки данных

Комплементарно к `PROJECT.md` (карта папок). Здесь — какие таблицы есть в БД,
как они связаны, как данные текут от Excel-шаблона до публичного дашборда.

---

## Таблицы в Railway Postgres

### AUTH

| Таблица | Поля | Назначение |
|---|---|---|
| `users` | id, email, password_hash, **role**, full_name | Логин + JWT. role='admin' даёт доступ к редактированию GM |

### GOLDEN MART (главная часть)

| Таблица | Что хранит | Сейчас в БД |
|---|---|---|
| `gm_entities` | список объектов (страна / область / город) | 9 строк |
| `gm_country` | значения по странам | 188 полей × 6 лет = до 6 строк |
| `gm_region`  | значения по областям | 169 полей × 6 лет = до 12 строк |
| `gm_city`    | значения по городам/туманам | 208 полей × 6 лет = 18+ строк |

### EDUCATION (учебная часть)
`courses`, `videos`, `learning_content`, `enrollments`, `progress` — для образовательного модуля. На GM не влияет.

### ANALYTICS (другие дашборды)
`analytics_*`, `rs_*` — для Regional Strategist. Тоже отдельный модуль.

---

## Структура `gm_entities`

```
key                level     parent_key        name_ru                name_uz                iso_kind
-----------------------------------------------------------------------------------------------------
uzbekistan         country   NULL              Узбекистан             Oʻzbekiston            NULL
fergana_region     region    uzbekistan        Ферганская область     Fargʻona viloyati      viloyat
samarqand_region   region    uzbekistan        Самаркандская обл.     Samarqand viloyati     viloyat
fargona_city       city      fergana_region    г. Фергана             Fargʻona shahri        shahar
qoqon_city         city      fergana_region    г. Коканд              Qoʻqon shahri          shahar
margilon_city      city      fergana_region    г. Маргилан            Margʻilon shahri       shahar
quvasoy_city       city      fergana_region    г. Кувасай             Quvasoy shahri         shahar
samarqand_city     city      samarqand_region  г. Самарканд           Samarqand shahri       shahar
kattaqorgon_city   city      samarqand_region  г. Каттакурган         Kattaqoʻrgʻon shahri   shahar
```

Это **lookup-таблица**. Имена городов уже двуязычные (`name_ru` + `name_uz`).

## Структура `gm_city` (на примере одной строки Коканда 2025)

| entity_key | year | region_key | s1_1 | s1_2 | s1_3 | s1_4 | s1_5 | s1_6 | s2_2 | s2_3 | ... | s11_7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qoqon_city | 2025 | fergana_region | `'Qoʻqon'` | `'city'` | `'no'` | 60 | 56 | 313600 | 9410.4 | 6371.1 | ... | 6923 |

Ключи колонок — позиционные: **`s{секция}_{поле}`**.
- `s1_1`..`s1_30` = §1 Базовая информация (название, тип, площадь, население, возрастные группы, ...)
- `s2_1`..`s2_7` = §2 Экономика — объёмы (промышленность, услуги, торговля, инвестиции, ...)
- `s11_1`..`s11_8` = §11 Здравоохранение
- `s21_*` = §21 Критические проблемы

**Один город × 6 годов = 6 строк** в `gm_city`.

---

## Pipeline 1 — Схема (Excel → код)

```
goldenmarts/golden_mart_city.xlsx     ← админ редактирует Excel
            │
            ▼ python goldenmarts/_to_md.py
goldenmarts/GM_city.md                ← человекочитаемая спека
            │
       ┌────┴────────────────────────────────┐
       ▼                                     ▼
python _md_to_schema_js.py        python _md_to_sqlalchemy.py
       │                                     │
       ▼                                     ▼
frontend/.../citySchema.js          backend/app/models_gm.py
(используется фронтом для           (используется бэком для
 рендера форм + детальной)           create_all() и SQL)
```

Когда меняешь Excel — нужно перегенерировать все три файла и закоммитить.

## Pipeline 2 — Сидинг данных при старте Railway

```
Railway деплоит → бэкенд стартует → lifespan() запускается:
  1. Base.metadata.create_all()             ← создать недостающие таблицы
  2. ensure_seed_admin()                    ← создать/обновить админа
  3. ensure_seed_entities()                 ← вставить 9 entities
  4. migrate_enum_values()                  ← конвертировать ru-text → enum-коды
  5. seed_gm_data()                         ← вставить верифицированные значения
                                              (ON CONFLICT DO NOTHING)
```

Все 5 идемпотентны — гонять при каждом редеплое безопасно.

---

## Flow 1 — Админ редактирует значение

```
Браузер (Cloudflare Pages)
   │ POST /api/auth/login (admin@nbu.uz / admin12345)
   ▼
Backend (Railway) → JWT токен с role='admin'
   │
   │ Браузер сохраняет в localStorage
   ▼
Открывает /admin/golden-mart
   │
   │ GET /api/gm/entities?level=city  → 4-9 entities
   │ Выбираем Коканд
   │ GET /api/gm/data/city/qoqon_city → 6 годов значений
   │
   │ Меняем «Промышленность 2025»: 9410.4 → 9500
   │ Жмём «Сохранить год 2025»
   ▼
PUT /api/gm/data/city/qoqon_city/2025
   { "values": { "s2_2": 9500 } }
   + Authorization: Bearer <jwt>
   ▼
Backend проверяет токен + admin role + валидное поле
   ▼
UPDATE gm_city SET s2_2=9500 WHERE entity_key='qoqon_city' AND year=2025
   ▼
200 OK → "Сохранено: 1 поле"
```

## Flow 2 — Публичный пользователь смотрит дашборд

```
Браузер: /districts?district=qoqon_city
   ▼
QoqonDashboard.vue mounted
   ▼
loader.js → loadEntity('city', 'qoqon_city')
   ▼
GET /api/gm/data/city/qoqon_city → 6 строк
   ▼
loader преобразует в:
{
  scalars: { s2_2: 9500 (последнее), s1_6: 319600, ... }
  yearly:  { s2_2: [4340, 5602, 5886, 6264, 9500, null], ... }
  source:  'api'
}
   ▼
QoqonDashboard рендерит:
  • scalars → KPI плитки
  • yearly  → sparkline графики
   ▼
Если API не отвечает → fallback на frontend/.../qoqon.js
```

## Flow 3 — Переключение языка RU ⇄ UZ

```
Юзер кликает UZ
   ▼
i18n.locale = 'uz'  (Vue реактивно)
   ▼
Все t('something') возвращают узбекские варианты:
   t('qoqon.kpi.industry')         → 'Sanoat'      (вместо 'Промышленность')
   t('gmEnum.objectType.city')     → 'Shahar'      (вместо 'Город')
   t('gmEnum.yesNo.no')            → 'Yoʻq'        (вместо 'Нет')
   ▼
Schema labels (admin + детальная):
   locale === 'uz' ? attr.labelUz : attr.label
   ▼
Имена городов:
   e.name_uz vs e.name_ru
```

---

## Что какого типа в БД

| Тип поля | Кол-во в city | Где хранится | Перевод |
|---|---|---|---|
| **Числовое** | ~179 / 208 | одна колонка `s{n}_{i}` | не нужен |
| **Enum-коды** | 7 (s1_2, s1_3, 5×priority) | одна колонка с кодом (`'city'`, `'no'`, `'high'`) | через `gmEnum.*` i18n при отображении |
| **Free-form текст** | ~22 (названия, описания) | колонка(и) с текстом | см. ниже |

**Free-form текст** включает:
- §1: Название (s1_1)
- §5: 6 названий стран (партнёры по торговле)
- §20: 5 названий махалли
- §21: 5 описаний проблем

---

## Карта файлов «где что менять»

| Что нужно изменить? | Где |
|---|---|
| Добавить новое поле в шаблон GM | `goldenmarts/golden_mart_*.xlsx` → запустить 3 codegen скрипта |
| Перевод подписей на узбекский | `goldenmarts/_translations_uz.json` → `_md_to_schema_js.py` |
| UI текст не из шаблона (заголовки секций, подписи) | `frontend/src/locales/ru.json` + `uz.json` |
| Добавить enum-поле | `frontend/src/data/goldenMart/enums.js` + `gmEnum.*` в локалях |
| Логика админки | `frontend/src/views/admin/GmAdminView.vue` (V1) или `GmAdminTableView.vue` (V2) |
| Публичный дашборд Коканда | `frontend/src/views/QoqonDashboard.vue` |
| Детальная панель GM | `frontend/src/views/QoqonGoldenMartDetail.vue` |
| API endpoints | `backend/app/routes/gm.py` |
| Какие entities существуют | `backend/app/main.py` → `ensure_seed_entities()` |
| Верифицированные значения для сидинга | `backend/app/seed_gm_data.py` |
| Проверить что в БД | `https://nbu-platform-production.up.railway.app/api/health/admin` или `/api/gm/data/city/qoqon_city` |
| Список endpoints на проде | `https://nbu-platform-production.up.railway.app/docs` |

---

## Ключевые правила

1. **Числа без языка** — лежат в одной колонке, отображаются одинаково
2. **Enum-поля** (тип, да/нет, приоритет) — лежат как коды, переводятся через i18n
3. **Свободный текст** — двуязычное хранение (см. отдельный раздел ниже)
4. **Один город = 6 строк** (по году), правишь через V1 (по годам) или V2 (Excel-таблица)
5. **Сидинг идемпотентен** — Railway редеплой не ломает админские правки
6. **Frontend → Backend → DB** — всегда через HTTP API
