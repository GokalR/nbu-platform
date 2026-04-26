// All numerical values in `raqamlarda` blocks are verified from stat.uz
// (National Statistics Committee of Uzbekistan) or its regional branches.
// Values shown as null mean stat.uz has not published a verified figure for
// that metric/period; the home view renders "no data" / "нет данных" /
// "maʻlumot yoʻq" for nulls.
//
// `raqamlarda.period` indicates the comparison period and matches what the
// regional stat office currently displays on its landing page:
//   '2025'    — January-December 2025 vs January-December 2024 (full year)
//   '2026Q1'  — January-March 2026 vs January-March 2025 (latest quarter)
// Some regions have already rolled forward to Q1 2026 on their public site.
//
// Sources:
// - Uzbekistan total: stat.uz infographic "Oʻzbekiston raqamlarda" (Jan-Dec 2025)
// - Per-region data: regional stat-office landing pages
//   (qrstat.uz, xorazmstat.uz, navstat.uz, buxstat.uz, samstat.uz, qashstat.uz,
//    surxonstat.uz, jizzaxstat.uz, sirstat.uz, toshvilstat.uz, toshstat.uz,
//    namstat.uz, andstat.uz, farstat.uz)
// - Per-region counts:
//     `districts` — rayons (туманов), excluding cities of regional rank.
//     `cities`    — cities of regional rank (шаҳарлар), separate from rayons.
//     `mahallas`  — total mahallas.
//   The hududlar 2026 photo only lists the combined count (туман+шаҳар сони);
//   the rayon/city split was filled from canonical Uzbekistan administrative
//   division references.

