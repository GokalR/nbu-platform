/**
 * Thin client for the CERR Mahalla Analytics v2 backend (/api/cerr).
 * Mirrors the rsApi.js pattern: returns { ok, data } on success, { ok: false, ... }
 * on failure. Falls back to no-op when VITE_API_URL is unset.
 */
import { BACKEND_URL } from '@/services/api'

// VITE_API_URL is the rs-tool convention and includes the "/api/rs" suffix.
// The cerr router is mounted at "/api/cerr" directly on the host (NOT under
// /api/rs), so we strip that suffix here and build /api/cerr ourselves.
const _raw = (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '')
const _full = _raw.startsWith('/') ? BACKEND_URL + _raw : _raw
const BASE = _full.replace(/\/api\/rs\/?$/i, '')

let runtimeDisabled = false
const isConfigured = () => Boolean(BASE) && !runtimeDisabled

function authHeaders() {
  const token = localStorage.getItem('edu_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path) {
  if (!isConfigured()) return { ok: false, reason: 'no-backend' }
  try {
    const res = await fetch(`${BASE}/api/cerr${path}`, {
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
    })
    if (!res.ok) {
      return { ok: false, status: res.status, error: await res.text().catch(() => res.statusText) }
    }
    return { ok: true, data: await res.json() }
  } catch (e) {
    runtimeDisabled = true
    return { ok: false, reason: 'no-backend', error: String(e) }
  }
}

export const cerrApi = {
  isConfigured,
  listRegions: () => request('/regions'),
  getRegion: (code) => request(`/regions/${code}`),
  getRegionOverview: (code) => request(`/regions/${code}/overview`),
  listRegionDistricts: (code) => request(`/regions/${code}/districts`),
  getDistrict: (code) => request(`/districts/${code}`),
  getDistrictOverview: (code) => request(`/districts/${code}/overview`),
  getDistrictMacro: (code) => request(`/districts/${code}/macro`),
  listDistrictMahallas: (code, sort = 'rating_asc', limit = 500) =>
    request(`/districts/${code}/mahallas?sort=${sort}&limit=${limit}`),
  getDistrictGeo: (code) => request(`/districts/${code}/geo`),
  searchMahallas: (q, limit = 50) =>
    request(`/mahallas/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  getMahalla: (stir) => request(`/mahallas/${stir}`),
  getMahallaAiInsights: (stir) => request(`/mahallas/${stir}/ai_insights`),
}
