<script setup>
/**
 * Golden Mart admin — fill / edit entity values.
 *
 * Layout:
 *   1. Entity picker (level dropdown + entity list)
 *   2. Year tab strip (2021–2026, switches the matrix below)
 *   3. 6 thematic tabs (mirrors the public detail view)
 *   4. Section cards inside each tab — one input per field
 *   5. Save button — PUTs the active year's values
 *
 * Auth: backend gates writes to admin role; frontend gates this whole
 * route via router meta (admin-only).
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import { schemaForLevel } from '@/data/goldenMart/schemaPicker.js'
import { isEnumField, isFreeTextField, enumOptions, enumI18nKey } from '@/data/goldenMart/enums.js'
import {
  gmListEntities, gmGetEntityData, gmWriteYear, gmCoverage,
} from '@/services/eduApi.js'

const { t, locale } = useI18n()

const YEARS = [2021, 2022, 2023, 2024, 2025, 2026]

// ── State ─────────────────────────────────────────────
const level = ref('city')
const schema = computed(() => schemaForLevel(level.value))
const SECTIONS = computed(() => schema.value.sections)
const TABS = computed(() => schema.value.tabs)
const TAB_SECTIONS = computed(() => schema.value.tabSections)
const entities = ref([])
const selectedKey = ref(null)
const yearsData = ref({})         // { 2021: {s1_1: ..., ...}, 2022: {...}, ... }
const activeYear = ref(2025)
const activeTab = ref('basic')
const dirty = ref(new Set())      // field keys edited but not saved
const saving = ref(false)
const saveOk = ref(null)
const saveError = ref(null)
const cov = ref({ overall: { filled: 0, total: 0, pct: 0 }, per_year: [] })

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
    for (const row of data.rows) {
      map[row.year] = row
    }
    // Ensure all 6 years exist (use empty object if no row yet)
    for (const y of YEARS) {
      if (!map[y]) map[y] = { entity_key: key, year: y }
    }
    yearsData.value = map
    dirty.value = new Set()
    saveOk.value = null
    saveError.value = null
    cov.value = await gmCoverage(level.value, key)
  } catch (e) {
    console.error('Failed to load entity data', e)
  }
}

// ── Active section list (depends on tab + level) ──────
const activeSections = computed(() => TAB_SECTIONS.value(activeTab.value))

// ── Edit helpers ──────────────────────────────────────
function valueOf(fieldKey) {
  const row = yearsData.value[activeYear.value]
  if (!row) return ''
  const v = row[fieldKey]
  return v == null ? '' : v
}

function setValue(fieldKey, raw, unit) {
  const row = yearsData.value[activeYear.value]
  if (!row) return
  const isText = ['текст', 'да/нет', 'высокий/средний/низкий', 'выс/ср/низ'].includes(unit)
  const v = raw === '' ? null : (isText ? raw : Number(raw))
  row[fieldKey] = Number.isNaN(v) ? raw : v
  dirty.value.add(fieldKey)
}

// ── Save ──────────────────────────────────────────────
async function save() {
  if (saving.value) return
  saving.value = true
  saveOk.value = null
  saveError.value = null
  try {
    const row = yearsData.value[activeYear.value] || {}
    // Send only fields that exist in current tab's sections (or all dirty)
    const values = {}
    for (const key of dirty.value) {
      values[key] = row[key] ?? null
    }
    if (Object.keys(values).length === 0) {
      saveError.value = t('gmAdmin.errNoDirty')
      saving.value = false
      return
    }
    await gmWriteYear(level.value, selectedKey.value, activeYear.value, values)
    saveOk.value = t('gmAdmin.savedOk', { n: Object.keys(values).length })
    dirty.value = new Set()
    cov.value = await gmCoverage(level.value, selectedKey.value)
  } catch (e) {
    saveError.value = e.message || t('gmAdmin.saveError')
  } finally {
    saving.value = false
  }
}

// ── Coverage helpers (recompute on level change via SECTIONS reactive) ──
function tabCoverage(tab) {
  const sections = TAB_SECTIONS.value(tab.id)
  const row = yearsData.value[activeYear.value] || {}
  let filled = 0, total = 0
  for (const s of sections) {
    for (const a of s.attrs) {
      total++
      if (row[a.key] != null && row[a.key] !== '') filled++
    }
  }
  return { filled, total }
}

const yearCoverage = computed(() => {
  const row = yearsData.value[activeYear.value] || {}
  const total = SECTIONS.value.reduce((n, s) => n + s.attrs.length, 0)
  let filled = 0
  for (const s of SECTIONS.value) {
    for (const a of s.attrs) {
      if (row[a.key] != null && row[a.key] !== '') filled++
    }
  }
  return { filled, total, pct: total ? Math.round(100 * filled / total) : 0 }
})
</script>

<template>
  <div class="gma">
    <header class="gma-head">
      <div class="gma-head-top">
        <div>
          <div class="gma-eyebrow">{{ t('gmAdmin.eyebrow') }} · ПО ГОДАМ</div>
          <h1 class="gma-title">{{ t('gmAdmin.title') }}</h1>
          <p class="gma-sub">{{ t('gmAdmin.sub') }}</p>
        </div>
        <button class="gma-toggle-v" @click="$router.push('/admin/golden-mart')">
          <AppIcon name="swap_horiz" /> Версия 2 (таблица)
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
        {{ t('gmAdmin.coveragePill', { filled: cov.overall.filled, total: cov.overall.total, pct: cov.overall.pct }) }}
      </div>
    </section>

    <template v-if="selectedKey">
      <!-- ── Year tab strip ── -->
      <nav class="gma-years">
        <button
          v-for="y in YEARS"
          :key="y"
          class="gma-year"
          :class="{ active: activeYear === y }"
          @click="activeYear = y"
        >
          <span class="gma-year-num">{{ y }}</span>
        </button>
        <span class="gma-year-cov">
          {{ t('gmAdmin.yearCoverage', { filled: yearCoverage.filled, total: yearCoverage.total, pct: yearCoverage.pct, year: activeYear }) }}
        </span>
      </nav>

      <!-- ── Tab strip (6 thematic) ── -->
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

      <!-- ── Section forms ── -->
      <main class="gma-main">
        <article
          v-for="section in activeSections"
          :key="section.n"
          class="gma-section"
        >
          <header class="gma-section-head">
            <div class="gma-section-num">{{ String(section.n).padStart(2, '0') }}</div>
            <AppIcon :name="section.icon" class="gma-section-icon" />
            <h2 class="gma-section-title">{{ locale === 'uz' ? (section.titleUz || section.title) : section.title }}</h2>
          </header>
          <div class="gma-fields">
            <div
              v-for="attr in section.attrs"
              :key="attr.key"
              class="gma-row"
              :class="{ 'is-dirty': dirty.has(attr.key) }"
            >
              <label class="gma-row-label">
                <span class="gma-row-label-text">{{ locale === 'uz' ? (attr.labelUz || attr.label) : attr.label }}</span>
                <span class="gma-row-unit">{{ attr.unit }}</span>
              </label>
              <!-- Enum: dropdown -->
              <select
                v-if="isEnumField(attr.key)"
                class="gma-input gma-select-enum"
                :value="valueOf(attr.key)"
                @change="setValue(attr.key, $event.target.value, attr.unit)"
              >
                <option value="">{{ t('gmEnum.placeholder') }}</option>
                <option v-for="code in enumOptions(attr.key)" :key="code" :value="code">
                  {{ t(enumI18nKey(attr.key, code)) }}
                </option>
              </select>
              <!-- Free-form text: paired RU + UZ inputs -->
              <div v-else-if="isFreeTextField(attr)" class="gma-input gma-bilingual">
                <input
                  class="gma-bilingual-input"
                  type="text"
                  placeholder="RU"
                  :value="valueOf(attr.key)"
                  @input="setValue(attr.key, $event.target.value, attr.unit)"
                />
                <input
                  class="gma-bilingual-input"
                  type="text"
                  placeholder="UZ"
                  :value="valueOf(`${attr.key}_uz`)"
                  @input="setValue(`${attr.key}_uz`, $event.target.value, attr.unit)"
                />
              </div>
              <!-- Numeric / single-text: single input -->
              <input
                v-else
                class="gma-input"
                :value="valueOf(attr.key)"
                :type="attr.unit === 'да/нет' ? 'text' : 'number'"
                :step="attr.unit === '%' || attr.unit === '‰' ? '0.01' : 'any'"
                :placeholder="`s${section.n}_${attr.key.split('_')[1]}`"
                @input="setValue(attr.key, $event.target.value, attr.unit)"
              />
            </div>
          </div>
        </article>
      </main>

      <!-- ── Save bar ── -->
      <footer class="gma-foot">
        <div class="gma-status">
          <span v-if="saving" class="gma-saving">{{ t('gmAdmin.saving') }}</span>
          <span v-else-if="saveOk" class="gma-ok">✓ {{ saveOk }}</span>
          <span v-else-if="saveError" class="gma-err">✕ {{ saveError }}</span>
          <span v-else-if="dirty.size">{{ t('gmAdmin.dirtyCount', { n: dirty.size }) }}</span>
          <span v-else class="gma-clean">{{ t('gmAdmin.noChanges') }}</span>
        </div>
        <button
          class="gma-save"
          :disabled="!dirty.size || saving"
          @click="save"
        >
          <AppIcon name="save" /> {{ t('gmAdmin.saveButton', { year: activeYear }) }}
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
  padding: 28px 56px 100px;
  font-family: 'Manrope', system-ui, sans-serif;
  color: var(--ink);
}

.gma-head { max-width: 1320px; margin: 0 auto 28px; }
.gma-head-top {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 20px; flex-wrap: wrap;
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

/* Picker */
.gma-picker {
  max-width: 1320px; margin: 0 auto 20px;
  background: var(--surface); border: 1px solid var(--line);
  padding: 18px 22px; border-radius: 14px;
  display: flex; gap: 16px; align-items: end; flex-wrap: wrap;
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

/* Year tabs */
.gma-years {
  max-width: 1320px; margin: 0 auto 16px;
  display: flex; gap: 4px; padding: 6px 16px 6px 6px;
  background: #ECEEF0; border-radius: 12px; align-items: center;
  overflow-x: auto;
}
.gma-year {
  padding: 8px 16px; border-radius: 8px; border: none; background: transparent;
  cursor: pointer; font-family: inherit; font-weight: 800;
  color: #424751; transition: all 0.15s;
}
.gma-year:hover { color: var(--primary); }
.gma-year.active { background: #fff; color: var(--primary); box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.gma-year-num { font-variant-numeric: tabular-nums; }
.gma-year-cov {
  margin-left: auto; font-size: 12px; color: var(--ink-muted);
  font-weight: 600;
}

/* Tab strip */
.gma-tabs {
  max-width: 1320px; margin: 0 auto 20px;
  display: flex; gap: 4px; padding: 6px;
  background: #ECEEF0; border-radius: 14px;
  overflow-x: auto;
}
.gma-tab {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 16px; border-radius: 10px; border: none;
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

/* Section forms */
.gma-main {
  max-width: 1320px; margin: 0 auto 80px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 14px;
}
.gma-section {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; overflow: hidden;
}
.gma-section-head {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 20px; border-bottom: 1px dashed var(--line);
}
.gma-section-num {
  font-family: ui-monospace, monospace; font-size: 11px; font-weight: 800;
  color: var(--primary); background: var(--primary-soft);
  padding: 3px 7px; border-radius: 5px;
}
.gma-section-icon { color: var(--primary); }
.gma-section-title {
  font-size: 15px; font-weight: 800; margin: 0;
}

.gma-fields { padding: 4px 0; }
.gma-row {
  display: grid; grid-template-columns: 1fr 160px;
  gap: 12px; align-items: center;
  padding: 8px 20px; border-bottom: 1px solid var(--line);
}
.gma-row:last-child { border-bottom: none; }
.gma-row.is-dirty { background: rgba(245,158,11,0.06); }

.gma-row-label { display: flex; flex-direction: column; gap: 2px; }
.gma-row-label-text { font-size: 13px; font-weight: 600; color: var(--ink); }
.gma-row-unit { font-size: 11px; color: var(--ink-muted); font-weight: 500; }

.gma-input {
  background: #fff; border: 1px solid var(--line);
  padding: 7px 10px; border-radius: 6px; font-family: ui-monospace, monospace;
  font-size: 13px; color: var(--ink); font-variant-numeric: tabular-nums;
  text-align: right;
}
.gma-input:focus {
  border-color: var(--primary); outline: 2px solid rgba(0,84,166,0.15);
}
.gma-row.is-dirty .gma-input { border-color: var(--gold); }

/* Bilingual paired input for free-form text */
.gma-bilingual {
  display: flex; gap: 6px;
  padding: 0; border: none; background: transparent;
}
.gma-bilingual-input {
  flex: 1;
  background: #fff; border: 1px solid var(--line);
  padding: 7px 10px; border-radius: 6px;
  font-family: inherit; font-size: 13px;
  color: var(--ink);
}
.gma-bilingual-input:focus {
  border-color: var(--primary); outline: 2px solid rgba(0,84,166,0.15);
}
.gma-bilingual-input::placeholder {
  color: var(--ink-muted); font-weight: 700; font-size: 11px; opacity: 0.6;
}

/* Save bar */
.gma-foot {
  position: fixed; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.96); backdrop-filter: blur(8px);
  border-top: 1px solid var(--line);
  padding: 14px 56px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px;
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
.gma-empty svg, .gma-empty .material-icons { font-size: 48px; opacity: 0.5; }
</style>
