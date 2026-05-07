const THIN_SPACE = '\u2009'

export function rsFormatNumber(n) {
  const str = typeof n === 'number' ? Math.round(n).toString() : String(n).replace(/\s/g, '')
  return str.replace(/\B(?=(\d{3})+(?!\d))/g, THIN_SPACE)
}

export function rsFormatDecimal(n, fractionDigits = 1) {
  const [intPart, frac] = n.toFixed(fractionDigits).split('.')
  const intFormatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, THIN_SPACE)
  return frac !== undefined ? `${intFormatted},${frac}` : intFormatted
}

export function rsScoreColor(score) {
  if (score < 40) return '#DC2626'
  if (score < 60) return '#D97706'
  if (score < 80) return '#2957A2'
  return '#059669'
}

export function cn(...args) {
  return args.filter(Boolean).join(' ')
}
