<script setup>
/* Region screen: hero + KPI strip + district map + featured rating bar + RAQAMLARDA macro. */
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import { fmt, iconForKpi } from '@/data/cerrV2Format.js'
import EntityMap from '@/components/cerr-v2/EntityMap.vue'
import MacroPanel from '@/components/cerr-v2/MacroPanel.vue'
import SidebarRail from '@/components/cerr-v2/SidebarRail.vue'
import CerrIcon from '@/components/cerr-v2/CerrIcon.vue'
import NavStepper from '@/components/cerr-v2/NavStepper.vue'

const route = useRoute()
const router = useRouter()
const store = useCerrV2Store()

const regionCode = computed(() => Number(route.params.regionCode))

watch(regionCode, async (code) => {
  if (!code) return
  await Promise.all([
    store.loadRegions(),
    store.loadRegionOverview(code),
    store.loadRegionDistricts(code),
    store.loadRegionGeo(code),
    store.loadRaqamlarda(String(code)),
  ])
  // Side-load district overviews (for rating tier coloring) in parallel —
  // 16-22 districts otherwise stack into ~600ms of sequential round-trips.
  await Promise.all((store.regionDistricts[code] || []).map((d) => store.loadDistrictOverview(d.code)))
}, { immediate: true })

const region = computed(() => store.regionByCode(regionCode.value))
const overview = computed(() => store.regionOverview[regionCode.value] || null)
const districts = computed(() => store.regionDistricts[regionCode.value] || [])
const geo = computed(() => store.regionGeo[regionCode.value])
const macro = computed(() => store.raqamlarda[String(regionCode.value)])

/** Build per-district rating ranking from district.overview.kpis[key='rating_score'].
 *  Rank is computed by rating (lower = better, since it's a "place" in CERR), but
 *  the array we return is then alphabetised for display in the rail. */
const districtRanking = computed(() => {
  const arr = districts.value.map((d) => {
    const ov = store.districtOverview[d.code]
    const r = (ov?.kpis || []).find((k) => k.key === 'rating_score')
    return { code: d.code, name: d.name, mahallas: d.mahalla_count, rating: r?.value ?? null }
  })
  // First sort by rating to assign ranks…
  const byRating = [...arr].sort((a, b) => (a.rating ?? Infinity) - (b.rating ?? Infinity))
  byRating.forEach((d, i) => { d.pos = i + 1 })
  // …then return alphabetised for the rail.
  arr.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ru'))
  return arr
})

/** Bar chart from region_overview.chart.data[]. */
const chartData = computed(() => overview.value?.chart?.data || [])
const chartTitle = computed(() => overview.value?.chart?.title || 'Туманлар бўйича энг юқори рейтинг ўрни')
const maxChart = computed(() => Math.max(1, ...chartData.value.map((d) => d.value || 0)))

const heroKpis = computed(() => {
  const k = (overview.value?.kpis || [])
  return k.filter((x) => ['population', 'active_businesses', 'unemployed', 'rating_score'].includes(x.key))
})

/** KPI strip data (mahalla-hero look): each tile gets a delta chip and an
 *  optional district-average footnote. Tone follows direction: for "down"
 *  KPIs (e.g. unemployed) a positive change_pct is bad. */
const heroStats = computed(() => {
  return heroKpis.value.map((k) => {
    const dir = k.direction
    let tone = 'neu'
    if (k.change_pct != null) {
      if (dir === 'down') tone = k.change_pct > 0 ? 'neg' : 'pos'
      else tone = k.change_pct > 0 ? 'pos' : 'neg'
    }
    return {
      key: k.key,
      label: k.label,
      ico: iconForKpi(k.key),
      value: fmt.num(k.value),
      delta: k.change_pct != null
        ? `${k.change_pct > 0 ? '+' : ''}${Number(k.change_pct).toFixed(1).replace('.', ',')}%`
        : null,
      deltaTone: tone,
    }
  })
})

/** Tier districts by rank-percentile within THEIR region (not absolute pos),
 *  so a region with 11 districts and one with 22 both get a balanced 4-band split. */
function tierForRatio(ratio) {
  if (ratio == null) return null
  if (ratio <= 0.25) return 'lead'
  if (ratio <= 0.60) return 'mid'
  if (ratio <= 0.85) return 'low'
  return 'risk'
}
function tierFromPos(pos) {
  const total = districtRanking.value.length
  if (!pos || !total) return null
  return tierForRatio(pos / total)
}
const TIER_COLOR = {
  lead: '#bfe5d4',
  mid:  '#f5e3b8',
  low:  '#f7c9b8',
  risk: '#eecccc',
}
function tierColor(pos) { return TIER_COLOR[tierFromPos(pos)] || '#f0f1f4' }
function tierLabelClass(pos) {
  const t = tierFromPos(pos)
  if (t === 'lead') return 'high'
  if (t === 'mid')  return 'mid'
  return 'low'
}

const dGetKey = (f) => String(f.properties.district_code)
const dGetLabel = (f) => f.properties.district_name
const dGetTooltip = (f) => {
  const d = districtRanking.value.find((x) => x.code === f.properties.district_code)
  return d?.pos ? `${d.name} · #${d.pos}` : f.properties.district_name
}
const dColorize = (f) => {
  const d = districtRanking.value.find((x) => x.code === f.properties.district_code)
  return tierColor(d?.pos)
}

function rowFor(d) {
  return {
    key: d.code,
    name: d.name,
    sub: `${d.mahallas} м.`,
    badge: d.pos ? `#${d.pos}` : '—',
    badgeTone: tierLabelClass(d.pos),
  }
}

