<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import FerganaMap from '@/components/FerganaMap.vue'
import SamarqandMap from '@/components/SamarqandMap.vue'
import { districts as ferganaDistricts, districtByKey as ferganaByKey } from '@/data/districts'
import { samarqandDistricts, samarqandByKey } from '@/data/samarqand'
import {
  buildDistrictAnalytics,
  buildFerganaOverview,
  buildSamarqandOverview,
} from '@/data/districtAnalytics'
import '@/assets/districtAnalytics.css'

const { t, te, tm } = useI18n()
const route = useRoute()
const router = useRouter()

const region = computed(() => (route.query.region === 'samarqand' ? 'samarqand' : 'fergana'))
const regionDistricts = computed(() =>
  region.value === 'samarqand' ? samarqandDistricts : ferganaDistricts,
)
const regionDistrictByKey = computed(() =>
  region.value === 'samarqand' ? samarqandByKey : ferganaByKey,
)
const RegionMap = computed(() => (region.value === 'samarqand' ? SamarqandMap : FerganaMap))

const districtKey = computed(() => {
  const k = route.query.district
  // Drill-down still works for Fergana pilot keys + samarqand_region pseudo-entry.
  if (k && ferganaByKey[k]) return k
  return null
})
const selectedDistrict = computed(() => (districtKey.value ? ferganaByKey[districtKey.value] : null))
const overview = computed(() =>
  region.value === 'samarqand' ? buildSamarqandOverview() : buildFerganaOverview(),
)

// Map selection mirror — both overview-map click and list click set the route.
const mapSelection = ref(districtKey.value)
watch(districtKey, (v) => (mapSelection.value = v))
watch(mapSelection, (v) => {
  if (v !== districtKey.value) selectDistrict(v)
})

const AVAILABLE_DISTRICTS = new Set(['fargona_city', 'margilon_city', 'samarqand_region'])
const unavailableToast = ref(null)

function selectDistrict(key) {
  if (key && !AVAILABLE_DISTRICTS.has(key)) {
    mapSelection.value = null
    unavailableToast.value = true
    setTimeout(() => { unavailableToast.value = null }, 3000)
    return
  }
  const query = key ? { ...route.query, district: key } : { ...route.query }
  if (!key) delete query.district
  router.push({ path: route.path, query })
}

// Drill-down analytics (null in overview mode)
const analytics = computed(() =>
  districtKey.value ? buildDistrictAnalytics(districtKey.value, t) : null,
)

const title = computed(() =>
  districtKey.value
    ? t(`districtsList.${districtKey.value}`)
    : t(`district.overviewTitle.${region.value}`),
)

const tabs = [
  { id: 'economic', labelKey: 'district.tabs.economic', num: '01', icon: 'finance' },
  { id: 'infra', labelKey: 'district.tabs.infra', num: '02', icon: 'hub' },
  { id: 'population', labelKey: 'district.tabs.population', num: '03', icon: 'groups' },
  { id: 'mahalla', labelKey: 'district.tabs.mahalla', num: '04', icon: 'storefront' },
  { id: 'opportunities', labelKey: 'district.tabs.opportunities', num: '05', icon: 'trending_up' },
  { id: 'summary', labelKey: 'district.tabs.summary', num: '06', icon: 'auto_awesome' },
]
const activeTab = ref('economic')
const activeTabMeta = computed(() => tabs.find((x) => x.id === activeTab.value))

// Split districts by kind for overview list (filtered to current region)
const cityList = computed(() => regionDistricts.value.filter((d) => d.kind === 'city'))
const districtList = computed(() => regionDistricts.value.filter((d) => d.kind === 'district'))

// ========== Drill-down chart configs (only when a district is selected) ==========
const grpTrendData = computed(() => {
  if (!analytics.value) return null
  const h = analytics.value.economic.history
  const datasets = [
    { label: t('district.legends.industry'), data: h.map((r) => r.industry), borderColor: '#003D7C', backgroundColor: 'rgba(0,61,124,.10)', borderWidth: 3, tension: 0.4, fill: true, pointRadius: 4, pointHoverRadius: 6 },
    { label: t('district.legends.invest'),   data: h.map((r) => r.invest),   borderColor: '#F59E0B', backgroundColor: 'rgba(245,158,11,.10)', borderWidth: 3, borderDash: [6, 4], tension: 0.4, fill: false, pointRadius: 4, pointHoverRadius: 6 },
  ]
  if (h[0]?.services != null) {
    datasets.push({
      label: t('district.legends.services'), data: h.map((r) => r.services),
      borderColor: '#059669', backgroundColor: 'rgba(5,150,105,.10)',
      borderWidth: 3, tension: 0.4, fill: false, pointRadius: 4, pointHoverRadius: 6,
    })
  }
  return { labels: h.map((r) => r.year), datasets }
})
const grpTrendOpts = {
  plugins: { legend: { position: 'bottom', labels: { font: { size: 12, weight: 600 }, boxWidth: 12, padding: 14 } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 12 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 12 } } },
  },
}

const sectorsData = computed(() => {
  if (!analytics.value || !analytics.value.economic.sectors) return null
  return {
    labels: analytics.value.economic.sectors.map((s) => s.name),
    datasets: [{ data: analytics.value.economic.sectors.map((s) => parseFloat(s.percent)), backgroundColor: analytics.value.economic.sectors.map((s) => s.color), borderWidth: 0, hoverOffset: 8 }],
  }
})
const sectorsOpts = {
  cutout: '65%',
  plugins: { legend: { position: 'bottom', labels: { font: { size: 12, weight: 600 }, boxWidth: 10, padding: 10 } } },
}

const laborData = computed(() => {
  if (!analytics.value) return null
  const rows = analytics.value.population.laborTrend
  return {
    labels: rows.map((r) => r.year),
    datasets: [
      { label: t('district.legends.formal'), data: rows.map((r) => r.formal), backgroundColor: '#34D399' },
      { label: t('district.legends.informal'), data: rows.map((r) => r.informal), backgroundColor: '#60A5FA' },
      { label: t('district.legends.abroad'), data: rows.map((r) => r.abroad), backgroundColor: '#FBBF24' },
      { label: t('district.legends.unemployed'), data: rows.map((r) => r.unemployed), backgroundColor: '#DC2626' },
    ],
  }
})
const laborOpts = {
  plugins: { legend: { position: 'bottom', labels: { font: { size: 12, weight: 600 }, boxWidth: 10, padding: 12 } } },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { font: { size: 12 } } },
    y: { stacked: true, grid: { color: '#F0F4FA' }, ticks: { font: { size: 12 } } },
  },
}

const unemploymentData = computed(() => {
  if (!analytics.value || !analytics.value.population.unemploymentTrend) return null
  return {
    labels: analytics.value.population.unemploymentTrend.map((r) => r.year),
    datasets: [{
      label: t('district.legends.unemploymentPct'),
      data: analytics.value.population.unemploymentTrend.map((r) => r.value),
      borderColor: '#DC2626', backgroundColor: 'rgba(220,38,38,.12)', borderWidth: 3, tension: 0.35, fill: true, pointRadius: 5, pointHoverRadius: 7,
    }],
  }
})
const unemploymentOpts = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 12 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 12 } } },
  },
}

