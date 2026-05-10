<script setup>
/* "Хозяйство" tab — economic specialization, crops, infrastructure.
 * Source: mahalla.overview.detail.{specialization, crops, infra} */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CerrIcon from './CerrIcon.vue'
import { fmt } from '@/data/cerrV2Format.js'

const props = defineProps({
  m: { type: Object, required: true },
})

const detail = computed(() => props.m?.detail || {})
const spec = computed(() => detail.value.specialization || null)
const crops = computed(() => detail.value.crops || null)
const infra = computed(() => detail.value.infra || null)

const SEASON_COLOR = {
  main: '#14a34a',
  repeat: '#0054a6',
  winter_sown: '#f59e0b',
}

const totalCropsHh = computed(() => {
  if (!crops.value) return 0
  return (crops.value.seasons || []).reduce((s, x) => s + (x.household_count || 0), 0)
})
function pctHh(s) { return totalCropsHh.value ? (s.household_count || 0) / totalCropsHh.value * 100 : 0 }

const totalSpecHh = computed(() => {
  if (!spec.value?.items) return 0
  return spec.value.items.reduce((s, x) => s + (x.households || 0), 0)
})
const totalSpecPop = computed(() => {
  if (!spec.value?.items) return 0
  return spec.value.items.reduce((s, x) => s + (x.population || 0), 0)
})

const socialCount = computed(() => {
  if (!infra.value) return 0
  return (infra.value.school || 0) + (infra.value.sport || 0) + (infra.value.kindergarten || 0)
})

/** Asphalt share of total roads (visual progress). */
const asphaltShare = computed(() => {
  if (!infra.value || !infra.value.road_km) return 0
  return Math.min(100, (infra.value.road_asphalt_km / infra.value.road_km) * 100)
})

const { t: tFn } = useI18n()
const SLOT_BADGE = computed(() => ({
  main: tFn('cerrV2.farm.slot.main'),
  add_2: tFn('cerrV2.farm.slot.add_2'),
  add_3: tFn('cerrV2.farm.slot.add_3'),
  add_4: tFn('cerrV2.farm.slot.add_4'),
  add_5: tFn('cerrV2.farm.slot.add_5'),
}))
</script>

