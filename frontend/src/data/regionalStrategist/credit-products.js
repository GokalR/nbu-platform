// Каталог кредитных продуктов NBU для МСБ.
// Источник: «Кредиты 2026.xlsx» — Паспорта МСБ продуктов (утверждено март 2026).
// Все суммы в сумах. Ставки — годовые.
// tier:  'easy'      — облегченные продукты (быстрое оформление)
//        'standard'  — стандартные продукты (без ограничений по сумме/сроку)
// entityTypes: ['LLC','IP'] — доступно для ЮЛ и ИП
// collateral: коды видов залога — realEstate | vehicle | insurance | purchasedVehicle | purchasedRealEstate | any
// purpose:    рабочая | основные | любые | покупка_авто | покупка_недвижимости

export const CREDIT_PRODUCTS = [
  // ── Облегченные продукты ───────────────────────────────────────────────
  {
    id: 'express_lombard',
    name: { ru: 'Ekspress (Lombardniy)', uz: 'Ekspress (Lombard)' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 25,
    rateLabel: { ru: '25%', uz: '25%' },
    termMaxMonths: 60,
    termLabel: { ru: 'do 5 let', uz: '5 yilgacha' },
    gracePeriod: null,
    amountMax: 3_500_000_000, // облегченный лимит
    amountMaxStandard: 10_000_000_000,
    amountLabel: { ru: 'do 3,5 mlrd sum (oblegch.) · do 10 mlrd (standart)', uz: '3,5 mlrd soʻmgacha (eng.) · 10 mlrd (standart)' },
    collateral: ['realEstate', 'vehicle'],
    purposes: ['any'],
    purposeLabel: { ru: 'Lyubie tseli', uz: 'Har qanday maqsad' },
  },
  {
    id: 'affordable_imkoniyat',
    name: { ru: 'Dostupniy (Imkoniyat)', uz: 'Imkoniyat' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 23,
    rateLabel: { ru: '23%', uz: '23%' },
    termMaxMonths: 36,
    termLabel: { ru: 'oborotnie — do 1,5 let · osnovnie — do 3 let', uz: 'aylanma — 1,5 yil · asosiy — 3 yil' },
    gracePeriodMonths: 6,
    amountMax: 500_000_000,
    amountFirst: 150_000_000,
    amountLabel: { ru: 'do 150 mln (perviy) · do 500 mln (povtorniy)', uz: '150 mln (birinchi) · 500 mln (takroriy)' },
    collateral: ['insurance'],
    purposes: ['working', 'fixed'],
    purposeLabel: { ru: 'Oborotnie ili osnovnie sredstva', uz: 'Aylanma yoki asosiy vositalar' },
  },
  {
    id: 'overdraft_easy',
    name: { ru: 'Overdraft (oblegch.)', uz: 'Overdraft (eng.)' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 23,
    rateLabel: { ru: '23%', uz: '23%' },
    termMaxMonths: 12,
    termLabel: { ru: 'do 1 goda', uz: '1 yilgacha' },
    gracePeriod: null,
    amountMax: 1_000_000_000,
    amountLabel: { ru: 'do 1 mlrd sum', uz: '1 mlrd soʻmgacha' },
    collateral: ['insurance'],
    purposes: ['any'],
    purposeLabel: { ru: 'Lyubie tseli', uz: 'Har qanday maqsad' },
  },
  {
    id: 'easy_start',
    name: { ru: 'Lyogkiy start', uz: 'Oson start' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 24,
    rateLabel: { ru: '24%', uz: '24%' },
    termMaxMonths: 36,
    termLabel: { ru: 'oborotnie — do 1,5 let · osnovnie — do 3 let', uz: 'aylanma — 1,5 yil · asosiy — 3 yil' },
    gracePeriodMonths: 6,
    amountMax: 300_000_000,
    amountLabel: { ru: 'do 300 mln sum', uz: '300 mln soʻmgacha' },
    collateral: ['realEstate', 'vehicle', 'insurance'],
    collateralNote: { ru: 'straxovoy polis — do 30%', uz: 'sugʻurta polisi — 30% gacha' },
    purposes: ['working', 'fixed'],
    purposeLabel: { ru: 'Oborotnie ili osnovnie sredstva', uz: 'Aylanma yoki asosiy vositalar' },
  },
  {
    id: 'tezkor_cash',
    name: { ru: 'Tezkor (nalichnimi)', uz: 'Tezkor' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 26,
    rateLabel: { ru: '26%', uz: '26%' },
    termMaxMonths: 18,
    termLabel: { ru: 'do 1,5 let', uz: '1,5 yilgacha' },
    gracePeriodMonths: 3,
    amountMax: 1_500_000_000,
    amountLabel: { ru: 'do 1,5 mlrd sum', uz: '1,5 mlrd soʻmgacha' },
    collateral: ['realEstate', 'vehicle'],
    purposes: ['any'],
    purposeLabel: { ru: 'Lyubie tseli', uz: 'Har qanday maqsad' },
  },
  {
    id: 'autocredit',
    name: { ru: 'Avtokredit', uz: 'Avtokredit' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateMinPct: 23,
    rateMaxPct: 24,
    rateLabel: { ru: '23–24%', uz: '23–24%' },
    termMaxMonths: 36,
    termLabel: { ru: 'oborotnie — do 1,5 let · osnovnie — do 3 let', uz: 'aylanma — 1,5 yil · asosiy — 3 yil' },
    gracePeriodMonths: 6,
    amountMax: 3_500_000_000,
    amountLabel: { ru: 'do 3,5 mlrd sum', uz: '3,5 mlrd soʻmgacha' },
    collateral: ['purchasedVehicle'],
    purposes: ['vehicle'],
    purposeLabel: { ru: 'Pokupka legkovogo avto ili malotonnajnogo gruzovika iz avtosalona', uz: 'Engil avtomobil yoki kichik yuk mashinasini avtosalondan sotib olish' },
  },
  {
    id: 'raspiryaysya',
    name: { ru: 'Rasshiryaysya (oborotnie)', uz: 'Kengay' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateByTerm: { '12': 23, '24': 24, '36': 25 },
    rateLabel: { ru: '1 god — 23% · 2 goda — 24% · 3 goda — 25%', uz: '1 yil — 23% · 2 yil — 24% · 3 yil — 25%' },
    termMaxMonths: 36,
    termLabel: { ru: 'do 1,5 let · do 3 let GKS (po 12 mes.)', uz: '1,5 yil · 3 yil GKS (12 oydan)' },
    gracePeriodMonths: 3,
    amountMax: 3_500_000_000,
    amountLabel: { ru: 'do 3,5 mlrd sum', uz: '3,5 mlrd soʻmgacha' },
    collateral: ['realEstate', 'vehicle', 'insurance'],
    collateralNote: { ru: 'straxovoy polis — do 30%', uz: 'sugʻurta polisi — 30% gacha' },
    purposes: ['working'],
    purposeLabel: { ru: 'Popolnenie oborotnix sredstv', uz: 'Aylanma mablagʻlarni toʻldirish' },
  },
  {
    id: 'razvivaysya',
    name: { ru: 'Razvivaysya (osnovnie)', uz: 'Rivojlan' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 23,
    rateLabel: { ru: '23%', uz: '23%' },
    termMaxMonths: 48,
    termLabel: { ru: 'do 4 let', uz: '4 yilgacha' },
    gracePeriodMonths: 3,
    amountMax: 3_500_000_000,
    amountLabel: { ru: 'do 3,5 mlrd sum', uz: '3,5 mlrd soʻmgacha' },
    collateral: ['realEstate', 'vehicle', 'insurance'],
    collateralNote: { ru: 'straxovoy polis — do 30%', uz: 'sugʻurta polisi — 30% gacha' },
    purposes: ['fixed'],
    purposeLabel: { ru: 'Pokupka osnovnix sredstv', uz: 'Asosiy vositalarni sotib olish' },
  },
  {
    id: 'business_mortgage',
    name: { ru: 'Biznes-ipoteka', uz: 'Biznes ipoteka' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateMinPct: 23,
    rateMaxPct: 26.5,
    rateLabel: { ru: '23–26,5%', uz: '23–26,5%' },
    termMaxMonths: 180,
    termLabel: { ru: 'do 15 let', uz: '15 yilgacha' },
    gracePeriod: null,
    amountMax: 3_500_000_000,
    amountMaxStandard: 10_000_000_000,
    amountLabel: { ru: 'do 3,5 mlrd (oblegch.) · do 10 mlrd (standart)', uz: '3,5 mlrd (eng.) · 10 mlrd (standart)' },
    collateral: ['purchasedRealEstate'],
    purposes: ['realEstate'],
    purposeLabel: { ru: 'Pokupka kommercheskoy nedvijimosti ot zastroyshikov', uz: 'Quruvchilardan tijorat koʻchmas mulkini sotib olish' },
  },
  // ── Стандартные продукты ───────────────────────────────────────────────
  {
    id: 'working_standard',
    name: { ru: 'Oborotniy kredit', uz: 'Aylanma krediti' },
    tier: 'standard',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateByTerm: { '12': 21, '24': 22 },
    rateLabel: { ru: '1 god — 21% · >1 goda — 22%', uz: '1 yil — 21% · 1+ yil — 22%' },
    termMaxMonths: null,
    termLabel: { ru: 'ne ogranicheno', uz: 'cheklanmagan' },
    gracePeriod: { ru: 'ne ogranicheno', uz: 'cheklanmagan' },
    amountMax: null,
    amountLabel: { ru: 'ne ogranicheno', uz: 'cheklanmagan' },
    collateral: ['any'],
    purposes: ['working'],
    purposeLabel: { ru: 'Popolnenie oborotnix sredstv', uz: 'Aylanma mablagʻlarni toʻldirish' },
  },
  {
    id: 'investment_standard',
    name: { ru: 'Investitsionniy kredit', uz: 'Investitsion kredit' },
    tier: 'standard',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 22,
    rateLabel: { ru: '22%', uz: '22%' },
    termMaxMonths: null,
    termLabel: { ru: 'ne ogranicheno', uz: 'cheklanmagan' },
    gracePeriod: { ru: 'ne ogranicheno', uz: 'cheklanmagan' },
    amountMax: null,
    amountLabel: { ru: 'ne ogranicheno', uz: 'cheklanmagan' },
    collateral: ['any'],
    purposes: ['fixed'],
    purposeLabel: { ru: 'Pokupka osnovnix sredstv', uz: 'Asosiy vositalarni sotib olish' },
  },
]

const COLL_LABELS = {
  realEstate: { ru: 'Nedvijimost', uz: 'Koʻchmas mulk' },
  vehicle: { ru: 'Avtotransport', uz: 'Avtotransport' },
  insurance: { ru: 'Straxovoy polis', uz: 'Sugʻurta polisi' },
  purchasedVehicle: { ru: 'Priobretaemoe avto', uz: 'Sotib olinayotgan avto' },
  purchasedRealEstate: { ru: 'Priobretaemaya nedvijimost', uz: 'Sotib olinayotgan mulk' },
  any: { ru: 'Lyuboy zakonniy vid zaloga', uz: 'Har qanday qonuniy garov' },
}

export const collateralLabel = (code, lang = 'ru') => COLL_LABELS[code]?.[lang] ?? code

// Scoring helper: given a user profile+finance object, rank products from best to worst fit.
// Returns [{ product, score, reasons: [string] }], sorted desc.
// Pure function, no side effects. Used by Step 5 Results.
export function matchCreditProducts({ loanAmount = 0, collateral = null, purpose = 'any', entityType = 'LLC', firstTime = true, lang = 'ru' } = {}) {
  const amount = Number(loanAmount) || 0

  return CREDIT_PRODUCTS.map((p) => {
    const reasons = []
    let score = 50

    // Entity type match
    if (p.entityTypes.includes(entityType)) {
      score += 5
    } else {
      score -= 40
      reasons.push(lang === 'uz' ? 'Субъект тури мос эмас' : 'Тип субъекта не подходит')
    }

    // Amount fit
    const cap = p.amountMax ?? Infinity
    const firstCap = firstTime && p.amountFirst ? p.amountFirst : cap
    if (amount === 0) {
      // no amount specified — neutral
    } else if (amount <= firstCap) {
      score += 20
      reasons.push(lang === 'uz' ? `Сумма ${formatAmount(amount, lang)} лимитга мос` : `Сумма ${formatAmount(amount, lang)} в пределах лимита`)
    } else if (amount <= cap) {
      score += 10
      if (firstTime && p.amountFirst) {
        reasons.push(lang === 'uz' ? 'Фақат такрорий кредит учун' : 'Доступно только для повторного кредита')
      }
    } else {
      score -= 30
      reasons.push(lang === 'uz' ? `Сумма лимитдан ошади (${p.amountLabel[lang]})` : `Сумма превышает лимит (${p.amountLabel[lang]})`)
    }

    // Collateral fit
    if (collateral && p.collateral.includes(collateral)) {
      score += 15
      reasons.push(lang === 'uz' ? `Гаров тури мос: ${collateralLabel(collateral, lang)}` : `Залог подходит: ${collateralLabel(collateral, lang)}`)
    } else if (p.collateral.includes('any')) {
      score += 5
    } else if (collateral) {
      score -= 10
    }

    // Purpose fit
    if (p.purposes.includes(purpose) || p.purposes.includes('any')) {
      score += 10
    } else {
      score -= 15
      reasons.push(lang === 'uz' ? 'Мақсад мос эмас' : 'Цель не соответствует')
    }

    // Rate preference — cheaper is better (nudge, not dominant)
    const rate = p.ratePct ?? p.rateMinPct ?? 24
    score += Math.max(0, 26 - rate) * 1.2

    return { product: p, score: Math.round(score), reasons }
  }).sort((a, b) => b.score - a.score)
}

function formatAmount(n, lang = 'ru') {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1).replace('.0', '')} ${lang === 'uz' ? 'млрд сўм' : 'млрд сум'}`
  if (n >= 1e6) return `${Math.round(n / 1e6)} ${lang === 'uz' ? 'млн сўм' : 'млн сум'}`
  return `${n.toLocaleString('ru-RU')} ${lang === 'uz' ? 'сўм' : 'сум'}`
}

export const CREDIT_TOTAL = CREDIT_PRODUCTS.length
