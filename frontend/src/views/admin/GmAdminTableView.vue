<script setup>
/**
 * Golden Mart admin V2 — Excel-like table view.
 *
 * Layout differs from V1:
 *   V1 (GmAdminView.vue):  Year tab strip → form for one year
 *   V2 (this file):        Table with years as columns, fields as rows
 *
 * Same level + entity picker, same 6 thematic tabs (Базовая / Экономика / ...).
 * Inside each tab, sections render as wide tables: [field, unit, 2021..2026].
 * All cells editable. Save collects dirty-by-year and fires one PUT per
 * dirty year.
 *
 * Same backend, same schema — just a different shell. Switch between V1
 * and V2 via the toggle in the toolbar.
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import { schemaForLevel } from '@/data/goldenMart/schemaPicker.js'
import { isEnumField, enumOptions, enumI18nKey } from '@/data/goldenMart/enums.js'
import {
  gmListEntities, gmGetEntityData, gmWriteYear, gmCoverage,
} from '@/services/eduApi.js'

const { t, locale } = useI18n()
const router = useRouter()

const YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
const TEXT_UNITS = ['текст', 'да/нет', 'высокий/средний/низкий', 'выс/ср/низ']

// ── State ─────────────────────────────────────────────
const level = ref('city')
const schema = computed(() => schemaForLevel(level.value))
const SECTIONS = computed(() => schema.value.sections)
const TABS = computed(() => schema.value.tabs)
const TAB_SECTIONS = computed(() => schema.value.tabSections)
const entities = ref([])
const selectedKey = ref(null)
const yearsData = ref({})         // { 2021: { s1_1: ..., ... }, ... }
const activeTab = ref('basic')
// dirty per year — { 2021: Set<fieldKey>, ... }
const dirtyByYear = ref(Object.fromEntries(YEARS.map((y) => [y, new Set()])))
const saving = ref(false)
const saveStatus = ref(null)      // null | 'ok' | 'err'
const saveMsg = ref('')
const cov = ref({ overall: { filled: 0, total: 0, pct: 0 } })

const activeSections = computed(() => TAB_SECTIONS.value(activeTab.value))

const totalDirty = computed(() =>
  Object.values(dirtyByYear.value).reduce((n, s) => n + s.size, 0),
)

// ── Load ──────────────────────────────────────────────
onMounted(async () => {
  await reloadEntities()
})

async function reloadEntities() {
  try {
    entities.value = await gmListEntities(level.value)
    if (entities.value.length && !selectedKey.value) {
      selectedKey.value = entities.value[0].key
    }
  } catch (e) {
    console.error('Failed to load entities', e)
  }
}

watch(level, async () => {
  selectedKey.value = null
  await reloadEntities()
})

watch(selectedKey, async (k) => {
  if (!k) return
  await loadEntityData(k)
})

async function loadEntityData(key) {
  try {
    const data = await gmGetEntityData(level.value, key)
    const map = {}
    for (const row of data.rows) map[row.year] = row
    for (const y of YEARS) if (!map[y]) map[y] = { entity_key: key, year: y }
    yearsData.value = map
    dirtyByYear.value = Object.fromEntries(YEARS.map((y) => [y, new Set()]))
    saveStatus.value = null
    cov.value = await gmCoverage(level.value, key)
  } catch (e) {
    console.error('Failed to load entity data', e)
  }
}

// ── Edit helpers ──────────────────────────────────────
function valueOf(year, fieldKey) {
  const row = yearsData.value[year]
  if (!row) return ''
  const v = row[fieldKey]
  return v == null ? '' : v
}

function setValue(year, fieldKey, raw, unit) {
  const row = yearsData.value[year]
  if (!row) return
  const isText = TEXT_UNITS.includes(unit)
  const v = raw === '' ? null : (isText ? raw : Number(raw))
  row[fieldKey] = Number.isNaN(v) ? raw : v
  dirtyByYear.value[year].add(fieldKey)
}

// ── Save — one PUT per dirty year ─────────────────────
async function saveAll() {
  if (saving.value || totalDirty.value === 0) return
  saving.value = true
  saveStatus.value = null
  saveMsg.value = ''
  let ok = 0, fail = 0, totalFields = 0
  try {
    for (const year of YEARS) {
      const dirty = dirtyByYear.value[year]
      if (dirty.size === 0) continue
      const row = yearsData.value[year] || {}
      const values = {}
      for (const k of dirty) values[k] = row[k] ?? null
      try {
        await gmWriteYear(level.value, selectedKey.value, year, values)
        ok++; totalFields += Object.keys(values).length
      } catch (e) {
        fail++
        console.error(`save year ${year} failed:`, e)
      }
    }
    if (fail === 0) {
      saveStatus.value = 'ok'
      saveMsg.value = `Сохранено: ${totalFields} полей в ${ok} ${ok === 1 ? 'году' : 'годах'}`
      dirtyByYear.value = Object.fromEntries(YEARS.map((y) => [y, new Set()]))
    } else {
      saveStatus.value = 'err'
      saveMsg.value = `Сохранено ${ok} лет, ошибок ${fail}`
    }
    cov.value = await gmCoverage(level.value, selectedKey.value)
  } finally {
    saving.value = false
  }
}

// ── Coverage helpers ──────────────────────────────────
function tabCoverage(tab) {
  const sections = TAB_SECTIONS.value(tab.id)
  let filled = 0, total = 0
  for (const y of YEARS) {
    const row = yearsData.value[y] || {}
    for (const s of sections) {
      for (const a of s.attrs) {
        total++
        if (row[a.key] != null && row[a.key] !== '') filled++
      }
    }
  }
  return { filled, total }
}

function isDirty(year, fieldKey) {
  return dirtyByYear.value[year]?.has(fieldKey)
}

function gotoV1() {
  router.push('/admin/golden-mart')
}
</script>

<template>
  <div class="gma">
    <header class="gma-head">
      <div class="gma-head-top">
        <div>
          <div class="gma-eyebrow">{{ t('gmAdmin.eyebrow') }} · ТАБЛИЦА</div>
          <h1 class="gma-title">{{ t('gmAdmin.title') }}</h1>
          <p class="gma-sub">
            Excel-вид: годы по колонкам, поля по строкам.
            Можно править ячейки сразу за все годы — одно нажатие «Сохранить» отправит изменения по нужным годам.
          </p>
        </div>
        <button class="gma-toggle-v" @click="gotoV1">
          <AppIcon name="swap_horiz" /> Версия 1 (по годам)
        </button>
      </div>
    </header>

    <!-- ── Picker ── -->
    <section class="gma-picker">
      <div class="gma-field">
        <label class="gma-label">{{ t('gmAdmin.levelLabel') }}</label>
        <select v-model="level" class="gma-select">
          <option value="country">{{ t('gmAdmin.levelCountry') }}</option>
          <option value="region">{{ t('gmAdmin.levelRegion') }}</option>
          <option value="city">{{ t('gmAdmin.levelCity') }}</option>
        </select>
      </div>
      <div class="gma-field gma-flex">
        <label class="gma-label">{{ t('gmAdmin.entityLabel') }}</label>
        <select v-model="selectedKey" class="gma-select">
          <option v-for="e in entities" :key="e.key" :value="e.key">
            {{ locale === 'uz' ? e.name_uz : e.name_ru }} ({{ e.key }})
          </option>
        </select>
      </div>
      <div v-if="cov.overall.total" class="gma-cov-pill">
        {{ t('gmAdmin.coveragePill', {
          filled: cov.overall.filled,
          total: cov.overall.total,
          pct: cov.overall.pct,
        }) }}
      </div>
    </section>

    <template v-if="selectedKey">
      <!-- ── Tab strip ── -->
      <nav class="gma-tabs">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          class="gma-tab"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="gma-tab-num">{{ tab.num }}</span>
          <AppIcon :name="tab.icon" />
          <span>{{ tab.label }}</span>
          <span class="gma-tab-cov">
            {{ tabCoverage(tab).filled }}/{{ tabCoverage(tab).total }}
          </span>
        </button>
      </nav>

      <!-- ── Section tables — years as columns ── -->
      <main class="gma-main">
        <article
          v-for="section in activeSections"
          :key="section.n"
          class="gma-section"
        >
          <header class="gma-section-head">
            <div class="gma-section-num">{{ String(section.n).padStart(2, '0') }}</div>
            <AppIcon :name="section.icon" class="gma-section-icon" />
            <h2 class="gma-section-title">
              {{ locale === 'uz' ? (section.titleUz || section.title) : section.title }}
            </h2>
          </header>
          <div class="gma-table-wrap">
            <table class="gma-table">
              <thead>
                <tr>
                  <th class="gma-th-label">Показатель</th>
                  <th class="gma-th-unit">Ед.</th>
                  <th v-for="y in YEARS" :key="y" class="gma-th-year">{{ y }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attr in section.attrs" :key="attr.key">
                  <td class="gma-td-label">
                    {{ locale === 'uz' ? (attr.labelUz || attr.label) : attr.label }}
                  </td>
                  <td class="gma-td-unit">{{ attr.unit }}</td>
                  <td
                    v-for="y in YEARS"
                    :key="y"
                    class="gma-td-cell"
                    :class="{ 'is-dirty': isDirty(y, attr.key) }"
                  >
                    <select
                      v-if="isEnumField(attr.key)"
                      class="gma-cell-input gma-cell-select"
                      :value="valueOf(y, attr.key)"
                      @change="setValue(y, attr.key, $event.target.value, attr.unit)"
                    >
                      <option value="">—</option>
                      <option v-for="code in enumOptions(attr.key)" :key="code" :value="code">
                        {{ t(enumI18nKey(attr.key, code)) }}
                      </option>
                    </select>
                    <input
                      v-else
                      class="gma-cell-input"
                      :value="valueOf(y, attr.key)"
                      :type="TEXT_UNITS.includes(attr.unit) ? 'text' : 'number'"
                      :step="attr.unit === '%' || attr.unit === '‰' ? '0.01' : 'any'"
                      @input="setValue(y, attr.key, $event.target.value, attr.unit)"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </main>

      <!-- ── Save bar ── -->
      <footer class="gma-foot">
        <div class="gma-status">
          <span v-if="saving" class="gma-saving">{{ t('gmAdmin.saving') }}</span>
          <span v-else-if="saveStatus === 'ok'" class="gma-ok">✓ {{ saveMsg }}</span>
          <span v-else-if="saveStatus === 'err'" class="gma-err">✕ {{ saveMsg }}</span>
          <span v-else-if="totalDirty">
            {{ t('gmAdmin.dirtyCount', { n: totalDirty }) }} (по {{ Object.values(dirtyByYear).filter((s) => s.size > 0).length }} годам)
          </span>
          <span v-else class="gma-clean">{{ t('gmAdmin.noChanges') }}</span>
        </div>
        <button
          class="gma-save"
          :disabled="!totalDirty || saving"
          @click="saveAll"
        >
          <AppIcon name="save" /> Сохранить все изменения
        </button>
      </footer>
    </template>

    <div v-else class="gma-empty">
      <AppIcon name="inbox" />
      <p>{{ t('gmAdmin.emptyState') }}</p>
    </div>
  </div>
</template>

<style scoped>
.gma {
  --bg: #F4F6FB;
  --surface: #FFFFFF;
  --ink: #0F1B2D;
  --ink-muted: #475569;
  --line: #E2E8F0;
  --primary: #0054A6;
  --primary-soft: rgba(0, 84, 166, 0.08);
  --gold: #F59E0B;
  --green: #10B981;
  --red: #DC2626;

  background: var(--bg);
  min-height: 100vh;
  padding: 28px 36px 100px;
  font-family: 'Manrope', system-ui, sans-serif;
  color: var(--ink);
}

.gma-head { max-width: 1600px; margin: 0 auto 24px; }
.gma-head-top {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 20px; flex-wrap: wrap;
}
.gma-eyebrow {
  font-size: 12px; font-weight: 800; letter-spacing: 0.16em;
  color: var(--primary); text-transform: uppercase;
}
.gma-title {
  font-size: clamp(28px, 3.2vw, 40px); font-weight: 900;
  letter-spacing: -0.025em; margin: 8px 0 12px;
}
.gma-sub {
  font-size: 14px; color: var(--ink-muted); max-width: 720px;
  font-weight: 500; line-height: 1.55; margin: 0;
}
.gma-toggle-v {
  display: inline-flex; align-items: center; gap: 8px;
  background: #fff; border: 1px solid var(--line);
  padding: 8px 14px 8px 10px; border-radius: 999px;
  font-size: 13px; font-weight: 700; font-family: inherit;
  color: var(--primary); cursor: pointer;
  transition: background 0.2s;
}
.gma-toggle-v:hover { background: var(--primary-soft); }

/* Picker */
.gma-picker {
  max-width: 1600px; margin: 0 auto 16px;
  background: var(--surface); border: 1px solid var(--line);
  padding: 16px 20px; border-radius: 12px;
  display: flex; gap: 14px; align-items: end; flex-wrap: wrap;
}
.gma-field { display: flex; flex-direction: column; gap: 4px; min-width: 180px; }
.gma-flex { flex: 1; min-width: 280px; }
.gma-label {
  font-size: 11px; font-weight: 700; color: var(--ink-muted);
  letter-spacing: 0.06em; text-transform: uppercase;
}
.gma-select {
  background: #fff; border: 1px solid var(--line);
  padding: 8px 12px; border-radius: 8px; font-family: inherit;
  font-size: 14px; color: var(--ink); font-weight: 600;
}
.gma-cov-pill {
  margin-left: auto; padding: 8px 14px; border-radius: 999px;
  background: var(--primary-soft); color: var(--primary);
  font-size: 12px; font-weight: 700;
}

