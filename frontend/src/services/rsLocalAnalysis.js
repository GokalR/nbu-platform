/**
 * Local (demo-mode) analysis generator for Regional Strategist.
 *
 * Produces the exact same JSON shape that the backend Claude call would
 * return — so the `<RsClaudeAnalysis>` component doesn't care whether the
 * analysis came from the API or from here.
 *
 * Inputs:
 *   - profile, finance — from the Pinia store
 *   - cityId          — 'fergana' | 'margilan' | null
 *   - uploads         — array of "uploaded" files ({kind, original_filename, ...})
 *   - lang            — 'ru' | 'uz'
 *
 * The generator is deterministic: same inputs → same output. No randomness.
 */

import benchmarks from '@/data/regionalStrategist/peer_benchmarks.json'
import { CITIES } from '@/data/regionalStrategist/cities'
import { computeScore } from '@/data/regionalStrategist/scoring'
import { matchCreditProducts, collateralLabel } from '@/data/regionalStrategist/credit-products'

const toNum = (v) => {
  const x = Number(String(v ?? '').replace(/[^\d.-]/g, ''))
  return Number.isFinite(x) ? x : 0
}
const isYes = (v) => /^(да|ҳа|yes|true|1)$/i.test(String(v ?? '').trim())

// Heuristic: guess the user's gross margin sector from businessDirection.
// Used only when the user uploaded Excel files — otherwise we leave the
// peerComparison table empty.
function guessSectorMargins(direction = '') {
  const d = direction.toLowerCase()
  if (/текстил|ткан|атлас|шёлк|тўқим|одежд|кийим/.test(d)) return { gross: 0.38, net: 0.10 }
  if (/пищев|еда|ресторан|кафе|food|озиқ/.test(d)) return { gross: 0.32, net: 0.08 }
  if (/услуг|сервис|салон|туризм|education|образован|таълим/.test(d)) return { gross: 0.52, net: 0.18 }
  if (/произв|продукц|ишлаб/.test(d)) return { gross: 0.30, net: 0.07 }
  if (/розниц|магазин|торгов|чакана|опт/.test(d)) return { gross: 0.34, net: 0.09 }
  return { gross: 0.38, net: 0.11 } // overall sample median
}

// Fake a minimal "user ratio sheet" from the reported monthly income/expenses.
// Produces only the ratios we can defend from the two numbers the user gave.
function deriveUserRatios(finance, direction) {
  const income = toNum(finance.monthlyIncome)
  const expenses = toNum(finance.monthlyExpenses)
  if (income <= 0) return null

  const revenue = income * 12
  const sector = guessSectorMargins(direction)

  const operatingMargin = income > 0 ? Math.max(-0.5, Math.min(0.6, (income - expenses) / income)) : 0
  // Net margin ≈ operating × (1 - tax stub 15% - assumed interest drag 3%).
  const netMargin = Math.max(-0.5, operatingMargin * 0.82)

  return {
    revenue,
    grossMargin: sector.gross,
    operatingMargin,
    netMargin,
  }
}

function cmpComment(user, median, lang, inverse = false) {
  if (user == null || median == null) return ''
  const diff = (user - median) / (Math.abs(median) || 1)
  const better = inverse ? diff < 0 : diff > 0
  const mag = Math.abs(diff)
  const much = mag > 0.25
  if (lang === 'uz') {
    if (mag < 0.05) return 'Медиана билан тенг'
    if (better) return much ? 'Медианадан анча юқори' : 'Медианадан юқори'
    return much ? 'Медианадан анча паст' : 'Медианадан паст'
  }
  if (mag < 0.05) return 'На уровне медианы'
  if (better) return much ? 'Заметно выше медианы' : 'Выше медианы отрасли'
  return much ? 'Заметно ниже медианы' : 'Ниже медианы отрасли'
}

