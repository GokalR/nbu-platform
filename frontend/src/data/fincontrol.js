// Demo data for the FinControl module — mirrors the colleague's HTML mockups.
// All amounts in UZS unless stated.
//
// User-visible labels are exposed as factory functions that accept `t` from
// vue-i18n. Views call e.g. `computed(() => makeAccounts(t))` to get a reactive
// list whose strings re-render when the locale switches.

import i18n from '@/i18n'

export const makeCompany = (t) => ({
  name: t('fincontrol.data.company.name'),
  inn: '302 874 566',
  contact: t('fincontrol.data.company.contact'),
  phone: '+998 90 256 47 12',
})

export const makeAccounts = (t) => [
  {
    key: 'nbu',
    bank: t('fincontrol.data.accounts.nbu.bank'),
    number: '•••• •••• 4402',
    balance: '524 000 000',
    balanceRaw: 524_000_000,
    badges: [
      { label: t('fincontrol.data.badges.settlement'), tone: 'blue' },
      { label: t('fincontrol.data.badges.activeDot'), tone: 'green' },
    ],
    stats: { min: '412М', max: '611М', avg: '518М' },
    share: 62,
    trend: { value: '+8.2%', tone: 'up' },
    spark: [42, 48, 45, 50, 53, 49, 55, 58, 56, 60, 62, 58, 64, 67, 65, 70, 68, 71, 74, 72, 76, 78, 75, 80, 82, 79, 84, 86, 83, 88],
    color: '#0054A6',
    cardTone: 'blue',
  },
  {
    key: 'hbk',
    bank: t('fincontrol.data.accounts.hbk.bank'),
    number: '•••• •••• 1192',
    balance: '215 000 000',
    balanceRaw: 215_000_000,
    badges: [
      { label: t('fincontrol.data.badges.reserve'), tone: 'teal' },
      { label: t('fincontrol.data.badges.activeDot'), tone: 'green' },
    ],
    stats: { min: '180М', max: '248М', avg: '210М' },
    share: 25,
    trend: { value: '+2.1%', tone: 'up' },
    spark: [180, 184, 187, 192, 195, 198, 200, 203, 205, 208, 210, 213, 215, 218, 220, 222, 220, 218, 217, 215, 213, 215, 218, 220, 222, 218, 215, 213, 215, 215],
    color: '#0891B2',
    cardTone: 'teal',
  },
  {
    key: 'cash',
    bank: t('fincontrol.data.accounts.cash.bank'),
    number: t('fincontrol.data.accounts.cash.number'),
    balance: '103 500 000',
    balanceRaw: 103_500_000,
    badges: [
      { label: t('fincontrol.data.badges.cash'), tone: 'amber' },
      { label: t('fincontrol.data.badges.bookkeeping'), tone: 'slate' },
    ],
    stats: { min: '62М', max: '140М', avg: '98М' },
    share: 13,
    trend: { value: '−1.4%', tone: 'down' },
    spark: [120, 115, 110, 118, 122, 125, 130, 128, 124, 120, 116, 112, 108, 105, 102, 100, 98, 96, 94, 92, 95, 98, 100, 102, 105, 108, 106, 104, 103, 103],
    color: '#94A3B8',
    cardTone: 'amber',
  },
]

export const makeDashboardKpis = (t) => [
  { key: 'balance', label: t('fincontrol.data.kpi.balance'), value: '842 500 000', unit: 'UZS', delta: '▲ 5.3%', deltaTone: 'green', sub: t('fincontrol.data.kpi.balanceSub'), icon: 'account_balance', iconBg: '#EEF4FF', iconColor: '#0054A6' },
  { key: 'inflow', label: t('fincontrol.data.kpi.inflow'), value: '320 000 000', unit: 'UZS', valueTone: 'green', delta: '▲ 12.1%', deltaTone: 'green', sub: t('fincontrol.data.kpi.currentMonth'), icon: 'south_west', iconBg: '#E6F7EE', iconColor: '#00A651' },
  { key: 'outflow', label: t('fincontrol.data.kpi.outflow'), value: '198 000 000', unit: 'UZS', valueTone: 'red', delta: '▲ 3.7%', deltaTone: 'red', sub: t('fincontrol.data.kpi.currentMonth'), icon: 'north_east', iconBg: '#FEE2E5', iconColor: '#E0384B' },
  { key: 'netcf', label: t('fincontrol.data.kpi.netCf'), value: '122 000 000', unit: 'UZS', valueTone: 'accent', delta: 'CF +', deltaTone: 'blue', sub: t('fincontrol.data.kpi.netCfSub'), icon: 'savings', iconBg: '#EEF4FF', iconColor: '#0054A6' },
  { key: 'runway', label: 'Runway', value: t('fincontrol.data.kpi.runwayValue', { n: '4.2' }), valueTone: 'amber', delta: t('fincontrol.data.kpi.runwayDelta', { n: '~4' }), deltaTone: 'amber', sub: t('fincontrol.data.kpi.runwaySub'), icon: 'flight_takeoff', iconBg: '#FEF3C7', iconColor: '#F59E0B' },
]

