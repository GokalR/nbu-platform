<script setup>
/**
 * Qoqon — Golden Mart detailed view (tabbed).
 *
 * 21 sections grouped into 6 thematic tabs (mirroring the Fergana
 * 6-tab pattern). User picks a tab, sees only that tab's sections
 * rendered as cards. Sections without verified data render dashed
 * with "Нет данных" pills so the data-gap is visible.
 */
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import { isEnumField, isFreeTextField, enumLabel, valueForLocale } from '@/data/goldenMart/enums.js'

const { t, locale } = useI18n()
import {
  CITY_SECTIONS, CITY_TOTAL_FIELDS, CITY_TABS, tabSections,
} from '@/data/goldenMart/citySchema.js'
import { loadEntity } from '@/data/goldenMart/loader.js'

const router = useRouter()
const route = useRoute()

// Live data: API → fallback to static qoqon.js. Empty until mounted.
const data = ref({})
const dataSource = ref('loading')

onMounted(async () => {
  const loaded = await loadEntity('city', 'qoqon_city')
  data.value = loaded.scalars
  dataSource.value = loaded.source
})
const activeTab = ref(CITY_TABS[0].id)

const filledCount = computed(() =>
  CITY_SECTIONS.reduce(
    (n, s) => n + s.attrs.filter((a) => data.value[a.key] != null && data.value[a.key] !== '').length,
    0,
  ),
)
const coveragePct = computed(() => Math.round((filledCount.value / CITY_TOTAL_FIELDS) * 100))

function sectionCoverage(section) {
  const filled = section.attrs.filter((a) => data.value[a.key] != null && data.value[a.key] !== '').length
  return { filled, total: section.attrs.length }
}

function tabCoverage(tab) {
  const sections = tabSections(tab.id)
  let filled = 0, total = 0
  for (const s of sections) {
    const c = sectionCoverage(s)
    filled += c.filled; total += c.total
  }
  return { filled, total }
}

function fmt(val, unit, fieldKey) {
  if (val == null || val === '') return null
  // Enum fields: translate code → localized label
  if (fieldKey && isEnumField(fieldKey)) {
    return enumLabel(fieldKey, val, t)
  }
  if (typeof val === 'number') {
    if (unit === '%') return `${val.toFixed(val % 1 === 0 ? 0 : 1)}%`
    if (unit === 'на 1000') return `${val.toFixed(1)}`
    return val.toLocaleString('ru-RU').replace(/,/g, ' ')
  }
  return String(val)
}

const activeSections = computed(() => tabSections(activeTab.value))

function backToOverview() {
  const q = { ...route.query }
  delete q.view
  router.push({ path: route.path, query: q })
}
function backToList() {
  const q = { ...route.query }
  delete q.district
  delete q.view
  router.push({ path: route.path, query: q })
}
</script>

