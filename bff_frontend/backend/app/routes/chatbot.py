"""Thin proxy to the cerr-chatbot service.

The chatbot runs as a separate Railway service (private network). Keeping it
behind the BFF means: no extra CORS surface, BFF can stamp auth/user context
later, and the chatbot URL is centralised in BFF settings.

Endpoints (all under /api/chatbot):
  GET  /health   forwards to chatbot /health
  POST /chat     forwards body { message, session_id?, max_rows? } to /chat
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..config import get_settings

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    max_rows: int = Field(default=10, ge=1, le=100)


def _base_url() -> str:
    url = get_settings().chatbot_api_url_clean
    if not url:
        raise HTTPException(status_code=503, detail="chatbot_not_configured")
    return url


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    base = settings.chatbot_api_url_clean
    if not base:
        return {"ok": False, "configured": False}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base}/health")
            return {"ok": resp.status_code == 200, "configured": True, "upstream": resp.json()}
    except Exception as exc:
        return {"ok": False, "configured": True, "error": str(exc)}


@router.post("/chat")
async def chat(req: ChatRequest) -> dict:
    settings = get_settings()
    base = _base_url()
    try:
        async with httpx.AsyncClient(timeout=settings.chatbot_timeout_sec) as client:
            resp = await client.post(f"{base}/chat", json=req.model_dump())
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail=f"chatbot_timeout: {exc}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"chatbot_unreachable: {exc}") from exc
    if resp.status_code >= 500:
        raise HTTPException(status_code=502, detail=f"chatbot_upstream_{resp.status_code}")
    return resp.json()