/* Tabs */
.gma-tabs {
  max-width: 1600px; margin: 0 auto 16px;
  display: flex; gap: 4px; padding: 6px;
  background: #ECEEF0; border-radius: 12px;
  overflow-x: auto;
}
.gma-tab {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-radius: 8px; border: none;
  background: transparent; cursor: pointer;
  font-family: inherit; font-size: 13px; font-weight: 700;
  color: #424751; white-space: nowrap; flex-shrink: 0;
  transition: all 0.15s;
}
.gma-tab:hover { color: var(--primary); }
.gma-tab.active { background: #fff; color: var(--primary); box-shadow: 0 2px 6px rgba(0,27,61,0.08); }
.gma-tab-num {
  font-family: ui-monospace, monospace; font-size: 11px; opacity: 0.6;
}
.gma-tab-cov {
  font-family: ui-monospace, monospace; font-size: 10px; font-weight: 700;
  background: rgba(15,23,42,0.04); padding: 2px 6px; border-radius: 6px;
}
.gma-tab.active .gma-tab-cov { background: rgba(0,84,166,0.10); color: var(--primary); }

/* Section tables */
.gma-main {
  max-width: 1600px; margin: 0 auto 80px;
  display: flex; flex-direction: column; gap: 14px;
}
.gma-section {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 12px; overflow: hidden;
}
.gma-section-head {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 18px; background: rgba(0,84,166,0.03);
  border-bottom: 1px solid var(--line);
}
.gma-section-num {
  font-family: ui-monospace, monospace; font-size: 11px; font-weight: 800;
  color: var(--primary); background: var(--primary-soft);
  padding: 3px 7px; border-radius: 5px;
}
.gma-section-icon { color: var(--primary); }
.gma-section-title { font-size: 15px; font-weight: 800; margin: 0; }

.gma-table-wrap {
  overflow-x: auto;
}
.gma-table {
  width: 100%; min-width: 900px; border-collapse: collapse;
  font-size: 13px;
}
.gma-table thead {
  background: #F8FAFC;
  border-bottom: 2px solid var(--line);
}
.gma-table th {
  text-align: left; padding: 10px 12px;
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
  color: var(--ink-muted); text-transform: uppercase;
}
.gma-th-label { width: 32%; }
.gma-th-unit  { width: 8%;  white-space: nowrap; }
.gma-th-year {
  width: 10%; text-align: center !important;
  font-family: ui-monospace, monospace;
  color: var(--primary) !important;
}

.gma-table tbody tr { border-bottom: 1px solid var(--line); }
.gma-table tbody tr:last-child { border-bottom: none; }
.gma-table tbody tr:hover { background: rgba(0,84,166,0.02); }

.gma-td-label {
  padding: 8px 12px; font-weight: 600; color: var(--ink);
  font-size: 13px;
}
.gma-td-unit {
  padding: 8px 12px; font-size: 11px; color: var(--ink-muted);
  font-weight: 600; white-space: nowrap;
}
.gma-td-cell {
  padding: 4px 6px;
  border-left: 1px dashed rgba(15,23,42,0.05);
}
.gma-td-cell.is-dirty {
  background: rgba(245,158,11,0.08);
}

.gma-cell-input {
  width: 100%;
  background: transparent; border: 1px solid transparent;
  padding: 6px 8px; border-radius: 5px;
  font-family: ui-monospace, monospace; font-size: 12.5px;
  color: var(--ink); font-variant-numeric: tabular-nums;
  text-align: right;
  transition: all 0.15s;
}
.gma-cell-select { font-family: inherit; text-align: left; cursor: pointer; }
.gma-cell-input:hover {
  border-color: var(--line); background: #fff;
}
.gma-cell-input:focus {
  border-color: var(--primary); background: #fff;
  outline: 2px solid rgba(0,84,166,0.15);
}
.gma-td-cell.is-dirty .gma-cell-input {
  border-color: var(--gold);
  background: #fff;
}

/* Save bar */
.gma-foot {
  position: fixed; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.96); backdrop-filter: blur(8px);
  border-top: 1px solid var(--line);
  padding: 12px 36px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; z-index: 50;
}
.gma-status { font-size: 13px; font-weight: 600; }
.gma-saving { color: var(--ink-muted); }
.gma-ok     { color: var(--green); font-weight: 800; }
.gma-err    { color: var(--red); font-weight: 800; }
.gma-clean  { color: var(--ink-muted); }
.gma-save {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--primary); color: #fff; border: none;
  padding: 10px 22px; border-radius: 10px; cursor: pointer;
  font-family: inherit; font-weight: 800; font-size: 14px;
  transition: all 0.15s;
}
.gma-save:hover:not(:disabled) { background: #003D7C; transform: translateY(-1px); }
.gma-save:disabled { opacity: 0.4; cursor: not-allowed; }

.gma-empty {
  max-width: 480px; margin: 60px auto;
  padding: 40px; text-align: center;
  color: var(--ink-muted); font-size: 14px;
}
</style>