<template>
  <div class="gmd-shell">
    <!-- Toolbar -->
    <div class="gmd-toolbar">
      <button class="gmd-back-btn" @click="backToOverview">
        <AppIcon name="arrow_back" /> К обзорной панели
      </button>
      <button class="gmd-back-btn ghost" @click="backToList">
        <AppIcon name="map" /> К списку городов
      </button>
    </div>

    <!-- Hero brief — rounded blue panel like Fergana -->
    <header class="gmd-brief">
      <div class="gmd-brief-glow" />
      <div class="gmd-brief-content">
        <div class="gmd-brief-eyebrow">GOLDEN MART · ДЕТАЛЬНЫЕ ДАННЫЕ ГОРОДА</div>
        <h1 class="gmd-brief-title">Qoʻqon</h1>
        <p class="gmd-brief-sub">
          Полный шаблон Golden Mart · 21 раздел · 6 тематических вкладок ·
          источник значений: <strong>fergana/</strong> PDF (farstat.uz)
        </p>
        <div class="gmd-brief-coverage">
          <div class="gmd-brief-cov-bar">
            <div class="gmd-brief-cov-fill" :style="{ width: `${coveragePct}%` }" />
          </div>
          <div class="gmd-brief-cov-meta">
            <span class="gmd-brief-cov-pct">{{ coveragePct }}%</span>
            <span class="gmd-brief-cov-text">
              {{ filledCount }} из {{ CITY_TOTAL_FIELDS }} полей · остальные ждут источников
            </span>
          </div>
        </div>
      </div>
    </header>

    <!-- Pill tab nav -->
    <nav class="gmd-tab-nav">
      <button
        v-for="tab in CITY_TABS"
        :key="tab.id"
        class="gmd-tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <span class="gmd-tab-num">{{ tab.num }}</span>
        <AppIcon :name="tab.icon" class="gmd-tab-icon" />
        <span class="gmd-tab-label">{{ tab.label }}</span>
        <span class="gmd-tab-cov">{{ tabCoverage(tab).filled }}/{{ tabCoverage(tab).total }}</span>
      </button>
    </nav>

    <!-- Active tab body -->
    <main class="gmd-main">
      <article
        v-for="section in activeSections"
        :key="section.n"
        class="gmd-section"
        :class="{ 'is-empty': sectionCoverage(section).filled === 0 }"
      >
        <header class="gmd-section-head">
          <div class="gmd-section-num">{{ String(section.n).padStart(2, '0') }}</div>
          <div class="gmd-section-icon"><AppIcon :name="section.icon" /></div>
          <div class="gmd-section-meta">
            <h2 class="gmd-section-title">{{ locale === 'uz' ? (section.titleUz || section.title) : section.title }}</h2>
            <div class="gmd-section-sub">
              <span class="gmd-section-cov">
                {{ sectionCoverage(section).filled }} / {{ sectionCoverage(section).total }} полей
              </span>
              <span v-if="sectionCoverage(section).filled === 0" class="gmd-pill-empty">Нет данных</span>
              <span
                v-else-if="sectionCoverage(section).filled === sectionCoverage(section).total"
                class="gmd-pill-full"
              >Заполнено полностью</span>
              <span v-else class="gmd-pill-partial">Частично</span>
            </div>
          </div>
        </header>

        <div class="gmd-section-body">
          <table class="gmd-table">
            <tbody>
              <tr
                v-for="attr in section.attrs"
                :key="attr.key"
                :class="{ 'is-empty-row': valueForLocale(data, attr, locale) == null || valueForLocale(data, attr, locale) === '' }"
              >
                <td class="gmd-cell-label">{{ locale === 'uz' ? (attr.labelUz || attr.label) : attr.label }}</td>
                <td class="gmd-cell-unit">{{ attr.unit }}</td>
                <td class="gmd-cell-val">
                  <template v-if="valueForLocale(data, attr, locale) != null && valueForLocale(data, attr, locale) !== ''">
                    <span class="gmd-val">{{ fmt(valueForLocale(data, attr, locale), attr.unit, attr.key) }}</span>
                  </template>
                  <template v-else>
                    <span class="gmd-no-data">Нет данных</span>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </main>

    <footer class="gmd-foot">
      <div>
        Источник схемы: <strong>goldenmarts/golden_mart_city.xlsx</strong> · 21 раздел.
        Источник значений: верифицированные строки <strong>Qoʻqon shahri</strong> в PDF
        farstat.uz.
      </div>
      <div class="gmd-foot-key">qoqon_city · golden_mart_detail · tab: {{ activeTab }}</div>
    </footer>
  </div>
</template>

<style scoped>
.gmd-shell {
  --bg: #F4F6FB;
  --surface: #FFFFFF;
  --ink: #0F1B2D;
  --ink-muted: #475569;
  --line: #E2E8F0;
  --primary: #0054A6;
  --primary-dark: #003D7C;

  background: var(--bg);
  min-height: 100vh;
  font-family: 'Manrope', system-ui, sans-serif;
  color: var(--ink);
  padding: 28px 56px 80px;
}

