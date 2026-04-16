<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRsLang } from '@/composables/useRsLang'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import RsStatusTag from '@/components/regionalStrategist/RsStatusTag.vue'
import RsInsightBox from '@/components/regionalStrategist/RsInsightBox.vue'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'
import RsMargilanHeatmap from '@/components/regionalStrategist/RsMargilanHeatmap.vue'
import RsFerganaHeatmap from '@/components/regionalStrategist/RsFerganaHeatmap.vue'
import RsInputSummary from '@/components/regionalStrategist/RsInputSummary.vue'
import RsScoreBreakdown from '@/components/regionalStrategist/RsScoreBreakdown.vue'
import RsClaudeAnalysis from '@/components/regionalStrategist/RsClaudeAnalysis.vue'
import { STEP5_T } from './rs-step5-i18n'
import { CITIES } from '@/data/regionalStrategist/cities'
import { matchCreditProducts, collateralLabel } from '@/data/regionalStrategist/credit-products'
import { computeScore, peerMediansFor } from '@/data/regionalStrategist/scoring'
import { rsApi } from '@/services/rsApi'
import { generateLocalAnalysisAsync } from '@/services/rsLocalAnalysis'
import { onMounted } from 'vue'

const emit = defineEmits(['restart'])
const { lang } = useRsLang()

const store = useRegionalStrategistStore()
const { profile, finance, submissionId, uploads, analysis, analysisStatus } = storeToRefs(store)

