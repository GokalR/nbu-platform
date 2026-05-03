/* global window */
// Data adapter — exposes regions data globally + helpers

// Re-export the user's data file via dynamic load. We mirror it inline so the
// design canvas works without ES modules.

const REGION_DATA = {
  fergana: {
    nameRu: 'Ферганская область',
    shortRu: 'Фергана',
    population: '4.22 mln',
    populationRaw: 4.22,
    districts: 19,
    cities: 4,
    area: '6,760 km²',
    mahallas: 1017,
    raqamlarda: {
      period: '2025',
      grp: 108.1, industry: 107.3, agriculture: 105.6, investment: 145.2,
      construction: 117.5, freight: 107.3, passenger: 101.4, retail: 112.1,
      services: 114.4,
      populationCount: 4223044,
      populationDate: '2026-01-01',
    },
    source: 'farstat.uz',
  },
  samarqand: {
    nameRu: 'Самаркандская область', shortRu: 'Самарканд',
    population: '4.38 mln', populationRaw: 4.38, districts: 16,
    area: '16,770 km²', mahallas: 1063,
    raqamlarda: {
      period: '2025',
      grp: 108.0, industry: 108.5, agriculture: 103.3, investment: 125.6,
      construction: 117.3, freight: 119.5, passenger: 113.1, retail: 110.3,
      services: 115.9, populationCount: 4379791, populationDate: '2026-01-01',
    },
    source: 'samstat.uz',
  },
  tashkent_city: {
    nameRu: 'Город Ташкент', shortRu: 'Ташкент',
    population: '3.18 mln', populationRaw: 3.18, districts: 12,
    area: '335 km²', mahallas: 585,
    raqamlarda: {
      period: '2025',
      grp: 111.3, industry: 107.3, agriculture: null, tashqi_savdo: 115.3,
      investment: 108.2, construction: 118.3, freight: 106.4, passenger: 108.7,
      retail: 113.9, services: 117.7, populationCount: 3178144,
      populationDate: '2025-01-01',
    },
    source: 'toshstat.uz',
  },
  bukhara: {
    nameRu: 'Бухарская область', shortRu: 'Бухара',
    population: '2.11 mln', populationRaw: 2.11, districts: 13,
    area: '40,328 km²', mahallas: 516,
    raqamlarda: {
      period: '2025',
      grp: 107.2, industry: 107.1, agriculture: 104.3, investment: 80.6,
      construction: 111.3, freight: 102.6, passenger: 101.2, retail: 109.2,
      services: 114.0, populationCount: 2107035, populationDate: null,
    },
    source: 'buxstat.uz',
  },
  namangan: {
    nameRu: 'Наманганская область', shortRu: 'Наманган',
    population: '3.20 mln', populationRaw: 3.20, districts: 14,
    area: '7,440 km²', mahallas: 754,
    raqamlarda: {
      period: '2026Q1',
      grp: 108.8, industry: 108.8, agriculture: 104.6, investment: 137.0,
      construction: 116.1, freight: 111.0, passenger: 105.0, retail: 128.8,
      services: 115.2, populationCount: 3202700, populationDate: '2026-04-01',
    },
    source: 'namstat.uz',
  },
};

const NATIONAL = {
  nameRu: 'Узбекистан',
  population: '38.24 mln',
  raqamlarda: {
    period: '2025',
    grp: 107.7, industry: 106.8, agriculture: 104.4, investment: 110.5,
    construction: 114.2, freight: 101.9, passenger: 105.8, retail: 111.2,
    services: 114.7, populationCount: 38236704, populationDate: '2026-01-01',
  },
};

// Metric definitions (Russian labels, icon name from Material Symbols)
const METRICS = [
  { key: 'grp',         labelRu: 'Валовой региональный продукт', shortRu: 'ВРП', icon: 'trending_up',     group: 'production' },
  { key: 'industry',    labelRu: 'Промышленность',                shortRu: 'Промышленность', icon: 'factory',         group: 'production' },
  { key: 'agriculture', labelRu: 'Сельское, лесное и рыбное хозяйство', shortRu: 'Сельское хоз-во', icon: 'agriculture',     group: 'production' },
  { key: 'investment',  labelRu: 'Инвестиции в основной капитал', shortRu: 'Инвестиции', icon: 'savings',         group: 'capital' },
  { key: 'construction',labelRu: 'Строительные работы',           shortRu: 'Строительство', icon: 'construction',    group: 'capital' },
  { key: 'freight',     labelRu: 'Грузооборот',                   shortRu: 'Грузооборот', icon: 'local_shipping',  group: 'trade' },
  { key: 'passenger',   labelRu: 'Пассажирооборот',               shortRu: 'Пассажирооборот', icon: 'directions_bus', group: 'trade' },
  { key: 'retail',      labelRu: 'Розничный товарооборот',        shortRu: 'Розница', icon: 'storefront',      group: 'trade' },
  { key: 'services',    labelRu: 'Услуги',                        shortRu: 'Услуги', icon: 'handyman',        group: 'trade' },
  { key: 'tashqi_savdo',labelRu: 'Внешнеторговый оборот',         shortRu: 'Внешняя торговля', icon: 'public',          group: 'trade' },
];

const PERIOD_LABELS = {
  '2025':   'январь — декабрь 2025 г.',
  '2026Q1': 'январь — март 2026 г.',
};

const COMP_LABELS = {
  '2025':   'в % к январю — декабрю 2024 г.',
  '2026Q1': 'в % к январю — марту 2025 г.',
};

// Helpers
function pctDelta(v) { return v == null ? null : +(v - 100).toFixed(1); }
function fmtCount(n) {
  if (n == null) return '—';
  return n.toLocaleString('ru-RU').replace(/,/g, ' ');
}
function fmtPct(v, sign = true) {
  if (v == null) return '—';
  return (sign && v > 0 ? '+' : '') + v.toFixed(1) + '%';
}
function deltaVsNational(v, key) {
  const nat = NATIONAL.raqamlarda[key];
  if (v == null || nat == null) return null;
  return +(v - nat).toFixed(1);
}
function tone(v) {
  if (v == null) return 'na';
  if (v >= 110) return 'pos-strong';
  if (v >= 102) return 'pos';
  if (v >= 99)  return 'neu';
  return 'neg';
}

// Synthetic 6-period sparkline series — deterministic per (region, key).
function sparkSeries(regionKey, metricKey, endValue) {
  if (endValue == null) return null;
  let h = 0;
  const s = regionKey + ':' + metricKey;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  const rand = () => { h = (h * 1664525 + 1013904223) >>> 0; return (h & 0xffff) / 0xffff; };
  const pts = [];
  let v = endValue + (rand() - 0.5) * 6;
  for (let i = 0; i < 5; i++) {
    pts.push(+v.toFixed(1));
    v += (endValue - v) * 0.35 + (rand() - 0.5) * 1.6;
  }
  pts.push(endValue);
  return pts;
}

window.RegionData = {
  REGIONS: REGION_DATA,
  NATIONAL,
  METRICS,
  PERIOD_LABELS,
  COMP_LABELS,
  pctDelta,
  fmtCount,
  fmtPct,
  deltaVsNational,
  tone,
  sparkSeries,
};
