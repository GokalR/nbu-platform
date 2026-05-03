/**
 * Enum field metadata for Golden Mart.
 *
 * For these fields the database stores a language-agnostic code (e.g.
 * 'city', 'no', 'high'); the UI renders a localized label via i18n
 * (gmEnum.* keys in ru.json/uz.json). Keeps free-form translation of
 * static enum values out of admin's hands.
 *
 * Used by:
 *   - admin forms (V1 + V2): render <select> instead of <input> for these keys
 *   - public detail view: translate code → label on render
 *   - backend seed_gm_data.py: writes codes
 *   - backend lifespan: migrates existing Russian text to codes
 */

// Single source of truth: { fieldKey: { i18nGroup: 'objectType', codes: ['city','tuman'] } }
export const ENUM_FIELDS = {
  // Section 1 — Базовая информация
  s1_2: { group: 'objectType',     codes: ['city', 'tuman'] },
  s1_3: { group: 'yesNo',          codes: ['yes', 'no'] },
  // Section 21 — Critical problems (city level only)
  s21_2:  { group: 'priority', codes: ['high', 'medium', 'low'] },
  s21_5:  { group: 'priority', codes: ['high', 'medium', 'low'] },
  s21_8:  { group: 'priority', codes: ['high', 'medium', 'low'] },
  s21_11: { group: 'priority', codes: ['high', 'medium', 'low'] },
  s21_14: { group: 'priority', codes: ['high', 'medium', 'low'] },
}

export function isEnumField(fieldKey) {
  return fieldKey in ENUM_FIELDS
}

/**
 * Free-form text field (admin types content, not picked from enum).
 * These have a paired `_uz` column in DB so admin enters both languages.
 * Public detail view picks `data[key_uz]` when locale==='uz', else `data[key]`.
 */
export function isFreeTextField(attr) {
  if (!attr) return false
  return attr.unit === 'текст' && !isEnumField(attr.key)
}

/**
 * Pick the right value for the current locale from a row.
 * - Free-form text: try `_uz` if locale='uz' and value present, else fall back to `key`
 * - Enum: same value (it's a code, translated via i18n at render)
 * - Numeric: same value
 */
export function valueForLocale(row, attr, locale) {
  if (!row) return null
  if (isFreeTextField(attr) && locale === 'uz') {
    const uz = row[`${attr.key}_uz`]
    if (uz != null && uz !== '') return uz
  }
  return row[attr.key]
}

export function enumOptions(fieldKey) {
  return ENUM_FIELDS[fieldKey]?.codes || []
}

export function enumI18nKey(fieldKey, code) {
  const meta = ENUM_FIELDS[fieldKey]
  if (!meta) return code
  return `gmEnum.${meta.group}.${code}`
}

/**
 * Translate an enum code → label for the current locale.
 * Pass the i18n `t` function. Returns the original code if unknown.
 */
export function enumLabel(fieldKey, code, t) {
  if (code == null || code === '') return ''
  const meta = ENUM_FIELDS[fieldKey]
  if (!meta) return String(code)
  if (!meta.codes.includes(code)) return String(code)  // legacy text — leave as-is
  return t(`gmEnum.${meta.group}.${code}`)
}
