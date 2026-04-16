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

export const kpis = [
  { key: 'population', value: '4.2 mln', delta: '+1.2%', icon: 'groups', tone: 'positive' },
  { key: 'gdpGrowth', value: '8.7%', delta: '+8.7%', icon: 'trending_up', tone: 'positive' },
  { key: 'exports', value: '$1.2 mlrd', delta: 'Target', icon: 'payments', tone: 'positive' },
  { key: 'mahallas', value: '1,248', delta: 'Total', icon: 'location_city', tone: 'neutral' },
]

export const economicBars = [
  { labelKey: 'home.cards.industry', value: '$420 mln', percent: 85, color: 'bg-primary' },
  { labelKey: 'home.cards.agriculture', value: '$380 mln', percent: 70, color: 'bg-primary-container' },
  { labelKey: 'home.cards.services', value: '$220 mln', percent: 45, color: 'bg-primary opacity-60' },
]

export const populationBars = [
  { labelKey: 'home.cards.employed', value: '2.1 mln', percent: 92, color: 'bg-tertiary' },
  { labelKey: 'home.cards.selfEmployed', value: '850k', percent: 65, color: 'bg-tertiary-container' },
  { labelKey: 'home.cards.education', value: '120k', percent: 30, color: 'bg-tertiary opacity-60' },
]

export const bankBars = [
  { labelKey: 'home.cards.credits', value: '8.4 trln', percent: 78, color: 'bg-primary-container' },
  { labelKey: 'home.cards.newBusiness', value: '4.2 ming', percent: 55, color: 'bg-primary' },
  { labelKey: 'home.cards.exporters', value: '850 ta', percent: 40, color: 'bg-secondary' },
]

export const tools = [
  { key: 'fincontrol', icon: 'account_balance_wallet', accent: 'bg-primary', to: '/tools/fincontrol', featured: true, inDev: true },
  { key: 'strategy', icon: 'rocket_launch', accent: 'bg-tertiary', to: '/tools/regional-strategist', featured: true },
  { key: 'forecast', icon: 'query_stats', accent: 'bg-primary', comingSoon: true },
  { key: 'credit', icon: 'credit_score', accent: 'bg-secondary', comingSoon: true },
]

export const districtByKey = Object.fromEntries(districts.map((d) => [d.key, d]))