function goDistrict(code) {
  router.push({ name: 'cerr-v2-district', params: { districtCode: code } })
}

const tierCounts = computed(() => {
  const c = { lead: 0, mid: 0, low: 0, risk: 0 }
  const total = districtRanking.value.length
  for (const d of districtRanking.value) {
    const t = total ? tierForRatio(d.pos / total) : null
    if (t && t in c) c[t]++
  }
  return c
})

const periodLabel = computed(() => '2026 1-кв.')
</script>

<template>
  <div class="page with-rail">
    <div :style="{ display: 'flex', flexDirection: 'column', gap: '22px', minWidth: 0 }">
      <section class="hero hero-v2 mahalla-hero entity-hero">
        <div class="hero-v2-head">
          <div class="hero-v2-l">
            <div class="hv2-eyebrow">РЕГИОН · ВИЛОЯТ</div>
            <h2 class="hero-title">{{ overview?.header?.title || region?.name || '—' }}</h2>
            <p class="hv2-breadcrumb">
              <span>Республика Узбекистан</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ region?.districts_count }} районов и городов</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ fmt.num(region?.mahalla_count) }} махаллей</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span class="hv2-breadcrumb-period">
                <CerrIcon name="info" :size="11" /> Данные за 2025 год
              </span>
            </p>
          </div>
        </div>
        <div class="hero-v2-stats mh-stats" :data-count="heroStats.length">
          <div v-for="s in heroStats" :key="s.key" class="hv2-stat">
            <div class="hv2-stat-head">
              <span class="hv2-stat-ico"><CerrIcon :name="s.ico" :size="16" /></span>
              <div class="hv2-stat-label">{{ s.label }}</div>
            </div>
            <div class="hv2-stat-row">
              <span class="hv2-stat-val tabular">{{ s.value }}</span>
              <span v-if="s.delta" :class="['mh-delta', s.deltaTone]">{{ s.delta }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="card map-card">
        <div class="map-grid">
          <EntityMap
            :geo="geo"
            :width="620"
            :height="380"
            :get-key="dGetKey"
            :get-label="dGetLabel"
            :get-tooltip="dGetTooltip"
            :colorize="dColorize"
            :selectable="() => true"
            :title="overview?.header?.title || region?.name || ''"
            :subtitle="region ? `${region.districts_count} районов · ${fmt.num(region.mahalla_count)} махаллей` : ''"
            @select="(k) => goDistrict(Number(k))"
            :label-min="32"
          />
          <div class="map-side">
            <div class="map-side-h">Рейтинговые группы</div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#bfe5d4' }" />
              <span class="lbl">Лидеры (топ 25%)</span>
              <span class="n tabular">{{ tierCounts.lead }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f5e3b8' }" />
              <span class="lbl">Средние (25–60%)</span>
              <span class="n tabular">{{ tierCounts.mid }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f7c9b8' }" />
              <span class="lbl">Отстающие (60–85%)</span>
              <span class="n tabular">{{ tierCounts.low }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#eecccc' }" />
              <span class="lbl">Группа риска (нижние 15%)</span>
              <span class="n tabular">{{ tierCounts.risk }}</span>
            </div>
            <div class="map-focus">
              <div class="eye">Подсказка</div>
              <div class="hint">Клик по полигону → анализ района</div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="chartData.length" class="card featured">
        <h3 class="card-title">
          <span class="ico-tile"><CerrIcon name="chart" :size="14" /></span>
          {{ chartTitle }}
          <span class="card-title-end">меньше = лучше</span>
        </h3>
        <div class="bar-chart">
          <div v-for="(d, i) in chartData" :key="i" class="bar-row">
            <div class="nm">{{ d.name }}</div>
            <div class="track"><i :style="{ width: `${(d.value / maxChart) * 100}%` }" /></div>
            <div class="rank">{{ d.value }}</div>
          </div>
        </div>
      </section>

      <MacroPanel v-if="macro" :data="macro" />
    </div>

    <SidebarRail
      :title="`Районы ${region?.name || ''}`"
      :count="districtRanking.length"
      :items="districtRanking"
      :row-for="rowFor"
      search-placeholder="Поиск района…"
      meta-right="сорт. по алфавиту"
      @select="(d) => goDistrict(d.code)"
    >
      <template #header-top><NavStepper /></template>
    </SidebarRail>
  </div>
</template>

<style>
/* Entity-hero variant (region/district): same chrome as mahalla-hero but
 * the head is single-column (no rating-card on the right) and the KPI
 * strip column count adapts to how many tiles are in the data. */
.cerr-v2-scope .entity-hero .hero-v2-head { grid-template-columns: 1fr; }
.cerr-v2-scope .entity-hero .mh-stats[data-count="4"] { grid-template-columns: repeat(4, 1fr); }
.cerr-v2-scope .entity-hero .mh-stats[data-count="5"] { grid-template-columns: repeat(5, 1fr); }
.cerr-v2-scope .entity-hero .mh-stats[data-count="6"] { grid-template-columns: repeat(6, 1fr); }
@media (max-width: 1280px) {
  .cerr-v2-scope .entity-hero .mh-stats[data-count="4"],
  .cerr-v2-scope .entity-hero .mh-stats[data-count="5"],
  .cerr-v2-scope .entity-hero .mh-stats[data-count="6"] { grid-template-columns: repeat(2, 1fr); }
}
</style>
