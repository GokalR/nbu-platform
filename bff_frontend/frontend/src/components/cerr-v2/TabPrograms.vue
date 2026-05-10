<script setup>
/* "Программы" tab — government subsidy programs + citizen appeals.
 * Source: mahalla.overview.detail.subsidies.programs[]  +  mahalla.overview.appeals
 *
 * Data shape:
 *   programs[].applications        — count of submitted applications (null = no data)
 *   programs[].required_amount_mln — total amount requested in млн сум (null = unspecified)
 *   programs[].has_amount_source   — whether the amount field is officially populated
 *   appeals.{crime,divorce,aid,employment,gas,registry} — counts per category for the period
 *   appeals.year + appeals.period — reporting window (e.g. "2026 йил 1-чорак")
 */
import { computed } from 'vue'
import CerrIcon from './CerrIcon.vue'

const props = defineProps({
  m: { type: Object, required: true },
})

const programs = computed(() => props.m?.detail?.subsidies?.programs || [])
const appeals = computed(() => props.m?.appeals || null)

const APPEAL_CATS = [
  { k: 'crime',      lbl: 'Преступность', sub: 'правонарушения', ico: 'shield', color: '#d83838' },
  { k: 'divorce',    lbl: 'Разводы',      sub: 'семейные',        ico: 'users',  color: '#a855f7' },
  { k: 'aid',        lbl: 'Соц. помощь',  sub: 'материальная',    ico: 'help',   color: '#f59e0b' },
  { k: 'employment', lbl: 'Занятость',    sub: 'трудоустройство', ico: 'tools',  color: '#0ea5e9' },
  { k: 'gas',        lbl: 'Газ / комму.', sub: 'инфратузилма',    ico: 'bolt',   color: '#facc15' },
  { k: 'registry',   lbl: 'Реестр',       sub: 'документы',       ico: 'file',   color: '#64748b' },
]

const active = computed(() => programs.value.filter((s) => s.applications != null && s.applications > 0))
const inactive = computed(() => programs.value.filter((s) => !(s.applications != null && s.applications > 0)))
const totalApps = computed(() => active.value.reduce((s, x) => s + (x.applications || 0), 0))
const totalAmount = computed(() =>
  active.value.filter((s) => s.required_amount_mln != null).reduce((s, x) => s + x.required_amount_mln, 0)
)

const totalAppeals = computed(() => {
  if (!appeals.value) return 0
  return APPEAL_CATS.reduce((s, c) => s + (appeals.value[c.k] || 0), 0)
})
const maxAppeal = computed(() => {
  if (!appeals.value) return 1
  return Math.max(1, ...APPEAL_CATS.map((c) => appeals.value[c.k] || 0))
})

function fmt(v) {
  if (v == null) return '—'
  return typeof v === 'number' && v >= 1000 ? Math.round(v).toLocaleString('ru-RU').replace(/,/g, ' ') : String(v)
}
function fmtAmount(v) {
  if (v == null) return null
  return v.toFixed(1).replace('.', ',')
}
</script>