export const makeMonthly = (t) => ({
  labels: [
    t('fincontrol.data.months.may'),
    t('fincontrol.data.months.jun'),
    t('fincontrol.data.months.jul'),
    t('fincontrol.data.months.aug'),
    t('fincontrol.data.months.sep'),
    t('fincontrol.data.months.oct'),
    t('fincontrol.data.months.nov'),
    t('fincontrol.data.months.dec'),
    t('fincontrol.data.months.jan'),
    t('fincontrol.data.months.feb'),
    t('fincontrol.data.months.mar'),
    t('fincontrol.data.months.apr'),
  ],
  income: [245, 310, 280, 320, 295, 260, 285, 300, 270, 315, 290, 320],
  expenses: [180, 195, 170, 210, 185, 175, 195, 200, 165, 185, 180, 198],
})

export const makeExpenseStructure = (t) => [
  { label: t('fincontrol.data.cat.purchases'), value: 34, amount: '67.3М', color: '#0054A6' },
  { label: t('fincontrol.data.cat.salary'),    value: 28, amount: '55.4М', color: '#00A651' },
  { label: t('fincontrol.data.cat.taxes'),     value: 14, amount: '27.7М', color: '#F59E0B' },
  { label: t('fincontrol.data.cat.rent'),      value: 12, amount: '23.8М', color: '#E0384B' },
  { label: t('fincontrol.data.cat.marketing'), value: 8,  amount: '15.8М', color: '#8B5CF6' },
  { label: t('fincontrol.data.cat.other'),     value: 4,  amount: '7.9М',  color: '#94A3B8' },
]

export const makeTopCounterpartiesSuppliers = (t) => [
  { initials: 'СТ', tone: 'av-blue',   name: 'Silk Trade LLC',     sub: t('fincontrol.data.cp.txCount', { n: 14, m: t('fincontrol.data.shortMonths.apr') }), amount: '−52 400 000' },
  { initials: 'АП', tone: 'av-green',  name: t('fincontrol.data.cp.agroPrime'),    sub: t('fincontrol.data.cp.txCount', { n: 9,  m: t('fincontrol.data.shortMonths.apr') }), amount: '−38 700 000' },
  { initials: 'УТ', tone: 'av-amber',  name: t('fincontrol.data.cp.uzPakTrans'),   sub: t('fincontrol.data.cp.txCount', { n: 6,  m: t('fincontrol.data.shortMonths.apr') }), amount: '−21 200 000' },
  { initials: 'НЛ', tone: 'av-purple', name: 'NovaTech Logistics', sub: t('fincontrol.data.cp.txCount', { n: 5,  m: t('fincontrol.data.shortMonths.apr') }), amount: '−18 900 000' },
  { initials: 'МС', tone: 'av-red',    name: t('fincontrol.data.cp.megaSnab'),     sub: t('fincontrol.data.cp.txCount', { n: 4,  m: t('fincontrol.data.shortMonths.apr') }), amount: '−14 600 000' },
]

export const makeAiSignals = (t) => [
  { tone: 'red',   icon: 'warning',  title: t('fincontrol.data.ai.expGrowthTitle'),  text: t('fincontrol.data.ai.expGrowthText'),  time: t('fincontrol.data.ai.timeToday',     { time: '09:14' }) },
  { tone: 'amber', icon: 'schedule', title: t('fincontrol.data.ai.runwayTitle'),     text: t('fincontrol.data.ai.runwayText'),     time: t('fincontrol.data.ai.timeToday',     { time: '08:30' }) },
  { tone: 'green', icon: 'thumb_up', title: t('fincontrol.data.ai.cfPositiveTitle'), text: t('fincontrol.data.ai.cfPositiveText'), time: t('fincontrol.data.ai.timeYesterday', { time: '18:05' }) },
]

