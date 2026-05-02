<script setup>
/**
 * Qoqon (Qoʻqon shahri) — premium analytics dashboard.
 *
 * Renders a hero-first, data-dense layout grounded entirely in verified
 * fergana/-PDF values exposed by REAL_DATA.qoqon_city in
 * districtAnalytics.js. Designed as a redesign sandbox for the unified
 * Golden Mart template — separate component so the existing
 * DistrictAnalyticsView remains untouched for other cities.
 */
import { computed, ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import FcSparkline from '@/components/fincontrol/FcSparkline.vue'
import { buildDistrictAnalytics } from '@/data/districtAnalytics'
import { loadEntity } from '@/data/goldenMart/loader.js'

// Hero style: 'A' glassmorphism quick-stats (default) | 'B' Fergana-style executive brief.
// Persisted in localStorage so the user's choice sticks across sessions.
const heroStyle = ref('A')
onMounted(() => {
  const saved = localStorage.getItem('qoqon_hero_style')
  if (saved === 'A' || saved === 'B') heroStyle.value = saved
})
function setHero(s) {
  heroStyle.value = s
  localStorage.setItem('qoqon_hero_style', s)
}

function openDetail() {
  router.push({ path: route.path, query: { ...route.query, view: 'goldenmart' } })
}

const { t, te, tm } = useI18n()
const router = useRouter()
const route = useRoute()

const KEY = 'qoqon_city'
const analytics = computed(() => buildDistrictAnalytics(KEY, t))

// ── Verified scalars (sourced through buildDistrictAnalytics → REAL_DATA) ──
// Initial values are baked-in fallbacks. On mount we try the API and overlay
// any non-null values returned — admin edits flow into the dashboard live.
const D = reactive({
  // Pulled directly from REAL_DATA.qoqon_city for chart-friendly access.
  popK: 319.6,
  area: 60,
  density: Math.round(319_600 / 60), // 5326/km²
  // Population history matches GM Excel year columns: 2021–2025 + 2026 plan.
  populationFiveYear:       [256.4, 259.7, 303.6, 308.1, 313.6, 319.6],
  populationFiveYearLabels: [2021, 2022, 2023, 2024, 2025, 2026],
  fiveYear: {
    industry:     [4340.0, 5602.6, 5886.6, 6264.5, 9410.4],
    services:     [2486.1, 3176.2, 3625.2, 4917.6, 6371.1],
    trade:        [3451.4, 4077.2, 4986.1, 5713.8, 6589.0],
    investments:  [ 997.9, 1032.3, 1591.5, 1956.6, 4111.2],
    construction: [ 516.6,  647.4,  770.4,  912.0, 1075.1],
    agriculture:  [ 240.6,  233.2,  330.5,  322.1,  382.1],
  },
  fiveYearLabels: [2021, 2022, 2023, 2024, 2025],
  vital: {
    births:  [5783, 6561, 7976, 7654, 6923],
    deaths:  [1565, 1249, 1499, 1490, 1513],
    natural: [4218, 5312, 6477, 6164, 5410],
    labels:  [2021, 2022, 2023, 2024, 2025],
  },
  ageGroups: {
    '0–2': 22968, '3–5': 19575, '6–7': 10777, '8–15': 43560,
    '16–17': 10769, '18–19': 9845, '20–24': 21293, '25–29': 22670,
    '30–34': 26460, '35–39': 24048, '40–49': 39225, '50–59': 27839,
    '60–69': 22468, '70–74': 6323, '75–79': 3533, '80–84': 1361, '85+': 883,
  },
  // Region real growth (constant prices, viloyat-level)
  regionReal: {
    industry: 7.3, services: 8.6, trade: 11.1,
    construction: 17.4, agriculture: 5.4, gross: 8.1,
  },
  // Per-capita comparison vs Fergana / Margilan (ths soʻm/person, 2025)
  perCapitaCompare: {
    Qoqon:    { industry: 29445, services: 19934, trade: 20617, construction: 3364, invest: 12863 },
    Fergana:  { industry: 38187, services: 36753, trade: 19785, construction: 9878, invest: 21491 },
    Margilan: { industry:  9389, services: 13496, trade: 21680, construction: 6846, invest:  4891 },
  },
})

// ── Live data overlay: pull from API on mount; merge non-null values into D ──
const dataSource = ref('static')

onMounted(async () => {
  try {
    const loaded = await loadEntity('city', 'qoqon_city')
    dataSource.value = loaded.source

    // Scalars that map to D fields
    if (loaded.scalars.s1_4 != null) D.area = +loaded.scalars.s1_4
    if (loaded.scalars.s1_6 != null) {
      D.popK = +loaded.scalars.s1_6 / 1000
      D.density = Math.round(+loaded.scalars.s1_6 / D.area)
    }
    // Year arrays — use API series when present (yearly[k] = [2021..2026])
    const py = loaded.yearly
    if (py?.s1_6?.some((v) => v != null)) {
      // Population history in thousands
      D.populationFiveYear = py.s1_6.map((v) => v == null ? null : +v / 1000)
    }
    // Sector 5y series — slice 0..4 for years 2021..2025
    const yearly5 = (key) => py?.[key]?.slice(0, 5).map((v) => v == null ? 0 : +v)
    if (py?.s2_2?.some((v) => v != null)) D.fiveYear.industry     = yearly5('s2_2')
    if (py?.s2_3?.some((v) => v != null)) D.fiveYear.services     = yearly5('s2_3')
    if (py?.s2_4?.some((v) => v != null)) D.fiveYear.trade        = yearly5('s2_4')
    if (py?.s2_5?.some((v) => v != null)) D.fiveYear.construction = yearly5('s2_5')
    if (py?.s2_6?.some((v) => v != null)) D.fiveYear.agriculture  = yearly5('s2_6')
    if (py?.s2_7?.some((v) => v != null)) D.fiveYear.investments  = yearly5('s2_7')
    // Vital stats series
    if (py?.s11_7?.some((v) => v != null)) D.vital.births = yearly5('s11_7')
    if (py?.s11_8?.some((v) => v != null)) D.vital.deaths = yearly5('s11_8')
    if (D.vital.births?.length === 5 && D.vital.deaths?.length === 5) {
      D.vital.natural = D.vital.births.map((b, i) => b - D.vital.deaths[i])
    }
    // Age structure (2025 snapshot — scalars s1_12..s1_28)
    const ageBracketKeys = ['0–2','3–5','6–7','8–15','16–17','18–19','20–24','25–29',
                            '30–34','35–39','40–49','50–59','60–69','70–74','75–79','80–84','85+']
    for (let i = 0; i < 17; i++) {
      const apiKey = `s1_${12 + i}`
      const v = loaded.scalars[apiKey]
      if (v != null) D.ageGroups[ageBracketKeys[i]] = +v
    }
  } catch (e) {
    console.warn('[QoqonDashboard] live data load failed, using static:', e.message)
    dataSource.value = 'static-error'
  }
})

// ── Helpers ──
const fmt = (n, d = 0) =>
  Number.isFinite(n)
    ? n.toLocaleString('ru-RU', { minimumFractionDigits: d, maximumFractionDigits: d })
    : '—'

const pct = (last, first) => +(((last / first) - 1) * 100).toFixed(1)
const mult = (last, first) => +(last / first).toFixed(2)

const yoy = (arr) => {
  const [a, b] = [arr[arr.length - 2], arr[arr.length - 1]]
  return +(((b / a) - 1) * 100).toFixed(1)
}

const toneOf = (v) => {
  if (v >= 30) return 'pos-strong'
  if (v >= 10) return 'pos'
  if (v >= 0)  return 'neu'
  return 'neg'
}

// ── Sector hero data ──
const sectorMeta = [
  { key: 'industry',     icon: 'factory',       label: 'Промышленность',  unit: 'млрд сум', color: '#0054A6' },
  { key: 'services',     icon: 'handyman',      label: 'Услуги',          unit: 'млрд сум', color: '#0EA5E9' },
  { key: 'trade',        icon: 'storefront',    label: 'Розн. торговля',  unit: 'млрд сум', color: '#06B6D4' },
  { key: 'investments',  icon: 'savings',       label: 'Инвестиции',      unit: 'млрд сум', color: '#F59E0B' },
  { key: 'construction', icon: 'construction',  label: 'Строительство',   unit: 'млрд сум', color: '#D97706' },
  { key: 'agriculture',  icon: 'agriculture',   label: 'Сельхоз',         unit: 'млрд сум', color: '#10B981' },
]

const sectorCards = computed(() =>
  sectorMeta.map((s) => {
    const series = D.fiveYear[s.key]
    const last = series[series.length - 1]
    const first = series[0]
    const yoyPct = yoy(series)
    const realKey = s.key === 'investments' ? null : s.key
    const realPct = realKey && D.regionReal[realKey] != null ? D.regionReal[realKey] : null
    return {
      ...s,
      total2025: last,
      yoy: yoyPct,
      yoyTone: toneOf(yoyPct),
      regionReal: realPct,
      mult5y: mult(last, first),
      pct5y: pct(last, first),
      series,
    }
  }),
)

// ── Investment surge breakout ──
const investData = computed(() => ({
  labels: D.fiveYearLabels.map(String),
  datasets: [{
    label: 'Инвестиции, млрд сум',
    data: D.fiveYear.investments,
    backgroundColor: D.fiveYear.investments.map((_, i, a) =>
      i === a.length - 1 ? '#F59E0B' : 'rgba(245,158,11,0.45)',
    ),
    borderRadius: 8,
    borderSkipped: false,
  }],
}))
const investOpts = {
  plugins: { legend: { display: false }, tooltip: { callbacks: {
    label: (ctx) => ` ${fmt(ctx.parsed.y, 1)} млрд сум`,
  } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 12, weight: 600 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 11 }, callback: (v) => `${v >= 1000 ? (v/1000).toFixed(1)+'к' : v}` } },
  },
}