<template>
  <!-- Specialization -->
  <section v-if="spec?.items?.length" class="card mh-frm-card">
    <header class="mh-frm-head">
      <div class="t-l">
        <div class="ico-tile" :style="{ background: 'rgba(245, 158, 11, .14)', color: '#d97706' }">
          <CerrIcon name="leaf" :size="14" />
        </div>
        <div>
          <div class="t">{{ $t('cerrV2.farm.specTitle') }}</div>
          <div class="s">{{ $t('cerrV2.farm.specSub') }}</div>
        </div>
      </div>
      <div class="t-r">
        <div class="kbig">
          <span class="num tabular">{{ fmt.num(totalSpecHh) }}</span>
          <span class="lbl">{{ $t('cerrV2.farm.households') }}</span>
        </div>
        <div v-if="totalSpecPop" class="period">{{ $t('cerrV2.farm.population', { n: fmt.num(totalSpecPop) }) }}</div>
      </div>
    </header>

    <!-- Stacked share bar — what fraction of households does each specialization cover -->
    <div class="mh-frm-share">
      <i
        v-for="(s, i) in spec.items"
        :key="`bar-${i}`"
        :style="{ width: `${s.percent}%` }"
        :class="`spec-${s.slot}`"
        :title="`${s.type}: ${s.percent.toFixed(1)}%`"
      >
        <span v-if="s.percent >= 6">{{ Number(s.percent).toFixed(0) }}%</span>
      </i>
      <i
        v-if="spec.residual_percent && spec.residual_percent > 0"
        :style="{ width: `${spec.residual_percent}%` }"
        class="spec-other"
        :title="`Прочее: ${spec.residual_percent.toFixed(1)}%`"
      >
        <span v-if="spec.residual_percent >= 6">{{ Number(spec.residual_percent).toFixed(0) }}%</span>
      </i>
    </div>

    <!-- Specialization rows -->
    <div class="mh-frm-list">
      <div v-for="(s, i) in spec.items" :key="i" :class="['mh-spec-row', `slot-${s.slot}`]">
        <div class="spec-emoji">{{ s.icon || '🌱' }}</div>
        <div class="info">
          <div class="row-top">
            <span class="badge">{{ SLOT_BADGE[s.slot] || s.slot_label || $t('cerrV2.farm.slot.default') }}</span>
            <span class="type">{{ s.type }}</span>
            <span class="dir">{{ s.direction }}</span>
          </div>
          <div class="row-meta">
            <span class="meta-item">
              <CerrIcon name="home2" :size="11" />
              <b>{{ fmt.num(s.households) }}</b> {{ $t('cerrV2.farm.households2') }}
            </span>
            <span class="meta-item">
              <CerrIcon name="users" :size="11" />
              <b>{{ fmt.num(s.population) }}</b> аҳоли
            </span>
          </div>
        </div>
        <div class="pct-block">
          <div class="pct-num tabular">{{ Number(s.percent).toFixed(1).replace('.', ',') }}<span class="pct-sym">%</span></div>
          <div class="pct-lbl">{{ $t('cerrV2.farm.fromHouseholds') }}</div>
        </div>
      </div>
      <div v-if="spec.residual_percent && spec.residual_percent > 0" class="mh-spec-row residual">
        <div class="spec-emoji">⋯</div>
        <div class="info">
          <div class="row-top">
            <span class="type muted">{{ $t('cerrV2.farm.otherActivity') }}</span>
          </div>
          <div class="row-meta muted">{{ $t('cerrV2.farm.otherHouseholds') }}</div>
        </div>
        <div class="pct-block">
          <div class="pct-num tabular muted">{{ Number(spec.residual_percent).toFixed(1).replace('.', ',') }}<span class="pct-sym">%</span></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Crops / Tomorqa -->
  <section v-if="crops?.seasons?.length" class="card mh-frm-card">
    <header class="mh-frm-head">
      <div class="t-l">
        <div class="ico-tile" :style="{ background: 'rgba(20, 163, 74, .12)', color: 'var(--pos-700)' }">
          <CerrIcon name="leaf" :size="14" />
        </div>
        <div>
          <div class="t">{{ $t('cerrV2.farm.tomorqaTitle') }}</div>
          <div class="s">{{ $t('cerrV2.farm.tomorqaSub') }}</div>
        </div>
      </div>
      <div class="t-r">
        <div class="kbig">
          <span class="num tabular">{{ Number(crops.total_homestead_area_sotikh ?? 0).toFixed(1).replace('.', ',') }}</span>
          <span class="lbl">{{ $t('cerrV2.farm.sotix') }}</span>
        </div>
        <div class="period">{{ $t('cerrV2.farm.totalArea') }}</div>
      </div>
    </header>

    <!-- Seasons stacked bar -->
    <div class="mh-frm-share crops-share">
      <i
        v-for="(s, i) in crops.seasons"
        :key="`cb-${i}`"
        :style="{ width: `${pctHh(s)}%`, background: SEASON_COLOR[s.key] || 'var(--brand-blue-500)' }"
        :title="`${s.label}: ${s.household_count} хонадон`"
      >
        <span v-if="pctHh(s) >= 8">{{ Math.round(pctHh(s)) }}%</span>
      </i>
    </div>

    <!-- Per-season cards -->
    <div class="mh-crops-grid">
      <div v-for="(s, i) in crops.seasons" :key="i" class="mh-crop-cell" :style="{ '--c': SEASON_COLOR[s.key] || 'var(--brand-blue-500)' }">
        <div class="cell-h">
          <span class="dot" />
          <span class="lbl">{{ s.label }}</span>
        </div>
        <div class="cell-v">
          <span class="num tabular">{{ fmt.num(s.household_count) }}</span>
          <span class="u">{{ $t('cerrV2.farm.households2') }}</span>
        </div>
        <div class="cell-foot">
          <CerrIcon name="leaf" :size="11" />
          <span v-if="s.homestead_area_ha != null">
            {{ $t('cerrV2.farm.areaHa', { n: Number(s.homestead_area_ha).toFixed(1) }) }}
          </span>
          <span v-else class="muted">{{ $t('cerrV2.farm.areaUnknown') }}</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Infrastructure -->
  <section v-if="infra" class="card mh-frm-card">
    <header class="mh-frm-head">
      <div class="t-l">
        <div class="ico-tile" :style="{ background: 'rgba(0, 84, 166, .1)', color: 'var(--brand-navy-bright)' }">
          <CerrIcon name="road" :size="14" />
        </div>
        <div>
          <div class="t">{{ $t('cerrV2.farm.infraTitle') }}</div>
          <div class="s">{{ $t('cerrV2.farm.infraSub') }}</div>
        </div>
      </div>
    </header>

    <div class="mh-infra-grid">
      <!-- Roads -->
      <div class="mh-infra-block">
        <div class="block-h">
          <CerrIcon name="road" :size="13" />
          <span>{{ $t('cerrV2.farm.roads') }}</span>
        </div>
        <div class="block-v">
          <span class="num tabular">{{ Number(infra.road_km || 0).toFixed(1) }}</span>
          <span class="u">{{ $t('cerrV2.farm.kmTotal') }}</span>
        </div>
        <div v-if="infra.road_km > 0" class="block-bar">
          <i :style="{ width: `${asphaltShare}%` }" />
        </div>
        <div class="block-meta">
          <div class="item pos">
            <span class="dot" /> {{ $t('cerrV2.farm.asphalt') }}
            <span class="iv tabular">{{ Number(infra.road_asphalt_km || 0).toFixed(2) }} км</span>
          </div>
          <div class="item neu">
            <span class="dot" /> {{ $t('cerrV2.farm.dirt') }}
            <span class="iv tabular">{{ Number(infra.road_dirt_km || 0).toFixed(1) }} км</span>
          </div>
          <div v-if="infra.road_km > 0" class="item asphalt-pct">
            <span>{{ $t('cerrV2.farm.asphalted') }}</span>
            <span class="iv tabular">{{ asphaltShare.toFixed(0) }}%</span>
          </div>
        </div>
      </div>

      <!-- Utilities -->
      <div class="mh-infra-block">
        <div class="block-h">
          <CerrIcon name="bolt" :size="13" />
          <span>{{ $t('cerrV2.farm.utility') }}</span>
        </div>
        <div class="block-v">
          <span class="num tabular">{{ infra.power_cuts ?? 0 }}</span>
          <span class="u">{{ $t('cerrV2.farm.outages') }}</span>
        </div>
        <div class="block-meta">
          <div :class="['item', (infra.no_water || 0) > 0 ? 'neg' : 'pos']">
            <CerrIcon name="drop" :size="11" /> {{ $t('cerrV2.farm.noWater') }}
            <span class="iv tabular">{{ infra.no_water ?? 0 }} {{ $t('cerrV2.farm.households3') }}</span>
          </div>
          <div class="item neu">
            <CerrIcon name="info" :size="11" /> {{ $t('cerrV2.farm.duration') }}
            <span class="iv tabular">{{ infra.power_hrs ?? '0' }} ч</span>
          </div>
        </div>
      </div>

      <!-- Social objects -->
      <div class="mh-infra-block">
        <div class="block-h">
          <CerrIcon name="hospital" :size="13" />
          <span>{{ $t('cerrV2.farm.social') }}</span>
        </div>
        <div class="block-v">
          <span class="num tabular">{{ socialCount }}</span>
          <span class="u">{{ $t('cerrV2.farm.objects') }}</span>
        </div>
        <div class="block-meta social">
          <div class="item">
            <CerrIcon name="school" :size="11" /> {{ $t('cerrV2.farm.schools') }}
            <span class="iv tabular">{{ infra.school ?? 0 }}</span>
          </div>
          <div class="item">
            <CerrIcon name="home2" :size="11" /> {{ $t('cerrV2.farm.kindergartens') }}
            <span class="iv tabular">{{ infra.kindergarten ?? 0 }}</span>
          </div>
          <div class="item">
            <CerrIcon name="award" :size="11" /> {{ $t('cerrV2.farm.sport') }}
            <span class="iv tabular">{{ infra.sport ?? 0 }}</span>
          </div>
        </div>
        <div v-if="infra.medical_km != null" class="block-foot">
          <CerrIcon name="hospital" :size="11" />
          {{ $t('cerrV2.farm.medical') }}: <b>{{ Number(infra.medical_km).toFixed(1) }} км</b>
        </div>
      </div>
    </div>

    <div v-if="infra.tomorqa_ha != null" class="mh-infra-foot">
      <CerrIcon name="leaf" :size="12" />
      <span>{{ $t('cerrV2.farm.tomorqaTotal') }}: <b class="tabular">{{ fmt.num(Math.round(infra.tomorqa_ha)) }}</b> {{ $t('cerrV2.farm.ha') }}</span>
    </div>
  </section>