export const makeTransactions = (t) => {
  const apr = t('fincontrol.data.shortMonths.apr')
  const day = (n) => `${n} ${apr}`
  return [
    { date: day(14), time: '15:22', av: 'АП',  avTone: 'av-green',  name: t('fincontrol.data.cp.agroPrime'),    purpose: t('fincontrol.data.tx.paymentContract',     { n: '145-А' }),    category: t('fincontrol.data.cat.income'),    categoryTone: 'green',  income: '+85 000 000', account: 'NBU •4402' },
    { date: day(13), time: '11:08', av: 'СТ',  avTone: 'av-blue',   name: 'Silk Trade LLC',                     purpose: t('fincontrol.data.tx.purchaseBatch',       { n: '38' }),       category: t('fincontrol.data.cat.purchases'), categoryTone: 'blue',   expense: '−52 400 000', account: 'NBU •4402' },
    { date: day(12), time: '09:45', av: 'НБУ', avTone: 'av-slate',  name: t('fincontrol.data.cp.gnk'),          purpose: t('fincontrol.data.tx.vatMarch'),                                  category: t('fincontrol.data.cat.taxes'),     categoryTone: 'amber',  expense: '−27 720 000', account: 'HBK •1192' },
    { date: day(11), time: '14:30', av: 'УТ',  avTone: 'av-amber',  name: t('fincontrol.data.cp.uzPakTrans'),   purpose: t('fincontrol.data.tx.logisticsApr'),                              category: t('fincontrol.data.cat.logistics'), categoryTone: 'amber',  expense: '−21 200 000', account: 'NBU •4402' },
    { date: day(10), time: '16:55', av: 'СА',  avTone: 'av-blue',   name: t('fincontrol.data.cp.sarmat'),       purpose: t('fincontrol.data.tx.paymentInvoice',      { n: '2026-084' }), category: t('fincontrol.data.cat.income'),    categoryTone: 'green',  income: '+63 500 000', account: 'NBU •4402' },
    { date: day(9),  time: '10:00', av: 'ЗП',  avTone: 'av-purple', name: t('fincontrol.data.tx.salaryPayout'), purpose: t('fincontrol.data.tx.salaryStaffApr'),                            category: t('fincontrol.data.cat.salary'),    categoryTone: 'purple', expense: '−55 440 000', account: 'NBU •4402' },
    { date: day(8),  time: '13:20', av: 'МС',  avTone: 'av-green',  name: t('fincontrol.data.cp.megaSnab'),     purpose: t('fincontrol.data.tx.govContract',         { n: '2026-08' }),  category: t('fincontrol.data.cat.govContracts'), categoryTone: 'green', income: '+38 400 000', account: 'HBK •1192' },
    { date: day(8),  time: '12:18', av: 'НЛ',  avTone: 'av-purple', name: 'NovaTech Logistics',                 purpose: t('fincontrol.data.tx.advanceCash'),                               category: t('fincontrol.data.cat.logistics'), categoryTone: 'amber',  expense: '−18 900 000', account: t('fincontrol.data.accounts.cash.short') },
  ]
}

