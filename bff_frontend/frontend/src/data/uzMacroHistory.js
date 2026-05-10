/* National macroeconomic series 2021-2025.
 * Source: stat.uz full-year totals; tracked in UZBEKISTAN_MACRO_2021_2025.md.
 * `abs` is nominal trln soums; `realYoY` is real growth % (only published for
 * GDP and investments). Nulls = gaps in the public series. */

export const UZ_MACRO_YEARS = [2021, 2022, 2023, 2024, 2025]

export const UZ_MACRO_HISTORY = {
  gdp: {
    label: 'ВВП',
    unit: 'трлн сум',
    abs: [861.2, 1041.9, 1261.8, 1535.4, 1849.7],
    realYoY2025: 7.7,
  },
  ind: {
    label: 'Промышленность',
    unit: 'трлн сум',
    abs: [451.6, 551.1, 655.8, 885.8, 1101.1],
  },
  inv: {
    label: 'Инвестиции в осн. капитал',
    unit: 'трлн сум',
    abs: [236.6, 266.2, 356.1, 507.5, 591.1],
    realYoY2025: 10.5,
  },
  retail: {
    label: 'Розничный товарооборот',
    unit: 'трлн сум',
    /* 2021 cell intentionally null — only Jan-Aug 2021 is published
     * (143.4 трлн); using a partial-year value next to full-year totals
     * would distort the bar chart. Documented in UZBEKISTAN_MACRO_2021_2025.md. */
    abs: [null, 319.3, 326.2, 403.4, 482.4],
  },
  serv: {
    label: 'Рыночные услуги',
    unit: 'трлн сум',
    abs: [389.4, 509.6, 664.8, 840.1, 1050.3],
  },
  pop: {
    label: 'Население',
    unit: 'млн чел.',
    /* 2021-2023 from stat.uz; 2025 = 38 236 704 (asof 1.01.2026) from
     * raqamlarda.national.population. 2024 = linear interpolation
     * between 36.7998 and 38.2367 (≈37.52) — see UZBEKISTAN_MACRO_2021_2025.md. */
    abs: [33.2713, 36.0249, 36.7998, 37.5183, 38.2367],
    interpolatedYears: [2024],
  },
}

/** "1 849,7" — Russian-style thousands separator + decimal comma. */
export function fmtTrln(n) {
  if (n == null) return '—'
  const [int, dec] = Number(n).toFixed(1).split('.')
  return int.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ',' + dec
}

/** Build an SVG polyline `points` string from a 5-year series; null years are
 *  skipped so the line just gets shorter. Returns '' if fewer than 2 points. */
export function buildSparkPoints(values, w = 100, h = 24, pad = 2) {
  const pts = []
  values.forEach((v, i) => {
    if (v == null) return
    pts.push({ i, v })
  })
  if (pts.length < 2) return ''
  const min = Math.min(...pts.map((p) => p.v))
  const max = Math.max(...pts.map((p) => p.v))
  const range = max - min || 1
  const last = values.length - 1
  return pts
    .map((p) => {
      const x = pad + (p.i / last) * (w - pad * 2)
      const y = h - pad - ((p.v - min) / range) * (h - pad * 2)
      return `${x.toFixed(2)},${y.toFixed(2)}`
    })
    .join(' ')
}

/** Build mini-bar geometry for the 5-year hero tile chart. Each bar gets
 *  `{ x, y, w, h, isLast, hasValue }`. Heights are scaled to the series
 *  max so the latest (and tallest) year fills the chart. Null years render
 *  as a thin baseline tick. Caller draws labels for first/last year. */
export function buildBars(values, w = 100, h = 28, gap = 3) {
  const n = values.length
  const slot = w / n
  const bw = Math.max(2, slot - gap)
  const max = Math.max(...values.filter((v) => v != null))
  const range = max || 1
  return values.map((v, i) => {
    const x = i * slot + (slot - bw) / 2
    if (v == null) {
      return { x, y: h - 1, w: bw, h: 1, isLast: i === n - 1, hasValue: false }
    }
    const bh = Math.max(1, (v / range) * (h - 1))
    return { x, y: h - bh, w: bw, h: bh, isLast: i === n - 1, hasValue: true }
  })
}
