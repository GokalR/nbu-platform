# NBU Analytics — Farg'ona viloyati (Vue 3 + Vite)

Frontend implementation of the Stitch-designed NBU Institutional Analytics dashboard.

## Stack

- **Vue 3** (Composition API, `<script setup>`)
- **Vite 5**
- **Vue Router 4** — file-based-style routes, lazy-loaded views
- **vue-i18n 10** — Uzbek (`uz`) / Russian (`ru`), persisted in `localStorage`
- **Tailwind CSS** — design tokens lifted from the Stitch HTML (Material 3 palette, Manrope/Inter, Material Symbols)
- **Pinia** — wired but not yet used (ready for state)

## Running locally

Requires Node.js 18+.

```bash
cd frontend
npm install
npm run dev
```

Opens at <http://localhost:5173>.

## Project structure

```
src/
  assets/main.css           Tailwind layers + base styles
  components/               Reusable UI atoms / molecules
    AppIcon.vue             Material Symbols wrapper
    AppSidebar.vue          Persistent left nav
    AppTopBar.vue           Sticky header + LanguageSwitcher
    LanguageSwitcher.vue    uz / ru toggle
    KpiCard.vue             Bento KPI tile
    ProgressBar.vue         Animated horizontal bar
    StatCard.vue            Card wrapping multiple ProgressBars
    DistrictList.vue        Selectable list (v-model)
    MapPanel.vue            SVG map with selected-district overlay
    PageHeader.vue          Eyebrow + title + subtitle
  data/districts.js         Static demo data
  i18n/index.js             createI18n + setLocale helper
  layouts/DefaultLayout.vue Sidebar + topbar + footer shell
  locales/                  uz.json, ru.json
  router/index.js           4 routes, lazy-loaded
  views/
    HomeView.vue                 KPI grid + map + districts + stat cards
    DistrictAnalyticsView.vue    Tab-based district deep-dive
    AiAdvisorView.vue            Chat-style AI assistant UI
    BusinessToolsView.vue        Tool catalogue grid
  App.vue                   <RouterView/> with fade transition
  main.js                   App bootstrap
```

## Adding a language

1. Add `src/locales/<code>.json`.
2. Register it in `src/i18n/index.js` (`messages` and `SUPPORTED`).
3. Add the label to `LanguageSwitcher.vue`.

## Adding a route

Add an entry to `src/router/index.js` and a file under `src/views/`. Add the nav item to `AppSidebar.vue` and a label key to both locale JSONs.

## Notes

- Demo data lives in `src/data/districts.js` and `src/data/regions.js` — replace with API calls when the backend is ready.
- The chat in `AiAdvisorView.vue` uses a stub response — wire it to your AI endpoint.

## Interactive Uzbekistan map

`src/components/UzbekistanMap.vue` renders an SVG map of the 14 administrative units
(12 viloyats + Karakalpakstan + Tashkent city). It loads geometry from
`public/uzbekistan-regions.geojson`, projects coordinates with a simple
equirectangular projection, and emits selection events.

The shipped GeoJSON is a **simplified placeholder** (rough polygons, ~5 KB) so the
app works out of the box. For production-quality borders, replace it with a
high-fidelity GeoJSON. Make sure each feature has `properties.key` matching one
of these IDs:

```
karakalpakstan, khorezm, navoiy, bukhara, samarqand, qashqadaryo,
surxondaryo, jizzax, sirdaryo, tashkent_region, tashkent_city,
namangan, andijan, fergana
```

Recommended sources (download then rename `properties.NAME_1` etc. to `key`):

- [GADM](https://gadm.org/download_country.html) — official admin level 1 boundaries
- [Natural Earth — Admin 1 States/Provinces](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/)
- [click_that_hood / public datasets](https://github.com/codeforgermany/click_that_hood)

You can also use [mapshaper.org](https://mapshaper.org) to simplify large GeoJSON
files (target ~50 KB) and rename properties before saving as GeoJSON.

To wire selection to your data, listen to `@update:modelValue` on the component
or use `v-model` (see [HomeView.vue](src/views/HomeView.vue) for an example
where map selection drives the KPI cards, stat bars, and info panel).
