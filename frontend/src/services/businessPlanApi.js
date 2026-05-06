/**
 * API client for the Business Plan tool.
 * Mirrors the rsApi pattern: VITE_API_URL is the base; falls back to a clear
 * 'no-backend' result if unset, so callers can show a friendly message.
 */

import { BACKEND_URL } from '@/services/api'

const BASE = (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '').startsWith('/')
  ? BACKEND_URL + (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '')
  : import.meta.env.VITE_API_URL?.replace(/\/$/, '') || ''

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
    const headers = { 'Content-Type': 'application/json', ...auth, ...(options.headers || {}) }
    const res = await fetch(`${BASE}${path}`, { ...options, headers })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      // FastAPI returns {"detail": "..."}; surface that nicely.
      let msg = res.statusText
      try {
        const j = JSON.parse(text)
        if (j && typeof j.detail === 'string') msg = j.detail
        else if (text) msg = text
      } catch {
        if (text) msg = text
      }
      return { ok: false, status: res.status, error: msg }
    }
    const data = await res.json()
    return { ok: true, data }
  } catch (e) {
    runtimeDisabled = true
    return { ok: false, reason: 'no-backend', error: String(e) }
  }
}

// Paths are appended to VITE_API_URL (which already contains /api/rs in
// production), so the final URL is /api/rs/business-plan/... matching the
// backend's mount.
export const businessPlanApi = {
  isConfigured,

  generate: (payload) =>
    request('/business-plan/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getPlan: (id) => request(`/business-plan/${id}`),

  // Admin
  adminList: () => request('/admin/business-plans'),
  adminDetail: (id) => request(`/admin/business-plans/${id}`),
}