export const regions = {
  karakalpakstan: {
    population: '2.06 mln',
    populationRaw: 2.06,
    districts: 16,
    cities: 1,
    area: '166,590 km²',
    mahallas: 452,
    status: 'active',
    raqamlarda: {
      period: '2026Q1',
      grp: 112.9,
      industry: 107.4,
      agriculture: 102.4,
      investment: 123.8,
      construction: 176.0,
      freight: 100.4,
      passenger: 104.6,
      retail: 135.1,
      services: 116.6,
      populationCount: 2057730,
      populationDate: '2026-04-01',
    },
  },
  khorezm: {
    population: '2.08 mln',
    populationRaw: 2.08,
    districts: 11,
    cities: 2,
    area: '6,464 km²',
    mahallas: 509,
    status: 'active',
    raqamlarda: {
      period: '2026Q1',
      grp: 110.6,
      industry: 108.1,
      agriculture: 105.0,
      investment: 143.3,
      construction: 128.4,
      freight: 109.7,
      passenger: 103.4,
      retail: 139.8,
      services: 117.0,
      populationCount: 2075044,
      populationDate: '2026-04-01',
    },
  },
  navoiy: {
    population: '1.19 mln',
    populationRaw: 1.19,
    districts: 8,
    cities: 3,
    area: '110,990 km²',
    mahallas: 313,
    status: 'active',
    // navstat.uz landing page returned ECONNREFUSED — no verified raqamlarda yet.
    raqamlarda: {
      period: null,
      grp: null,
      industry: null,
      agriculture: null,
      investment: null,
      construction: null,
      freight: null,
      passenger: null,
      retail: null,
      services: null,
      populationCount: null,
      populationDate: null,
    },
  },
  bukhara: {
    population: '2.11 mln',
    populationRaw: 2.11,
    districts: 11,
    cities: 2,
    area: '40,328 km²',
    mahallas: 516,
    status: 'active',
    raqamlarda: {
      period: '2025',
      grp: 107.2,
      industry: 107.1,
      agriculture: 104.3,
      investment: 80.6,
      construction: 111.3,
      freight: 102.6,
      passenger: 101.2,
      retail: 109.2,
      services: 114.0,
      populationCount: 2107035,
      populationDate: null,
      populationCaption: 'currentCount',
    },
  },
  samarqand: {
    population: '4.38 mln',
    populationRaw: 4.38,
    districts: 14,
    cities: 2,
    area: '16,770 km²',
    mahallas: 1063,
    status: 'active',
    raqamlarda: {
      period: '2025',
      grp: 108.0,
      industry: 108.5,
      agriculture: 103.3,
      investment: 125.6,
      construction: 117.3,
      freight: 119.5,
      passenger: 113.1,
      retail: 110.3,
      services: 115.9,
      populationCount: 4379791,
      populationDate: '2026-01-01',
    },
  },
  qashqadaryo: {
    population: '3.72 mln',
    populationRaw: 3.72,
    districts: 14,
    cities: 2,
    area: '28,568 km²',
    mahallas: 776,
    status: 'active',
    // qashstat.uz "Qashqadaryo viloyati raqamlarda" infographic (Jan-Dec 2025).
    raqamlarda: {
      period: '2025',
      grp: 106.8,
      industry: 107.2,
      agriculture: 104.3,
      investment: 106.9,
      construction: 110.8,
      freight: 104.8,
      passenger: 103.2,
      retail: 108.6,
      services: 113.6,
      populationCount: 3716949,
      populationDate: '2026-01-01',
    },
  },
  surxondaryo: {
    population: '3.02 mln',
    populationRaw: 3.02,
    districts: 14,
    cities: 1,
    area: '20,099 km²',
    mahallas: 723,
    status: 'active',
    raqamlarda: {
      period: '2026Q1',
      grp: 109.1,
      industry: 108.7,
      agriculture: 109.7,
      investment: 120.6,
      construction: 110.0,
      freight: 110.8,
      passenger: 104.2,
      retail: 123.1,
      services: 116.3,
      populationCount: 3024871,
      populationDate: '2026-04-01',
    },
  },
  jizzax: {
    population: '1.57 mln',
    populationRaw: 1.57,
    districts: 12,
    cities: 1,
    area: '21,179 km²',
    mahallas: 304,
    status: 'active',
    raqamlarda: {
      period: '2025',
      grp: 106.1,
      industry: 114.3,
      agriculture: 104.4,
      investment: 100.8,
      construction: 120.4,
      freight: 105.0,
      passenger: 101.2,
      retail: 108.6,
      services: 114.7,
      populationCount: 1566885,
      populationDate: null,
      populationCaption: 'currentCount',
    },
  },
  sirdaryo: {
    population: '0.95 mln',
    populationRaw: 0.95,
    districts: 9,
    cities: 2,
    area: '4,276 km²',
    mahallas: 221,
    status: 'active',
    raqamlarda: {
      period: '2026Q1',
      grp: 108.8,
      industry: 108.9,
      agriculture: 107.8,
      investment: 86.0,
      construction: 115.6,
      freight: 112.0,
      passenger: 104.4,
      retail: 107.3,
      services: 115.2,
      populationCount: 949559,
      populationDate: '2026-04-01',
    },
  },
  tashkent_region: {
    population: '3.16 mln',
    populationRaw: 3.16,
    districts: 15,
    cities: 7,
    area: '15,258 km²',
    mahallas: 883,
    status: 'active',
    raqamlarda: {
      period: '2025',
      grp: 107.2,
      industry: 106.6,
      agriculture: 104.2,
      investment: 101.4,
      construction: 109.8,
      freight: 109.1,
      passenger: 102.2,
      retail: 110.6,
      services: 115.2,
      populationCount: 3160671,
      populationDate: null,
      populationCaption: 'currentCount',
    },
  },
  tashkent_city: {
    population: '3.18 mln',
    populationRaw: 3.18,
    districts: 12,
    area: '335 km²',
    mahallas: 585,
    status: 'active',
    // toshstat.uz infographic — Jan-Dec 2025. The city bulletin replaces the
    // agriculture tile with foreign trade turnover (`tashqi_savdo`).
    raqamlarda: {
      period: '2025',
      grp: 111.3,
      industry: 107.3,
      agriculture: null,
      tashqi_savdo: 115.3,
      investment: 108.2,
      construction: 118.3,
      freight: 106.4,
      passenger: 108.7,
      retail: 113.9,
      services: 117.7,
      populationCount: 3178144,
      populationDate: '2025-01-01',
    },
  },
  namangan: {
    population: '3.20 mln',
    populationRaw: 3.20,
    districts: 11,
    cities: 3,
    area: '7,440 km²',
    mahallas: 754,
    status: 'active',
    raqamlarda: {
      period: '2026Q1',
      grp: 108.8,
      industry: 108.8,
      agriculture: 104.6,
      investment: 137.0,
      construction: 116.1,
      freight: 111.0,
      passenger: 105.0,
      retail: 128.8,
      services: 115.2,
      populationCount: 3202700,
      populationDate: '2026-04-01',
    },
  },
  andijan: {
    population: '3.51 mln',
    populationRaw: 3.51,
    districts: 14,
    cities: 2,
    area: '4,303 km²',
    mahallas: 879,
    status: 'active',
    // andstat.uz landing page returned HTTP 500 — only headline GRP growth
    // verified from stat.uz top-regions release (6.8% / 106.8%, Jan-Dec 2025).
    raqamlarda: {
      period: '2025',
      grp: 106.8,
      industry: null,
      agriculture: null,
      investment: null,
      construction: null,
      freight: null,
      passenger: null,
      retail: null,
      services: null,
      populationCount: null,
      populationDate: null,
    },
  },
  fergana: {
    population: '4.22 mln',
    populationRaw: 4.22,
    districts: 15,
    cities: 4,
    area: '6,760 km²',
    mahallas: 1017,
    status: 'active',
    // farstat.uz infographic — Jan-Dec 2025 (user-supplied screenshot).
    raqamlarda: {
      period: '2025',
      grp: 108.1,
      industry: 107.3,
      agriculture: 105.6,
      investment: 145.2,
      construction: 117.5,
      freight: 107.3,
      passenger: 101.4,
      retail: 112.1,
      services: 114.4,
      populationCount: 4223044,
      populationDate: '2026-01-01',
    },
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

// Source attribution per region: which website the `raqamlarda` data was
// fetched from. Used by the home view to render a transparent footer like
// "Источник: samstat.uz (январь–декабрь 2025 г.)".
//   `site`   — domain of the regional stat office (or `stat.uz` fallback)
//   `note`   — null when full bulletin was published; short tag when the
//              source was unreachable or only published headline numbers.
export const regionSources = {
  karakalpakstan: { site: 'qrstat.uz', note: null },
  khorezm: { site: 'xorazmstat.uz', note: null },
  navoiy: { site: 'navstat.uz', note: 'unreachable' },
  bukhara: { site: 'buxstat.uz', note: null },
  samarqand: { site: 'samstat.uz', note: null },
  qashqadaryo: { site: 'qashstat.uz', note: null },
  surxondaryo: { site: 'surxonstat.uz', note: null },
  jizzax: { site: 'jizzaxstat.uz', note: null },
  sirdaryo: { site: 'sirstat.uz', note: null },
  tashkent_region: { site: 'toshvilstat.uz', note: null },
  tashkent_city: { site: 'toshstat.uz', note: null },
  namangan: { site: 'namstat.uz', note: null },
  andijan: { site: 'stat.uz', note: 'headlineOnly' },
  fergana: { site: 'farstat.uz', note: null },
}

export const nationalSource = { site: 'stat.uz', note: null }

export const regionKeys = Object.keys(regions)

// National total — stat.uz "Oʻzbekiston raqamlarda" (Jan-Dec 2025) infographic.
// Hududlar 2026 reports 208 туманов+шаҳаров total and 8 998 махалля. The
// 208 splits as 176 туманов (164 across viloyats + 12 within Tashkent city)
// and 32 шаҳаров of regional rank.
export const national = {
  population: '38.24 mln',
  populationRaw: 38.24,
  districts: 176,
  cities: 32,
  area: '448,978 km²',
  mahallas: 8998,
  raqamlarda: {
    period: '2025',
    grp: 107.7,
    industry: 106.8,
    agriculture: 104.4,
    investment: 110.5,
    construction: 114.2,
    freight: 101.9,
    passenger: 105.8,
    retail: 111.2,
    services: 114.7,
    populationCount: 38236704,
    populationDate: '2026-01-01',
  },
}
