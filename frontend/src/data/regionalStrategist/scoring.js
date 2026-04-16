// Прозрачная скоринговая модель для Regional Strategist.
// Чистая функция — вход (profile, finance, city), выход:
//   {
//     total: 0..100,
//     verdict: 'good' | 'fair' | 'weak',
//     factors: [{ key, label{ru,uz}, value 0..100, weight 0..1,
//                 contribution: value*weight, inputs: [{label, value, impact}], hint }]
//   }
//
// Цель: пользователь может открыть любой фактор и увидеть, какие его ответы
// повлияли и как. Никакой магии.

import { CITIES } from './cities'

// Sector-specific peer medians for financial ratios. Education services
// (kindergartens, courses) sit at higher margins than manufacturing/retail;
// scoring against the wrong bucket produces misleading "above/below median"
// claims (e.g. a kindergarten's 12% net margin is healthy vs generic 8%
// cross-sector median, but mid-pack vs the education bucket's 14%).
export function guessSectorBucket(direction = '') {
  const d = String(direction).toLowerCase()
  if (/детск|богча|боғча|kindergarten|дошколь|мактабгача/.test(d)) return 'kindergarten'
  if (/текстил|ткан|атлас|шёлк|тўқим|одежд|кийим/.test(d)) return 'textile'
  if (/пищев|еда|ресторан|кафе|food|озиқ/.test(d)) return 'food'
  if (/услуг|сервис|салон|туризм|education|образован|таълим|учебн|ўқув/.test(d)) return 'services'
  if (/произв|продукц|ишлаб/.test(d)) return 'manufacturing'
  if (/розниц|магазин|торгов|чакана|опт/.test(d)) return 'retail'
  return 'general'
}

const SECTOR_MEDIANS = {
  //              grossMargin netMargin  roa    roe   currentRatio debtToEquity
  kindergarten:  { grossMargin: 0.45, netMargin: 0.14, roa: 0.06, roe: 0.16, currentRatio: 1.5, debtToEquity: 1.4 },
  services:      { grossMargin: 0.52, netMargin: 0.15, roa: 0.08, roe: 0.18, currentRatio: 1.6, debtToEquity: 1.2 },
  textile:       { grossMargin: 0.38, netMargin: 0.10, roa: 0.07, roe: 0.14, currentRatio: 1.5, debtToEquity: 1.5 },
  food:          { grossMargin: 0.32, netMargin: 0.08, roa: 0.06, roe: 0.13, currentRatio: 1.4, debtToEquity: 1.6 },
  manufacturing: { grossMargin: 0.30, netMargin: 0.07, roa: 0.06, roe: 0.13, currentRatio: 1.5, debtToEquity: 1.7 },
  retail:        { grossMargin: 0.34, netMargin: 0.09, roa: 0.08, roe: 0.16, currentRatio: 1.3, debtToEquity: 1.8 },
  general:       { grossMargin: 0.38, netMargin: 0.11, roa: 0.07, roe: 0.15, currentRatio: 1.6, debtToEquity: 1.2 },
}

export function peerMediansFor(direction) {
  return SECTOR_MEDIANS[guessSectorBucket(direction)] || SECTOR_MEDIANS.general
}

// ── helpers ────────────────────────────────────────────────────────────────
const n = (v) => {
  const x = Number(String(v ?? '').replace(/[^\d.-]/g, ''))
  return Number.isFinite(x) ? x : 0
}
const has = (v) => {
  if (v === undefined || v === null) return false
  const s = String(v).trim().toLowerCase()
  return s && !['', 'нет', 'йўқ', 'no', '0', 'false', '—'].includes(s)
}
const isYes = (v) => /^(да|ҳа|yes|true|1)$/i.test(String(v ?? '').trim())

// Возвращает «мягкий» процент прироста от 0 до max при value в [0, cap].
const ramp = (value, cap, max) => Math.min(max, (Math.max(0, value) / cap) * max)