export const makeRecurring = (t) => ({
  outgoing: [
    { name: t('fincontrol.data.rec.warehouseRent'),  sub: t('fincontrol.data.cp.megaLogist'),    category: t('fincontrol.data.cat.rent'),       categoryTone: 'purple', period: t('fincontrol.data.period.monthly'),    date: t('fincontrol.data.shortDate.may01'), amount: '−24 000 000', status: t('fincontrol.data.status.fundsOk'),    statusTone: 'green' },
    { name: t('fincontrol.data.rec.staffSalary'),    sub: t('fincontrol.data.rec.staffCount',    { n: 31 }),  category: t('fincontrol.data.cat.salary'),  categoryTone: 'red',    period: t('fincontrol.data.period.monthly'),    date: t('fincontrol.data.shortDate.apr25'), amount: '−55 440 000', status: t('fincontrol.data.status.fundsLow'),   statusTone: 'red',  danger: true },
    { name: t('fincontrol.data.rec.vatTax'),         sub: t('fincontrol.data.cp.gnk'),           category: t('fincontrol.data.cat.taxes'),   categoryTone: 'amber',  period: t('fincontrol.data.period.quarterly'),  date: t('fincontrol.data.shortDate.jul15'), amount: '−27 720 000', status: t('fincontrol.data.status.fundsOk'),    statusTone: 'green' },
    { name: t('fincontrol.data.rec.internetPhone'),  sub: 'UzTelecom',                              category: t('fincontrol.data.cat.operational'), categoryTone: 'blue', period: t('fincontrol.data.period.monthly'),    date: t('fincontrol.data.shortDate.may05'), amount: '−2 400 000',  status: t('fincontrol.data.status.fundsOk'),    statusTone: 'green' },
    { name: t('fincontrol.data.rec.propertyIns'),    sub: t('fincontrol.data.cp.uzAgroSig'),     category: t('fincontrol.data.cat.insurance'), categoryTone: 'green', period: t('fincontrol.data.period.perQuarter'), date: t('fincontrol.data.shortDate.jun30'), amount: '−8 700 000',  status: t('fincontrol.data.status.expected'),   statusTone: 'amber' },
  ],
  incoming: [
    { name: t('fincontrol.data.cp.sarmat'),          sub: t('fincontrol.data.rec.subscription'),    category: t('fincontrol.data.cat.income'),    categoryTone: 'green', period: t('fincontrol.data.period.monthly'), date: t('fincontrol.data.shortDate.may03'), amount: '+45 000 000', status: t('fincontrol.data.status.confirmed'), statusTone: 'green' },
    { name: t('fincontrol.data.rec.hbkCoupon'),      sub: t('fincontrol.data.rec.deposit',          { n: '9963517' }), category: t('fincontrol.data.cat.financial'), categoryTone: 'blue', period: t('fincontrol.data.period.monthly'), date: t('fincontrol.data.shortDate.may10'), amount: '+3 870 000',  status: t('fincontrol.data.status.confirmed'), statusTone: 'green' },
    { name: t('fincontrol.data.rec.agroInstall'),    sub: t('fincontrol.data.rec.payment',          { n: 3, total: 6 }), category: t('fincontrol.data.cat.income'), categoryTone: 'green', period: t('fincontrol.data.period.monthly'), date: t('fincontrol.data.shortDate.may15'), amount: '+28 000 000', status: t('fincontrol.data.status.expected'),  statusTone: 'amber' },
  ],
})

