import { BACKEND_URL } from './api'

// Phase 2D-1: chat endpoints + session endpoints all require the same
// Authorization: Bearer <edu_token> header that the rest of the platform uses.
function authHeaders() {
  const token = localStorage.getItem('edu_token')
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function _request(path, options = {}) {
  const resp = await fetch(`${BACKEND_URL}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  })
  if (!resp.ok) {
    let detail = ''
    try {
      const data = await resp.json()
      detail = data.detail || JSON.stringify(data)
    } catch {
      detail = await resp.text()
    }
    throw new Error(`chatbot ${resp.status}: ${detail}`)
  }
  return resp.json()
}

// ---- Session management -----------------------------------------------

export function listChatSessions() {
  return _request('/api/chatbot/sessions', { method: 'GET' })
}

export function createChatSession() {
  return _request('/api/chatbot/sessions', { method: 'POST' })
}

export function loadChatSession(sessionId) {
  return _request(`/api/chatbot/sessions/${encodeURIComponent(sessionId)}`, { method: 'GET' })
}

export function deleteChatSession(sessionId) {
  return _request(`/api/chatbot/sessions/${encodeURIComponent(sessionId)}`, { method: 'DELETE' })
}

// ---- Sending messages -------------------------------------------------

export async function sendChatMessage({ message, sessionId, maxRows = 10 }) {
  return _request('/api/chatbot/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      session_id: sessionId,
      max_rows: maxRows,
    }),
  })
}

/**
 * Open an SSE stream to the chatbot. The chatbot emits three event types:
 *   - status: { stage, message } — phase-of-pipeline progress updates
 *   - token:  { text }            — append to the rendered answer bubble
 *   - done:   { kind, answer, sql, row_count, columns, pipeline, ok }
 *
 * EventSource cannot set Authorization headers, so we pass the token as a
 * query param. The BFF accepts either Bearer header OR `token=` query — the
 * existing /api/chatbot/chat/stream uses `require_auth(credentials=...)`
 * which reads the Bearer header. To keep it simple, we tunnel the token via
 * the URL's `Authorization` header… wait — EventSource doesn't allow that.
 * Fallback: fetch + ReadableStream is used so we can set headers.
 */
export function openChatStream(
  { message, sessionId, maxRows = 10 },
  { onStatus, onToken, onDone, onError } = {},
) {
  const url = new URL(`${BACKEND_URL || window.location.origin}/api/chatbot/chat/stream`)
  url.searchParams.set('message', message)
  url.searchParams.set('max_rows', String(maxRows))
  if (sessionId) url.searchParams.set('session_id', sessionId)

  const controller = new AbortController()
  let doneSeen = false

  ;(async () => {
    try {
      const resp = await fetch(url.toString(), {
        method: 'GET',
        headers: authHeaders(),
        signal: controller.signal,
      })
      if (!resp.ok) {
        onError?.(`stream ${resp.status}`)
        return
      }
      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buf = ''
      let currentEvent = 'message'

      const handleFrame = (evt, data) => {
        if (evt === 'status') {
          try {
            onStatus?.(JSON.parse(data))
          } catch {}
        } else if (evt === 'token') {
          try {
            const { text } = JSON.parse(data)
            if (typeof text === 'string' && text) onToken?.(text)
          } catch {}
        } else if (evt === 'done') {
          doneSeen = true
          try {
            onDone?.(JSON.parse(data))
          } catch {
            onDone?.({})
          }
        } else if (evt === 'error') {
          let detail = ''
          try {
            detail = JSON.parse(data || '{}')?.error || ''
          } catch {}
          onError?.(detail || 'stream error')
        }
      }

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        let idx
        while ((idx = buf.indexOf('\n\n')) !== -1) {
          const frame = buf.slice(0, idx)
          buf = buf.slice(idx + 2)
          let evtName = 'message'
          let dataPayload = ''
          for (const line of frame.split('\n')) {
            if (line.startsWith('event:')) evtName = line.slice(6).trim()
            else if (line.startsWith('data:')) dataPayload = line.slice(5).trim()
          }
          if (dataPayload) handleFrame(evtName, dataPayload)
        }
      }
      if (!doneSeen) onError?.('stream ended without done event')
    } catch (err) {
      if (err.name !== 'AbortError' && !doneSeen) {
        onError?.(err?.message || 'stream error')
      }
    }
  })()

  return { close: () => controller.abort() }
}