function buildPeerComparison(userRatios, lang) {
  if (!userRatios) return []
  const b = benchmarks.benchmarks
  return [
    {
      metric: lang === 'uz' ? 'Ялпи маржа' : 'Валовая маржа',
      user: userRatios.grossMargin,
      peerMedian: b.grossMargin.median,
      comment: cmpComment(userRatios.grossMargin, b.grossMargin.median, lang),
    },
    {
      metric: lang === 'uz' ? 'Операцион маржа' : 'Операционная маржа',
      user: userRatios.operatingMargin,
      peerMedian: b.operatingMargin.median,
      comment: cmpComment(userRatios.operatingMargin, b.operatingMargin.median, lang),
    },
    {
      metric: lang === 'uz' ? 'Соф маржа' : 'Чистая маржа',
      user: userRatios.netMargin,
      peerMedian: b.netMargin.median,
      comment: cmpComment(userRatios.netMargin, b.netMargin.median, lang),
    },
  ]
}

function buildStrengthsFromFactors(factors, lang) {
  return [...factors]
    .sort((a, b) => b.value - a.value)
    .slice(0, 3)
    .filter((f) => f.value >= 60)
    .map((f) => {
      const pct = f.value
      if (lang === 'uz') return `${f.label.uz}: ${pct}/100 — мустаҳкам жиҳат`
      return `${f.label.ru}: ${pct}/100 — сильная сторона`
    })
}

function buildWeaknessesFromFactors(factors, lang) {
  return [...factors]
    .sort((a, b) => a.value - b.value)
    .slice(0, 3)
    .filter((f) => f.value < 60)
    .map((f) => {
      const pct = f.value
      if (lang === 'uz') return `${f.label.uz}: ${pct}/100 — ривожлантириш керак`
      return `${f.label.ru}: ${pct}/100 — требует укрепления`
    })
}

function buildCityFit(city, finance, lang) {
  if (!city) {
    return lang === 'uz'
      ? 'Шаҳар танланмаган — жойлашувга асосланган таҳлил мавжуд эмас.'
      : 'Город не выбран — анализ по локации недоступен.'
  }
  const direction = String(finance.businessDirection || '').toLowerCase()
  const sectors = city.recommendedSectors || []
  const match = sectors.some((s) => direction.includes(s) || s.includes(direction.slice(0, 4)))

  if (city.id === 'margilan') {
    const retail = /розниц|магазин|торгов|чакана/.test(direction)
    if (retail) {
      return lang === 'uz'
        ? `Марғилонда чакана 38,2% иқтисодиётни ташкил этади, ЯТТларнинг 43% эса тўхтатилган — бозор тўйинган. ${match ? 'Лекин йўналишингиз шаҳар тавсияларига мос.' : 'Нишани қайта кўриб чиқинг — экспортга йўналган тўқимачилик ёки туризм йўналишлари ўсмоқда.'}`
        : `В Маргилане розница — 38,2% экономики, но 43,1% ИП в приостановке: рынок перенасыщен. ${match ? 'При этом ваше направление совпадает с рекомендованными секторами города.' : 'Рассмотрите смежные ниши — экспортный текстиль/атлас (+202%) или туризм/услуги (+107%) растут заметно быстрее.'}`
    }
    return lang === 'uz'
      ? `Марғилон — туризм (йилига 380 минг меҳмон) ва экспорт (+202%) шаҳри. NBU 1,5 трлн сўм кредит режаси (×5,6) сизнинг йўналишингизни қўллаб-қувватлаши мумкин.`
      : `Маргилан — город туризма (380 тыс. гостей/год) и рекордного экспорта (+202%). Кредитный план NBU на 2026 — 1,5 трлн сум (×5,6 к 2025), что расширяет доступ к финансированию.`
  }

  if (city.id === 'fergana') {
    return lang === 'uz'
      ? `Фарғона вилояти — минтақанинг энг йирик саноат базаси (45,9 трлн сўм). Тўқимачилик ва кимё кластерлари устунлик қилади. ${match ? 'Йўналишингиз шаҳар кластерига мос.' : 'Йўналишингиз кластерларга тўғридан-тўғри мос келмайди — хизмат ёки ихтисослашув орқали ниша қидиринг.'}`
      : `Ферганская область — крупнейшая промышленная база региона (45,9 трлн сум), с лидирующими кластерами текстиля и химии. ${match ? 'Ваше направление совпадает с промышленной специализацией области.' : 'Ваше направление не входит в ключевые кластеры — ищите нишу через сервис или специализацию под существующие производства.'}`
  }
  return ''
}

