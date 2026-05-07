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
    // Don't override Content-Type when sending FormData — browser sets it
    // with the boundary automatically.
    const isFormData = options.body instanceof FormData
    const headers = isFormData
      ? { ...auth, ...(options.headers || {}) }
      : { 'Content-Type': 'application/json', ...auth, ...(options.headers || {}) }
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

  /**
   * Fetch the .docx as a Blob. We do this manually (not via `request`) so
   * we don't try to JSON.parse the binary response. Auth header still
   * applied. Returns { ok, blob, filename } or { ok: false, error }.
   */
  downloadDocx: async (id) => {
    if (!isConfigured()) return { ok: false, reason: 'no-backend' }
    try {
      const auth = _authHeaders()
      const res = await fetch(`${BASE}/business-plan/${id}/docx`, { headers: { ...auth } })
      if (!res.ok) {
        const text = await res.text().catch(() => '')
        let msg = res.statusText
        try {
          const j = JSON.parse(text)
          if (j?.detail) msg = j.detail
        } catch {
          if (text) msg = text
        }
        return { ok: false, status: res.status, error: msg }
      }
      const blob = await res.blob()
      // Pull filename out of Content-Disposition if present.
      const cd = res.headers.get('content-disposition') || ''
      const m = cd.match(/filename="([^"]+)"/)
      const filename = m ? m[1] : `business-plan-${id.slice(0, 8)}.docx`
      return { ok: true, blob, filename }
    } catch (e) {
      return { ok: false, reason: 'no-backend', error: String(e) }
    }
  },

  parseExcel: (balanceFile, pnlFile) => {
    const fd = new FormData()
    fd.append('balance', balanceFile)
    fd.append('pnl', pnlFile)
    return request('/business-plan/parse-excel', { method: 'POST', body: fd })
  },

  // Admin
  adminList: () => request('/admin/business-plans'),
  adminDetail: (id) => request(`/admin/business-plans/${id}`),
}
