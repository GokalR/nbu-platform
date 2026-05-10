/**
 * Mapping of CERR district.macro.indicators[].key → theme group + role.
 *
 * The 17 keys are stable across all 14 regions (verified in CERR_V2_DATA_AUDIT.md).
 * Each theme block renders one "headline" indicator (full row with sparkline-position
 * value, rank chip) and 3-5 detail rows.
 */

export const THEMES = [
  { id: 'prod', name: 'Производство', sub: 'Промышленность · сельское хозяйство', icon: 'factory' },
  { id: 'ext',  name: 'Внешний сектор', sub: 'Экспорт · инвестиции',                icon: 'globe'   },
  { id: 'bud',  name: 'Бюджет',         sub: 'Доходы · платные услуги',             icon: 'coin'    },
  { id: 'soc',  name: 'Социальная сфера', sub: 'Бедность · занятость',              icon: 'users'   },
]

// theme_id → { headline: indicatorKey, rows: [indicatorKey, ...] }
export const THEME_MAP = {
  prod: {
    headline: 'industry_volume_bln_uzs',
    rows: [
      'industry_growth_pct',
      'industry_per_capita_uzs',
      'agriculture_volume_bln',
      'agriculture_growth_pct',
    ],
  },
  ext: {
    headline: 'investment_volume_mln_usd',
    rows: [
      'investment_growth_pct',
      'export_volume_mln_usd',
      'export_growth_pct',
    ],
  },
  bud: {
    headline: 'budget_revenue_bln',
    rows: [
      'budget_revenue_growth_pct',
      'market_services_volume_bln',
      'market_services_growth_pct',
    ],
  },
  soc: {
    headline: 'poverty_rate_pct_2026_04_01',
    rows: [
      'poverty_rate_pct_2026_01_01',
      'unemployment_rate_pct_2026_04_01',
      'unemployment_rate_pct_2026_01_01',
    ],
  },
}

/** Returns { theme_id: { theme, headline, rows } } where each indicator carries
 *  its full CERR record plus this district's value, rank, total. */
export function groupMacroByTheme(macro) {
  if (!macro || !Array.isArray(macro.indicators)) return []
  const byKey = new Map(macro.indicators.map((i) => [i.key, i]))
  return THEMES.map((theme) => {
    const def = THEME_MAP[theme.id]
    const headlineInd = def && byKey.get(def.headline)
    const rowInds = (def?.rows || []).map((k) => byKey.get(k)).filter(Boolean)
    return {
      ...theme,
      headline: headlineInd ? annotateIndicator(headlineInd) : null,
      rows: rowInds.map(annotateIndicator),
    }
  }).filter((t) => t.headline || t.rows.length)
}

/** Pull current district's value (the "highlighted" point) and its rank. */
function annotateIndicator(ind) {
  const points = Array.isArray(ind.points) ? ind.points : []
  // Sort points by value desc; record original "highlighted" point's rank.
  const sorted = [...points].sort((a, b) => (b.value ?? -Infinity) - (a.value ?? -Infinity))
  const highlightedIdx = sorted.findIndex((p) => p.highlighted)
  const total = points.length
  const rank = highlightedIdx >= 0 ? highlightedIdx + 1 : null
  const myPoint = points.find((p) => p.highlighted) || null
  // Percentile: top of list = 100, bottom = 0.
  const percentile = rank && total > 1 ? Math.round(((total - rank) / (total - 1)) * 100) : null
  return {
    ...ind,
    value: myPoint ? myPoint.value : null,
    rank,
    total,
    percentile,
  }
}