// Fergana-city + kindergarten override for section subtitles and project copy.
// Applied on top of STEP5_T[lang] when the user's direction + city match.
// Keeps Margilan branch untouched.
const FERGANA_KINDERGARTEN_OVERRIDE = {
  ru: {
    aiConclusionText:
      'Бизнес имеет хороший потенциал для расширения. Сильные стороны — стабильная история (3–5 лет) и нулевая кредитная нагрузка при ROE 15,5%. Основной риск — текущая ликвидность 1,19 (ниже нормы 1,5). Расширение на 2 ясельные группы (2–3 года) закрывает рыночный пробел в маҳалле и увеличивает выручку на 35–45%.',
    section2Sub: 'Частный детский сад — Фарғона шаҳар, Мирзо Улуғбек MFY',
    section3Sub: 'Ферганская область · 15 районов + 4 города · 98 319 рождений в 2025 → базовый спрос на ДОУ',
    locationInsightText:
      'Мирзо Улуғбек MFY в Фарғона шаҳар — городская маҳалла в столице области (328 409 жителей). Рождаемость региона 98 319 в 2025 году (+0,2%) обеспечивает стабильный приток детей. Государственных ясель в радиусе 1 км — нет; ближайшие частные ДОУ работают с 3 лет. Ниша для групп 2–3 лет открыта.',
    section4Title: 'Бизнес-план: расширение частного детского сада',
    section4Sub: 'ERKIN PARVOZ NURI OLTIN · +2 ясельные группы · Фарғона шаҳар',
    projectDescText:
      'Расширение действующего частного детского сада ERKIN PARVOZ NURI OLTIN MCHJ (ИФУТ 85100, Мирзо Улуғбек MFY, г. Фергана) на 2 ясельные группы для детей 2–3 лет. Ремонт + мебель + оборудование = ~800 млн сум. Дополнительно 36–44 места × 400 тыс. сум/мес × 10 мес. ≈ +1,2–1,5 млрд сум/год выручки при марже 12–14%.',
    coursesLabel: 'НОВЫЕ УСЛУГИ',
    courses: [
      'Ясельная группа (2–3 года)',
      'Полный день 7:30–18:30',
      'Питание 4-разовое',
      'Музыкальные занятия',
      'Физкультура + бассейн',
      'Логопед (вводится)',
      'Раннее развитие речи',
      'Подготовка к мл. группе',
    ],
    studentsCol: 'Дети',
    STARTUP_COSTS: [
      ['Ремонт и подготовка 2 помещений', '250 млн'],
      ['Мебель, кроватки, шкафчики', '150 млн'],
      ['Игровое и развивающее оборудование', '120 млн'],
      ['Кухонное оборудование (расширение)', '80 млн'],
      ['Игрушки, учебные материалы', '50 млн'],
      ['Сантехника, безопасность, пожарная сигнализация', '80 млн'],
      ['Лицензии и маркетинг', '70 млн'],
    ],
    startupTotal: '800 млн сум',
    MONTHLY_COSTS: [
      ['Зарплата (4 воспитателя + 2 нянечки)', '42 млн'],
      ['Питание детей (4-разовое)', '20 млн'],
      ['Коммунальные услуги', '10 млн'],
      ['Повар + помощник', '12 млн'],
      ['Учебные материалы, игрушки', '5 млн'],
      ['Прочие (хозтовары, медикаменты)', '6 млн'],
    ],
    monthlyTotal: '95 млн/мес',
    REVENUE_FORECAST: [
      { period: 'Месяц 1–3', students: 20, revenue: '8 млн', profit: '-14 млн', profitPositive: false },
      { period: 'Месяц 4–6', students: 30, revenue: '12 млн', profit: '-2 млн', profitPositive: false },
      { period: 'Месяц 7–9', students: 38, revenue: '15,2 млн', profit: '+4 млн', profitPositive: true },
      { period: 'Месяц 10–12', students: 44, revenue: '17,6 млн', profit: '+8 млн', profitPositive: true },
    ],
    revenueForecastLabel: 'ПРОГНОЗ ВЫРУЧКИ (400 тыс. сум/мес за место, 2 новые группы)',
    breakeven: 'Точка безубыточности: месяц 4–5 (при наполняемости 70%+)',
    ACTION_STEPS: [
      { week: 'Неделя 1–2', title: 'Доработка бизнес-плана', desc: 'Финансовые прогнозы на 2 ясельные группы, расчёт себестоимости питания', status: 'warning' },
      { week: 'Неделя 3–4', title: 'Подача заявки на кредит', desc: 'Подать на «Развивайся» (23%, до 3,5 млрд, 48 мес.) в отделение NBU Фергана', status: 'negative' },
      { week: 'Месяц 2', title: 'Проектирование помещений', desc: 'Согласовать планировку 2 групповых комнат, спальни, санузлов с СЭС', status: 'neutral' },
      { week: 'Месяц 2–3', title: 'Ремонт и оборудование', desc: 'Закупка кроваток, шкафчиков, игрового оборудования, кухонной техники', status: 'neutral' },
      { week: 'Месяц 3', title: 'Набор персонала', desc: '4 воспитателя + 2 нянечки + повар; медосмотр, аттестация', status: 'neutral' },
      { week: 'Месяц 3–4', title: 'Маркетинг и набор детей', desc: 'Объявления в маҳалле, соцсети, дни открытых дверей для родителей', status: 'neutral' },
      { week: 'Месяц 4', title: 'Открытие 2 ясельных групп', desc: 'Приём первых 20 детей (2–3 года), запуск 4-разового питания', status: 'positive' },
      { week: 'Месяц 7–8', title: 'Выход на окупаемость', desc: '38+ детей, выручка 15+ млн/мес, покрытие расходов расширения', status: 'positive' },
    ],
    ctaSubtitle: 'Подайте заявку на «Развивайся» (до 3,5 млрд, 23%, 48 мес.) — оптимально под расширение с залогом недвижимости.',
    MAHALLA_RANKING: null,
  },
  uz: {
    aiConclusionText:
      'Biznes kengaytirish uchun yaxshi potentsialga ega. Kuchli tomonlar — barqaror tarix (3–5 yil) va nol kredit yuki, ROE 15,5%. Asosiy xavf — joriy likvidlik 1,19 (norma 1,5 dan past). 2 ta yasli guruh (2–3 yosh) ochish mahalladagi bozor bo'shligini to'ldiradi va tushumni 35–45% ga oshiradi.',
    section2Sub: 'Xususiy bolalar bog'chasi — Farg'ona sh., Mirzo Ulug'bek MFY',
    section3Sub: 'Farg'ona viloyati · 15 tuman + 4 shahar · 2025 yilda 98 319 tug'ilish → bolalar bog'chasiga asosiy talab',
    locationInsightText:
      'Farg'ona sh. Mirzo Ulug'bek MFY — viloyat markazi shaharida joylashgan (328 409 aholi). 2025 yildagi tug'ilish 98 319 (+0,2%) barqaror bolalar oqimini ta'minlaydi. 1 km radiusda davlat yasli yo'q; yaqin xususiy bog'chalar 3 yoshdan ishlaydi. 2–3 yoshli guruhlar uchun nisha ochiq.',
    section4Title: 'Biznes-reja: xususiy bolalar bog'chasini kengaytirish',
    section4Sub: 'ERKIN PARVOZ NURI OLTIN · +2 yasli guruh · Farg'ona sh.',
    projectDescText:
      'Amaldagi xususiy bolalar bog'chasi ERKIN PARVOZ NURI OLTIN MCHJ (IFUT 85100, Mirzo Ulug'bek MFY, Farg'ona sh.) ni 2 ta yasli guruh (2–3 yosh) bilan kengaytirish. Ta'mir + mebel + jihoz = ~800 mln so'm. Qo'shimcha 36–44 o'rin × 400 ming so'm/oy × 10 oy ≈ +1,2–1,5 mlrd so'm/yil tushum, marja 12–14%.',
    coursesLabel: 'YaNGI XIZMATLAR',
    courses: [
      'Yasli guruh (2–3 yosh)',
      'To'liq kun 7:30–18:30',
      '4 mahal ovqat',
      'Musiqa mashg'ulotlari',
      'Jismoniy tarbiya + hovuz',
      'Logoped (kiritiladi)',
      'Erta nutq rivojlanishi',
      'Kichik guruhga tayyorgarlik',
    ],
    studentsCol: 'Bolalar',
    STARTUP_COSTS: [
      ['2 ta xonani ta'mirlash va tayyorlash', '250 mln'],
      ['Mebel, krovatkalar, shkafchalar', '150 mln'],
      ['O'yin va rivojlantiruvchi jihozlar', '120 mln'],
      ['Oshxona jihozlari (kengaytirish)', '80 mln'],
      ['O'yinchoqlar, o'quv materiallari', '50 mln'],
      ['Santexnika, xavfsizlik, yong'in signalizatsiyasi', '80 mln'],
      ['Litsenziyalar va marketing', '70 mln'],
    ],
    startupTotal: '800 mln so'm',
    MONTHLY_COSTS: [
      ['Ish haqi (4 tarbiyachi + 2 enaga)', '42 mln'],
      ['Bolalar ovqati (4 mahal)', '20 mln'],
      ['Kommunal xizmatlar', '10 mln'],
      ['Oshpaz + yordamchi', '12 mln'],
      ['O'quv materiallari, o'yinchoqlar', '5 mln'],
      ['Boshqa (xo'jalik, dori-darmon)', '6 mln'],
    ],
    monthlyTotal: '95 mln/oy',
    REVENUE_FORECAST: [
      { period: '1–3 oy', students: 20, revenue: '8 mln', profit: '-14 mln', profitPositive: false },
      { period: '4–6 oy', students: 30, revenue: '12 mln', profit: '-2 mln', profitPositive: false },
      { period: '7–9 oy', students: 38, revenue: '15,2 mln', profit: '+4 mln', profitPositive: true },
      { period: '10–12 oy', students: 44, revenue: '17,6 mln', profit: '+8 mln', profitPositive: true },
    ],
    revenueForecastLabel: 'TUShUM PROGNOZI (400 ming so'm/oy har o'rin, 2 yangi guruh)',
    breakeven: 'Foydalilik nuqtasi: 4–5 oy (to'ldirilish 70%+ da)',
    ACTION_STEPS: [
      { week: '1–2 hafta', title: 'Biznes-planni yakunlash', desc: '2 yasli guruh uchun moliyaviy prognozlar, ovqat tannarxini hisoblash', status: 'warning' },
      { week: '3–4 hafta', title: 'Kreditga ariza berish', desc: 'NBU Farg'ona bo'limiga «Razvivaysya» (23%, 3,5 mlrdgacha, 48 oy) uchun ariza', status: 'negative' },
      { week: '2 oy', title: 'Xonalarni loyihalash', desc: '2 guruh xonasi, uxlash xonasi, sanuzellar rejasini SES bilan kelishish', status: 'neutral' },
      { week: '2–3 oy', title: 'Ta'mir va jihozlash', desc: 'Krovatkalar, shkafchalar, o'yin jihozlari, oshxona texnikasi sotib olish', status: 'neutral' },
      { week: '3 oy', title: 'Xodimlarni yollash', desc: '4 tarbiyachi + 2 enaga + oshpaz; tibbiy ko'rik, attestatsiya', status: 'neutral' },
      { week: '3–4 oy', title: 'Marketing va bolalar yig'ish', desc: 'Mahallada e'lonlar, ijtimoiy tarmoqlar, ota-onalar uchun ochiq kunlar', status: 'neutral' },
      { week: '4 oy', title: '2 yasli guruhni ochish', desc: 'Birinchi 20 bola (2–3 yosh) qabul qilish, 4 mahal ovqatni boshlash', status: 'positive' },
      { week: '7–8 oy', title: 'Foydalilik nuqtasiga chiqish', desc: '38+ bola, tushum 15+ mln/oy, kengaytirish xarajatlarini qoplash', status: 'positive' },
    ],
    ctaSubtitle: '«Razvivaysya» (3,5 mlrd so'mgacha, 23%, 48 oy) uchun ariza bering — ko'chmas mulk garovida kengaytirish uchun optimal.',
    MAHALLA_RANKING: null,
  },
}

// Detect pilot city from the user's profile answers. Only Fergana + Margilan
// have real data; everything else shows a "data not yet available" state.
const resolvedCityId = computed(() => {
  const h = [profile.value.hudud, profile.value.viloyat, profile.value.mahalla].join(' ').toLowerCase()
  if (/marg|марғ|марг/.test(h)) return 'margilan'
  if (/farg|фарғ|ферг|фарг/.test(h)) return 'fergana'
  return null
})
const isPilotCity = computed(() => resolvedCityId.value !== null)
const selectedCity = computed(() => (resolvedCityId.value ? CITIES[resolvedCityId.value] : CITIES.fergana))
const isMargilan = computed(() => resolvedCityId.value === 'margilan')
const isFergana = computed(() => resolvedCityId.value === 'fergana')

const isKindergarten = computed(() => /детск|богча|боғча|kindergarten|дошколь/i.test(finance.value.businessDirection || ''))
const useFerganaKgOverride = computed(() => isFergana.value && isKindergarten.value)
const t = computed(() => {
  const base = STEP5_T[lang.value]
  if (!useFerganaKgOverride.value) return base
  const ov = FERGANA_KINDERGARTEN_OVERRIDE[lang.value] || {}
  return { ...base, ...ov }
})

// Label the user's own region (what they picked), regardless of pilot status.
const userPickedLabel = computed(() => {
  const h = (profile.value.hudud || '').trim()
  const v = (profile.value.viloyat || '').trim()
  return h || v || (isPilotCity.value ? selectedCity.value.name[lang.value] : '')
})
const isCityDataReal = computed(() => {
  if (!isPilotCity.value) return false
  if (isMargilan.value) return true
  const h = (profile.value.hudud || '').toLowerCase()
  return !h
})

// Pick the most recent upload with computed ratios/absolutes (from backend parse).
const extractedFinancials = computed(() => {
  const ups = [...(uploads.value || [])].sort((a, b) => {
    const ta = new Date(a.created_at || 0).getTime()
    const tb = new Date(b.created_at || 0).getTime()
    return tb - ta
  })
  for (const u of ups) {
    const c = u?.parsed?.computed
    if (c && (c.ratios || c.absolutes)) {
      return { ratios: c.ratios || {}, absolutes: c.absolutes || {} }
    }
  }
  return null
})

const formatPct = (v) => (v == null || isNaN(v) ? '—' : `${(v * 100).toFixed(1)}%`)
const formatRatio = (v) => (v == null || isNaN(v) ? '—' : Number(v).toFixed(2))
const formatUzs = (v) => {
  if (v == null || isNaN(v)) return '—'
  const n = Number(v)
  if (Math.abs(n) >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(2)} ${lang.value === 'uz' ? 'млрд' : 'млрд'}`
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)} ${lang.value === 'uz' ? 'млн' : 'млн'}`
  return n.toLocaleString('ru-RU')
}

const financialMetrics = computed(() => {
  const f = extractedFinancials.value
  if (!f) return []
  const r = f.ratios || {}
  const a = f.absolutes || {}
  const L = lang.value
  return [
    { key: 'revenue',      label: L === 'uz' ? 'Тушум'            : 'Выручка',             value: formatUzs(a.revenue),      kind: 'abs' },
    { key: 'netProfit',    label: L === 'uz' ? 'Соф фойда'         : 'Чистая прибыль',      value: formatUzs(a.netProfit),    kind: 'abs' },
    { key: 'grossMargin',  label: L === 'uz' ? 'Ялпи маржа'        : 'Валовая маржа',       value: formatPct(r.grossMargin),  kind: 'pct' },
    { key: 'netMargin',    label: L === 'uz' ? 'Соф маржа'         : 'Чистая маржа',        value: formatPct(r.netMargin),    kind: 'pct' },
    { key: 'roa',          label: 'ROA',                                                    value: formatPct(r.roa),          kind: 'pct' },
    { key: 'roe',          label: 'ROE',                                                    value: formatPct(r.roe),          kind: 'pct' },
    { key: 'currentRatio', label: L === 'uz' ? 'Жорий ликвидлик'   : 'Текущ. ликвидность',  value: formatRatio(r.currentRatio), kind: 'ratio' },
    { key: 'debtToEquity', label: L === 'uz' ? 'Қарз/капитал'      : 'Долг/капитал',        value: formatRatio(r.debtToEquity), kind: 'ratio' },
  ].filter((m) => m.value !== '—')
})

/* ── Excel aggregates section helpers ────────────────────── */
const uploadedFiles = computed(() => (uploads.value || []).filter((u) => u?.original_filename || u?.id))
const hasExcelData = computed(() => uploadedFiles.value.length > 0 || !!extractedFinancials.value)

const kindLabel = (kind) => {
  const map = {
    ru: { balance: 'Баланс', pnl: 'ОПиУ', cashflow: 'ДДС' },
    uz: { balance: 'Balans', pnl: 'FZH', cashflow: 'PH' },
  }
  return map[lang.value]?.[kind] || kind || (lang.value === 'uz' ? 'Файл' : 'Файл')
}

const formatSize = (bytes) => {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

const absoluteHighlights = computed(() => {
  const f = extractedFinancials.value
  if (!f) return []
  const a = f.absolutes || {}
  const L = lang.value
  const items = [
    { key: 'revenue',     raw: a.revenue,     label: L === 'uz' ? 'Йиллик тушум'  : 'Годовая выручка', icon: 'trending-up',  color: '#0054A6', tint: '#EEF4FF',
      hint: L === 'uz' ? 'ОПиУ: жами тушум' : 'ОПиУ: итого выручка' },
    { key: 'netProfit',   raw: a.netProfit,   label: L === 'uz' ? 'Соф фойда'      : 'Чистая прибыль',  icon: 'sparkles',     color: '#10B981', tint: '#E6F7EE',
      hint: L === 'uz' ? 'Солиқдан сўнг'    : 'После налогов' },
    { key: 'totalAssets', raw: a.totalAssets, label: L === 'uz' ? 'Жами активлар'  : 'Итого активов',   icon: 'briefcase',    color: '#8B5CF6', tint: '#F3E8FF',
      hint: L === 'uz' ? 'Баланс якуни'     : 'Итог баланса' },
    { key: 'equity',      raw: a.equity,      label: L === 'uz' ? 'Ўз капитал'     : 'Собственный капитал', icon: 'shield',  color: '#F59E0B', tint: '#FEF3C7',
      hint: L === 'uz' ? 'Пассив: III бўлим': 'Пассив: раздел III' },
  ]
  return items
    .filter((m) => m.raw != null && !isNaN(m.raw))
    .map((m) => ({ ...m, value: formatUzs(m.raw) }))
})

// Sector-aware peer medians: a kindergarten's 12% net margin should not be
// compared to a retailer's 8% — use the bucket that matches businessDirection.
const PEER_MEDIANS = computed(() => peerMediansFor(finance.value.businessDirection))

const ratioBars = computed(() => {
  const f = extractedFinancials.value
  if (!f) return []
  const r = f.ratios || {}
  const L = lang.value
  const defs = [
    { key: 'grossMargin',  label: L === 'uz' ? 'Ялпи маржа'      : 'Валовая маржа',      max: 0.6,  pct: true,  higherBetter: true },
    { key: 'netMargin',    label: L === 'uz' ? 'Соф маржа'       : 'Чистая маржа',       max: 0.25, pct: true,  higherBetter: true },
    { key: 'roa',          label: 'ROA',                                                  max: 0.2,  pct: true,  higherBetter: true },
    { key: 'roe',          label: 'ROE',                                                  max: 0.35, pct: true,  higherBetter: true },
    { key: 'currentRatio', label: L === 'uz' ? 'Жорий ликвидлик' : 'Текущ. ликвидность', max: 3,    pct: false, higherBetter: true },
    { key: 'debtToEquity', label: L === 'uz' ? 'Қарз/капитал'    : 'Долг/капитал',       max: 3,    pct: false, higherBetter: false },
  ]
  const clamp = (v, max) => Math.max(0, Math.min(100, (v / max) * 100))
  const fmtV = (v, pct) => (pct ? formatPct(v) : formatRatio(v))
  return defs
    .map((d) => {
      const user = r[d.key]
      const peer = PEER_MEDIANS.value[d.key]
      if (user == null || isNaN(user)) return null
      const diff = d.higherBetter ? user - peer : peer - user
      const ratio = diff / Math.max(Math.abs(peer), 0.01)
      const verdictTone = ratio >= 0.1 ? 'good' : ratio >= -0.15 ? 'warn' : 'bad'
      const verdictLabel = verdictTone === 'good'
        ? (L === 'uz' ? 'яхши' : 'выше')
        : verdictTone === 'warn' ? (L === 'uz' ? 'ўртача' : 'средне')
        : (L === 'uz' ? 'паст' : 'ниже')
      return {
        key: d.key,
        label: d.label,
        userLabel: fmtV(user, d.pct),
        peerLabel: fmtV(peer, d.pct),
        userBar: clamp(user, d.max),
        peerBar: clamp(peer, d.max),
        verdictTone,
        verdictLabel,
      }
    })
    .filter(Boolean)
})

const excelInsight = computed(() => {
  const f = extractedFinancials.value
  if (!f) return null
  const r = f.ratios || {}
  const L = lang.value
  const strong = []
  const weak = []

  if (r.netMargin != null) {
    if (r.netMargin >= 0.10) strong.push(L === 'uz' ? `соф маржа ${(r.netMargin*100).toFixed(1)}% — яхши даражада` : `чистая маржа ${(r.netMargin*100).toFixed(1)}% — хороший уровень`)
    else if (r.netMargin >= 0.05) strong.push(L === 'uz' ? `соф маржа ${(r.netMargin*100).toFixed(1)}%` : `чистая маржа ${(r.netMargin*100).toFixed(1)}%`)
    else weak.push(L === 'uz' ? `соф маржа паст (${(r.netMargin*100).toFixed(1)}%)` : `чистая маржа низкая (${(r.netMargin*100).toFixed(1)}%)`)
  }
  if (r.currentRatio != null) {
    if (r.currentRatio >= 1.5) strong.push(L === 'uz' ? 'ликвидлик соғлом (>1.5)' : 'ликвидность здоровая (>1.5)')
    else if (r.currentRatio >= 1.0) weak.push(L === 'uz' ? `жорий ликвидлик чегарада (${r.currentRatio.toFixed(2)}) — қисқа муддатли мажбуриятлар чекланган` : `текущая ликвидность на границе (${r.currentRatio.toFixed(2)}) — ограниченный запас по краткосрочным обязательствам`)
    else weak.push(L === 'uz' ? 'ликвидлик хавфли (<1.0)' : 'ликвидность в зоне риска (<1.0)')
  }
  if (r.debtToEquity != null) {
    if (r.debtToEquity > 2) weak.push(L === 'uz' ? 'қарз юки юқори (D/E>2)' : 'высокая долговая нагрузка (D/E>2)')
    else if (r.debtToEquity > 1.5) weak.push(L === 'uz' ? `D/E ${r.debtToEquity.toFixed(2)} — юқори` : `D/E ${r.debtToEquity.toFixed(2)} — повышенный`)
  }
  if (r.roe != null && r.roe > 0.12) strong.push(L === 'uz' ? `ROE ${(r.roe*100).toFixed(1)}% — капитал самарали ишлатилмоқда` : `ROE ${(r.roe*100).toFixed(1)}% — капитал работает эффективно`)
  if (r.roa != null && r.roa < 0.03) weak.push(L === 'uz' ? 'активлар рентабеллиги паст (ROA<3%)' : 'рентабельность активов низкая (ROA<3%)')

  if (!strong.length && !weak.length) return null
  const good = strong.length ? (L === 'uz' ? `Кучли томонлар: ${strong.join('; ')}.` : `Сильные стороны: ${strong.join('; ')}.`) : ''
  const bad = weak.length ? (L === 'uz' ? ` Эътибор берилиши керак: ${weak.join('; ')}.` : ` Требует внимания: ${weak.join('; ')}.`) : ''
  return (good + bad).trim()
})

// On arrival at results: run real backend analysis if configured,
// else fall back to the local deterministic generator.
onMounted(async () => {
  if (analysis.value || analysisStatus.value === 'analyzing') return

  if (rsApi.isConfigured()) {
    store.setAnalysisStatus('analyzing')

    // Ensure submission exists (Step 2 uploads may have already created one).
    if (!submissionId.value) {
      const created = await rsApi.createSubmission({
        profile: profile.value,
        finance: finance.value,
        city_id: resolvedCityId.value,
        lang: lang.value,
      })
      if (!created.ok) {
        store.setAnalysisStatus('error', created.error || 'Submission creation failed')
        return
      }
      store.setSubmission(created.data.id)
    }

    const res = await rsApi.runAnalysis(submissionId.value, { lang: lang.value })
    if (res.ok) {
      store.setAnalysis(res.data)
    } else {
      store.setAnalysisStatus('error', res.error || 'Analysis failed')
    }
    return
  }

  // Demo mode — local generator.
  store.setAnalysisStatus('analyzing')
  const result = await generateLocalAnalysisAsync({
    profile: profile.value,
    finance: finance.value,
    cityId: resolvedCityId.value,
    uploads: uploads.value,
    lang: lang.value,
  })
  store.setAnalysis(result)
})

// Map finance inputs to matcher arguments.
// Parse loan-amount option strings like '200–500 млн', '500 млн – 1 млрд', 'Более 1 млрд'
// into a representative numeric value in sum.  Uses the midpoint of a range.
function parseLoanAmount(raw) {
  const s = String(raw || '').toLowerCase()
  if (!s) return 0
  const mult = s.includes('млрд') ? 1e9 : 1e6 // default to млн
  // Extract all numbers from the string
  const nums = s.match(/[\d.]+/g)?.map(Number).filter(Number.isFinite) || []
  if (!nums.length) return 0
  if (nums.length === 1) {
    // "До 50 млн" → 50 млн; "Более 1 млрд" → 1 млрд; "50 млн гача" → 50 млн
    return nums[0] * mult
  }
  // Range like "200–500 млн" or "500 млн – 1 млрд"
  // If both млн and млрд present (e.g. '500 млн – 1 млрд'), parse individually
  if (s.includes('млн') && s.includes('млрд')) {
    return Math.round((nums[0] * 1e6 + nums[1] * 1e9) / 2)
  }
  return Math.round((nums[0] + nums[1]) / 2 * mult)
}

const matcherInputs = computed(() => {
  const amt = parseLoanAmount(finance.value.loanAmount)
  const collMap = {
    'Недвижимость': 'realEstate',
    'Автотранспорт': 'vehicle',
    'Страховой полис': 'insurance',
    'Недвижимость + автотранспорт': 'realEstate',
  }
  const coll = collMap[finance.value.collateralType] || (finance.value.hasCollateral === 'Да' ? 'realEstate' : null)
  const purposeMap = {
    'Оборотные средства': 'working',
    'Основные средства': 'fixed',
    'Покупка автотранспорта': 'vehicle',
    'Покупка недвижимости': 'realEstate',
  }
  const purpose = purposeMap[finance.value.businessGoal] || 'any'
  const entity = /ИП|ЯТТ/i.test(profile.value.entityType || '') ? 'IP' : 'LLC'
  const firstTime = profile.value.businessAge === '' || /нет|йўқ|менее/i.test(profile.value.businessAge || '')
  return { loanAmount: amt, collateral: coll, purpose, entityType: entity, firstTime, lang: lang.value }
})

const matchedProducts = computed(() => matchCreditProducts(matcherInputs.value).slice(0, 4))
const primaryMatch = computed(() => matchedProducts.value[0])
const altMatches = computed(() => matchedProducts.value.slice(1))

const formatProductCollateral = (p) =>
  p.collateral.map((c) => collateralLabel(c, lang.value)).join(' · ')

/* ── Live score from user data ────────────────────── */
const scoreResult = computed(() => computeScore(profile.value, finance.value, selectedCity.value.id, extractedFinancials.value))
const RADIUS = 54
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const scoreOffset = computed(() => CIRCUMFERENCE - (scoreResult.value.total / 100) * CIRCUMFERENCE)
const scoreColor = computed(() =>
  scoreResult.value.total >= 70 ? '#16a34a' : scoreResult.value.total >= 50 ? '#d97706' : '#dc2626',
)
const verdictLabel = computed(() => {
  const map = {
    good: { ru: 'Xoroshiy potentsial', uz: 'Yaxshi potentsial', cls: 'text-emerald-600 bg-emerald-50' },
    fair: { ru: 'Sredniy potentsial', uz: 'O'rta potentsial', cls: 'text-amber-600 bg-amber-50' },
    weak: { ru: 'Trebuet dorabotki', uz: 'Takomillashtirish kerak', cls: 'text-red-600 bg-red-50' },
  }
  return map[scoreResult.value.verdict]
})

/* ── SWOT colour map (inlined, was SWOTCard) ──────── */
const SWOT_STYLES = {
  emerald: { bg: 'bg-emerald-50', border: 'border-emerald-200', title: 'text-emerald-700', dot: 'bg-emerald-500' },
  red:     { bg: 'bg-red-50',     border: 'border-red-200',     title: 'text-red-700',     dot: 'bg-red-400' },
  blue:    { bg: 'bg-blue-50',    border: 'border-blue-200',    title: 'text-blue-700',    dot: 'bg-blue-500' },
  amber:   { bg: 'bg-amber-50',   border: 'border-amber-200',   title: 'text-amber-700',   dot: 'bg-amber-500' },
}

const swotQuadrants = computed(() => [
  { title: t.value.swotStrengths,     color: 'emerald', items: t.value.SWOT.strengths },
  { title: t.value.swotWeaknesses,    color: 'red',     items: t.value.SWOT.weaknesses },
  { title: t.value.swotOpportunities, color: 'blue',    items: t.value.SWOT.opportunities },
  { title: t.value.swotThreats,       color: 'amber',   items: t.value.SWOT.threats },
])

/* ── Action step circle colour ────────────────────── */
const stepCircleClass = (i, total) => {
  if (i < 2) return 'bg-gold-500'
  if (i >= 6) return 'bg-emerald-500'
  return 'bg-navy-900'
}

const onDownload = () => {
  // eslint-disable-next-line no-alert
  alert(t.value.downloadAlert)
}
</script>

<template>
  <div class="animate-rs-fade-in-up space-y-8 rs-step5-root">
    <!-- Restart link -->
    <button
      type="button"
      @click="emit('restart')"
      class="font-sans text-[14px] font-medium text-navy-700 hover:bg-navy-900/[0.04] rounded-[8px] py-2 px-3 transition-colors duration-150"
    >
      {{ t.restartBtn }}
    </button>

    <!-- ═══ REGION / CITY SELECTION BANNER ═══ -->
    <section
      class="rounded-[14px] overflow-hidden border shadow-rs-card"
      :class="isPilotCity
        ? 'border-navy-200 bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900'
        : 'border-amber-200 bg-gradient-to-r from-amber-50 via-white to-amber-50'"
    >
      <div class="px-8 py-7 flex flex-wrap items-center justify-between gap-6">
        <div class="flex items-center gap-5 min-w-0">
          <span
            class="inline-flex items-center justify-center w-14 h-14 rounded-[14px] shrink-0"
            :class="isPilotCity ? 'bg-gold-500/20 text-gold-400' : 'bg-amber-100 text-amber-700'"
          >
            <RsIcon name="building-2" :size="26" />
          </span>
          <div class="min-w-0">
            <div
              class="font-mono text-[11px] font-bold uppercase tracking-[1.5px] mb-1"
              :class="isPilotCity ? 'text-gold-400' : 'text-amber-700'"
            >
              {{ lang === 'uz' ? 'Сиз танлаган ҳудуд' : 'Выбранный вами регион' }}
            </div>
            <h3
              class="font-sans text-[22px] font-bold leading-tight truncate"
              :class="isPilotCity ? 'text-white' : 'text-carbon'"
            >
              <template v-if="profile.viloyat">{{ profile.viloyat }}</template>
              <template v-else-if="isPilotCity">{{ selectedCity.name[lang] }}</template>
              <template v-else>{{ lang === 'uz' ? 'Ҳудуд кўрсатилмаган' : 'Регион не указан' }}</template>
            </h3>
            <div
              class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 font-sans text-[13px]"
              :class="isPilotCity ? 'text-white/80' : 'text-gray-700'"
            >
              <span v-if="profile.hudud" class="inline-flex items-center gap-1.5">
                <RsIcon name="landmark" :size="13" />
                {{ profile.hudud }}
              </span>
              <span v-if="profile.hudud && profile.mahalla" :class="isPilotCity ? 'text-white/30' : 'text-gray-300'">·</span>
              <span v-if="profile.mahalla" class="inline-flex items-center gap-1.5">
                <RsIcon name="user" :size="13" />
                {{ lang === 'uz' ? 'маҳалла' : 'махалля' }}: {{ profile.mahalla }}
              </span>
            </div>
          </div>
        </div>

        <div class="shrink-0 flex items-center gap-3">
          <span
            v-if="isPilotCity && isCityDataReal"
            class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] rounded-full py-1.5 px-3 bg-emerald-500/15 text-emerald-300 border border-emerald-400/30"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            {{ lang === 'uz' ? 'Тўлиқ маълумот' : 'Полные данные' }}
          </span>
          <span
            v-else-if="isPilotCity"
            class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] rounded-full py-1.5 px-3 bg-gold-500/15 text-gold-300 border border-gold-400/30"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-gold-400"></span>
            {{ lang === 'uz' ? 'Пилот шаҳар' : 'Пилотный город' }}
          </span>
          <span
            v-else
            class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] rounded-full py-1.5 px-3 bg-amber-100 text-amber-800 border border-amber-200"
          >
            <RsIcon name="alert-triangle" :size="12" />
            {{ lang === 'uz' ? 'Маълумотлар чекланган' : 'Данные ограничены' }}
          </span>
        </div>
      </div>
    </section>

    <!-- ═══ A — YOUR ANSWERS FROM STEP 1 + STEP 2 ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div class="px-8 py-6"
           style="background: rgba(215,181,109,0.04); border-bottom: 1px solid rgba(215,181,109,0.12);">
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-gold-500 shrink-0 font-mono text-[15px] font-bold text-white">A</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">
              {{ lang === 'uz' ? 'Сиз тўлдирган маълумотлар' : 'Ваши ответы' }}
              <span class="font-normal text-steel-500 text-[15px]">
                · {{ lang === 'uz' ? '1- ва 2-қадам' : 'Шаг 1 и Шаг 2' }}
              </span>
            </h2>
            <p class="font-sans text-[13px] text-gray-600 mt-1">
              {{ lang === 'uz'
                ? 'Қуйидаги балл, SWOT ва тавсиялар сиз бёрган жавоблар асосида ҳисобланган'
                : 'Балл, SWOT и рекомендации ниже рассчитаны на основании ваших ответов в анкете' }}
            </p>
          </div>
        </div>
      </div>
      <div class="px-8 py-7">
        <RsInputSummary :profile="profile" :finance="finance" :lang="lang" />
      </div>
    </section>

    <!-- ═══ B — AGGREGATED EXCEL DATA (only when user uploaded financials) ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div class="px-8 py-6"
           style="background: rgba(16,185,129,0.05); border-bottom: 1px solid rgba(16,185,129,0.15);">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-emerald-500 shrink-0 font-mono text-[15px] font-bold text-white">B</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">
                {{ lang === 'uz' ? 'Excel файлдан агрегат маълумотлар' : 'Агрегаты из вашего Excel' }}
              </h2>
              <p class="font-sans text-[13px] text-gray-600 mt-1">
                {{ lang === 'uz'
                  ? 'Стандарт 1С / Документы.uz шакллари бўйича автоматик ҳисобланди'
                  : 'Автоматически посчитано по стандартным формам 1С / Документы.uz' }}
              </p>
            </div>
          </div>
          <span v-if="uploadedFiles.length"
                class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-[6px] py-1 px-2">
            {{ uploadedFiles.length }} {{ lang === 'uz' ? 'файл' : 'файл(ов)' }}
          </span>
        </div>
      </div>

      <!-- Empty state — user skipped Excel upload -->
      <div v-if="!hasExcelData" class="px-8 py-10 flex items-start gap-5">
        <span class="inline-flex items-center justify-center w-11 h-11 rounded-full bg-amber-50 shrink-0">
          <RsIcon name="file-question" :size="20" class="text-amber-600" />
        </span>
        <div class="max-w-[560px]">
          <div class="font-sans text-[15px] font-semibold text-carbon">
            {{ lang === 'uz' ? 'Excel файл юкланмаган' : 'Excel файл не загружен' }}
          </div>
          <p class="font-sans text-[13px] text-gray-600 mt-1 leading-[1.6]">
            {{ lang === 'uz'
              ? 'Молия кўрсаткичлари фақат Шаг 2 да қўлда киритилган даромад/харажатга асосланади. 1С ёки Документы.uz дан Баланс ва Фойда ва зарар ҳисоботини юкласангиз, таҳлил аниқроқ бўлади.'
              : 'Финансовые показатели взяты только из введённых вручную на Шаге 2 сумм дохода и расходов. Загрузите Баланс и Отчёт о прибылях из 1С или Документы.uz — тогда анализ будет точнее.' }}
          </p>
        </div>
      </div>

      <!-- Loaded state -->
      <div v-else class="px-8 py-8 space-y-7">
        <!-- Uploaded files list -->
        <div v-if="uploadedFiles.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div v-for="u in uploadedFiles" :key="u.id || u.original_filename"
               class="flex items-center gap-3 border border-rs-border rounded-[10px] py-3 px-4 bg-navy-900/[0.02]">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-[8px] bg-emerald-50 shrink-0">
              <RsIcon name="file-spreadsheet" :size="18" class="text-emerald-600" />
            </span>
            <div class="min-w-0 flex-1">
              <div class="font-sans text-[13px] font-semibold text-carbon truncate">
                {{ u.original_filename || (lang === 'uz' ? 'Файл' : 'Файл') }}
              </div>
              <div class="flex items-center gap-2 mt-[2px]">
                <span class="text-[10px] font-bold uppercase tracking-[0.5px] rounded-[4px] py-[2px] px-[6px]"
                      :class="u.kind === 'balance' ? 'bg-blue-50 text-blue-700' : u.kind === 'pnl' ? 'bg-purple-50 text-purple-700' : 'bg-slate-100 text-slate-600'">
                  {{ kindLabel(u.kind) }}
                </span>
                <span v-if="u.size_bytes" class="text-[11px] text-steel-500 font-mono">
                  {{ formatSize(u.size_bytes) }}
                </span>
              </div>
            </div>
            <RsIcon name="check-circle" :size="18" class="text-emerald-500 shrink-0" />
          </div>
        </div>

        <!-- Headline absolute numbers -->
        <div v-if="absoluteHighlights.length"
             class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="m in absoluteHighlights" :key="m.key"
               class="border border-rs-border rounded-[10px] p-4 bg-gradient-to-br from-white to-navy-900/[0.02]">
            <div class="flex items-center justify-between">
              <div class="text-[10px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ m.label }}</div>
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-[6px]"
                    :style="{ background: m.tint }">
                <RsIcon :name="m.icon" :size="12" :style="{ color: m.color }" />
              </span>
            </div>
            <div class="font-mono text-[20px] font-bold text-carbon mt-2">{{ m.value }}</div>
            <div class="font-sans text-[11px] text-steel-500 mt-1">{{ m.hint }}</div>
          </div>
        </div>

        <!-- Ratio bars (user's own ratios only) -->
        <div v-if="ratioBars.length">
          <div class="flex items-center justify-between gap-3 mb-3">
            <div class="font-sans text-[12px] font-semibold uppercase tracking-[1px] text-steel-500">
              {{ lang === 'uz' ? 'Молиявий коэффициентлар' : 'Финансовые коэффициенты' }}
            </div>
          </div>
          <div class="border border-rs-border rounded-[10px] divide-y divide-rs-border">
            <div v-for="r in ratioBars" :key="r.key" class="py-3 px-4">
              <div class="flex items-center justify-between mb-2">
                <div class="font-sans text-[13px] font-medium text-carbon">{{ r.label }}</div>
                <div class="flex items-center gap-3 font-mono text-[12px]">
                  <span class="font-bold text-carbon">{{ r.userLabel }}</span>
                </div>
              </div>
              <div class="relative h-[8px] bg-slate-100 rounded-full overflow-hidden">
                <div class="absolute inset-y-0 left-0 bg-emerald-500 rounded-full transition-all"
                     :style="{ width: r.userBar + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Insight -->
        <div v-if="excelInsight"
             class="rounded-[8px] py-4 px-5 flex gap-3 items-start"
             style="border-left: 3px solid #10B981; background: rgba(16,185,129,0.06);">
          <RsIcon name="sparkles" :size="16" class="text-emerald-600 mt-[2px] shrink-0" />
          <div>
            <div class="font-sans text-[13px] font-bold text-emerald-700 mb-1">
              {{ lang === 'uz' ? 'Хулоса' : 'Вывод по финансам' }}
            </div>
            <div class="font-sans text-[14px] font-medium text-carbon leading-[1.6]">{{ excelInsight }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ AI ANALYSIS (demo: local generator runs on mount; backend-powered if VITE_API_URL is set) ═══ -->
    <RsClaudeAnalysis v-if="analysis" :analysis="analysis" :lang="lang" />

    <div v-else-if="analysisStatus === 'analyzing'"
         class="bg-white border border-rs-border rounded-[12px] py-6 px-8 text-center text-[13px] text-steel-500 italic">
      {{ lang === 'uz' ? 'AI таҳлил қиляпти…' : 'AI анализирует…' }}
    </div>
    <div v-else-if="analysisStatus === 'error'"
         class="bg-red-50 border border-red-200 rounded-[12px] py-5 px-6 text-[13px] text-red-700">
      {{ lang === 'uz' ? 'Таҳлил хатоси:' : 'Ошибка анализа:' }} {{ store.analysisError }}
    </div>

    <!-- ═══ CITY CONTEXT — only for pilot cities (Fergana, Margilan) ═══ -->
    <section v-if="isPilotCity" class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div class="px-8 py-6 flex items-start justify-between gap-4"
           style="background: rgba(25,63,114,0.03); border-bottom: 1px solid rgba(25,63,114,0.08);">
        <div class="flex items-start gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-navy-900 shrink-0">
            <RsIcon name="landmark" :size="16" class="text-white" />
          </span>
          <div class="min-w-0">
            <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.cityContextTitle }}: {{ userPickedLabel }}</h2>
            <p class="font-sans text-[13px] text-gray-600 mt-1">{{ t.cityContextHint }}</p>
          </div>
        </div>
        <span v-if="!isCityDataReal"
              class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-amber-700 bg-amber-50 border border-amber-200 rounded-[6px] py-1 px-2 self-start"
              :title="lang === 'uz' ? 'Шаҳар бўйича батафсил маълумотлар тайёрланмоқда — қуйида вилоят бўйича' : 'Детальные данные по городу в разработке — ниже показаны областные'">
          {{ lang === 'uz' ? 'Данные по области' : 'Данные по области' }}
        </span>
      </div>
      <div class="px-8 py-7 grid grid-cols-2 md:grid-cols-4 gap-5">
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Аҳоли' : 'Население' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">
            {{ selectedCity.populationK.toLocaleString('ru-RU') }}
            <span class="text-[13px] font-medium text-steel-500">{{ lang === 'uz' ? 'минг' : 'тыс.' }}</span>
          </div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ lang === 'uz' ? 'шаҳар маркази' : 'жители города' }}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Саноат' : 'Промышленность' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">
            {{ Math.round(selectedCity.industryBlnUzs).toLocaleString('ru-RU') }}
            <span class="text-[13px] font-medium text-steel-500">{{ lang === 'uz' ? 'млрд сўм' : 'млрд сум' }}</span>
          </div>
          <div class="text-[11px] text-steel-500 mt-0.5">2024 · +104.3%</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">
            {{ selectedCity.id === 'margilan' ? (lang === 'uz' ? 'Экспорт' : 'Экспорт') : (lang === 'uz' ? 'Инвестиция' : 'Инвестиции') }}
          </div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">
            {{ (selectedCity.exportsBlnUzs ?? selectedCity.investmentsBlnUzs).toLocaleString('ru-RU') }}
            <span class="text-[13px] font-medium text-steel-500">{{ lang === 'uz' ? 'млрд' : 'млрд' }}</span>
          </div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ selectedCity.id === 'margilan' ? (lang === 'uz' ? '2023' : '2023') : (lang === 'uz' ? '2023 · +29.4%' : '2023 · +29.4%') }}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Маҳаллалар' : 'Махаллей' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">
            {{ selectedCity.mahallas.toLocaleString('ru-RU') }}
          </div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ lang === 'uz' ? 'ўзини ўзи бошқариш' : 'самоуправления' }}</div>
        </div>
      </div>

      <!-- Regional demographic + social context row -->
      <div class="px-8 pb-2 grid grid-cols-2 md:grid-cols-4 gap-5 border-t border-rs-border/50 pt-5">
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Туғилиш (вилоят)' : 'Рождаемость (область)' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">98 319</div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ lang === 'uz' ? '2025 · янги оилалар' : '2025 · новорождённые' }}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Никоҳлар (вилоят)' : 'Браки (область)' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">28 896</div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ lang === 'uz' ? '2025' : '2025' }}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Шаҳар улуши' : 'Городское население' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">56.7<span class="text-[13px] font-medium text-steel-500">%</span></div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ lang === 'uz' ? 'вилоят бўйича' : 'по области' }}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ lang === 'uz' ? 'Туман ва шаҳарлар' : 'Районов и городов' }}</div>
          <div class="font-mono text-[20px] font-bold text-carbon mt-1">15 + 4</div>
          <div class="text-[11px] text-steel-500 mt-0.5">{{ lang === 'uz' ? 'маъмурий бирликлар' : 'административных единиц' }}</div>
        </div>
      </div>

      <div class="px-8 pb-7 pt-5">
        <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 mb-2">
          {{ lang === 'uz' ? 'Тавсия этилган соҳалар' : 'Рекомендуемые отрасли' }}
        </div>
        <div class="flex flex-wrap gap-2">
          <span v-for="sec in selectedCity.topSectors || selectedCity.industries" :key="sec.key"
                class="inline-flex items-center gap-2 text-[13px] font-medium text-navy-900 bg-navy-900/[0.05] rounded-[8px] py-[6px] px-3">
            {{ lang === 'uz' ? sec.nameUz : sec.nameRu }}
            <span class="font-mono text-[12px] text-steel-500">{{ sec.blnUzs }} {{ lang === 'uz' ? 'млрд' : 'млрд' }}</span>
          </span>
        </div>

        <!-- Kindergarten-specific context block -->
        <div v-if="useFerganaKgOverride"
             class="mt-5 rounded-[10px] border border-emerald-200 bg-emerald-50/60 px-5 py-4">
          <div class="flex items-start gap-3">
            <span class="shrink-0 mt-[2px] inline-flex items-center justify-center w-7 h-7 rounded-full bg-emerald-500 text-white text-[12px] font-bold">ДОУ</span>
            <div class="min-w-0">
              <div class="text-[13px] font-bold text-emerald-800 mb-1">
                {{ lang === 'uz' ? 'Мактабгача таълим сегменти — шаҳар хусусиятлари' : 'Сегмент дошкольного образования — специфика города' }}
              </div>
              <ul class="space-y-[6px]">
                <li class="flex items-start gap-2 text-[13px] text-carbon leading-[1.55]">
                  <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[8px] shrink-0" />
                  {{ lang === 'uz'
                    ? 'Фарғона шаҳарда давлат боғчаларида ўринлар танқислиги; хусусий сегмент йиллик ~10–12% ўсмоқда.'
                    : 'В Фарғона шаҳар хронический дефицит мест в госсадах; частный сегмент растёт на ~10–12% в год.' }}
                </li>
                <li class="flex items-start gap-2 text-[13px] text-carbon leading-[1.55]">
                  <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[8px] shrink-0" />
                  {{ lang === 'uz'
                    ? 'Вилоят бўйича 2025 йил 98 319 туғилиш → келгуси 2–4 йилда ясли (2–3 ёш) талаби кескин ортади.'
                    : 'По области 98 319 рождений в 2025 → спрос на ясли (2–3 года) в ближайшие 2–4 года резко растёт.' }}
                </li>
                <li class="flex items-start gap-2 text-[13px] text-carbon leading-[1.55]">
                  <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[8px] shrink-0" />
                  {{ lang === 'uz'
                    ? 'Ўртача тўлов 600 000 – 1 200 000 сўм/ой; ўрта синф оилалар учун маҳалла ичидаги боғча устувор.'
                    : 'Средняя плата 600 000 – 1 200 000 сум/мес; для семей среднего класса приоритетен сад в своей маҳалле.' }}
                </li>
                <li class="flex items-start gap-2 text-[13px] text-carbon leading-[1.55]">
                  <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[8px] shrink-0" />
                  {{ lang === 'uz'
                    ? 'Давлат дастури «Илк қадам» — хусусий ДОУ учун имтиёз ва қисман молиялаштириш.'
                    : 'Госпрограмма «Илк қадам» — льготы и частичное софинансирование для частных ДОУ.' }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Non-pilot region: show honest 'no data yet' banner instead of city KPIs -->
    <section v-else class="bg-amber-50 border border-amber-200 rounded-[12px] overflow-hidden">
      <div class="px-8 py-6 flex items-start gap-4">
        <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-amber-500 shrink-0">
          <RsIcon name="alert-triangle" :size="16" class="text-white" />
        </span>
        <div class="min-w-0">
          <h2 class="font-sans text-[18px] font-bold text-amber-900">
            {{ lang === 'uz'
              ? 'Бу ҳудуд бўйича батафсил маълумотлар ҳозирча мавжуд эмас'
              : 'Детальные данные по этому региону пока недоступны' }}
          </h2>
          <p class="font-sans text-[13px] text-amber-800 mt-1 leading-[1.5]">
            {{ lang === 'uz'
              ? 'Пилот шаҳарлар: Фарғона ва Марғилон. AI таҳлили сизнинг профил ва молиявий маълумотларингиз асосида умумий тавсия беради.'
              : 'Пилотные города: Фергана и Маргилан. AI-анализ даст общую рекомендацию по вашему профилю и финансам без опоры на региональные показатели.' }}
          </p>
          <p v-if="userPickedLabel" class="font-sans text-[12px] text-amber-700 mt-2">
            {{ lang === 'uz' ? 'Сиз танлаган ҳудуд:' : 'Ваш выбор:' }}
            <span class="font-semibold">{{ userPickedLabel }}</span>
          </p>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 1 — AI Scoring ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(215,181,109,0.04); border-bottom: 1px solid rgba(215,181,109,0.12);"
      >
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">1</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section1Title }}</h2>
            <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section1Sub }}</p>
          </div>
        </div>
      </div>
      <div class="px-8 py-8">
        <div class="flex flex-col md:flex-row gap-8 md:gap-10">
          <!-- ScoreCircle (live) -->
          <div class="flex flex-col items-center gap-3 shrink-0">
            <div class="relative w-[140px] h-[140px]">
              <svg viewBox="0 0 120 120" class="w-full h-full -rotate-90">
                <circle cx="60" cy="60" :r="RADIUS" fill="none" stroke="#f3f4f6" stroke-width="10" />
                <circle
                  cx="60" cy="60" :r="RADIUS" fill="none"
                  :stroke="scoreColor" stroke-width="10" stroke-linecap="round"
                  :stroke-dasharray="CIRCUMFERENCE" :stroke-dashoffset="scoreOffset"
                  class="transition-all duration-1000"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="font-mono text-[36px] font-bold text-carbon leading-none">{{ scoreResult.total }}</span>
                <span class="font-sans text-[12px] font-medium text-steel-500">{{ t.outOf100 }}</span>
              </div>
            </div>
            <span :class="['font-sans text-[14px] font-semibold rounded-[6px] py-1 px-3', verdictLabel.cls]">
              {{ verdictLabel[lang] }}
            </span>
            <p class="text-[11px] text-steel-500 text-center max-w-[160px] leading-[1.4]">
              {{ lang === 'uz' ? 'Ҳар бир омилни очиб, қандай ҳисобланганини кўринг' : 'Раскройте любой фактор, чтобы увидеть как он посчитан' }}
            </p>
          </div>

          <!-- Live breakdown -->
          <div class="flex-1 min-w-0">
            <RsScoreBreakdown :factors="scoreResult.factors" :lang="lang" />
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 2 — SWOT ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(41,87,162,0.04); border-bottom: 1px solid rgba(41,87,162,0.1);"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">2</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section2Title }}</h2>
              <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section2Sub }}</p>
            </div>
          </div>
          <span class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 rounded-[6px] py-1 px-2"
                :title="t.demoBadgeHint">
            {{ t.demoBadge }}
          </span>
        </div>
      </div>
      <div class="px-8 py-8">
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="q in swotQuadrants" :key="q.title"
            :class="['rounded-[10px] border p-5', SWOT_STYLES[q.color].bg, SWOT_STYLES[q.color].border]"
          >
            <h4 :class="['font-sans text-[13px] font-bold uppercase tracking-[0.5px] mb-3', SWOT_STYLES[q.color].title]">
              {{ q.title }}
            </h4>
            <ul class="space-y-2">
              <li v-for="item in q.items" :key="item" class="flex items-start gap-2">
                <span :class="['w-[5px] h-[5px] rounded-full mt-[7px] shrink-0', SWOT_STYLES[q.color].dot]" />
                <span class="font-sans text-[13px] text-carbon leading-[1.5]">{{ item }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 3 — Geographic Heatmap (Margilan if matched, Fergana as default) ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(215,181,109,0.04); border-bottom: 1px solid rgba(215,181,109,0.12);"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-gold-500">3</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">
                {{ isMargilan
                  ? t.section3Title
                  : (lang === 'uz' ? 'Фарғона вилояти — имкониятлар харитаси' : 'Ферганская область — карта возможностей') }}
              </h2>
              <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">
                {{ isMargilan
                  ? t.section3Sub
                  : (lang === 'uz' ? 'Ҳар бир туман учун балл, аҳоли, рақобат ва вердикт' : 'По каждому району — балл, население, конкуренция и вердикт') }}
              </p>
            </div>
          </div>
          <span class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 rounded-[6px] py-1 px-2">
            {{ t.demoBadge }}
          </span>
        </div>
      </div>
      <div class="px-8 py-8 space-y-6">
        <RsMargilanHeatmap v-if="isMargilan" :ranking="t.MAHALLA_RANKING" />
        <RsFerganaHeatmap v-else :direction="finance.businessDirection" />

        <RsInsightBox v-if="isMargilan || useFerganaKgOverride" variant="info" :title="t.locationInsightTitle">
          {{ t.locationInsightText }}
        </RsInsightBox>
        <RsInsightBox v-else variant="info"
          :title="lang === 'uz' ? 'Ферғона вилояти учун тавсия' : 'Что это значит для вашего бизнеса в Фергане'"
        >
          {{ lang === 'uz'
            ? 'Фарғона шаҳри — вилоят маркази, 328 409 аҳоли, саноат маҳсулоти 8 587 млрд сўм (2024). Вилоят бўйича 2025 йилда 98 319 туғилиш, 28 896 никоҳ — истеъмол бозори барқарор ўсмоқда. Ўз бизнесингиз жойлашган туманни юқоридаги рейтингда кўринг.'
            : 'Фарғона шаҳар — столица области с 328 409 жителей и промышленной продукцией 8 587 млрд сум (2024). За 2025 год в области 98 319 рождений и 28 896 браков — потребительский рынок стабильно растёт. Найдите ваш район в рейтинге выше — он учитывает население, плотность бизнеса и конкуренцию.' }}
        </RsInsightBox>
      </div>
    </section>

    <!-- ═══ SECTION 5 — Business Plan ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(41,87,162,0.04); border-bottom: 1px solid rgba(41,87,162,0.1);"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">4</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section4Title }}</h2>
              <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section4Sub }}</p>
            </div>
          </div>
          <span class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 rounded-[6px] py-1 px-2"
                :title="t.demoBadgeHint">
            {{ t.demoBadge }}
          </span>
        </div>
      </div>
      <div class="px-8 py-8 space-y-8">
        <!-- Description -->
        <div
          class="rounded-[8px] py-4 px-5"
          style="border-left: 3px solid #D7B56D; background: rgba(215,181,109,0.06);"
        >
          <div class="font-sans text-[13px] font-bold mb-1 text-gold-500">{{ t.projectDescLabel }}</div>
          <div class="font-sans text-[14px] font-medium text-carbon leading-[1.6]">
            {{ t.projectDescText }}
          </div>
        </div>

        <!-- Courses -->
        <div>
          <div class="font-sans text-[11px] font-semibold uppercase tracking-[1px] text-steel-500 mb-3">{{ t.coursesLabel }}</div>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="c in t.courses" :key="c"
              class="font-sans text-[13px] font-medium text-navy-900 bg-navy-900/[0.06] rounded-[8px] py-[6px] px-3"
            >{{ c }}</span>
          </div>
        </div>

        <!-- Costs side by side -->
        <div class="grid grid-cols-2 gap-6">
          <div>
            <div class="font-sans text-[11px] font-semibold uppercase tracking-[1px] text-steel-500 mb-3">{{ t.startupCostsLabel }}</div>
            <div class="border border-rs-border rounded-[10px] overflow-hidden">
              <div class="divide-y divide-rs-border">
                <div v-for="row in t.STARTUP_COSTS" :key="row[0]" class="flex justify-between py-3 px-4">
                  <span class="font-sans text-[13px] text-carbon">{{ row[0] }}</span>
                  <span class="font-mono text-[13px] font-semibold text-carbon">{{ row[1] }}</span>
                </div>
                <div class="flex justify-between py-3 px-4 bg-navy-900/[0.03]">
                  <span class="font-sans text-[13px] font-bold text-carbon">{{ t.total }}</span>
                  <span class="font-mono text-[14px] font-bold text-navy-900">{{ t.startupTotal }}</span>
                </div>
              </div>
            </div>
          </div>
          <div>
            <div class="font-sans text-[11px] font-semibold uppercase tracking-[1px] text-steel-500 mb-3">{{ t.monthlyCostsLabel }}</div>
            <div class="border border-rs-border rounded-[10px] overflow-hidden">
              <div class="divide-y divide-rs-border">
                <div v-for="row in t.MONTHLY_COSTS" :key="row[0]" class="flex justify-between py-3 px-4">
                  <span class="font-sans text-[13px] text-carbon">{{ row[0] }}</span>
                  <span class="font-mono text-[13px] font-semibold text-carbon">{{ row[1] }}</span>
                </div>
                <div class="flex justify-between py-3 px-4 bg-navy-900/[0.03]">
                  <span class="font-sans text-[13px] font-bold text-carbon">{{ t.total }}</span>
                  <span class="font-mono text-[14px] font-bold text-navy-900">{{ t.monthlyTotal }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Revenue forecast -->
        <div>
          <div class="font-sans text-[11px] font-semibold uppercase tracking-[1px] text-steel-500 mb-3">{{ t.revenueForecastLabel }}</div>
          <div class="border border-rs-border rounded-[10px] overflow-hidden">
            <table class="w-full">
              <thead>
                <tr class="bg-navy-900/[0.03]">
                  <th class="text-left font-sans text-[12px] font-semibold text-steel-500 uppercase tracking-[0.5px] py-3 px-4">{{ t.periodCol }}</th>
                  <th class="text-center font-sans text-[12px] font-semibold text-steel-500 uppercase tracking-[0.5px] py-3 px-4">{{ t.studentsCol }}</th>
                  <th class="text-right font-sans text-[12px] font-semibold text-steel-500 uppercase tracking-[0.5px] py-3 px-4">{{ t.revenueCol }}</th>
                  <th class="text-right font-sans text-[12px] font-semibold text-steel-500 uppercase tracking-[0.5px] py-3 px-4">{{ t.profitCol }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-rs-border">
                <tr v-for="r in t.REVENUE_FORECAST" :key="r.period">
                  <td class="font-sans text-[13px] font-medium text-carbon py-3 px-4">{{ r.period }}</td>
                  <td class="font-mono text-[13px] font-semibold text-carbon py-3 px-4 text-center">{{ r.students }}</td>
                  <td class="font-mono text-[13px] font-semibold text-carbon py-3 px-4 text-right">{{ r.revenue }}</td>
                  <td
                    :class="[
                      'font-mono text-[13px] font-bold py-3 px-4 text-right',
                      r.profitPositive ? 'text-emerald-600' : 'text-red-500',
                    ]"
                  >
                    {{ r.profit }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="font-sans text-[12px] text-steel-500 mt-2 italic">{{ t.breakeven }}</p>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 5 — NBU Credit Products (climactic recommendation) ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(215,181,109,0.08); border-bottom: 1px solid rgba(215,181,109,0.2);"
      >
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-gold-500">5</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">
              {{ lang === 'uz' ? 'Сизга тавсия қилинган NBU маҳсулотлари' : 'Рекомендуемые продукты NBU для вас' }}
            </h2>
            <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">
              {{ lang === 'uz'
                ? 'Сиз киритган профил, молиявий ҳолат ва Excel маълумотлари асосида танланган'
                : 'Подобрано по вашему профилю, финансам и данным из загруженных Excel-файлов' }}
            </p>
          </div>
        </div>
      </div>
      <div class="px-8 py-8 space-y-6">
        <!-- Primary product — live match -->
        <div v-if="primaryMatch"
          class="border border-rs-border rounded-[10px] overflow-hidden"
          style="border-top: 3px solid #D7B56D;"
        >
          <div class="px-6 py-5 flex items-center justify-between">
            <div>
              <div class="font-sans text-[11px] font-semibold text-gold-500 uppercase tracking-[0.5px] mb-1">
                {{ primaryMatch.product.tier === 'easy' ? (lang === 'uz' ? 'Енгил маҳсулот' : 'Облегчённый продукт') : (lang === 'uz' ? 'Стандарт маҳсулот' : 'Стандартный продукт') }}
              </div>
              <h3 class="font-sans text-[20px] font-bold text-carbon">
                {{ primaryMatch.product.name[lang] }}
              </h3>
            </div>
            <span class="font-sans text-[12px] font-bold text-emerald-600 bg-emerald-50 rounded-[6px] py-[6px] px-[14px] uppercase tracking-[0.5px]">
              {{ t.recommendedBadge }}
            </span>
          </div>
          <div class="px-6 pb-6">
            <div class="divide-y divide-rs-border">
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.rateLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.rateLabel[lang] }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.amountLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.amountLabel[lang] }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.termLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.termLabel[lang] }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.collateralLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ formatProductCollateral(primaryMatch.product) }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.purposeLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.purposeLabel[lang] }}</div>
              </div>
              <div v-if="primaryMatch.reasons.length" class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.matchReasons }}</div>
                <ul class="space-y-1">
                  <li v-for="r in primaryMatch.reasons" :key="r" class="flex items-start gap-2">
                    <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[7px] shrink-0" />
                    <span class="font-sans text-[13px] text-carbon leading-[1.5]">{{ r }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional products -->
        <div v-if="altMatches.length">
          <div class="font-sans text-[12px] font-semibold uppercase tracking-[1px] text-steel-500 mb-4">
            {{ t.altProductsLabel }}
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div
              v-for="m in altMatches" :key="m.product.id"
              class="border border-rs-border rounded-[10px] py-[14px] px-[18px]"
            >
              <div class="font-sans text-[15px] font-semibold text-carbon">{{ m.product.name[lang] }}</div>
              <div class="font-sans text-[12px] font-normal text-gray-600 mt-[2px]">
                {{ m.product.tier === 'easy' ? (lang === 'uz' ? 'Енгил' : 'Облегчённый') : (lang === 'uz' ? 'Стандарт' : 'Стандартный') }}
              </div>
              <div class="mt-3 space-y-1">
                <div class="font-sans text-[12px] text-steel-500">
                  <span class="font-semibold">{{ t.rateLabel }}</span> {{ m.product.rateLabel[lang] }}
                </div>
                <div class="font-sans text-[12px] text-steel-500">
                  <span class="font-semibold">{{ t.amountLabel }}</span> {{ m.product.amountLabel[lang] }}
                </div>
                <div class="font-sans text-[12px] text-steel-500">
                  <span class="font-semibold">{{ t.termLabel }}</span> {{ m.product.termLabel[lang] }}
                </div>
              </div>
              <p class="font-sans text-[12px] font-normal text-gray-600 mt-2 leading-[1.4]">{{ m.product.purposeLabel[lang] }}</p>
            </div>
          </div>
        </div>

        <p class="font-sans text-[12px] text-steel-500 italic">{{ t.catalogNote }}</p>
      </div>
    </section>

    <!-- ═══ SECTION 6 — Action Plan ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(41,87,162,0.04); border-bottom: 1px solid rgba(41,87,162,0.1);"
      >
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">6</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section6Title }}</h2>
            <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section6Sub }}</p>
          </div>
        </div>
      </div>
      <div class="px-8 py-8">
        <div class="space-y-3">
          <div
            v-for="(s, i) in t.ACTION_STEPS" :key="s.title"
            class="flex items-start gap-4 border border-rs-border rounded-[10px] p-4"
          >
            <div class="flex flex-col items-center shrink-0">
              <span
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center font-mono text-[13px] font-bold text-white',
                  stepCircleClass(i, t.ACTION_STEPS.length),
                ]"
              >
                {{ i + 1 }}
              </span>
              <div v-if="i < t.ACTION_STEPS.length - 1" class="w-[2px] h-4 bg-rs-border mt-1" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3">
                <span class="font-sans text-[15px] font-semibold text-carbon">{{ s.title }}</span>
                <RsStatusTag :variant="s.status">{{ s.week }}</RsStatusTag>
              </div>
              <p class="font-sans text-[13px] text-gray-600 mt-1 leading-[1.5]">{{ s.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 7 — CTA ═══ -->
    <section
      class="rounded-[16px] py-14 px-10 text-center"
      style="background: linear-gradient(135deg, #0F2847, #193F72);"
    >
      <h2 class="font-sans text-[24px] font-bold text-white">{{ t.ctaTitle }}</h2>
      <p class="font-sans text-[15px] font-normal text-white/65 mt-2">{{ t.ctaSubtitle }}</p>
      <div class="flex items-center justify-center gap-4 mt-7">
        <a
          href="https://nbu.uz"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center justify-center font-sans text-[15px] font-bold text-navy-900 bg-gold-500 hover:bg-[#C9A85F] rounded-btn py-[14px] px-8 transition-colors duration-200"
        >
          {{ t.applyBtn }}
        </a>
        <button
          type="button"
          @click="onDownload"
          class="inline-flex items-center justify-center font-sans text-[15px] font-semibold text-white border-[1.5px] border-white/30 hover:bg-white/10 rounded-btn py-[13px] px-8 transition-colors duration-200"
        >
          {{ t.downloadBtn }}
        </button>
      </div>
      <button
        type="button"
        @click="emit('restart')"
        class="font-sans text-[14px] font-medium text-white/45 hover:text-white/70 mt-5 transition-colors duration-150"
      >
        {{ t.restartCta }}
      </button>
    </section>
  </div>
</template>

<style>
/* Unscoped so bumps cascade into child Vue components on this page. */
.rs-step5-root .text-\[10px\]  { font-size: 12px !important; }
.rs-step5-root .text-\[11px\]  { font-size: 13px !important; font-weight: 600; }
.rs-step5-root .text-\[12px\]  { font-size: 14px !important; font-weight: 500; }
.rs-step5-root .text-\[13px\]  { font-size: 15px !important; font-weight: 500; }
.rs-step5-root .text-\[14px\]  { font-size: 16px !important; }
.rs-step5-root .text-\[15px\]  { font-size: 17px !important; }
.rs-step5-root .text-\[16px\]  { font-size: 19px !important; }
.rs-step5-root .text-\[17px\]  { font-size: 20px !important; }
.rs-step5-root .text-\[18px\]  { font-size: 22px !important; }
.rs-step5-root .text-\[20px\]  { font-size: 24px !important; }
.rs-step5-root .text-\[22px\]  { font-size: 26px !important; }
.rs-step5-root .text-\[24px\]  { font-size: 28px !important; }
.rs-step5-root .text-\[28px\]  { font-size: 32px !important; }
.rs-step5-root .text-\[30px\]  { font-size: 34px !important; }
.rs-step5-root .text-\[34px\]  { font-size: 38px !important; }
.rs-step5-root .text-\[36px\]  { font-size: 42px !important; }
.rs-step5-root .text-\[42px\]  { font-size: 48px !important; }

/* Bump weights one step up so text reads bolder everywhere. */
.rs-step5-root .font-normal    { font-weight: 500 !important; }
.rs-step5-root .font-medium    { font-weight: 600 !important; }
.rs-step5-root .font-semibold  { font-weight: 700 !important; }
</style>
