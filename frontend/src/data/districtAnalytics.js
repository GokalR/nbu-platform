// Per-district analytics for Fergana oblast (19 entries).
// Values are scaled from population + the district profile so every drill-down
// screen is populated realistically. The shape matches buildAnalytics() from
// regionAnalytics.js so the existing DistrictAnalyticsView tabs can render it.
//
// All user-visible labels accept a `t` translator (vue-i18n). Callers without
// translation context can omit it — the identity fallback returns the key.

import { districtByKey } from './districts'
import { samarqandDistricts, samarqandByKey } from './samarqand'

// Heuristic profile per district: sector mix, infra maturity, growth tilt.
// industry/agri/services/trade sum to 100. growth is % grp/yr. infra is 0–1.
// Fergana city & Margilan use REAL_DATA below; profiles kept for score computation.
const PROFILE = {
  fargona_city:  { industry: 42, agri:  8, services: 32, trade: 18, growth: 9.8, infra: 0.92, tourism: 0.8, textile: 0.6, enclave: false },
  margilon_city: { industry: 19.4, agri: 6.5, services: 23.8, trade: 38.2, growth: 9.1, infra: 0.86, tourism: 0.9, textile: 1.0, enclave: false },
  qoqon_city:    { industry: 40, agri:  6, services: 30, trade: 24, growth: 8.9, infra: 0.88, tourism: 0.8, textile: 0.5, enclave: false },
  quvasoy_city:  { industry: 64, agri:  6, services: 18, trade: 12, growth: 8.2, infra: 0.78, tourism: 0.3, textile: 0.2, enclave: false },
  oltiariq:      { industry: 28, agri: 48, services: 14, trade: 10, growth: 7.8, infra: 0.58, tourism: 0.2, textile: 0.3, enclave: false },
  beshariq:      { industry: 24, agri: 52, services: 14, trade: 10, growth: 7.2, infra: 0.55, tourism: 0.1, textile: 0.2, enclave: false },
  bogdod:        { industry: 22, agri: 56, services: 12, trade: 10, growth: 6.9, infra: 0.52, tourism: 0.1, textile: 0.2, enclave: false },
  buvayda:       { industry: 22, agri: 58, services: 12, trade:  8, growth: 6.8, infra: 0.50, tourism: 0.1, textile: 0.2, enclave: false },
  dangara:       { industry: 26, agri: 50, services: 14, trade: 10, growth: 7.1, infra: 0.55, tourism: 0.2, textile: 0.4, enclave: false },
  farhona:       { industry: 34, agri: 40, services: 16, trade: 10, growth: 8.0, infra: 0.68, tourism: 0.3, textile: 0.4, enclave: false },
  furqat:        { industry: 20, agri: 60, services: 12, trade:  8, growth: 6.5, infra: 0.48, tourism: 0.1, textile: 0.2, enclave: false },
  qoshtepa:      { industry: 32, agri: 44, services: 14, trade: 10, growth: 7.5, infra: 0.60, tourism: 0.2, textile: 0.3, enclave: false },
  quva:          { industry: 30, agri: 46, services: 14, trade: 10, growth: 7.6, infra: 0.62, tourism: 0.4, textile: 0.4, enclave: false },
  rishton:       { industry: 34, agri: 42, services: 14, trade: 10, growth: 7.4, infra: 0.60, tourism: 0.9, textile: 0.3, enclave: false }, // ceramics
  sox:           { industry: 16, agri: 64, services: 12, trade:  8, growth: 5.8, infra: 0.38, tourism: 0.1, textile: 0.1, enclave: true },  // Tajik enclave
  toshloq:       { industry: 28, agri: 48, services: 14, trade: 10, growth: 7.3, infra: 0.58, tourism: 0.2, textile: 0.3, enclave: false },
  uchkoprik:     { industry: 26, agri: 50, services: 14, trade: 10, growth: 7.0, infra: 0.55, tourism: 0.1, textile: 0.2, enclave: false },
  ozbekiston:    { industry: 30, agri: 46, services: 14, trade: 10, growth: 7.5, infra: 0.60, tourism: 0.2, textile: 0.3, enclave: false },
  yozyovon:      { industry: 24, agri: 54, services: 12, trade: 10, growth: 6.9, infra: 0.52, tourism: 0.1, textile: 0.2, enclave: false },
  // Samarkand viloyat — region-level pseudo-entry (real data verified from NBU Excel briefs)
  samarqand_region: { industry: 17.4, agri: 28.5, services: 47.7, trade: 0, growth: 8.5, infra: 0.7, tourism: 0.9, textile: 0.4, enclave: false },
}