<template>
  <!-- Subsidies -->
  <section class="card mh-pgr-card">
    <header class="mh-pgr-head">
      <div class="t-l">
        <div class="ico-tile" :style="{ background: 'rgba(0, 84, 166, .1)', color: 'var(--brand-navy-bright)' }">
          <CerrIcon name="docs" :size="14" />
        </div>
        <div>
          <div class="t">Государственные программы поддержки</div>
          <div class="s">Какие субсидии и дотации работают в маҳалле</div>
        </div>
      </div>
      <div class="t-r">
        <div class="kbig">
          <span class="num tabular">{{ active.length }}</span>
          <span class="lbl">из {{ programs.length }} активных</span>
        </div>
      </div>
    </header>

    <div v-if="active.length || totalAmount" class="mh-pgr-summary">
      <div class="mh-pgr-stat">
        <div class="lbl">Заявок принято</div>
        <div class="v"><span class="num tabular">{{ totalApps }}</span><span class="u">заявок</span></div>
      </div>
      <div class="mh-pgr-stat">
        <div class="lbl">Запрошено бюджета</div>
        <div class="v">
          <span class="num tabular">{{ totalAmount > 0 ? fmtAmount(totalAmount) : '—' }}</span>
          <span class="u">млн сум</span>
        </div>
      </div>
      <div class="mh-pgr-stat">
        <div class="lbl">Не использовано</div>
        <div class="v"><span class="num tabular">{{ inactive.length }}</span><span class="u">программ</span></div>
      </div>
    </div>

    <!-- Active programs list -->
    <div v-if="active.length" class="mh-pgr-section">
      <div class="mh-pgr-section-h">
        <CerrIcon name="check" :size="11" />
        <span>Активные программы</span>
      </div>
      <div class="mh-pgr-list">
        <div v-for="(s, i) in active" :key="`a-${i}`" class="mh-pgr-row active">
          <div class="row-name">
            <div class="bullet" />
            <span class="lbl">{{ s.label }}</span>
          </div>
          <div class="row-meta">
            <span class="apps tabular"><b>{{ s.applications }}</b> заявок</span>
            <span v-if="s.required_amount_mln != null" class="amt tabular">
              <b>{{ fmtAmount(s.required_amount_mln) }}</b> млн сум
            </span>
            <span v-else class="muted">сумма уточняется</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Inactive programs (collapsed-style, muted) -->
    <div v-if="inactive.length" class="mh-pgr-section">
      <div class="mh-pgr-section-h muted">
        <CerrIcon name="info" :size="11" />
        <span>Не используются в маҳалле</span>
        <span class="ct">{{ inactive.length }}</span>
      </div>
      <div class="mh-pgr-tags">
        <span v-for="(s, i) in inactive" :key="`i-${i}`" class="mh-pgr-tag">{{ s.label }}</span>
      </div>
    </div>
  </section>

  <!-- Citizen appeals -->
  <section v-if="appeals" class="card mh-pgr-card">
    <header class="mh-pgr-head">
      <div class="t-l">
        <div class="ico-tile" :style="{ background: 'rgba(245, 158, 11, .12)', color: '#d97706' }">
          <CerrIcon name="users" :size="14" />
        </div>
        <div>
          <div class="t">Обращения граждан</div>
          <div class="s">Зарегистрированные жалобы и запросы за период</div>
        </div>
      </div>
      <div class="t-r">
        <div class="kbig">
          <span class="num tabular">{{ totalAppeals }}</span>
          <span class="lbl">всего обращений</span>
        </div>
        <div v-if="appeals.period" class="period">{{ appeals.period }}</div>
      </div>
    </header>

    <!-- Stacked horizontal bar — visual share by category -->
    <div v-if="totalAppeals > 0" class="mh-app-bar">
      <i
        v-for="c in APPEAL_CATS"
        :key="c.k"
        v-show="(appeals[c.k] || 0) > 0"
        :style="{
          width: `${((appeals[c.k] || 0) / totalAppeals) * 100}%`,
          background: c.color,
        }"
        :title="`${c.lbl}: ${appeals[c.k]}`"
      />
    </div>

    <!-- Per-category grid -->
    <div class="mh-app-grid">
      <div
        v-for="c in APPEAL_CATS"
        :key="c.k"
        :class="['mh-app-cell', appeals[c.k] ? 'has' : 'muted']"
      >
        <div class="ico" :style="{ background: appeals[c.k] ? `${c.color}1f` : 'var(--n-50)', color: appeals[c.k] ? c.color : 'var(--text-faint)' }">
          <CerrIcon :name="c.ico" :size="14" />
        </div>
        <div class="body">
          <div class="lbl">{{ c.lbl }}</div>
          <div class="sub">{{ c.sub }}</div>
        </div>
        <div class="num tabular">{{ appeals[c.k] ?? 0 }}</div>
      </div>
    </div>

    <div v-if="totalAppeals === 0" class="mh-app-empty">
      <CerrIcon name="check" :size="14" />
      <span>За {{ appeals.period || 'период' }} обращений не зарегистрировано.</span>
    </div>
  </section>
</template>

<style>
/* ============== Programs tab ============== */
.cerr-v2-scope .mh-pgr-card {
  padding: 0;
  border-radius: 14px;
  overflow: hidden;
}
.cerr-v2-scope .mh-pgr-head {
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--border);
}
.cerr-v2-scope .mh-pgr-head .t-l { display: flex; gap: 12px; align-items: flex-start; }
.cerr-v2-scope .mh-pgr-head .t { font-size: 15px; font-weight: 800; color: var(--text); line-height: 1.2; }
.cerr-v2-scope .mh-pgr-head .s { font-size: 12px; color: var(--text-soft); margin-top: 2px; font-weight: 500; }
.cerr-v2-scope .mh-pgr-head .t-r { text-align: right; flex-shrink: 0; }
.cerr-v2-scope .mh-pgr-head .kbig {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}
.cerr-v2-scope .mh-pgr-head .kbig .num {
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -.025em;
  color: var(--text);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.cerr-v2-scope .mh-pgr-head .kbig .lbl {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--text-soft);
}
.cerr-v2-scope .mh-pgr-head .period {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-faint);
  margin-top: 4px;
}

/* Summary stats */
.cerr-v2-scope .mh-pgr-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--border);
  border-bottom: 1px solid var(--border);
}
.cerr-v2-scope .mh-pgr-stat {
  background: var(--surface);
  padding: 14px 18px;
}
.cerr-v2-scope .mh-pgr-stat .lbl {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--text-soft);
}
.cerr-v2-scope .mh-pgr-stat .v {
  display: flex; align-items: baseline; gap: 6px; margin-top: 4px;
}
.cerr-v2-scope .mh-pgr-stat .v .num {
  font-size: 22px; font-weight: 900; letter-spacing: -.022em;
  color: var(--text); font-variant-numeric: tabular-nums; line-height: 1;
}
.cerr-v2-scope .mh-pgr-stat .v .u {
  font-size: 11.5px; font-weight: 600; color: var(--text-soft);
}

