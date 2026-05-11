import { BACKEND_URL } from './api'

export async function sendChatMessage({ message, sessionId, maxRows = 10 }) {
  const resp = await fetch(`${BACKEND_URL}/api/chatbot/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId || null,
      max_rows: maxRows,
    }),
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

/**
 * Open an SSE stream to the chatbot. The chatbot emits three event types:
 *   - status: { stage, message } — phase-of-pipeline progress updates
 *   - token:  { text }            — append to the rendered answer bubble
 *   - done:   { kind, answer, sql, row_count, columns, pipeline, ok }
 *
 * Returns an object with { close() }. The caller passes named handlers
 * (onStatus / onToken / onDone / onError) for each event family. Callers
 * MUST keep the returned object so they can close the connection on
 * component unmount, otherwise the EventSource leaks.
 */
export function openChatStream(
  { message, sessionId, maxRows = 10 },
  { onStatus, onToken, onDone, onError } = {},
) {
  const params = new URLSearchParams({
    message,
    max_rows: String(maxRows),
  })
  if (sessionId) params.set('session_id', sessionId)
  const url = `${BACKEND_URL}/api/chatbot/chat/stream?${params.toString()}`

  const es = new EventSource(url)
  let doneSeen = false

  es.addEventListener('status', (ev) => {
    try {
      onStatus?.(JSON.parse(ev.data))
    } catch {
      /* ignore malformed status frames */
    }
  })
  es.addEventListener('token', (ev) => {
    try {
      const { text } = JSON.parse(ev.data)
      if (typeof text === 'string' && text) onToken?.(text)
    } catch {
      /* ignore */
    }
  })
  es.addEventListener('done', (ev) => {
    doneSeen = true
    try {
      onDone?.(JSON.parse(ev.data))
    } catch {
      onDone?.({})
    }
    es.close()
  })
  es.addEventListener('error', (ev) => {
    // EventSource fires onerror both on real failures AND on normal close.
    // We treat absence of `done` as a real error.
    if (!doneSeen) {
      let detail = ''
      try {
        detail = JSON.parse(ev.data || '{}')?.error || ''
      } catch {
        detail = ''
      }
      onError?.(detail || 'stream connection lost')
    }
    es.close()
  })

  return { close: () => es.close() }
}

export function ensureChatSessionId() {
  const KEY = 'chatbot_session_id'
  let id = sessionStorage.getItem(KEY)
  if (!id) {
    id =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : `s_${Date.now()}_${Math.random().toString(36).slice(2)}`
    sessionStorage.setItem(KEY, id)
  }
  return id
}
