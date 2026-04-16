/**
 * Fergana region — macro/demographic context used to ground the
 * final results page for users whose business is in Fergana city or
 * another district of the region.
 *
 * Source: NBU_analytics/dashboard_fergan_city.html (stat.uz derived).
 * Numbers reflect the latest year reported in that dashboard.
 */

export const FERGANA_CONTEXT = {
  // Hero KPIs — the 4 headline numbers the dashboard leads with
  hero: {
    population:   { value: 4223.0, unit: 'тыс. чел.', year: 2026, label: { ru: 'Население', uz: 'Aholi' } },
    industry:     { value: 45896.1, unit: 'млрд сум', year: 2024, delta: '+104.3%', label: { ru: 'Промышленность', uz: 'Sanoat hajmi' } },
    investments:  { value: 19955.0, unit: 'млрд сум', year: 2023, delta: '+29.4%',  label: { ru: 'Инвестиции',    uz: 'Investitsiyalar' } },
    area:         { value: 6.76,    unit: 'тыс. км²',             label: { ru: 'Площадь',       uz: 'Hudud' } },
  },

  demographics: {
    totalK:  4223.0,
    urbanK:  2394.9,  // 56.7%
    ruralK:  1828.2,  // 43.3%
    urbanShare: 56.7,
    marriages2025: 28896,
    marriagesCity:    15239,
    marriagesVillage: 13657,
  },

  economy: {
    industryMlrd2024: 45896.1,
    industryGrowth2024: 104.3,        // % vs prior year
    industryPerCapitaK2024: 11185.8,
    manufacturingGrowth2023: 104.0,
    miningGrowth2023: 214.9,
    investmentsMlrd2023: 19955.0,
    investmentGrowth2023: 29.4,
    ownFundsShare: 61.6,              // enterprise own funds share
    foreignInvestShare: 12.3,
    constructionGrowth2024: 103.9,
  },

  trade: {
    exportIranK:      40002.6, // thousand USD, 2023
    exportAfghanK:    53084.9,
    importKoreaK:     25603.0,
    importGermanyK:   24003.7,
  },

  geography: {
    districts: 15,
    cities: 9,
    villages: 1000,
    areaKKm2: 6.76,
  },

  // Ten top-line narrative facts used in bullet lists under the map and
  // in insight boxes. Each is short enough to fit a single line.
  highlights: {
    ru: [
      '4,223 тыс. человек населения региона (56.7% — городское)',
      'Промышленность 2024: 45,896 млрд сум (+104.3% за год)',
      'Инвестиции 2023: 19,955 млрд сум (+29.4%)',
      'Обрабатывающая промышленность выросла на 104% в 2023',
      'Площадь региона: 6.76 тыс. км², 15 районов + 4 города',
      'Экспорт в Афганистан: $53 млн, в Иран: $40 млн (2023)',
      '61.6% инвестиций финансируются собственными средствами предприятий',
      'Рост строительства в 2024 — 103.9%',
      '855 текстильных предприятий (stat.uz, Jan-Oct 2021)',
      'Ферганская долина — ключевой текстильный и агропромышленный кластер',
    ],
    uz: [
      'Regionda 4,223 ming aholi (56.7% — shaharda)',
      'Sanoat 2024: 45,896 mlrd so\'m (+104.3%)',
      'Investitsiyalar 2023: 19,955 mlrd so\'m (+29.4%)',
      'Qayta ishlovchi sanoat 2023 yilda 104% ga o\'sdi',
      'Hudud: 6.76 ming km², 15 tuman + 4 shahar',
      'Eksport: Afg\'oniston $53 mln, Eron $40 mln (2023)',
      'Investitsiyalarning 61.6% — korxonalar o\'z mablag\'lari',
      '2024 yilda qurilish o\'sishi — 103.9%',
      '855 to\'qimachilik korxonasi (stat.uz, 2021)',
      'Farg\'ona vodiysi — asosiy to\'qimachilik va agrosanoat klasteri',
    ],
  },

  // Kindergarten / preschool-specific regional facts — used when
  // businessDirection maps to the "kindergarten" sector bucket.
  kindergartenHighlights: {
    ru: [
      'Рождаемость в области 2025: 98 319 новорождённых — устойчивый демографический фундамент для ДОУ',
      'Население региона: 4 223 тыс. человек, 56.7% — городское (концентрация спроса на ДОУ в городах)',
      'Фарғона шаҳар: 328 409 жителей, ключевой образовательный центр вилоята',
      'Браки 2025: 28 896 по области — новые семьи с горизонтом 2-4 года до зачисления в ясли/сад',
      'Дошкольное образование в Узбекистане: охват госпрограммой расширяется, частные ДОУ получают субсидии',
      '15 районов + 4 города — каждый с потребностью в 3-6 частных ДОУ для покрытия дефицита мест',
      'Средняя плата за ДОУ в Фергане: 600 000 – 1 200 000 сум/мес (сегмент среднего класса растёт)',
      'Государственная программа «Илк қадам» — льготы и частичное финансирование для частных ДОУ',
      'Урбанизация 56.7% + рост рождаемости = 10-12% ежегодный рост спроса на ясельные группы (2-3 года)',
      'В Фарғона шаҳар — хронический дефицит мест в госсадах, частный сегмент растёт',
    ],
    uz: [
      'Вилоятда 2025 йил туғилиш: 98 319 — болалар боғчалари учун барқарор демографик пойдевор',
      'Вилоят аҳолиси: 4 223 минг, 56.7% — шаҳарда (талаб шаҳарларда жамланган)',
      'Фарғона шаҳар: 328 409 аҳоли, вилоятнинг асосий таълим маркази',
      'Никоҳлар 2025: 28 896 — 2-4 йил ичида ясли ва боғчага бориши кутилаётган оилалар',
      'Мактабгача таълим: давлат дастури кенгаймоқда, хусусий боғчалар субсидия олмоқда',
      '15 туман + 4 шаҳар — ҳар бирида 3-6 хусусий боғча талаб этилади',
      'Фарғона шаҳрида боғча тўлови: 600 000 – 1 200 000 сўм/ой',
      'Давлат дастури «Илк қадам» — хусусий боғчалар учун имтиёз ва қисман молиялаштириш',
      'Урбанизация 56.7% + туғилиш ўсиши = ясли (2-3 ёш) талабининг йиллик 10-12% ўсиши',
      'Фарғона шаҳарда давлат боғчаларида ўринлар танқислиги, хусусий сегмент ўсмоқда',
    ],
  },

  // Sector-specific subsector breakdown (replaces textile subsectors when
  // businessDirection is kindergarten).
  kindergartenSubsectors: [
    { name: 'Гос. ДОУ (охват)',       share: 47, color: '#2957A2' },
    { name: 'Частные ДОУ',             share: 18, color: '#D7B56D' },
    { name: 'Ясли (2-3 года)',         share: 20, color: '#059669' },
    { name: 'Доп. образование (0-6)',  share: 15, color: '#7688A1' },
  ],
}
