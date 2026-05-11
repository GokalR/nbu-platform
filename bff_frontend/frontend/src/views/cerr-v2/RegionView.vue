<script setup>
/* Region screen: hero + KPI strip + district map + featured rating bar + RAQAMLARDA macro. */
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
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
const { t: tFn } = useI18n()

const regionCode = computed(() => Number(route.params.regionCode))

watch(regionCode, async (code) => {
  if (!code) return
  await Promise.all([
    store.loadRegions(),
    store.loadRegionOverview(code),
    store.loadRegionDistricts(code),
    store.loadRegionGeo(code),
    store.loadRaqamlarda(String(code)),
    /* Country aggregate carries the cross-region rank + integrated score
     * this region's hero shows in the bottom-right two tiles. */
    store.loadCountryAggregate(),
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

/** Pull the population KPI from the region overview (kept separate so the
 *  structured 5-tile hero below doesn't have to scan kpis on every render). */
const populationKpi = computed(() => {
  return (overview.value?.kpis || []).find((k) => k.key === 'population') || null
})

/** Rank + integrated score of this region within the country (mean of
 *  district means of mahalla rating_score). Comes from the precomputed
 *  country aggregate so it doesn't trigger any new R2 reads. */
const countryEntry = computed(() => {
  const arr = store.countryAggregate?.regions || []
  return arr.find((r) => r.code === regionCode.value) || null
})
const countryRegionsCount = computed(() => (store.countryAggregate?.regions || []).length || 14)

/** Tone helper: 'lead' tier (top 40%) is positive, 'low' (bottom 20%) is
 *  negative, 'mid' is neutral. Matches the country page's rank-tier split. */
function tierTone(tier) {
  if (tier === 'lead') return 'pos'
  if (tier === 'low')  return 'neg'
  return 'neu'
}

/** 3-tile structured stat strip: population, districts, mahallas. Rating
 *  + rank live in the right-side callout instead (see ratingPanel below). */
const heroStats = computed(() => {
  const pop = populationKpi.value
  const r = region.value
  const out = []
  if (pop) {
    out.push({ key: 'pop', label: tFn('cerrV2.region.stat.pop'), ico: iconForKpi('population'), value: fmt.num(pop.value) })
  }
  if (r?.districts_count != null) {
    out.push({ key: 'districts', label: tFn('cerrV2.region.stat.districts'), ico: iconForKpi('mahalla_count'), value: fmt.num(r.districts_count) })
  }
  if (r?.mahalla_count != null) {
    out.push({ key: 'mahallas', label: tFn('cerrV2.region.stat.mahallas'), ico: 'grid', value: fmt.num(r.mahalla_count) })
  }
  return out
})

/** Rating callout on the right side of the hero (same look as the mahalla
 *  page): big score + tier-tinted rank chip. Tier comes from country
 *  aggregate so colour matches the country map. */
const ratingPanel = computed(() => {
  const ce = countryEntry.value
  if (!ce || ce.score == null) return null
  return {
    score: Number(ce.score).toFixed(1).replace('.', ','),
    tier: ce.tier || 'mid',
    rank: ce.rank,
    total: countryRegionsCount.value,
  }
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
    sub: tFn('cerrV2.district.mahallasShort', { n: d.mahallas }),
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
      <section :class="['hero hero-v2 mahalla-hero entity-hero', ratingPanel ? 'has-rating-card' : '']">
        <div class="hero-v2-head">
          <div class="hero-v2-l">
            <div class="hv2-eyebrow">{{ $t('cerrV2.eyebrow.region') }}</div>
            <h2 class="hero-title">{{ overview?.header?.title || region?.name || '—' }}</h2>
            <p class="hv2-breadcrumb">
              <span>{{ $t('cerrV2.country.title') }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ $t('cerrV2.region.districtsAndCities', { n: region?.districts_count }) }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ $t('cerrV2.region.mahallasCount', { n: fmt.num(region?.mahalla_count) }) }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span class="hv2-breadcrumb-period">
                <CerrIcon name="info" :size="11" /> {{ $t('cerrV2.common.data2025') }}
              </span>
            </p>
          </div>

          <!-- Rating callout on the right side of hero (same look as mahalla page) -->
          <div v-if="ratingPanel" :class="['mh-rating-card', `tier-${ratingPanel.tier}`]">
            <div class="mh-rating-num tabular">{{ ratingPanel.score }}</div>
            <div class="mh-rating-lbl">{{ $t('cerrV2.mahalla.ratingScore') }}</div>
            <div class="mh-rating-ranks">
              <div v-if="ratingPanel.rank" :class="['mh-rank-pill', `tier-${ratingPanel.tier}`]">
                <CerrIcon name="map" :size="11" />
                <span><b>{{ ratingPanel.rank }}</b> / {{ ratingPanel.total }}</span>
                <span class="lbl">{{ $t('cerrV2.region.inCountry') }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="hero-v2-stats mh-stats" :data-count="heroStats.length">
          <div v-for="s in heroStats" :key="s.key" class="hv2-stat">
            <div class="hv2-stat-head">
              <span class="hv2-stat-ico"><CerrIcon :name="s.ico" :size="16" /></span>
              <div class="hv2-stat-label">{{ s.label }}</div>
            </div>
            <div class="hv2-stat-row">
              <span :class="['hv2-stat-val tabular', s.deltaTone === 'pos' ? 'is-pos' : s.deltaTone === 'neg' ? 'is-neg' : '']">{{ s.value }}</span>
              <span v-if="s.unit" class="hv2-stat-unit">{{ s.unit }}</span>
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
            :subtitle="region ? $t('cerrV2.region.mapSub', { n: region.districts_count, m: fmt.num(region.mahalla_count) }) : ''"
            @select="(k) => goDistrict(Number(k))"
            :label-min="32"
          />
          <div class="map-side">
            <div class="map-side-h">{{ $t('cerrV2.region.tierGroups') }}</div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#bfe5d4' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.lead') }}</span>
              <span class="n tabular">{{ tierCounts.lead }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f5e3b8' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.mid') }}</span>
              <span class="n tabular">{{ tierCounts.mid }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f7c9b8' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.low') }}</span>
              <span class="n tabular">{{ tierCounts.low }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#eecccc' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.risk') }}</span>
              <span class="n tabular">{{ tierCounts.risk }}</span>
            </div>
            <div class="map-focus">
              <div class="eye">{{ $t('cerrV2.common.hint') }}</div>
              <div class="hint">{{ $t('cerrV2.region.clickHintDistrict') }}</div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="chartData.length" class="card featured">
        <h3 class="card-title">
          <span class="ico-tile"><CerrIcon name="chart" :size="14" /></span>
          {{ chartTitle }}
          <span class="card-title-end">{{ $t('cerrV2.common.lessBetter') }}</span>
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
      :title="`${$t('cerrV2.region.districtsTitle')} ${region?.name || ''}`"
      :count="districtRanking.length"
      :items="districtRanking"
      :row-for="rowFor"
      :search-placeholder="$t('cerrV2.region.searchDistrict')"
      :meta-right="$t('cerrV2.common.sortAlpha')"
      @select="(d) => goDistrict(d.code)"
    >
      <template #header-top><NavStepper /></template>
    </SidebarRail>
  </div>
</template>

<style>
/* Entity-hero variant (region/district): same chrome as mahalla-hero but
 * the head is single-column (no rating-card on the right) and the KPI
 * strip column count adapts to how many tiles are in the data. When a
 * rating callout is present (region with country rank, district with
 * region rank), restore the 2-column head to give the callout a slot. */
.cerr-v2-scope .entity-hero .hero-v2-head { grid-template-columns: 1fr; }
.cerr-v2-scope .entity-hero.has-rating-card .hero-v2-head {
  grid-template-columns: minmax(0, 1fr) minmax(240px, 320px);
  gap: 32px;
}
.cerr-v2-scope .entity-hero .mh-stats[data-count="4"] { grid-template-columns: repeat(4, 1fr); }
.cerr-v2-scope .entity-hero .mh-stats[data-count="5"] { grid-template-columns: repeat(5, 1fr); }
.cerr-v2-scope .entity-hero .mh-stats[data-count="6"] { grid-template-columns: repeat(6, 1fr); }
@media (max-width: 1280px) {
  .cerr-v2-scope .entity-hero .mh-stats[data-count="4"],
  .cerr-v2-scope .entity-hero .mh-stats[data-count="5"],
  .cerr-v2-scope .entity-hero .mh-stats[data-count="6"] { grid-template-columns: repeat(2, 1fr); }
}

/* Rating / rank tiles use a tier-tone colour for the value so 'top 40 %'
 * regions show green and 'bottom 20 %' show red. */
.cerr-v2-scope .entity-hero .hv2-stat-val.is-pos { color: #34d399; }
.cerr-v2-scope .entity-hero .hv2-stat-val.is-neg { color: #f87171; }
</style>
