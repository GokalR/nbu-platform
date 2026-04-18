/**
 * Format seconds into "m:ss" string.
 * @param {number|null} sec - Duration in seconds
 * @returns {string}
 */
export function formatDuration(sec) {
  if (!sec) return ''
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}
