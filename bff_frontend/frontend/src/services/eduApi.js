/**
 * Education API service — wraps all calls to the Python FastAPI backend.
 *
 *  - In dev: relative URLs ('/api/...') are proxied by Vite to localhost:8000.
 *  - In prod: VITE_BACKEND_URL (e.g. https://nbu-platform-production.up.railway.app)
 *    is prepended so requests go straight to Railway. The previous
 *    Cloudflare Pages /api/* proxy rewrite was rejected at build time.
 */

const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '')

function resolve(url) {
  if (!url.startsWith('/api') && !url.startsWith('/health')) return url
  return BACKEND_URL ? BACKEND_URL + url : url
}

function getAuthHeaders() {
  const token = localStorage.getItem('edu_token')
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function request(url, options = {}) {
  const res = await fetch(resolve(url), {
    ...options,
    headers: { ...getAuthHeaders(), ...options.headers },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

// ── Courses ──────────────────────────────────────────
export const getCourses = () => request('/api/courses')
export const getCourse = (id) => request(`/api/courses/${id}`)
export const getCourseVideos = (courseId) => request(`/api/courses/${courseId}/videos`)

// ── Videos ───────────────────────────────────────────
export const getVideo = (id) => request(`/api/videos/${id}`)
export const getVideoContent = (videoId) => request(`/api/videos/${videoId}/content`)

// ── Enrollment ───────────────────────────────────────
export const checkEnrollment = (courseId) => request(`/api/courses/${courseId}/enroll`)
export const enrollCourse = (courseId) =>
  request(`/api/courses/${courseId}/enroll`, { method: 'POST' })

// ── Progress ─────────────────────────────────────────
export const saveVideoProgress = (data) =>
  request('/api/progress/video', { method: 'POST', body: JSON.stringify(data) })

export const submitQuiz = (data) =>
  request('/api/progress/quiz', { method: 'POST', body: JSON.stringify(data) })

export const submitTest = (data) =>
  request('/api/progress/test', { method: 'POST', body: JSON.stringify(data) })

export const saveFlashcardProgress = (data) =>
  request('/api/progress/flashcard', { method: 'POST', body: JSON.stringify(data) })

// ── Dashboard ────────────────────────────────────────
export const getDashboard = () => request('/api/me/dashboard')
export const getDueFlashcards = () => request('/api/me/flashcards/due')

// ── Golden Mart ──────────────────────────────────────
export const gmListEntities = (level) =>
  request(`/api/gm/entities${level ? `?level=${level}` : ''}`)

export const gmGetEntityData = (level, key) =>
  request(`/api/gm/data/${level}/${key}`)

export const gmGetYear = (level, key, year) =>
  request(`/api/gm/data/${level}/${key}/${year}`)

export const gmWriteYear = (level, key, year, values) =>
  request(`/api/gm/data/${level}/${key}/${year}`, {
    method: 'PUT',
    body: JSON.stringify({ values }),
  })

export const gmCoverage = (level, key) =>
  request(`/api/gm/coverage/${level}/${key}`)

// ── Auth ─────────────────────────────────────────────
export const login = (email, password) =>
  request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })

export const register = (email, password, fullName) =>
  request('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName }),
  })

export const getMe = () => request('/api/auth/me')