// ── Population history ──
const popData = computed(() => ({
  labels: D.populationFiveYearLabels.map(String),
  datasets: [{
    label: 'Население, тыс.',
    data: D.populationFiveYear,
    borderColor: '#0054A6',
    backgroundColor: 'rgba(0,84,166,0.10)',
    borderWidth: 3,
    fill: true,
    tension: 0.4,
    pointRadius: 5,
    pointHoverRadius: 7,
    pointBackgroundColor: '#fff',
    pointBorderColor: '#0054A6',
    pointBorderWidth: 2.5,
  }],
}))
const popOpts = {
  plugins: { legend: { display: false }, tooltip: { callbacks: {
    label: (ctx) => ` ${fmt(ctx.parsed.y, 1)} тыс. чел.`,
  } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 12, weight: 600 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 11 } } },
  },
}

// ── Age structure (vertical bars) ──
const ageData = computed(() => {
  const labels = Object.keys(D.ageGroups)
  const values = Object.values(D.ageGroups)
  return {
    labels,
    datasets: [{
      label: 'Чел.',
      data: values,
      backgroundColor: values.map((v, i) => {
        // Working-age 20-59 highlighted
        const wa = ['20–24','25–29','30–34','35–39','40–49','50–59']
        return wa.includes(labels[i]) ? '#0054A6' : 'rgba(0,84,166,0.35)'
      }),
      borderRadius: 6,
      borderSkipped: false,
    }],
  }
})
const ageOpts = {
  plugins: { legend: { display: false }, tooltip: { callbacks: {
    label: (ctx) => ` ${fmt(ctx.parsed.y)} чел. (${(ctx.parsed.y / 313597 * 100).toFixed(1)}%)`,
  } } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 11, weight: 600 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 10 }, callback: (v) => v >= 1000 ? `${v/1000}к` : v } },
  },
}

// ── Vital stats sparklines ──
const naturalIncrease2025 = D.vital.natural[D.vital.natural.length - 1]

