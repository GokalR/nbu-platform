# Uzbekistan Regional Analytics — Backend (RAG via OpenAI File Search)

Self-contained FastAPI backend. Answers questions about Uzbekistan's 14 regions
(viloyats / shahars + Qoraqalpog'iston) using OpenAI's File Search managed RAG.
Source documents live in `rag_single/` (Uzbek Cyrillic). Final answer is in **Latin Uzbek**.

## Folder layout

```
backend/
├── config.py          env loader, region registry, model name, timeout
├── router.py          deterministic name router (Cyrillic + Latin index)
├── prompts.py         RAG system prompt (Latin Uzbek output, hard bans)
├── rag.py             OpenAI Responses API + file_search streaming
├── orchestrator.py    route → rag, emits SSE events
├── main.py            FastAPI app
├── ingest.py          one-time vector-store builder
├── cli.py             command-line tester
├── requirements.txt
├── README.md
├── .env               (you create this — see below)
└── rag_single/        14 .md source documents
```

## Architecture

```
User question
    │
    ▼
Deterministic name router  (free, ~1 ms)
    │ matches viloyat / tuman / mahalla names → list of viloyat_codes
    │ no match → all 14 (treated as global query)
    ▼
OpenAI Responses API + file_search tool
    │ vector_store_id from .env
    │ metadata filter: viloyat_code IN [matched codes]
    │ retrieves ~30 relevant chunks
    ▼
Streaming Latin-Uzbek answer (SSE) over HTTP
```

## Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` (inside `backend/`):

```
OPENAI=sk-...
```

Optional overrides:

```
RAG_MODEL=gpt-5.4-mini
VECTOR_STORE_NAME=uzbekistan-regional-analytics
RAG_TIMEOUT_SEC=180
CORS_ORIGINS=*
```

## One-time ingest (creates the vector store)

```powershell
python ingest.py
```

It uploads the 14 MDs with metadata (`viloyat_code`, `viloyat_latin`, `viloyat_cyrillic`)
and waits for indexing. When done it prints:

```
VECTOR_STORE_ID=vs_xxxxxxxxxxxxxx
```

Add that line to `.env`.

## Run

Dev:

```powershell
uvicorn main:app --reload --port 8000
```

Prod:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

CLI sanity check:

```powershell
python cli.py "Yangiyer shahri Yuksalish mahallasida aholi soni qancha?"
```

## API endpoints

| Method | Path             | Body / Query           | Returns                                                                |
|--------|------------------|------------------------|------------------------------------------------------------------------|
| GET    | `/health`        | —                      | `{ok, vector_store_configured, rag_model, region_count, regions[]}`    |
| POST   | `/chat`          | `{"question": "..."}`  | `{question, answer, router_selected[], router_matched[], total_elapsed_s}` |
| GET    | `/chat/stream`   | `?question=...`        | `text/event-stream` (SSE)                                              |
| GET    | `/docs`          | —                      | Swagger UI (auto)                                                      |
| GET    | `/redoc`         | —                      | ReDoc UI (auto)                                                        |
| GET    | `/openapi.json`  | —                      | OpenAPI spec (auto)                                                    |

### SSE protocol (`/chat/stream`)

Client opens `EventSource('/chat/stream?question=...')` and receives newline-delimited
events. Each event's `data:` line is JSON:

```
{"type":"status","stage":"routed","selected":["Sirdaryo viloyati"],"matched":["юксалиш"],"n":1}
{"type":"status","stage":"rag_started"}
{"type":"token","text":"Yu"}
{"type":"token","text":"ksalish"}
...
{"type":"done","elapsed_s":3.21}
```

Accumulate `token.text` into the answer. Finalize on `done`. Status events are optional UX.

### POST `/chat` request/response example

Request:

```json
{ "question": "Sirdaryo viloyatining eng yuqori reytingli 5 mahallasi?" }
```

Response (truncated):

```json
{
  "question": "Sirdaryo viloyatining eng yuqori reytingli 5 mahallasi?",
  "answer": "| O'rin | Mahalla | Tuman | Reyting |\n|---|---|---|---|\n| 1 | ...",
  "router_selected": ["Sirdaryo viloyati"],
  "router_matched": ["sirdaryo"],
  "total_elapsed_s": 3.41
}
```

## Validation & limits

- `question`: required, 1–1500 chars (otherwise HTTP 400 / 413).
- Timeouts: `RAG_TIMEOUT_SEC` (default 180 s).
- CORS: `CORS_ORIGINS=*` by default; set comma-separated origins for prod.

## Cost ballpark

- Vector storage: 14 MDs ≈ 7 MB → first 1 GB free → **$0**.
- File Search: ~$0.0025 per query.
- Tokens (gpt-5.4-mini): ~$0.001–0.005 per query.
- **Per-query total**: ~$0.005.
- Latency: 1–3 s warm, 3–6 s cold.

## Re-ingest workflow

If the source MDs change:

1. Run `python ingest.py` again — it creates a NEW vector store and prints a new id.
2. Replace `VECTOR_STORE_ID` in `.env` with the new id.
3. Restart uvicorn.
4. (Optional) delete the old vector store via the OpenAI dashboard to stop storage charges.

## Production checklist

- [ ] Restrict `CORS_ORIGINS` to your frontend's exact origins.
- [ ] Add an API key / auth header check (no auth is included).
- [ ] Add rate limiting (e.g., `slowapi` middleware) to prevent OpenAI quota abuse.
- [ ] Ship `print()` logs to a real logger / cloud logging service.
- [ ] Set OpenAI usage cap in the OpenAI dashboard.
- [ ] Run uvicorn behind a reverse proxy (Caddy / nginx) for HTTPS.
- [ ] Verify the vector store is reachable in the `/health` probe (current probe is env-only).

## How the router decides which regions to search

At startup `router.py` parses every MD heading (`## N. <name>`, `#### N. <name>`) and
builds an in-memory set of all viloyat / tuman / mahalla names in BOTH Cyrillic and Latin.
On each request it lowercases the question and substring-matches against that index.

- Match in N regions → file_search restricted to those regions only (metadata filter).
- Match in 0 regions → no filter (treated as a country-wide query).
- Names < 4 chars are skipped (avoids junk matches).