// ── фактор: опыт предпринимателя ───────────────────────────────────────────
function factorExperience(profile) {
  const inputs = []
  let v = 30 // базовая планка

  const exp = String(profile.experienceLevel || '').toLowerCase()
  if (/10\+|более 10/.test(exp)) { v += 35; inputs.push({ label: 'experienceLevel', value: profile.experienceLevel, impact: +35 }) }
  else if (/5–10|5-10|5 до 10/.test(exp)) { v += 25; inputs.push({ label: 'experienceLevel', value: profile.experienceLevel, impact: +25 }) }
  else if (/3–5|3-5|3 до 5/.test(exp)) { v += 18; inputs.push({ label: 'experienceLevel', value: profile.experienceLevel, impact: +18 }) }
  else if (/1–3|1-3|1 до 3/.test(exp)) { v += 10; inputs.push({ label: 'experienceLevel', value: profile.experienceLevel, impact: +10 }) }
  else if (has(exp)) { v += 3; inputs.push({ label: 'experienceLevel', value: profile.experienceLevel, impact: +3 }) }
  else { inputs.push({ label: 'experienceLevel', value: '—', impact: 0 }) }

  if (isYes(profile.domainExperience)) { v += 15; inputs.push({ label: 'domainExperience', value: profile.domainExperience, impact: +15 }) }
  else if (has(profile.domainExperience)) inputs.push({ label: 'domainExperience', value: profile.domainExperience, impact: 0 })

  if (isYes(profile.hasHigherEducation)) { v += 8; inputs.push({ label: 'hasHigherEducation', value: profile.hasHigherEducation, impact: +8 }) }
  if (has(profile.educationField)) { v += 4; inputs.push({ label: 'educationField', value: profile.educationField, impact: +4 }) }
  if (isYes(profile.hasTraining)) { v += 5; inputs.push({ label: 'hasTraining', value: profile.hasTraining, impact: +5 }) }
  if (isYes(profile.hasMentor)) { v += 5; inputs.push({ label: 'hasMentor', value: profile.hasMentor, impact: +5 }) }

  return {
    key: 'experience',
    label: { ru: 'Opit predprinimatelya', uz: 'Tadbirkor tajribasi' },
    value: Math.max(0, Math.min(100, Math.round(v))),
    inputs,
    hint: {
      ru: 'Учитываем стаж, опыт в отрасли, образование, обучение и наличие ментора.',
      uz: 'Tajriba, sohadagi ish, ta'lim, o'qitish va mentor mavjudligini hisobga olamiz.',
    },
  }
}