// ── Sector mix donut ──
const sectorMixData = computed(() => {
  const labels = ['Промышленность', 'Торговля', 'Услуги', 'Строительство', 'Сельхоз']
  const data = [39.5, 27.7, 26.7, 4.5, 1.6]
  const colors = ['#0054A6', '#06B6D4', '#0EA5E9', '#D97706', '#10B981']
  return {
    labels,
    datasets: [{
      data,
      backgroundColor: colors,
      borderWidth: 0,
      hoverOffset: 12,
    }],
  }
})
const sectorMixOpts = {
  cutout: '66%',
  plugins: { legend: { display: false }, tooltip: { callbacks: {
    label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%`,
  } } },
}

// ── Per-capita comparative ──
const compareSectors = ['industry', 'services', 'trade', 'investments', 'construction']
const compareLabels = {
  industry: 'Промышленность', services: 'Услуги', trade: 'Торговля',
  investments: 'Инвестиции', construction: 'Строительство',
}
const compareKeyMap = { industry: 'industry', services: 'services', trade: 'trade', investments: 'invest', construction: 'construction' }
const compareData = computed(() => ({
  labels: compareSectors.map((k) => compareLabels[k]),
  datasets: [
    {
      label: 'Коканд',
      data: compareSectors.map((k) => D.perCapitaCompare.Qoqon[compareKeyMap[k]]),
      backgroundColor: '#F59E0B',
      borderRadius: 6,
    },
    {
      label: 'Фергана',
      data: compareSectors.map((k) => D.perCapitaCompare.Fergana[compareKeyMap[k]]),
      backgroundColor: '#0054A6',
      borderRadius: 6,
    },
    {
      label: 'Маргилан',
      data: compareSectors.map((k) => D.perCapitaCompare.Margilan[compareKeyMap[k]]),
      backgroundColor: '#10B981',
      borderRadius: 6,
    },
  ],
}))
const compareOpts = {
  indexAxis: 'y',
  plugins: { legend: { position: 'bottom', labels: { font: { size: 12, weight: 600 }, boxWidth: 12, padding: 14 } }, tooltip: { callbacks: {
    label: (ctx) => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.x)} тыс. сум`,
  } } },
  scales: {
    x: { grid: { color: '#F0F4FA' }, ticks: { font: { size: 11 }, callback: (v) => v >= 1000 ? `${(v/1000).toFixed(0)}к` : v } },
    y: { grid: { display: false }, ticks: { font: { size: 12, weight: 600 } } },
  },
}

// ── AI strategic recommendations (from i18n) ──
const aiOverall = computed(() => {
  const path = `district.aiAnalysis.${KEY}.overall`
  if (!te(`${path}.title`)) return null
  return {
    title: t(`${path}.title`),
    summary: t(`${path}.summary`),
    tags: tm(`${path}.tags`) || [],
  }
})
const aiSummary = computed(() => {
  const path = `district.aiAnalysis.${KEY}.summary`
  if (!te(`${path}.title`)) return null
  return {
    title: t(`${path}.title`),
    summary: t(`${path}.summary`),
    insights: tm(`${path}.insights`) || [],
    risks: tm(`${path}.risks`) || [],
  }
})

// ── Navigation ──
function back() {
  const q = { ...route.query }
  delete q.district
  router.push({ path: route.path, query: q })
}

const sectorMix = [
  { label: 'Промышленность', pct: 39.5, color: '#0054A6' },
  { label: 'Розн. торговля', pct: 27.7, color: '#06B6D4' },
  { label: 'Услуги',         pct: 26.7, color: '#0EA5E9' },
  { label: 'Строительство',  pct:  4.5, color: '#D97706' },
  { label: 'Сельхоз',        pct:  1.6, color: '#10B981' },
]
</script>