export const makeCounterparties = (t) => [
  { initials: 'ИР',  tone: 'av-green',  name: t('fincontrol.data.cp.ipRashidov'),  inn: '307 282 145', type: t('fincontrol.data.cpType.payer'),    typeTone: 'green',  tx: 9, amount: '+35 600 000', amountTone: 'green', last: t('fincontrol.data.shortDate.apr14_2026'), status: t('fincontrol.data.cpStatus.regular'), statusTone: 'blue' },
  { initials: 'СТ',  tone: 'av-blue',   name: 'Silk Trade LLC',                       inn: '302 418 762', type: t('fincontrol.data.cpType.recipient'), typeTone: 'blue',   tx: 7, amount: '−18 900 000', amountTone: 'red',   last: t('fincontrol.data.shortDate.apr13_2026'), status: t('fincontrol.data.cpStatus.regular'), statusTone: 'blue' },
  { initials: 'АГ',  tone: 'av-amber',  name: t('fincontrol.data.cp.arendaGroup'), inn: '201 843 920', type: t('fincontrol.data.cpType.recipient'), typeTone: 'amber',  tx: 1, amount: '−12 800 000', amountTone: 'red',   last: t('fincontrol.data.shortDate.apr01_2026'), status: t('fincontrol.data.cpStatus.regular'), statusTone: 'blue' },
  { initials: 'СА',  tone: 'av-blue',   name: t('fincontrol.data.cp.sarmat'),      inn: '308 194 012', type: t('fincontrol.data.cpType.payer'),    typeTone: 'green',  tx: 3, amount: '+28 400 000', amountTone: 'green', last: t('fincontrol.data.shortDate.apr10_2026'), status: t('fincontrol.data.cpStatus.regular'), statusTone: 'blue' },
  { initials: 'НЛ',  tone: 'av-purple', name: 'NovaTech Logistics',                  inn: '402 183 774', type: t('fincontrol.data.cpType.recipient'), typeTone: 'blue',   tx: 5, amount: '−8 900 000',  amountTone: 'red',   last: t('fincontrol.data.shortDate.apr08_2026'), status: t('fincontrol.data.cpStatus.regular'), statusTone: 'blue' },
  { initials: 'МС',  tone: 'av-green',  name: t('fincontrol.data.cp.megaSnab'),    inn: '310 284 198', type: t('fincontrol.data.cpType.payer'),    typeTone: 'green',  tx: 4, amount: '+14 200 000', amountTone: 'green', last: t('fincontrol.data.shortDate.apr07_2026'), status: t('fincontrol.data.cpStatus.oneTime'), statusTone: 'slate' },
  { initials: 'АД',  tone: 'av-amber',  name: 'Ad Pro Agency',                       inn: '405 192 831', type: t('fincontrol.data.cpType.recipient'), typeTone: 'amber',  tx: 2, amount: '−7 200 000',  amountTone: 'red',   last: t('fincontrol.data.shortDate.apr05_2026'), status: t('fincontrol.data.cpStatus.oneTime'), statusTone: 'slate' },
  { initials: 'ГНК', tone: 'av-slate',  name: t('fincontrol.data.cp.gnk'),         inn: '100 000 001', type: t('fincontrol.data.cpType.gov'),       typeTone: 'purple', tx: 3, amount: '−6 100 000',  amountTone: 'red',   last: t('fincontrol.data.shortDate.apr03_2026'), status: t('fincontrol.data.cpStatus.regular'), statusTone: 'blue' },
]

export const makeExpenseCategories = (t) => [
  { emoji: '🛒', name: t('fincontrol.data.cat.purchases'), amount: '67 320 000', share: 34, bar: 82, trend: '↑ +4.1%', trendTone: 'red' },
  { emoji: '👥', name: t('fincontrol.data.cat.salary'),    amount: '55 440 000', share: 28, bar: 68, trend: '→ 0.0%',  trendTone: 'slate' },
  { emoji: '🏛', name: t('fincontrol.data.cat.taxes'),     amount: '27 720 000', share: 14, bar: 35, trend: '↓ −2.3%', trendTone: 'green' },
  { emoji: '🏢', name: t('fincontrol.data.cat.rent'),      amount: '23 760 000', share: 12, bar: 29, trend: '→ 0.0%',  trendTone: 'slate' },
  { emoji: '📣', name: t('fincontrol.data.cat.marketing'), amount: '15 840 000', share: 8,  bar: 20, trend: '↑ +22%',  trendTone: 'red', overspend: true },
  { emoji: '📦', name: t('fincontrol.data.cat.other'),     amount: '7 920 000',  share: 4,  bar: 10, trend: '↓ −8.4%', trendTone: 'green' },
]

export const makeIncomeCategories = (t) => [
  { emoji: '💼', name: t('fincontrol.data.cat.sales'),         amount: '256 000 000', share: 80, bar: 80 },
  { emoji: '🏛', name: t('fincontrol.data.cat.govContracts'), amount: '38 400 000',  share: 12, bar: 12 },
  { emoji: '📈', name: t('fincontrol.data.cat.interest'),      amount: '16 000 000',  share: 5,  bar: 5 },
  { emoji: '📦', name: t('fincontrol.data.cat.others'),        amount: '9 600 000',   share: 3,  bar: 3 },
]