/* Toolbar */
.gmd-toolbar {
  max-width: 1320px; margin: 0 auto 16px;
  display: flex; align-items: center; gap: 10px;
}
.gmd-back-btn {
  display: inline-flex; align-items: center; gap: 8px;
  background: #fff; border: 1px solid var(--line); color: var(--ink);
  font-size: 13px; font-weight: 700; font-family: inherit;
  padding: 8px 14px 8px 10px; border-radius: 999px; cursor: pointer;
  transition: background 0.2s;
}
.gmd-back-btn:hover { background: rgba(0,84,166,0.04); }
.gmd-back-btn.ghost { background: transparent; }

/* Brief — rounded blue panel like Fergana */
.gmd-brief {
  max-width: 1320px; margin: 0 auto 24px;
  background: linear-gradient(135deg, #001b3d 0%, #003D7C 65%, #0054A6 100%);
  color: #fff;
  border-radius: 24px;
  padding: clamp(28px, 3vw, 40px);
  box-shadow: 0 24px 56px -24px rgba(0,27,61,0.40);
  position: relative;
  overflow: hidden;
}
.gmd-brief-glow {
  position: absolute; top: -50%; right: -20%;
  width: 700px; height: 700px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 60%);
  pointer-events: none;
}
.gmd-brief-content { position: relative; }
.gmd-brief-eyebrow {
  font-size: 13px; font-weight: 800; letter-spacing: 0.16em;
  color: #93C5FD; text-transform: uppercase;
}
.gmd-brief-title {
  font-size: clamp(36px, 5vw, 56px); font-weight: 900;
  letter-spacing: -0.03em; line-height: 1; margin: 10px 0 14px;
}
.gmd-brief-sub {
  font-size: 14px; font-weight: 600;
  color: rgba(191,219,254,0.80); line-height: 1.55;
  max-width: 720px; margin: 0 0 24px;
}
.gmd-brief-coverage {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  padding: 18px 22px; border-radius: 14px;
  max-width: 520px;
}
.gmd-brief-cov-bar {
  height: 8px; background: rgba(255,255,255,0.10);
  border-radius: 999px; overflow: hidden; margin-bottom: 10px;
}
.gmd-brief-cov-fill {
  height: 100%;
  background: linear-gradient(90deg, #FBBF24, #F59E0B);
  border-radius: 999px;
  transition: width 0.5s ease;
}
.gmd-brief-cov-meta {
  display: flex; justify-content: space-between; align-items: baseline; gap: 12px;
}
.gmd-brief-cov-pct {
  font-size: 22px; font-weight: 900; color: #FCD34D;
  font-variant-numeric: tabular-nums;
}
.gmd-brief-cov-text {
  font-size: 12px; font-weight: 600;
  color: rgba(191,219,254,0.70);
}

/* Pill tab nav */
.gmd-tab-nav {
  max-width: 1320px; margin: 0 auto 20px;
  display: flex; gap: 4px; padding: 6px;
  background: #ECEEF0; border-radius: 14px;
  overflow-x: auto;
}
.gmd-tab {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 18px; border-radius: 10px;
  font-size: 14px; font-weight: 700; font-family: inherit;
  color: #424751; background: transparent; border: none;
  cursor: pointer; white-space: nowrap; flex-shrink: 0;
  transition: all 0.2s;
}
.gmd-tab:hover { color: var(--primary-dark); }
.gmd-tab.active {
  background: #fff; color: var(--primary-dark);
  box-shadow: 0 2px 6px rgba(0,27,61,0.08);
}
.gmd-tab-num {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px; font-weight: 800; opacity: 0.6;
}
.gmd-tab-icon { font-size: 16px; }
.gmd-tab-cov {
  font-family: ui-monospace, monospace;
  font-size: 11px; font-weight: 700;
  color: var(--ink-muted); opacity: 0.7;
  padding: 2px 6px; border-radius: 6px;
  background: rgba(15,23,42,0.04);
}
.gmd-tab.active .gmd-tab-cov {
  background: rgba(0,84,166,0.10); color: var(--primary); opacity: 1;
}

/* Sections */
.gmd-main {
  max-width: 1320px; margin: 0 auto;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
  gap: 18px;
}
.gmd-section {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.gmd-section:hover {
  border-color: rgba(0,84,166,0.18);
  box-shadow: 0 1px 0 rgba(15,23,42,0.02), 0 12px 28px -16px rgba(15,23,42,0.10);
}
.gmd-section.is-empty {
  background: rgba(248,250,252,0.7); border-style: dashed;
}

.gmd-section-head {
  display: flex; align-items: center; gap: 14px; padding: 18px 22px;
  border-bottom: 1px dashed var(--line);
}
.gmd-section-num {
  font-family: ui-monospace, monospace;
  font-size: 11px; font-weight: 800; color: var(--primary);
  background: rgba(0,84,166,0.08);
  padding: 4px 8px; border-radius: 6px; letter-spacing: 0.05em;
}
.gmd-section.is-empty .gmd-section-num { color: var(--ink-muted); background: rgba(15,23,42,0.06); }

.gmd-section-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,84,166,0.10); color: var(--primary);
}
.gmd-section.is-empty .gmd-section-icon { background: rgba(15,23,42,0.06); color: var(--ink-muted); }