<template>
  <div class="qoq-shell">
    <!-- ============== HERO — variant A (glassmorphism, default) ============== -->
    <header v-if="heroStyle === 'A'" class="qoq-hero">
      <div class="qoq-hero-bg" />
      <div class="qoq-hero-content">
        <div class="qoq-hero-toolbar">
          <button class="qoq-back" @click="back">
            <AppIcon name="arrow_back" /> Назад к Ферганской области
          </button>
          <div class="qoq-style-toggle">
            <span class="qoq-style-label">Стиль:</span>
            <button :class="['qoq-style-btn', heroStyle === 'A' && 'active']" @click="setHero('A')">A</button>
            <button :class="['qoq-style-btn', heroStyle === 'B' && 'active']" @click="setHero('B')">B</button>
          </div>
        </div>
        <div class="qoq-hero-eyebrow">Qoʻqon shahri · Индустриальный хаб западной Ферганы</div>
        <h1 class="qoq-hero-title">Коканд</h1>
        <p class="qoq-hero-sub">
          Industrial leader of the Western Fergana valley · 2025 yanvar–dekabr · farstat.uz
        </p>
        <div class="qoq-quick-stats">
          <div class="qoq-quick">
            <div class="qoq-quick-label">Население</div>
            <div class="qoq-quick-val">{{ fmt(D.popK, 1) }} <span class="qoq-quick-u">тыс.</span></div>
            <div class="qoq-quick-sub">1 янв 2026 · 100% урбан</div>
          </div>
          <div class="qoq-quick">
            <div class="qoq-quick-label">Площадь</div>
            <div class="qoq-quick-val">{{ D.area }} <span class="qoq-quick-u">км²</span></div>
            <div class="qoq-quick-sub">Самый компактный</div>
          </div>
          <div class="qoq-quick">
            <div class="qoq-quick-label">Плотность</div>
            <div class="qoq-quick-val">{{ fmt(D.density) }} <span class="qoq-quick-u">/км²</span></div>
            <div class="qoq-quick-sub">★ Лидер вилоята</div>
          </div>
          <div class="qoq-quick">
            <div class="qoq-quick-label">Тип</div>
            <div class="qoq-quick-val qoq-quick-text">Город</div>
            <div class="qoq-quick-sub">Областного подчинения</div>
          </div>
        </div>
        <button class="qoq-detail-cta" @click="openDetail">
          <AppIcon name="dataset" />
          <span>
            <span class="qoq-cta-title">Подробные данные Golden Mart</span>
            <span class="qoq-cta-sub">21 раздел · полный шаблон города</span>
          </span>
          <AppIcon name="arrow_forward" />
        </button>
      </div>
    </header>

    <!-- ============== HERO — variant B (rounded executive brief, Fergana style) ============== -->
    <div v-else class="qoq-heroB-wrap">
      <div class="qoq-hero-toolbar dark">
        <button class="qoq-back outline" @click="back">
          <AppIcon name="arrow_back" /> Назад к Ферганской области
        </button>
        <div class="qoq-style-toggle outline">
          <span class="qoq-style-label">Стиль:</span>
          <button :class="['qoq-style-btn', heroStyle === 'A' && 'active']" @click="setHero('A')">A</button>
          <button :class="['qoq-style-btn', heroStyle === 'B' && 'active']" @click="setHero('B')">B</button>
        </div>
      </div>

      <header class="qoq-briefB">
        <div class="qoq-briefB-glow" />
        <div class="qoq-briefB-content">
          <div class="qoq-briefB-eyebrow">EXECUTIVE BRIEF · ГОРОД</div>
          <h1 class="qoq-briefB-title">г. Коканд</h1>
          <p class="qoq-briefB-sub">
            {{ fmt(D.popK, 1) }} тыс. жителей · {{ D.area }} км² · плотность {{ fmt(D.density) }}/км²
          </p>
          <div class="qoq-briefB-kpis">
            <div class="qoq-briefB-kpi">
              <div class="qoq-briefB-kpi-label">Промышленность</div>
              <div class="qoq-briefB-kpi-val">9 410</div>
              <div class="qoq-briefB-kpi-foot">
                <span class="qoq-briefB-kpi-unit">млрд сум</span>
                <span class="qoq-briefB-delta tone-green">+50,2%</span>
              </div>
            </div>
            <div class="qoq-briefB-kpi">
              <div class="qoq-briefB-kpi-label">Услуги</div>
              <div class="qoq-briefB-kpi-val">6 371</div>
              <div class="qoq-briefB-kpi-foot">
                <span class="qoq-briefB-kpi-unit">млрд сум</span>
                <span class="qoq-briefB-delta tone-green">+29,6%</span>
              </div>
            </div>
            <div class="qoq-briefB-kpi">
              <div class="qoq-briefB-kpi-label">Инвестиции</div>
              <div class="qoq-briefB-kpi-val">4 111</div>
              <div class="qoq-briefB-kpi-foot">
                <span class="qoq-briefB-kpi-unit">млрд сум</span>
                <span class="qoq-briefB-delta tone-green">×4,1</span>
              </div>
            </div>
            <div class="qoq-briefB-kpi">
              <div class="qoq-briefB-kpi-label">Прирост</div>
              <div class="qoq-briefB-kpi-val">+5 410</div>
              <div class="qoq-briefB-kpi-foot">
                <span class="qoq-briefB-kpi-unit">2025</span>
                <span class="qoq-briefB-delta tone-blue">★ рекорд</span>
              </div>
            </div>
            <div class="qoq-briefB-kpi">
              <div class="qoq-briefB-kpi-label">Население</div>
              <div class="qoq-briefB-kpi-val">319 600</div>
              <div class="qoq-briefB-kpi-foot">
                <span class="qoq-briefB-kpi-unit">человек</span>
                <span class="qoq-briefB-delta tone-blue">городское</span>
              </div>
            </div>
          </div>
          <button class="qoq-detail-cta on-brief" @click="openDetail">
            <AppIcon name="dataset" />
            <span>
              <span class="qoq-cta-title">Подробные данные Golden Mart</span>
              <span class="qoq-cta-sub">21 раздел · 6 тематических вкладок</span>
            </span>
            <AppIcon name="arrow_forward" />
          </button>
        </div>
      </header>
    </div>

    <!-- ============== SECTOR HERO GRID ============== -->
    <section class="qoq-section">
      <div class="qoq-section-head">
        <div>
          <div class="qoq-eyebrow">01 · Шесть секторов</div>
          <h2 class="qoq-h2">Структура экономики 2025</h2>
          <p class="qoq-lede">
            Все шесть верифицированных секторов показали двузначный номинальный рост в 2025 г.
            Промышленность +50,2% — рекорд области, при региональном реальном росте всего +7,3%.
          </p>
        </div>
        <div class="qoq-source-tag">farstat.uz · ratlib таблицы Tumanlar bo'yicha</div>
      </div>

      <div class="qoq-sector-grid">
        <article v-for="s in sectorCards" :key="s.key" class="qoq-card qoq-sector" :style="{ '--accent': s.color }">
          <header class="qoq-sector-head">
            <div class="qoq-sector-icon"><AppIcon :name="s.icon" /></div>
            <div class="qoq-sector-name">{{ s.label }}</div>
          </header>
          <div class="qoq-sector-val">
            {{ fmt(s.total2025, 1) }}
            <span class="qoq-sector-u">{{ s.unit }}</span>
          </div>
          <div class="qoq-sector-meta">
            <span class="qoq-chip" :class="`tone-${s.yoyTone}`">
              {{ s.yoy >= 0 ? '+' : '' }}{{ s.yoy }}% YoY
            </span>
            <span v-if="s.regionReal != null" class="qoq-chip-soft">
              вилоята real +{{ s.regionReal }}%
            </span>
          </div>
          <div class="qoq-spark-wrap">
            <FcSparkline :data="s.series" :color="s.color" :height="50" />
          </div>
          <footer class="qoq-sector-foot">
            <span class="qoq-mult">×{{ s.mult5y }}</span>
            <span class="qoq-mult-label">за 5 лет {{ s.pct5y >= 0 ? '+' : '' }}{{ s.pct5y }}%</span>
          </footer>
        </article>
      </div>
    </section>

    <!-- ============== INVESTMENT SURGE BREAKOUT ============== -->
    <section class="qoq-section">
      <div class="qoq-card qoq-breakout">
        <div class="qoq-breakout-side">
          <div class="qoq-eyebrow gold">02 · Инвестиционный взрыв</div>
          <h2 class="qoq-h2">Капитал ×4,1 за 5 лет</h2>
          <p class="qoq-lede">
            Самый сильный приток инвестиций в основной капитал среди городов Ферганской области.
            В 2025 году объём удвоился к 2024 году (×2,1) — индикатор веры рынка в город.
          </p>
          <div class="qoq-stat-row">
            <div class="qoq-stat-tile">
              <div class="qoq-stat-num">+312%</div>
              <div class="qoq-stat-lbl">5-летний рост (2021→2025)</div>
            </div>
            <div class="qoq-stat-tile">
              <div class="qoq-stat-num">×2,1</div>
              <div class="qoq-stat-lbl">2024 → 2025 (за один год)</div>
            </div>
            <div class="qoq-stat-tile">
              <div class="qoq-stat-num">4 111</div>
              <div class="qoq-stat-lbl">млрд сум в 2025 г.</div>
            </div>
          </div>
        </div>
        <div class="qoq-breakout-chart">
          <FcChart type="bar" :data="investData" :options="investOpts" :height="300" />
        </div>
      </div>
    </section>

    <!-- ============== POPULATION + VITAL ============== -->
    <section class="qoq-section qoq-grid-2">
      <div class="qoq-card">
        <div class="qoq-eyebrow">03 · Демография</div>
        <h2 class="qoq-h2">Население 2021 → 2026</h2>
        <p class="qoq-lede">
          Рост на 63,2 тыс. за 5 лет (+24,6%). Часть прироста между 2022 и 2023 — следствие
          административно-территориального изменения, не естественной демографии.
          Период совпадает с шаблоном Golden Mart.
        </p>
        <div class="qoq-chart-h300">
          <FcChart type="line" :data="popData" :options="popOpts" :height="280" />
        </div>
        <div class="qoq-annotation">
          <AppIcon name="info" />
          Скачок 2022→2023 (+44 тыс., +17%) — изменение админ-границ
        </div>
      </div>

      <div class="qoq-card qoq-vital">
        <div class="qoq-eyebrow">Естественный прирост 2025</div>
        <div class="qoq-vital-big">
          <span class="qoq-vital-num">+{{ fmt(naturalIncrease2025) }}</span>
          <span class="qoq-vital-tag">★ Рекорд области</span>
        </div>
        <div class="qoq-vital-grid">
          <div class="qoq-vital-cell">
            <div class="qoq-vital-cell-num">{{ fmt(D.vital.births[4]) }}</div>
            <div class="qoq-vital-cell-lbl">Рождений</div>
            <FcSparkline :data="D.vital.births" color="#10B981" :height="36" />
          </div>
          <div class="qoq-vital-cell">
            <div class="qoq-vital-cell-num">{{ fmt(D.vital.deaths[4]) }}</div>
            <div class="qoq-vital-cell-lbl">Смертей</div>
            <FcSparkline :data="D.vital.deaths" color="#94A3B8" :height="36" />
          </div>
          <div class="qoq-vital-cell qoq-vital-cell-acc">
            <div class="qoq-vital-cell-num">+{{ fmt(naturalIncrease2025) }}</div>
            <div class="qoq-vital-cell-lbl">Прирост</div>
            <FcSparkline :data="D.vital.natural" color="#0054A6" :height="36" />
          </div>
        </div>
        <p class="qoq-note">
          Самый высокий естественный прирост среди городов Ферганской области в 2025 г.
        </p>
      </div>
    </section>

    <!-- ============== AGE PYRAMID ============== -->
    <section class="qoq-section">
      <div class="qoq-card">
        <div class="qoq-section-head">
          <div>
            <div class="qoq-eyebrow">04 · Возрастная структура</div>
            <h2 class="qoq-h2">Возрастные группы · 1 янв 2025 · 313 597 чел.</h2>
            <p class="qoq-lede">
              0–15 лет: 96 649 (30,8%) · 20–59 лет: 161 535 (51,5%) · 60+: 35 568 (11,3%).
              Подсвечены трудоспособные группы 20–59 лет.
            </p>
          </div>
        </div>
        <div class="qoq-chart-h320">
          <FcChart type="bar" :data="ageData" :options="ageOpts" :height="320" />
        </div>
      </div>
    </section>

    <!-- ============== PER-CAPITA COMPARE ============== -->
    <section class="qoq-section qoq-grid-21">
      <div class="qoq-card">
        <div class="qoq-eyebrow">05 · Сравнение с вилоята</div>
        <h2 class="qoq-h2">На душу населения · тыс. сум</h2>
        <p class="qoq-lede">
          Коканд против Ферганы и Маргилана: индустриальный лидер по объёму, но по душе населения
          уступает Фергане; в торговле паритет с обоими, в строительстве — отставание.
        </p>
        <div class="qoq-chart-h360">
          <FcChart type="bar" :data="compareData" :options="compareOpts" :height="340" />
        </div>
      </div>

      <div class="qoq-card qoq-mix-card">
        <div class="qoq-eyebrow">06 · Структура секторов</div>
        <h2 class="qoq-h2">Доли в общем объёме</h2>
        <div class="qoq-mix-wrap">
          <div class="qoq-mix-chart">
            <FcChart type="doughnut" :data="sectorMixData" :options="sectorMixOpts" :height="240" />
            <div class="qoq-mix-center">
              <div class="qoq-mix-center-num">39,5%</div>
              <div class="qoq-mix-center-lbl">промышленности</div>
            </div>
          </div>
          <ul class="qoq-mix-legend">
            <li v-for="m in sectorMix" :key="m.label">
              <span class="qoq-mix-dot" :style="{ background: m.color }"></span>
              <span class="qoq-mix-name">{{ m.label }}</span>
              <span class="qoq-mix-pct">{{ m.pct }}%</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ============== AI STRATEGIC ============== -->
    <section v-if="aiOverall" class="qoq-section">
      <div class="qoq-card qoq-ai">
        <div class="qoq-ai-head">
          <div>
            <div class="qoq-eyebrow gold">07 · AI Стратегические выводы</div>
            <h2 class="qoq-h2">{{ aiOverall.title }}</h2>
          </div>
          <span class="qoq-badge">AI · Анализ по верифицированным данным</span>
        </div>
        <p class="qoq-ai-lede">{{ aiOverall.summary }}</p>
        <div class="qoq-ai-tags">
          <span v-for="(tag, i) in aiOverall.tags" :key="i" class="qoq-ai-tag">{{ tag }}</span>
        </div>

        <div v-if="aiSummary" class="qoq-ai-cols">
          <div>
            <div class="qoq-ai-col-head">
              <AppIcon name="check_circle" /> Инсайты
            </div>
            <ul class="qoq-ai-list">
              <li v-for="(item, i) in aiSummary.insights" :key="`i-${i}`">{{ item }}</li>
            </ul>
          </div>
          <div>
            <div class="qoq-ai-col-head amber">
              <AppIcon name="lightbulb" /> На что смотреть
            </div>
            <ul class="qoq-ai-list">
              <li v-for="(item, i) in aiSummary.risks" :key="`r-${i}`">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <footer class="qoq-foot">
      <div>
        Источник данных: <strong>farstat.uz</strong> · Tumanlar bo‘yicha таблицы (Jan-Dec 2025 preliminary).
        Шаблон Golden Mart · уровень города/тумана · 21 раздел атрибутов.
      </div>
      <div class="qoq-foot-key">qoqon_city · sandbox dashboard</div>
    </footer>
  </div>
