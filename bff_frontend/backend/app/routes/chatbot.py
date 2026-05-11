"""Thin proxy to the cerr-chatbot service.

The chatbot runs as a separate Railway service (private network). Keeping it
behind the BFF means: no extra CORS surface, BFF can stamp auth/user context
later, and the chatbot URL is centralised in BFF settings.

Endpoints (all under /api/chatbot):
  GET  /health        forwards to chatbot /health
  POST /chat          forwards body { message, session_id?, max_rows? } to /chat
  GET  /chat/stream   forwards SSE from chatbot /chat/stream (token-by-token UI)
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
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


@router.get("/chat/stream")
async def chat_stream(
    request: Request,
    message: str = Query(..., min_length=1, max_length=4000),
    session_id: str | None = Query(default=None, max_length=128),
    max_rows: int = Query(default=10, ge=1, le=100),
) -> StreamingResponse:
    """Pass the upstream chatbot SSE stream through unchanged.

    The streaming timeout is longer than the blocking /chat endpoint because
    the narrator can take 20+ seconds on advisory questions, and the client
    needs the connection to stay open until the `done` event arrives.
    """
    settings = get_settings()
    base = _base_url()
    params = {"message": message, "max_rows": max_rows}
    if session_id:
        params["session_id"] = session_id

    async def _proxy() -> "AsyncIterator[bytes]":  # type: ignore[name-defined]
        timeout = httpx.Timeout(
            connect=10.0,
            read=settings.chatbot_timeout_sec * 5,
            write=10.0,
            pool=10.0,
        )
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("GET", f"{base}/chat/stream", params=params) as upstream:
                if upstream.status_code >= 500:
                    err = (
                        f'event: error\ndata: {{"error":"upstream_{upstream.status_code}"}}\n\n'
                    )
                    yield err.encode("utf-8")
                    return
                async for chunk in upstream.aiter_raw():
                    if await request.is_disconnected():
                        break
                    if chunk:
                        yield chunk

    return StreamingResponse(
        _proxy(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
