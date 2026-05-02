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
