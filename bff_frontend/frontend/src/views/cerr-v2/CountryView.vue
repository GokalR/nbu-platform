<script setup>
/* Country screen: 14 regions, country-level KPIs aggregated, RAQAMLARDA national. */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import { fmt } from '@/data/cerrV2Format.js'
import { UZ_MACRO_HISTORY, UZ_MACRO_YEARS, fmtTrln, buildBars } from '@/data/uzMacroHistory.js'
import EntityMap from '@/components/cerr-v2/EntityMap.vue'
import MacroPanel from '@/components/cerr-v2/MacroPanel.vue'
import SidebarRail from '@/components/cerr-v2/SidebarRail.vue'
import CerrIcon from '@/components/cerr-v2/CerrIcon.vue'
import NavStepper from '@/components/cerr-v2/NavStepper.vue'

const router = useRouter()
const store = useCerrV2Store()
const { t: tFn } = useI18n()
const sortMode = ref('pop')

onMounted(async () => {
  /* Single aggregate fetch (~10 KB, served from a precomputed static file)
   * hydrates `regions`, `regionOverview` (population only) and
   * `countryRankings` in one shot — replaces the previous fan-out of
   * 14 region overviews + a country-rankings call that was walking
   * ~200 mahallas.json files from R2 on every cold start. */
  await Promise.all([
    store.loadCountryAggregate(),
    store.loadCountryGeo(),
    store.loadRaqamlarda('national'),
  ])
})

const regionsEnriched = computed(() => {
  const list = store.regions || []
  return list.map((r) => {
    const ov = store.regionOverview[r.code]
    const popKpi = (ov?.kpis || []).find((k) => k.key === 'population')
    return {
      ...r,
      pop: popKpi?.value || 0,
      hasCerr: !!ov,
    }
  })
})

const aggregates = computed(() => {
  const arr = regionsEnriched.value
  return {
    pop: arr.reduce((s, r) => s + (r.pop || 0), 0),
    mahallas: arr.reduce((s, r) => s + (r.mahalla_count || 0), 0),
    districts: arr.reduce((s, r) => s + (r.districts_count || 0), 0),
    covered: arr.filter((r) => r.hasCerr).length,
  }
})

/** 4-up demographic strip in the hero. Population uses the curated national
 *  figure (38,24 млн, asof 1.01.2026) instead of the live region-aggregate sum
 *  — the aggregate misses recent updates and runs ~700k low. Other tiles
 *  remain projected from aggregates. */
const heroStats = computed(() => {
  const totalRegions = (store.regions || []).length || 14
  return [
    { key: 'pop', label: tFn('cerrV2.country.stat.pop'),     value: popChart.value.valueStr,             unit: tFn('cerrV2.country.macroLabel.gdp') === 'ВВП' ? 'млн' : 'млн', ico: 'users', hasChart: true },
    { key: 'mah', label: tFn('cerrV2.country.stat.mahalla'), value: fmt.num(aggregates.value.mahallas),  unit: '',                                                  ico: 'grid'  },
    { key: 'dst', label: tFn('cerrV2.country.stat.district'),value: fmt.num(aggregates.value.districts), unit: '',                                                  ico: 'map'   },
    { key: 'cov', label: tFn('cerrV2.country.stat.covered'), value: String(totalRegions),                unit: '',                                                          ico: 'check' },
  ]
})

/** 5 hero macro tiles. Absolute trln-soum value comes from the curated
 *  2021-2025 series in `uzMacroHistory.js`; the YoY % delta keeps using the
 *  RAQAMLARDA feed (which already carries the official real-growth figure for
 *  the current period — Industry, Retail and Services do not have a separate
 *  real-growth publication, so the value is nominal share-of-100 in those
 *  cases). The 5-point sparkline visualises the 2021→2025 trajectory. */
