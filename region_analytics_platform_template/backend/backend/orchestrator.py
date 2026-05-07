"""
Orchestrator: deterministic name router → file_search RAG → stream answer.
"""
from __future__ import annotations
import time
from typing import AsyncIterator, Any

from router import route as route_question
from rag import stream_rag_answer, run_rag_blocking


def _log_routing(question: str, selected: list[dict], matched: list[str]) -> None:
    print(f"[router] Q: {question[:120]}")
    print(
        f"[router] selected ({len(selected)}/14): "
        + ", ".join(v["name_latin"] for v in selected)
    )
    if matched:
        print(f"[router] matched terms: {matched}")
    else:
        print("[router] no name match → no metadata filter (global search)")


async def answer_question(user_question: str) -> AsyncIterator[dict[str, Any]]:
    """Yield SSE-style events:
      {"type":"status","stage":"routed", ...}
      {"type":"status","stage":"rag_started"}
      {"type":"token","text":"..."} (many)
      {"type":"done","elapsed_s":...}
    """
    if not user_question or not user_question.strip():
        yield {"type": "token", "text": "Iltimos, savol yozing."}
        yield {"type": "done", "elapsed_s": 0.0}
        return

    t0 = time.time()
    selected, matched = route_question(user_question)
    _log_routing(user_question, selected, matched)
    yield {
        "type": "status", "stage": "routed",
        "selected": [v["name_latin"] for v in selected],
        "matched": matched,
        "n": len(selected),
    }

    yield {"type": "status", "stage": "rag_started"}
    async for chunk in stream_rag_answer(user_question, selected):
        yield {"type": "token", "text": chunk}

    yield {"type": "done", "elapsed_s": round(time.time() - t0, 2)}


async def answer_question_blocking(user_question: str) -> dict[str, Any]:
    t0 = time.time()
    selected, matched = route_question(user_question)
    _log_routing(user_question, selected, matched)
    answer = await run_rag_blocking(user_question, selected)
    return {
        "question": user_question,
        "answer": answer,
        "router_selected": [v["name_latin"] for v in selected],
        "router_matched": matched,
        "total_elapsed_s": round(time.time() - t0, 2),
    }