</template>

<style>
/* ============== Хозяйство tab ============== */
.cerr-v2-scope .mh-frm-card {
  padding: 0;
  border-radius: 14px;
  overflow: hidden;
}
.cerr-v2-scope .mh-frm-head {
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--border);
}
.cerr-v2-scope .mh-frm-head .t-l { display: flex; gap: 12px; align-items: flex-start; }
.cerr-v2-scope .mh-frm-head .t { font-size: 15px; font-weight: 800; color: var(--text); line-height: 1.2; }
.cerr-v2-scope .mh-frm-head .s { font-size: 12px; color: var(--text-soft); margin-top: 2px; font-weight: 500; }
.cerr-v2-scope .mh-frm-head .t-r { text-align: right; flex-shrink: 0; }
.cerr-v2-scope .mh-frm-head .kbig { display: inline-flex; align-items: baseline; gap: 6px; }
.cerr-v2-scope .mh-frm-head .kbig .num {
  font-size: 26px; font-weight: 900; letter-spacing: -.025em;
  color: var(--text); font-variant-numeric: tabular-nums; line-height: 1;
}
.cerr-v2-scope .mh-frm-head .kbig .lbl {
  font-size: 11px; font-weight: 700; letter-spacing: .04em;
  text-transform: uppercase; color: var(--text-soft);
}
.cerr-v2-scope .mh-frm-head .period {
  font-size: 11px; font-weight: 600; color: var(--text-faint); margin-top: 4px;
}

