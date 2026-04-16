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
    name: { ru: 'Экспресс (Ломбардный)', uz: 'Экспресс (Ломбард)' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 25,
    rateLabel: { ru: '25%', uz: '25%' },
    termMaxMonths: 60,
    termLabel: { ru: 'до 5 лет', uz: '5 йилгача' },
    gracePeriod: null,
    amountMax: 3_500_000_000, // облегченный лимит
    amountMaxStandard: 10_000_000_000,
    amountLabel: { ru: 'до 3,5 млрд сум (облегч.) · до 10 млрд (стандарт)', uz: '3,5 млрд сўмгача (енг.) · 10 млрд (стандарт)' },
    collateral: ['realEstate', 'vehicle'],
    purposes: ['any'],
    purposeLabel: { ru: 'Любые цели', uz: 'Ҳар қандай мақсад' },
  },
  {
    id: 'affordable_imkoniyat',
    name: { ru: 'Доступный (Имконият)', uz: 'Имконият' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 23,
    rateLabel: { ru: '23%', uz: '23%' },
    termMaxMonths: 36,
    termLabel: { ru: 'оборотные — до 1,5 лет · основные — до 3 лет', uz: 'айланма — 1,5 йил · асосий — 3 йил' },
    gracePeriodMonths: 6,
    amountMax: 500_000_000,
    amountFirst: 150_000_000,
    amountLabel: { ru: 'до 150 млн (первый) · до 500 млн (повторный)', uz: '150 млн (биринчи) · 500 млн (такрорий)' },
    collateral: ['insurance'],
    purposes: ['working', 'fixed'],
    purposeLabel: { ru: 'Оборотные или основные средства', uz: 'Айланма ёки асосий воситалар' },
  },
  {
    id: 'overdraft_easy',
    name: { ru: 'Овердрафт (облегч.)', uz: 'Овердрафт (енг.)' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 23,
    rateLabel: { ru: '23%', uz: '23%' },
    termMaxMonths: 12,
    termLabel: { ru: 'до 1 года', uz: '1 йилгача' },
    gracePeriod: null,
    amountMax: 1_000_000_000,
    amountLabel: { ru: 'до 1 млрд сум', uz: '1 млрд сўмгача' },
    collateral: ['insurance'],
    purposes: ['any'],
    purposeLabel: { ru: 'Любые цели', uz: 'Ҳар қандай мақсад' },
  },
  {
    id: 'easy_start',
    name: { ru: 'Лёгкий старт', uz: 'Осон старт' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 24,
    rateLabel: { ru: '24%', uz: '24%' },
    termMaxMonths: 36,
    termLabel: { ru: 'оборотные — до 1,5 лет · основные — до 3 лет', uz: 'айланма — 1,5 йил · асосий — 3 йил' },
    gracePeriodMonths: 6,
    amountMax: 300_000_000,
    amountLabel: { ru: 'до 300 млн сум', uz: '300 млн сўмгача' },
    collateral: ['realEstate', 'vehicle', 'insurance'],
    collateralNote: { ru: 'страховой полис — до 30%', uz: 'суғурта полиси — 30% гача' },
    purposes: ['working', 'fixed'],
    purposeLabel: { ru: 'Оборотные или основные средства', uz: 'Айланма ёки асосий воситалар' },
  },
  {
    id: 'tezkor_cash',
    name: { ru: 'Тезкор (наличными)', uz: 'Тезкор' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 26,
    rateLabel: { ru: '26%', uz: '26%' },
    termMaxMonths: 18,
    termLabel: { ru: 'до 1,5 лет', uz: '1,5 йилгача' },
    gracePeriodMonths: 3,
    amountMax: 1_500_000_000,
    amountLabel: { ru: 'до 1,5 млрд сум', uz: '1,5 млрд сўмгача' },
    collateral: ['realEstate', 'vehicle'],
    purposes: ['any'],
    purposeLabel: { ru: 'Любые цели', uz: 'Ҳар қандай мақсад' },
  },
  {
    id: 'autocredit',
    name: { ru: 'Автокредит', uz: 'Автокредит' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateMinPct: 23,
    rateMaxPct: 24,
    rateLabel: { ru: '23–24%', uz: '23–24%' },
    termMaxMonths: 36,
    termLabel: { ru: 'оборотные — до 1,5 лет · основные — до 3 лет', uz: 'айланма — 1,5 йил · асосий — 3 йил' },
    gracePeriodMonths: 6,
    amountMax: 3_500_000_000,
    amountLabel: { ru: 'до 3,5 млрд сум', uz: '3,5 млрд сўмгача' },
    collateral: ['purchasedVehicle'],
    purposes: ['vehicle'],
    purposeLabel: { ru: 'Покупка легкового авто или малотоннажного грузовика из автосалона', uz: 'Енгил автомобил ёки кичик юк машинасини автосалондан сотиб олиш' },
  },
  {
    id: 'raspiryaysya',
    name: { ru: 'Расширяйся (оборотные)', uz: 'Кенгай' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateByTerm: { '12': 23, '24': 24, '36': 25 },
    rateLabel: { ru: '1 год — 23% · 2 года — 24% · 3 года — 25%', uz: '1 йил — 23% · 2 йил — 24% · 3 йил — 25%' },
    termMaxMonths: 36,
    termLabel: { ru: 'до 1,5 лет · до 3 лет ГКС (по 12 мес.)', uz: '1,5 йил · 3 йил ГКС (12 ойдан)' },
    gracePeriodMonths: 3,
    amountMax: 3_500_000_000,
    amountLabel: { ru: 'до 3,5 млрд сум', uz: '3,5 млрд сўмгача' },
    collateral: ['realEstate', 'vehicle', 'insurance'],
    collateralNote: { ru: 'страховой полис — до 30%', uz: 'суғурта полиси — 30% гача' },
    purposes: ['working'],
    purposeLabel: { ru: 'Пополнение оборотных средств', uz: 'Айланма маблағларни тўлдириш' },
  },
  {
    id: 'razvivaysya',
    name: { ru: 'Развивайся (основные)', uz: 'Ривожлан' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 23,
    rateLabel: { ru: '23%', uz: '23%' },
    termMaxMonths: 48,
    termLabel: { ru: 'до 4 лет', uz: '4 йилгача' },
    gracePeriodMonths: 3,
    amountMax: 3_500_000_000,
    amountLabel: { ru: 'до 3,5 млрд сум', uz: '3,5 млрд сўмгача' },
    collateral: ['realEstate', 'vehicle', 'insurance'],
    collateralNote: { ru: 'страховой полис — до 30%', uz: 'суғурта полиси — 30% гача' },
    purposes: ['fixed'],
    purposeLabel: { ru: 'Покупка основных средств', uz: 'Асосий воситаларни сотиб олиш' },
  },
  {
    id: 'business_mortgage',
    name: { ru: 'Бизнес-ипотека', uz: 'Бизнес ипотека' },
    tier: 'easy',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateMinPct: 23,
    rateMaxPct: 26.5,
    rateLabel: { ru: '23–26,5%', uz: '23–26,5%' },
    termMaxMonths: 180,
    termLabel: { ru: 'до 15 лет', uz: '15 йилгача' },
    gracePeriod: null,
    amountMax: 3_500_000_000,
    amountMaxStandard: 10_000_000_000,
    amountLabel: { ru: 'до 3,5 млрд (облегч.) · до 10 млрд (стандарт)', uz: '3,5 млрд (енг.) · 10 млрд (стандарт)' },
    collateral: ['purchasedRealEstate'],
    purposes: ['realEstate'],
    purposeLabel: { ru: 'Покупка коммерческой недвижимости от застройщиков', uz: 'Қурувчилардан тижорат кўчмас мулкини сотиб олиш' },
  },
  // ── Стандартные продукты ───────────────────────────────────────────────
  {
    id: 'working_standard',
    name: { ru: 'Оборотный кредит', uz: 'Айланма кредити' },
    tier: 'standard',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    rateByTerm: { '12': 21, '24': 22 },
    rateLabel: { ru: '1 год — 21% · >1 года — 22%', uz: '1 йил — 21% · 1+ йил — 22%' },
    termMaxMonths: null,
    termLabel: { ru: 'не ограничено', uz: 'чекланмаган' },
    gracePeriod: { ru: 'не ограничено', uz: 'чекланмаган' },
    amountMax: null,
    amountLabel: { ru: 'не ограничено', uz: 'чекланмаган' },
    collateral: ['any'],
    purposes: ['working'],
    purposeLabel: { ru: 'Пополнение оборотных средств', uz: 'Айланма маблағларни тўлдириш' },
  },
  {
    id: 'investment_standard',
    name: { ru: 'Инвестиционный кредит', uz: 'Инвестицион кредит' },
    tier: 'standard',
    entityTypes: ['LLC', 'IP'],
    currency: 'UZS',
    ratePct: 22,
    rateLabel: { ru: '22%', uz: '22%' },
    termMaxMonths: null,
    termLabel: { ru: 'не ограничено', uz: 'чекланмаган' },
    gracePeriod: { ru: 'не ограничено', uz: 'чекланмаган' },
    amountMax: null,
    amountLabel: { ru: 'не ограничено', uz: 'чекланмаган' },
    collateral: ['any'],
    purposes: ['fixed'],
    purposeLabel: { ru: 'Покупка основных средств', uz: 'Асосий воситаларни сотиб олиш' },
  },
]

const COLL_LABELS = {
  realEstate: { ru: 'Недвижимость', uz: 'Кўчмас мулк' },
  vehicle: { ru: 'Автотранспорт', uz: 'Автотранспорт' },
  insurance: { ru: 'Страховой полис', uz: 'Суғурта полиси' },
  purchasedVehicle: { ru: 'Приобретаемое авто', uz: 'Сотиб олинаётган авто' },
  purchasedRealEstate: { ru: 'Приобретаемая недвижимость', uz: 'Сотиб олинаётган мулк' },
  any: { ru: 'Любой законный вид залога', uz: 'Ҳар қандай қонуний гаров' },
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
