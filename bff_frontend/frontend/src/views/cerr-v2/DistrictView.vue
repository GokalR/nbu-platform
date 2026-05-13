<script setup>
/* District screen: hero KPIs + rating histogram + mahalla map + macro themes + mahalla rail. */
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import { fmt, iconForKpi } from '@/data/cerrV2Format.js'
import { groupMacroByTheme } from '@/data/macroThemes.js'
import EntityMap from '@/components/cerr-v2/EntityMap.vue'
import HistogramCard from '@/components/cerr-v2/HistogramCard.vue'
import ThemeBlock from '@/components/cerr-v2/ThemeBlock.vue'
import SidebarRail from '@/components/cerr-v2/SidebarRail.vue'
import CerrIcon from '@/components/cerr-v2/CerrIcon.vue'
import NavStepper from '@/components/cerr-v2/NavStepper.vue'

const route = useRoute()
const router = useRouter()
const store = useCerrV2Store()
const { t: tFn } = useI18n()

const districtCode = computed(() => Number(route.params.districtCode))

watch(districtCode, async (code) => {
  if (!code) return
  await store.loadRegions()
  // Determine owning region (lazy: scan loaded regions, else load all overviews)
  let regionCode = null
  for (const list of Object.values(store.regionDistricts)) {
    if ((list || []).find((d) => d.code === code)) {
      regionCode = (list[0] || {}).region_code
      break
    }
  }
  if (!regionCode) {
    // Fallback: load each region's districts list once.
    for (const r of store.regions || []) {
      const ds = await store.loadRegionDistricts(r.code)
      if ((ds || []).find((d) => d.code === code)) { regionCode = r.code; break }
    }
  }
  await Promise.all([
    store.loadDistrictOverview(code),
    store.loadDistrictMacro(code),
    store.loadDistrictMahallas(code),
    store.loadDistrictGeo(code),
  ])
}, { immediate: true })

const district = computed(() => store.districtByCode(districtCode.value))
const overview = computed(() => store.districtOverview[districtCode.value] || null)
const macro = computed(() => store.districtMacro[districtCode.value] || null)
const mahallas = computed(() => store.districtMahallas[districtCode.value] || [])
const geo = computed(() => store.districtGeo[districtCode.value])

/** Place rank of this district within its region (1 = best — direction is
 *  'down' in CERR). Pulled from overview.kpis.rating_score VALUE. */
const populationKpi = computed(() => (overview.value?.kpis || []).find((k) => k.key === 'population') || null)
const ratingRankKpi = computed(() => (overview.value?.kpis || []).find((k) => k.key === 'rating_score') || null)

/** Total districts in the owning region. Tries: 1) the rating_score KPI's
 *  district_avg (CERR fills it with ~total/2 — not exact), 2) the cached
 *  region record. */
const districtsInRegion = computed(() => {
  const r = district.value?.region_code ? store.regionByCode(district.value.region_code) : null
  return r?.districts_count || null
})

/** Compose a 0-100 score from the place rank: top of region → 100, bottom → ~0.
 *  Formula: ((total - rank + 1) / total) * 100. Falls back to null when we
 *  don't know the total yet. */
function scoreFromRank(rank, total) {
  if (!rank || !total) return null
  return ((total - rank + 1) / total) * 100
}

function tierFromRankPos(rank, total) {
  if (!rank || !total) return null
  const ratio = rank / total
  if (ratio <= 0.40) return 'lead'
  if (ratio <= 0.80) return 'mid'
  return 'low'
}
function tierTone(t) {
  if (t === 'lead') return 'pos'
  if (t === 'low')  return 'neg'
  return 'neu'
}

/** 2-tile structured stat strip: population, mahallas. Rating + rank
 *  moved to the right-side callout (see ratingPanel below). */
const heroStats = computed(() => {
  const pop = populationKpi.value
  const out = []
  if (pop) {
    out.push({ key: 'pop', label: tFn('cerrV2.district.stat.pop'), ico: iconForKpi('population'), value: fmt.num(pop.value) })
  }
  if (district.value?.mahalla_count != null) {
    out.push({ key: 'mahallas', label: tFn('cerrV2.district.stat.mahallas'), ico: 'grid', value: fmt.num(district.value.mahalla_count) })
  }
  return out
})

/** Rating callout on the right side of the hero — same look as the mahalla
 *  page. Score derived from the place rank within the region; tier picks
 *  the chip colour. */
