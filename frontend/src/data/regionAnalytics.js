// Rich per-region analytics data, derived from the main.html dashboard by @analytics_per_region.
// The template uses Marg'ilon (Ferghana) as the canonical shape. Per-region numbers scale
// from the base region data so the dashboard is populated for every oblast.
//
// User-visible labels accept a `t` translator (vue-i18n) so they re-render on locale change.
// Any caller without translation context can pass `(key) => key` as a fallback.

import { regions, national } from './regions'

const TEMPLATE_POPULATION = 661.0 // thousand — Marg'ilon benchmark
const TEMPLATE_GRP = 3616 // mlrd UZS
const identity = (k) => k

function parsePopulation(str) {
  const n = parseFloat(String(str).replace(',', '.'))
  return Number.isFinite(n) ? n * 1000 : TEMPLATE_POPULATION // mln → thousand
}
function parseExports(str) {
  const n = parseFloat(String(str).replace('$', '').replace(',', '.'))
  return Number.isFinite(n) ? n : 1.2
}
function parseGrowth(str) {
  const n = parseFloat(String(str).replace('%', '').replace(',', '.'))
  return Number.isFinite(n) ? n : 8.0
}
function fmt(n, d = 0) {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('ru-RU', { minimumFractionDigits: d, maximumFractionDigits: d })
}