// Population history (verified, only for districts with rd.populationFiveYear)
const populationHistoryData = computed(() => {
  if (!analytics.value?.population?.history) return null
  const h = analytics.value.population.history
  return {
    labels: h.labels,
    datasets: [
      {
        label: t('district.cards.populationHistoryLegend'),
        data: h.values,
        borderColor: '#003D7C',
        backgroundColor: 'rgba(0,61,124,0.10)',
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
      },
    ],
  }
})
const populationHistoryOpts = {
  plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${c.parsed.y.toFixed(1)} тыс. чел.` } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 12, weight: '600' } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 12 }, callback: (v) => `${v} k` } },
  },
}

// Vital statistics (verified, births vs deaths 2021-2025)
const vitalStatsData = computed(() => {
  if (!analytics.value?.population?.vitalStats) return null
  const v = analytics.value.population.vitalStats
  return {
    labels: v.historyLabels,
    datasets: [
      { label: t('district.cards.vitalBirths'), data: v.birthsHistory, backgroundColor: 'rgba(5,150,105,0.85)', borderRadius: 4, barPercentage: 0.7 },
      { label: t('district.cards.vitalDeaths'), data: v.deathsHistory, backgroundColor: 'rgba(220,38,38,0.85)', borderRadius: 4, barPercentage: 0.7 },
    ],
  }
})
const vitalStatsOpts = {
  plugins: { legend: { position: 'bottom', labels: { font: { size: 12, weight: '600' } } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 12, weight: '600' } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 11 }, callback: (v) => v.toLocaleString('ru-RU') } },
  },
}

// Age distribution (verified, 17 brackets, year-end 2025)
const ageGroupsData = computed(() => {
  if (!analytics.value?.population?.ageGroups) return null
  const a = analytics.value.population.ageGroups
  return {
    labels: a.labels,
    datasets: [
      {
        label: t('district.cards.ageGroupsLegend'),
        data: a.values,
        backgroundColor: 'rgba(0,84,166,0.85)',
        borderRadius: 4,
        borderSkipped: false,
        barPercentage: 0.85,
      },
    ],
  }
})
const ageGroupsOpts = {
  plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => c.parsed.y.toLocaleString('ru-RU') + ' чел.' } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 11, weight: '600' } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 11 }, callback: (v) => `${(v / 1000).toFixed(0)}k` } },
  },
}

const radarPoints = computed(() => {
  if (!analytics.value) return null
  const axes = analytics.value.summary.radar
  const cx = 140, cy = 140, r = 105
  const angles = axes.map((_, i) => (Math.PI * 2 * i) / axes.length - Math.PI / 2)
  const toPoint = (angle, value) => {
    const p = (value / 10) * r
    return [cx + Math.cos(angle) * p, cy + Math.sin(angle) * p]
  }
  return {
    labels: axes.map((a, i) => ({
      x: cx + Math.cos(angles[i]) * (r + 22),
      y: cy + Math.sin(angles[i]) * (r + 22),
      name: a.axis, value: a.value,
    })),
    regionPoly: axes.map((a, i) => toPoint(angles[i], parseFloat(a.value))).map(([x, y]) => `${x},${y}`).join(' '),
    provincialPoly: axes.map((a, i) => toPoint(angles[i], parseFloat(a.provincial))).map(([x, y]) => `${x},${y}`).join(' '),
    regionDots: axes.map((a, i) => { const [x, y] = toPoint(angles[i], parseFloat(a.value)); return { x, y } }),
  }
})

const threatLevelClass = (level) => {
  if (level === t('regionAnalytics.priority.high')) return 'bg-red-600 text-white'
  if (level === t('regionAnalytics.priority.medium')) return 'bg-amber-500 text-white'
  return 'bg-slate-400 text-white'
}

// Static AI analysis per district + tab — pre-written from verified PDFs.
// Returns null when no analysis text exists for the current district/tab,
// so the section is hidden rather than showing fallback boilerplate.
const aiAnalysis = computed(() => {
  if (!districtKey.value) return null
  const path = `district.aiAnalysis.${districtKey.value}.${activeTab.value}`
  if (!te(`${path}.title`)) return null
  const insights = tm(`${path}.insights`)
  const risks = tm(`${path}.risks`)
  return {
    title: t(`${path}.title`),
    summary: t(`${path}.summary`),
    insights: Array.isArray(insights) ? insights : [],
    risks: Array.isArray(risks) ? risks : [],
  }
})

// City-level AI banner — compact recommendation shown at the top of the
// drill-down page, above the tabs. Drawn from district.aiAnalysis.<key>.overall.
const aiOverall = computed(() => {
  if (!districtKey.value) return null
  const path = `district.aiAnalysis.${districtKey.value}.overall`
  if (!te(`${path}.title`)) return null
  const tags = tm(`${path}.tags`)
  return {
    title: t(`${path}.title`),
    summary: t(`${path}.summary`),
    tags: Array.isArray(tags) ? tags : [],
  }
})

</script>

<template>
  <div>
  <section class="p-6 lg:p-8 space-y-8 da-root">
    <!-- Breadcrumb strip -->
    <div class="flex items-center gap-2 text-primary font-bold tracking-wide text-xs uppercase flex-wrap">
      <AppIcon name="location_on" class="text-sm" />
      <template v-if="districtKey">
        <button
          type="button"
          class="hover:underline cursor-pointer"
          @click="selectDistrict(null)"
        >{{ t(`district.overviewTitle.${region}`) }}</button>
        <span class="text-slate-400">/</span>
        <span class="text-slate-700">{{ t(`district.kind.${selectedDistrict.kind}`) }}</span>
        <span class="text-slate-400">/</span>
        <span>{{ t(`districtsList.${districtKey}`) }}</span>
      </template>
      <template v-else>
        <span>{{ t(`district.overviewTitle.${region}`) }}</span>
      </template>
    </div>

    <!-- =============== OVERVIEW MODE =============== -->
    <template v-if="!districtKey">
      <!-- Executive brief for the active region -->
      <div class="da-brief">
        <div class="relative z-10">
          <div class="sub-header-eyebrow" style="color:#93C5FD;font-size:15px">
            {{ t(`district.overviewEyebrow.${region}`) }}
          </div>
          <h2 class="font-black leading-[1.05] mt-3" style="font-family:'Manrope',sans-serif;letter-spacing:-0.02em;font-size:clamp(1.75rem,4.2vw,3.25rem)">
            {{ t(`district.overviewTitle.${region}`) }}
          </h2>
          <p class="text-blue-100/85 max-w-3xl mt-5 leading-relaxed" style="font-size:clamp(0.95rem,1.2vw,1.15rem)">
            {{ t(`district.overviewIntro.${region}`) }}
          </p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-9 relative z-10">
          <div class="da-brief-kpi">
            <div class="da-brief-kpi-label">{{ t('district.brief.population') }}</div>
            <div class="da-brief-kpi-value">
              {{ (overview.totalPopulationK / 1000).toFixed(2) }}
            </div>
            <div class="da-brief-kpi-unit mt-3">{{ t('district.units.mlnPeople') }}</div>
          </div>
          <div class="da-brief-kpi">
            <div class="da-brief-kpi-label">{{ t('district.brief.grpEstimate') }}</div>
            <div class="da-brief-kpi-value">{{ overview.totalGrpBln.toLocaleString('ru-RU') }}</div>
            <div class="da-brief-kpi-unit mt-3">{{ t('district.units.bnSum') }}</div>
          </div>
          <div class="da-brief-kpi">
            <div class="da-brief-kpi-label">{{ t('district.brief.avgGrowth') }}</div>
            <div class="da-brief-kpi-value" style="color:#A7F3D0">+{{ overview.avgGrowth.toFixed(1) }}%</div>
            <div class="da-brief-kpi-unit mt-3">{{ t('district.units.year2025') }}</div>
          </div>
          <div class="da-brief-kpi">
            <div class="da-brief-kpi-label">{{ t('district.brief.cities') }}</div>
            <div class="da-brief-kpi-value">{{ overview.cities }}</div>
            <div class="da-brief-kpi-unit mt-3">{{ t('district.units.regCities') }}</div>
          </div>
          <div class="da-brief-kpi">
            <div class="da-brief-kpi-label">{{ t('district.brief.districts') }}</div>
            <div class="da-brief-kpi-value">{{ overview.districts }}</div>
            <div class="da-brief-kpi-unit mt-3">{{ t('district.units.ruralDistricts') }}</div>
          </div>
        </div>
      </div>

      <!-- Map + list -->
      <div class="grid grid-cols-12 gap-6">
        <div class="col-span-12 lg:col-span-8">
          <div class="da-card-title mb-3">
            <span class="dot"></span>{{ t(`district.mapTitle${region === 'samarqand' ? 'Samarqand' : ''}`) }}
          </div>
          <component :is="RegionMap" v-model="mapSelection" @select="selectDistrict" />
        </div>

        <aside class="col-span-12 lg:col-span-4 space-y-5">
          <!-- Cities -->
          <div class="da-card" style="padding:18px">
            <div class="flex items-center justify-between mb-3">
              <div class="da-card-title"><span class="dot"></span>{{ t('district.listCities') }}</div>
              <span class="text-[11px] font-bold text-primary bg-primary-fixed px-2 py-0.5 rounded-full">{{ cityList.length }}</span>
            </div>
            <ul class="space-y-1">
              <li v-for="c in cityList" :key="c.key">
                <button
                  type="button"
                  class="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary-fixed transition-colors text-left"
                  :class="{ 'opacity-40': !AVAILABLE_DISTRICTS.has(c.key) }"
                  @click="selectDistrict(c.key)"
                >
                  <span class="w-2 h-2 rounded-full flex-shrink-0" style="background:#003D7C"></span>
                  <span class="flex-1 text-[13px] font-semibold truncate">{{ t(`districtsList.${c.key}`) }}</span>
                  <span class="text-[10px] font-bold text-primary bg-primary-fixed px-1.5 py-0.5 rounded">{{ c.population }}k</span>
                </button>
              </li>
            </ul>
          </div>

          <!-- Districts -->
          <div class="da-card" style="padding:18px">
            <div class="flex items-center justify-between mb-3">
              <div class="da-card-title"><span class="dot" style="background:#0054A6"></span>{{ t('district.listDistricts') }}</div>
              <span class="text-[11px] font-bold text-primary bg-primary-fixed px-2 py-0.5 rounded-full">{{ districtList.length }}</span>
            </div>
            <ul class="space-y-1 max-h-[420px] overflow-y-auto">
              <li v-for="d in districtList" :key="d.key">
                <button
                  type="button"
                  class="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary-fixed transition-colors text-left"
                  :class="{ 'opacity-40': !AVAILABLE_DISTRICTS.has(d.key) }"
                  @click="selectDistrict(d.key)"
                >
                  <span class="w-2 h-2 rounded-full flex-shrink-0" style="background:#7FB5E6"></span>
                  <span class="flex-1 text-[13px] font-semibold truncate">{{ t(`districtsList.${d.key}`) }}</span>
                  <span class="text-[10px] font-bold text-primary bg-primary-fixed px-1.5 py-0.5 rounded">{{ d.population }}k</span>
                </button>
              </li>
            </ul>
          </div>
        </aside>
      </div>

    </template>

    <!-- =============== DRILL-DOWN MODE =============== -->
    <template v-else-if="analytics">
      <button
        type="button"
        class="text-sm font-bold text-primary hover:underline flex items-center gap-1"
        @click="selectDistrict(null)"
      >
        {{ t('district.backToRegion') }}
      </button>

      <!-- Executive Brief -->
      <div class="da-brief">
        <div class="relative z-10">
          <div class="sub-header-eyebrow" style="color:#93C5FD;font-size:13px;letter-spacing:0.18em">
            {{ t('district.briefDrill.eyebrow') }} · {{ t(`district.kind.${selectedDistrict.kind}`).toUpperCase() }}
          </div>
          <h2 class="font-black leading-[1.02] mt-3" style="font-family:'Manrope',sans-serif;letter-spacing:-0.025em;font-size:clamp(1.75rem,4.2vw,3.25rem)">
            {{ title }}
          </h2>
          <p class="text-blue-100/85 max-w-3xl mt-5 leading-relaxed font-semibold" style="font-size:clamp(0.95rem,1.2vw,1.15rem)">
            {{ selectedDistrict.population }} {{ t('district.units.thousandResidents') }} · {{ selectedDistrict.area.toLocaleString('ru-RU') }} {{ t('district.units.kmSq') }} ·
            {{ t('district.units.density') }} {{ Math.round((selectedDistrict.population * 1000) / selectedDistrict.area).toLocaleString('ru-RU') }} {{ t('district.units.peoplePerKmSq') }}
          </p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-8 relative z-10">
          <div
            v-for="kpi in analytics.brief.kpis"
            :key="kpi.label"
            class="da-brief-kpi"
          >
            <div class="da-brief-kpi-label">{{ kpi.label }}</div>
            <div class="da-brief-kpi-value">{{ kpi.value }}</div>
            <div class="da-brief-kpi-foot">
              <span v-if="kpi.unit" class="da-brief-kpi-unit">{{ kpi.unit }}</span>
              <span class="da-brief-kpi-delta" :class="kpi.tone === 'green' ? 'tone-green' : 'tone-blue'">{{ kpi.delta }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Verified 2026 plan -->
      <div v-if="analytics.plan2026" class="da-card">
        <div class="flex items-start justify-between flex-wrap gap-3">
          <div>
            <div class="da-card-title"><span class="dot" style="background:#0054A6"></span>{{ t('district.cards.plan2026Title') }}</div>
            <div class="da-card-sub">{{ t('district.cards.plan2026Sub') }}</div>
          </div>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mt-5">
          <div class="da-kpi">
            <div class="da-kpi-label">{{ t('district.cards.plan2026Infra') }}</div>
            <div class="da-kpi-value">{{ analytics.plan2026.infraBudgetBln }}</div>
            <div class="da-kpi-sub">{{ t('district.cards.bnSum') }}</div>
          </div>
          <div class="da-kpi">
            <div class="da-kpi-label">{{ t('district.cards.plan2026Tourism') }}</div>
            <div class="da-kpi-value">{{ analytics.plan2026.tourismVisitorsK }}</div>
            <div class="da-kpi-sub">{{ t('district.cards.plan2026Visitors') }}</div>
          </div>
          <div class="da-kpi">
            <div class="da-kpi-label">{{ t('district.cards.plan2026Jobs') }}</div>
            <div class="da-kpi-value">{{ analytics.plan2026.jobs.toLocaleString('ru-RU') }}</div>
            <div class="da-kpi-sub">{{ t('district.cards.jobs') }}</div>
          </div>
          <div class="da-kpi">
            <div class="da-kpi-label">{{ t('district.cards.plan2026Preschools') }}</div>
            <div class="da-kpi-value">{{ analytics.plan2026.preschools }}</div>
            <div class="da-kpi-sub">{{ analytics.plan2026.preschoolPlaces.toLocaleString('ru-RU') }} {{ t('district.cards.plan2026PreschoolPlaces') }}</div>
          </div>
        </div>
      </div>

      <!-- City-level AI banner — overall takeaways, shown only for districts
           with curated district.aiAnalysis.<key>.overall content -->
      <div v-if="aiOverall" class="da-ai-banner">
        <div class="da-ai-banner-icon">
          <AppIcon name="auto_awesome" filled class="!text-[24px] text-white" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-1.5 flex-wrap">
            <div class="da-ai-banner-title">{{ aiOverall.title }}</div>
            <span class="da-ai-banner-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>
          <p class="da-ai-banner-summary">{{ aiOverall.summary }}</p>
          <div v-if="aiOverall.tags.length" class="flex gap-2 mt-3 flex-wrap">
            <span v-for="(tag, i) in aiOverall.tags" :key="i" class="da-ai-banner-tag">{{ tag }}</span>
          </div>
        </div>
      </div>

      <!-- Pill tab nav -->
      <div class="da-tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="da-tab"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="num">{{ tab.num }}</span>
          <AppIcon :name="tab.icon" class="text-[18px]" />
          {{ t(tab.labelKey) }}
        </button>
      </div>

      <!-- Section title -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h2 class="da-section-title">
          <span class="num">#{{ activeTabMeta.num }}</span>
          {{ t(activeTabMeta.labelKey) }}
        </h2>
        <span class="bg-primary-fixed text-primary text-[11px] font-bold px-3 py-1.5 rounded-full tracking-widest uppercase">
          Data · stat.uz
        </span>
      </div>

      <!-- #1 Economic -->
      <div v-if="activeTab === 'economic'" class="space-y-6">
        <!-- 8-KPI macro row (reference dashboard style) -->
        <div class="da-macro-row">
          <div
            v-for="m in analytics.economic.macroKpis"
            :key="m.label"
            class="da-macro-kpi"
            :class="`tone-${m.tone}`"
          >
            <div class="da-macro-kpi-label">{{ m.label }}</div>
            <div class="da-macro-kpi-value">{{ m.value }}</div>
            <div class="da-macro-kpi-sub">{{ m.sub }}</div>
            <div class="flex items-center gap-2 flex-wrap">
              <div v-if="m.delta" class="da-macro-kpi-delta" :class="`tone-${m.tone}`">{{ m.delta }}</div>
              <span v-if="m.regionDelta" class="da-region-delta">
                {{ t('district.cards.regionRealLabel') }} {{ m.regionDelta }}
              </span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
          <div v-for="kpi in analytics.economic.kpis" :key="kpi.label" class="da-kpi">
            <div class="da-kpi-label">{{ kpi.label }}</div>
            <div class="da-kpi-value">{{ kpi.value }}</div>
            <div class="da-kpi-sub">{{ kpi.sub }}</div>
            <div class="flex items-center gap-2 flex-wrap mt-auto">
              <span v-if="kpi.delta" class="da-kpi-delta" :class="`tone-${kpi.tone}`">{{ kpi.delta }}</span>
              <span v-if="kpi.regionDelta" class="da-region-delta">
                {{ t('district.cards.regionRealLabel') }} {{ kpi.regionDelta }}
              </span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-6">
          <div class="col-span-12 lg:col-span-8 da-card">
            <div class="da-card-title"><span class="dot"></span>{{ t('district.cards.grpInvestTitle') }} <span class="text-slate-400 font-normal ml-1">{{ t('district.cards.grpInvestForecast') }}</span></div>
            <div class="da-card-sub">{{ t('district.cards.grpInvestSub') }}</div>
            <div class="mt-5">
              <FcChart type="line" :data="grpTrendData" :options="grpTrendOpts" :height="300" />
            </div>
          </div>
          <div v-if="analytics.economic.sectors" class="col-span-12 lg:col-span-4 da-card">
            <div class="da-card-title"><span class="dot" style="background:#059669"></span>{{ t('district.cards.grpStructTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.grpStructSub') }}</div>
            <div class="mt-5">
              <FcChart type="doughnut" :data="sectorsData" :options="sectorsOpts" :height="300" />
            </div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-6">
          <div
            class="da-card"
            :class="analytics.economic.entities ? 'col-span-12 lg:col-span-4' : 'col-span-12'"
          >
            <div class="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <div class="da-card-title"><span class="dot" style="background:#DC2626"></span>{{ t('district.cards.foreignTradeTitle') }}</div>
                <div class="da-card-sub">{{ t('district.cards.foreignTradeSub') }}</div>
              </div>
              <span
                v-if="analytics.economic.trade?.level === 'region'"
                class="da-region-badge"
              >
                {{ t('district.cards.regionLevel') }}
              </span>
              <span
                v-else-if="analytics.economic.trade?.level === 'city'"
                class="da-city-badge"
              >
                {{ t('district.cards.cityLevel') }}
              </span>
            </div>

            <!-- 3-tile horizontal when card spans full width, stacked when narrow -->
            <div
              v-if="analytics.economic.trade"
              class="mt-5"
              :class="analytics.economic.entities ? 'flex flex-col gap-4' : 'grid grid-cols-1 md:grid-cols-3 gap-4'"
            >
              <div class="da-ft-tile">
                <div class="da-kpi-label">{{ t('district.cards.export') }}</div>
                <div class="da-ft-value text-emerald-700">
                  {{ analytics.economic.trade.exportMln.toLocaleString('ru-RU') }}
                  <span class="da-ft-unit">{{ t('districtAnalytics.macro.mlnUSD') }}</span>
                </div>
                <span v-if="analytics.economic.trade.exportGrowth" class="da-chip tone-green">▲ {{ analytics.economic.trade.exportGrowth }}</span>
              </div>
              <div class="da-ft-tile">
                <div class="da-kpi-label">{{ t('district.cards.import') }}</div>
                <div class="da-ft-value text-slate-700">
                  {{ analytics.economic.trade.importMln.toLocaleString('ru-RU') }}
                  <span class="da-ft-unit">{{ t('districtAnalytics.macro.mlnUSD') }}</span>
                </div>
                <span v-if="analytics.economic.trade.importGrowth" class="da-chip tone-blue">▲ {{ analytics.economic.trade.importGrowth }}</span>
              </div>
              <div class="da-ft-tile">
                <div class="da-kpi-label">{{ t('district.cards.balance') }}</div>
                <div class="da-ft-value" :class="analytics.economic.trade.deficitMln >= 0 ? 'text-emerald-700' : 'text-red-600'">
                  {{ analytics.economic.trade.deficitMln.toLocaleString('ru-RU') }}
                  <span class="da-ft-unit">{{ t('districtAnalytics.macro.mlnUSD') }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="analytics.economic.entities" class="col-span-12 lg:col-span-8 da-card">
            <div class="da-card-title"><span class="dot" style="background:#2563EB"></span>{{ t('district.cards.businessTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.businessSub') }}</div>
            <div class="grid grid-cols-12 gap-6 mt-5">
              <div class="col-span-12 md:col-span-5 space-y-4">
                <div>
                  <div class="da-bar-row">
                    <span class="font-semibold">{{ t('district.cards.active') }}</span>
                    <span class="da-mono font-bold text-base">{{ analytics.economic.entities.active }}</span>
                  </div>
                  <div class="da-bar-outer mt-2"><div class="da-bar-inner" :style="{ width: `${analytics.economic.entities.activeShare}%` }"></div></div>
                </div>
                <div>
                  <div class="da-bar-row">
                    <span class="font-semibold">{{ t('district.cards.inactive') }}</span>
                    <span class="da-mono font-bold text-base">{{ analytics.economic.entities.inactive }}</span>
                  </div>
                  <div class="da-bar-outer mt-2"><div class="da-bar-inner" style="background:linear-gradient(90deg,#94A3B8,#CBD5E1)" :style="{ width: `${100 - analytics.economic.entities.activeShare}%` }"></div></div>
                </div>
                <div class="grid grid-cols-2 gap-3 pt-2">
                  <div class="bg-emerald-50 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">{{ t('district.cards.opened') }}</div>
                    <div class="text-2xl font-black text-emerald-600 da-mono">+{{ analytics.economic.entities.opened }}</div>
                  </div>
                  <div class="bg-red-50 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-red-700 uppercase tracking-wider">{{ t('district.cards.closed') }}</div>
                    <div class="text-2xl font-black text-red-600 da-mono">−{{ analytics.economic.entities.closed }}</div>
                  </div>
                </div>
              </div>
              <div class="col-span-12 md:col-span-7">
                <table class="da-table">
                  <thead>
                    <tr><th>{{ t('district.cards.form') }}</th><th class="text-right">{{ t('district.cards.count') }}</th><th class="text-right">{{ t('district.cards.share') }}</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="et in analytics.economic.entities.types" :key="et.code">
                      <td class="font-semibold">{{ et.code }}</td>
                      <td class="text-right da-mono font-bold">{{ et.count }}</td>
                      <td class="text-right text-slate-500">{{ et.share }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- 5-year economic history -->
        <div class="da-card" style="padding:0;overflow:hidden">
          <div style="padding:24px 24px 12px">
            <div class="flex items-start justify-between flex-wrap gap-3">
              <div>
                <div class="da-card-title"><span class="dot"></span>{{ t('district.cards.key5yTitle') }}</div>
                <div class="da-card-sub">{{ t('district.cards.key5ySub') }}</div>
              </div>
              <span class="bg-primary-fixed text-primary text-[11px] font-bold px-3 py-1.5 rounded-full tracking-widest uppercase">
                {{ t('district.cards.sourceEstimate') }}
              </span>
            </div>
          </div>
          <table class="da-trend-table">
            <thead>
              <tr>
                <th>{{ t('district.cards.indicator') }}</th>
                <th class="num">2021</th>
                <th class="num">2022</th>
                <th class="num">2023</th>
                <th class="num">2024</th>
                <th class="num">2025</th>
                <th class="num">{{ t('district.cards.trend') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in analytics.economic.fiveYear" :key="row.label">
                <td>{{ row.label }}</td>
                <td v-for="(v, i) in row.values" :key="i" class="num" :class="{ current: i === row.values.length - 1 }">
                  {{ v.toLocaleString('ru-RU') }}
                </td>
                <td class="num"><span class="da-trend-chip" :class="`tone-${row.trendTone}`">{{ row.trend }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Investment sources + benchmark -->
        <div class="grid grid-cols-12 gap-6">
          <div v-if="analytics.economic.investmentSources" class="col-span-12 lg:col-span-5 da-card">
            <div class="da-card-title"><span class="dot" style="background:#D97706"></span>{{ t('district.cards.investStructTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.investStructSub') }}</div>
            <div class="flex items-center gap-3 mt-4 mb-4">
              <div class="big-number text-primary">{{ analytics.economic.macroKpis[4].value }}</div>
              <div>
                <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{{ t('district.cards.bnSum') }}</div>
                <div class="text-xs font-bold text-emerald-600">{{ t('district.cards.growthVs2024') }}</div>
              </div>
            </div>
            <div>
              <div v-for="src in analytics.economic.investmentSources" :key="src.label" class="da-invest-row">
                <div class="da-invest-row-label">{{ src.label }}</div>
                <div class="da-invest-row-track"><div class="da-invest-row-fill" :style="{ width: `${src.percent}%`, background: src.color }"></div></div>
                <div class="da-invest-row-value">{{ src.percent }}%</div>
              </div>
            </div>
          </div>

          <div :class="['da-card', analytics.economic.investmentSources ? 'col-span-12 lg:col-span-7' : 'col-span-12']">
            <div class="flex items-start justify-between">
              <div>
                <div class="da-card-title"><span class="dot" style="background:#0891B2"></span>{{ t('district.cards.perCapitaTitle') }}</div>
                <div class="da-card-sub">{{ title }} <span class="text-slate-400 font-normal">{{ t('district.cards.vs') }}</span> {{ analytics.economic.benchmark.versus }} · {{ t('district.cards.perCapitaUnit') }}</div>
              </div>
              <div class="flex gap-3 text-[10px] font-bold uppercase tracking-wider">
                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm" style="background:linear-gradient(90deg,#003D7C,#2563EB)"></span>{{ analytics.economic.benchmark.districtLabel || t('district.cards.district') }}</span>
                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm" style="background:linear-gradient(90deg,#0891B2,#22D3EE)"></span>{{ analytics.economic.benchmark.benchmarkLabel || t('district.cards.benchmark') }}</span>
              </div>
            </div>
            <div class="mt-4">
              <div v-for="row in analytics.economic.benchmark.rows" :key="row.label" class="da-bench-row">
                <div class="da-bench-head">
                  <span>{{ row.label }}</span>
                  <span class="da-bench-ratio" :class="row.district >= row.benchmark ? 'win' : 'lose'">
                    {{ row.district >= row.benchmark
                      ? `×${(row.district / Math.max(1, row.benchmark)).toFixed(1)} ▲`
                      : `×${(row.benchmark / Math.max(1, row.district)).toFixed(1)} ▼` }}
                  </span>
                </div>
                <div class="da-bench-bar">
                  <span class="da-bench-bar-label text-primary">{{ analytics.economic.benchmark.districtLabel || t('district.cards.district') }}</span>
                  <div class="da-bench-bar-track"><div class="da-bench-bar-fill district" :style="{ width: `${Math.min(100, (row.district / Math.max(row.district, row.benchmark)) * 100)}%` }"></div></div>
                  <span class="da-bench-bar-value text-primary">{{ row.district.toLocaleString('ru-RU') }}</span>
                </div>
                <div class="da-bench-bar">
                  <span class="da-bench-bar-label" style="color:#0891B2">{{ analytics.economic.benchmark.benchmarkLabel || t('district.cards.benchmark') }}</span>
                  <div class="da-bench-bar-track"><div class="da-bench-bar-fill benchmark" :style="{ width: `${Math.min(100, (row.benchmark / Math.max(row.district, row.benchmark)) * 100)}%` }"></div></div>
                  <span class="da-bench-bar-value" style="color:#0891B2">{{ row.benchmark.toLocaleString('ru-RU') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI analysis card — static, curated from verified PDFs -->
        <div v-if="aiAnalysis" class="da-ai-card">
          <div class="flex items-start justify-between gap-3 flex-wrap mb-4">
            <div class="flex items-center gap-3">
              <div class="da-ai-card-icon">
                <AppIcon name="auto_awesome" filled class="!text-[22px] text-white" />
              </div>
              <div>
                <div class="da-ai-card-title">{{ aiAnalysis.title }}</div>
                <div class="da-ai-card-sub">{{ t('district.aiAnalysis.disclaimer') }}</div>
              </div>
            </div>
            <span class="da-ai-card-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>

          <p class="da-ai-card-summary">{{ aiAnalysis.summary }}</p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <div class="da-ai-card-block-title">
                <AppIcon name="check_circle" class="!text-[16px] text-emerald-600" />
                {{ t('district.aiAnalysis.insightsTitle') }}
              </div>
              <ul class="da-ai-card-list">
                <li v-for="(item, i) in aiAnalysis.insights" :key="`ins-${i}`">{{ item }}</li>
              </ul>
            </div>
            <div>
              <div class="da-ai-card-block-title">
                <AppIcon name="lightbulb" class="!text-[16px] text-amber-600" />
                {{ t('district.aiAnalysis.risksTitle') }}
              </div>
              <ul class="da-ai-card-list">
                <li v-for="(item, i) in aiAnalysis.risks" :key="`rsk-${i}`">{{ item }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Fallback: short auto-generated AI note for districts without curated analysis -->
        <div v-else class="da-ai">
          <div class="da-ai-icon"><AppIcon name="psychology" /></div>
          <div class="flex-1">
            <div class="da-ai-title">{{ t('district.cards.aiRecTitle') }}</div>
            <p>{{ analytics.economic.aiNote }}</p>
          </div>
        </div>
      </div>

      <!-- #2 Infrastructure -->
      <div v-else-if="activeTab === 'infra'" class="space-y-6">
        <div v-if="analytics.infra.kpis" class="grid grid-cols-2 lg:grid-cols-5 gap-5">
          <div v-for="k in analytics.infra.kpis" :key="k.label" class="da-kpi">
            <div class="da-kpi-label">{{ k.label }}</div>
            <div class="da-kpi-value">{{ k.value }}</div>
            <span class="da-kpi-delta" :class="`tone-${k.tone}`">{{ k.delta }}</span>
          </div>
        </div>

        <!-- Verified housing supply card (m² per resident, 2020-2024) -->
        <div v-if="analytics.infra.housing" class="da-card">
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <div class="da-card-title"><span class="dot" style="background:#0054A6"></span>{{ t('district.cards.housingTitle') }}</div>
              <div class="da-card-sub">{{ t('district.cards.housingSub') }}</div>
            </div>
            <span class="da-city-badge">{{ t('district.cards.cityLevel') }}</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
            <div class="da-ft-tile md:col-span-1">
              <div class="da-kpi-label">{{ t('district.cards.housingCurrent') }}</div>
              <div class="da-ft-value text-primary">
                {{ analytics.infra.housing.currentSqMPerPerson }}
                <span class="da-ft-unit">{{ t('district.cards.housingUnit') }}</span>
              </div>
              <span class="da-chip tone-green">{{ t('district.cards.housingYear', { year: analytics.infra.housing.historyLabels[analytics.infra.housing.historyLabels.length - 1] }) }}</span>
            </div>
            <div class="md:col-span-2 grid grid-cols-5 gap-2 items-end">
              <div v-for="(v, i) in analytics.infra.housing.history" :key="i" class="flex flex-col items-center gap-2">
                <div class="text-xs font-bold text-slate-700 da-mono">{{ v }}</div>
                <div
                  class="w-full rounded-t bg-gradient-to-t from-primary to-primary-fixed"
                  :style="{ height: `${(v / 30) * 80}px`, minHeight: '20px' }"
                ></div>
                <div class="text-[10px] text-slate-500 da-mono">{{ analytics.infra.housing.historyLabels[i] }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-6">
          <div v-if="analytics.infra.matrix" class="col-span-12 lg:col-span-7 da-card" style="padding:0;overflow:hidden">
            <div style="padding:24px 24px 12px">
              <div class="da-card-title"><span class="dot" style="background:#D97706"></span>{{ t('district.cards.infraMatrixTitle') }}</div>
              <div class="da-card-sub">{{ t('district.cards.infraMatrixSub') }}</div>
            </div>
            <table class="da-table">
              <thead><tr><th>{{ t('district.cards.system') }}</th><th>{{ t('district.cards.status') }}</th><th>{{ t('district.cards.comment') }}</th></tr></thead>
              <tbody>
                <tr v-for="m in analytics.infra.matrix" :key="m.name">
                  <td class="font-semibold">{{ m.name }}</td>
                  <td>
                    <span class="da-status" :class="`status-${m.status}`">
                      <span class="light"></span>
                      {{ m.status === 'ok' ? t('district.cards.statusOk') : m.status === 'warn' ? t('district.cards.statusWarn') : t('district.cards.statusBad') }}
                    </span>
                  </td>
                  <td class="text-slate-500">{{ m.note }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div :class="['space-y-5', analytics.infra.matrix ? 'col-span-12 lg:col-span-5' : 'col-span-12']">
            <div class="da-card">
              <div class="da-card-title"><span class="dot" style="background:#059669"></span>{{ t('district.cards.devBudgetTitle') }}</div>
              <div class="da-card-sub">{{ t('district.cards.devBudgetSub') }}</div>
              <div class="big-number mt-4 text-primary">{{ analytics.infra.budgetMlrd }}</div>
              <div class="text-sm text-slate-500 mt-1">{{ t('district.cards.bnSum') }}</div>
            </div>
            <div class="da-card">
              <div class="da-card-title"><span class="dot" style="background:#0054A6"></span>{{ t('district.cards.roadsTitle') }}</div>
              <div class="da-card-sub">{{ t('district.cards.roadsTotal') }} {{ analytics.infra.roads.totalKm }} {{ t('district.cards.km') }}</div>
              <div class="space-y-3 mt-4 text-sm">
                <div v-if="analytics.infra.roads.asphaltKm != null">
                  <div class="da-bar-row"><span>{{ t('district.cards.asphalt') }}</span><span class="da-mono font-bold">{{ analytics.infra.roads.asphaltKm }} {{ t('district.cards.km') }}</span></div>
                  <div class="da-bar-outer mt-1.5"><div class="da-bar-inner" :style="{ width: `${(analytics.infra.roads.asphaltKm / analytics.infra.roads.totalKm) * 100}%`, background: 'linear-gradient(90deg,#059669,#10B981)' }"></div></div>
                </div>
                <div v-if="analytics.infra.roads.gravelKm != null">
                  <div class="da-bar-row"><span>{{ t('district.cards.gravel') }}</span><span class="da-mono font-bold">{{ analytics.infra.roads.gravelKm }} {{ t('district.cards.km') }}</span></div>
                  <div class="da-bar-outer mt-1.5"><div class="da-bar-inner" :style="{ width: `${(analytics.infra.roads.gravelKm / analytics.infra.roads.totalKm) * 100}%`, background: 'linear-gradient(90deg,#FBBF24,#F59E0B)' }"></div></div>
                </div>
                <div v-if="analytics.infra.roads.patchedKm != null">
                  <div class="da-bar-row"><span>{{ t('district.cards.patched') }}</span><span class="da-mono font-bold">{{ analytics.infra.roads.patchedKm }} {{ t('district.cards.km') }}</span></div>
                  <div class="da-bar-outer mt-1.5"><div class="da-bar-inner" :style="{ width: `${(analytics.infra.roads.patchedKm / analytics.infra.roads.totalKm) * 100}%`, background: 'linear-gradient(90deg,#D97706,#B45309)' }"></div></div>
                </div>
                <div v-if="analytics.infra.roads.earthKm != null">
                  <div class="da-bar-row"><span>{{ t('district.cards.earth') }}</span><span class="da-mono font-bold">{{ analytics.infra.roads.earthKm }} {{ t('district.cards.km') }}</span></div>
                  <div class="da-bar-outer mt-1.5"><div class="da-bar-inner" :style="{ width: `${(analytics.infra.roads.earthKm / analytics.infra.roads.totalKm) * 100}%`, background: 'linear-gradient(90deg,#DC2626,#991B1B)' }"></div></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="da-card">
          <div class="flex items-start justify-between flex-wrap gap-3">
            <div>
              <div class="da-card-title"><span class="dot" style="background:#F59E0B"></span>{{ t('district.cards.issuesTitle') }}</div>
              <div class="da-card-sub">{{ t('district.cards.issuesSub') }}</div>
            </div>
            <div class="text-right">
              <div class="sub-header-eyebrow">{{ t('district.cards.totalBudget') }}</div>
              <div class="medium-number text-primary">{{ analytics.infra.problems.reduce((s, p) => s + p.cost, 0).toFixed(1) }} <span class="text-sm text-slate-500 font-semibold">{{ t('district.cards.bnSum') }}</span></div>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-5">
            <div v-for="p in analytics.infra.problems" :key="p.code" class="border border-outline-variant/30 rounded-xl p-4 hover:shadow-md hover:border-primary/30 transition-all">
              <div class="flex items-center justify-between">
                <span class="da-mono text-xs font-bold text-primary">{{ p.code }}</span>
                <span class="da-chip" :class="p.priority === t('regionAnalytics.priority.high') ? 'tone-red' : p.priority === t('regionAnalytics.priority.medium') ? 'tone-amber' : 'tone-blue'">{{ p.priority }}</span>
              </div>
              <div class="font-bold text-base mt-2 leading-tight">{{ p.name }}</div>
              <div class="text-sm text-slate-500 mt-2 da-mono">{{ p.cost }} <span class="text-xs">{{ t('district.cards.bnSum') }}</span></div>
            </div>
          </div>
        </div>

        <div v-if="aiAnalysis" class="da-ai-card">
          <div class="flex items-start justify-between gap-3 flex-wrap mb-4">
            <div class="flex items-center gap-3">
              <div class="da-ai-card-icon"><AppIcon name="auto_awesome" filled class="!text-[22px] text-white" /></div>
              <div>
                <div class="da-ai-card-title">{{ aiAnalysis.title }}</div>
                <div class="da-ai-card-sub">{{ t('district.aiAnalysis.disclaimer') }}</div>
              </div>
            </div>
            <span class="da-ai-card-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>
          <p class="da-ai-card-summary">{{ aiAnalysis.summary }}</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="check_circle" class="!text-[16px] text-emerald-600" />{{ t('district.aiAnalysis.insightsTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.insights" :key="`ins-${i}`">{{ item }}</li></ul>
            </div>
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="lightbulb" class="!text-[16px] text-amber-600" />{{ t('district.aiAnalysis.risksTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.risks" :key="`rsk-${i}`">{{ item }}</li></ul>
            </div>
          </div>
        </div>
        <div v-else class="da-ai">
          <div class="da-ai-icon"><AppIcon name="psychology" /></div>
          <div class="flex-1">
            <div class="da-ai-title">{{ t('district.cards.aiRecTitle') }}</div>
            <p>{{ analytics.infra.aiNote }}</p>
          </div>
        </div>
      </div>

      <!-- #3 Population -->
      <div v-else-if="activeTab === 'population'" class="space-y-6">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
          <div v-for="k in analytics.population.kpis" :key="k.label" class="da-kpi">
            <div class="da-kpi-label">{{ k.label }}</div>
            <div class="da-kpi-value">{{ k.value }}</div>
            <span class="da-kpi-delta" :class="`tone-${k.tone}`">{{ k.delta }}</span>
            <div class="da-kpi-sub">{{ k.sub }}</div>
          </div>
        </div>

        <!-- Verified vital statistics (births / deaths / natural increase) -->
        <div v-if="analytics.population.vitalStats" class="da-card">
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <div class="da-card-title"><span class="dot" style="background:#059669"></span>{{ t('district.cards.vitalStatsTitle') }}</div>
              <div class="da-card-sub">{{ t('district.cards.vitalStatsSub') }}</div>
            </div>
            <span class="da-city-badge">{{ t('district.cards.cityLevel') }}</span>
          </div>
          <div class="grid grid-cols-12 gap-5 mt-5">
            <div class="col-span-12 md:col-span-4 grid grid-cols-1 gap-3">
              <div class="da-ft-tile">
                <div class="da-kpi-label">{{ t('district.cards.vitalBirths') }} 2025</div>
                <div class="da-ft-value text-emerald-700">
                  {{ analytics.population.vitalStats.births2025.toLocaleString('ru-RU') }}
                  <span class="da-ft-unit">{{ t('district.units.peopleShort') }}</span>
                </div>
                <div class="text-[11px] text-slate-500">
                  {{ t('district.cards.vitalBoys') }}: {{ analytics.population.vitalStats.birthsBoys2025.toLocaleString('ru-RU') }} ·
                  {{ t('district.cards.vitalGirls') }}: {{ analytics.population.vitalStats.birthsGirls2025.toLocaleString('ru-RU') }}
                </div>
              </div>
              <div class="da-ft-tile">
                <div class="da-kpi-label">{{ t('district.cards.vitalDeaths') }} 2025</div>
                <div class="da-ft-value text-red-600">
                  {{ analytics.population.vitalStats.deaths2025.toLocaleString('ru-RU') }}
                  <span class="da-ft-unit">{{ t('district.units.peopleShort') }}</span>
                </div>
              </div>
              <div class="da-ft-tile">
                <div class="da-kpi-label">{{ t('district.cards.vitalNaturalIncrease') }} 2025</div>
                <div class="da-ft-value text-primary">
                  +{{ analytics.population.vitalStats.naturalIncrease2025.toLocaleString('ru-RU') }}
                  <span class="da-ft-unit">{{ t('district.units.peopleShort') }}</span>
                </div>
              </div>
            </div>
            <div class="col-span-12 md:col-span-8">
              <FcChart type="bar" :data="vitalStatsData" :options="vitalStatsOpts" :height="280" />
            </div>
          </div>
        </div>

        <!-- Verified population history + age distribution (city-level data
             only — only renders when rd.populationFiveYear / ageGroups2025
             exist on the district record). -->
        <div v-if="populationHistoryData || ageGroupsData" class="grid grid-cols-12 gap-6">
          <div v-if="populationHistoryData" class="col-span-12 lg:col-span-5 da-card">
            <div class="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <div class="da-card-title"><span class="dot" style="background:#003D7C"></span>{{ t('district.cards.populationHistoryTitle') }}</div>
                <div class="da-card-sub">{{ t('district.cards.populationHistorySub') }}</div>
              </div>
              <span class="da-city-badge">{{ t('district.cards.cityLevel') }}</span>
            </div>
            <div class="mt-5">
              <FcChart type="line" :data="populationHistoryData" :options="populationHistoryOpts" :height="260" />
            </div>
          </div>
          <div v-if="ageGroupsData" class="col-span-12 lg:col-span-7 da-card">
            <div class="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <div class="da-card-title"><span class="dot" style="background:#0054A6"></span>{{ t('district.cards.ageGroupsTitle') }}</div>
                <div class="da-card-sub">{{ t('district.cards.ageGroupsSub') }}</div>
              </div>
              <span class="da-city-badge">{{ t('district.cards.cityLevel') }}</span>
            </div>
            <div class="mt-5">
              <FcChart type="bar" :data="ageGroupsData" :options="ageGroupsOpts" :height="260" />
            </div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-6">
          <div class="col-span-12 lg:col-span-8 da-card">
            <div class="da-card-title"><span class="dot"></span>{{ t('district.cards.laborMarketTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.laborMarketSub') }}</div>
            <div class="mt-5">
              <FcChart type="bar" :data="laborData" :options="laborOpts" :height="320" />
            </div>
          </div>
          <div class="col-span-12 lg:col-span-4 da-card">
            <div class="da-card-title"><span class="dot" style="background:#DC2626"></span>{{ t('district.cards.unemploymentTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.unemploymentSub') }}</div>
            <div class="mt-5">
              <FcChart type="line" :data="unemploymentData" :options="unemploymentOpts" :height="320" />
            </div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-6">
          <div class="col-span-12 lg:col-span-7 da-card">
            <div class="da-card-title"><span class="dot" style="background:#D97706"></span>{{ t('district.cards.migrationTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.migrationSub') }}</div>
            <div class="grid grid-cols-3 gap-5 mt-5">
              <div class="border-r border-outline-variant/30 pr-4">
                <div class="da-kpi-label mb-2">{{ t('district.cards.abroad') }}</div>
                <div class="medium-number text-amber-600">{{ analytics.population.migration.countAbroad.toLocaleString('ru-RU') }}</div>
              </div>
              <div class="border-r border-outline-variant/30 pr-4">
                <div class="da-kpi-label mb-2">{{ t('district.cards.growth5y') }}</div>
                <div class="medium-number text-red-600">{{ analytics.population.migration.growthPct }}</div>
              </div>
              <div>
                <div class="da-kpi-label mb-2">{{ t('district.cards.share2') }}</div>
                <div class="medium-number text-primary">{{ analytics.population.migration.shareOfWorkforce }}</div>
              </div>
            </div>
            <div class="tone-red rounded-xl px-4 py-3 mt-5 text-sm font-semibold flex gap-2 items-start">
              <AppIcon name="warning" class="flex-shrink-0 mt-0.5" />
              <span>{{ analytics.population.migration.warning }}</span>
            </div>
          </div>

          <div class="col-span-12 lg:col-span-5 da-card">
            <div class="da-card-title"><span class="dot" style="background:#059669"></span>{{ analytics.population.program2026.title }}</div>
            <div class="da-card-sub">
              {{ t('district.cards.goal') }}: <b class="text-primary">{{ analytics.population.program2026.goal.toLocaleString('ru-RU') }}</b> {{ t('district.cards.jobs') }}
            </div>
            <div class="mt-4 space-y-2.5">
              <div v-for="item in analytics.population.program2026.breakdown" :key="item.code" class="flex items-center justify-between text-sm border border-outline-variant/20 rounded-xl px-4 py-3 hover:border-primary/30 transition-colors">
                <span class="flex items-center gap-3">
                  <span class="da-mono text-[11px] font-bold text-primary bg-primary-fixed px-2 py-0.5 rounded">{{ item.code }}</span>
                  <span class="font-semibold">{{ item.label }}</span>
                </span>
                <span class="da-mono font-bold text-base">{{ item.count.toLocaleString('ru-RU') }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="aiAnalysis" class="da-ai-card">
          <div class="flex items-start justify-between gap-3 flex-wrap mb-4">
            <div class="flex items-center gap-3">
              <div class="da-ai-card-icon"><AppIcon name="auto_awesome" filled class="!text-[22px] text-white" /></div>
              <div>
                <div class="da-ai-card-title">{{ aiAnalysis.title }}</div>
                <div class="da-ai-card-sub">{{ t('district.aiAnalysis.disclaimer') }}</div>
              </div>
            </div>
            <span class="da-ai-card-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>
          <p class="da-ai-card-summary">{{ aiAnalysis.summary }}</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="check_circle" class="!text-[16px] text-emerald-600" />{{ t('district.aiAnalysis.insightsTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.insights" :key="`ins-${i}`">{{ item }}</li></ul>
            </div>
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="lightbulb" class="!text-[16px] text-amber-600" />{{ t('district.aiAnalysis.risksTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.risks" :key="`rsk-${i}`">{{ item }}</li></ul>
            </div>
          </div>
        </div>
      </div>

      <!-- #4 Mahalla & Bank -->
      <div v-else-if="activeTab === 'mahalla'" class="space-y-6">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
          <div v-for="k in analytics.mahalla.kpis" :key="k.label" class="da-kpi">
            <div class="da-kpi-label">{{ k.label }}</div>
            <div class="da-kpi-value">{{ k.value }}</div>
            <div class="da-kpi-sub">{{ k.sub }}</div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-6">
          <div class="col-span-12 lg:col-span-7 da-card">
            <div class="da-card-title"><span class="dot"></span>{{ t('district.cards.bankEntTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.bankEntSub') }}</div>
            <div class="mt-5 space-y-4">
              <div v-for="b in analytics.mahalla.bankMetrics" :key="b.label">
                <div class="da-bar-row">
                  <span class="font-semibold">{{ b.label }}</span>
                  <span class="da-mono font-bold text-base text-primary">{{ b.percent }}%</span>
                </div>
                <div class="da-bar-outer mt-1.5"><div class="da-bar-inner" :style="{ width: `${b.percent}%` }"></div></div>
              </div>
            </div>
          </div>

          <div class="col-span-12 lg:col-span-5 da-card">
            <div class="da-card-title"><span class="dot" style="background:#2563EB"></span>{{ t('district.cards.digitalTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.digitalSub') }}</div>
            <div class="grid grid-cols-2 gap-3 mt-5">
              <div class="border border-outline-variant/30 rounded-xl p-4">
                <AppIcon name="credit_card" class="text-primary text-2xl mb-2" filled />
                <div class="da-kpi-label">{{ t('district.cards.payments') }}</div>
                <div class="medium-number text-primary">{{ analytics.mahalla.digitalAdoption.payments }}%</div>
              </div>
              <div class="border border-outline-variant/30 rounded-xl p-4">
                <AppIcon name="credit_score" class="text-primary text-2xl mb-2" filled />
                <div class="da-kpi-label">{{ t('district.cards.cards') }}</div>
                <div class="medium-number text-primary">{{ analytics.mahalla.digitalAdoption.cards }}%</div>
              </div>
              <div class="border border-outline-variant/30 rounded-xl p-4">
                <AppIcon name="storefront" class="text-primary text-2xl mb-2" filled />
                <div class="da-kpi-label">{{ t('district.cards.merchants') }}</div>
                <div class="medium-number text-primary">{{ analytics.mahalla.digitalAdoption.merchants }}%</div>
              </div>
              <div class="border border-outline-variant/30 rounded-xl p-4">
                <AppIcon name="savings" class="text-primary text-2xl mb-2" filled />
                <div class="da-kpi-label">{{ t('district.cards.onlineCredit') }}</div>
                <div class="medium-number text-primary">{{ analytics.mahalla.digitalAdoption.lending }}%</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="analytics.mahalla.topMahallas" class="da-card" style="padding:0;overflow:hidden">
          <div style="padding:24px 24px 12px">
            <div class="da-card-title"><span class="dot" style="background:#059669"></span>{{ t('district.cards.topMahallasTitle') }}</div>
            <div class="da-card-sub">{{ t('district.cards.topMahallasSub') }}</div>
          </div>
          <table class="da-table" style="table-layout:fixed">
            <thead><tr><th style="width:8%">#</th><th style="width:52%">{{ t('district.cards.mahalla') }}</th><th style="width:20%; text-align:center">{{ t('district.cards.credits') }}</th><th style="width:20%; text-align:center">{{ t('district.cards.score') }}</th></tr></thead>
            <tbody>
              <tr v-for="(m, i) in analytics.mahalla.topMahallas" :key="m.name">
                <td class="da-mono text-slate-400 font-bold">{{ i + 1 }}</td>
                <td class="font-bold text-base">{{ m.name }}</td>
                <td style="text-align:center" class="da-mono font-bold text-base">{{ m.loans }}</td>
                <td style="text-align:center">
                  <span class="da-chip" :class="m.score >= 8.5 ? 'tone-green' : m.score >= 8 ? 'tone-blue' : 'tone-amber'">★ {{ m.score }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="aiAnalysis" class="da-ai-card">
          <div class="flex items-start justify-between gap-3 flex-wrap mb-4">
            <div class="flex items-center gap-3">
              <div class="da-ai-card-icon"><AppIcon name="auto_awesome" filled class="!text-[22px] text-white" /></div>
              <div>
                <div class="da-ai-card-title">{{ aiAnalysis.title }}</div>
                <div class="da-ai-card-sub">{{ t('district.aiAnalysis.disclaimer') }}</div>
              </div>
            </div>
            <span class="da-ai-card-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>
          <p class="da-ai-card-summary">{{ aiAnalysis.summary }}</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="check_circle" class="!text-[16px] text-emerald-600" />{{ t('district.aiAnalysis.insightsTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.insights" :key="`ins-${i}`">{{ item }}</li></ul>
            </div>
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="lightbulb" class="!text-[16px] text-amber-600" />{{ t('district.aiAnalysis.risksTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.risks" :key="`rsk-${i}`">{{ item }}</li></ul>
            </div>
          </div>
        </div>
      </div>

      <!-- #5 SWOT -->
      <div v-else-if="activeTab === 'opportunities'" class="space-y-6">
        <div class="da-card">
          <div class="da-card-title"><span class="dot" style="background:#DC2626"></span>{{ t('district.cards.criticalIssuesTitle') }}</div>
          <div class="da-card-sub">{{ t('district.cards.criticalIssuesSub') }}</div>
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mt-5">
            <div v-for="iss in analytics.opportunities.criticalIssues" :key="iss.code" class="da-issue" :class="`sev-${iss.severity}`">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span class="da-issue-code">{{ iss.code }}</span>
                  <span class="da-issue-title">{{ iss.title }}</span>
                </div>
                <span class="da-chip" :class="iss.severity === 'high' ? 'tone-red' : iss.severity === 'medium' ? 'tone-amber' : 'tone-blue'">
                  {{ iss.severity === 'high' ? t('district.cards.severityHigh') : iss.severity === 'medium' ? t('district.cards.severityMedium') : t('district.cards.severityLow') }}
                </span>
              </div>
              <p class="da-issue-detail">{{ iss.detail }}</p>
              <div class="da-issue-kpi">
                <span class="da-issue-kpi-from">{{ iss.kpi.from }}</span>
                <span class="da-issue-kpi-arr">→</span>
                <span class="da-issue-kpi-to">{{ iss.kpi.to }}</span>
                <span class="da-issue-kpi-unit">{{ iss.kpi.unit }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="swot-card">
            <div class="swot-header" style="background:linear-gradient(135deg,#059669,#047857)">
              <span>{{ t('district.cards.swotStrengths') }}</span>
              <span class="da-mono opacity-70">S{{ analytics.opportunities.swot.strengths.length }}</span>
            </div>
            <ul class="swot-body" style="background:#F0FDF8">
              <li v-for="(s, i) in analytics.opportunities.swot.strengths" :key="s">
                <span class="tag" style="color:#059669">S{{ i + 1 }}</span>
                <span>{{ s }}</span>
              </li>
            </ul>
          </div>
          <div class="swot-card">
            <div class="swot-header" style="background:linear-gradient(135deg,#DC2626,#991B1B)">
              <span>{{ t('district.cards.swotWeaknesses') }}</span>
              <span class="da-mono opacity-70">W{{ analytics.opportunities.swot.weaknesses.length }}</span>
            </div>
            <ul class="swot-body" style="background:#FFF5F5">
              <li v-for="(w, i) in analytics.opportunities.swot.weaknesses" :key="w">
                <span class="tag" style="color:#DC2626">W{{ i + 1 }}</span>
                <span>{{ w }}</span>
              </li>
            </ul>
          </div>
          <div class="swot-card">
            <div class="swot-header" style="background:linear-gradient(135deg,#2563EB,#1D4ED8)">
              <span>{{ t('district.cards.swotOpportunities') }}</span>
              <span class="da-mono opacity-70">O{{ analytics.opportunities.swot.opportunities.length }}</span>
            </div>
            <ul class="swot-body" style="background:#EFF6FF">
              <li v-for="(o, i) in analytics.opportunities.swot.opportunities" :key="o">
                <span class="tag" style="color:#2563EB">O{{ i + 1 }}</span>
                <span>{{ o }}</span>
              </li>
            </ul>
          </div>
          <div class="swot-card">
            <div class="swot-header" style="background:linear-gradient(135deg,#D97706,#B45309)">
              <span>{{ t('district.cards.swotThreats') }}</span>
              <span class="da-mono opacity-70">T{{ analytics.opportunities.swot.threats.length }}</span>
            </div>
            <ul class="swot-body" style="background:#FFFBEB">
              <li v-for="(th, i) in analytics.opportunities.swot.threats" :key="th.label" class="swot-threat">
                <span class="flex gap-2 items-baseline flex-1">
                  <span class="tag" style="color:#D97706">T{{ i + 1 }}</span>
                  <span>{{ th.label }}</span>
                </span>
                <span class="da-mono text-[10px] font-bold rounded-full px-2.5 py-1" :class="threatLevelClass(th.level)">{{ th.level.toUpperCase() }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div v-if="aiAnalysis" class="da-ai-card">
          <div class="flex items-start justify-between gap-3 flex-wrap mb-4">
            <div class="flex items-center gap-3">
              <div class="da-ai-card-icon"><AppIcon name="auto_awesome" filled class="!text-[22px] text-white" /></div>
              <div>
                <div class="da-ai-card-title">{{ aiAnalysis.title }}</div>
                <div class="da-ai-card-sub">{{ t('district.aiAnalysis.disclaimer') }}</div>
              </div>
            </div>
            <span class="da-ai-card-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>
          <p class="da-ai-card-summary">{{ aiAnalysis.summary }}</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="check_circle" class="!text-[16px] text-emerald-600" />{{ t('district.aiAnalysis.insightsTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.insights" :key="`ins-${i}`">{{ item }}</li></ul>
            </div>
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="lightbulb" class="!text-[16px] text-amber-600" />{{ t('district.aiAnalysis.risksTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.risks" :key="`rsk-${i}`">{{ item }}</li></ul>
            </div>
          </div>
        </div>
        <div v-else class="da-ai">
          <div class="da-ai-icon"><AppIcon name="psychology" /></div>
          <div class="flex-1">
            <div class="da-ai-title">{{ t('district.cards.aiRecTitle') }}</div>
            <p>{{ analytics.opportunities.aiRecommendation }}</p>
          </div>
        </div>
      </div>

      <!-- #6 Summary & Plan -->
      <div v-else-if="activeTab === 'summary'" class="space-y-6">
        <div class="grid grid-cols-12 gap-6">
          <div class="col-span-12 lg:col-span-6 da-card">
            <div class="flex items-center justify-between gap-6">
              <div class="flex-1">
                <div class="sub-header-eyebrow text-primary">{{ t('district.cards.executivePass') }}</div>
                <h3 class="text-3xl font-black leading-tight mt-2" style="font-family:'Manrope',sans-serif;letter-spacing:-0.02em">{{ title }}</h3>
                <p class="text-sm text-slate-500 mt-3 leading-relaxed max-w-sm">
                  {{ t('district.cards.integralScoreDesc') }}
                </p>
              </div>
              <div class="bg-gradient-to-br from-primary to-[#0054A6] text-white rounded-2xl text-center px-6 py-6 shadow-xl min-w-[140px]">
                <div class="text-[10px] font-bold uppercase opacity-80 tracking-widest">Score</div>
                <div class="font-black mt-1" style="font-family:'Manrope',sans-serif;letter-spacing:-0.03em;font-size:clamp(2rem,4.5vw,3rem)">{{ analytics.summary.score }}</div>
                <div class="text-[10px] opacity-70 mt-0.5">{{ t('district.cards.outOf10') }}</div>
                <div class="mt-3 h-1.5 bg-white/20 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-400" :style="{ width: `${parseFloat(analytics.summary.score) * 10}%` }"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-span-12 lg:col-span-6 da-card flex items-center gap-6">
            <svg viewBox="0 0 280 280" class="w-56 flex-shrink-0">
              <polygon points="140,35 240,105 205,225 75,225 40,105" fill="none" stroke="#E5E7EB" stroke-width="2" />
              <polygon points="140,70 210,118 183,195 97,195 70,118" fill="none" stroke="#F0F4FA" stroke-width="1.5" />
              <polygon points="140,105 180,130 161,163 119,163 100,130" fill="none" stroke="#F5F7FB" stroke-width="1" />
              <polygon :points="radarPoints.provincialPoly" fill="#0891B2" fill-opacity="0.12" stroke="#0891B2" stroke-width="1.5" stroke-dasharray="5,4" />
              <polygon :points="radarPoints.regionPoly" fill="#003D7C" fill-opacity="0.25" stroke="#003D7C" stroke-width="2.5" stroke-linejoin="round" />
              <circle v-for="(pt, i) in radarPoints.regionDots" :key="i" :cx="pt.x" :cy="pt.y" r="5" fill="#003D7C" stroke="#fff" stroke-width="2" />
              <text
                v-for="(l, i) in radarPoints.labels"
                :key="`lab-${i}`"
                :x="l.x"
                :y="l.y"
                text-anchor="middle"
                font-size="11"
                font-weight="800"
                fill="#0b1a33"
                dominant-baseline="middle"
              >{{ l.name }} ({{ l.value }})</text>
            </svg>
            <div class="flex-1 space-y-3">
              <div class="flex items-center gap-2 font-bold text-sm"><span class="w-4 h-4 bg-primary rounded-sm"></span> {{ title }}</div>
              <div class="flex items-center gap-2 font-bold text-sm text-cyan-700"><span class="w-4 h-4 rounded-sm border-2 border-dashed border-cyan-600"></span> {{ t('district.cards.regionAverage') }}</div>
              <p class="text-sm text-slate-600 mt-4 leading-relaxed">{{ analytics.summary.conclusion }}</p>
            </div>
          </div>
        </div>

        <div class="da-card" style="padding:0;overflow:hidden">
          <div style="padding:24px 24px 12px">
            <div class="da-card-title"><span class="dot"></span>{{ title }} <span class="text-slate-400 font-normal">{{ t('district.cards.vs') }}</span> {{ t('district.cards.regionAverage') }}</div>
            <div class="da-card-sub">{{ t('district.cards.perCapitaThousand') }}</div>
          </div>
          <table class="da-table" style="table-layout:fixed">
            <thead><tr><th style="width:40%">{{ t('district.cards.indicator') }}</th><th style="width:20%; text-align:center">{{ t('district.cards.district') }}</th><th style="width:20%; text-align:center">{{ t('district.cards.mean') }}</th><th style="width:20%; text-align:center">{{ t('district.cards.diff') }}</th></tr></thead>
            <tbody>
              <tr v-for="row in analytics.summary.comparison" :key="row.metric">
                <td class="font-semibold">{{ row.metric }}</td>
                <td style="text-align:center" class="da-mono font-bold text-base text-primary">{{ row.region.toLocaleString('ru-RU') }}</td>
                <td style="text-align:center" class="da-mono text-cyan-700">{{ row.provincial.toLocaleString('ru-RU') }}</td>
                <td style="text-align:center">
                  <span class="da-chip" :class="row.region >= row.provincial ? 'tone-green' : 'tone-red'">
                    {{ row.region >= row.provincial ? '▲' : '▼' }}
                    {{ Math.abs(Math.round(((row.region - row.provincial) / Math.max(1, row.provincial)) * 100)) }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="da-card">
          <div class="da-card-title"><span class="dot" style="background:#2563EB"></span>{{ t('district.cards.strategicTitle') }}</div>
          <div class="da-card-sub">{{ t('district.cards.strategicSub') }}</div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
            <div v-for="(hz, hi) in analytics.summary.strategicPriorities" :key="hz.horizon" class="da-horizon-col">
              <div class="da-horizon-head" :style="{ background: hz.color }">
                <span class="text-[10px] font-bold tracking-widest opacity-80 uppercase">{{ t('district.cards.horizon') }} {{ hi + 1 }}</span>
                <span class="text-lg font-black da-mono">{{ hz.horizon }}</span>
                <span class="text-xs font-semibold opacity-90">{{ hz.label }}</span>
              </div>
              <div class="da-horizon-body">
                <div v-for="(it, i) in hz.items" :key="it.title" class="da-horizon-item">
                  <div class="flex items-start gap-2">
                    <span class="da-mono text-[10px] font-bold text-slate-400 mt-1">{{ i + 1 }}</span>
                    <div class="flex-1">
                      <div class="da-horizon-title">{{ it.title }}</div>
                      <div class="flex items-center justify-between mt-2 gap-2">
                        <span class="da-horizon-budget">{{ it.budget }} {{ t('district.cards.bn') }}</span>
                        <span class="da-horizon-kpi">{{ it.kpi }}</span>
                      </div>
                      <div class="da-horizon-owner">{{ it.owner }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="da-card">
          <div class="da-card-title"><span class="dot" style="background:#059669"></span>{{ t('district.cards.actionPlanTitle') }}</div>
          <div class="da-card-sub">{{ t('district.cards.actionPlanSub') }}</div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-5">
            <div v-for="(p, i) in analytics.summary.plan" :key="p.title" class="relative border border-outline-variant/30 rounded-xl p-5 hover:shadow-md hover:border-primary/30 transition-all">
              <div class="absolute -top-3 left-5 bg-primary text-white px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase">
                {{ t('district.cards.step') }} {{ i + 1 }}
              </div>
              <div class="sub-header-eyebrow text-primary mt-2">{{ p.horizon }}</div>
              <div class="font-bold text-lg mt-2 leading-tight">{{ p.title }}</div>
              <div class="flex items-center justify-between mt-4 pt-3 border-t border-outline-variant/30">
                <div>
                  <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{{ t('district.cards.budget') }}</div>
                  <div class="text-lg font-black da-mono text-primary">{{ p.mlrd }}</div>
                </div>
                <div class="text-right">
                  <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">KPI</div>
                  <div class="text-xs font-bold text-emerald-600">{{ p.kpi }}</div>
                </div>
              </div>
              <div class="text-xs text-slate-500 mt-2">{{ p.owner }}</div>
            </div>
          </div>
        </div>

        <div v-if="aiAnalysis" class="da-ai-card">
          <div class="flex items-start justify-between gap-3 flex-wrap mb-4">
            <div class="flex items-center gap-3">
              <div class="da-ai-card-icon"><AppIcon name="auto_awesome" filled class="!text-[22px] text-white" /></div>
              <div>
                <div class="da-ai-card-title">{{ aiAnalysis.title }}</div>
                <div class="da-ai-card-sub">{{ t('district.aiAnalysis.disclaimer') }}</div>
              </div>
            </div>
            <span class="da-ai-card-badge">{{ t('district.aiAnalysis.badge') }}</span>
          </div>
          <p class="da-ai-card-summary">{{ aiAnalysis.summary }}</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="check_circle" class="!text-[16px] text-emerald-600" />{{ t('district.aiAnalysis.insightsTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.insights" :key="`ins-${i}`">{{ item }}</li></ul>
            </div>
            <div>
              <div class="da-ai-card-block-title"><AppIcon name="lightbulb" class="!text-[16px] text-amber-600" />{{ t('district.aiAnalysis.risksTitle') }}</div>
              <ul class="da-ai-card-list"><li v-for="(item, i) in aiAnalysis.risks" :key="`rsk-${i}`">{{ item }}</li></ul>
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>

  <!-- Unavailable district toast -->
  <div v-if="unavailableToast"
    class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-[#1A2B4A] text-white px-5 py-3 rounded-xl shadow-lg text-sm font-semibold flex items-center gap-2">
    <AppIcon name="info" class="!text-[18px]" />
    {{ t(`district.unavailable.${region}`) }}
  </div>
  </div>
</template>
