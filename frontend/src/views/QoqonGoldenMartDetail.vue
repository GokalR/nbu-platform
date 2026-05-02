<script setup>
/**
 * Qoqon — Golden Mart detailed view.
 *
 * Renders all 21 sections from the unified Golden Mart city template.
 * Schema lives in goldenMart/citySchema.js, data in goldenMart/qoqon.js.
 * Fields without a verified value render a "Нет данных" pill so the
 * data-gap is visible (drives next-step source acquisition decisions).
 */
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import { CITY_SECTIONS, CITY_TOTAL_FIELDS } from '@/data/goldenMart/citySchema.js'
import { QOQON_GM } from '@/data/goldenMart/qoqon.js'

const router = useRouter()
const route = useRoute()

const data = QOQON_GM

const filledCount = computed(() =>
  CITY_SECTIONS.reduce(
    (n, s) => n + s.attrs.filter((a) => data[a.key] != null && data[a.key] !== '').length,
    0,
  ),
)
const coveragePct = computed(() => Math.round((filledCount.value / CITY_TOTAL_FIELDS) * 100))

// Per-section coverage (for the section card subtitle)
function sectionCoverage(section) {
  const filled = section.attrs.filter((a) => data[a.key] != null && data[a.key] !== '').length
  return { filled, total: section.attrs.length }
}

// Format value with unit
function fmt(val, unit) {
  if (val == null || val === '') return null
  if (typeof val === 'number') {
    if (unit === '%') return `${val.toFixed(val % 1 === 0 ? 0 : 1)}%`
    if (unit === 'на 1000') return `${val.toFixed(1)}`
    return val.toLocaleString('ru-RU').replace(/,/g, ' ')
  }
  return String(val)
}

// Collapsible state — sections with >0 filled fields default open
const collapsed = ref(
  Object.fromEntries(
    CITY_SECTIONS.map((s) => {
      const cov = s.attrs.filter((a) => data[a.key] != null && data[a.key] !== '').length
      return [s.n, cov === 0]
    }),
  ),
)
function toggle(n) { collapsed.value[n] = !collapsed.value[n] }

function backToOverview() {
  // Stay on the same district, just drop &view=goldenmart
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
    <header class="gmd-head">
      <div class="gmd-head-inner">
        <button class="gmd-back-btn" @click="backToOverview">
          <AppIcon name="arrow_back" /> К обзорной панели Коканда
        </button>
        <button class="gmd-back-btn ghost" @click="backToList">
          <AppIcon name="map" /> К списку городов
        </button>
        <div class="gmd-eyebrow">Golden Mart · уровень города/тумана · 21 раздел</div>
        <h1 class="gmd-title">Qoʻqon — детальные данные</h1>
        <p class="gmd-sub">
          Полный шаблон Golden Mart для города. Заполненные поля основаны на
          верифицированных данных из <strong>fergana/</strong> PDF (farstat.uz).
          Поля без верифицированного источника помечены «Нет данных».
        </p>
        <div class="gmd-coverage">
          <div class="gmd-coverage-bar">
            <div class="gmd-coverage-fill" :style="{ width: `${coveragePct}%` }" />
          </div>
          <div class="gmd-coverage-meta">
            <span class="gmd-coverage-pct">{{ coveragePct }}%</span>
            <span class="gmd-coverage-text">
              {{ filledCount }} из {{ CITY_TOTAL_FIELDS }} полей заполнено
            </span>
          </div>
        </div>
      </div>
    </header>

    <main class="gmd-main">
      <article
        v-for="section in CITY_SECTIONS"
        :key="section.n"
        class="gmd-section"
        :class="{ 'is-collapsed': collapsed[section.n], 'is-empty': sectionCoverage(section).filled === 0 }"
      >
        <header class="gmd-section-head" @click="toggle(section.n)">
          <div class="gmd-section-num">{{ String(section.n).padStart(2, '0') }}</div>
          <div class="gmd-section-icon"><AppIcon :name="section.icon" /></div>
          <div class="gmd-section-meta">
            <h2 class="gmd-section-title">{{ section.title }}</h2>
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
          <button class="gmd-section-toggle">
            <AppIcon :name="collapsed[section.n] ? 'expand_more' : 'expand_less'" />
          </button>
        </header>

        <div v-if="!collapsed[section.n]" class="gmd-section-body">
          <table class="gmd-table">
            <tbody>
              <tr
                v-for="attr in section.attrs"
                :key="attr.key"
                :class="{ 'is-empty-row': data[attr.key] == null || data[attr.key] === '' }"
              >
                <td class="gmd-cell-label">{{ attr.label }}</td>
                <td class="gmd-cell-unit">{{ attr.unit }}</td>
                <td class="gmd-cell-val">
                  <template v-if="data[attr.key] != null && data[attr.key] !== ''">
                    <span class="gmd-val">{{ fmt(data[attr.key], attr.unit) }}</span>
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
      <div class="gmd-foot-key">qoqon_city · golden_mart_detail</div>
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
  --gold: #F59E0B;
  --green: #10B981;

  background: var(--bg);
  min-height: 100vh;
  font-family: 'Manrope', system-ui, sans-serif;
  color: var(--ink);
  padding-bottom: 80px;
}

