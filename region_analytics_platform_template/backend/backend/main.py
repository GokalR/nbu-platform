"""
FastAPI backend (API-only, no frontend).

Endpoints:
  GET  /health        -> health probe + active model + region count
  POST /chat          -> JSON in, JSON out (blocking; full answer)
  GET  /chat/stream   -> Server-Sent-Events stream (token-by-token)
  GET  /docs          -> auto-generated OpenAPI UI (FastAPI default)
  GET  /redoc         -> auto-generated ReDoc UI (FastAPI default)

Run:
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations
import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config import RAG_MODEL, VECTOR_STORE_ID, VILOYATS
from orchestrator import answer_question, answer_question_blocking


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Cap to protect from runaway requests.
MAX_QUESTION_CHARS = 1500

# CORS: allow * by default (this is an internal analytics API). Override via env.
# Comma-separated list, e.g.  CORS_ORIGINS=https://app.example.com,https://admin.example.com
_cors_env = os.getenv("CORS_ORIGINS", "*").strip()
if _cors_env == "*":
    CORS_ORIGINS = ["*"]
else:
    CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="O'zbekiston Hududiy Tahlil API",
    description="Backend for the regional analytics chatbot (RAG via OpenAI File Search).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_CHARS)


class ChatResponse(BaseModel):
    question: str
    answer: str
    router_selected: list[str]
    router_matched: list[str]
    total_elapsed_s: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_question(q: str) -> str:
    q = (q or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty question.")
    if len(q) > MAX_QUESTION_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Question too long (max {MAX_QUESTION_CHARS} chars).",
        )
    return q


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "vector_store_configured": bool(VECTOR_STORE_ID),
        "rag_model": RAG_MODEL,
        "region_count": len(VILOYATS),
        "regions": [v["name_latin"] for v in VILOYATS],
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_blocking(req: ChatRequest):
    """Blocking endpoint — waits for the full answer, returns JSON."""
    question = _validate_question(req.question)
    result = await answer_question_blocking(question)
    return JSONResponse(result)


@app.get("/chat/stream")
async def chat_stream(question: str, request: Request):
    """SSE stream — emits status events + token deltas + a final 'done' event."""
    question = _validate_question(question)

    async def event_generator():
        async for event in answer_question(question):
            if await request.is_disconnected():
                break
            payload = json.dumps(event, ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