const HERO_MACRO_LABELS = computed(() => ({
  gdp:    tFn('cerrV2.country.macroLabel.gdp'),
  ind:    tFn('cerrV2.country.macroLabel.ind'),
  inv:    tFn('cerrV2.country.macroLabel.inv'),
  retail: tFn('cerrV2.country.macroLabel.retail'),
  serv:   tFn('cerrV2.country.macroLabel.serv'),
}))
const HERO_MACRO_ORDER = ['gdp', 'ind', 'inv', 'retail', 'serv']
const heroMacro = computed(() => {
  return HERO_MACRO_ORDER.map((key) => {
    const hist = UZ_MACRO_HISTORY[key]
    if (!hist) return null
    const last = hist.abs[hist.abs.length - 1]
    if (last == null) return null
    const r = store.raqamlarda.national
    const ind = r?.indicators?.find((i) => i.key === key)
    const delta = ind?.val != null ? ind.val - 100 : null
    return {
      key,
      label: HERO_MACRO_LABELS.value[key] || hist.label,
      absStr: fmtTrln(last),
      deltaStr: delta == null ? null : (delta >= 0 ? '+' : '') + delta.toFixed(1).replace('.', ','),
      isPos: delta == null ? true : delta >= 0,
      bars: buildBars(hist.abs, 100, 28, 4),
    }
  }).filter(Boolean)
})

/** Population mini-chart for the demographic strip's "Аҳоли сони" tile.
 *  Renders a smooth Catmull-Rom-to-Bezier curve with an area fill underneath
 *  (instead of the previous straight polyline). Latest value from raqamlarda
 *  (38,24 млн asof 1.01.2026); 2024 is linear-interpolated. Delta is the
 *  cumulative 5-year growth (2021 → 2025) since population grows steadily
 *  rather than in measurable YoY steps. */
const popChart = computed(() => {
  const hist = UZ_MACRO_HISTORY.pop
  const interp = new Set(hist.interpolatedYears || [])
  const w = 100, h = 46, pad = 4
  const last = hist.abs[hist.abs.length - 1]
  const first = hist.abs.find((v) => v != null)
  const valid = hist.abs.filter((v) => v != null)
  const min = Math.min(...valid), max = Math.max(...valid)
  const range = max - min || 1
  const lastIdx = hist.abs.length - 1
  const points = hist.abs.map((v, i) => {
    if (v == null) return null
    const x = pad + (i / lastIdx) * (w - pad * 2)
    const y = h - pad - ((v - min) / range) * (h - pad * 2)
    return {
      x, y,
      year: UZ_MACRO_YEARS[i],
      isLast: i === lastIdx,
      isInterp: interp.has(UZ_MACRO_YEARS[i]),
    }
  }).filter(Boolean)

  // Catmull-Rom → cubic Bezier smoothing. Tension 1/6 produces a gentle
  // S-curve that doesn't overshoot above the highest point.
  let path = ''
  if (points.length >= 2) {
    path = `M ${points[0].x.toFixed(2)},${points[0].y.toFixed(2)}`
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i - 1] || points[i]
      const p1 = points[i]
      const p2 = points[i + 1]
      const p3 = points[i + 2] || p2
      const c1x = p1.x + (p2.x - p0.x) / 6
      const c1y = p1.y + (p2.y - p0.y) / 6
      const c2x = p2.x - (p3.x - p1.x) / 6
      const c2y = p2.y - (p3.y - p1.y) / 6
      path += ` C ${c1x.toFixed(2)},${c1y.toFixed(2)} ${c2x.toFixed(2)},${c2y.toFixed(2)} ${p2.x.toFixed(2)},${p2.y.toFixed(2)}`
    }
  }
  const areaPath = path
    ? `${path} L ${points[points.length - 1].x.toFixed(2)},${h} L ${points[0].x.toFixed(2)},${h} Z`
    : ''

  // Cumulative growth across the full series (2021 → 2025).
  const delta = (first != null && last != null && first > 0)
    ? ((last - first) / first) * 100
    : null
  const deltaStr = delta == null
    ? null
    : (delta >= 0 ? '+' : '') + delta.toFixed(1).replace('.', ',') + '%'

  return {
    valueStr: fmtTrln(last),
    path,
    areaPath,
    points,
    deltaStr,
    isPos: delta == null ? true : delta >= 0,
    width: w,
    height: h,
  }
})

