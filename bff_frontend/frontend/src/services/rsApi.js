/**
 * Thin API client for the Regional Strategist backend.
 * Base URL comes from VITE_API_URL (see .env or Railway/Vercel env settings).
 * If unset, all calls resolve as { ok: false, reason: 'no-backend' } so the
 * app keeps working in static/demo mode.
 */

import { BACKEND_URL } from '@/services/api'

const BASE = (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '').startsWith('/')
  ? BACKEND_URL + (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '')
  : import.meta.env.VITE_API_URL?.replace(/\/$/, '') || ''

// Once a network failure happens, stop trying to reach the backend for the
// rest of this session — UI treats the app as unconfigured and uses local mode.
let runtimeDisabled = false

const isConfigured = () => Boolean(BASE) && !runtimeDisabled

function _authHeaders() {
  const token = localStorage.getItem('edu_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  if (!isConfigured()) return { ok: false, reason: 'no-backend' }
  try {
    const auth = _authHeaders()
    const contentHeaders = options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }
    const res = await fetch(`${BASE}${path}`, {
      headers: { ...contentHeaders, ...auth },
      ...options,
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      return { ok: false, status: res.status, error: text || res.statusText }
    }
    const data = await res.json()
    return { ok: true, data }
  } catch (e) {
    // Network error (backend down, CORS, offline, etc.) — disable the backend
    // path so later calls skip the failing fetch and run locally.
    runtimeDisabled = true
    return { ok: false, reason: 'no-backend', error: String(e) }
  }
}

export const rsApi = {
  isConfigured,
  baseUrl: () => BASE,

  createSubmission: (payload) =>
    request('/submissions', { method: 'POST', body: JSON.stringify(payload) }),

  getSubmission: (id) => request(`/submissions/${id}`),

  uploadExcel: (subId, kind, file) => {
    const fd = new FormData()
    fd.append('kind', kind)
    fd.append('file', file)
    return request(`/submissions/${subId}/uploads`, { method: 'POST', body: fd })
  },

  listUploads: (subId) => request(`/submissions/${subId}/uploads`),

  runAnalysis: (subId, opts = {}) =>
    request(`/submissions/${subId}/analysis`, {
      method: 'POST',
      body: JSON.stringify(opts),
    }),

  latestAnalysis: (subId) => request(`/submissions/${subId}/analysis/latest`),

  health: () => request('/health'),

  // User's submission history (requires auth)
  mySubmissions: () => request('/submissions/my'),

  // Reference data (cities + benchmarks from DB)
  getCities: () => request('/reference/cities'),
  getCity: (id) => request(`/reference/cities/${id}`),
  getBenchmarks: (region = 'fergana') => request(`/reference/benchmarks/${region}`),
  getCityDistricts: (cityId) => request(`/reference/districts?city_id=${encodeURIComponent(cityId)}`),
  getCityEnterprises: (cityId, sector = '') => {
    const q = new URLSearchParams({ city_id: cityId })
    if (sector) q.set('sector', sector)
    return request(`/reference/enterprises?${q.toString()}`)
  },
  getCreditProducts: (tier = '') => {
    const q = tier ? `?tier=${encodeURIComponent(tier)}` : ''
    return request(`/reference/credit-products${q}`)
  },
}