</template>

<style scoped>
.qoq-shell {
  --bg: #F4F6FB;
  --surface: #FFFFFF;
  --ink: #0F1B2D;
  --ink-muted: #475569;
  --line: #E2E8F0;
  --primary: #0054A6;
  --primary-soft: rgba(0, 84, 166, 0.08);
  --gold: #F59E0B;
  --gold-soft: rgba(245, 158, 11, 0.10);
  --green: #10B981;
  --red: #DC2626;

  background: var(--bg);
  min-height: 100vh;
  font-family: 'Manrope', system-ui, sans-serif;
  color: var(--ink);
  padding-bottom: 80px;
}

/* ── HERO TOOLBAR (shared) ── */
.qoq-hero-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  gap: 12px; flex-wrap: wrap;
}
.qoq-style-toggle {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.16);
  padding: 4px; border-radius: 999px;
}
.qoq-style-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
  color: rgba(255,255,255,0.6); text-transform: uppercase;
  padding: 0 8px 0 10px;
}
.qoq-style-btn {
  background: transparent; border: none; cursor: pointer;
  width: 30px; height: 26px; border-radius: 999px;
  font-size: 12px; font-weight: 800; letter-spacing: 0.04em;
  color: rgba(255,255,255,0.7); transition: all 0.2s;
}
.qoq-style-btn:hover { color: #fff; }
.qoq-style-btn.active {
  background: #fff; color: #0F1B2D;
  box-shadow: 0 1px 3px rgba(0,0,0,0.18);
}

/* ── DETAIL CTA (shared between both heroes) ── */
.qoq-detail-cta {
  display: inline-flex; align-items: center; gap: 14px;
  margin-top: 28px; padding: 16px 22px;
  background: rgba(245,158,11,0.16);
  border: 1px solid rgba(245,158,11,0.40);
  border-radius: 14px; cursor: pointer;
  color: #FCD34D; font-family: inherit;
  transition: all 0.2s;
}
.qoq-detail-cta:hover {
  background: rgba(245,158,11,0.24);
  transform: translateX(4px);
}
.qoq-detail-cta.light {
  background: rgba(255,255,255,0.92);
  border-color: rgba(245,158,11,0.50);
  color: #B45309;
}
.qoq-detail-cta.light:hover { background: #fff; }
.qoq-detail-cta > span {
  display: flex; flex-direction: column; align-items: flex-start;
  text-align: left;
}
.qoq-cta-title { font-size: 15px; font-weight: 800; }
.qoq-cta-sub { font-size: 11px; font-weight: 600; opacity: 0.75; margin-top: 2px; }

/* ── HERO A — glassmorphism (default) ── */
.qoq-hero {
  position: relative;
  background:
    radial-gradient(800px 400px at 20% 0%, rgba(245,158,11,0.18), transparent 60%),
    radial-gradient(600px 300px at 80% 100%, rgba(14,165,233,0.20), transparent 60%),
    linear-gradient(135deg, #061B36 0%, #0A2848 50%, #103E6E 100%);
  color: #fff;
  overflow: hidden;
  padding: 64px 56px 80px;
}
.qoq-hero-bg {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask: radial-gradient(ellipse at 50% 30%, black 30%, transparent 80%);
  pointer-events: none;
}
.qoq-hero-content { position: relative; max-width: 1320px; margin: 0 auto; }
.qoq-back {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.16);
  color: #fff; font-size: 13px; font-weight: 700;
  padding: 8px 14px 8px 10px; border-radius: 999px; cursor: pointer;
  transition: background 0.2s;
}
.qoq-back:hover { background: rgba(255,255,255,0.16); }
.qoq-hero-eyebrow {
  margin-top: 28px;
  font-size: 12px; font-weight: 800; letter-spacing: 0.18em;
  color: #FCD34D; text-transform: uppercase;
}
.qoq-hero-title {
  font-size: clamp(56px, 8vw, 112px); line-height: 0.92; font-weight: 900;
  letter-spacing: -0.04em; margin: 12px 0 16px;
  background: linear-gradient(135deg, #fff 0%, #FCD34D 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.qoq-hero-sub {
  font-size: 16px; font-weight: 600; color: rgba(255,255,255,0.72);
  max-width: 720px; margin-bottom: 36px;
}
.qoq-quick-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  padding: 22px 28px; border-radius: 18px; backdrop-filter: blur(8px);
}
.qoq-quick { display: flex; flex-direction: column; gap: 6px; }
.qoq-quick-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.14em;
  color: rgba(255,255,255,0.6); text-transform: uppercase;
}
.qoq-quick-val { font-size: 32px; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; }
.qoq-quick-text { font-size: 24px; }
.qoq-quick-u { font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.6); margin-left: 4px; }
.qoq-quick-sub { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.5); }

