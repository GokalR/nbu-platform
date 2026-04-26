// All numerical values are verified from stat.uz (National Statistics Committee
// of Uzbekistan) or marked null when stat.uz has not published a verified
// 2025 figure. The home view renders "no data" / "нет данных" / "maʻlumot yoʻq"
// for nulls.
//
// Sources:
// - Population (1 Oct 2025): stat.uz press release "Qaysi hudud aholisi eng koʻp?"
//   https://stat.uz/en/press-center/news-of-committee/64960-...
// - National GDP +7.7% (full-year 2025): stat.uz press release 27 Jan 2026
//   https://stat.uz/en/press-center/news-of-committee/66556-...
// - Regional GDP growth 2025 (top 4 / bottom 3 only published):
//   https://oz.sputniknews.uz/20260311/yaim-osish-uzbekistan-etakchi-hudud-...
// - National exports 2025 ($33.8 bn): https://www.gazeta.uz/oz/2026/01/29/trade-2025/
// - Per-region 2025 export breakdown was not published — set to null.
// - Per-region industry/agri/services dollar breakdowns were not published —
//   stat cards fall back to "no data" except for Samarqand which has the
//   verified Excel block from the regional statistics committee.
// - Districts, cities and mahalla counts: фото таблицы hududlar (2026 г.).

export const regions = {
  karakalpakstan: {
    population: '2.05 mln',
    populationRaw: 2.05,
    districts: 17,
    area: '166,590 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: null,
    mahallas: 452,
  },
  khorezm: {
    population: '2.06 mln',
    populationRaw: 2.06,
    districts: 13,
    area: '6,464 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: null,
    mahallas: 509,
  },
  navoiy: {
    population: '1.19 mln',
    populationRaw: 1.19,
    districts: 11,
    area: '110,990 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: null,
    mahallas: 313,
  },
  bukhara: {
    population: '2.10 mln',
    populationRaw: 2.10,
    districts: 13,
    area: '40,328 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: null,
    mahallas: 516,
  },
  // Samarkand: verified from stat.uz Excel exports (Самарқанд вил ПРОМП, 2025).
  samarqand: {
    population: '4.36 mln',
    populationRaw: 4.36,
    districts: 16,
    area: '16,770 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: '$1.15 mlrd',
    mahallas: 1063,
    verified: {
      // Production volumes 2025, mlrd UZS — from "ПРОМТ қўшимча Самарқанд вилоят (3).xlsx"
      economic: [
        { labelKey: 'home.cards.industry',    value: '57.8 trln', percent: 74 },
        { labelKey: 'home.cards.agriculture', value: '60.8 trln', percent: 78 },
        { labelKey: 'home.cards.services',    value: '78.2 trln', percent: 100 },
      ],
      // Labor market 2025, K people — total employed 1 611.7 K (formal+informal).
      population: [
        { labelKey: 'home.cards.employed',     value: '1.6 mln', percent: 96 },
        { labelKey: 'home.cards.selfEmployed', value: null,      percent: 0 },
        { labelKey: 'home.cards.education',    value: null,      percent: 0 },
      ],
      // Banking 2025 — credit coverage of employed 73%, opened businesses 6 564, exporter coverage 26%.
      bank: [
        { labelKey: 'home.cards.credits',     value: '73%',      percent: 73 },
        { labelKey: 'home.cards.newBusiness', value: '6 564 ta', percent: 65 },
        { labelKey: 'home.cards.exporters',   value: '26%',      percent: 26 },
      ],
    },
  },
  qashqadaryo: {
    population: '3.70 mln',
    populationRaw: 3.70,
    districts: 16,
    area: '28,568 km²',
    status: 'active',
    gdpGrowth: '6.8%',
    gdpDelta: '+6.8%',
    exports: null,
    mahallas: 776,
  },
  surxondaryo: {
    population: '2.99 mln',
    populationRaw: 2.99,
    districts: 15,
    area: '20,099 km²',
    status: 'active',
    gdpGrowth: '6.6%',
    gdpDelta: '+6.6%',
    exports: null,
    mahallas: 723,
  },
  jizzax: {
    population: '1.56 mln',
    populationRaw: 1.56,
    districts: 13,
    area: '21,179 km²',
    status: 'active',
    gdpGrowth: '8.2%',
    gdpDelta: '+8.2%',
    exports: null,
    mahallas: 304,
  },
  sirdaryo: {
    population: '0.94 mln',
    populationRaw: 0.94,
    districts: 11,
    area: '4,276 km²',
    status: 'active',
    gdpGrowth: '9.8%',
    gdpDelta: '+9.8%',
    exports: null,
    mahallas: 221,
  },
  tashkent_region: {
    population: '3.15 mln',
    populationRaw: 3.15,
    districts: 22,
    area: '15,258 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: null,
    mahallas: 883,
  },
  tashkent_city: {
    population: '3.16 mln',
    populationRaw: 3.16,
    districts: 12,
    area: '335 km²',
    status: 'active',
    gdpGrowth: '11.3%',
    gdpDelta: '+11.3%',
    exports: null,
    mahallas: 585,
  },
  namangan: {
    population: '3.18 mln',
    populationRaw: 3.18,
    districts: 14,
    area: '7,440 km²',
    status: 'active',
    gdpGrowth: '8.2%',
    gdpDelta: '+8.2%',
    exports: null,
    mahallas: 754,
  },
  andijan: {
    population: '3.51 mln',
    populationRaw: 3.51,
    districts: 16,
    area: '4,303 km²',
    status: 'active',
    gdpGrowth: '6.8%',
    gdpDelta: '+6.8%',
    exports: null,
    mahallas: 879,
  },
  fergana: {
    population: '4.20 mln',
    populationRaw: 4.20,
    districts: 19,
    cities: 4,
    area: '6,760 km²',
    status: 'active',
    gdpGrowth: null,
    gdpDelta: null,
    exports: null,
    mahallas: 1017,
  },
}

// Main specialization / "best for" per region.
// `icon` is a Material Symbols name. Tag + bullets are rendered via i18n
// (specializations.tags.<key>, specializations.bullets.<key>).
export const regionSpecializations = {
  karakalpakstan: { icon: 'agriculture' },
  khorezm: { icon: 'museum' },
  navoiy: { icon: 'diamond' },
  bukhara: { icon: 'mosque' },
  samarqand: { icon: 'account_balance' },
  qashqadaryo: { icon: 'bolt' },
  surxondaryo: { icon: 'nutrition' },
  jizzax: { icon: 'local_shipping' },
  sirdaryo: { icon: 'electric_bolt' },
  tashkent_region: { icon: 'factory' },
  tashkent_city: { icon: 'business_center' },
  namangan: { icon: 'checkroom' },
  andijan: { icon: 'directions_car' },
  fergana: { icon: 'oil_barrel' },
}

export const regionKeys = Object.keys(regions)

// National total — used when no region is selected.
// Population (1 Oct 2025): 38.07 mln. GDP 2025: 1 849.7 trln UZS, +7.7%.
// Exports 2025: $33.8 bn (gazeta.uz citing stat.uz, Jan 2026).
// 208 районов/городов, 8 998 махалля (источник: таблица hududlar, 2026 г.).
export const national = {
  population: '38.07 mln',
  gdpGrowth: '7.7%',
  gdpDelta: '+7.7%',
  exports: '$33.8 mlrd',
  districts: 208,
  mahallas: 8998,
}
