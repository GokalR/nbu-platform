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