/* ── HERO B — Fergana-style executive brief (rounded blue panel) ── */
.qoq-heroB-wrap {
  background: var(--bg);
  padding: 28px 56px 0;
}
.qoq-hero-toolbar.dark {
  max-width: 1320px; margin: 0 auto 16px;
}
.qoq-back.outline {
  background: #fff; border: 1px solid var(--line); color: var(--ink);
}
.qoq-back.outline:hover { background: rgba(0,84,166,0.04); }
.qoq-style-toggle.outline {
  background: #fff; border: 1px solid var(--line);
}
.qoq-style-toggle.outline .qoq-style-label { color: var(--ink-muted); }
.qoq-style-toggle.outline .qoq-style-btn { color: var(--ink-muted); }
.qoq-style-toggle.outline .qoq-style-btn.active {
  background: var(--primary); color: #fff;
}

.qoq-briefB {
  max-width: 1320px; margin: 0 auto;
  background: linear-gradient(135deg, #001b3d 0%, #003D7C 65%, #0054A6 100%);
  color: #fff;
  border-radius: 24px;
  padding: clamp(28px, 3vw, 40px);
  box-shadow: 0 24px 56px -24px rgba(0,27,61,0.40);
  position: relative;
  overflow: hidden;
}
.qoq-briefB-glow {
  position: absolute; top: -50%; right: -20%;
  width: 700px; height: 700px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 60%);
  pointer-events: none;
}
.qoq-briefB-content { position: relative; }
.qoq-briefB-eyebrow {
  font-size: 13px; font-weight: 800; letter-spacing: 0.16em;
  color: #93C5FD; text-transform: uppercase;
}
.qoq-briefB-title {
  font-size: clamp(40px, 6vw, 64px); font-weight: 900;
  letter-spacing: -0.03em; line-height: 1.0;
  margin: 12px 0 16px; color: #fff;
}
.qoq-briefB-sub {
  font-size: 15px; font-weight: 600;
  color: rgba(191,219,254,0.80);
  margin: 0 0 28px;
}
.qoq-briefB-kpis {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px;
}
.qoq-briefB-kpi {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 18px;
  padding: clamp(18px, 1.6vw, 26px);
  display: flex; flex-direction: column; justify-content: space-between;
  min-height: clamp(140px, 11vw, 170px);
  box-shadow: 0 10px 25px -15px rgba(0,0,0,0.35);
  transition: background 0.2s, transform 0.2s, border-color 0.2s;
}
.qoq-briefB-kpi:hover {
  background: rgba(255,255,255,0.13);
  border-color: rgba(255,255,255,0.24);
  transform: translateY(-2px);
}
.qoq-briefB-kpi-label {
  font-size: 12px; font-weight: 800; letter-spacing: 0.14em;
  text-transform: uppercase; color: #BFDBFE;
}
.qoq-briefB-kpi-val {
  font-size: clamp(28px, 2.8vw, 42px); line-height: 1; font-weight: 900;
  letter-spacing: -0.03em; color: #fff;
  font-variant-numeric: tabular-nums;
  margin-top: 14px;
}
.qoq-briefB-kpi-foot {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; margin-top: 14px; padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.10);
}
.qoq-briefB-kpi-unit {
  font-size: 12px; font-weight: 700;
  color: rgba(191,219,254,0.80); letter-spacing: 0.02em;
}
.qoq-briefB-delta {
  font-size: 12px; font-weight: 800;
  padding: 4px 10px; border-radius: 999px; letter-spacing: 0.02em;
  font-variant-numeric: tabular-nums; white-space: nowrap;
}
.qoq-briefB-delta.tone-green {
  color: #A7F3D0; background: rgba(16,185,129,0.18);
}
.qoq-briefB-delta.tone-blue {
  color: #BFDBFE; background: rgba(59,130,246,0.22);
}