function buildRecommendedProduct(finance, profile, lang) {
  const firstTime = !isYes(finance.hasRegisteredBusiness) || !isYes(profile.experienceLevel)
  const entityType = /ип|яккa|индивид/i.test(profile.entityType || '') ? 'IP' : 'LLC'
  const collKey = (() => {
    const c = String(finance.collateralType || '').toLowerCase()
    if (/недвиж|кўчмас/i.test(c)) return 'realEstate'
    if (/авто|транспорт/i.test(c)) return 'vehicle'
    if (/страх|суғурт/i.test(c)) return 'insurance'
    return null
  })()

  const purposeMap = {
    'Оборотные средства': 'working',
    'Основные средства': 'fixed',
    'Покупка автотранспорта': 'vehicle',
    'Покупка недвижимости': 'realEstate',
  }
  const purpose = purposeMap[finance.businessGoal] || 'any'

  const matches = matchCreditProducts({
    loanAmount: toNum(finance.loanAmount),
    collateral: collKey,
    purpose,
    entityType,
    firstTime,
    lang,
  })
  const best = matches[0]
  if (!best) return null

  const p = best.product
  const reason = best.reasons.length
    ? best.reasons.slice(0, 3).join(' · ')
    : (lang === 'uz'
        ? `Ставка ${p.rateLabel.uz}, муддат ${p.termLabel.uz}`
        : `Ставка ${p.rateLabel.ru}, срок ${p.termLabel.ru}`)

  return { name: p.name[lang], reason }
}

function buildNextSteps(profile, finance, city, lang) {
  const steps = []
  const push = (ru, uz) => steps.push(lang === 'uz' ? uz : ru)

  if (!isYes(finance.hasBusinessPlan)) {
    push(
      'Подготовьте базовый бизнес-план на 3 года: доходы, расходы, точка безубыточности.',
      '3 йиллик бизнес-режа тайёрланг: даромадлар, харажатлар, фойда нуқтаси.',
    )
  }
  if (!toNum(finance.monthlyIncome) || !toNum(finance.monthlyExpenses)) {
    push(
      'Зафиксируйте среднемесячные доходы и расходы — без этих цифр банк не рассмотрит заявку.',
      'Ўртача ойлик даромад ва харажатни қайд этинг — бусиз ариза кўрилмайди.',
    )
  }
  if (!isYes(finance.hasCollateral) && toNum(finance.loanAmount) > 300_000_000) {
    push(
      'Под сумму выше 300 млн нужен залог. Оцените недвижимость или транспорт заранее.',
      '300 млн дан юқори сумма учун гаров керак. Кўчмас мулк ёки транспортни олдиндан баҳоланг.',
    )
  }
  if (!isYes(profile.hasTraining) && !isYes(profile.hasMentor)) {
    push(
      'Пройдите профильное обучение или найдите ментора — это усилит скоринг банка.',
      'Касбий ўқитиш ёки ментор топинг — банк скорингини кучайтиради.',
    )
  }
  if (city?.id === 'margilan' && /розниц|магазин|торгов|чакана/.test((finance.businessDirection || '').toLowerCase())) {
    push(
      'Рассмотрите пивот в экспортный текстиль или туризм — розница в Маргилане перенасыщена.',
      'Экспорт тўқимачилиги ёки туризмга ўтишни кўриб чиқинг — Марғилонда чакана тўйинган.',
    )
  }
  push(
    'Подайте заявку через ближайшее отделение NBU или онлайн-форму с пакетом документов.',
    'Энг яқин NBU бўлимига ёки онлайн-шаклга ҳужжатлар билан ариза топширинг.',
  )
  return steps.slice(0, 5)
}