.gmd-section-meta { flex: 1; min-width: 0; }
.gmd-section-title {
  font-size: 17px; font-weight: 800; letter-spacing: -0.01em;
  color: var(--ink); margin: 0;
}
.gmd-section.is-empty .gmd-section-title { color: var(--ink-muted); }

.gmd-section-sub {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 4px;
}
.gmd-section-cov {
  font-size: 12px; font-weight: 700; color: var(--ink-muted);
  font-variant-numeric: tabular-nums;
}
.gmd-pill-full {
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
  background: rgba(16,185,129,0.12); color: #047857;
  padding: 3px 9px; border-radius: 999px;
}
.gmd-pill-partial {
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
  background: rgba(245,158,11,0.12); color: #B45309;
  padding: 3px 9px; border-radius: 999px;
}
.gmd-pill-empty {
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
  background: rgba(15,23,42,0.06); color: var(--ink-muted);
  padding: 3px 9px; border-radius: 999px;
}

.gmd-section-body { padding: 0; }
.gmd-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.gmd-table tr { border-bottom: 1px solid var(--line); }
.gmd-table tr:last-child { border-bottom: none; }
.gmd-table tr.is-empty-row { background: rgba(248,250,252,0.5); }
.gmd-table tr:hover { background: rgba(0,84,166,0.03); }
.gmd-cell-label { padding: 11px 22px; font-weight: 600; color: var(--ink); }
.gmd-cell-unit { padding: 11px 12px; font-size: 11.5px; color: var(--ink-muted); font-weight: 600; white-space: nowrap; }
.gmd-cell-val { padding: 11px 22px; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.gmd-val { font-weight: 800; font-size: 14px; color: var(--ink); }
.gmd-no-data {
  font-size: 11px; font-weight: 700;
  background: rgba(15,23,42,0.05); color: var(--ink-muted);
  padding: 4px 10px; border-radius: 999px; letter-spacing: 0.04em;
}

.gmd-foot {
  max-width: 1320px; margin: 40px auto 0; padding: 20px 0;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: var(--ink-muted); border-top: 1px solid var(--line);
  flex-wrap: wrap; gap: 12px;
}
.gmd-foot-key {
  font-family: ui-monospace, monospace; font-size: 11px;
  color: var(--ink-muted); padding: 4px 10px;
  background: rgba(15,23,42,0.04); border-radius: 6px;
}

@media (max-width: 800px) {
  .gmd-shell { padding: 20px 20px 60px; }
  .gmd-cell-label, .gmd-cell-val { padding-left: 14px; padding-right: 14px; }
}
</style>
