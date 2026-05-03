/* global window */
// Fergana CITY (Farg'ona shahri) — verified data adapter for the design canvas.
// Every value below is sourced from a PDF in the local fergana/ folder
// (farstat.uz district-breakdown publications, Jan-Dec 2025 preliminary).
// Folder structure documented in `frontend/src/data/raqamlarda_sources.md`.

// ── Identity ────────────────────────────────────────────────────────────────
const CITY = {
  nameRu:    'Город Фергана',
  nameUz:    'Fargʻona shahri',
  shortRu:   'Фергана',
  shortUz:   'Fargʻona',
  region:    'Ферганская область',
  population: 335_100,                  // 1 yanvar 2026 (verified)
  area:      110,                       // km²
  mahallas:  74,                        // hududlar 2026
  density:   3046,                      // people / km² (computed)
  source:    'farstat.uz',
  period:    'Jan-Dec 2025 (preliminary)',
};

// ── Sector totals 2025 (mlrd soʻm, current prices) ─────────────────────────
// Every sector also has a 5-year history series (2021-2025) and a nominal
// year-on-year growth rate computed from the published series.
const SECTORS = [
  {
    key: 'industry',
    labelRu: 'Промышленность',
    labelUz: 'Sanoat',
    icon: 'factory',
    total2025: 12_666.6,
    history:   [7_075.5, 6_935.4, 10_296.9, 11_303.3, 12_666.6],
    nominalYoY: 112.1,                  // 2025/2024 nominal (current prices)
    regionRealYoY: 107.3,               // viloyat real growth (constant prices)
    sourcePdf: 'fergana/промышленность/10. Tumanlar bo\'yicha sanoat mahsuloti hajmi.pdf',
  },
  {
    key: 'services',
    labelRu: 'Услуги',
    labelUz: 'Xizmatlar',
    icon: 'handyman',
    total2025: 12_191.0,
    history:   [4_387.5, 5_574.6, 6_744.2, 9_299.6, 12_191.0],
    nominalYoY: 131.1,
    regionRealYoY: 108.6,
    sourcePdf: 'fergana/услуги/Hududlar bo\'yicha ko\'rsatilgan xizmatlar hajmi.pdf',
  },
  {
    key: 'investments',
    labelRu: 'Инвестиции в основной капитал',
    labelUz: 'Asosiy kapitalga investitsiyalar',
    icon: 'savings',
    total2025: 7_128.4,
    history:   [3_139.8, 4_077.4, 4_976.4, 5_183.2, 7_128.4],
    nominalYoY: 137.5,
    regionRealYoY: null,                // not published as real growth
    sourcePdf: 'fergana/инвестиции/2.Asosiy kapitalga o\'zlashtirilgan investitsiyalar jami.pdf',
  },
  {
    key: 'trade',
    labelRu: 'Розничный товарооборот',
    labelUz: 'Chakana savdo aylanmasi',
    icon: 'storefront',
    total2025: 6_562.8,
    history:   [2_897.4, 3_603.3, 4_603.2, 5_396.3, 6_562.8],
    nominalYoY: 121.6,
    regionRealYoY: 111.1,               // savdo, yashash va ovqatlanish (subset of services)
    sourcePdf: 'fergana/внутреняя торговля/Farg\'ona viloyati tumanlari bo\'yicha chakana savdo tovar aylanmasi hajmi.pdf',
  },
  {
    key: 'construction',
    labelRu: 'Строительство',
    labelUz: 'Qurilish',
    icon: 'construction',
    total2025: 3_276.6,
    history:   [1_742.5, 2_463.6, 2_928.6, 2_872.2, 3_276.6],
    nominalYoY: 114.1,
    regionRealYoY: 117.4,
    sourcePdf: 'fergana/строительство/Qurilish ishlari (mlrd.so\'m).pdf',
  },
  {
    key: 'agriculture',
    labelRu: 'Сельское хозяйство',
    labelUz: 'Qishloq xoʻjaligi',
    icon: 'agriculture',
    total2025: 1_020.3,
    history:   [587.3, 654.8, 754.6, 833.1, 1_020.3],
    nominalYoY: 122.5,
    regionRealYoY: 105.4,
    sourcePdf: 'fergana/Сельское хозяйство/Qishloq xo\'jaligi mahsuloti (amaldagi narxlarda).pdf',
  },
];

const SECTOR_HISTORY_LABELS = [2021, 2022, 2023, 2024, 2025];