// ── Real data from NBU Data Office dashboards (farstat.uz / Margilan brief) ──
// Sources: dashboard_fergan_city.html, DASHBOARD_margilan_city.html
const REAL_DATA = {
  fargona_city: {
    // Verified scalars — farstat.uz district-breakdown PDFs, Jan-Dec 2025
    // preliminary (folder fergana/, "Tumanlar bo'yicha ..." tables).
    populationK: 335.1,
    area: 110,
    // 2025 sector totals (mlrd soʻm, current prices)
    industryBln: 12666.6,
    investBln: 7128.4,
    servicesBln: 12191.0,
    tradeBln: 6562.8,
    constructionBln: 3276.6,
    agricultureBln: 1020.3,
    mahallas: 74,
    perCapita: { industry: 38187, invest: 21491, services: 36753, trade: 19785, construction: 9878 },
    // Nominal YoY growth 2025/2024 (% — current prices, derived from PDFs)
    industryGrowthPct: 112.1,
    servicesGrowthPct: 131.1,
    tradeGrowthPct: 121.6,
    investGrowthPct: 137.5,
    agricultureGrowthPct: 122.5,
    constructionGrowth: 114.1,
    // 5-year history 2021-2025 (mlrd soʻm, current prices) — verified from
    // farstat.uz district-breakdown PDFs, used for trend charts.
    fiveYear: {
      industry:     [7075.5, 6935.4, 10296.9, 11303.3, 12666.6],
      services:     [4387.5, 5574.6, 6744.2, 9299.6, 12191.0],
      investments:  [3139.8, 4077.4, 4976.4, 5183.2, 7128.4],
      trade:        [2897.4, 3603.3, 4603.2, 5396.3, 6562.8],
      construction: [1742.5, 2463.6, 2928.6, 2872.2, 3276.6],
      agriculture:  [587.3, 654.8, 754.6, 833.1, 1020.3],
    },
    // Verified demographics — farstat.uz "Hududlar bo'yicha shahar va qishloq
    // aholisi soni" (1 yanvar 2026): Farg'ona shahri 335.1 ming, 100% urban.
    // Population history 2019-2026 (kishi):
    populationFiveYear: [283.8, 289.0, 293.5, 299.2, 314.5, 321.8, 328.4, 335.1],
    populationFiveYearLabels: [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    // Verified age structure 2025 — farstat.uz "Yosh guruhlari bo'yicha".
    ageGroups2025: {
      '0-2': 20784, '3-5': 17391, '6-7': 9615, '8-15': 40235,
      '16-17': 10515, '18-19': 8374, '20-24': 22037, '25-29': 28537,
      '30-34': 32224, '35-39': 28005, '40-49': 41543, '50-59': 32395,
      '60-69': 25517, '70-74': 6073, '75-79': 3312, '80-84': 869, '85+': 983,
    },
    // Verified housing supply — farstat.uz услуги/Aholining uy-joy bilan
    // ta'minlanish darajasi.pdf (sq.m per resident, year-end).
    housingSupply: {
      current: 25.4,                        // 2024
      history: [21.8, 23.4, 22.9, 24.2, 25.4],
      historyLabels: [2020, 2021, 2022, 2023, 2024],
    },
    // ── Fields below were intentionally REMOVED because no city-level source
    // was found in the fergana/ folder. Restore once a verified publication
    // is dropped in (see verification report):
    //   demographics — gender / families / households (no city PDF)
    //   employment — active / unemployed (no city Mehnat bozori PDF)
    //   poverty — соцреестр (no city Ehtiyojmand oilalar PDF)
    //   foreignTrade2025 — viloyat-only in folder; city slice not published
    //   plan2026 — NBU brief, separate source
    //   population.abroad — pending Ko'chib ketganlar audit
    //   unemployment — pending city employment publication
  },
  margilon_city: {
    populationK: 261.9,          // 261,948
    area: 52,
    industryBln: 2459,           // 2025
    investBln: 1281,             // 2025 (+83% vs 2024)
    grpBln: 5725,                // GTP 2025
    servicesBln: 3564,           // derived: 13,599 per-capita × 261.9K
    tradeBln: 5722,              // derived: 21,846 per-capita × 261.9K
    constructionBln: 1807,       // derived: 6,899 per-capita × 261.9K
    avgSalary: 3974,             // exact from dashboard
    unemployment: 5.8,           // exact
    unemploymentStart: 9.5,
    mahallas: 50,                // exact
    households: 46580,
    constructionGrowth: 118.8,
    tourism: { visitors: 380, objects: 42 },  // K visitors, heritage objects
    perCapita: { industry: 9461, invest: 4928, services: 13599, trade: 21846, construction: 6899 },
    // Margilan vs Fergana city benchmark
    benchmark: { industry: 38187, invest: 21491, services: 36753, trade: 19785, construction: 9878 },
    // 5-year history (2021–2025), exact from dashboard
    fiveYear: {
      industry:     [1440, 1554, 1683, 2079, 2459],
      export:       [149, 191, 260, 213, 450],
      import:       [777, 790, 800, 817, 745],
      construction: [121.9, 88.9, 110.2, 102.7, 118.8],
      migration:    [253, 630, 1772, 6240, 1180],
      enterprises:  [4928, 4200, 3500, 3100, 2787],
      unemployment: [9.5, 9.0, 7.8, 6.5, 5.8],
      investments:  [780, 910, 1574, 700, 1281],
    },
    // GTP sector structure (exact from dashboard)
    sectors: [
      { key: 'trade',        pct: 38.2 },
      { key: 'services',     pct: 23.8 },
      { key: 'industry',     pct: 19.4 },
      { key: 'construction', pct: 12.1 },
      { key: 'other',        pct: 6.5 },
    ],
    // Investment financing sources 2025 (exact)
    investSources: [
      { key: 'foreign',      pct: 44.3 },
      { key: 'enterprises',  pct: 19.1 },
      { key: 'govBudget',    pct: 16.0 },
      { key: 'population',   pct: 13.9 },
      { key: 'restoration',  pct: 6.7 },
    ],
    entities: { active: 2787, inactive: 3080, opened: 350, closed: 752, ie: 7143, ooo: 562, farmer: 84, other: 120 },
    population: {
      workingAge: 140164,        // exact
      abroad: 15574,             // exact — citizens abroad
      naturalIncrease: 4757,     // exact
      pensioners: 28315,
      migrationBalance: -687,
    },
    infra: { water: 99, sewage: 62, gas: 89, roads: 75 },  // water 98.8% → 99%
    topMahallas: ['Kashkar', 'Pichoqchi', 'Turaqu\'rg\'on', 'Yuksalish', 'Go\'riavval'],
    // Credit & social data
    nplRate: 4.6,
    socialRegistry: 2602,
    socialRegistryPct: 4.2,
    unregisteredSelfEmployed: 2682,
    informalEconomy: 37,
  },
  // ── Samarkand viloyat (region-level) — verified 2025 data from NBU Excel briefs ──
  samarqand_region: {
    populationK: 4297.5,           // 2025 total population (file 1: "Жами аҳоли")
    area: 16770,                   // km² (16.77 thsd km²)
    mahallas: 1063,                // 2025 (down from 1126 after 2024 reform)
    households: 841957,
    grpBln: 121489.5,
    industryBln: 57767.5,
    servicesBln: 78163.0,
    tradeBln: 41892.4,
    constructionBln: 18637.5,
    agricultureBln: 60758.2,
    investBln: 38281.9,
    industryGrowthPct: 108.5,
    servicesGrowthPct: 115.9,
    tradeGrowthPct: 110.3,
    constructionGrowth: 117.3,
    agricultureGrowthPct: 103.3,
    investGrowthPct: 125.6,
    unemployment: 4.74,
    unemploymentStart: 9.9,
    perCapita: { industry: 11820, invest: 8824, services: 18016, trade: 9656, construction: 4296 },
    benchmark: { industry: 11186, invest: 4726, services: 11400, trade: 9380, construction: 5100 },
    fiveYear: {
      industry:     [22834.3, 29188.6, 32955.7, 45408, 57767.5],
      export:       [531.7,   636.6,   766.8,   886.3,  1150.9],
      import:       [1388.8,  1729,    2125.6,  2158.3, 2915.4],
      construction: [117.8,   111.8,   103.6,   113.6,  117.3],
      migration:    [232545,  217432,  210892,  261576, 174374],
      enterprises:  [40903,   48155,   37598,   31669,  34722],
      unemployment: [9.9,     9.3,     6.6,     5.4,    4.7],
      investments:  [15641.6, 18917.1, 25717.1, 28946.9, 38281.9],
    },
    sectors: [
      { key: 'services',     pct: 47.7 },
      { key: 'agri',         pct: 28.5 },
      { key: 'industry',     pct: 17.4 },
      { key: 'construction', pct:  6.4 },
    ],
    investSources: [
      { key: 'foreign',      pct: 62.4 },
      { key: 'enterprises',  pct: 19.8 },
      { key: 'population',   pct:  4.7 },
      { key: 'govBudget',    pct:  4.7 },
      { key: 'bankCredits',  pct:  3.1 },
    ],
    foreignTrade2025: {
      turnoverMln: 4066.3,
      exportMln: 1150.9,
      importMln: 2915.4,
      balanceMln: -1764.5,
      exportPct: 129.9,         // 1150.9 / 886.3 - 1 = +29.9%
    },
    demographics: {
      men: 2207355,
      women: 2172436,
      womenPct: 49.6,
      households: 841957,
    },
    employment: {
      economicallyActive: 1691961,
      employed: 1611680,
      unemployed: 80281,
      unemploymentPct: 4.74,
      formal: 813248,
      informal: 580308,
    },
    poverty: { pct: 6.1, families: 70285, prevPct: 7.5, prevFamilies: 98420 },
    population: {
      abroad: 218124,
      naturalIncrease: 82300,
      pensioners: 456004,
      workingAge: 1691961,
    },
    tourism: { visitors: 3021, objects: 860 },
    topMahallas: [
      { name: 'Нуробод т. Пулатчи',   loans: 98 },
      { name: 'Пайариқ т. Галлакор',  loans: 85 },
      { name: 'Қўшработ т. Шовона',   loans: 81 },
      { name: 'Оқдарё т. Пичоқчи',    loans: 76 },
      { name: 'Нарпай т. Қозиёқли',   loans: 76 },
    ],
    nplRate: 2.1,
    bankCoverage: { smbCredits: 51.8, exporters: 26, employed: 73 },
    digitalAdoption2025: { payments: 77.6, cards: 71.4, merchants: 70.0, lending: 4.6 },
    // Roads — file 2 §13 (km, 2025): total + asphalt + earth verified; gravel/patched no data
    roads2025: { totalKm: 21916, asphaltKm: 21248, earthKm: 667, gravelKm: null, patchedKm: null },
    // Education — file 1 §8 (2025 counts)
    education2025: {
      schools: 1275,
      schoolsPlanned: null,
      kindergartens: 779,
      kindergartensPlanned: null,
      privateSchools: 55,
      familyKindergartens: 3158,
      preschoolCoveragePct: 75.6,
    },
    // Labor trend — file 2 §17 (in thousand people, converted to absolute by ×1000 in build)
    laborTrend5Y: [
      { year: 2021, formalK: 483.6, informalK: 694.5, abroadK: 263.2, unemployedK: 158.4 },
      { year: 2022, formalK: 539.9, informalK: 664.2, abroadK: 275.7, unemployedK: 152.5 },
      { year: 2023, formalK: 525.3, informalK: 678.9, abroadK: 300.0, unemployedK: 106.8 },
      { year: 2024, formalK: 686.2, informalK: 648.9, abroadK: 185.96, unemployedK: 86.44 },
      { year: 2025, formalK: 813.2, informalK: 580.3, abroadK: 218.12, unemployedK: 80.28 },
    ],
    // Note: avgSalary, infra coverage % (water/sewage/gas), entities org-form split,
    // gravelKm, patchedKm, mahalla credit scores, 2026 plan are not in source data.
  },
}

// Sector key → color mapping
const SECTOR_COLORS = {
  industry: '#003D7C', agri: '#059669', services: '#0054A6', trade: '#2563EB',
  construction: '#D97706', other: '#6B7280',
}
const INVEST_SRC_COLORS = {
  foreign: '#003D7C', enterprises: '#059669', govBudget: '#D97706',
  population: '#7C3AED', bankCredits: '#2563EB', restoration: '#6B7280',
}

// Benchmark district = Marg'ilon (base for template scales — used for non-real districts).
const BENCH_POP = 261.9
const BENCH_GRP = 5725 // mlrd UZS
const identity = (k) => k

function fmt(n, d = 0) {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('ru-RU', { minimumFractionDigits: d, maximumFractionDigits: d })
}

// Helper: pick "city" or "district" label keys for grammatical context.
function kindLabels(t, kind) {
  const suffix = kind === 'city' ? 'city' : kind === 'region' ? 'region' : 'district'
  return {
    nom: t(`districtAnalytics.kind.${suffix}`),
    gen: t(`districtAnalytics.kindGen.${suffix}`),
    adj: t(`districtAnalytics.kindAdj.${suffix}`),
  }
}

export function buildDistrictAnalytics(districtKey, t = identity) {
  const d = districtByKey[districtKey]
  if (!d) return null
  const p = PROFILE[districtKey] || PROFILE.oltiariq
  const rd = REAL_DATA[districtKey] // may be undefined for non-pilot districts
  const popK = rd ? rd.populationK : d.population
  const popAbs = Math.round(popK * 1000)
  const scale = popK / BENCH_POP

  const grpTotal    = rd?.grpBln       != null ? rd.grpBln       : Math.round(BENCH_GRP * scale * (p.growth / 8.0))
  const industryBln = rd?.industryBln  != null ? rd.industryBln  : Math.round(grpTotal * (p.industry / 100))
  const servicesBln = rd?.servicesBln  != null ? rd.servicesBln  : Math.round(grpTotal * (p.services / 100))
  const tradeBln    = rd?.tradeBln     != null ? rd.tradeBln     : Math.round(grpTotal * (p.trade / 100))
  const investBln   = rd?.investBln    != null ? rd.investBln    : Math.round(883 * scale * (p.growth / 8.0))
  const agriBln     = rd?.agricultureBln != null ? rd.agricultureBln : Math.round(grpTotal * (p.agri / 100))
  const constructionBln = rd?.constructionBln != null ? rd.constructionBln : Math.round(grpTotal * 0.12)
  const unemployment      = rd?.unemployment      != null ? rd.unemployment.toFixed(1) : Math.max(3.0, 7.0 - p.growth * 0.25).toFixed(1)
  const unemploymentStart = rd?.unemploymentStart != null ? rd.unemploymentStart.toFixed(1) : (parseFloat(unemployment) + 6.5).toFixed(1)
  const hasUnemploymentStart = rd?.unemploymentStart != null

  const mahallas = rd?.mahallas != null ? rd.mahallas : Math.max(18, Math.round(popK * 0.35))
  const score = Math.min(9.4, 5.5 + p.growth * 0.25 + p.infra * 2.0).toFixed(1)
  const k = kindLabels(t, d.kind)
  const mlrdSum = t('regionAnalytics.units.bnSum')
  const ppPoints = t('regionAnalytics.units.pp')
  const sumUnit = t('regionAnalytics.units.sum2025')

  // Composite-score breakdown exposed to UI so users understand what feeds it.
  const scoreBreakdown = [
    { axis: t('districtAnalytics.score.grpGrowth'),    value: Math.min(10, p.growth).toFixed(1), weight: 30 },
    { axis: t('districtAnalytics.score.infra'),        value: (p.infra * 10).toFixed(1), weight: 30 },
    { axis: t('districtAnalytics.score.employment'),   value: Math.min(10, 5 + p.growth * 0.35).toFixed(1), weight: 20 },
    { axis: t('districtAnalytics.score.investments'),  value: Math.min(10, 5.5 + p.growth * 0.4).toFixed(1), weight: 20 },
  ]

  const brief = {
    score,
    scoreBreakdown,
    kpis: [
      { label: t('regionAnalytics.brief.grp'),          value: fmt(grpTotal),    unit: mlrdSum, delta: `+${p.growth.toFixed(1)}%`, tone: 'green' },
      { label: t('regionAnalytics.brief.industry'),     value: fmt(industryBln), unit: mlrdSum, delta: t('districtAnalytics.brief.shareOfGrp', { n: p.industry }), tone: 'green' },
      { label: t('regionAnalytics.brief.investments'),  value: fmt(investBln),   unit: mlrdSum, delta: `×${(1.6 + p.growth * 0.15).toFixed(1)}`, tone: 'green' },
      { label: t('regionAnalytics.brief.unemployment'), value: `${unemployment}%`, unit: '',     delta: hasUnemploymentStart ? `−${(parseFloat(unemploymentStart) - parseFloat(unemployment)).toFixed(1)} ${ppPoints}` : '2025', tone: 'green' },
      { label: t('regionAnalytics.brief.population'),   value: fmt(popAbs),      unit: t('regionAnalytics.units.people'), delta: t(d.kind === 'city' ? 'districtAnalytics.brief.urban' : 'districtAnalytics.brief.rural'), tone: 'blue' },
    ],
  }

  // Helper: render a +X.X% YoY chip from the verified growth rate, or empty
  // string when no rate is available (so tiles never show a fabricated chip).
  const growthChip = (pct) => {
    if (pct == null) return ''
    const delta = pct - 100
    return `${delta >= 0 ? '+' : ''}${delta.toFixed(1)}% YoY`
  }
  const toneOf = (pct) => {
    if (pct == null) return 'blue'
    if (pct >= 102) return 'green'
    if (pct >= 99)  return 'blue'
    return 'red'
  }

  const economic = {
    // Sector breakdown — 4 tiles for sectors NOT shown in the macro row above.
    // Industry sits in macro row, so this row covers Services / Trade /
    // Construction / Agriculture; drops the fabricated "businessCoverage".
    kpis: [
      { label: t('regionAnalytics.econ.services'),         value: `${fmt(servicesBln)} ${t('regionAnalytics.units.bnShort')}`, sub: sumUnit, delta: growthChip(rd?.servicesGrowthPct),     tone: toneOf(rd?.servicesGrowthPct) },
      { label: t('districtAnalytics.sector.trade'),        value: `${fmt(tradeBln)} ${t('regionAnalytics.units.bnShort')}`,    sub: sumUnit, delta: growthChip(rd?.tradeGrowthPct),        tone: toneOf(rd?.tradeGrowthPct) },
      { label: t('regionAnalytics.sector.construction'),   value: `${fmt(constructionBln)} ${t('regionAnalytics.units.bnShort')}`, sub: sumUnit, delta: growthChip(rd?.constructionGrowth),  tone: toneOf(rd?.constructionGrowth) },
      { label: t('districtAnalytics.econ.agriShort'),      value: `${fmt(agriBln)} ${t('regionAnalytics.units.bnShort')}`,     sub: sumUnit, delta: growthChip(rd?.agricultureGrowthPct),  tone: toneOf(rd?.agricultureGrowthPct) },
    ],
    // 5-year trend: use verified series from rd.fiveYear when available
    // (fargona_city, margilon_city). For non-pilot districts, scale current
    // totals by a synthetic growth factor so the line still trends upward.
    history: rd?.fiveYear
      ? [2021, 2022, 2023, 2024, 2025].map((y, i) => ({
          year: y,
          industry: rd.fiveYear.industry[i],
          invest: rd.fiveYear.investments[i],
          services: rd.fiveYear.services ? rd.fiveYear.services[i] : null,
        }))
      : [2021, 2022, 2023, 2024, 2025].map((y, i) => {
          const factor = 0.55 + i * 0.12
          return {
            year: y,
            industry: Math.round(industryBln * factor),
            invest: Math.round(investBln * factor * (i === 4 ? 2.4 : 1)),
            services: Math.round(servicesBln * factor),
          }
        }),
    // True when the trend chart shows verified rather than estimated values
    historyVerified: !!rd?.fiveYear,
    sectors: rd?.sectors
      ? rd.sectors.map((s) => ({
          name: t(s.key === 'industry' ? 'regionAnalytics.sector.industry'
              : s.key === 'services'   ? 'regionAnalytics.sector.services'
              : s.key === 'trade'      ? 'districtAnalytics.sector.trade'
              : s.key === 'construction' ? 'regionAnalytics.sector.construction'
              : s.key === 'agri'       ? 'districtAnalytics.econ.agriShort'
              : 'districtAnalytics.sector.other'),
          percent: s.pct.toFixed(1),
          color: SECTOR_COLORS[s.key] || '#6B7280',
        }))
      : rd
        ? null
        : [
            { name: t('regionAnalytics.sector.industry'),     percent: p.industry.toFixed(1), color: '#003D7C' },
            { name: t('districtAnalytics.econ.agriShort'),    percent: p.agri.toFixed(1),     color: '#059669' },
            { name: t('regionAnalytics.sector.services'),     percent: p.services.toFixed(1), color: '#0054A6' },
            { name: t('districtAnalytics.sector.trade'),      percent: p.trade.toFixed(1),    color: '#2563EB' },
          ],
    // Foreign trade card: prefer city-level rd.foreignTrade2025, then 5Y
    // export/import series, then verified Fergana viloyat totals (farstat.uz
    // Makroiqtisodiy ko'rsatkichlar Jan-Dec 2025) as regional context for
    // cities without city-level publication. `level` field tells the view
    // whether to render city or region badge.
    trade: rd?.foreignTrade2025 ? {
      level: 'city',
      importMln: rd.foreignTrade2025.importMln,
      exportMln: rd.foreignTrade2025.exportMln,
      deficitMln: rd.foreignTrade2025.balanceMln,
      exportGrowth: `${rd.foreignTrade2025.exportPct >= 100 ? '+' : ''}${Math.round(rd.foreignTrade2025.exportPct - 100)}%`,
      importGrowth: rd.foreignTrade2025.importPct != null ? `${rd.foreignTrade2025.importPct >= 100 ? '+' : ''}${Math.round(rd.foreignTrade2025.importPct - 100)}%` : '',
    } : rd?.fiveYear?.export && rd?.fiveYear?.import ? {
      level: 'city',
      importMln: rd.fiveYear.import[4],
      exportMln: rd.fiveYear.export[4],
      deficitMln: rd.fiveYear.import[4] - rd.fiveYear.export[4],
      exportGrowth: `+${Math.round(((rd.fiveYear.export[4] / rd.fiveYear.export[0]) - 1) * 100)}%`,
      importGrowth: `+${Math.round(((rd.fiveYear.import[4] / rd.fiveYear.import[0]) - 1) * 100)}%`,
    } : rd ? {
      // City has no published foreign-trade data — show verified Fergana
      // viloyat totals for context (farstat.uz Jan-Dec 2025, mln USD).
      level: 'region',
      importMln: 1586.3,
      exportMln: 1082.1,
      deficitMln: -504.2,
      exportGrowth: '+29.4%',
      importGrowth: '+18.8%',
    } : {
      level: 'estimate',
      importMln: Math.round(40 * scale),
      exportMln: Math.round(11.4 * scale * (p.growth / 8.0) * (1 + p.textile * 0.4)),
      deficitMln: Math.round(-28.6 * scale),
      exportGrowth: `+${Math.round(30 + p.growth * 5)}%`,
      importGrowth: '',
    },
    entities: rd?.entities ? {
      active: rd.entities.active,
      inactive: rd.entities.inactive,
      opened: rd.entities.opened,
      closed: rd.entities.closed,
      activeShare: Math.round((rd.entities.active / (rd.entities.active + rd.entities.inactive)) * 100),
      types: [
        { code: t('regionAnalytics.orgForm.ip'),     count: rd.entities.ie,     share: Math.round(rd.entities.ie / (rd.entities.ie + rd.entities.ooo + rd.entities.farmer + rd.entities.other) * 100) },
        { code: t('regionAnalytics.orgForm.ooo'),    count: rd.entities.ooo,    share: Math.round(rd.entities.ooo / (rd.entities.ie + rd.entities.ooo + rd.entities.farmer + rd.entities.other) * 100) },
        { code: t('regionAnalytics.orgForm.farmer'), count: rd.entities.farmer, share: Math.round(rd.entities.farmer / (rd.entities.ie + rd.entities.ooo + rd.entities.farmer + rd.entities.other) * 100) },
        { code: t('regionAnalytics.orgForm.other'),  count: rd.entities.other,  share: Math.round(rd.entities.other / (rd.entities.ie + rd.entities.ooo + rd.entities.farmer + rd.entities.other) * 100) },
      ],
    } : rd ? null : {
      active: Math.round(866 * scale),
      inactive: Math.round(336 * scale),
      opened: Math.round(141 * scale),
      closed: Math.round(338 * scale * (1 - p.infra * 0.3)),
      activeShare: Math.round(60 + p.infra * 20),
      types: [
        { code: t('regionAnalytics.orgForm.ip'),     count: Math.round(817 * scale), share: 60 },
        { code: t('regionAnalytics.orgForm.ooo'),    count: Math.round(264 * scale), share: 22 },
        { code: t('regionAnalytics.orgForm.farmer'), count: Math.round(84 * scale * (1 + p.agri / 60)), share: 11 },
        { code: t('regionAnalytics.orgForm.other'),  count: Math.round(37 * scale), share: 7 },
      ],
    },
    aiNote: p.industry >= 40
      ? t('districtAnalytics.ai.industryHeavy', { kind: k.nom, share: p.industry })
      : t('districtAnalytics.ai.agrarian',      { kindGen: k.gen, share: p.agri }),
  }

  const hasInfraData = !!rd?.infra
  const water  = rd?.infra?.water  != null ? rd.infra.water  : Math.round(p.infra * 70 + 10)
  const sewage = rd?.infra?.sewage != null ? rd.infra.sewage : Math.round(p.infra * 60 + 5)
  const roads  = rd?.infra?.roads  != null ? rd.infra.roads  : Math.round(p.infra * 60 + 20)
  const gas    = rd?.infra?.gas    != null ? rd.infra.gas    : Math.min(100, Math.round(p.infra * 80 + 20))

  const showInfraEstimates = !rd || hasInfraData
  const infra = {
    kpis: showInfraEstimates ? [
      { label: t('regionAnalytics.infra.electricity'), value: '100%', delta: t('regionAnalytics.infra.coverage'), tone: 'green' },
      { label: t('regionAnalytics.infra.water'),       value: `${water}%`, delta: water >= 60 ? t('regionAnalytics.infra.stable') : water >= 40 ? t('regionAnalytics.infra.belowNorm') : t('regionAnalytics.infra.critical'), tone: water >= 60 ? 'green' : water >= 40 ? 'amber' : 'red' },
      { label: t('regionAnalytics.infra.gas'),         value: `${gas}%`, delta: t('districtAnalytics.infra.network'), tone: 'green' },
      { label: t('regionAnalytics.infra.sewage'),      value: `${sewage}%`, delta: sewage >= 55 ? t('districtAnalytics.infra.norm') : t('regionAnalytics.infra.belowNorm'), tone: sewage >= 55 ? 'green' : 'amber' },
      { label: t('regionAnalytics.infra.transport'),   value: `${roads}%`, delta: t('regionAnalytics.infra.inOperation'), tone: 'blue' },
    ] : null,
    matrix: showInfraEstimates ? [
      { name: t('regionAnalytics.infra.matrix.electricity'),  status: 'ok',                                                 note: t('regionAnalytics.infra.note.elNoOutages') },
      { name: t('regionAnalytics.infra.matrix.drinkingWater'), status: water >= 60 ? 'ok' : water >= 40 ? 'warn' : 'bad',  note: t('districtAnalytics.infra.note.waterPct',  { n: water,   txt: water >= 60 ? t('districtAnalytics.infra.inNorm') : t('districtAnalytics.infra.modernization') }) },
      { name: t('regionAnalytics.infra.matrix.gas'),           status: gas >= 80 ? 'ok' : 'warn',                            note: t('districtAnalytics.infra.note.gasPct',    { n: gas,     txt: gas >= 80 ? t('districtAnalytics.infra.working') : t('districtAnalytics.infra.expanding') }) },
      { name: t('regionAnalytics.infra.matrix.sewage'),        status: sewage >= 55 ? 'ok' : 'warn',                         note: t('districtAnalytics.infra.note.sewagePct', { n: sewage }) },
      { name: t('regionAnalytics.infra.matrix.roads'),         status: roads >= 60 ? 'ok' : 'warn',                          note: t('districtAnalytics.infra.note.roadsKm',   { n: Math.round(popK * 0.6) }) },
      { name: t('regionAnalytics.infra.matrix.publicTransport'), status: p.infra >= 0.7 ? 'ok' : 'warn',                     note: t('districtAnalytics.infra.note.transport', { n: Math.round(p.infra * 100) }) },
      { name: t('regionAnalytics.infra.matrix.digital'),       status: 'warn',                                               note: t('districtAnalytics.infra.note.digital',    { n: Math.round(60 + p.infra * 30) }) },
    ] : null,
    // Verified housing supply (m²/resident) — farstat.uz уцлуги folder.
    // null when not in REAL_DATA so the view skips the verified card.
    housing: rd?.housingSupply ? {
      currentSqMPerPerson: rd.housingSupply.current,
      history: rd.housingSupply.history,
      historyLabels: rd.housingSupply.historyLabels,
    } : null,
    // Budget and roads: render only when rd has a verified source. For pilot
    // cities (rd present) without rd.budget / rd.roads2025, return null so
    // the view shows a "Нет данных" placeholder. For non-pilot districts
    // (rd absent) keep the synthetic estimate so the dashboard isn't empty.
    budgetMlrd: rd?.budget?.mlrd ?? (!rd ? Math.round(46.3 * scale * 10) / 10 : null),
    roads: rd?.roads2025 ? {
      totalKm:   rd.roads2025.totalKm,
      asphaltKm: rd.roads2025.asphaltKm,
      gravelKm:  rd.roads2025.gravelKm,
      patchedKm: rd.roads2025.patchedKm,
      earthKm:   rd.roads2025.earthKm,
    } : !rd ? {
      totalKm: Math.round(popK * 0.6),
      asphaltKm: Math.round(popK * 0.6 * (0.2 + p.infra * 0.4)),
      gravelKm: Math.round(popK * 0.6 * 0.15),
      patchedKm: Math.round(popK * 0.6 * 0.25),
      earthKm: Math.round(popK * 0.6 * 0.3 * (1 - p.infra * 0.5)),
    } : null,
    education: rd?.education2025 ? {
      schools:               rd.education2025.schools,
      schoolsPlanned:        rd.education2025.schoolsPlanned,
      kindergartens:         rd.education2025.kindergartens,
      kindergartensPlanned:  rd.education2025.kindergartensPlanned,
      privateSchools:        rd.education2025.privateSchools,
      familyKindergartens:   rd.education2025.familyKindergartens,
      preschoolCoveragePct:  rd.education2025.preschoolCoveragePct,
    } : !rd ? {
      schools: Math.max(4, Math.round(popK * 0.06)),
      schoolsPlanned: Math.max(1, Math.round(popK * 0.015)),
      kindergartens: Math.max(6, Math.round(popK * 0.09)),
      kindergartensPlanned: Math.max(3, Math.round(popK * 0.04)),
    } : null,
    // Infrastructure problems list: synthetic priorities + costs derived from
    // the same fabricated water/sewage % and population scale. Show only when
    // there's a verified source (none currently), null otherwise.
    problems: !rd ? [
      { code: 'M1', name: t('regionAnalytics.problems.waterRecon'),    cost: Math.round(12.8 * scale * 10) / 10, priority: water  < 55 ? t('regionAnalytics.priority.high') : t('regionAnalytics.priority.medium') },
      { code: 'M2', name: t('regionAnalytics.problems.sewageSystem'),  cost: Math.round(8.4  * scale * 10) / 10, priority: sewage < 50 ? t('regionAnalytics.priority.high') : t('regionAnalytics.priority.medium') },
      { code: 'M3', name: t('regionAnalytics.problems.roadNetwork'),   cost: Math.round(6.2  * scale * 10) / 10, priority: t('regionAnalytics.priority.medium') },
      { code: 'M4', name: t('regionAnalytics.problems.energySystem'),  cost: Math.round(3.0  * scale * 10) / 10, priority: t('regionAnalytics.priority.medium') },
      { code: 'T1', name: t('districtAnalytics.problems.newSchools'),  cost: Math.round(4.8  * scale * 10) / 10, priority: t('regionAnalytics.priority.high') },
      { code: 'T2', name: t('districtAnalytics.problems.kindergartens'), cost: Math.round(2.2 * scale * 10) / 10, priority: t('regionAnalytics.priority.medium') },
      { code: 'T3', name: t('regionAnalytics.problems.digital5g'),     cost: Math.round(1.5  * scale * 10) / 10, priority: t('regionAnalytics.priority.low') },
      { code: 'T4', name: t('regionAnalytics.problems.greenEnergy'),   cost: Math.round(1.5  * scale * 10) / 10, priority: t('regionAnalytics.priority.low') },
    ] : null,
    aiNote: water < 50
      ? t('districtAnalytics.ai.waterCritical', { n: water, mlrd: Math.round(12.8 * scale * 10) / 10 })
      : t('districtAnalytics.ai.infraBalanced', { kindGen: k.gen, n: Math.round(p.infra * 100) }),
  }

  const empEmployed = Math.round(75 + p.infra * 20)
  // Prefer verified employment.economicallyActive; fall back to workingAge; finally to estimate
  const workingAge = rd?.employment?.economicallyActive
    ?? rd?.population?.workingAge
    ?? Math.round(29811 * scale)
  const hasNaturalIncrease = rd?.population?.naturalIncrease != null
  const population = {
    kpis: [
      { label: t('regionAnalytics.brief.population'),       value: fmt(popAbs), delta: t(d.kind === 'city' ? 'districtAnalytics.pop.cityRate' : 'districtAnalytics.pop.ruralRate'), sub: rd ? t('districtAnalytics.pop.density', { n: Math.round(popAbs / (rd.area || d.area)).toLocaleString('ru-RU') }) : t('districtAnalytics.pop.under18Approx'), tone: 'blue' },
      { label: t('regionAnalytics.pop.area'),               value: `${rd ? rd.area : d.area} ${t('regionAnalytics.units.kmSq')}`, delta: '—', sub: t('regionAnalytics.pop.density', { n: Math.round(popAbs / (rd ? rd.area : d.area)).toLocaleString('ru-RU') }), tone: 'blue' },
      { label: t('regionAnalytics.pop.economicallyActive'), value: fmt(workingAge), delta: hasNaturalIncrease ? `+${fmt(rd.population.naturalIncrease)}` : (rd ? '—' : `+${fmt(Math.round(5745 * scale))}`), sub: hasNaturalIncrease ? t('districtAnalytics.pop.naturalIncrease') : (rd ? '' : t('regionAnalytics.pop.since2021')), tone: 'green' },
      { label: t('regionAnalytics.brief.unemployment'),     value: `${unemployment}%`, delta: hasUnemploymentStart ? `${unemploymentStart}% → ${unemployment}%` : `${unemployment}%`, sub: hasUnemploymentStart ? '2021 → 2025' : '2025', tone: 'green' },
    ],
    laborTrend: rd?.laborTrend5Y
      ? rd.laborTrend5Y.map((r) => ({
          year: r.year,
          formal:     Math.round(r.formalK * 1000),
          informal:   Math.round(r.informalK * 1000),
          abroad:     Math.round(r.abroadK * 1000),
          unemployed: Math.round(r.unemployedK * 1000),
        }))
      : [
          { year: 2021, formal: 16137, informal: 3455, abroad: 4474, unemployed: 2784 },
          { year: 2022, formal: 16618, informal: 3010, abroad: 4875, unemployed: 2246 },
          { year: 2023, formal: 17618, informal: 2995, abroad: 5213, unemployed: 1854 },
          { year: 2024, formal: 19455, informal: 2765, abroad: 5566, unemployed: 1520 },
          { year: 2025, formal: 20415, informal: 2210, abroad: 6936, unemployed: 1197 },
        ].map((row) => ({
          year: row.year,
          formal: Math.round(row.formal * scale),
          informal: Math.round(row.informal * scale),
          abroad: Math.round(row.abroad * scale * (1 + (1 - p.infra) * 0.5)),
          unemployed: Math.round(row.unemployed * scale),
        })),
    unemploymentTrend: hasUnemploymentStart ? [
      { year: 2021, value: parseFloat(unemploymentStart) },
      { year: 2022, value: parseFloat(unemploymentStart) - 2.0 },
      { year: 2023, value: parseFloat(unemploymentStart) - 3.7 },
      { year: 2024, value: parseFloat(unemploymentStart) - 5.2 },
      { year: 2025, value: parseFloat(unemployment) },
    ] : null,
    migration: {
      countAbroad: rd?.population?.abroad != null ? rd.population.abroad : Math.round(6812 * scale * (1 + (1 - p.infra) * 0.6)),
      growthPct: rd?.population?.abroad != null ? `+${Math.round(((rd.population.abroad / popAbs) * 100))}%` : `+${Math.round(40 + (1 - p.infra) * 30)}%`,
      shareOfWorkforce: rd?.population?.abroad != null ? `${((rd.population.abroad / workingAge) * 100).toFixed(1)}%` : `${(19.2 * (1 + (1 - p.infra) * 0.3)).toFixed(1)}%`,
      totalEmployed: workingAge,
      warning: p.enclave
        ? t('districtAnalytics.migration.enclave')
        : t('regionAnalytics.migration.warning'),
    },
    program2026: {
      title: t('regionAnalytics.program.title'),
      goal: Math.round(2500 * scale),
      breakdown: [
        { code: 'P1', label: t('regionAnalytics.program.crafts'),        count: Math.round(800 * scale) },
        { code: 'P2', label: t('regionAnalytics.program.subsidies'),     count: Math.round(620 * scale) },
        { code: 'P3', label: t('regionAnalytics.program.employment'),    count: Math.round(580 * scale) },
        { code: 'P4', label: t('regionAnalytics.program.exportCluster'), count: Math.round(500 * scale * (1 + p.textile * 0.5)) },
      ],
    },
  }

  const bankCredits     = rd?.bankCoverage?.smbCredits != null ? Math.round(rd.bankCoverage.smbCredits) : Math.round(55 + p.infra * 30)
  const bankExporters   = rd?.bankCoverage?.exporters  != null ? Math.round(rd.bankCoverage.exporters)  : Math.round(20 + p.textile * 40 + p.tourism * 15)
  const bankEmployed    = rd?.bankCoverage?.employed   != null ? Math.round(rd.bankCoverage.employed)   : null
  const bankNewBusiness = Math.round(40 + p.growth * 3)

  const mahalla = {
    kpis: [
      { label: t('regionAnalytics.mahalla.mahallas'),     value: mahallas.toLocaleString('ru-RU'), sub: t(d.kind === 'city' ? 'districtAnalytics.mahalla.urban' : 'districtAnalytics.mahalla.rural'), tone: 'blue' },
      { label: t('regionAnalytics.mahalla.creditCover'),  value: `${bankCredits}%`,    sub: t('districtAnalytics.mahalla.smbDistrict'), tone: 'green' },
      { label: t('regionAnalytics.mahalla.newIp'),        value: `${bankNewBusiness}%`, sub: t('regionAnalytics.mahalla.quarterGrowth'), tone: 'green' },
      { label: t('regionAnalytics.mahalla.digitalization'), value: `${Math.round(bankCredits * 0.65)}%`, sub: t('regionAnalytics.mahalla.onlineBanking'), tone: 'blue' },
    ],
    bankMetrics: [
      { label: t('regionAnalytics.bank.smbCredits'),     percent: bankCredits,                                color: 'bg-primary' },
      { label: t('regionAnalytics.bank.newEntrepr'),     percent: bankNewBusiness,                            color: 'bg-primary-container' },
      { label: t('regionAnalytics.bank.exporters'),      percent: bankExporters,                              color: 'bg-secondary' },
      { label: t('regionAnalytics.bank.employed'),       percent: bankEmployed != null ? bankEmployed : empEmployed, color: 'bg-tertiary' },
      { label: t('regionAnalytics.bank.selfEmployed'),   percent: Math.round(40 + p.agri * 0.5),              color: 'bg-tertiary opacity-60' },
      { label: t('regionAnalytics.bank.profEducation'),  percent: Math.round(25 + p.infra * 20),              color: 'bg-primary opacity-60' },
    ],
    topMahallas: rd?.topMahallas
      ? rd.topMahallas.map((entry, i) => {
          const name  = typeof entry === 'string' ? entry : entry.name
          const loans = typeof entry === 'string' ? Math.max(4, Math.round((24 - i * 2) * scale)) : entry.loans
          return {
            name,
            loans,
            score: parseFloat((9.0 - i * 0.3).toFixed(1)),
          }
        })
      : rd
        ? null
        : buildTopMahallas(d, p, scale),
    digitalAdoption: rd?.digitalAdoption2025
      ? {
          payments:  Math.round(rd.digitalAdoption2025.payments),
          cards:     Math.round(rd.digitalAdoption2025.cards),
          merchants: Math.round(rd.digitalAdoption2025.merchants),
          lending:   Math.round(rd.digitalAdoption2025.lending),
        }
      : {
          payments: Math.round(60 + p.infra * 30),
          cards: Math.round(45 + p.infra * 30),
          merchants: Math.round(35 + p.infra * 25),
          lending: Math.round(25 + p.infra * 20),
        },
  }

  // ---- Enrichments: 5-year time series (real for pilot cities, estimated for others) ----
  // Moved before summary/opportunities because they reference perCapita and exportYears.
  let industryYears, exportYears, importYears, deficitYears, constructionYears
  let migrationYears, enterprisesYears, unemploymentYears, investmentYears

  if (rd?.fiveYear) {
    industryYears     = rd.fiveYear.industry
    constructionYears = rd.fiveYear.construction
    investmentYears   = rd.fiveYear.investments
    // Optional series — fall back to synthetic when the city dataset doesn't
    // include them (fargona_city has no published 5Y export/import or
    // migration/enterprises/unemployment trend).
    if (rd.fiveYear.export && rd.fiveYear.import) {
      exportYears  = rd.fiveYear.export
      importYears  = rd.fiveYear.import
      deficitYears = importYears.map((im, i) => im - exportYears[i])
    } else {
      const exportBaseline = Math.round(11.4 * scale * (p.growth / 8.0) * (1 + p.textile * 0.4))
      exportYears  = [0.33, 0.42, 0.58, 0.47, 1.0].map((f) => Math.round(exportBaseline * f * 39))
      const importBaseline = Math.round(40 * scale * 18)
      importYears  = [1.04, 1.06, 1.07, 1.10, 1.0].map((f) => Math.round(importBaseline * f))
      deficitYears = importYears.map((im, i) => im - exportYears[i])
    }
    migrationYears    = rd.fiveYear.migration    || null
    enterprisesYears  = rd.fiveYear.enterprises  || null
    unemploymentYears = rd.fiveYear.unemployment || null
  } else {
    industryYears = [0.58, 0.63, 0.68, 0.84, 1.0].map((f) => Math.round(industryBln * f))
    const exportBaseline = Math.round(11.4 * scale * (p.growth / 8.0) * (1 + p.textile * 0.4))
    exportYears = [0.33, 0.42, 0.58, 0.47, 1.0].map((f) => Math.round(exportBaseline * f * 39))
    const importBaseline = Math.round(40 * scale * 18)
    importYears = [1.04, 1.06, 1.07, 1.10, 1.0].map((f) => Math.round(importBaseline * f))
    deficitYears = importYears.map((im, i) => im - exportYears[i])
    constructionYears = [121.9, 88.9, 110.2, 102.7, 118.8]
    const migrationBase = Math.round(253 * scale * (1 + (1 - p.infra) * 0.6))
    migrationYears = [1.0, 2.49, 7.0, 24.6, 4.67].map((f) => Math.round(migrationBase * f))
    enterprisesYears = [1.0, 0.85, 0.71, 0.63, 0.57].map((f) => Math.round(4928 * scale * f))
    if (hasUnemploymentStart) {
      unemploymentYears = [
        parseFloat(unemploymentStart),
        parseFloat(unemploymentStart) - 2.0,
        parseFloat(unemploymentStart) - 3.7,
        parseFloat(unemploymentStart) - 5.2,
        parseFloat(unemployment),
      ].map((v) => parseFloat(v.toFixed(1)))
    } else {
      unemploymentYears = [null, null, null, null, parseFloat(unemployment)]
    }
    investmentYears = [0.61, 0.71, 1.23, 0.55, 1.0].map((f) => Math.round(investBln * f))
    // For pilot cities lacking verified 5Y migration/enterprises data, null these
    // arrays so the corresponding rows are dropped from the 5Y history table.
    if (rd) {
      migrationYears   = null
      enterprisesYears = null
    }
  }

  // Compute trend labels from actual 5Y data
  const pctTrend = (arr) => {
    const first = arr[0]; const last = arr[arr.length - 1]
    if (!first) return '+0%'
    const pct = ((last / first) - 1) * 100
    return pct >= 0 ? `+${Math.round(pct)}%` : `${Math.round(pct)}%`
  }
  const industryTrend = pctTrend(industryYears)
  const exportTrend = pctTrend(exportYears)
  const importTrend = pctTrend(importYears)
  const deficitFirst = deficitYears[0]; const deficitLast = deficitYears[deficitYears.length - 1]
  const deficitTrend = deficitFirst > 0 ? pctTrend(deficitYears) : `${Math.round(((deficitLast / deficitFirst) - 1) * 100)}%`
  const migFirst = migrationYears ? migrationYears[0] : null
  const migLast  = migrationYears ? migrationYears[migrationYears.length - 1] : null
  const migTrend = migrationYears
    ? (migFirst > 0 ? `×${(migLast / migFirst).toFixed(1)}` : `+${migLast}`)
    : null
  const investTrend = pctTrend(investmentYears)
  const enterpriseTrend = enterprisesYears ? pctTrend(enterprisesYears) : null

  // Per-capita values: use real data when available
  const perCapitaIndustry  = rd ? rd.perCapita.industry     : Math.round((industryBln * 1e9) / popAbs / 1000)
  const perCapitaInvest    = rd ? rd.perCapita.invest        : Math.round((investBln * 1e9) / popAbs / 1000)
  const perCapitaServices  = rd ? rd.perCapita.services      : Math.round((servicesBln * 1e9) / popAbs / 1000)
  const perCapitaTrade     = rd ? rd.perCapita.trade          : Math.round((tradeBln * 1e9) / popAbs / 1000)
  const perCapitaConstr    = rd ? rd.perCapita.construction   : Math.round((grpTotal * 0.12 * 1e9) / popAbs / 1000)

  const opportunities = {
    swot: {
      strengths: buildStrengths(d, p, t),
      weaknesses: buildWeaknesses(d, p, water, sewage, t),
      opportunities: buildOpportunities(d, p, t),
      threats: buildThreats(d, p, t),
    },
    aiRecommendation: p.textile >= 0.8
      ? t('districtAnalytics.ai.textileHub',     { kind: k.nom, mlrd: Math.round(24 * scale) })
      : p.tourism >= 0.8
        ? t('districtAnalytics.ai.tourismHub')
        : p.enclave
          ? t('districtAnalytics.ai.enclave')
          : t('districtAnalytics.ai.balancedSlow', { kindAdj: k.adj }),
  }

  const summary = {
    score,
    radar: [
      { axis: t('regionAnalytics.radar.economy'),     value: Math.min(9.5, 5.5 + p.growth * 0.3).toFixed(1),  provincial: 7.0 },
      { axis: t('regionAnalytics.radar.infra'),       value: (4 + p.infra * 5.5).toFixed(1),                  provincial: 6.5 },
      { axis: t('regionAnalytics.radar.employment'),  value: Math.min(9.0, 5.5 + p.growth * 0.25).toFixed(1), provincial: 7.0 },
      { axis: t('regionAnalytics.radar.demography'),  value: (d.kind === 'city' ? 7.8 : 6.8).toFixed(1),      provincial: 7.0 },
      { axis: t('regionAnalytics.radar.investments'), value: Math.min(9.2, 5.5 + p.growth * 0.3).toFixed(1),  provincial: 6.8 },
    ],
    comparison: [
      { metric: t('regionAnalytics.compare.industryPC'), region: perCapitaIndustry, provincial: 11186 },
      { metric: t('regionAnalytics.compare.servicesPC'), region: perCapitaServices, provincial: 11400 },
      { metric: t('regionAnalytics.compare.tradePC'),    region: perCapitaTrade,    provincial: 9380 },
      { metric: t('regionAnalytics.compare.investPC'),   region: perCapitaInvest,   provincial: 4726 },
      { metric: t('regionAnalytics.compare.exportPC'),   region: Math.round((exportYears[4] * 1e9) / popAbs / 1000), provincial: 28 },
    ],
    plan: buildPlan(d, p, scale, water, t),
    conclusion: t('districtAnalytics.summary.conclusion', {
      kind: k.nom,
      pop: fmt(popAbs),
      pct: (scale * 100).toFixed(0),
      score,
      tier: score >= 8.5 ? t('districtAnalytics.tier.leader')
          : score >= 7.5 ? t('districtAnalytics.tier.aboveAvg')
          : score >= 6.5 ? t('districtAnalytics.tier.growthGroup')
          : t('districtAnalytics.tier.catchingUp'),
    }),
  }

  economic.fiveYear = [
    { label: t('districtAnalytics.fiveY.industry'),       values: industryYears,     trend: industryTrend,   trendTone: 'green' },
    { label: t('districtAnalytics.fiveY.export'),         values: exportYears,       trend: exportTrend,     trendTone: 'green' },
    { label: t('districtAnalytics.fiveY.import'),         values: importYears,       trend: importTrend,     trendTone: importYears[4] <= importYears[0] ? 'green' : 'red' },
    { label: t('districtAnalytics.fiveY.tradeDeficit'),   values: deficitYears,      trend: deficitTrend,    trendTone: deficitLast < deficitFirst ? 'green' : 'red' },
    { label: t('districtAnalytics.fiveY.construction'),   values: constructionYears, trend: `${constructionYears[4] >= 100 ? '+' : ''}${(constructionYears[4] - constructionYears[0]).toFixed(1)}`, trendTone: constructionYears[4] >= constructionYears[0] ? 'green' : 'red' },
    migrationYears   ? { label: t('districtAnalytics.fiveY.migration'),    values: migrationYears,   trend: migTrend,        trendTone: migLast > migFirst * 2 ? 'red' : 'green' } : null,
    enterprisesYears ? { label: t('districtAnalytics.fiveY.enterprises'),  values: enterprisesYears, trend: enterpriseTrend, trendTone: enterprisesYears[4] >= enterprisesYears[0] ? 'green' : 'red' } : null,
    unemploymentYears && unemploymentYears[0] != null
      ? { label: t('districtAnalytics.fiveY.unemployment'), values: unemploymentYears, trend: `−${(parseFloat(unemploymentStart) - parseFloat(unemployment)).toFixed(1)} ${ppPoints}`, trendTone: 'green' }
      : null,
    { label: t('districtAnalytics.fiveY.investments'),    values: investmentYears,   trend: investTrend,     trendTone: 'green' },
  ].filter(Boolean)

  economic.investmentSources = rd?.investSources
    ? rd.investSources.map((s) => ({
        label: t(`districtAnalytics.invSrc.${s.key}`),
        percent: s.pct,
        color: INVEST_SRC_COLORS[s.key] || '#6B7280',
      }))
    : rd
      ? null
      : [
          { label: t('districtAnalytics.invSrc.foreign'),      percent: 44.3, color: '#003D7C' },
          { label: t('districtAnalytics.invSrc.enterprises'),  percent: 19.1, color: '#059669' },
          { label: t('districtAnalytics.invSrc.govBudget'),    percent: 16.0, color: '#D97706' },
          { label: t('districtAnalytics.invSrc.population'),   percent: 13.9, color: '#7C3AED' },
          { label: t('districtAnalytics.invSrc.restoration'),  percent:  6.7, color: '#6B7280' },
        ]

  economic.perCapita = {
    industry: perCapitaIndustry,
    services: perCapitaServices,
    trade: perCapitaTrade,
    invest: perCapitaInvest,
    construction: perCapitaConstr,
  }

  const benchIsCity = districtKey === 'fargona_city'
  const bm = rd?.benchmark ?? null
  economic.benchmark = {
    versus: benchIsCity ? t('districtAnalytics.bench.regionAvg') : t('districtAnalytics.bench.ferganaCenter'),
    districtLabel: t(`districtsList.${districtKey}`),
    benchmarkLabel: benchIsCity ? t('districtAnalytics.bench.regionAvg') : t('districtAnalytics.bench.ferganaCenter'),
    rows: [
      { label: t('regionAnalytics.brief.industry'),      district: perCapitaIndustry, benchmark: bm ? bm.industry     : (benchIsCity ? 11186 : 38187) },
      { label: t('regionAnalytics.brief.investments'),    district: perCapitaInvest,   benchmark: bm ? bm.invest       : (benchIsCity ? 4726  : 21491) },
      { label: t('regionAnalytics.econ.services'),        district: perCapitaServices, benchmark: bm ? bm.services     : (benchIsCity ? 11400 : 36753) },
      { label: t('districtAnalytics.sector.trade'),       district: perCapitaTrade,    benchmark: bm ? bm.trade        : (benchIsCity ? 9380  : 19785) },
      { label: t('regionAnalytics.sector.construction'),  district: perCapitaConstr,   benchmark: bm ? bm.construction : (benchIsCity ? 5100  :  9878) },
    ],
  }

  const realArea = rd?.area != null ? rd.area : d.area
  const hasSalary = rd?.avgSalary != null
  const hasTourism = rd?.tourism != null
  const hasGrpAggregate = rd?.grpBln != null
  const realSalary = hasSalary ? rd.avgSalary : Math.round(2100 + p.growth * 200 + p.infra * 900)
  const tourVisitors = hasTourism ? `${rd.tourism.visitors}K` : `${Math.round(80 + p.tourism * 300)}K`
  const tourObjects = hasTourism ? rd.tourism.objects : Math.max(4, Math.round(8 + p.tourism * 40))
  const grpPC = Math.round((grpTotal * 1e9) / popAbs / 1000)
  // For pilot cities (rd present), drop KPIs that lack a verified source so the
  // dashboard never displays fabricated salary/tourism/GRP-per-capita numbers.
  // City-level export figures aren't published in the farstat.uz folder
  // (only viloyat-level is available); show the export tile only when we
  // have an explicit foreignTrade2025.exportMln on the city record.
  const hasCityExport = rd?.foreignTrade2025?.exportMln != null
  economic.macroKpis = [
    { label: t('regionAnalytics.brief.population'),       value: fmt(popAbs),               sub: `${Math.round(popAbs / realArea).toLocaleString('ru-RU')}/${t('regionAnalytics.units.kmSq')}`, delta: rd ? '' : t(d.kind === 'city' ? 'districtAnalytics.macro.cityRate' : 'districtAnalytics.macro.ruralRate'), tone: 'green' },
    { label: t('regionAnalytics.pop.area'),               value: `${realArea} ${t('regionAnalytics.units.kmSq')}`, sub: t('districtAnalytics.macro.administrative'), delta: '', tone: 'blue' },
    rd?.mahallas != null
      ? { label: t('districtAnalytics.macro.mahalla'),    value: fmt(rd.mahallas),          sub: t('districtAnalytics.macro.mahallaUnit'), delta: '', tone: 'blue' }
      : null,
    { label: t('districtAnalytics.macro.industryShort'),  value: fmt(industryBln),          sub: mlrdSum, delta: rd?.industryGrowthPct != null ? growthChip(rd.industryGrowthPct) : (rd ? '' : `${industryTrend} 5Y`),  tone: toneOf(rd?.industryGrowthPct) },
    hasCityExport
      ? { label: t('districtAnalytics.fiveY.export'),     value: fmt(rd.foreignTrade2025.exportMln), sub: t('districtAnalytics.macro.mlnUSD'), delta: growthChip(rd.foreignTrade2025.exportPct), tone: toneOf(rd.foreignTrade2025.exportPct) }
      : (!rd ? { label: t('districtAnalytics.fiveY.export'), value: fmt(exportYears[4]), sub: mlrdSum, delta: `${exportTrend} 5Y`, tone: 'green' } : null),
    { label: t('regionAnalytics.brief.investments'),      value: fmt(investBln),            sub: mlrdSum, delta: rd?.investGrowthPct != null ? growthChip(rd.investGrowthPct) : (rd ? '' : `${investTrend} 5Y`), tone: toneOf(rd?.investGrowthPct) },
    (hasSalary || !rd) ? { label: t('districtAnalytics.macro.avgSalary'), value: fmt(realSalary), sub: t('districtAnalytics.macro.thsSumPerMonth'), delta: rd ? '' : '+86% 5Y', tone: 'green' } : null,
    (hasTourism || !rd) ? { label: t('districtAnalytics.macro.tourism'), value: tourVisitors, sub: t('districtAnalytics.macro.visitorsPerYear'), delta: t('districtAnalytics.macro.objects', { n: tourObjects }), tone: 'blue' } : null,
    (hasGrpAggregate || !rd) ? { label: t('districtAnalytics.macro.grpPerCapita'), value: fmt(grpPC), sub: t('districtAnalytics.macro.thsSumPerPerson'), delta: t(grpPC > 15000 ? 'districtAnalytics.macro.aboveProv' : 'districtAnalytics.macro.belowProv'), tone: grpPC > 15000 ? 'green' : 'amber' } : null,
  ].filter(Boolean)

  const abroadCount = rd?.population?.abroad
  opportunities.criticalIssues = [
    migrationYears
      ? {
          code: 'I1',
          severity: migrationYears[4] > migrationYears[0] * 3 ? 'high' : 'medium',
          title: t('districtAnalytics.crit.migrationCrisis'),
          detail: t('districtAnalytics.crit.migrationDetail', {
            peak: fmt(migrationYears[3]),
            accum: abroadCount != null ? fmt(abroadCount) : fmt(Math.round(migrationYears.reduce((a, b) => a + b, 0))),
            pct: abroadCount != null ? ((abroadCount / (popAbs * 0.52)) * 100).toFixed(0) : ((migrationYears.reduce((a, b) => a + b, 0) / (popAbs * 0.52)) * 100).toFixed(0),
          }),
          kpi: { from: fmt(migrationYears[3]), to: fmt(Math.round(migrationYears[0] * 2)), unit: t('districtAnalytics.crit.unitDeparturesPerYear') },
        }
      : abroadCount != null
        ? {
            code: 'I1',
            severity: abroadCount / popAbs > 0.05 ? 'high' : 'medium',
            title: t('districtAnalytics.crit.migrationCrisis'),
            detail: t('districtAnalytics.crit.migrationDetail', {
              peak: '—',
              accum: fmt(abroadCount),
              pct: ((abroadCount / (popAbs * 0.52)) * 100).toFixed(0),
            }),
            kpi: { from: fmt(abroadCount), to: fmt(Math.round(abroadCount * 0.7)), unit: t('districtAnalytics.crit.unitDeparturesPerYear') },
          }
        : null,
    {
      code: 'I2',
      severity: p.industry < 30 ? 'high' : 'medium',
      title: p.industry < 30 ? t('districtAnalytics.crit.weakIndustry') : t('districtAnalytics.crit.singleSector'),
      detail: p.industry < 30
        ? t('districtAnalytics.crit.weakIndustryDetail', { share: p.industry })
        : t('districtAnalytics.crit.singleSectorDetail', { share: p.industry }),
      kpi: { from: `${p.industry}%`, to: `${Math.min(50, p.industry + 8)}%`, unit: t('districtAnalytics.crit.unitGrpShare') },
    },
    {
      code: 'I3',
      severity: water < 50 ? 'high' : 'medium',
      title: t('districtAnalytics.crit.infraGaps'),
      detail: t('districtAnalytics.crit.infraGapsDetail', { water, sewage, roads }),
      kpi: { from: `${water}%`, to: '≥70%', unit: t('regionAnalytics.infra.water') },
    },
    {
      code: 'I4',
      severity: 'medium',
      title: t('districtAnalytics.crit.dormantBiz'),
      detail: t('districtAnalytics.crit.dormantBizDetail', { n: fmt(Math.round(336 * scale)), shadow: Math.round(25 + (1 - p.infra) * 15) }),
      kpi: { from: `${Math.round(25 + (1 - p.infra) * 15)}%`, to: '12%', unit: t('districtAnalytics.crit.unitShadow') },
    },
    {
      code: 'I5',
      severity: p.growth < 7.5 ? 'medium' : 'low',
      title: t('districtAnalytics.crit.incomeGap'),
      detail: t('districtAnalytics.crit.incomeGapDetail', {
        n: fmt(Math.round((grpTotal * 1e9) / popAbs / 1000)),
        cmp: t(p.industry >= 40 ? 'districtAnalytics.crit.closeTo' : 'districtAnalytics.crit.fartherFrom'),
      }),
      kpi: { from: `×${(38187 / Math.max(1, perCapitaIndustry)).toFixed(1)}`, to: '×1.5', unit: t('districtAnalytics.crit.unitGap') },
    },
    {
      code: 'I6',
      severity: p.enclave ? 'high' : 'low',
      title: p.enclave ? t('districtAnalytics.crit.enclaveLogistics') : t('districtAnalytics.crit.digitalLag'),
      detail: p.enclave
        ? t('districtAnalytics.crit.enclaveLogisticsDetail')
        : t('districtAnalytics.crit.digitalLagDetail', { n: Math.round(60 + p.infra * 30) }),
      kpi: p.enclave
        ? { from: '1', to: '2', unit: t('districtAnalytics.crit.unitCorridors') }
        : { from: `${Math.round(60 + p.infra * 30)}%`, to: '95%', unit: t('districtAnalytics.crit.unitCoverage') },
    },
  ].filter(Boolean)

  const strategyPick = (title, base, kpi, owner) => ({
    title, budget: Math.round(base * scale * 10) / 10, kpi, owner,
  })
  summary.strategicPriorities = [
    {
      horizon: '2026',
      label: t('districtAnalytics.strategic.quickWins'),
      color: '#DC2626',
      items: [
        strategyPick(water < 55 ? t('regionAnalytics.plan.water2026') : t('districtAnalytics.strategic.modernize'), water < 55 ? 12.8 : 6.2, `${water}% → 70%`, t('regionAnalytics.owner.hokimNbu')),
        strategyPick(t('districtAnalytics.strategic.smbSubsidy'), 8.0, t('districtAnalytics.strategic.jobsAdded', { n: Math.round(1200 * scale) }), t('regionAnalytics.owner.nbuCredit')),
        strategyPick(t('districtAnalytics.strategic.energyEff'),  5.6, t('regionAnalytics.kpi.peakCut12'), t('districtAnalytics.owner.uzEnergoNbu')),
      ],
    },
    {
      horizon: '2027–2028',
      label: t('districtAnalytics.strategic.sectorBreakthrough'),
      color: '#D97706',
      items: [
        p.textile >= 0.5 || d.kind === 'city'
          ? strategyPick(t('regionAnalytics.plan.smartTextile'), 24.0, t('regionAnalytics.kpi.exportPlus35'), 'IFC + NBU')
          : strategyPick(t('districtAnalytics.strategic.agroProcHub'), 18.0, t('districtAnalytics.strategic.addedValue35'), t('districtAnalytics.owner.minAgroNbu')),
        p.tourism >= 0.7
          ? strategyPick(t('districtAnalytics.strategic.tourHub'), 12.5, t('districtAnalytics.strategic.visitors', { n: Math.round(60 + p.tourism * 300) }), t('districtAnalytics.owner.minTourism'))
          : strategyPick(t('districtAnalytics.strategic.cooperativeSmb'), 5.2, t('districtAnalytics.strategic.jobsAdded', { n: Math.round(600 * scale) }), t('districtAnalytics.owner.nbuHokim')),
        d.kind === 'city'
          ? strategyPick(t('regionAnalytics.plan.itParkBranch'), 6.4, t('districtAnalytics.strategic.itJobs', { n: Math.round(1200 * scale) }), t('regionAnalytics.owner.minDigital'))
          : strategyPick(t('districtAnalytics.strategic.logisticsWh'), 9.0, t('districtAnalytics.strategic.turnoverPlus40'), t('districtAnalytics.owner.minTransport')),
      ],
    },
    {
      horizon: '2029–2031',
      label: t('districtAnalytics.strategic.scaling'),
      color: '#059669',
      items: [
        strategyPick(t('districtAnalytics.strategic.exportHub'), 45.0, t('districtAnalytics.strategic.exportUSD', { n: Math.round(50 + p.textile * 400) }), t('districtAnalytics.owner.nbuExportMfa')),
        strategyPick(t('districtAnalytics.strategic.greenEnergy'), 28.0, t('districtAnalytics.strategic.mwRen', { n: Math.round(40 + p.infra * 120) }), t('districtAnalytics.owner.uzEnergo')),
        strategyPick(t('districtAnalytics.strategic.socialInfra'), 32.0, t('districtAnalytics.strategic.schoolsAdded', { n: Math.max(4, Math.round(popK * 0.06)) }), t('districtAnalytics.owner.hokim')),
      ],
    },
  ]

  // Verified 2026 city plan (only present when sourced — see fargona_city.plan2026)
  const plan2026 = rd?.plan2026 ?? null

  return { brief, economic, infra, population, mahalla, opportunities, summary, plan2026 }
}

function buildTopMahallas(d, p, scale) {
  // Mahalla names are local Uzbek toponyms — leave unchanged across locales.
  const names = d.kind === 'city'
    ? ['Markaziy', 'Yangi hayot', 'Istiqlol', 'Bunyodkor', 'Do\'stlik']
    : ['Turon', 'Oltintop', 'Yangiobod', 'G\'alaba', 'Bo\'ston']
  return names.map((name, i) => ({
    name,
    loans: Math.max(4, Math.round((24 - i * 2) * scale)),
    score: parseFloat((9.0 - i * 0.3).toFixed(1)),
  }))
}

function buildStrengths(d, p, t) {
  const s = []
  if (d.kind === 'city') s.push(t('districtAnalytics.swot.strengths.cityAgglom', { n: d.population }))
  if (p.textile >= 0.6) s.push(t('districtAnalytics.swot.strengths.textileCluster'))
  if (p.tourism >= 0.7) s.push(t('districtAnalytics.swot.strengths.tourismPotential'))
  if (p.industry >= 40) s.push(t('districtAnalytics.swot.strengths.industryBase', { n: p.industry }))
  if (p.agri >= 45) s.push(t('districtAnalytics.swot.strengths.agroSector', { n: p.agri }))
  s.push(t('districtAnalytics.swot.strengths.grpGrowth', { n: p.growth.toFixed(1) }))
  s.push(t('districtAnalytics.swot.strengths.investInflow', { n: (1.6 + p.growth * 0.15).toFixed(1) }))
  if (p.infra >= 0.75) s.push(t('districtAnalytics.swot.strengths.matureInfra'))
  if (!p.enclave) s.push(t('districtAnalytics.swot.strengths.linkedToValley'))
  return s.slice(0, 7)
}

function buildWeaknesses(d, p, water, sewage, t) {
  const w = []
  if (water < 50) w.push(t('districtAnalytics.swot.weak.lowWater', { n: water }))
  if (sewage < 50) w.push(t('districtAnalytics.swot.weak.sewageProblems', { n: sewage }))
  if (p.infra < 0.6) w.push(t('districtAnalytics.swot.weak.engNetworkLow', { n: Math.round(p.infra * 100) }))
  if (p.industry < 30) w.push(t('districtAnalytics.swot.weak.weakIndustry'))
  if (p.agri >= 55) w.push(t('districtAnalytics.swot.weak.monoAgrarian'))
  if (p.enclave) w.push(t('districtAnalytics.swot.weak.enclave'))
  w.push(t('districtAnalytics.swot.weak.smbOldEquipment'))
  w.push(t('regionAnalytics.swot.weak.informal'))
  w.push(t('regionAnalytics.swot.weak.digitalSkills'))
  return w.slice(0, 8)
}

function buildOpportunities(d, p, t) {
  const o = []
  if (p.tourism >= 0.6) o.push(t('districtAnalytics.swot.opp.tourismHub'))
  if (p.textile >= 0.5) o.push(t('regionAnalytics.swot.opp.smartTextile'))
  if (d.kind === 'city') o.push(t('regionAnalytics.swot.opp.itPark'))
  o.push(t('districtAnalytics.swot.opp.agroExport'))
  o.push(t('districtAnalytics.swot.opp.logisticsCorridor'))
  o.push(t('regionAnalytics.swot.opp.greenEnergy'))
  o.push(t('regionAnalytics.swot.opp.exportDiv'))
  return o.slice(0, 6)
}

function buildThreats(d, p, t) {
  const high = t('regionAnalytics.priority.high')
  const med = t('regionAnalytics.priority.medium')
  const th = [
    { label: t('regionAnalytics.swot.threats.climate'),   level: high },
    { label: t('regionAnalytics.swot.threats.global'),    level: med },
    { label: t('regionAnalytics.swot.threats.rawPrices'), level: med },
    { label: t('regionAnalytics.swot.threats.migration'), level: p.infra < 0.6 ? high : med },
    { label: t('regionAnalytics.swot.threats.shocks'),    level: med },
  ]
  if (p.enclave) th.push({ label: t('districtAnalytics.swot.threats.enclaveGeo'), level: high })
  return th
}

function buildPlan(d, p, scale, water, t) {
  const plan = []
  if (water < 55) plan.push({ horizon: t('regionAnalytics.horizon.0_6'), title: t('regionAnalytics.plan.water2026'), mlrd: Math.round(12.8 * scale * 10) / 10, owner: t('regionAnalytics.owner.hokimNbu'), kpi: `${water}% → 60%` })
  plan.push({ horizon: t('regionAnalytics.horizon.6_12'), title: t('regionAnalytics.plan.energySmb'), mlrd: Math.round(8.6 * scale * 10) / 10, owner: t('regionAnalytics.owner.nbuCredit'), kpi: t('regionAnalytics.kpi.peakCut12') })
  if (p.textile >= 0.4 || d.kind === 'city') {
    plan.push({ horizon: t('regionAnalytics.horizon.12_18'), title: t('regionAnalytics.plan.smartTextile'), mlrd: Math.round(24.0 * scale * 10) / 10, owner: 'IFC + NBU', kpi: t('regionAnalytics.kpi.exportPlus35') })
  } else {
    plan.push({ horizon: t('regionAnalytics.horizon.12_18'), title: t('districtAnalytics.strategic.agroProcHub'), mlrd: Math.round(18.0 * scale * 10) / 10, owner: t('districtAnalytics.owner.minAgroNbu'), kpi: t('districtAnalytics.strategic.addedValue35') })
  }
  if (d.kind === 'city') {
    plan.push({ horizon: t('regionAnalytics.horizon.18_24'), title: t('regionAnalytics.plan.itParkBranch'), mlrd: Math.round(6.4 * scale * 10) / 10, owner: t('regionAnalytics.owner.minDigital'), kpi: t('districtAnalytics.strategic.jobsAdded', { n: Math.round(1200 * scale) }) })
  } else {
    plan.push({ horizon: t('regionAnalytics.horizon.18_24'), title: t('districtAnalytics.strategic.cooperativeSmb'), mlrd: Math.round(5.2 * scale * 10) / 10, owner: t('districtAnalytics.owner.nbuHokim'), kpi: t('districtAnalytics.strategic.jobsAdded', { n: Math.round(600 * scale) }) })
  }
  while (plan.length < 4) plan.unshift({ horizon: t('regionAnalytics.horizon.0_6'), title: t('districtAnalytics.plan.baseline'), mlrd: 1.0, owner: 'NBU', kpi: t('districtAnalytics.plan.riskMap') })
  return plan.slice(0, 4)
}

// Fergana-region aggregate: for the overview panel (no district selected).
// Headline population, GRP and growth come from farstat.uz
// "Makroiqtisodiy ko'rsatkichlar" (Jan–Dec 2025, preliminary). Cities,
// districts and area are derived from the per-district profiles (excluding
// non-Fergana entries like samarqand_region).
export function buildFerganaOverview() {
  const ferganaKeys = Object.keys(PROFILE).filter((k) => {
    const d = districtByKey[k]
    return d && (d.kind === 'city' || d.kind === 'district')
  })
  const cities = ferganaKeys.filter((k) => districtByKey[k].kind === 'city').length
  const districts = ferganaKeys.filter((k) => districtByKey[k].kind === 'district').length
  const totalArea = ferganaKeys.reduce((s, k) => s + districtByKey[k].area, 0)

  // Verified 2025 totals from farstat.uz Makroiqtisodiy ko'rsatkichlar table.
  const totalPopulationAbs = 4223044   // 1 jan 2026
  const totalGrpBln = 111305.3         // mlrd soʻm, Jan–Dec 2025 preliminary
  const avgGrowth = 8.1                // 108.1% YoY

  return {
    totalPopulationK: totalPopulationAbs / 1000,
    totalPopulationAbs,
    totalGrpBln,
    avgGrowth,
    cities,
    districts,
    totalArea,
  }
}

// Samarkand-region aggregate: same shape as buildFerganaOverview, headline
// values verified from samstat.uz / NBU Excel briefs (Jan–Dec 2025).
export function buildSamarqandOverview() {
  const cities = samarqandDistricts.filter((d) => d.kind === 'city').length
  const districts = samarqandDistricts.filter((d) => d.kind === 'district').length
  const totalArea = samarqandDistricts.reduce((s, d) => s + d.area, 0)

  return {
    totalPopulationK: 4379.791,         // 4 379 791 (1 jan 2026)
    totalPopulationAbs: 4379791,
    totalGrpBln: 121489.5,              // mlrd soʻm (NBU Excel brief, 2025)
    avgGrowth: 8.0,                     // 108.0% YoY
    cities,
    districts,
    totalArea,
  }
}