const ratingPanel = computed(() => {
  const rankVal = ratingRankKpi.value?.value || null
  const total = districtsInRegion.value
  const score = scoreFromRank(rankVal, total)
  const tier = tierFromRankPos(rankVal, total)
  if (score == null || rankVal == null || !total) return null
  return {
    score: score.toFixed(1).replace('.', ','),
    tier: tier || 'mid',
    rank: rankVal,
    total,
  }
})

const histogram = computed(() => overview.value?.rating_histogram || [])
const macroThemes = computed(() => groupMacroByTheme(macro.value))

/** True when at least one indicator has a point marked `highlighted: true`
 *  (i.e. CERR's per-district comparison row for THIS district exists).
 *  When false but the indicator skeleton still loads, every theme block
 *  would render as "—"/"#— из N" — we replace that with a single empty-
 *  state card instead. Affects ~12 newly-created/renamed tumans whose
 *  CERR macro report doesn't yet include them. */
const macroHasData = computed(() => {
  const inds = macro.value?.indicators
  if (!Array.isArray(inds) || inds.length === 0) return false
  for (const ind of inds) {
    const pts = ind.points || []
    for (const p of pts) {
      if (p && p.highlighted) return true
    }
  }
  return false
})

/** Mahalla list for the rail — alphabetical (per user request). Rank/tier is
 *  still computed from rating_score (see mahallaTier) for the badge color. */
const mahallaList = computed(() => {
  return mahallas.value.slice().sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ru'))
})

/** Higher rating_score = better. Rank mahallas within THIS district and tier by
 *  rank-percentile so every district gets a balanced 4-band split regardless of
 *  the score scale (some districts cluster 5-15, others 50-90). */
const TIER_COLOR = {
  lead: '#bfe5d4',
  mid:  '#f5e3b8',
  low:  '#f7c9b8',
  risk: '#eecccc',
}
function tierForRatio(ratio) {
  if (ratio == null) return null
  if (ratio <= 0.25) return 'lead'
  if (ratio <= 0.60) return 'mid'
  if (ratio <= 0.85) return 'low'
  return 'risk'
}

const mahallaTier = computed(() => {
  // Summary `rating_score` is the mahalla's place rank within its region
  // (lower number = better — e.g. rating_score 5 means 5th best in Sirdaryo).
  // Sort ASCENDING so position 1 → lowest value → best → "lead" tier.
  const arr = mahallas.value
    .filter((m) => m.rating_score != null)
    .slice()
    .sort((a, b) => a.rating_score - b.rating_score)
  const total = arr.length || 1
  const out = new Map()
  arr.forEach((m, i) => out.set(String(m.stir), tierForRatio((i + 1) / total)))
  return out
})

const tierCounts = computed(() => {
  const c = { lead: 0, mid: 0, low: 0, risk: 0 }
  for (const t of mahallaTier.value.values()) if (t in c) c[t]++
  return c
})

function rowFor(m) {
  const t = mahallaTier.value.get(String(m.stir))
  const tone = t === 'lead' ? 'high' : t === 'mid' ? 'mid' : 'low'
  return {
    key: m.stir,
    name: m.name,
    badge: m.rating_score != null ? `${Number(m.rating_score).toFixed(1)}` : '—',
    badgeTone: tone,
  }
}

const mGetKey = (f) => String(f.properties.stir || f.properties.STIR || '')
const mGetLabel = (f) => {
  const name = f.properties.mahalla_name || f.properties.name
  const score = f.properties.rating_score
  return score != null ? `${name} · ${Number(score).toFixed(1)}` : name
}
const mColorize = (f) => {
  const stir = String(f.properties.stir || f.properties.STIR || '')
  const t = mahallaTier.value.get(stir)
  return TIER_COLOR[t] || '#f0f1f4'
}

const sideHistogram = computed(() => {
  if (!histogram.value.length) return null
  const top10 = histogram.value[0]?.count || 0
  const total = histogram.value.reduce((s, b) => s + b.count, 0)
  return {
    big: `${top10} / ${total}`,
    lbl: tFn('cerrV2.histogram.topPct'),
    desc: tFn('cerrV2.histogram.desc'),
    chips: [
      { tone: 'good', count: histogram.value[0]?.count || 0, label: tFn('cerrV2.histogram.chipLeaders') },
      { tone: 'mid',  count: histogram.value[2]?.count || 0, label: tFn('cerrV2.histogram.chipMid') },
      { tone: 'bad',  count: histogram.value[histogram.value.length - 1]?.count || 0, label: tFn('cerrV2.histogram.chipRisk') },
    ],
  }
})

