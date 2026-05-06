/**
 * API client for the SME Profile (Business Questionnaire) tool.
 * Mirrors businessPlanApi.js but mounted under /api/sme-profile (not /api/rs).
 */

import { BACKEND_URL } from '@/services/api'

const RAW = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
// VITE_API_URL is typically '/api/rs'. We want '/api'. Strip the '/rs' suffix
// if present, then append '/sme-profile' per-call.
const API_ROOT = RAW.endsWith('/rs') ? RAW.slice(0, -'/rs'.length) : RAW
const BASE = API_ROOT.startsWith('/') ? BACKEND_URL + API_ROOT : API_ROOT

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
    const headers = {
      'Content-Type': 'application/json',
      ...auth,
      ...(options.headers || {}),
    }
    const res = await fetch(`${BASE}${path}`, { ...options, headers })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
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

export const smeProfileApi = {
  isConfigured,
  fetchQuestions: () => request('/sme-profile/questions'),
  lookup: (q) => request(`/sme-profile/lookup?q=${encodeURIComponent(q)}`),
  fetchViloyats: () => request('/sme-profile/address/viloyats'),
  fetchTumans: (viloyat) =>
    request(`/sme-profile/address/tumans?viloyat=${encodeURIComponent(viloyat)}`),
  fetchMfy: (viloyat, tuman) =>
    request(
      `/sme-profile/address/mfy?viloyat=${encodeURIComponent(viloyat)}&tuman=${encodeURIComponent(tuman)}`,
    ),
  submit: (payload) =>
    request('/sme-profile/submissions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