.qoq-detail-cta.on-brief {
  margin-top: 28px;
  background: rgba(252,211,77,0.16);
  border-color: rgba(252,211,77,0.36);
  color: #FCD34D;
}
.qoq-detail-cta.on-brief:hover { background: rgba(252,211,77,0.24); }

@media (max-width: 1100px) {
  .qoq-briefB-kpis { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 700px) {
  .qoq-briefB-kpis { grid-template-columns: repeat(2, 1fr); }
  .qoq-heroB-wrap { padding: 20px 20px 0; }
}

/* ── SECTIONS ── */
.qoq-section {
  max-width: 1320px; margin: 0 auto; padding: 56px 56px 0;
}
.qoq-section-head {
  display: flex; justify-content: space-between; align-items: flex-end;
  flex-wrap: wrap; gap: 20px; margin-bottom: 28px;
}
.qoq-eyebrow {
  font-size: 11px; font-weight: 800; letter-spacing: 0.16em;
  color: var(--primary); text-transform: uppercase; margin-bottom: 8px;
}
.qoq-eyebrow.gold { color: var(--gold); }
.qoq-h2 {
  font-size: clamp(28px, 3.2vw, 40px); font-weight: 900;
  letter-spacing: -0.025em; line-height: 1.05; margin: 0 0 12px;
}
.qoq-lede {
  font-size: 15px; line-height: 1.55; color: var(--ink-muted);
  font-weight: 500; max-width: 760px; margin: 0;
}
.qoq-source-tag {
  display: inline-flex; align-items: center; padding: 7px 14px;
  background: var(--primary-soft); color: var(--primary);
  font-size: 11px; font-weight: 800; letter-spacing: 0.06em;
  border-radius: 999px; text-transform: lowercase;
}
.qoq-card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 20px; padding: 28px;
  box-shadow: 0 1px 0 rgba(15,23,42,0.02), 0 8px 24px -12px rgba(15,23,42,0.08);
}
.qoq-grid-2 { display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; }
.qoq-grid-21 { display: grid; grid-template-columns: 1.6fr 1fr; gap: 24px; }
@media (max-width: 1100px) {
  .qoq-grid-2, .qoq-grid-21 { grid-template-columns: 1fr; }
  .qoq-section, .qoq-hero { padding-left: 24px; padding-right: 24px; }
}