function buildRisks(profile, finance, city, lang) {
  const risks = []
  const push = (ru, uz) => risks.push(lang === 'uz' ? uz : ru)

  const income = toNum(finance.monthlyIncome)
  const expenses = toNum(finance.monthlyExpenses)
  const debt = toNum(finance.existingDebt)
  const loan = toNum(finance.loanAmount)

  if (income > 0 && expenses > 0 && (income - expenses) / income < 0.1) {
    push(
      'Узкая маржа (<10%) — любой всплеск расходов сделает кредит неподъёмным.',
      'Маржа тор (<10%) — ҳар қандай харажат ўсиши кредитни оғирлаштиради.',
    )
  }
  if (debt > 0 && income > 0 && debt / (income * 12) > 0.3) {
    push(
      'Высокая долговая нагрузка — перед новым кредитом закройте или реструктурируйте текущий.',
      'Қарз юки юқори — янги кредитдан олдин мавжудини ёпинг ёки реструктуризация қилинг.',
    )
  }
  if (!isYes(finance.hasCollateral) && loan > 500_000_000) {
    push(
      'Сумма >500 млн без залога — высокий риск отказа по любым стандартным продуктам.',
      'Гаровсиз 500 млн дан юқори сумма — стандарт маҳсулотларда рад этиш хавфи катта.',
    )
  }
  if (!isYes(finance.hasBusinessPlan)) {
    push(
      'Отсутствие бизнес-плана — ключевой фактор отказа для впервые обращающихся.',
      'Бизнес-режа йўқлиги — биринчи марта мурожаат қилувчилар учун рад сабаби.',
    )
  }
  if (city?.id === 'margilan' && city.nplPct > 3) {
    push(
      `NPL в Маргилане ${city.nplPct}% — банк будет строже оценивать risk-профиль.`,
      `Марғилонда NPL ${city.nplPct}% — банк риск-профилни жиддий баҳолайди.`,
    )
  }
  if (!risks.length) {
    push(
      'Явных финансовых рисков не выявлено — следите за кассовым разрывом после получения кредита.',
      'Очиқ молиявий хатарлар кузатилмади — кредитдан сўнг касса тақсимотини назорат қилинг.',
    )
  }
  return risks.slice(0, 5)
}

function buildSummary(score, city, finance, userRatios, lang) {
  const verdictPhrase = (() => {
    if (lang === 'uz') {
      if (score.verdict === 'good') return 'лойиҳангизни амалга ошириш учун яхши потенциал'
      if (score.verdict === 'fair') return 'ўрта потенциал — айрим жиҳатларни кучайтириш керак'
      return 'ҳозирча заиф — юкланган молиявий ва бозор позициясига эътибор беринг'
    }
    if (score.verdict === 'good') return 'хороший потенциал для реализации проекта'
    if (score.verdict === 'fair') return 'средний потенциал — несколько направлений требуют укрепления'
    return 'слабый потенциал на текущем этапе — ключевые блоки финансов и рынка ещё не собраны'
  })()

  const cityName = city ? (lang === 'uz' ? city.name.uz : city.name.ru) : (lang === 'uz' ? 'танланган ҳудуд' : 'выбранной локации')
  const direction = finance.businessDirection || (lang === 'uz' ? 'танланган йўналиш' : 'выбранное направление')

  const marginNote = userRatios
    ? (lang === 'uz'
        ? ` Юкланган ҳисоботлар бўйича операцион маржа ${Math.round(userRatios.operatingMargin * 100)}%.`
        : ` По загруженным отчётам операционная маржа ${Math.round(userRatios.operatingMargin * 100)}%.`)
    : ''

  return lang === 'uz'
    ? `${cityName}да «${direction}» йўналиши учун — ${verdictPhrase}. Умумий скор ${score.total}/100.${marginNote}`
    : `По «${direction}» в ${cityName} — ${verdictPhrase}. Общий скор ${score.total}/100.${marginNote}`
}

// ── Detailed hardcoded analysis for the ERKIN PARVOZ demo ──────────────────
// When the user runs the demo, we return a rich Claude-quality analysis
// instead of generic rule-based text. This is detected by matching the
// profile name and business direction.
function isDemoSeed(profile, finance) {
  const name = (profile.name || '').toUpperCase()
  const dir = (finance.businessDirection || '').toLowerCase()
  return name.includes('SMART EDUCATION') && (/учебн|oʻquv|markaz|центр/.test(dir))
}