// ── фактор: финансовая устойчивость ────────────────────────────────────────
// When Excel-derived ratios are available (`financials`), we prefer them over
// the self-reported monthlyIncome/monthlyExpenses bands: Excel is ground truth.
function factorFinance(finance, financials = null) {
  const inputs = []
  let v = 30

  // ─ Excel-first path: score off real ratios (net margin, current ratio, D/E, ROE).
  if (financials && financials.ratios) {
    const r = financials.ratios
    const a = financials.absolutes || {}

    if (r.netMargin != null) {
      // 0% → 0 bonus, 15% → +25 bonus (capped)
      const bonus = Math.round(ramp(r.netMargin, 0.15, 25))
      v += bonus
      inputs.push({ label: 'netMargin (Excel)', value: `${(r.netMargin * 100).toFixed(1)}%`, impact: +bonus })
    }
    if (r.currentRatio != null) {
      if (r.currentRatio >= 1.5) { v += 15; inputs.push({ label: 'currentRatio (Excel)', value: r.currentRatio.toFixed(2), impact: +15 }) }
      else if (r.currentRatio >= 1.0) { v += 8; inputs.push({ label: 'currentRatio (Excel)', value: r.currentRatio.toFixed(2), impact: +8 }) }
      else { v -= 10; inputs.push({ label: 'currentRatio (Excel)', value: `${r.currentRatio.toFixed(2)} — низкая ликвидность`, impact: -10 }) }
    }
    if (r.debtToEquity != null) {
      if (r.debtToEquity <= 1) { v += 10; inputs.push({ label: 'debtToEquity (Excel)', value: r.debtToEquity.toFixed(2), impact: +10 }) }
      else if (r.debtToEquity <= 2) { v += 3; inputs.push({ label: 'debtToEquity (Excel)', value: r.debtToEquity.toFixed(2), impact: +3 }) }
      else { v -= 12; inputs.push({ label: 'debtToEquity (Excel)', value: `${r.debtToEquity.toFixed(2)} — высокая нагрузка`, impact: -12 }) }
    }
    if (r.roe != null) {
      const bonus = Math.round(ramp(r.roe, 0.25, 12))
      v += bonus
      inputs.push({ label: 'ROE (Excel)', value: `${(r.roe * 100).toFixed(1)}%`, impact: +bonus })
    }
    if (isYes(finance.hasCollateral)) {
      v += 8
      inputs.push({ label: 'hasCollateral', value: finance.collateralType || 'да', impact: +8 })
    }
    if (a.revenue != null) {
      inputs.push({ label: 'revenue (Excel)', value: `${(a.revenue / 1_000_000_000).toFixed(2)} млрд сум`, impact: 0 })
    }
    return {
      key: 'finance',
      label: { ru: 'Finansovaya ustoychivost', uz: 'Moliyaviy barqarorlik' },
      value: Math.max(0, Math.min(100, Math.round(v))),
      inputs,
      hint: {
        ru: 'По данным Excel: чистая маржа, текущая ликвидность, D/E, ROE и наличие залога.',
        uz: 'Excel bo'yicha: sof marja, joriy likvidlik, D/E, ROE va garov mavjudligi.',
      },
    }
  }

  // ─ Legacy path: self-reported Step 2 bands.

  const income = n(finance.monthlyIncome)
  const expenses = n(finance.monthlyExpenses)
  const debt = n(finance.existingDebt)
  const loan = n(finance.loanAmount)
  const ownFunds = n(finance.hasOwnFunds)

  if (income > 0 && expenses >= 0) {
    const margin = income - expenses
    if (margin > 0) {
      const pct = margin / income
      const bonus = Math.round(ramp(pct, 0.5, 25))
      v += bonus
      inputs.push({ label: 'monthlyIncome − monthlyExpenses', value: `${margin.toLocaleString('ru-RU')} сум/мес (маржа ${Math.round(pct * 100)}%)`, impact: +bonus })
    } else {
      v -= 15
      inputs.push({ label: 'monthlyIncome − monthlyExpenses', value: `${margin.toLocaleString('ru-RU')} сум/мес (убыток)`, impact: -15 })
    }
  } else {
    inputs.push({ label: 'monthlyIncome / monthlyExpenses', value: '—', impact: 0 })
  }

  if (ownFunds > 0 && loan > 0) {
    const share = ownFunds / (ownFunds + loan)
    const bonus = Math.round(ramp(share, 0.5, 20))
    v += bonus
    inputs.push({ label: 'hasOwnFunds ÷ (own + loan)', value: `${Math.round(share * 100)}% собственных средств`, impact: +bonus })
  } else if (ownFunds > 0) {
    v += 10
    inputs.push({ label: 'hasOwnFunds', value: ownFunds.toLocaleString('ru-RU'), impact: +10 })
  } else {
    inputs.push({ label: 'hasOwnFunds', value: '—', impact: 0 })
  }

  if (isYes(finance.hasCollateral)) {
    v += 10
    inputs.push({ label: 'hasCollateral', value: finance.collateralType || 'да', impact: +10 })
  } else {
    inputs.push({ label: 'hasCollateral', value: 'нет', impact: 0 })
  }

  if (debt > 0 && income > 0) {
    const ratio = debt / (income * 12)
    if (ratio > 0.4) {
      v -= 15
      inputs.push({ label: 'existingDebt ÷ годовой доход', value: `${Math.round(ratio * 100)}% — высокая нагрузка`, impact: -15 })
    } else if (ratio > 0.2) {
      v -= 5
      inputs.push({ label: 'existingDebt ÷ годовой доход', value: `${Math.round(ratio * 100)}%`, impact: -5 })
    }
  }

  return {
    key: 'finance',
    label: { ru: 'Finansovaya ustoychivost', uz: 'Moliyaviy barqarorlik' },
    value: Math.max(0, Math.min(100, Math.round(v))),
    inputs,
    hint: {
      ru: 'Маржа дохода, доля собственных средств, наличие залога и текущая долговая нагрузка.',
      uz: 'Daromad marjasi, o'z mablag'lari ulushi, garov mavjudligi va hozirgi qarz yuki.',
    },
  }
}