export function buildAnalytics(regionKey, t = identity) {
  const r = regionKey && regions[regionKey] ? regions[regionKey] : null
  const pop = r ? parsePopulation(r.population) : 36800 // thousand
  const popScale = pop / TEMPLATE_POPULATION
  const grpGrowth = r ? parseGrowth(r.gdpGrowth) : parseGrowth(national.gdpGrowth)
  const expBil = r ? parseExports(r.exports) : parseExports(national.exports)
  const empl = (r ? r.employment : national.employment) || { employed: 85, selfEmployed: 60, education: 35 }
  const bars = (r ? r.bars : national.bars) || { industry: 80, agriculture: 65, services: 60 }
  const bank = (r ? r.bank : national.bank) || { credits: 78, newBusiness: 62, exporters: 52 }
  const mahallas = r ? r.mahallas : national.mahallas
  const districts = r ? r.districts : 14
  const area = r ? r.area : '—'

  const grpTotal = Math.round(TEMPLATE_GRP * popScale * (grpGrowth / 8.0))
  const industryBln = Math.round((grpTotal * (bars.industry / (bars.industry + bars.agriculture + bars.services))))
  const tradeBln = Math.round(grpTotal * 0.185)
  const servicesBln = Math.round(grpTotal * 0.297)
  const investBln = Math.round(883 * popScale * (grpGrowth / 8.0))
  const unemployment = Math.max(3.2, 6.5 - grpGrowth * 0.2).toFixed(1)
  const unemploymentStart = (parseFloat(unemployment) + 6.5).toFixed(1)

  const mlrdSum = t('regionAnalytics.units.bnSum')
  const peopleUnit = t('regionAnalytics.units.people')
  const sumUnit = t('regionAnalytics.units.sum2025')
  const ppPoints = t('regionAnalytics.units.pp')

  const brief = {
    score: Math.min(9.4, 7.2 + grpGrowth * 0.12).toFixed(1),
    kpis: [
      { label: t('regionAnalytics.brief.grp'),            value: fmt(grpTotal),       unit: mlrdSum, delta: `+${grpGrowth.toFixed(1)}%`, tone: 'green' },
      { label: t('regionAnalytics.brief.industry'),       value: fmt(industryBln),    unit: mlrdSum, delta: '+16.7%', tone: 'green' },
      { label: t('regionAnalytics.brief.investments'),    value: fmt(investBln),      unit: mlrdSum, delta: `×${(2.0 + grpGrowth * 0.12).toFixed(1)}`, tone: 'green' },
      { label: t('regionAnalytics.brief.unemployment'),   value: `${unemployment}%`,  unit: '',      delta: `−${(parseFloat(unemploymentStart) - parseFloat(unemployment)).toFixed(1)} ${ppPoints}`, tone: 'green' },
      { label: t('regionAnalytics.brief.population'),     value: fmt(Math.round(pop * 1000)), unit: peopleUnit, delta: '+6.1%', tone: 'blue' },
      { label: t('regionAnalytics.brief.resilience'),     value: Math.min(9.4, 7.2 + grpGrowth * 0.12).toFixed(1), unit: '/ 10', delta: t('regionAnalytics.brief.strong'), tone: 'blue' },
    ],
  }

  const economic = {
    kpis: [
      { label: t('regionAnalytics.econ.businessCoverage'), value: `${Math.round(70 + bank.newBusiness * 0.2)}%`, sub: t('regionAnalytics.econ.activePoints', { n: Math.round(mahallas * 0.65) }), tone: 'green' },
      { label: t('regionAnalytics.brief.industry'),        value: `${fmt(industryBln)} ${t('regionAnalytics.units.bnShort')}`, sub: sumUnit, tone: 'blue' },
      { label: t('regionAnalytics.econ.retailTrade'),      value: `${fmt(tradeBln)} ${t('regionAnalytics.units.bnShort')}`,    sub: sumUnit, tone: 'blue' },
      { label: t('regionAnalytics.econ.services'),         value: `${fmt(servicesBln)} ${t('regionAnalytics.units.bnShort')}`, sub: sumUnit, tone: 'blue' },
    ],
    history: [2021, 2022, 2023, 2024, 2025].map((y, i) => {
      const factor = 0.55 + i * 0.12
      return {
        year: y,
        grp: Math.round(grpTotal * factor),
        industry: Math.round(industryBln * factor),
        invest: Math.round(investBln * factor * (i === 4 ? 2.6 : 1)),
      }
    }),
    sectors: [
      { name: t('regionAnalytics.sector.industry'),    percent: Math.min(55, 30 + bars.industry * 0.25).toFixed(1), color: '#003D7C' },
      { name: t('regionAnalytics.sector.services'),    percent: Math.min(40, 18 + bars.services * 0.2).toFixed(1),  color: '#0054A6' },
      { name: t('regionAnalytics.sector.construction'),percent: '18.5', color: '#2563EB' },
      { name: t('regionAnalytics.sector.agriculture'), percent: Math.min(20, 4 + bars.agriculture * 0.12).toFixed(1), color: '#059669' },
    ],
    trade: {
      importMln: Math.round(40 * popScale),
      exportMln: Math.round(11.4 * popScale * (grpGrowth / 8.0)),
      deficitMln: Math.round(-28.6 * popScale),
      exportGrowth: '+46.7%',
    },
    entities: {
      active: Math.round(866 * popScale),
      inactive: Math.round(336 * popScale),
      opened: Math.round(141 * popScale),
      closed: Math.round(338 * popScale),
      activeShare: 72,
      types: [
        { code: t('regionAnalytics.orgForm.ip'),     count: Math.round(817 * popScale), share: 60 },
        { code: t('regionAnalytics.orgForm.ooo'),    count: Math.round(264 * popScale), share: 22 },
        { code: t('regionAnalytics.orgForm.farmer'), count: Math.round(84 * popScale),  share: 7 },
        { code: t('regionAnalytics.orgForm.other'),  count: Math.round(37 * popScale),  share: 3 },
      ],
    },
    aiNote: t('regionAnalytics.ai.smbClosing'),
  }

  const infra = {
    kpis: [
      { label: t('regionAnalytics.infra.electricity'), value: '100%',  delta: t('regionAnalytics.infra.coverage'),  tone: 'green' },
      { label: t('regionAnalytics.infra.water'),       value: '30.6%', delta: t('regionAnalytics.infra.critical'),  tone: 'red' },
      { label: t('regionAnalytics.infra.gas'),         value: '89%',   delta: t('regionAnalytics.infra.stable'),    tone: 'green' },
      { label: t('regionAnalytics.infra.sewage'),      value: '44.8%', delta: t('regionAnalytics.infra.belowNorm'), tone: 'amber' },
      { label: t('regionAnalytics.infra.transport'),   value: '80%',   delta: t('regionAnalytics.infra.inOperation'), tone: 'blue' },
    ],
    matrix: [
      { name: t('regionAnalytics.infra.matrix.electricity'),  status: 'ok',   note: t('regionAnalytics.infra.note.elNoOutages') },
      { name: t('regionAnalytics.infra.matrix.drinkingWater'), status: 'bad', note: t('regionAnalytics.infra.note.waterModern') },
      { name: t('regionAnalytics.infra.matrix.gas'),          status: 'ok',   note: t('regionAnalytics.infra.note.gasWorking') },
      { name: t('regionAnalytics.infra.matrix.sewage'),       status: 'warn', note: t('regionAnalytics.infra.note.sewageNeeded') },
      { name: t('regionAnalytics.infra.matrix.roads'),        status: 'warn', note: t('regionAnalytics.infra.note.roads49km') },
      { name: t('regionAnalytics.infra.matrix.publicTransport'), status: 'ok', note: t('regionAnalytics.infra.note.transportRenewed') },
      { name: t('regionAnalytics.infra.matrix.digital'),      status: 'warn', note: t('regionAnalytics.infra.note.lte5g') },
    ],
    budgetMlrd: Math.round(46.3 * popScale * 10) / 10,
    roads: {
      totalKm: 160,
      asphaltKm: 49,
      gravelKm: 23,
      patchedKm: 42,
      earthKm: 46,
    },
    education: { schools: 11, schoolsPlanned: 3, kindergartens: 19, kindergartensPlanned: 30 },
    problems: [
      { code: 'M1', name: t('regionAnalytics.problems.waterRecon'),    cost: 12.8, priority: t('regionAnalytics.priority.high') },
      { code: 'M2', name: t('regionAnalytics.problems.sewageSystem'),  cost: 8.4,  priority: t('regionAnalytics.priority.high') },
      { code: 'M3', name: t('regionAnalytics.problems.roadNetwork'),   cost: 6.2,  priority: t('regionAnalytics.priority.medium') },
      { code: 'M4', name: t('regionAnalytics.problems.energySystem'),  cost: 3.0,  priority: t('regionAnalytics.priority.medium') },
      { code: 'T1', name: t('regionAnalytics.problems.newSchools3'),   cost: 4.8,  priority: t('regionAnalytics.priority.high') },
      { code: 'T2', name: t('regionAnalytics.problems.kindergartens30'), cost: 2.2, priority: t('regionAnalytics.priority.medium') },
      { code: 'T3', name: t('regionAnalytics.problems.digital5g'),     cost: 1.5,  priority: t('regionAnalytics.priority.low') },
      { code: 'T4', name: t('regionAnalytics.problems.greenEnergy'),   cost: 1.5,  priority: t('regionAnalytics.priority.low') },
    ],
    aiNote: t('regionAnalytics.ai.infraGap'),
  }

  const population = {
    kpis: [
      { label: t('regionAnalytics.brief.population'),       value: fmt(Math.round(pop * 1000)), delta: '+6.1%', sub: t('regionAnalytics.pop.under18'), tone: 'blue' },
      { label: t('regionAnalytics.pop.area'),               value: area, delta: '—', sub: t('regionAnalytics.pop.density', { n: Math.round((pop * 1000) / 20).toLocaleString('ru-RU') }), tone: 'blue' },
      { label: t('regionAnalytics.pop.economicallyActive'), value: fmt(Math.round(29811 * popScale)), delta: `+${fmt(Math.round(5745 * popScale))}`, sub: t('regionAnalytics.pop.since2021'), tone: 'green' },
      { label: t('regionAnalytics.brief.unemployment'),     value: `${unemployment}%`, delta: `${unemploymentStart}% → ${unemployment}%`, sub: '2021 → 2025', tone: 'green' },
    ],
    laborTrend: [
      { year: 2021, formal: 16137, informal: 3455, abroad: 4474, unemployed: 2784 },
      { year: 2022, formal: 16618, informal: 3010, abroad: 4875, unemployed: 2246 },
      { year: 2023, formal: 17618, informal: 2995, abroad: 5213, unemployed: 1854 },
      { year: 2024, formal: 19455, informal: 2765, abroad: 5566, unemployed: 1520 },
      { year: 2025, formal: 20415, informal: 2210, abroad: 6936, unemployed: 1197 },
    ].map((row) => ({
      year: row.year,
      formal: Math.round(row.formal * popScale),
      informal: Math.round(row.informal * popScale),
      abroad: Math.round(row.abroad * popScale),
      unemployed: Math.round(row.unemployed * popScale),
    })),
    unemploymentTrend: [
      { year: 2021, value: parseFloat(unemploymentStart) },
      { year: 2022, value: parseFloat(unemploymentStart) - 2.0 },
      { year: 2023, value: parseFloat(unemploymentStart) - 3.7 },
      { year: 2024, value: parseFloat(unemploymentStart) - 5.2 },
      { year: 2025, value: parseFloat(unemployment) },
    ],
    migration: {
      countAbroad: Math.round(6812 * popScale),
      growthPct: '+52%',
      shareOfWorkforce: '19.2%',
      totalEmployed: Math.round(29811 * popScale),
      warning: t('regionAnalytics.migration.warning'),
    },
    program2026: {
      title: t('regionAnalytics.program.title'),
      goal: Math.round(2500 * popScale),
      breakdown: [
        { code: 'P1', label: t('regionAnalytics.program.crafts'),       count: Math.round(800 * popScale) },
        { code: 'P2', label: t('regionAnalytics.program.subsidies'),    count: Math.round(620 * popScale) },
        { code: 'P3', label: t('regionAnalytics.program.employment'),   count: Math.round(580 * popScale) },
        { code: 'P4', label: t('regionAnalytics.program.exportCluster'),count: Math.round(500 * popScale) },
      ],
    },
  }

  const mahalla = {
    kpis: [
      { label: t('regionAnalytics.mahalla.mahallas'),     value: mahallas.toLocaleString('ru-RU'), sub: t('regionAnalytics.mahalla.districtsCount', { n: districts }), tone: 'blue' },
      { label: t('regionAnalytics.mahalla.creditCover'),  value: `${bank.credits}%`, sub: t('regionAnalytics.mahalla.smbInRegion'), tone: 'green' },
      { label: t('regionAnalytics.mahalla.newIp'),        value: `${bank.newBusiness}%`, sub: t('regionAnalytics.mahalla.quarterGrowth'), tone: 'green' },
      { label: t('regionAnalytics.mahalla.digitalization'), value: `${Math.round(bank.credits * 0.65)}%`, sub: t('regionAnalytics.mahalla.onlineBanking'), tone: 'blue' },
    ],
    bankMetrics: [
      { label: t('regionAnalytics.bank.smbCredits'),     percent: bank.credits, color: 'bg-primary' },
      { label: t('regionAnalytics.bank.newEntrepr'),     percent: bank.newBusiness, color: 'bg-primary-container' },
      { label: t('regionAnalytics.bank.exporters'),      percent: bank.exporters, color: 'bg-secondary' },
      { label: t('regionAnalytics.bank.employed'),       percent: empl.employed, color: 'bg-tertiary' },
      { label: t('regionAnalytics.bank.selfEmployed'),   percent: empl.selfEmployed, color: 'bg-tertiary opacity-60' },
      { label: t('regionAnalytics.bank.profEducation'),  percent: empl.education, color: 'bg-primary opacity-60' },
    ],
    topMahallas: [
      { name: 'Олтиариқ', loans: Math.round(24 * popScale), score: 8.8 },
      { name: 'Беш-терак', loans: Math.round(19 * popScale), score: 8.4 },
      { name: 'Янги Марғилон', loans: Math.round(17 * popScale), score: 8.1 },
      { name: 'Турон', loans: Math.round(15 * popScale), score: 7.9 },
      { name: 'Фарғона йўли', loans: Math.round(14 * popScale), score: 7.6 },
    ],
    digitalAdoption: {
      payments: 72,
      cards: 58,
      merchants: 46,
      lending: 34,
    },
  }

  const opportunities = {
    swot: {
      strengths: [
        t('regionAnalytics.swot.strengths.textileCenter'),
        t('regionAnalytics.swot.strengths.industryGrowth', { n: Math.round(grpGrowth * 9) }),
        t('regionAnalytics.swot.strengths.investments2025', { n: Math.round(grpGrowth * 20) }),
        t('regionAnalytics.swot.strengths.logistics'),
        t('regionAnalytics.swot.strengths.workforce'),
        t('regionAnalytics.swot.strengths.employmentGrowth', { n: Math.round(grpGrowth * 3) }),
        t('regionAnalytics.swot.strengths.exportTrend'),
      ],
      weaknesses: [
        t('regionAnalytics.swot.weak.water'),
        t('regionAnalytics.swot.weak.sewage'),
        t('regionAnalytics.swot.weak.energyDeficit'),
        t('regionAnalytics.swot.weak.oldEquipment'),
        t('regionAnalytics.swot.weak.land'),
        t('regionAnalytics.swot.weak.informal'),
        t('regionAnalytics.swot.weak.digitalSkills'),
        t('regionAnalytics.swot.weak.exportNarrow'),
      ],
      opportunities: [
        t('regionAnalytics.swot.opp.tourism'),
        t('regionAnalytics.swot.opp.smartTextile'),
        t('regionAnalytics.swot.opp.logisticsHub'),
        t('regionAnalytics.swot.opp.itPark'),
        t('regionAnalytics.swot.opp.exportDiv'),
        t('regionAnalytics.swot.opp.greenEnergy'),
      ],
      threats: [
        { label: t('regionAnalytics.swot.threats.climate'),   level: t('regionAnalytics.priority.high') },
        { label: t('regionAnalytics.swot.threats.global'),    level: t('regionAnalytics.priority.medium') },
        { label: t('regionAnalytics.swot.threats.rawPrices'), level: t('regionAnalytics.priority.medium') },
        { label: t('regionAnalytics.swot.threats.migration'), level: t('regionAnalytics.priority.high') },
        { label: t('regionAnalytics.swot.threats.shocks'),    level: t('regionAnalytics.priority.medium') },
      ],
    },
    aiRecommendation: t('regionAnalytics.ai.swotRecommendation'),
  }

  const summary = {
    score: brief.score,
    radar: [
      { axis: t('regionAnalytics.radar.economy'),       value: Math.min(9.5, 6.5 + grpGrowth * 0.3).toFixed(1), provincial: 7.0 },
      { axis: t('regionAnalytics.radar.infra'),         value: 6.5, provincial: 7.2 },
      { axis: t('regionAnalytics.radar.employment'),    value: Math.min(9.0, 6.0 + grpGrowth * 0.2).toFixed(1), provincial: 7.0 },
      { axis: t('regionAnalytics.radar.demography'),    value: 7.0, provincial: 7.0 },
      { axis: t('regionAnalytics.radar.investments'),   value: Math.min(9.2, 6.2 + grpGrowth * 0.28).toFixed(1), provincial: 6.8 },
    ],
    comparison: [
      { metric: t('regionAnalytics.compare.industryPC'),  region: Math.round(23847 * (bars.industry / 80)), provincial: 28914 },
      { metric: t('regionAnalytics.compare.servicesPC'),  region: Math.round(16218 * (bars.services / 60)), provincial: 14120 },
      { metric: t('regionAnalytics.compare.tradePC'),     region: Math.round(10092 * (bars.services / 60)), provincial: 9380 },
      { metric: t('regionAnalytics.compare.investPC'),    region: Math.round(13344 * (grpGrowth / 8.0)), provincial: 9910 },
      { metric: t('regionAnalytics.compare.exportPC'),    region: Math.round((expBil * 1000) * popScale / pop * 1000000), provincial: 28 },
    ],
    plan: [
      { horizon: t('regionAnalytics.horizon.0_6'),    title: t('regionAnalytics.plan.water2026'),  mlrd: 12.8, owner: t('regionAnalytics.owner.hokimNbu'),  kpi: '30.6% → 55%' },
      { horizon: t('regionAnalytics.horizon.6_12'),   title: t('regionAnalytics.plan.energySmb'),  mlrd: 8.6,  owner: t('regionAnalytics.owner.nbuCredit'), kpi: t('regionAnalytics.kpi.peakCut12') },
      { horizon: t('regionAnalytics.horizon.12_18'),  title: t('regionAnalytics.plan.smartTextile'), mlrd: 24.0, owner: 'IFC + NBU', kpi: t('regionAnalytics.kpi.exportPlus35') },
      { horizon: t('regionAnalytics.horizon.18_24'),  title: t('regionAnalytics.plan.itParkBranch'), mlrd: 6.4,  owner: t('regionAnalytics.owner.minDigital'), kpi: t('regionAnalytics.kpi.jobs1200') },
    ],
    conclusion: t('regionAnalytics.summary.conclusion'),
  }

  return { brief, economic, infra, population, mahalla, opportunities, summary }
}
