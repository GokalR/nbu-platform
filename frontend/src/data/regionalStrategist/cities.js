// Реальные данные по пилотным городам.
// Источники: farstat.uz (Фергана, 2010–2025), NBU Data Office (Маргилан, март 2026).
// Файлы: NBU_analytics/dashboard_fergan_city.html · DASHBOARD_margilan_city.html

// kpi.value — число; label — подпись; hint — единица/контекст; tone — positive|neutral|warn
// sectors — структура экономики в процентах ВТП (валовой территориальный продукт)
// industries — крупнейшие отрасли обрабатывающей промышленности, млрд сум
// strengths / challenges — что учитывает рекомендательный движок

export const CITIES = {
  fergana: {
    id: 'fergana',
    kind: 'province', // весь регион Ферганской области — для общих выводов
    nameKey: 'cities.fergana',
    name: { ru: 'Ferganskaya oblast', uz: 'Farg'ona viloyati' },
    capital: { ru: 'g. Fergana', uz: 'Farg'ona sh.' },
    dataYear: 2025,
    populationK: 4223.0,
    areaKm2: 6760,
    districts: 19, // 4 города + 15 туманов
    mahallas: 1248,
    industryBlnUzs: 45896.1, // 2024
    industryGrowthPct: 104.3,
    industryPerCapitaK: 11185.8, // ×4 к Маргилану
    investmentsBlnUzs: 19955.0, // 2023
    investmentsGrowthPct: 29.4,
    exportsTopPartners: [
      { country: { ru: 'Afganistan', uz: 'Afg'oniston' }, usdK: 53084.9, trend: 14.6 },
      { country: { ru: 'Iran', uz: 'Eron' }, usdK: 40002.6, trend: 82.1 },
      { country: { ru: 'Belarus', uz: 'Belarus' }, usdK: 5884.4, trend: 28.7 },
    ],
    importsTopPartners: [
      { country: { ru: 'Koreya', uz: 'Koreya' }, usdK: 25603.0, trend: -15.5 },
      { country: { ru: 'Germaniya', uz: 'Germaniya' }, usdK: 24003.7, trend: 21.9 },
      { country: { ru: 'Indiya', uz: 'Hindiston' }, usdK: 24324.5, trend: -27.8 },
    ],
    industries: [
      { key: 'textiles', nameRu: 'Текстиль', nameUz: 'Тўқимачилик', blnUzs: 12338.1 },
      { key: 'chemicals', nameRu: 'Химия', nameUz: 'Кимё', blnUzs: 5354.4 },
      { key: 'clothing', nameRu: 'Одежда', nameUz: 'Кийим', blnUzs: 2841.3 },
      { key: 'oilRefining', nameRu: 'Нефтепереработка', nameUz: 'Нефть қайта ишлаш', blnUzs: 2290.9 },
      { key: 'food', nameRu: 'Пищевая', nameUz: 'Озиқ-овқат', blnUzs: 2061.2 },
      { key: 'leather', nameRu: 'Кожа и изделия', nameUz: 'Тери маҳсулотлари', blnUzs: 1338.3 },
    ],
    topIndustrialDistricts: [
      { key: 'fergana_city', nameRu: 'Фергана (г.)', nameUz: 'Фарғона ш.', sharePct: 24.6, blnUzs: 8587.4 },
      { key: 'qoqon_city', nameRu: 'Коканд (г.)', nameUz: 'Қўқон ш.', sharePct: 13.6, blnUzs: 1880.3 },
      { key: 'uchkoprik', nameRu: 'Учкоприк', nameUz: 'Учкўприк', sharePct: 8.8, blnUzs: 3143.6 },
      { key: 'qoshtepa', nameRu: 'Кўштепа', nameUz: 'Қўштепа', sharePct: 6.3, blnUzs: 2390.8 },
    ],
    strengths: {
      ru: [
        'Крупнейшая промышленная база региона (45,9 трлн сум)',
        'Развитый текстильный и химический кластер',
        'Растущий экспорт в Афганистан и Иран',
        'Плотная сеть из 4 городов + 15 туманов — широкий рынок сбыта',
      ],
      uz: [
        'Mintaqaning eng yirik sanoat bazasi (45,9 trln so'm)',
        'Rivojlangan to'qimachilik va kimyo klasteri',
        'Afg'oniston va Eronga eksportning o'sishi',
        '4 shahar + 15 tuman — keng bozor',
      ],
    },
    challenges: {
      ru: [
        'Неравномерное распределение — 4,9% vs 24,6% между туманами',
        'Зависимость от импорта сырья из Кореи и Индии',
        'Сох — всего 0,33% в промышленности региона',
      ],
      uz: [
        'Notekis taqsimot — tumanlar o'rtasida 4,9% dan 24,6% gacha',
        'Koreya va Hindistondan xomashyoga bog'liqlik',
        'So'x — viloyat sanoatining bor-yo'g'i 0,33%',
      ],
    },
    recommendedSectors: ['textiles', 'food', 'services', 'agriculture'],
  },

  margilan: {
    id: 'margilan',
    kind: 'city',
    nameKey: 'cities.margilan',
    name: { ru: 'Margilan', uz: 'Marg'ilon' },
    province: { ru: 'Ferganskaya obl.', uz: 'Farg'ona vil.' },
    dataYear: 2025,
    populationK: 261.9,
    areaKm2: 52,
    densityPerKm2: 5035,
    mahallas: 50,
    households: 46580,
    youthSharePct: 54,
    industryBlnUzs: 2459, // 2025
    industryGrowthPct: 71, // за 4 года
    industryShareOfProvincePct: 4.9,
    industryPerCapitaK: 9461, // vs 38187 у г. Фергана
    smeSharePct: 97,
    exportsBlnUzs: 450, // 2025 рекорд
    exportsGrowthPct: 202,
    investmentsBlnUzs: 1281,
    investmentsGrowthPct: 83,
    avgSalaryKUzs: 3974, // в месяц
    avgSalaryMigrantsKUzs: 7700, // медиана за рубежом
    tourismPerYear: 380000,
    tourismObjects: 42,
    unemploymentPct: 5.8,
    activeEnterprises: 2787,
    activeIp: 7143,
    ipActiveSharePct: 46.4,
    ipSuspendedSharePct: 43.1,
    nplPct: 4.6,
    economyStructure: [
      { key: 'retail', nameRu: 'Розница и опт', nameUz: 'Чакана ва улгуржи', pct: 38.2, tag: '№1' },
      { key: 'services', nameRu: 'Услуги и туризм', nameUz: 'Хизматлар ва туризм', pct: 23.8, tag: '+107%' },
      { key: 'industry', nameRu: 'Промышленность', nameUz: 'Саноат', pct: 19.4, tag: 'слабо' },
      { key: 'construction', nameRu: 'Строительство', nameUz: 'Қурилиш', pct: 12.1 },
      { key: 'other', nameRu: 'Прочее', nameUz: 'Бошқа', pct: 6.5 },
    ],
    topSectors: [
      { key: 'food', nameRu: 'Пищевая (562 активных)', nameUz: 'Озиқ-овқат (562)', blnUzs: 471 },
      { key: 'textiles', nameRu: 'Текстиль (ручное + атлас)', nameUz: 'Тўқимачилик (атлас)', blnUzs: 394 },
      { key: 'shoes', nameRu: 'Обувь', nameUz: 'Пойабзал', blnUzs: 257 },
      { key: 'construction_mat', nameRu: 'Стройматериалы', nameUz: 'Қурилиш ашёлари', blnUzs: 104 },
      { key: 'furniture', nameRu: 'Мебель', nameUz: 'Мебел', blnUzs: 44 },
    ],
    creditPlan2026BlnUzs: 1500, // ×5,6 к 2025
    creditPlan2026Jobs: 3614,
    strengths: {
      ru: [
        'Рекордный экспорт 450 млрд сум (+202%) — атлас, трикотаж, фрукты',
        'Туризм: 380 тыс. гостей в год, 42 объекта',
        '97% экономики — МСБ, низкий порог входа',
        'План NBU: 1,5 трлн сум новых кредитов (×5,6) и 3 614 рабочих мест',
      ],
      uz: [
        'Rekord eksport 450 mlrd so'm (+202%) — atlas, trikotaj, mevalar',
        'Turizm: yiliga 380 ming mehmon, 42 ob'ekt',
        '97% iqtisodiyot — MSB, kirish to'sig'i past',
        'NBU rejasi: 1,5 trln so'm yangi kreditlar (×5,6) va 3 614 ish o'rni',
      ],
    },
    challenges: {
      ru: [
        'Миграционный кризис: 15,6 тыс. за рубежом, 76% — ради заработка',
        '43,1% ИП в приостановке — низкая рентабельность розницы',
        'Промпроизводство на душу в 4× ниже Ферганы (9,5 тыс. vs 38,2 тыс. сум)',
        '«Спящий» бизнес + теневая экономика ~37% активности',
      ],
      uz: [
        'Migratsiya: 15,6 ming chet elda, 76% — ish uchun',
        '43,1% YaTT to'xtatilgan — chakana past rentabellik',
        'Jon boshiga sanoat Farg'onadan 4× past (9,5 vs 38,2 ming so'm)',
        '«Uxlab yotgan» biznes + ~37% norasmiy faoliyat',
      ],
    },
    recommendedSectors: ['textiles', 'services', 'food', 'tourism'],
  },
}

export const CITY_LIST = Object.values(CITIES)

export const getCity = (id) => CITIES[id] ?? null

// Сколько реальных пилотных городов у платформы сейчас (для hero stats).
export const CITY_COUNT = CITY_LIST.length

// Сколько реальных кредитных продуктов NBU (см. credit-products.js)
export { CREDIT_TOTAL } from './credit-products'
