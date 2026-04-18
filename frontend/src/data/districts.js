// All 19 entities of Fergana region (4 cities + 15 districts).
// Population in thousands; area in km². Sources: stat.uz tail figures rounded,
// geoBoundaries ADM2 for geometry (see public/fergana-districts.geojson).

export const districts = [
  // Cities
  { key: 'fargona_city',  kind: 'city',     population: 335.1, area: 110,  status: 'active' },
  { key: 'margilon_city', kind: 'city',     population: 261.9, area: 52,   status: 'active' },
  { key: 'qoqon_city',    kind: 'city',     population: 319.6, area: 60,   status: 'active' },
  { key: 'quvasoy_city',  kind: 'city',     population: 104.8, area: 260,  status: 'active' },
  // Districts (tumanlar)
  { key: 'oltiariq',  kind: 'district', population: 237.3, area: 630, status: 'active' },
  { key: 'beshariq',  kind: 'district', population: 198.2, area: 770, status: 'active' },
  { key: 'bogdod',    kind: 'district', population: 197.5, area: 340, status: 'active' },
  { key: 'buvayda',   kind: 'district', population: 182.3, area: 280, status: 'active' },
  { key: 'dangara',   kind: 'district', population: 175.0, area: 430, status: 'active' },
  { key: 'farhona',   kind: 'district', population: 274.5, area: 590, status: 'active' },
  { key: 'furqat',    kind: 'district', population: 109.3, area: 310, status: 'active' },
  { key: 'qoshtepa',  kind: 'district', population: 217.8, area: 370, status: 'active' },
  { key: 'quva',      kind: 'district', population: 296.8, area: 440, status: 'active' },
  { key: 'rishton',   kind: 'district', population: 210.6, area: 310, status: 'active' },
  { key: 'sox',       kind: 'district', population: 75.3,  area: 220, status: 'active' },
  { key: 'toshloq',   kind: 'district', population: 178.4, area: 240, status: 'active' },
  { key: 'uchkoprik', kind: 'district', population: 189.5, area: 270, status: 'active' },
  { key: 'ozbekiston',kind: 'district', population: 205.1, area: 670, status: 'active' },
  { key: 'yozyovon',  kind: 'district', population: 167.2, area: 410, status: 'active' },
]

export const tools = [
  { key: 'fincontrol', icon: 'account_balance_wallet', accent: 'bg-primary', to: '/tools/fincontrol', featured: true, inDev: true },
  { key: 'strategy', icon: 'rocket_launch', accent: 'bg-tertiary', to: '/tools/regional-strategist', featured: true },
  { key: 'forecast', icon: 'query_stats', accent: 'bg-primary', comingSoon: true },
  { key: 'credit', icon: 'credit_score', accent: 'bg-secondary', comingSoon: true },
]

export const districtByKey = Object.fromEntries(districts.map((d) => [d.key, d]))