const DEMO_ANALYSIS = {
  ru: {
    verdict: 'good',
    summary: 'SMART EDUCATION MCHJ — действующий IT-учебный центр в Маргилане с 3–5 летней историей, 6 преподавателями и ~80 студентами. Ежемесячный доход 50–100 млн сум при расходах 30–50 млн — операционная маржа около 47%, что значительно выше медианы сектора образовательных услуг (15%). Залог в виде жилой недвижимости покрывает запрашиваемые 200–500 млн. Общий скор 78/100 — хороший потенциал для расширения второго филиала.',
    strengths: [
      'Стабильная операционная маржа ~47% — значительно выше медианы сектора образовательных услуг (15%). Бизнес генерирует 20–50 млн чистой прибыли ежемесячно.',
      'ООО с 3–5 летней кредитной историей, нулевая долговая нагрузка — банк оценит финансовую дисциплину. Отсутствие действующих кредитов упрощает одобрение.',
      'Профильное IT-образование + 3–5 лет предпринимательского опыта в сфере — ключевой фактор для банковского скоринга. Учредитель понимает рынок и операционную модель.',
      'Рынок IT-образования в Ферганской области растёт: 45 896 млрд сум промышленного выпуска (+104.3%) создаёт спрос на квалифицированные IT-кадры для предприятий.',
    ],
    weaknesses: [
      'Зависимость от одного филиала в Маргилане — при открытии второго в Бахрине операционные риски удвоятся. Рекомендуется phased expansion с контролем unit-экономики.',
      'Отсутствие ментора — при масштабировании с 80 до 150+ студентов потребуется управленческая экспертиза. Рассмотрите программу менторства NBU или UNDP.',
      'Бизнес-план в черновике — для получения кредита 200–500 млн необходим полный план с прогнозами P&L на 3 года, расчётом точки безубыточности и планом набора.',
    ],
    peerComparison: [
      { metric: 'Валовая маржа', user: 0.52, peerMedian: 0.52, comment: 'На уровне медианы сектора образования — здоровый показатель' },
      { metric: 'Операционная маржа', user: 0.47, peerMedian: 0.15, comment: 'Заметно выше медианы — высокая эффективность операций' },
      { metric: 'Чистая маржа', user: 0.39, peerMedian: 0.15, comment: 'Заметно выше медианы — бизнес генерирует стабильную прибыль' },
    ],
    cityFit: 'Маргилан — город с населением 235 тыс. человек в составе Ферганской области (4,2 млн). Город известен как центр туризма (380 тыс. гостей/год) и текстильного экспорта (+202%). IT-образование создаёт кадровый ресурс для обоих направлений. Район Бахрин перспективен для второго филиала: жилая застройка, близость к центру, нет конкурирующих IT-курсов в радиусе 2 км. Кредитный план NBU на 2026 — 1,5 трлн сум (×5,6 к 2025), расширяющий доступ к финансированию.',
    recommendedProduct: null,
    nextSteps: [
      'Доработайте бизнес-план: добавьте P&L-прогноз на 3 года для второго филиала, план набора 80 студентов за 6 месяцев, расчёт себестоимости одного студенто-месяца.',
      'Подготовьте оценку залога: закажте независимую оценку жилой недвижимости (дом/квартира). Для суммы 200–500 млн залоговая стоимость должна покрывать 120–150% от суммы кредита.',
      'Подберите помещение в Бахрине: площадь от 150 м², близость к транспорту и жилым кварталам. Предварительный договор аренды усилит заявку.',
      'Подайте заявку через отделение NBU Маргилан на продукт «Бизнес прогресс» или «Развивайся» — ставка от 23%, срок до 48 месяцев, покрытие залогом недвижимости.',
      'После одобрения: запустите маркетинговую кампанию — день открытых дверей, партнёрство с местными школами, продвижение через Telegram-каналы Маргилана.',
    ],
    risks: [
      'Конкуренция: в Маргилане и Фергане появляются новые IT-курсы. Дифференциация через AI/ML и кибербезопасность — ваше конкурентное преимущество, но требуется постоянное обновление программ.',
      'Кадровый риск: найти 3–4 квалифицированных преподавателя AI/ML в Маргилане сложно. Рассмотрите удалённых преподавателей из Ташкента или онлайн-формат для спецкурсов.',
      'Ликвидность при расширении: первые 3–6 месяцев второй филиал будет убыточным (набор студентов). Убедитесь, что первый филиал генерирует достаточно кэша для покрытия кредитных платежей (~15–25 млн/мес).',
    ],
  },
  uz: {
    verdict: 'good',
    summary: 'SMART EDUCATION MCHJ — Margʻilondagi 3–5 yillik tarixga ega IT oʻquv markazi, 6 oʻqituvchi va ~80 talaba. Oylik daromad 50–100 mln soʻm, xarajat 30–50 mln — operatsion marja ~47%, taʻlim xizmatlari medianasidan (15%) ancha yuqori. Uy-joy garovi soʻralgan 200–500 mln ni qoplaydi. Umumiy skor 78/100 — ikkinchi filialni kengaytirish uchun yaxshi potentsial.',
    strengths: [
      'Barqaror operatsion marja ~47% — taʻlim xizmatlari medianasidan (15%) sezilarli darajada yuqori. Biznes oyiga 20–50 mln sof foyda ishlab chiqaradi.',
      'MChJ 3–5 yillik kredit tarixiga ega, nol qarz yuki — bank moliyaviy intizomni yuqori baholaydi. Joriy kreditlar yoʻqligi tasdiqlashni osonlashtiradi.',
      'IT boʻyicha oliy maʻlumot + 3–5 yillik tadbirkorlik tajribasi — bank skoringi uchun hal qiluvchi omil. Taʻsischi bozor va operatsion modelni tushunadi.',
      'Fargʻona viloyatida IT taʻlim bozori oʻsmoqda: 45 896 mlrd soʻm sanoat ishlab chiqarishi (+104,3%) korxonalar uchun malakali IT kadrlar talabini yaratmoqda.',
    ],
    weaknesses: [
      'Margʻilondagi bitta filialga bogʻliqlik — Bahrin tumanida ikkinchisini ochganda operatsion xatarlar ikki baravar oshadi. Bosqichma-bosqich kengaytirish va unit-iqtisodiyotni nazorat qilish tavsiya etiladi.',
      'Mentor yoʻq — 80 dan 150+ talabaga koʻpaytirganda boshqaruv tajribasi zarur boʻladi. NBU yoki UNDP mentorlik dasturini koʻrib chiqing.',
      'Biznes-reja qoralama holatda — 200–500 mln kredit olish uchun 3 yillik P&L prognozi, zararsizlik nuqtasi va talabalar yigʻish rejasi bilan toʻliq reja kerak.',
    ],
    peerComparison: [
      { metric: 'Yalpi marja', user: 0.52, peerMedian: 0.52, comment: 'Taʻlim sektori medianasi darajasida — sogʻlom koʻrsatkich' },
      { metric: 'Operatsion marja', user: 0.47, peerMedian: 0.15, comment: 'Medianadan ancha yuqori — yuqori operatsion samaradorlik' },
      { metric: 'Sof marja', user: 0.39, peerMedian: 0.15, comment: 'Medianadan ancha yuqori — biznes barqaror foyda ishlab chiqarmoqda' },
    ],
    cityFit: 'Margʻilon — Fargʻona viloyati (4,2 mln aholi) tarkibidagi 235 ming aholiga ega shahar. Shahar turizm (yiliga 380 ming mehmon) va toʻqimachilik eksporti (+202%) markazi. IT taʻlim ikkala yoʻnalish uchun kadrlar zaxirasini yaratadi. Bahrin tumani ikkinchi filial uchun istiqbolli: turar-joy qurilishi, markazga yaqinlik, 2 km radiusda raqobatchi IT kurslar yoʻq. NBU ning 2026 yilgi kredit rejasi — 1,5 trln soʻm (2025 yilga nisbatan ×5,6), moliyalashtirish imkoniyatlarini kengaytiradi.',
    recommendedProduct: null,
    nextSteps: [
      'Biznes-rejani yakunlang: ikkinchi filial uchun 3 yillik P&L prognozi, 6 oy ichida 80 talaba yigʻish rejasi, bir talaba-oy tannarxi hisobi.',
      'Garov baholashni tayyorlang: uy-joy (uy/kvartira) uchun mustaqil baho buyurtma bering. 200–500 mln summa uchun garov qiymati kredit summasining 120–150% ni qoplashi kerak.',
      'Bahrin tumanida joy tanlang: 150 m² dan, transportga va turar-joy mavzeleriga yaqin. Dastlabki ijara shartnomasi arizani kuchaytiradi.',
      'NBU Margʻilon boʻlimiga «Biznes progress» yoki «Razvivaysya» mahsulotiga ariza bering — stavka 23% dan, muddat 48 oygacha, koʻchmas mulk garovi bilan.',
      'Tasdiqlangandan soʻng: marketing kampaniyasi boshlang — ochiq kunlar, mahalliy maktablar bilan hamkorlik, Margʻilon Telegram kanallari orqali targ\'ib.',
    ],
    risks: [
      'Raqobat: Margʻilon va Fargʻonada yangi IT kurslar paydo boʻlmoqda. AI/ML va kiber xavfsizlik orqali farqlanish — sizning raqobat ustunligingiz, lekin dasturlarni doimiy yangilash zarur.',
      'Kadr xatari: Margʻilonda 3–4 malakali AI/ML oʻqituvchi topish qiyin. Toshkentdan masofaviy oʻqituvchilar yoki maxsus kurslar uchun onlayn formatni koʻrib chiqing.',
      'Kengayishda likvidlik: ikkinchi filial birinchi 3–6 oyda zarar koʻradi (talabalar yigʻish). Birinchi filial kredit toʻlovlarini (~15–25 mln/oy) qoplash uchun yetarli naqd pul ishlab chiqarishiga ishonch hosil qiling.',
    ],
  },
}

