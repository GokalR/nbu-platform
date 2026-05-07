import { QuestionsResponse, SubmissionPayload, ClientInfo } from './types'

const BASE: string = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export async function fetchQuestions(): Promise<QuestionsResponse> {
  const res = await fetch(`${BASE}/questions`)
  if (!res.ok) throw new Error('Failed to fetch questions')
  return res.json()
}

export async function lookupClient(q: string): Promise<{ found: false } | ({ found: true } & ClientInfo)> {
  const res = await fetch(`${BASE}/lookup?q=${encodeURIComponent(q)}`)
  if (!res.ok) throw new Error('Lookup failed')
  return res.json()
}

export async function fetchViloyats(): Promise<{ viloyats: string[]; source_found: boolean }> {
  const res = await fetch(`${BASE}/address/viloyats`)
  if (!res.ok) throw new Error('Failed to load viloyats')
  return res.json()
}

export async function fetchTumans(viloyat: string): Promise<{ tumans: string[] }> {
  const res = await fetch(`${BASE}/address/tumans?viloyat=${encodeURIComponent(viloyat)}`)
  if (!res.ok) throw new Error('Failed to load tumans')
  return res.json()
}

export async function fetchMfy(viloyat: string, tuman: string): Promise<{ mfy: string[] }> {
  const res = await fetch(
    `${BASE}/address/mfy?viloyat=${encodeURIComponent(viloyat)}&tuman=${encodeURIComponent(tuman)}`
  )
  if (!res.ok) throw new Error('Failed to load MFY')
  return res.json()
}

export async function submitAnswers(payload: SubmissionPayload): Promise<void> {
  const res = await fetch(`${BASE}/submissions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail ?? 'Submission failed')
  }
}

export function downloadResponsesUrl(): string {
  return `${BASE}/download-responses`
}