export const makePnlRows = (t) => [
  { type: 'group', label: t('fincontrol.data.pnl.groupRevenue') },
  { label: t('fincontrol.data.pnl.revenue'),             may: '320 000 000', apr: '295 700 000', delta: '+8.2%', deltaTone: 'green', total: true },
  { label: t('fincontrol.data.pnl.salesGoods'),          may: '256 000 000', apr: '238 800 000', delta: '+7.2%', deltaTone: 'green' },
  { label: t('fincontrol.data.pnl.govContracts'),        may: '38 400 000',  apr: '35 200 000',  delta: '+9.1%', deltaTone: 'green' },
  { label: t('fincontrol.data.pnl.interestOther'),       estimated: true, may: '16 000 000', apr: '14 700 000', delta: '+8.8%', deltaTone: 'green' },
  { label: t('fincontrol.data.pnl.otherIncome'),         estimated: true, may: '9 600 000',  apr: '7 000 000',  delta: '+37.1%', deltaTone: 'green' },
  { type: 'group', label: t('fincontrol.data.pnl.groupCogs') },
  { label: t('fincontrol.data.pnl.materials'),           may: '−145 000 000', apr: '−139 000 000', delta: '+4.3%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.directLabor'),         estimated: true, may: '−38 000 000', apr: '−36 400 000', delta: '+4.4%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.prodOverhead'),        estimated: true, may: '−12 000 000', apr: '−11 800 000', delta: '+1.7%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.transportLogistics'),  may: '−3 000 000',  apr: '−2 400 000',  delta: '+25.0%', deltaTone: 'red' },
  { type: 'result', tone: 'green', label: t('fincontrol.data.pnl.grossProfit'), meta: t('fincontrol.data.pnl.metaMargin38'), may: '122 000 000', apr: '106 100 000', delta: '+15.0%', deltaTone: 'green' },
  { type: 'group', label: t('fincontrol.data.pnl.groupOpex') },
  { label: t('fincontrol.data.pnl.payroll'),             may: '−19 000 000', apr: '−18 400 000', delta: '+3.3%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.officeRent'),          may: '−3 800 000',  apr: '−3 800 000',  delta: '0.0%', deltaTone: 'slate' },
  { label: t('fincontrol.data.pnl.marketingAd'),         icon: '📣', warning: t('fincontrol.data.pnl.warnOverspend'), may: '−15 840 000', apr: '−12 960 000', delta: '+22.2%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.depreciation'),        estimated: true, may: '−4 000 000',  apr: '−3 800 000', delta: '+5.3%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.otherOpex'),           estimated: true, may: '−2 360 000',  apr: '−2 100 000', delta: '+12.4%', deltaTone: 'red' },
  { type: 'result', tone: 'blue', label: t('fincontrol.data.pnl.ebit'), meta: t('fincontrol.data.pnl.metaMargin24'), may: '77 000 000', apr: '65 040 000', delta: '+18.4%', deltaTone: 'green' },
  { type: 'group', label: t('fincontrol.data.pnl.groupBelowOp') },
  { label: t('fincontrol.data.pnl.interestExp'),         estimated: true, may: '−3 500 000', apr: '−3 200 000', delta: '+9.4%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.otherFinExp'),         estimated: true, may: '−1 500 000', apr: '−1 200 000', delta: '+25.0%', deltaTone: 'red' },
  { label: t('fincontrol.data.pnl.fxDiff'),              estimated: true, may: '−1 400 000', apr: '+800 000',   delta: '—', deltaTone: 'slate' },
  { type: 'group', label: t('fincontrol.data.pnl.groupTaxes') },
  { label: t('fincontrol.data.pnl.profitTax'),           estimated: true, may: '−6 100 000', apr: '−5 600 000', delta: '+8.9%', deltaTone: 'red' },
  { type: 'result', tone: 'amber', label: t('fincontrol.data.pnl.netProfit'), meta: t('fincontrol.data.pnl.metaNetMargin'), estimated: true, may: '65 000 000', apr: '55 840 000', delta: '+16.4%', deltaTone: 'green' },
]

// Legacy bare exports — resolved once at module load using the current locale.
// Views that import these (rather than the make* factories) won't re-render on
// locale switch; use the make* factories inside a computed() if you need that.
const t = i18n.global.t
export const company = makeCompany(t)
export const accounts = makeAccounts(t)
export const dashboardKpis = makeDashboardKpis(t)
export const monthly = makeMonthly(t)
export const expenseStructure = makeExpenseStructure(t)
export const topCounterpartiesSuppliers = makeTopCounterpartiesSuppliers(t)
export const aiSignals = makeAiSignals(t)
export const transactions = makeTransactions(t)
export const recurring = makeRecurring(t)
export const counterparties = makeCounterparties(t)
export const expenseCategories = makeExpenseCategories(t)
export const incomeCategories = makeIncomeCategories(t)
export const pnlRows = makePnlRows(t)