const macroYears = UZ_MACRO_YEARS

const sortedRegions = computed(() => {
  const out = [...regionsEnriched.value]
  if (sortMode.value === 'pop') out.sort((a, b) => (b.pop || 0) - (a.pop || 0))
  else out.sort((a, b) => (b.districts_count || 0) - (a.districts_count || 0))
  return out
})

const railRows = computed(() => regionsEnriched.value.slice().sort((a, b) => a.name.localeCompare(b.name, 'ru')))

// Country rankings: rank-tier per region (top 25% / 25-60% / 60-85% / bottom 15%).
const rankingByCode = computed(() => {
  const m = new Map()
  for (const r of (store.countryRankings || [])) m.set(r.code, r)
  return m
})
const totalRanked = computed(() => (store.countryRankings || []).length || 14)

/** Country-level uses 3 groups split 40/40/20 per user request. Region/district
 *  pages keep their 4-band split because they have more polygons. */
function tierForRatio(ratio) {
  if (ratio == null) return null
  if (ratio <= 0.40) return 'lead'
  if (ratio <= 0.80) return 'mid'
  return 'low'
}
const TIER_COLOR = { lead: '#bfe5d4', mid: '#f5e3b8', low: '#eecccc' }
function tierFromRank(rank) {
  if (!rank || !totalRanked.value) return null
  return tierForRatio(rank / totalRanked.value)
}
function tierColor(rank) { return TIER_COLOR[tierFromRank(rank)] || '#e8eef7' }
function tierLabelClass(rank) {
  const t = tierFromRank(rank)
  if (t === 'lead') return 'high'
  if (t === 'mid')  return 'mid'
  return 'low'
}

const tierCounts = computed(() => {
  const c = { lead: 0, mid: 0, low: 0 }
  for (const r of (store.countryRankings || [])) {
    const t = tierFromRank(r.rank)
    if (t && t in c) c[t]++
  }
  return c
})

// Bar chart: 14 regions sorted by rank with score on x-axis.
const rankingChart = computed(() => {
  const arr = store.countryRankings || []
  if (!arr.length) return []
  const max = Math.max(...arr.map((r) => r.score || 0))
  const min = Math.min(...arr.map((r) => r.score || 0))
  const span = max - min || 1
  return arr.map((r) => ({
    code: r.code,
    name: r.name,
    score: r.score,
    rank: r.rank,
    width: 30 + ((r.score - min) / span) * 70,  // 30-100% so bars are always visible
    tier: tierFromRank(r.rank),
  }))
})

function rowFor(r) {
  const ranked = rankingByCode.value.get(r.code)
  return {
    key: r.code,
    name: r.name,
    sub: tFn('cerrV2.region.districtsCount', { n: r.districts_count }),
    badge: ranked ? `#${ranked.rank}` : (r.pop ? fmt.shortPop(r.pop) : '—'),
    badgeTone: ranked ? tierLabelClass(ranked.rank) : (r.hasCerr ? '' : 'low'),
    disabled: !r.hasCerr,
  }
}

function go(code) {
  router.push({ name: 'cerr-v2-region', params: { regionCode: code } })
}

// Inject scoped style overrides for the methodology panel from JS so we don't
// have to touch the global cerr-v2-theme.css. Vue auto-hoists this <style>
// block whether or not we use it here, so this is just a marker.

