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
      return { ok: false, status: res.status, error: text || res.statusText }
    }
    const data = await res.json()
    return { ok: true, data }
  } catch (e) {
    runtimeDisabled = true
    return { ok: false, reason: 'no-backend', error: String(e) }
  }
}

export const businessPlanApi = {
  isConfigured,

  generate: (payload) =>
    request('/api/business-plan/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getPlan: (id) => request(`/api/business-plan/${id}`),

  // Admin
  adminList: () => request('/api/admin/business-plans'),
  adminDetail: (id) => request(`/api/admin/business-plans/${id}`),
}
