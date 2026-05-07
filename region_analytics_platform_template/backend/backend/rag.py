"""
RAG layer using OpenAI Responses API + the built-in `file_search` tool.

The router has already decided which viloyats are relevant; we pass that as a metadata
filter so the vector search only retrieves chunks from those regions. If the router
returned ALL 14 (no name match → global query), we omit the filter entirely.
"""
from __future__ import annotations
import asyncio
from typing import AsyncIterator, Any

from openai import AsyncOpenAI

from config import (
    OPENAI_API_KEY, RAG_MODEL, VECTOR_STORE_ID, RAG_TIMEOUT_SEC, VILOYATS,
)
from prompts import RAG_SYSTEM_PROMPT


_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _client


def _build_filters(selected_codes: list[str]) -> dict | None:
    """Build a vector-store metadata filter for `viloyat_code`.

    No filter (None) is returned when:
      - selected_codes is empty
      - selected_codes covers all 14 regions (treat as global, no filter needed)
    """
    if not selected_codes:
        return None
    if len(selected_codes) >= len(VILOYATS):
        return None
    if len(selected_codes) == 1:
        return {"type": "eq", "key": "viloyat_code", "value": selected_codes[0]}
    return {
        "type": "or",
        "filters": [
            {"type": "eq", "key": "viloyat_code", "value": code}
            for code in selected_codes
        ],
    }


async def stream_rag_answer(
    user_question: str,
    selected_viloyats: list[dict[str, Any]],
) -> AsyncIterator[str]:
    """Stream the final Latin-Uzbek answer chunk-by-chunk."""
    if not VECTOR_STORE_ID:
        yield (
            "[Konfiguratsiya xatoligi: VECTOR_STORE_ID .env faylda mavjud emas. "
            "Avval `python -m backend.ingest` ishga tushiring va olingan id ni .env ga qo'shing.]"
        )
        return

    client = _get_client()
    codes = [v["code"] for v in selected_viloyats]
    flt = _build_filters(codes)

    file_search_tool: dict[str, Any] = {
        "type": "file_search",
        "vector_store_ids": [VECTOR_STORE_ID],
        "max_num_results": 30,
    }
    if flt is not None:
        file_search_tool["filters"] = flt

    try:
        stream = await asyncio.wait_for(
            client.responses.create(
                model=RAG_MODEL,
                instructions=RAG_SYSTEM_PROMPT,
                input=user_question,
                tools=[file_search_tool],
                stream=True,
            ),
            timeout=RAG_TIMEOUT_SEC,
        )
        async for event in stream:
            etype = getattr(event, "type", None)
            if etype == "response.output_text.delta":
                delta = getattr(event, "delta", "")
                if delta:
                    yield delta
            elif etype == "response.error":
                err = getattr(event, "error", None)
                yield f"\n\n[Xatolik: {err}]"
            # Other events (tool calls, completed, etc.) are silently ignored — we only
            # surface model-generated text to the user.
    except asyncio.TimeoutError:
        yield "\n\n[Tizim javob berishda kechikdi. Iltimos, savolni qaytadan yuboring.]"
    except Exception as e:
        msg = str(e) or repr(e)
        yield f"\n\n[Xatolik: {type(e).__name__}: {msg}]"


async def run_rag_blocking(
    user_question: str,
    selected_viloyats: list[dict[str, Any]],
) -> str:
    chunks: list[str] = []
    async for piece in stream_rag_answer(user_question, selected_viloyats):
        chunks.append(piece)
    return "".join(chunks)
