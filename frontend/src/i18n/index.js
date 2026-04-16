import { createI18n } from 'vue-i18n'
import uz from '@/locales/uz.json'
import ru from '@/locales/ru.json'

const STORAGE_KEY = 'nbu.locale'
const SUPPORTED = ['uz', 'ru']

function detectLocale() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && SUPPORTED.includes(saved)) return saved
  const browser = (navigator.language || 'uz').slice(0, 2).toLowerCase()
  return SUPPORTED.includes(browser) ? browser : 'uz'
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLocale(),
  fallbackLocale: 'uz',
  messages: { uz, ru },
})

export function setLocale(locale) {
  if (!SUPPORTED.includes(locale)) return
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.setAttribute('lang', locale)
}

export const supportedLocales = SUPPORTED
export default i18n
