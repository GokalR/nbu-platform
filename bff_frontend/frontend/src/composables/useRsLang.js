import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

/**
 * Regional Strategist language helper. The RS module stores its copy
 * locally inside each component (mirroring the original React port's
 * T = { ru, uz } pattern). This composable returns the active locale
 * key so components can do: const t = T[lang.value].
 */
export function useRsLang() {
  const { locale } = useI18n()
  const lang = computed(() => (locale.value === 'uz' ? 'uz' : 'ru'))
  return { lang }
}
