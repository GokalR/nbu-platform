"""Thin proxy to the cerr-chatbot service + Phase 2D-1 chat history.

Layout:
  GET  /chatbot/health                       upstream health
  POST /chatbot/chat                         (legacy/blocking) — persisted
  GET  /chatbot/chat/stream                  SSE — persisted
  GET  /chatbot/sessions                     list current user's threads
  POST /chatbot/sessions                     create a new empty thread
  GET  /chatbot/sessions/{id}                load one thread's messages
  DELETE /chatbot/sessions/{id}              delete a thread + its messages

Auth: all session endpoints + the chat endpoints require a valid JWT. The
frontend already gates the `/chatbot` page behind login so this is just
asking for the token that's already in localStorage.

Session ids are UUIDs and double as the upstream chatbot's `session_id`
parameter — so the chatbot-api's short-term ephemeral memory continues to
work for the active thread; the BFF only adds persistence on top.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_auth
from ..config import get_settings
from ..db_async import get_db
from ..models_chatbot import ChatbotMessage, ChatbotSession
from ..models_education import User

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


# ---------------------------------------------------------------------------
# Request / response shapes
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    max_rows: int = Field(default=10, ge=1, le=100)


class CreateSessionResponse(BaseModel):
    id: str
    created_at: datetime


class SessionListItem(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    last_message_at: datetime


class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    sql: str | None = None
    row_count: int | None = None
    kind: str | None = None
    created_at: datetime


class SessionDetail(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    last_message_at: datetime
    messages: list[MessageItem]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _base_url() -> str:
    url = get_settings().chatbot_api_url_clean
    if not url:
        raise HTTPException(status_code=503, detail="chatbot_not_configured")
    return url


def _coerce_uuid(value: str, label: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise HTTPException(status_code=400, detail=f"invalid_{label}") from exc


async def _load_owned_session(
    db: AsyncSession, session_id: str, user_id: uuid.UUID
) -> ChatbotSession:
    sid = _coerce_uuid(session_id, "session_id")
    result = await db.execute(
        select(ChatbotSession).where(
            ChatbotSession.id == sid, ChatbotSession.user_id == user_id
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session


async def _persist_user_message(
    db: AsyncSession,
    session: ChatbotSession,
    content: str,
) -> None:
    """Save the user's message + set title if this is the first turn."""
    db.add(
        ChatbotMessage(
            session_id=session.id,
            role="user",
            content=content,
        )
    )
    session.last_message_at = _utcnow()
    if not session.title:
        # First user message becomes the thread title (truncated for sidebar).
        session.title = content[:200]
    await db.commit()


async def _persist_assistant_message(
    db: AsyncSession,
    session: ChatbotSession,
    *,
    content: str,
    sql: str | None,
    row_count: int | None,
    kind: str | None,
) -> None:
    db.add(
        ChatbotMessage(
            session_id=session.id,
            role="assistant",
            content=content,
            sql_text=sql,
            row_count=row_count,
            kind=kind,
        )
    )
    session.last_message_at = _utcnow()
    await db.commit()


# ---------------------------------------------------------------------------
# Health (public — no auth)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Session management (auth required)
# ---------------------------------------------------------------------------