/* Stacked share bar */
.cerr-v2-scope .mh-frm-share {
  display: flex; height: 26px;
  margin: 14px 20px 0;
  border-radius: 6px; overflow: hidden;
  background: var(--n-100);
}
.cerr-v2-scope .mh-frm-share i {
  display: flex; align-items: center; justify-content: center;
  height: 100%;
  font-size: 11px; font-weight: 800;
  color: rgba(255, 255, 255, 0.92);
  transition: width .25s ease;
  white-space: nowrap;
  overflow: hidden;
}
.cerr-v2-scope .mh-frm-share .spec-main  { background: #f59e0b; }
.cerr-v2-scope .mh-frm-share .spec-add_2 { background: #0ea5e9; }
.cerr-v2-scope .mh-frm-share .spec-add_3 { background: #8b5cf6; }
.cerr-v2-scope .mh-frm-share .spec-add_4 { background: #14a34a; }
.cerr-v2-scope .mh-frm-share .spec-add_5 { background: #ec4899; }
.cerr-v2-scope .mh-frm-share .spec-other {
  background: var(--n-200);
  color: var(--text-muted);
}

/* Specialization rows */
.cerr-v2-scope .mh-frm-list {
  display: flex; flex-direction: column;
  padding: 14px 20px 16px;
  gap: 8px;
}
.cerr-v2-scope .mh-spec-row {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 12px 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  border-left: 3px solid var(--n-200);
}
.cerr-v2-scope .mh-spec-row.slot-main  { border-left-color: #f59e0b; }
.cerr-v2-scope .mh-spec-row.slot-add_2 { border-left-color: #0ea5e9; }
.cerr-v2-scope .mh-spec-row.slot-add_3 { border-left-color: #8b5cf6; }
.cerr-v2-scope .mh-spec-row.slot-add_4 { border-left-color: #14a34a; }
.cerr-v2-scope .mh-spec-row.slot-add_5 { border-left-color: #ec4899; }
.cerr-v2-scope .mh-spec-row.residual { border-left-color: var(--n-200); background: var(--n-25); }
.cerr-v2-scope .mh-spec-row .spec-emoji {
  width: 44px; height: 44px;
  display: grid; place-items: center;
  border-radius: 10px;
  background: var(--n-50);
  font-size: 22px;
  flex-shrink: 0;
}
.cerr-v2-scope .mh-spec-row .info { min-width: 0; }
.cerr-v2-scope .mh-spec-row .row-top {
  display: flex; align-items: center; flex-wrap: wrap;
  gap: 8px;
}
.cerr-v2-scope .mh-spec-row .badge {
  font-size: 10px; font-weight: 800;
  padding: 2px 7px; border-radius: 6px;
  background: var(--n-100);
  color: var(--text-muted);
  letter-spacing: 0.06em; text-transform: uppercase;
}
.cerr-v2-scope .mh-spec-row.slot-main  .badge { background: #fef3c7; color: #92400e; }
.cerr-v2-scope .mh-spec-row.slot-add_2 .badge { background: #dbeafe; color: #1e40af; }
.cerr-v2-scope .mh-spec-row.slot-add_3 .badge { background: #ede9fe; color: #6d28d9; }
.cerr-v2-scope .mh-spec-row .type { font-size: 14px; font-weight: 800; color: var(--text); }
.cerr-v2-scope .mh-spec-row .type.muted { color: var(--text-soft); font-weight: 700; }
.cerr-v2-scope .mh-spec-row .dir { font-size: 12.5px; font-weight: 600; color: var(--text-soft); }
.cerr-v2-scope .mh-spec-row .row-meta {
  display: flex; flex-wrap: wrap;
  gap: 12px;
  margin-top: 4px;
  font-size: 12px; font-weight: 600; color: var(--text-soft);
}
.cerr-v2-scope .mh-spec-row .row-meta.muted { color: var(--text-faint); }
.cerr-v2-scope .mh-spec-row .meta-item {
  display: inline-flex; align-items: center; gap: 4px;
}
.cerr-v2-scope .mh-spec-row .meta-item b { font-weight: 800; color: var(--text); }
.cerr-v2-scope .mh-spec-row .pct-block {
  text-align: right;
  flex-shrink: 0;
}
.cerr-v2-scope .mh-spec-row .pct-num {
  font-size: 24px; font-weight: 900; letter-spacing: -.022em;
  color: var(--text); font-variant-numeric: tabular-nums; line-height: 1;
}
.cerr-v2-scope .mh-spec-row .pct-num.muted { color: var(--text-soft); }
.cerr-v2-scope .mh-spec-row .pct-sym {
  font-size: 14px; font-weight: 700; color: var(--text-soft);
  margin-left: 1px;
}
.cerr-v2-scope .mh-spec-row .pct-lbl {
  font-size: 10px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: var(--text-faint);
  margin-top: 2px;
}

/* Crops grid */
.cerr-v2-scope .mh-crops-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  padding: 14px 20px 16px;
}
.cerr-v2-scope .mh-crop-cell {
  display: flex; flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
  border-top: 3px solid var(--c, var(--brand-blue-500));
}
.cerr-v2-scope .mh-crop-cell .cell-h {
  display: flex; align-items: center; gap: 7px;
}
.cerr-v2-scope .mh-crop-cell .cell-h .dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--c, var(--brand-blue-500));
}
.cerr-v2-scope .mh-crop-cell .cell-h .lbl {
  font-size: 12px; font-weight: 800; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--text);
}
.cerr-v2-scope .mh-crop-cell .cell-v {
  display: flex; align-items: baseline; gap: 5px;
}
.cerr-v2-scope .mh-crop-cell .cell-v .num {
  font-size: 26px; font-weight: 900; letter-spacing: -.022em;
  color: var(--text); font-variant-numeric: tabular-nums; line-height: 1;
}
.cerr-v2-scope .mh-crop-cell .cell-v .u {
  font-size: 11.5px; font-weight: 600; color: var(--text-soft);
}
.cerr-v2-scope .mh-crop-cell .cell-foot {
  display: flex; align-items: center; gap: 5px;
  font-size: 11.5px; font-weight: 600; color: var(--text-soft);
}
.cerr-v2-scope .mh-crop-cell .cell-foot b { font-weight: 900; color: var(--text); }
.cerr-v2-scope .mh-crop-cell .cell-foot .muted { color: var(--text-faint); font-style: italic; }

/* Infrastructure grid */
.cerr-v2-scope .mh-infra-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 8px;
  padding: 14px 20px 8px;
}
.cerr-v2-scope .mh-infra-block {
  display: flex; flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
}
.cerr-v2-scope .mh-infra-block .block-h {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 11px; font-weight: 800; letter-spacing: .08em;
  text-transform: uppercase; color: var(--text-muted);
}
.cerr-v2-scope .mh-infra-block .block-v {
  display: flex; align-items: baseline; gap: 5px;
}
.cerr-v2-scope .mh-infra-block .block-v .num {
  font-size: 30px; font-weight: 900; letter-spacing: -.025em;
  color: var(--text); font-variant-numeric: tabular-nums; line-height: 1;
}
.cerr-v2-scope .mh-infra-block .block-v .u {
  font-size: 12px; font-weight: 600; color: var(--text-soft);
}
.cerr-v2-scope .mh-infra-block .block-bar {
  height: 5px;
  background: var(--n-100);
  border-radius: 999px;
  overflow: hidden;
}
.cerr-v2-scope .mh-infra-block .block-bar i {
  display: block; height: 100%;
  background: linear-gradient(90deg, var(--pos-500), var(--pos-600));
  border-radius: 999px;
}
.cerr-v2-scope .mh-infra-block .block-meta {
  display: flex; flex-direction: column; gap: 4px;
}
.cerr-v2-scope .mh-infra-block .block-meta.social { flex-direction: row; flex-wrap: wrap; gap: 12px; }
.cerr-v2-scope .mh-infra-block .item {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600;
  color: var(--text-soft);
}
.cerr-v2-scope .mh-infra-block .item .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--n-300);
}
.cerr-v2-scope .mh-infra-block .item.pos .dot { background: var(--pos-500); }
.cerr-v2-scope .mh-infra-block .item.pos { color: var(--pos-700); }
.cerr-v2-scope .mh-infra-block .item.neg { color: var(--neg-700); }
.cerr-v2-scope .mh-infra-block .item .iv {
  margin-left: auto; font-weight: 800; color: var(--text);
}
.cerr-v2-scope .mh-infra-block .item.asphalt-pct {
  margin-top: 2px; font-size: 11px;
  color: var(--text-faint); text-transform: uppercase;
  letter-spacing: 0.05em; font-weight: 700;
}
.cerr-v2-scope .mh-infra-block .item.asphalt-pct .iv { color: var(--pos-700); }
.cerr-v2-scope .mh-infra-block .block-foot {
  margin-top: 6px;
  padding-top: 8px;
  border-top: 1px dashed var(--border);
  font-size: 12px; font-weight: 600; color: var(--text-soft);
  display: flex; align-items: center; gap: 6px;
}
.cerr-v2-scope .mh-infra-block .block-foot b { font-weight: 800; color: var(--text); }

.cerr-v2-scope .mh-infra-foot {
  padding: 12px 20px 16px;
  border-top: 1px solid var(--border);
  display: flex; align-items: center; gap: 6px;
  font-size: 12.5px; font-weight: 600;
  color: var(--text-soft);
}
.cerr-v2-scope .mh-infra-foot b { font-weight: 900; color: var(--text); }

@media (max-width: 720px) {
  .cerr-v2-scope .mh-spec-row { grid-template-columns: 36px 1fr; }
  .cerr-v2-scope .mh-spec-row .pct-block { grid-column: 2; text-align: left; }
  .cerr-v2-scope .mh-spec-row .spec-emoji { width: 36px; height: 36px; font-size: 18px; }
}
</style>
