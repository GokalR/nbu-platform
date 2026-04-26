// All 16 entities of Samarkand region (2 cities + 14 districts).
// Per-district population and area are 2024-2025 estimates from public
// references — they sum close to but not exactly to the verified regional
// total (4 379 791 / 16 770 km²). The headline regional KPIs in
// `buildSamarqandOverview()` come from samstat.uz / NBU Excel briefs.
// Source: geoBoundaries gbOpen ADM2 for geometry (see public/samarqand-districts.geojson).

export const samarqandDistricts = [
  // Cities of regional rank
  { key: 'samarqand_city',   kind: 'city',     population: 559.0, area: 115,  status: 'active' },
  { key: 'kattaqorgon_city', kind: 'city',     population: 88.0,  area: 17,   status: 'active' },
  // Rural districts
  { key: 'bulungur',    kind: 'district', population: 220.0, area: 720,  status: 'active' },
  { key: 'ishtikhon',   kind: 'district', population: 230.0, area: 600,  status: 'active' },
  { key: 'jomboy',      kind: 'district', population: 200.0, area: 740,  status: 'active' },
  { key: 'kattaqorgon', kind: 'district', population: 290.0, area: 760,  status: 'active' },
  { key: 'narpay',      kind: 'district', population: 230.0, area: 590,  status: 'active' },
  { key: 'nurobod',     kind: 'district', population: 180.0, area: 2870, status: 'active' },
  { key: 'oqdaryo',     kind: 'district', population: 220.0, area: 660,  status: 'active' },
  { key: 'pastdargom',  kind: 'district', population: 470.0, area: 1100, status: 'active' },
  { key: 'paxtachi',    kind: 'district', population: 200.0, area: 760,  status: 'active' },
  { key: 'payariq',     kind: 'district', population: 250.0, area: 990,  status: 'active' },
  { key: 'qoshrabod',   kind: 'district', population: 110.0, area: 1700, status: 'active' },
  { key: 'samarqand',   kind: 'district', population: 360.0, area: 360,  status: 'active' },
  { key: 'tayloq',      kind: 'district', population: 230.0, area: 360,  status: 'active' },
  { key: 'urgut',       kind: 'district', population: 540.0, area: 2100, status: 'active' },
]

export const samarqandByKey = Object.fromEntries(
  samarqandDistricts.map((d) => [d.key, d]),
)
