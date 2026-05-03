/**
 * Golden Mart loader — single entry point that the public dashboards use.
 *
 *   Public detail/dashboard
 *           │
 *           ▼
 *      loadEntity(level, key)
 *           │
 *           ├──→ try API: GET /api/gm/data/{level}/{key}
 *           │     ├─ success → flatten rows[] → return shape used by views
 *           │     └─ failure → fall back to static JS file (resilient)
 *           │
 *           └──→ static fallback (qoqon.js, etc.)
 *
 * Returned shape:
 *   {
 *     scalars: { s1_1: 'Qoʻqon', s1_4: 60, ... }    // latest year wins
 *     yearly:  { s2_2: [4340.0, 5602.6, ...],       // 2021..2026 series
 *                s11_7: [5783, 6561, ...] }
 *     years:   [2021, 2022, 2023, 2024, 2025, 2026]
 *     source:  'api' | 'static-fallback'
 *   }
 */
import { gmGetEntityData } from '@/services/eduApi.js'

const STATIC_FALLBACKS = {
  city: {
    qoqon_city: () => import('./qoqon.js').then((m) => m.QOQON_GM),
  },
}

const YEARS = [2021, 2022, 2023, 2024, 2025, 2026]

function rowsToShape(rows) {
  const years = rows.map((r) => r.year).sort((a, b) => a - b)
  const byYear = Object.fromEntries(rows.map((r) => [r.year, r]))
  const scalars = {}
  const yearly = {}

  // Find all field keys (any s{n}_{i} present in any row)
  const fieldKeys = new Set()
  for (const r of rows) {
    for (const k of Object.keys(r)) {
      if (/^s\d+_\d+$/.test(k)) fieldKeys.add(k)
    }
  }

  for (const k of fieldKeys) {
    // Build the year-series array (uses real years present in DB)
    const series = years.map((y) => byYear[y]?.[k] ?? null)
    yearly[k] = series
    // Pick latest non-null as scalar
    const latest = [...series].reverse().find((v) => v != null)
    scalars[k] = latest ?? null
  }
  return { scalars, yearly, years, source: 'api' }
}

function staticToShape(staticObj) {
  // Static JS file is one flat object of latest values; year arrays unknown.
  return {
    scalars: { ...staticObj },
    yearly: {},
    years: YEARS,
    source: 'static-fallback',
  }
}

export async function loadEntity(level, key) {
  try {
    const res = await gmGetEntityData(level, key)
    if (res?.rows?.length) return rowsToShape(res.rows)
    // API responded but no rows — fall through
  } catch (e) {
    console.warn(`[gm loader] API failed for ${level}/${key}, falling back:`, e.message)
  }
  // Fallback
  const loader = STATIC_FALLBACKS[level]?.[key]
  if (loader) {
    const staticObj = await loader()
    return staticToShape(staticObj)
  }
  // No fallback — return empty shape
  return { scalars: {}, yearly: {}, years: YEARS, source: 'empty' }
}

/**
 * Helper: turn the API "scalars" view into a flat object mirroring the
 * old static qoqon.js shape — for components that haven't been rewritten
 * to use `yearly` series yet.
 */
export function flatScalars(loaded) {
  return loaded.scalars
}

/**
 * Reshape the loaded API data into the shape consumed by
 * `buildDistrictAnalytics` (the REAL_DATA[key] block in districtAnalytics.js).
 * This lets `DistrictAnalyticsView` read live values from the DB while the
 * rest of the analytics-build pipeline keeps working unchanged.
 *
 * Map:
 *   populationK         ← s1_6 (latest year) / 1000
 *   area / mahallas     ← s1_4 / s1_5
 *   industryBln, etc.   ← s2_2..s2_7 at 2025
 *   *GrowthPct          ← yearly[2025] / yearly[2024] × 100
 *   perCapita.*         ← bln × 1e6 / popAbs
 *   fiveYear.*          ← s2_2..s2_7 sliced 2021..2025
 *   populationFiveYear  ← s1_6 series 2019..2026 if available, else 2021..2026
 *   vitalStats.*        ← s11_7 / s11_8 series
 *   ageGroups2025       ← s1_12..s1_28 at 2025
 *
 * Returns null if the loaded shape has no usable numeric data.
 */
