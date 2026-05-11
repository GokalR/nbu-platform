/**
 * CERR Mahalla Analytics — REST client.
 *
 * Backed by FastAPI routes at /api/cerr/* (bff_frontend/backend/app/routes/cerr.py),
 * which read from Cloudflare R2 (cerr-data.devgokal.com) or a local cerr_runs/
 * tree depending on CERR_DATA_ROOT.
 *
 * Vue region map keys (e.g. "fergana", "tashkent_city") are translated to CERR
 * numeric region codes here so the rest of the app can keep using its existing
 * keys for things like icons, colors, and i18n.
 *
 * Sirdaryo (key "sirdaryo" → 1724) is now covered: data comes from the big
 * cerr_region_1724.json (folder loader missed it before).
 */

const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '')

function resolve(url) {
  return BACKEND_URL ? BACKEND_URL + url : url
}

async function request(url) {
  const res = await fetch(resolve(url))
  if (res.status === 404) return null
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

// Regions
export const listRegions = () => request('/api/cerr/regions')
export const getRegion = (code) => request(`/api/cerr/regions/${code}`)
export const getRegionOverview = (code) => request(`/api/cerr/regions/${code}/overview`)
export const listRegionDistricts = (code) => request(`/api/cerr/regions/${code}/districts`)

// Districts
export const getDistrict = (code) => request(`/api/cerr/districts/${code}`)
export const getDistrictOverview = (code) => request(`/api/cerr/districts/${code}/overview`)
export const getDistrictMacro = (code) => request(`/api/cerr/districts/${code}/macro`)
export const listDistrictMahallas = (code, { sort = 'rating_asc', limit = 500 } = {}) =>
  request(`/api/cerr/districts/${code}/mahallas?sort=${sort}&limit=${limit}`)
export const getDistrictGeo = (code) => request(`/api/cerr/districts/${code}/geo`)

// Mahallas
export const searchMahallas = (q, limit = 50) =>
  request(`/api/cerr/mahallas/search?q=${encodeURIComponent(q)}&limit=${limit}`)
export const getMahallaOverview = (stir) => request(`/api/cerr/mahallas/${stir}`)
export const getMahallaAiInsights = (stir) => request(`/api/cerr/mahallas/${stir}/ai_insights`)

// Geo (cerr-v2 maps)
export const getCountryGeo = () => request('/api/cerr/geo/country')
export const getRegionDistrictsGeo = (code) => request(`/api/cerr/regions/${code}/geo`)

// RAQAMLARDA national + per-region macro panel (compiled from REGIONS_RAQAMLARDA.md)
export const getRaqamlarda = (scope) => request(`/api/cerr/raqamlarda/${scope}`)

// Country rankings: 14 regions ranked by aggregated mahalla rating_score.
// First call ~7s (cold compute), subsequent calls cached.
export const getCountryRankings = () => request('/api/cerr/country/rankings')

// Country aggregate: one-shot payload (regions + populations + ranks +
// totals + tier counts) backed by a precomputed static JSON. Replaces the
// previous fan-out (regions list + 14 region overviews + country/rankings)
// with a single ~10 KB request. Powers the cerr-v2 country page.
export const getCountryAggregate = () => request('/api/cerr/country/aggregate')
