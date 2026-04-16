/**
 * Key verified textile enterprises in Fergana region.
 * Ported from NBU-business-analysis/lib/fergana-enterprises.ts
 */
export const KEY_ENTERPRISES = [
  {
    name: 'Маргиланская шёлковая фабрика',
    district: 'Марғилон',
    districtId: 'margilon',
    type: 'production',
    workers: 15_000,
    detail: '22 млн м² шёлка в год. Крупнейшее текстильное предприятие региона.',
    source: 'central-asia.guide',
  },
  {
    name: 'Yodgorlik Silk Factory',
    district: 'Марғилон',
    districtId: 'margilon',
    type: 'craft',
    workers: 2_000,
    detail: 'Традиционное производство хан-атласа и адраса ручным способом. 250 000 м² шёлка в год.',
    source: 'britannica.com, advantour.com',
  },
  {
    name: 'Global Textile LLC',
    district: 'Фарғона',
    districtId: 'fargona',
    type: 'production',
    workers: 5_000,
    detail: '62 000 т трикотажа в год. Контракт с французской сетью Kiabi.',
    source: 'gov.uz',
  },
  {
    name: 'Innovative Apparel',
    district: 'Қўштепа',
    districtId: 'qoshtepa',
    type: 'fdi',
    workers: 3_500,
    detail: '$15 млн FDI (Шри-Ланка). Контракт с H&M. Запуск — август 2025.',
    source: 'trend.az, kursiv.media',
  },
  {
    name: 'Маргиланский центр ремёсел',
    district: 'Марғилон',
    districtId: 'margilon',
    type: 'craft',
    workers: 600,
    detail: '200+ видов атласа и адраса, ковры, швейные изделия.',
    source: 'uzbekistan.travel',
  },
]

export const SUBSECTORS = [
  { name: 'Шёлк (атлас, адрас)',  share: 28, color: '#059669' },
  { name: 'Трикотаж и одежда',     share: 35, color: '#2957A2' },
  { name: 'Хлопкопереработка',     share: 22, color: '#D7B56D' },
  { name: 'Ковры и домтекстиль',   share: 15, color: '#7688A1' },
]