function getKey(f) { return String(f.properties.region_code) }
function getLabel(f) { return f.properties.region_name }
function getTooltip(f) {
  const code = Number(f.properties.region_code)
  const ranked = rankingByCode.value.get(code)
  return ranked
    ? `${f.properties.region_name} · #${ranked.rank} · ${ranked.score.toFixed(1)}`
    : f.properties.region_name
}
function selectable(k) {
  const r = regionsEnriched.value.find((x) => String(x.code) === String(k))
  return !!r?.hasCerr
}
function colorize(f) {
  const code = Number(f.properties.region_code)
  const ranked = rankingByCode.value.get(code)
  return tierColor(ranked?.rank)
}
</script>

<template>
  <div class="page with-rail">
    <div :style="{ display: 'flex', flexDirection: 'column', gap: '22px', minWidth: 0 }">
      <section class="hero hero-v2">
        <div class="hero-v2-head">
          <div class="hero-v2-l">
            <h2 class="hero-title">{{ $t('cerrV2.country.title') }}</h2>
          </div>
        </div>

        <div class="hero-v2-meta">
          <span class="hv2-meta-item"><CerrIcon name="pin" :size="12" /> {{ $t('cerrV2.country.area') }}</span>
          <span class="hv2-meta-sep" />
          <span class="hv2-meta-item"><CerrIcon name="info" :size="12" /> {{ $t('cerrV2.common.data2025') }}</span>
          <span class="hv2-meta-sep" />
          <span class="hv2-meta-item"><CerrIcon name="layers" :size="12" /> {{ $t('cerrV2.country.source') }}</span>
        </div>

        <div class="hero-v2-stats">
          <div v-for="s in heroStats" :key="s.key" :class="['hv2-stat', s.hasChart ? 'is-pop' : '']">
            <div class="hv2-stat-head">
              <span class="hv2-stat-ico"><CerrIcon :name="s.ico" :size="14" /></span>
              <div class="hv2-stat-label">{{ s.label }}</div>
              <span
                v-if="s.hasChart && popChart.deltaStr"
                :class="['hv2-pop-delta', popChart.isPos ? 'pos' : 'neg']"
              >{{ popChart.deltaStr }}</span>
            </div>
            <div class="hv2-stat-row">
              <span :class="['hv2-stat-val tabular', s.hasChart ? 'is-pop-num' : '']">{{ s.value }}</span>
              <span v-if="s.unit" class="hv2-stat-unit">{{ s.unit }}</span>
            </div>
            <div v-if="s.hasChart" class="hv2-stat-chart">
              <svg
                class="hv2-stat-line"
                :viewBox="`0 0 ${popChart.width} ${popChart.height}`"
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <defs>
                  <linearGradient id="popAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stop-color="#21b6ce" stop-opacity="0.55" />
                    <stop offset="100%" stop-color="#21b6ce" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <path v-if="popChart.areaPath" class="hv2-pop-area" :d="popChart.areaPath" />
                <path v-if="popChart.path"     class="hv2-pop-line" :d="popChart.path" />
              </svg>
              <div class="hv2-stat-axis">
                <span v-for="(y, i) in macroYears" :key="y" :class="['hv2-stat-tick', i === macroYears.length - 1 ? 'is-last' : '']">
                  {{ String(y).slice(2) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="heroMacro.length" class="hero-v2-macro-head">
          <span>{{ $t('cerrV2.country.macroHead') }}</span>
        </div>

        <div v-if="heroMacro.length" class="hero-v2-macro">
          <div v-for="m in heroMacro" :key="m.key" class="hv2-macro">
            <div class="hv2m-label">{{ m.label }}</div>
            <div class="hv2m-val-row">
              <span class="hv2m-val tabular">{{ m.absStr }}</span>
              <span class="hv2m-pct">трлн</span>
            </div>
            <div class="hv2m-chart">
              <svg
                class="hv2m-bars"
                viewBox="0 0 100 28"
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <rect
                  v-for="(b, i) in m.bars"
                  :key="i"
                  :class="['hv2m-bar', b.isLast ? 'is-last' : '', !b.hasValue ? 'is-empty' : '']"
                  :x="b.x"
                  :y="b.y"
                  :width="b.w"
                  :height="b.h"
                  rx="1"
                />
              </svg>
              <div class="hv2m-axis">
                <span v-for="(y, i) in macroYears" :key="y" :class="['hv2m-tick', i === macroYears.length - 1 ? 'is-last' : '']">
                  {{ String(y).slice(2) }}
                </span>
              </div>
            </div>
            <div class="hv2m-foot">
              <span v-if="m.deltaStr" :class="['hv2m-delta', m.isPos ? 'pos' : 'neg']">
                <span class="arr">{{ m.isPos ? '↑' : '↓' }}</span>
                {{ m.deltaStr }}%
              </span>
              <span class="hv2m-since">{{ $t('cerrV2.common.since2024') }}</span>
            </div>
          </div>
        </div>
      </section>

      <div class="section-h"><span>{{ $t('cerrV2.country.mapHint') }}</span></div>

      <section class="card map-card">
        <div class="map-grid">
          <EntityMap
            :geo="store.countryGeo"
            :width="620"
            :height="380"
            :get-key="getKey"
            :get-label="getLabel"
            :get-tooltip="getTooltip"
            :colorize="colorize"
            :selectable="selectable"
            :title="$t('cerrV2.country.title')"
            :subtitle="$t('cerrV2.country.mapSub', { r: 14, d: aggregates.districts })"
            @select="(k) => go(Number(k))"
          />
          <div class="map-side">
            <div class="map-side-h">{{ $t('cerrV2.country.rating.title') }}</div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#bfe5d4' }" />
              <span class="lbl">
                <b>{{ $t('cerrV2.country.rating.lead') }}</b>
                <span class="sub">{{ $t('cerrV2.country.rating.leadDesc') }}</span>
              </span>
              <span class="n tabular">{{ tierCounts.lead }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f5e3b8' }" />
              <span class="lbl">
                <b>{{ $t('cerrV2.country.rating.mid') }}</b>
                <span class="sub">{{ $t('cerrV2.country.rating.midDesc') }}</span>
              </span>
              <span class="n tabular">{{ tierCounts.mid }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#eecccc' }" />
              <span class="lbl">
                <b>{{ $t('cerrV2.country.rating.low') }}</b>
                <span class="sub">{{ $t('cerrV2.country.rating.lowDesc') }}</span>
              </span>
              <span class="n tabular">{{ tierCounts.low }}</span>
            </div>
            <div class="map-focus">
              <div class="eye">{{ $t('cerrV2.country.rating.calcHeading') }}</div>
              <div class="hint">
                {{ $t('cerrV2.country.rating.calcExplain') }}
                <br /><br />
                <b>{{ $t('cerrV2.country.rating.calcLabel') }}:</b>
                {{ $t('cerrV2.country.rating.calcChain') }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="rankingChart.length" class="card featured">
        <h3 class="card-title">
          <span class="ico-tile"><CerrIcon name="award" :size="14" /></span>
          {{ $t('cerrV2.country.rankingHead') }}
          <span class="card-title-end">{{ $t('cerrV2.common.moreBetter') }}</span>
        </h3>
        <div class="bar-chart">
          <button
            v-for="d in rankingChart"
            :key="d.code"
            class="bar-row"
            :style="{ background: 'none', border: 0, padding: '5px 0', width: '100%', textAlign: 'left', cursor: 'pointer' }"
            @click="go(d.code)"
          >
            <div class="nm">{{ d.name }}</div>
            <div class="track">
              <i :style="{ width: `${d.width}%`, background: TIER_COLOR[d.tier] || 'var(--brand-navy-bright)' }" />
            </div>
            <div class="rank">{{ d.score.toFixed(1) }}</div>
          </button>
        </div>
      </section>

      <div class="section-h"><span>{{ $t('cerrV2.country.regionsHead', { n: aggregates.covered }) }}</span></div>

      <div class="region-grid">
        <button
          v-for="r in sortedRegions"
          :key="r.code"
          :class="['region-card', !r.hasCerr ? 'disabled' : '']"
          :disabled="!r.hasCerr"
          @click="r.hasCerr && go(r.code)"
        >
          <span v-if="!r.hasCerr" class="badge">нет данных</span>
          <div class="name">{{ r.name }}</div>
          <div class="meta">
            <span>{{ $t('cerrV2.country.districtsShort', { n: r.districts_count }) }}</span>
            <span :style="{ color: 'var(--text-faint)' }">·</span>
            <span>{{ $t('cerrV2.country.mahallasShort', { n: fmt.num(r.mahalla_count) }) }}</span>
          </div>
          <div class="pop">
            <span class="v tabular">{{ r.pop ? (r.pop / 1e6).toFixed(2).replace('.', ',') : '—' }}</span>
            <span class="u">{{ $t('cerrV2.country.mlnPeople') }}</span>
          </div>
          <div class="bar">
            <i :style="{ width: `${Math.min(100, ((r.pop || 0) / 4.5e6) * 100)}%` }" />
          </div>
        </button>
      </div>

      <MacroPanel :data="store.raqamlarda.national" />
    </div>

    <SidebarRail
      :title="$t('nav.regionsAnalytics')"
      :count="regionsEnriched.length"
      :items="railRows"
      :row-for="rowFor"
      :search-placeholder="$t('cerrV2.region.searchDistrict')"
      :meta-right="$t('cerrV2.common.withData', { n: regionsEnriched.filter(r => r.hasCerr).length })"
      @select="(r) => r.hasCerr && go(r.code)"
    >
      <template #header-top><NavStepper /></template>
    </SidebarRail>
  </div>
</template>

<style>
/* Methodology panel: stack a bold tier name + subtitle inside .map-tier > .lbl,
 * and let the methodology block be a bit taller so the explanation fits. */
.cerr-v2-scope .map-tier .lbl b {
  display: block;
  font-size: 13px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.005em;
}
.cerr-v2-scope .map-tier .lbl .sub {
  display: block;
  font-size: 10.5px;
  font-weight: 600;
  color: var(--text-soft);
  margin-top: 1px;
  letter-spacing: 0;
}
.cerr-v2-scope .map-tier {
  align-items: flex-start;
}
.cerr-v2-scope .map-focus .hint {
  font-size: 11.5px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  opacity: 1;
  margin-top: 6px;
}
.cerr-v2-scope .map-focus .hint b {
  color: #fff;
  font-weight: 800;
}

/* ============== Hero v2 — compact dashboard hero ============== */
.cerr-v2-scope .hero.hero-v2 {
  position: relative;
  background:
    radial-gradient(circle at 88% -10%, rgba(33,182,206,.35), transparent 50%),
    radial-gradient(circle at 100% 100%, rgba(0,84,166,.5), transparent 60%),
    linear-gradient(135deg, #001b3d 0%, #003D7C 65%, #0054A6 100%);
  color: #fff;
  border-radius: 20px;
  /* tighter outer padding + smaller section gap → ~30 px shorter overall
   * without shrinking any individual content (title, stats, charts stay). */
  padding: 18px 28px 16px;
  box-shadow: 0 20px 50px -20px rgba(0,27,61,.5);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.cerr-v2-scope .hero-v2 > * { position: relative; }

.cerr-v2-scope .hero-v2-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 32px;
  align-items: start;
}
.cerr-v2-scope .hero-v2-l { min-width: 0; }
.cerr-v2-scope .hero-v2 .hero-title {
  font-size: clamp(34px, 3.6vw, 46px);
  font-weight: 900;
  letter-spacing: -.032em;
  line-height: 1;
  margin: 0;
  color: #fff;
}

.cerr-v2-scope .hero-v2-meta {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,.6);
}
.cerr-v2-scope .hv2-meta-item { display: inline-flex; align-items: center; gap: 6px; }
.cerr-v2-scope .hv2-meta-sep  { width: 3px; height: 3px; border-radius: 50%; background: rgba(255,255,255,.3); }

/* Scoped to the country hero only (`hero-v2` without `mahalla-hero`).
 * Otherwise this 4-column rule leaks onto the mahalla / region / district
 * hero stats strip (which also has class `hero-v2-stats`) and the 6-tile
 * layout wraps into 4 + 2 depending on cascade order. */
.cerr-v2-scope .hero-v2:not(.mahalla-hero) .hero-v2-stats {
  /* Concentrated on the left — strip takes only what it needs (≈ 70 % of
   * the hero) instead of stretching to full width. The macro grid below
   * stays full-width as before. */
  display: grid; grid-template-columns: repeat(4, minmax(0, 220px)); gap: 0;
  border-top: 1px solid rgba(255,255,255,.12);
  border-bottom: 1px solid rgba(255,255,255,.12);
  padding: 10px 0;
}
.cerr-v2-scope .hv2-stat {
  padding: 0 22px; border-left: 1px solid rgba(255,255,255,.10);
  display: flex; flex-direction: column; gap: 6px; min-width: 0;
}
.cerr-v2-scope .hv2-stat:first-child { border-left: none; padding-left: 0; }
.cerr-v2-scope .hv2-stat-head { display: flex; align-items: center; gap: 8px; }
.cerr-v2-scope .hv2-stat-ico  {
  width: 24px; height: 24px; border-radius: 6px;
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.10);
  display: grid; place-items: center; color: rgba(255,255,255,.78); flex-shrink: 0;
}
.cerr-v2-scope .hv2-stat-label {
  font-size: 10.5px; font-weight: 700; letter-spacing: .14em;
  text-transform: uppercase; color: rgba(255,255,255,.52);
}
.cerr-v2-scope .hv2-stat-row  { display: flex; align-items: baseline; gap: 8px; flex-wrap: nowrap; min-width: 0; }
.cerr-v2-scope .hv2-stat-val  {
  font-size: clamp(30px, 2.8vw, 38px); font-weight: 800; letter-spacing: -.035em;
  line-height: .95; color: #fff; white-space: nowrap; font-variant-numeric: tabular-nums;
}
.cerr-v2-scope .hv2-stat-unit { font-size: 12px; font-weight: 600; color: rgba(255,255,255,.5); white-space: nowrap; }

.cerr-v2-scope .hv2-stat-chart { display: flex; flex-direction: column; gap: 2px; margin-top: 4px; }
.cerr-v2-scope .hv2-stat-line  { width: 100%; height: 46px; display: block; overflow: visible; }
.cerr-v2-scope .hv2-pop-line {
  fill: none;
  stroke: #34d399;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.cerr-v2-scope .hv2-pop-area { fill: url(#popAreaGrad); stroke: none; }

/* Population value rendered green, matching the +delta chip and the
 * curve stroke. Other stat tiles keep the white default. */
.cerr-v2-scope .hv2-stat-val.is-pop-num { color: #34d399; }

/* Delta chip ('+13,5%') aligned right inside the stat head. */
.cerr-v2-scope .hv2-pop-delta {
  margin-left: auto;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: -.005em;
  padding: 3px 9px;
  border-radius: 999px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  border: 1px solid transparent;
}
.cerr-v2-scope .hv2-pop-delta.pos {
  background: rgba(52, 211, 153, .14);
  border-color: rgba(52, 211, 153, .35);
  color: #34d399;
}
.cerr-v2-scope .hv2-pop-delta.neg {
  background: rgba(248, 113, 113, .14);
  border-color: rgba(248, 113, 113, .35);
  color: #f87171;
}

.cerr-v2-scope .hv2-stat-axis  {
  display: flex; justify-content: space-between;
  font-size: 9px; font-weight: 700; letter-spacing: .04em;
  color: rgba(255, 255, 255, .42);
  font-variant-numeric: tabular-nums;
  padding: 0 1px;
}
.cerr-v2-scope .hv2-stat-tick.is-last { color: #34d399; }

.cerr-v2-scope .hero-v2-macro-head {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 10.5px; font-weight: 700; letter-spacing: .14em;
  text-transform: uppercase; color: rgba(255,255,255,.5); margin-top: 2px;
}
.cerr-v2-scope .hero-v2-macro-head .hv2m-src { letter-spacing: .06em; color: rgba(255,255,255,.4); font-weight: 600; }

.cerr-v2-scope .hero-v2-macro { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.cerr-v2-scope .hv2-macro {
  padding: 12px 14px 10px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 10px;
  display: flex; flex-direction: column; gap: 6px; min-width: 0;
}
.cerr-v2-scope .hv2m-label {
  font-size: 10px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  color: rgba(255,255,255,.62); line-height: 1.3; min-height: 26px;
  display: flex; align-items: flex-start;
}
.cerr-v2-scope .hv2m-val-row { display: flex; align-items: baseline; gap: 4px; flex-wrap: nowrap; min-width: 0; }
.cerr-v2-scope .hv2m-val     {
  font-size: clamp(20px, 1.9vw, 24px); font-weight: 800; letter-spacing: -.025em; line-height: 1;
  color: #fff; font-variant-numeric: tabular-nums; white-space: nowrap;
}
.cerr-v2-scope .hv2m-pct     { font-size: 12px; font-weight: 700; color: rgba(255,255,255,.55); }

.cerr-v2-scope .hv2m-chart {
  margin-top: 2px;
  display: flex; flex-direction: column; gap: 2px;
}
.cerr-v2-scope .hv2m-bars {
  width: 100%; height: 28px; display: block; overflow: visible;
}
.cerr-v2-scope .hv2m-bar {
  fill: rgba(255, 255, 255, .26);
  transition: fill .15s ease;
}
.cerr-v2-scope .hv2m-bar.is-empty { fill: rgba(255, 255, 255, .12); }
.cerr-v2-scope .hv2m-bar.is-last  { fill: #34d399; }
.cerr-v2-scope .hv2m-axis {
  display: flex; justify-content: space-between;
  font-size: 9px; font-weight: 700; letter-spacing: .04em;
  color: rgba(255, 255, 255, .42);
  font-variant-numeric: tabular-nums;
  padding: 0 1px;
}
.cerr-v2-scope .hv2m-tick.is-last { color: #34d399; }

.cerr-v2-scope .hv2m-foot    { display: flex; align-items: baseline; gap: 8px; margin-top: 2px; }
.cerr-v2-scope .hv2m-delta   {
  font-size: 13px; font-weight: 800; font-variant-numeric: tabular-nums;
  letter-spacing: -.01em;
  display: inline-flex; align-items: baseline; gap: 2px; white-space: nowrap;
}
.cerr-v2-scope .hv2m-delta.pos { color: #34d399; }
.cerr-v2-scope .hv2m-delta.neg { color: #f87171; }
.cerr-v2-scope .hv2m-delta .arr { font-size: 11px; font-weight: 900; line-height: 1; }
.cerr-v2-scope .hv2m-since      { font-size: 11px; font-weight: 600; color: rgba(255,255,255,.42); white-space: nowrap; }

@media (max-width: 1100px) {
  .cerr-v2-scope .hero-v2-macro { grid-template-columns: repeat(3, 1fr); }
  .cerr-v2-scope .hero-v2-stats { grid-template-columns: repeat(2, 1fr); row-gap: 18px; }
  .cerr-v2-scope .hv2-stat:nth-child(3) { border-left: none; padding-left: 0; }
}
@media (max-width: 720px) {
  .cerr-v2-scope .hero-v2-head  { grid-template-columns: 1fr; }
  .cerr-v2-scope .hero-v2-macro { grid-template-columns: repeat(2, 1fr); }
  .cerr-v2-scope .hero-v2-stats { grid-template-columns: 1fr; }
  .cerr-v2-scope .hv2-stat      { border-left: none; padding-left: 0; }
}
</style>