export function reshapeCityToDistrictAnalytics(loaded) {
  if (!loaded || !loaded.years?.length) return null
  const { years, yearly, scalars } = loaded
  const idx = (y) => years.indexOf(y)
  const at = (key, y) => {
    const i = idx(y)
    if (i < 0) return null
    return yearly[key]?.[i] ?? null
  }
  const num = (v) => (typeof v === 'number' ? v : v == null ? null : Number(v))

  const industryBln     = num(at('s2_2', 2025))
  const servicesBln     = num(at('s2_3', 2025))
  const tradeBln        = num(at('s2_4', 2025))
  const constructionBln = num(at('s2_5', 2025))
  const agricultureBln  = num(at('s2_6', 2025))
  const investBln       = num(at('s2_7', 2025))

  // Need 2024 to derive nominal YoY growth.
  const ind2024 = num(at('s2_2', 2024))
  const svc2024 = num(at('s2_3', 2024))
  const trd2024 = num(at('s2_4', 2024))
  const con2024 = num(at('s2_5', 2024))
  const agr2024 = num(at('s2_6', 2024))
  const inv2024 = num(at('s2_7', 2024))

  const pop2025 = num(at('s1_6', 2025)) ?? num(scalars.s1_6)
  const popK = pop2025 != null ? pop2025 / 1000 : null
  const popAbs = pop2025

  const yoy = (a, b) => (a != null && b != null && b !== 0 ? (a / b) * 100 : null)
  const perCap = (bln) =>
    bln != null && popAbs && popAbs > 0
      ? Math.round((bln * 1e9) / popAbs / 1000)
      : null

  // 5-year array 2021..2025 (filter nulls preserved as zeros? no — keep nulls
  // and let downstream guards handle them).
  const series2021_2025 = (key) =>
    [2021, 2022, 2023, 2024, 2025].map((y) => num(at(key, y)))

  const popSeries = [2021, 2022, 2023, 2024, 2025, 2026]
    .map((y) => {
      const v = num(at('s1_6', y))
      return v != null ? v / 1000 : null
    })
    .filter((v) => v != null)
  const popLabels = [2021, 2022, 2023, 2024, 2025, 2026].slice(0, popSeries.length)

  // Vital stats — births / deaths from §11 (preferred) or §9 mirror.
  const births = [2021, 2022, 2023, 2024, 2025].map(
    (y) => num(at('s11_7', y)) ?? num(at('s9_5', y)),
  )
  const deaths = [2021, 2022, 2023, 2024, 2025].map(
    (y) => num(at('s11_8', y)) ?? num(at('s9_6', y)),
  )
  const births2025 = births[4]
  const deaths2025 = deaths[4]

  // Age groups 2025 — s1_12..s1_28 at 2025.
  const AGE_KEYS = {
    '0-2': 's1_12', '3-5': 's1_13', '6-7': 's1_14', '8-15': 's1_15',
    '16-17': 's1_16', '18-19': 's1_17', '20-24': 's1_18', '25-29': 's1_19',
    '30-34': 's1_20', '35-39': 's1_21', '40-49': 's1_22', '50-59': 's1_23',
    '60-69': 's1_24', '70-74': 's1_25', '75-79': 's1_26', '80-84': 's1_27',
    '85+':   's1_28',
  }
  const ageGroups2025 = {}
  let anyAge = false
  for (const [bucket, key] of Object.entries(AGE_KEYS)) {
    const v = num(at(key, 2025))
    if (v != null) anyAge = true
    ageGroups2025[bucket] = v
  }

  // Sector mix as % of the 6-sector sum (matches the static block shape).
  const sectorTotal = [industryBln, servicesBln, tradeBln, constructionBln, agricultureBln]
    .filter((v) => v != null)
    .reduce((a, b) => a + b, 0)
  const sectorPct = (bln) =>
    bln != null && sectorTotal > 0 ? Number(((bln / sectorTotal) * 100).toFixed(1)) : null
  const sectors = sectorTotal > 0
    ? [
        { key: 'industry',     pct: sectorPct(industryBln) },
        { key: 'trade',        pct: sectorPct(tradeBln) },
        { key: 'services',     pct: sectorPct(servicesBln) },
        { key: 'construction', pct: sectorPct(constructionBln) },
        { key: 'agri',         pct: sectorPct(agricultureBln) },
      ].filter((s) => s.pct != null)
    : null

  const rd = {
    populationK: popK,
    area: num(scalars.s1_4),
    mahallas: num(scalars.s1_5),
    industryBln, servicesBln, tradeBln, constructionBln, agricultureBln, investBln,
    industryGrowthPct:    yoy(industryBln, ind2024),
    servicesGrowthPct:    yoy(servicesBln, svc2024),
    tradeGrowthPct:       yoy(tradeBln, trd2024),
    constructionGrowth:   yoy(constructionBln, con2024),
    agricultureGrowthPct: yoy(agricultureBln, agr2024),
    investGrowthPct:      yoy(investBln, inv2024),
    perCapita: {
      industry:     perCap(industryBln),
      services:     perCap(servicesBln),
      trade:        perCap(tradeBln),
      construction: perCap(constructionBln),
      invest:       perCap(investBln),
    },
    fiveYear: {
      industry:     series2021_2025('s2_2'),
      services:     series2021_2025('s2_3'),
      trade:        series2021_2025('s2_4'),
      construction: series2021_2025('s2_5'),
      agriculture:  series2021_2025('s2_6'),
      investments:  series2021_2025('s2_7'),
    },
    populationFiveYear: popSeries,
    populationFiveYearLabels: popLabels,
    vitalStats: {
      births, deaths,
      labels: [2021, 2022, 2023, 2024, 2025],
      births2025, deaths2025,
      naturalIncrease2025:
        births2025 != null && deaths2025 != null ? births2025 - deaths2025 : null,
    },
    ageGroups2025: anyAge ? ageGroups2025 : null,
    sectors,
    _source: loaded.source,   // 'api' | 'static-fallback' | 'empty'
  }
  return rd
}