function openTier(stir) {
  router.push({ name: 'cerr-v2-mahalla', params: { stir: String(stir) } })
}
</script>

<template>
  <div class="page with-rail district-page">
    <div :style="{ display: 'flex', flexDirection: 'column', gap: '22px', minWidth: 0 }">
      <section :class="['hero hero-v2 mahalla-hero entity-hero', ratingPanel ? 'has-rating-card' : '']">
        <div class="hero-v2-head">
          <div class="hero-v2-l">
            <div class="hv2-eyebrow">{{ $t('cerrV2.eyebrow.district') }}</div>
            <h2 class="hero-title">{{ overview?.header?.title || district?.name || '—' }}</h2>
            <p class="hv2-breadcrumb">
              <span>{{ $t('cerrV2.country.title') }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ district?.region_name }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ $t('cerrV2.region.mahallasCount', { n: district?.mahalla_count }) }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span class="hv2-breadcrumb-period">
                <CerrIcon name="info" :size="11" /> {{ $t('cerrV2.common.data2025') }}
              </span>
            </p>
          </div>

          <!-- Rating callout (same look as mahalla page) — score derived from
               the district's place rank within its region. -->
          <div v-if="ratingPanel" :class="['mh-rating-card', `tier-${ratingPanel.tier}`]">
            <div class="mh-rating-num tabular">{{ ratingPanel.score }}</div>
            <div class="mh-rating-lbl">{{ $t('cerrV2.mahalla.ratingScore') }}</div>
            <div class="mh-rating-ranks">
              <div :class="['mh-rank-pill', `tier-${ratingPanel.tier}`]">
                <CerrIcon name="award" :size="11" />
                <span><b>{{ ratingPanel.rank }}</b> / {{ ratingPanel.total }}</span>
                <span class="lbl">{{ $t('cerrV2.mahalla.inRegion') }}</span>
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

      <HistogramCard v-if="histogram.length" :histogram="histogram" :side="sideHistogram" />

      <section v-if="geo" class="card map-card">
        <div class="map-grid">
          <EntityMap
            :geo="geo"
            :width="620"
            :height="420"
            :get-key="mGetKey"
            :get-label="mGetLabel"
            :colorize="mColorize"
            :selectable="() => true"
            :show-labels="false"
            :label-min="28"
            :title="overview?.header?.title || district?.name || ''"
            :subtitle="district ? $t('cerrV2.district.mapSub', { region: district.region_name, n: district.mahalla_count }) : ''"
            @select="(k) => openTier(String(k))"
          />
          <div class="map-side">
            <div class="map-side-h">{{ $t('cerrV2.district.ratingMahalla') }}</div>
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
              <div class="hint">{{ $t('cerrV2.district.clickHintMahalla') }}</div>
            </div>
          </div>
        </div>
      </section>

      <div v-if="macroThemes.length && macroHasData" class="section-h">
        <span>{{ $t('cerrV2.macroSummary', { n: macro?.indicators?.length || 0, m: macroThemes.length }) }}</span>
      </div>
      <div v-if="macroThemes.length && macroHasData" class="macro-themes">
        <ThemeBlock v-for="t in macroThemes" :key="t.id" :theme="t" />
      </div>
      <section v-else-if="macroThemes.length" class="card district-macro-empty">
        <div class="dme-icon"><CerrIcon name="info" :size="20" /></div>
        <div class="dme-text">
          <div class="dme-title">{{ $t('cerrV2.district.macroNoData') }}</div>
          <div class="dme-sub">{{ $t('cerrV2.district.macroNoDataSub') }}</div>
        </div>
      </section>
    </div>

    <SidebarRail
      :title="$t('cerrV2.district.siblingsTitle')"
      :count="mahallas.length"
      :items="mahallaList"
      :row-for="rowFor"
      :search-placeholder="$t('cerrV2.district.searchMahalla')"
      :meta-right="$t('cerrV2.common.sortAlpha')"
      @select="(m) => openTier(m.stir)"
    >
      <template #header-top><NavStepper /></template>
    </SidebarRail>
  </div>
</template>

<style>
.cerr-v2-scope .district-macro-empty {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}
.cerr-v2-scope .district-macro-empty .dme-icon {
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 84, 166, 0.08);
  color: var(--brand-navy-bright, #0054A6);
}
.cerr-v2-scope .district-macro-empty .dme-title {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--brand-navy-deep, #001b3d);
}
.cerr-v2-scope .district-macro-empty .dme-sub {
  margin-top: 4px;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.45;
  color: var(--text-soft, #5a6473);
}
</style>