/* ── SECTOR HERO GRID ── */
.qoq-sector-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}
@media (max-width: 1024px) { .qoq-sector-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  { .qoq-sector-grid { grid-template-columns: 1fr; } }

.qoq-sector {
  position: relative; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s;
  display: flex; flex-direction: column; gap: 14px;
  padding: 24px 24px 20px;
}
.qoq-sector::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--accent);
}
.qoq-sector:hover {
  transform: translateY(-2px);
  box-shadow: 0 1px 0 rgba(15,23,42,0.02), 0 18px 36px -16px rgba(15,23,42,0.16);
}
.qoq-sector-head {
  display: flex; align-items: center; gap: 12px;
}
.qoq-sector-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent);
}
.qoq-sector-name { font-size: 13px; font-weight: 700; color: var(--ink-muted); letter-spacing: 0.02em; }
.qoq-sector-val {
  font-size: 38px; font-weight: 900; line-height: 1; letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums;
}
.qoq-sector-u { font-size: 12px; font-weight: 700; color: var(--ink-muted); margin-left: 6px; letter-spacing: 0.02em; }
.qoq-sector-meta {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.qoq-chip {
  padding: 4px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
  font-variant-numeric: tabular-nums;
}
.qoq-chip.tone-pos-strong { background: rgba(16,185,129,0.14); color: #047857; }
.qoq-chip.tone-pos        { background: rgba(16,185,129,0.10); color: #059669; }
.qoq-chip.tone-neu        { background: rgba(100,116,139,0.12); color: #475569; }
.qoq-chip.tone-neg        { background: rgba(220,38,38,0.12);   color: #b91c1c; }
.qoq-chip-soft {
  padding: 4px 10px; border-radius: 999px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.04em;
  background: rgba(15,23,42,0.05); color: #475569;
}
.qoq-spark-wrap { height: 50px; }
.qoq-sector-foot {
  display: flex; align-items: baseline; gap: 8px;
  border-top: 1px dashed var(--line); padding-top: 12px;
}
.qoq-mult { font-size: 22px; font-weight: 900; color: var(--ink); font-variant-numeric: tabular-nums; }
.qoq-mult-label { font-size: 12px; font-weight: 600; color: var(--ink-muted); }

/* ── BREAKOUT ── */
.qoq-breakout {
  display: grid; grid-template-columns: 1fr 1.3fr; gap: 32px; align-items: center;
  background:
    linear-gradient(135deg, rgba(245,158,11,0.06) 0%, rgba(245,158,11,0) 50%),
    var(--surface);
  border-color: rgba(245,158,11,0.20);
  padding: 36px;
}
@media (max-width: 1024px) { .qoq-breakout { grid-template-columns: 1fr; } }
.qoq-stat-row { display: flex; gap: 16px; margin-top: 24px; flex-wrap: wrap; }
.qoq-stat-tile {
  flex: 1; min-width: 130px;
  background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.20);
  padding: 16px 18px; border-radius: 14px;
}
.qoq-stat-num {
  font-size: 28px; font-weight: 900; color: var(--gold);
  font-variant-numeric: tabular-nums; letter-spacing: -0.02em; line-height: 1;
}
.qoq-stat-lbl { font-size: 11px; font-weight: 700; color: var(--ink-muted); margin-top: 6px; letter-spacing: 0.02em; }

/* ── POPULATION + VITAL ── */
.qoq-chart-h300, .qoq-chart-h320, .qoq-chart-h360 { margin-top: 16px; }
.qoq-annotation {
  display: inline-flex; align-items: center; gap: 6px;
  margin-top: 12px; padding: 6px 12px; border-radius: 999px;
  background: rgba(245,158,11,0.10); color: #B45309;
  font-size: 11px; font-weight: 700; letter-spacing: 0.02em;
}
.qoq-vital { display: flex; flex-direction: column; gap: 16px; }
.qoq-vital-big { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.qoq-vital-num {
  font-size: 56px; font-weight: 900; color: var(--primary);
  font-variant-numeric: tabular-nums; letter-spacing: -0.03em; line-height: 1;
}
.qoq-vital-tag {
  background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff;
  padding: 5px 12px; border-radius: 999px;
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
}
.qoq-vital-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.qoq-vital-cell {
  background: rgba(0,84,166,0.04); border: 1px solid var(--line);
  padding: 14px; border-radius: 12px;
}
.qoq-vital-cell-acc { background: rgba(0,84,166,0.10); border-color: rgba(0,84,166,0.20); }
.qoq-vital-cell-num {
  font-size: 22px; font-weight: 900; color: var(--ink);
  font-variant-numeric: tabular-nums; line-height: 1.1;
}
.qoq-vital-cell-lbl {
  font-size: 11px; font-weight: 700; color: var(--ink-muted);
  margin: 4px 0 8px; letter-spacing: 0.04em;
}
.qoq-note { font-size: 12px; color: var(--ink-muted); font-weight: 500; margin: 0; }

/* ── SECTOR MIX DONUT ── */
.qoq-mix-wrap { display: flex; align-items: center; gap: 16px; margin-top: 16px; }
.qoq-mix-chart { position: relative; width: 240px; flex-shrink: 0; }
.qoq-mix-center {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; pointer-events: none;
}
.qoq-mix-center-num {
  font-size: 32px; font-weight: 900; color: var(--primary);
  font-variant-numeric: tabular-nums; line-height: 1;
}
.qoq-mix-center-lbl {
  font-size: 10px; font-weight: 700; color: var(--ink-muted);
  letter-spacing: 0.06em; text-transform: uppercase; text-align: center;
}
.qoq-mix-legend { list-style: none; padding: 0; margin: 0; flex: 1; display: flex; flex-direction: column; gap: 10px; }
.qoq-mix-legend li {
  display: flex; align-items: center; gap: 10px;
  padding-bottom: 8px; border-bottom: 1px dashed var(--line);
}
.qoq-mix-legend li:last-child { border-bottom: none; }
.qoq-mix-dot { width: 12px; height: 12px; border-radius: 4px; flex-shrink: 0; }
.qoq-mix-name { flex: 1; font-size: 13px; font-weight: 600; }
.qoq-mix-pct { font-size: 14px; font-weight: 800; font-variant-numeric: tabular-nums; }

/* ── AI ── */
.qoq-ai {
  background:
    linear-gradient(135deg, rgba(0,84,166,0.04) 0%, rgba(245,158,11,0.04) 100%),
    var(--surface);
}
.qoq-ai-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 16px; flex-wrap: wrap; margin-bottom: 16px;
}
.qoq-badge {
  padding: 7px 14px; background: var(--primary); color: #fff;
  border-radius: 999px; font-size: 11px; font-weight: 800; letter-spacing: 0.06em;
}
.qoq-ai-lede {
  font-size: 15px; line-height: 1.6; color: var(--ink);
  font-weight: 500; margin: 0 0 16px;
}
.qoq-ai-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }
.qoq-ai-tag {
  padding: 6px 14px; background: rgba(0,84,166,0.08); color: var(--primary);
  border-radius: 999px; font-size: 12px; font-weight: 700;
}
.qoq-ai-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 800px) { .qoq-ai-cols { grid-template-columns: 1fr; } }
.qoq-ai-col-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 800; color: var(--green);
  letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 12px;
}
.qoq-ai-col-head.amber { color: #B45309; }
.qoq-ai-list { list-style: none; padding: 0; margin: 0; }
.qoq-ai-list li {
  position: relative; padding: 8px 0 8px 18px;
  font-size: 14px; line-height: 1.5; color: var(--ink);
  border-bottom: 1px dashed var(--line);
}
.qoq-ai-list li::before {
  content: '→'; position: absolute; left: 0; color: var(--primary); font-weight: 800;
}
.qoq-ai-list li:last-child { border-bottom: none; }

/* ── FOOTER ── */
.qoq-foot {
  max-width: 1320px; margin: 56px auto 0; padding: 24px 56px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: var(--ink-muted); border-top: 1px solid var(--line);
  flex-wrap: wrap; gap: 12px;
}
.qoq-foot-key {
  font-family: ui-monospace, monospace; font-size: 11px;
  color: var(--ink-muted); padding: 4px 10px;
  background: rgba(15,23,42,0.04); border-radius: 6px;
}
</style>