@router.get("/sessions", response_model=list[SessionListItem])
async def list_sessions(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> list[SessionListItem]:
    """Return the current user's threads, newest first."""
    result = await db.execute(
        select(ChatbotSession)
        .where(ChatbotSession.user_id == user.id)
        .order_by(desc(ChatbotSession.last_message_at))
        .limit(200)
    )
    sessions = result.scalars().all()
    return [
        SessionListItem(
            id=str(s.id),
            title=s.title,
            created_at=s.created_at,
            last_message_at=s.last_message_at,
        )
        for s in sessions
    ]


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> CreateSessionResponse:
    """Create an empty thread. Title is filled when the user sends the first message."""
    session = ChatbotSession(user_id=user.id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return CreateSessionResponse(id=str(session.id), created_at=session.created_at)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> SessionDetail:
    session = await _load_owned_session(db, session_id, user.id)
    result = await db.execute(
        select(ChatbotMessage)
        .where(ChatbotMessage.session_id == session.id)
        .order_by(ChatbotMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return SessionDetail(
        id=str(session.id),
        title=session.title,
        created_at=session.created_at,
        last_message_at=session.last_message_at,
        messages=[
            MessageItem(
                id=str(m.id),
                role=m.role,
                content=m.content,
                sql=m.sql_text,
                row_count=m.row_count,
                kind=m.kind,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict:
    session = await _load_owned_session(db, session_id, user.id)
    await db.delete(session)
    await db.commit()
    return {"ok": True, "id": session_id}


# ---------------------------------------------------------------------------
# Blocking /chat — persisted around the upstream call
# ---------------------------------------------------------------------------


@router.post("/chat")
async def chat(
    req: ChatRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Persist user message → forward to chatbot-api → persist assistant response."""
    settings = get_settings()
    base = _base_url()

    if not req.session_id:
        raise HTTPException(status_code=400, detail="session_id_required")
    session = await _load_owned_session(db, req.session_id, user.id)
    await _persist_user_message(db, session, req.message)

    try:
        async with httpx.AsyncClient(timeout=settings.chatbot_timeout_sec) as client:
            resp = await client.post(
                f"{base}/chat",
                json={
                    "message": req.message,
                    "session_id": str(session.id),
                    "max_rows": req.max_rows,
                },
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail=f"chatbot_timeout: {exc}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"chatbot_unreachable: {exc}") from exc
    if resp.status_code >= 500:
        raise HTTPException(status_code=502, detail=f"chatbot_upstream_{resp.status_code}")

    data: dict[str, Any] = resp.json()
    await _persist_assistant_message(
        db,
        session,
        content=data.get("answer") or "",
        sql=data.get("sql"),
        row_count=data.get("row_count"),
        kind=data.get("kind"),
    )
    return data


# ---------------------------------------------------------------------------
# SSE /chat/stream — persists user message before, assistant message after `done`
# ---------------------------------------------------------------------------


@router.get("/chat/stream")
async def chat_stream(
    request: Request,
    message: str = Query(..., min_length=1, max_length=4000),
    session_id: str | None = Query(default=None, max_length=128),
    max_rows: int = Query(default=10, ge=1, le=100),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """SSE proxy with persistence. The user message is saved up-front; the
    assistant message is saved when the upstream `done` event arrives.

    We sniff (don't transform) the SSE frames: each `event: token` adds to a
    running answer buffer, and each `event: done` carries the canonical
    answer + sql + row_count which we persist as the final assistant
    message. Frames are forwarded byte-for-byte to the browser.
    """
    settings = get_settings()
    base = _base_url()

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id_required")
    session = await _load_owned_session(db, session_id, user.id)
    await _persist_user_message(db, session, message)

    params = {"message": message, "session_id": str(session.id), "max_rows": max_rows}

    # Pull session attributes out of the ORM session before we hand it back
    # to the dependency framework — the SSE generator outlives the request's
    # `db` lifespan, so we cannot use the session inside it. We open a fresh
    # session inside `_proxy` to write the assistant message.
    session_pk = session.id

    async def _proxy():
        from ..db_async import async_session

        buffer: list[str] = []
        done_payload: dict[str, Any] | None = None
        timeout = httpx.Timeout(
            connect=10.0,
            read=settings.chatbot_timeout_sec * 5,
            write=10.0,
            pool=10.0,
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "GET", f"{base}/chat/stream", params=params
                ) as upstream:
                    if upstream.status_code >= 500:
                        err = (
                            f'event: error\ndata: {{"error":"upstream_{upstream.status_code}"}}\n\n'
                        )
                        yield err.encode("utf-8")
                        return
                    # SSE frames are CR/LF-terminated; aiter_lines yields one
                    # line at a time so we can sniff event types cleanly.
                    current_event = "message"
                    pending_data = ""
                    async for line in upstream.aiter_lines():
                        if await request.is_disconnected():
                            break
                        if line.startswith("event:"):
                            current_event = line[6:].strip()
                            yield (line + "\n").encode("utf-8")
                            continue
                        if line.startswith("data:"):
                            pending_data = line[5:].strip()
                            # Sniff for persistence.
                            if current_event == "token":
                                try:
                                    import json as _json

                                    tok = _json.loads(pending_data).get("text", "")
                                    if isinstance(tok, str):
                                        buffer.append(tok)
                                except Exception:
                                    pass
                            elif current_event == "done":
                                try:
                                    import json as _json

                                    done_payload = _json.loads(pending_data)
                                except Exception:
                                    done_payload = None
                            yield (line + "\n").encode("utf-8")
                            continue
                        # Empty line ends an SSE frame.
                        yield (line + "\n").encode("utf-8")
        finally:
            # Best-effort persistence: prefer the canonical answer from the
            # done payload (server-side trimmed/transliterated), fall back to
            # the accumulated tokens if the stream died before `done`.
            answer_text = ""
            sql = None
            row_count = None
            kind = None
            if isinstance(done_payload, dict):
                answer_text = done_payload.get("answer") or ""
                sql = done_payload.get("sql")
                row_count = done_payload.get("row_count")
                kind = done_payload.get("kind")
            if not answer_text and buffer:
                answer_text = "".join(buffer)
            if answer_text:
                try:
                    async with async_session() as fresh_db:
                        # Update last_message_at + insert assistant row.
                        sess_res = await fresh_db.execute(
                            select(ChatbotSession).where(ChatbotSession.id == session_pk)
                        )
                        fresh_session = sess_res.scalar_one_or_none()
                        if fresh_session is not None:
                            fresh_db.add(
                                ChatbotMessage(
                                    session_id=fresh_session.id,
                                    role="assistant",
                                    content=answer_text,
                                    sql_text=sql,
                                    row_count=row_count,
                                    kind=kind,
                                )
                            )
                            fresh_session.last_message_at = _utcnow()
                            await fresh_db.commit()
                except Exception:
                    # Persistence failure must not break the user's UX.
                    pass

    return StreamingResponse(
        _proxy(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
