"""AI Advisor (regional chatbot) routes.

Endpoints (all under /api/ai-advisor):
  GET  /health        diagnostic — is the vector store configured? which model?
  POST /chat          blocking JSON in/out
  GET  /chat/stream   Server-Sent-Events token stream
"""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from ..config import get_settings
from ..services.regional_chat import (
    answer_question,
    answer_question_blocking,
    VILOYATS,
)

MAX_QUESTION_CHARS = 1500

router = APIRouter(prefix="/ai-advisor", tags=["ai-advisor"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_CHARS)


class ChatResponse(BaseModel):
    question: str
    answer: str
    router_selected: list[str]
    router_matched: list[str]
    total_elapsed_s: float


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


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "ok": True,
        "vector_store_configured": bool(settings.vector_store_id_clean),
        "openai_configured": bool(settings.openai_api_key_clean),
        "rag_model": settings.rag_model_clean,
        "region_count": len(VILOYATS),
        "regions": [v["name_latin"] for v in VILOYATS],
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_blocking(req: ChatRequest):
    question = _validate_question(req.question)
    result = await answer_question_blocking(question)
    return JSONResponse(result)


@router.get("/chat/stream")
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