/* Sections inside the card */
.cerr-v2-scope .mh-pgr-section { padding: 14px 20px 16px; }
.cerr-v2-scope .mh-pgr-section + .mh-pgr-section { border-top: 1px solid var(--border); }
.cerr-v2-scope .mh-pgr-section-h {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--pos-700);
  margin-bottom: 10px;
}
.cerr-v2-scope .mh-pgr-section-h.muted { color: var(--text-soft); }
.cerr-v2-scope .mh-pgr-section-h .ct {
  font-size: 10.5px; font-weight: 800; padding: 1px 7px;
  border-radius: 6px; background: var(--n-100); color: var(--text-muted);
  letter-spacing: 0.02em;
}

.cerr-v2-scope .mh-pgr-list {
  display: flex; flex-direction: column;
}
.cerr-v2-scope .mh-pgr-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  transition: background .14s, border-color .14s;
}
.cerr-v2-scope .mh-pgr-row + .mh-pgr-row { margin-top: 6px; }
.cerr-v2-scope .mh-pgr-row.active {
  background: linear-gradient(90deg, rgba(20, 163, 74, .04), transparent 60%);
  border-color: rgba(20, 163, 74, .24);
}
.cerr-v2-scope .mh-pgr-row .row-name {
  display: flex; align-items: center; gap: 10px; min-width: 0;
}
.cerr-v2-scope .mh-pgr-row .bullet {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--pos-500);
  flex-shrink: 0;
}
.cerr-v2-scope .mh-pgr-row .lbl {
  font-size: 13px; font-weight: 700; color: var(--text); line-height: 1.35;
}
.cerr-v2-scope .mh-pgr-row .row-meta {
  display: flex; align-items: baseline; gap: 14px;
  font-size: 12px; font-weight: 600;
  color: var(--text-soft);
  flex-shrink: 0;
}
.cerr-v2-scope .mh-pgr-row .apps b, .cerr-v2-scope .mh-pgr-row .amt b {
  font-weight: 900; color: var(--text);
}
.cerr-v2-scope .mh-pgr-row .muted { font-style: italic; color: var(--text-faint); }

/* Inactive programs as compact tags */
.cerr-v2-scope .mh-pgr-tags {
  display: flex; flex-wrap: wrap; gap: 6px;
}
.cerr-v2-scope .mh-pgr-tag {
  font-size: 11.5px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--n-50);
  border: 1px solid var(--border);
  color: var(--text-soft);
}

/* Stacked appeals bar */
.cerr-v2-scope .mh-app-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin: 14px 20px 0;
  background: var(--n-100);
}
.cerr-v2-scope .mh-app-bar i {
  display: block;
  height: 100%;
  transition: width .25s ease;
}

/* Appeals grid */
.cerr-v2-scope .mh-app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  padding: 14px 20px 16px;
}
.cerr-v2-scope .mh-app-cell {
  display: grid;
  grid-template-columns: 32px 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  transition: background .14s;
}
.cerr-v2-scope .mh-app-cell.muted .body .lbl { color: var(--text-soft); }
.cerr-v2-scope .mh-app-cell.muted .body .sub { color: var(--text-faint); }
.cerr-v2-scope .mh-app-cell .ico {
  width: 32px; height: 32px;
  display: grid; place-items: center;
  border-radius: 8px;
  flex-shrink: 0;
}
.cerr-v2-scope .mh-app-cell .body { min-width: 0; }
.cerr-v2-scope .mh-app-cell .lbl {
  font-size: 12.5px; font-weight: 700; color: var(--text); line-height: 1.2;
}
.cerr-v2-scope .mh-app-cell .sub {
  font-size: 10.5px; font-weight: 600; color: var(--text-faint);
  letter-spacing: 0.04em; text-transform: uppercase;
  margin-top: 2px;
}
.cerr-v2-scope .mh-app-cell .num {
  font-size: 22px; font-weight: 900; letter-spacing: -.02em;
  font-variant-numeric: tabular-nums; color: var(--text);
}
.cerr-v2-scope .mh-app-cell.muted .num { color: var(--text-faint); }

.cerr-v2-scope .mh-app-empty {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 20px 16px;
  color: var(--pos-700);
  font-size: 13px;
  font-weight: 600;
}

@media (max-width: 720px) {
  .cerr-v2-scope .mh-pgr-summary { grid-template-columns: 1fr; }
  .cerr-v2-scope .mh-pgr-row { flex-direction: column; align-items: flex-start; gap: 8px; }
  .cerr-v2-scope .mh-pgr-row .row-meta { padding-left: 18px; }
}
</style>
