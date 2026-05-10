/** Number formatters for cerr-v2. Mirrors nbu_platform/components.jsx `fmt`. */

export const fmt = {
  num(n) {
    if (n == null) return '—'
    return Math.round(n).toLocaleString('ru-RU').replace(/,/g, ' ')
  },
  pct(n, opts = {}) {
    if (n == null) return '—'
    const sign = opts.signed && n > 0 ? '+' : ''
    return sign + Number(n).toFixed(1).replace('.', ',') + '%'
  },
  shortPop(n) {
    if (n == null) return '—'
    if (n >= 1e6) return (n / 1e6).toFixed(2).replace('.', ',') + ' млн'
    if (n >= 1e3) return (n / 1e3).toFixed(1).replace('.', ',') + ' тыс'
    return String(n)
  },
  ord(n, total) {
    return n != null && total != null ? `${n}/${total}` : '—'
  },
  /** Display value for a KPI: handle "thousands" format for big counts,
   *  "index1" for fractional indices like RAQAMLARDA growth values (107.7%). */
  kpi(kpi) {
    if (kpi.value == null) return '—'
    if (kpi.format === 'index1') return Number(kpi.value).toFixed(1).replace('.', ',')
    if (kpi.format === 'thousands' && kpi.value > 1e5) return fmt.shortPop(kpi.value)
    return fmt.num(kpi.value)
  },
  /** Δ chip text for a KPI. Returns { text, tone } or null if no delta. */
  delta(kpi) {
    const dir = kpi.direction === 'down' ? -1 : kpi.direction === 'neu' ? 0 : 1
    if (kpi.change_pct != null) {
      const isPos = (kpi.change_pct > 0 && dir >= 0) || (kpi.change_pct < 0 && dir < 0)
      const sign = kpi.change_pct > 0 ? '+' : ''
      return {
        text: sign + Number(kpi.change_pct).toFixed(1).replace('.', ',') + '%',
        tone: isPos ? 'pos' : 'neg',
      }
    }
    return null
  },
}

/** Default Material Symbols icon name per CERR KPI key. */
export function iconForKpi(key) {
  const m = {
    population: 'users',
    active_businesses: 'factory',
    unemployed: 'pulse',
    rating_score: 'award',
    problem_loans: 'warn',
    poor_families: 'shield',
    investment: 'coin',
    industry: 'tools',
    mahalla_count: 'grid',
  }
  return m[key] || 'chart'
}