// ── фактор: рыночный потенциал ─────────────────────────────────────────────
function factorMarket(finance, city) {
  const inputs = []
  let v = 50

  const direction = String(finance.businessDirection || '').toLowerCase()
  if (!city) {
    inputs.push({ label: 'city', value: '—', impact: 0 })
    return {
      key: 'market',
      label: { ru: 'Rinochniy potentsial', uz: 'Bozor potentsiali' },
      value: 50, inputs,
      hint: { ru: 'Gorod ne opredelyon — nevozmojno otsenit sootvetstvie otrasli.', uz: 'Shahar aniqlanmagan.' },
    }
  }

  const sectors = city.recommendedSectors || []
  const match = sectors.some((s) => direction.includes(s) || s.includes(direction.slice(0, 4)))
  const textile = /текстил|ткан|атлас|шёлк|тўқим/.test(direction)
  const food = /пищев|еда|ресторан|кафе|food|озиқ/.test(direction)
  const services = /услуг|сервис|салон|туризм|education|образование|таълим/.test(direction)

  if (match) { v += 20; inputs.push({ label: 'businessDirection ↔ city.recommendedSectors', value: `совпадает (${finance.businessDirection})`, impact: +20 }) }
  else if (direction) { v -= 5; inputs.push({ label: 'businessDirection', value: finance.businessDirection, impact: -5 }) }
  else { inputs.push({ label: 'businessDirection', value: '—', impact: 0 }) }

  // Margilan-specific boosts: export-oriented textiles and tourism are the growth drivers
  if (city.id === 'margilan') {
    if (textile) { v += 12; inputs.push({ label: 'direction=textile × Margilan export +202%', value: 'атлас/трикотаж — экспортный рост', impact: +12 }) }
    if (services) { v += 8; inputs.push({ label: 'direction=services × Margilan tourism 380K/год', value: 'туризм и услуги — растущий сектор (+107%)', impact: +8 }) }
  }
  // Fergana: industrial hubs (textiles, chemicals, food)
  if (city.id === 'fergana') {
    if (textile || food) { v += 8; inputs.push({ label: 'direction × Fergana industrial base 45.9 трлн', value: 'текстиль/пищёвка — крупнейшие кластеры', impact: +8 }) }
  }

  return {
    key: 'market',
    label: { ru: 'Rinochniy potentsial', uz: 'Bozor potentsiali' },
    value: Math.max(0, Math.min(100, Math.round(v))),
    inputs,
    hint: {
      ru: 'Соответствие вашего направления рекомендованным отраслям города и отраслевым трендам.',
      uz: 'Yo'nalishingizning shahar tavsiya etilgan sohalari va soha trendlariga mosligi.',
    },
  }
}

// ── фактор: локация ────────────────────────────────────────────────────────
function factorLocation(profile, city) {
  const inputs = []
  let v = 40

  if (city) {
    v += 25
    inputs.push({ label: 'viloyat/hudud', value: `${profile.viloyat || ''} ${profile.hudud || ''}`.trim() || city.name.ru, impact: +25 })
  } else {
    inputs.push({ label: 'viloyat/hudud', value: '—', impact: 0 })
  }

  if (profile.urbanRural === 'Город' || /шаҳар|urban/i.test(profile.urbanRural || '')) {
    v += 15
    inputs.push({ label: 'urbanRural', value: profile.urbanRural, impact: +15 })
  } else if (has(profile.urbanRural)) {
    v += 5
    inputs.push({ label: 'urbanRural', value: profile.urbanRural, impact: +5 })
  }

  if (has(profile.mahalla)) {
    v += 8
    inputs.push({ label: 'mahalla', value: profile.mahalla, impact: +8 })
  }

  return {
    key: 'location',
    label: { ru: 'Lokatsiya', uz: 'Joylashuv' },
    value: Math.max(0, Math.min(100, Math.round(v))),
    inputs,
    hint: {
      ru: 'Пилотные города (Фергана, Маргилан) дают полный анализ. Городские локации — выше плотность рынка.',
      uz: 'Pilot shaharlarda (Farg'ona, Marg'ilon) to'liq tahlil. Shahar joylashuvlarida — bozor zichligi yuqori.',
    },
  }
}

