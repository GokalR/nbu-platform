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

/**
 * Main entry point. Returns Claude-shape analysis object synchronously,
 * or via a Promise if the caller wants to simulate a delay.
 */
export function generateLocalAnalysis({ profile, finance, cityId, uploads = [], lang = 'ru' }) {
  const city = cityId ? CITIES[cityId] ?? null : null
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