/**
 * Main entry point. Returns Claude-shape analysis object synchronously,
 * or via a Promise if the caller wants to simulate a delay.
 */
export function generateLocalAnalysis({ profile, finance, cityId, uploads = [], lang = 'ru' }) {
  const city = cityId ? CITIES[cityId] ?? null : null

  // Return detailed hardcoded analysis for the demo seed
  if (isDemoSeed(profile, finance)) {
    const demo = DEMO_ANALYSIS[lang] || DEMO_ANALYSIS.ru
    return {
      output: { ...demo },
      model: 'local-demo-v1',
      input_tokens: 0,
      output_tokens: 0,
      source: 'demo',
    }
  }

  const extracted = (() => {
    for (const u of [...uploads].reverse()) {
      const c = u?.parsed?.computed
      if (c && (c.ratios || c.absolutes)) return { ratios: c.ratios || {}, absolutes: c.absolutes || {} }
    }
    return null
  })()
  const score = computeScore(profile, finance, cityId, extracted)
  const hasUploads = uploads.length > 0
  const userRatios = hasUploads ? deriveUserRatios(finance, finance.businessDirection) : null

  const output = {
    verdict: score.verdict,
    summary: buildSummary(score, city, finance, userRatios, lang),
    strengths: buildStrengthsFromFactors(score.factors, lang),
    weaknesses: buildWeaknessesFromFactors(score.factors, lang),
    peerComparison: buildPeerComparison(userRatios, lang),
    cityFit: buildCityFit(city, finance, lang),
    // Credit product recommendation is handled exclusively by Section 5
    // (matchCreditProducts in RsStep5Results) to avoid showing two conflicting
    // product cards.  Setting to null hides the card in RsClaudeAnalysis.
    recommendedProduct: null,
    nextSteps: buildNextSteps(profile, finance, city, lang),
    risks: buildRisks(profile, finance, city, lang),
  }

  return {
    output,
    model: 'local-rules-v1',
    input_tokens: 0,
    output_tokens: 0,
    source: hasUploads ? 'local+uploads' : 'local',
  }
}

export async function generateLocalAnalysisAsync(opts, simulatedDelayMs = 1200) {
  await new Promise((r) => setTimeout(r, simulatedDelayMs))
  return generateLocalAnalysis(opts)
}