// ── фактор: конкуренция ────────────────────────────────────────────────────
function factorCompetition(finance, city) {
  const inputs = []
  let v = 65 // нейтрально-оптимистичная база

  if (!city) return {
    key: 'competition',
    label: { ru: 'Konkurentsiya', uz: 'Raqobat' },
    value: 60, inputs,
    hint: { ru: 'Nujen gorod dlya analiza nasishennosti.', uz: 'Tahlil uchun shahar kerak.' },
  }

  const direction = String(finance.businessDirection || '').toLowerCase()
  const isRetail = /розниц|магазин|торгов|чакана/.test(direction)
  const isFood = /пищев|еда|ресторан|кафе|food|озиқ/.test(direction)
  const isTextile = /текстил|ткан|атлас|тўқим/.test(direction)

  if (city.id === 'margilan') {
    if (isRetail) { v -= 25; inputs.push({ label: 'retail × Margilan: 38.2% экономики + 43% ИП в приостановке', value: 'перенасыщено', impact: -25 }) }
    if (isFood) { v -= 8; inputs.push({ label: 'food × Margilan: 562 активных предприятий', value: 'плотный рынок', impact: -8 }) }
    if (isTextile) { v += 5; inputs.push({ label: 'textile × Margilan: экспортный рост', value: 'ниша есть', impact: +5 }) }
  }
  if (city.id === 'fergana') {
    if (isRetail) { v -= 10; inputs.push({ label: 'retail × Fergana area province', value: 'плотный рынок', impact: -10 }) }
  }

  if (!inputs.length) inputs.push({ label: 'businessDirection × city', value: finance.businessDirection || '—', impact: 0 })

  return {
    key: 'competition',
    label: { ru: 'Konkurentsiya', uz: 'Raqobat' },
    value: Math.max(0, Math.min(100, Math.round(v))),
    inputs,
    hint: {
      ru: 'Оценка насыщенности вашей отрасли в выбранном городе на основе данных дашбордов.',
      uz: 'Tanlangan shaharda sohangiz to'yinganligi — dashbord ma'lumotlari asosida.',
    },
  }
}

// ── фактор: бизнес-модель ──────────────────────────────────────────────────
function factorBusinessModel(finance) {
  const inputs = []
  let v = 35

  if (isYes(finance.hasBusinessPlan)) { v += 20; inputs.push({ label: 'hasBusinessPlan', value: 'да', impact: +20 }) }
  else { inputs.push({ label: 'hasBusinessPlan', value: 'нет', impact: 0 }) }

  const ideaLen = String(finance.ideaDescription || '').trim().length
  if (ideaLen > 200) { v += 15; inputs.push({ label: 'ideaDescription (длина)', value: `${ideaLen} симв.`, impact: +15 }) }
  else if (ideaLen > 80) { v += 8; inputs.push({ label: 'ideaDescription (длина)', value: `${ideaLen} симв.`, impact: +8 }) }
  else if (ideaLen > 0) { v += 3; inputs.push({ label: 'ideaDescription (длина)', value: `${ideaLen} симв.`, impact: +3 }) }
  else inputs.push({ label: 'ideaDescription', value: '—', impact: 0 })

  if (has(finance.targetCustomer)) { v += 10; inputs.push({ label: 'targetCustomer', value: finance.targetCustomer, impact: +10 }) }
  if (has(finance.whyThisBusiness)) { v += 7; inputs.push({ label: 'whyThisBusiness', value: 'заполнено', impact: +7 }) }
  if (has(finance.timeline)) { v += 5; inputs.push({ label: 'timeline', value: finance.timeline, impact: +5 }) }
  if (isYes(finance.hasSpace)) { v += 4; inputs.push({ label: 'hasSpace', value: 'да', impact: +4 }) }
  if (isYes(finance.hasEquipment)) { v += 4; inputs.push({ label: 'hasEquipment', value: 'да', impact: +4 }) }

  return {
    key: 'model',
    label: { ru: 'Biznes-model', uz: 'Biznes-model' },
    value: Math.max(0, Math.min(100, Math.round(v))),
    inputs,
    hint: {
      ru: 'Проработанность идеи: план, описание, целевой клиент, сроки, ресурсы.',
      uz: 'G'oyaning pishikligi: reja, tavsif, maqsadli mijoz, muddatlar, resurslar.',
    },
  }
}

// ── Веса (должны в сумме давать 1.0) ───────────────────────────────────────
const WEIGHTS = {
  experience: 0.18,
  finance: 0.22,
  market: 0.18,
  location: 0.14,
  competition: 0.14,
  model: 0.14,
}

export function computeScore(profile = {}, finance = {}, cityId = null, financials = null) {
  const city = cityId ? CITIES[cityId] ?? null : null

  const factors = [
    factorExperience(profile),
    factorFinance(finance, financials),
    factorMarket(finance, city),
    factorLocation(profile, city),
    factorCompetition(finance, city),
    factorBusinessModel(finance),
  ].map((f) => ({
    ...f,
    weight: WEIGHTS[f.key],
    contribution: Math.round(f.value * WEIGHTS[f.key] * 10) / 10,
  }))

  const total = Math.round(factors.reduce((acc, f) => acc + f.value * f.weight, 0))
  const verdict = total >= 70 ? 'good' : total >= 50 ? 'fair' : 'weak'

  return { total, verdict, factors }
}