// ── Population & demographics ──────────────────────────────────────────────
const POPULATION = {
  current:  335_100,                    // 1 yanvar 2026
  history: [283_800, 289_000, 293_500, 299_200, 314_500, 321_800, 328_400, 335_100],
  historyLabels: [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
  urbanShare: 100,                      // 100% urban (no rural)
  sourcePdf: 'fergana/демографические_данные/Hududlar bo\'yicha shahar va qishloq aholisi soni.pdf',
};

// 17 age brackets, 1 yanvar 2025 (kishi)
const AGE_GROUPS_2025 = {
  '0-2':   20_784,
  '3-5':   17_391,
  '6-7':    9_615,
  '8-15':  40_235,
  '16-17': 10_515,
  '18-19':  8_374,
  '20-24': 22_037,
  '25-29': 28_537,
  '30-34': 32_224,
  '35-39': 28_005,
  '40-49': 41_543,
  '50-59': 32_395,
  '60-69': 25_517,
  '70-74':  6_073,
  '75-79':  3_312,
  '80-84':    869,
  '85+':      983,
};
// Total: 328 409 (1 yanvar 2025)
// Source: fergana/демографические_данные/Yosh guruhlari bo'yicha doimiy aholi soni-Hududlar.pdf

// ── Vital statistics 2021-2025 ─────────────────────────────────────────────
const VITAL_STATS = {
  births:    [6_291, 6_893, 7_373, 6_871, 6_226],
  deaths:    [1_751, 1_901, 1_740, 1_750, 1_786],
  labels:    [2021,  2022,  2023,  2024,  2025],
  // 2025 detail
  births2025: 6_226,
  deaths2025: 1_786,
  naturalIncrease2025: 4_440,           // 6 226 − 1 786
  birthsBoys2025:  3_189,
  birthsGirls2025: 3_037,
  sourcePdfs: [
    'fergana/демографические_данные/Tug\'ilganlar soni.pdf',
    'fergana/демографические_данные/O\'lganlar soni.pdf',
  ],
};

// ── Housing supply (m² per resident, year-end) ─────────────────────────────
const HOUSING_SUPPLY = {
  current2024: 25.4,                    // m²/person
  history:     [21.8, 23.4, 22.9, 24.2, 25.4],
  historyLabels: [2020, 2021, 2022, 2023, 2024],
  sourcePdf: 'fergana/услуги/Aholining uy-joy bilan ta\'minlanish darajasi.pdf',
};

// ── Region (Fergana viloyat) context — for badges and comparisons ──────────
const REGION_FERGANA = {
  // Foreign trade 2025 (mln USD) — viloyat-only; city slice not published.
  foreignTrade2025: {
    turnoverMlnUsd: 2_668.4,
    exportMlnUsd:   1_082.1,
    importMlnUsd:   1_586.3,
    balanceMlnUsd:   -504.2,
    growthYoY: { turnover: 122.9, exportYoY: 129.4, importYoY: 118.8 },
    sourcePdf: 'fergana/внешнеэкономическая_деятельность/5. Tashqi savdo aylanmasi tarkibi.pdf',
  },
  // Real growth 2025/2024 (constant prices) — useful as context next to nominal city YoY.
  realGrowth2025: {
    grp:           108.1,               // overall
    industry:      107.3,
    construction:  117.4,
    services:      108.6,
    tradeServices: 111.1,               // savdo, yashash va ovqatlanish (subset)
    transport:     117.7,               // tashish va saqlash, axborot va aloqa
    agriculture:   105.4,
    sourcePdf: 'fergana/ВРП/3. Yalpi hududiy mahsulotning o\'sish sur\'atlari.pdf',
  },
  // Auto-transport 2025 (region totals, preliminary)
  autoTransport2025: {
    cargoThsT:        75_869.9,
    cargoMlnTKm:       2_403.9,
    passengersThs:   729_497.3,
    passengerMlnPKm:  16_340.3,
    sourcePdf: 'fergana/услуги/Avtotransportning asosiy ko\'rsatkichlari.pdf',
  },
};

// ── Helpers ────────────────────────────────────────────────────────────────
function fmtNum(n) {
  if (n == null) return '—';
  return n.toLocaleString('ru-RU').replace(/,/g, ' ');
}
function fmtPct(v, sign = true) {
  if (v == null) return '—';
  return (sign && v > 0 ? '+' : '') + v.toFixed(1) + '%';
}
function deltaYoY(pct) {
  if (pct == null) return null;
  return +(pct - 100).toFixed(1);
}
function tone(pct) {
  if (pct == null) return 'na';
  if (pct >= 110) return 'pos-strong';
  if (pct >= 102) return 'pos';
  if (pct >= 99)  return 'neu';
  return 'neg';
}

// ── Expose ─────────────────────────────────────────────────────────────────
window.FerganaCityData = {
  CITY,
  SECTORS,
  SECTOR_HISTORY_LABELS,
  POPULATION,
  AGE_GROUPS_2025,
  VITAL_STATS,
  HOUSING_SUPPLY,
  REGION_FERGANA,
  // helpers
  fmtNum,
  fmtPct,
  deltaYoY,
  tone,
};