.gmd-head {
  background:
    radial-gradient(800px 360px at 30% 0%, rgba(0,84,166,0.18), transparent 60%),
    linear-gradient(135deg, #061B36 0%, #0A2848 50%, #103E6E 100%);
  color: #fff;
  padding: 36px 56px 56px;
}
.gmd-head-inner { max-width: 1200px; margin: 0 auto; }
.gmd-back-btn {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.16);
  color: #fff; font-size: 13px; font-weight: 700;
  padding: 8px 14px 8px 10px; border-radius: 999px; cursor: pointer;
  transition: background 0.2s; margin-right: 10px;
}
.gmd-back-btn:hover { background: rgba(255,255,255,0.16); }
.gmd-back-btn.ghost { background: transparent; }

.gmd-eyebrow {
  margin-top: 24px;
  font-size: 11px; font-weight: 800; letter-spacing: 0.18em;
  color: #FCD34D; text-transform: uppercase;
}
.gmd-title {
  font-size: clamp(36px, 5vw, 56px); line-height: 1; font-weight: 900;
  letter-spacing: -0.03em; margin: 8px 0 14px;
}
.gmd-sub {
  font-size: 14px; font-weight: 500; line-height: 1.6;
  color: rgba(255,255,255,0.72); max-width: 760px; margin: 0 0 24px;
}
.gmd-coverage {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  padding: 16px 20px; border-radius: 14px; backdrop-filter: blur(8px);
}
.gmd-coverage-bar {
  height: 8px; background: rgba(255,255,255,0.10); border-radius: 999px;
  overflow: hidden; margin-bottom: 10px;
}
.gmd-coverage-fill {
  height: 100%; background: linear-gradient(90deg, #FBBF24, #F59E0B);
  border-radius: 999px; transition: width 0.5s ease;
}
.gmd-coverage-meta {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 13px;
}
.gmd-coverage-pct { font-size: 22px; font-weight: 900; color: #FCD34D; font-variant-numeric: tabular-nums; }
.gmd-coverage-text { color: rgba(255,255,255,0.6); font-weight: 600; }

.gmd-main {
  max-width: 1200px; margin: 0 auto; padding: 32px 56px 0;
  display: flex; flex-direction: column; gap: 14px;
}

.gmd-section {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; overflow: hidden;
  transition: border-color 0.2s;
}
.gmd-section:hover { border-color: rgba(0,84,166,0.20); }
.gmd-section.is-empty { background: rgba(248,250,252,0.7); border-style: dashed; }

.gmd-section-head {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 22px; cursor: pointer; user-select: none;
}
.gmd-section.is-collapsed .gmd-section-head:hover { background: rgba(0,84,166,0.03); }

.gmd-section-num {
  font-family: ui-monospace, monospace;
  font-size: 12px; font-weight: 800; color: var(--primary);
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
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin-top: 4px;
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

.gmd-section-toggle {
  background: transparent; border: none; cursor: pointer;
  color: var(--ink-muted); width: 32px; height: 32px;
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
}
.gmd-section-toggle:hover { background: rgba(0,84,166,0.06); color: var(--primary); }

.gmd-section-body {
  border-top: 1px dashed var(--line);
}
.gmd-table {
  width: 100%; border-collapse: collapse;
  font-size: 14px;
}
.gmd-table tr { border-bottom: 1px solid var(--line); }
.gmd-table tr:last-child { border-bottom: none; }
.gmd-table tr.is-empty-row { background: rgba(248,250,252,0.5); }
.gmd-table tr:hover { background: rgba(0,84,166,0.03); }

.gmd-cell-label {
  padding: 12px 22px; font-weight: 600; color: var(--ink);
  width: 50%;
}
.gmd-cell-unit {
  padding: 12px 16px; font-size: 12px; color: var(--ink-muted);
  font-weight: 600; letter-spacing: 0.02em;
  width: 18%; white-space: nowrap;
}
.gmd-cell-val {
  padding: 12px 22px; text-align: right;
  font-variant-numeric: tabular-nums;
  width: 32%;
}
.gmd-val { font-weight: 800; font-size: 15px; color: var(--ink); }
.gmd-no-data {
  font-size: 11px; font-weight: 700;
  background: rgba(15,23,42,0.05); color: var(--ink-muted);
  padding: 4px 10px; border-radius: 999px; letter-spacing: 0.04em;
}

.gmd-foot {
  max-width: 1200px; margin: 40px auto 0; padding: 20px 56px;
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
  .gmd-head, .gmd-main, .gmd-foot { padding-left: 24px; padding-right: 24px; }
  .gmd-cell-label, .gmd-cell-val { padding-left: 14px; padding-right: 14px; }
}
</style>
