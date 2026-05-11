"""Pluggable answer pipelines.

A `Pipeline` accepts a user question and returns a JSON-safe dict with a
single user-visible answer plus metadata (SQL, row count, columns, debug
notes). Two implementations:

- `LegacyPipeline`     — `QueryService.ask()` + a `Narrator`. Existing
                          single-SQL path. Default.
- `EvidencePipeline`   — `evidence_ask()` + `EvidenceLlmNarrator`. New
                          multi-SQL path with primary + context queries.

`make_pipeline_from_settings(engine, settings)` builds the right pipeline
from `Settings.query_pipeline_mode`. Both pipelines yield the same dict
shape so transports and the eval runner do not need to know which is in use.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol

from sqlalchemy import Engine

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.query.evidence import (
    EvidencePlanner,
    EvidenceServiceResult,
    evidence_ask,
)
from cerr_chatbot.query.evidence_narrator import EvidenceLlmNarrator
from cerr_chatbot.query.narrator import (
    DeterministicNarrator,
    Narrator,
    make_narrator_from_settings,
)
from cerr_chatbot.query.service import (
    Planner,
    QueryService,
    QueryServiceResult,
)
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
    SessionMemoryStore,
    build_snapshot_from_evidence_result,
)

_ALLOWED_MEMORY_MODES = ("off", "ephemeral")

EMPTY_QUESTION_RESPONSE: dict[str, Any] = {
    "ok": False,
    "kind": "empty_question",
    "answer": "Savol yozing.",
    "sql": None,
    "row_count": 0,
    "columns": [],
    "debug_notes": [],
}


class Pipeline(Protocol):
    def answer(
        self,
        question: str,
        *,
        max_rows: int = 10,
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> dict[str, Any]: ...

    def answer_stream(
        self,
        question: str,
        *,
        max_rows: int = 10,
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> Iterator[dict[str, Any]]: ...


# ---------------------------------------------------------------------------
# Legacy single-SQL path
# ---------------------------------------------------------------------------


@dataclass
class LegacyPipeline:
    service: QueryService
    narrator: Narrator = field(default_factory=DeterministicNarrator)

    def answer_stream(
        self,
        question: str,
        *,
        max_rows: int = 10,
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Streaming wrapper for the legacy single-SQL path.

        The legacy narrator is deterministic markdown (no LLM call), so there
        is nothing to stream token-by-token. We emit a single status event,
        compute the full answer, and emit one done event so the SSE consumer
        sees the same protocol as the evidence pipeline.
        """
        result = self.answer(
            question,
            max_rows=max_rows,
            include_debug=include_debug,
            session_id=session_id,
        )
        yield {"type": "status", "stage": "planning", "message": "Javob hisoblanmoqda..."}
        text = result.get("answer", "")
        if text:
            yield {"type": "token", "text": text}
        yield {"type": "done", **result}

    def answer(
        self,
        question: str,
        *,
        max_rows: int = 10,
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        cleaned = question.strip()
        if not cleaned:
            return dict(EMPTY_QUESTION_RESPONSE)

        _ = session_id  # legacy path has no memory store
        result: QueryServiceResult = self.service.ask(cleaned)
        ans = self.narrator.narrate(result, max_rows=max_rows)
        return {
            "ok": result.kind == "sql_result",
            "kind": result.kind,
            "answer": ans.text,
            "sql": ans.sql,
            "row_count": ans.row_count,
            "columns": list(ans.columns),
            "debug_notes": list(result.debug_notes) if include_debug else [],
            "pipeline": "legacy",
        }


# ---------------------------------------------------------------------------
# Evidence multi-SQL path
# ---------------------------------------------------------------------------


@dataclass
class EvidencePipeline:
    engine: Engine
    planner: EvidencePlanner
    narrator: EvidenceLlmNarrator | None = None
    memory_store: SessionMemoryStore | None = None

    def answer_stream(
        self,
        question: str,
        *,
        max_rows: int = 10,
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield SSE event dicts as the pipeline runs.

        Events match `EvidenceLlmNarrator.narrate_stream`:
          {"type": "status", "stage": "planning|executing|narrating", "message": "..."}
          {"type": "token",  "text": "..."}
          {"type": "done",   "kind": "...", "answer": "...", "sql": "...",
                              "row_count": N, "columns": [...], "pipeline": "evidence"}

        Empty question short-circuits with one done event.
        """
        cleaned = question.strip()
        if not cleaned:
            yield {"type": "done", **EMPTY_QUESTION_RESPONSE, "pipeline": "evidence"}
            return

        yield {
            "type": "status",
            "stage": "planning",
            "message": "So'rovingiz rejalashtirilmoqda...",
        }

        prior_snapshot = (
            self.memory_store.get(session_id)
            if (self.memory_store is not None and session_id)
            else None
        )
        result: EvidenceServiceResult = evidence_ask(
            self.engine,
            self.planner,
            cleaned,
            memory_snapshot=prior_snapshot,
        )

        # Persist memory snapshot (matches the non-streaming path).
        if self.memory_store is not None and session_id:
            resolved = result.pack.question if result.pack is not None else cleaned
            snapshot = build_snapshot_from_evidence_result(
                original_question=cleaned,
                resolved_question=resolved,
                result=result,
            )
            if snapshot is not None:
                self.memory_store.set(session_id, snapshot)

        if result.kind != "sql_result" or result.pack is None:
            # No data path — emit user_message in a single done.
            yield {
                "type": "done",
                "kind": result.kind,
                "ok": False,
                "answer": result.user_message,
                "sql": None,
                "row_count": 0,
                "columns": [],
                "pipeline": "evidence",
            }
            return

        yield {
            "type": "status",
            "stage": "executing",
            "message": (
                f"{result.pack.primary.row_count} ta yozuv topildi. "
                "Javob tayyorlanmoqda..."
            ),
        }

        narrator = self.narrator or EvidenceLlmNarrator()
        final_done: dict[str, Any] | None = None
        for event in narrator.narrate_stream(result):
            if event.get("type") == "done":
                # Merge narrator's done with pipeline metadata; defer emit
                # until after the loop so we always emit one terminal event.
                final_done = {
                    "type": "done",
                    "ok": event.get("kind") == "sql_result",
                    "kind": event.get("kind"),
                    "answer": event.get("answer", ""),
                    "sql": event.get("sql"),
                    "row_count": event.get("row_count", 0),
                    "columns": event.get("columns", []),
                    "pipeline": "evidence",
                }
            else:
                yield event

        if final_done is None:
            final_done = {
                "type": "done",
                "ok": True,
                "kind": "sql_result",
                "answer": "",
                "sql": result.pack.primary.sql,
                "row_count": result.pack.primary.row_count,
                "columns": list(result.pack.primary.columns),
                "pipeline": "evidence",
            }
        yield final_done

    def answer(
        self,
        question: str,
        *,
        max_rows: int = 10,  # consumed by EvidenceLlmNarrator only via prompt cap
        include_debug: bool = True,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        cleaned = question.strip()
        if not cleaned:
            return dict(EMPTY_QUESTION_RESPONSE)

        prior_snapshot = (
            self.memory_store.get(session_id)
            if (self.memory_store is not None and session_id)
            else None
        )
        result: EvidenceServiceResult = evidence_ask(
            self.engine,
            self.planner,
            cleaned,
            memory_snapshot=prior_snapshot,
        )
        nar = self.narrator or EvidenceLlmNarrator()
        ans = nar.narrate(result)
        debug_notes: list[str] = []
        if include_debug:
            if prior_snapshot is not None:
                debug_notes.append("memory_snapshot_sent_to_planner=true")
            debug_notes.extend(result.debug_notes)
            if result.pack is not None:
                for ctx in result.pack.context:
                    if ctx.error:
                        debug_notes.append(f"context[{ctx.purpose}]: {ctx.error}")
        if self.memory_store is not None and session_id:
            resolved = result.pack.question if result.pack is not None else cleaned
            snapshot = build_snapshot_from_evidence_result(
                original_question=cleaned,
                resolved_question=resolved,
                result=result,
            )
            if snapshot is not None:
                self.memory_store.set(session_id, snapshot)
        return {
            "ok": result.kind == "sql_result",
            "kind": result.kind,
            "answer": ans.text,
            "sql": ans.sql,
            "row_count": ans.row_count,
            "columns": list(ans.columns),
            "debug_notes": debug_notes,
            "pipeline": "evidence",
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def make_pipeline_from_settings(
    engine: Engine,
    *,
    legacy_planner: Planner | None = None,
    evidence_planner: EvidencePlanner | None = None,
    settings: Settings | None = None,
) -> Pipeline:
    """Build the runtime pipeline based on `settings.query_pipeline_mode`.

    The CLI provides the LLM planner adapters; tests can inject stubs.
    """
    cfg = settings or get_settings()
    mode = (cfg.query_pipeline_mode or "legacy").strip().lower()
    memory_mode = (cfg.query_memory_mode or "off").strip().lower()
    if memory_mode not in _ALLOWED_MEMORY_MODES:
        raise ValueError(
            f"Unsupported QUERY_MEMORY_MODE={memory_mode!r}; "
            f"expected one of {_ALLOWED_MEMORY_MODES}"
        )
    if mode == "evidence":
        if evidence_planner is None:
            raise ValueError(
                "QUERY_PIPELINE_MODE=evidence requires an EvidencePlanner; "
                "build one with make_evidence_planner_from_settings()."
            )
        ev_narrator = EvidenceLlmNarrator(settings=cfg)
        memory_store: SessionMemoryStore | None = (
            InMemorySessionMemoryStore() if memory_mode == "ephemeral" else None
        )
        return EvidencePipeline(
            engine=engine,
            planner=evidence_planner,
            narrator=ev_narrator,
            memory_store=memory_store,
        )
    if mode == "legacy":
        if legacy_planner is None:
            raise ValueError(
                "QUERY_PIPELINE_MODE=legacy requires a Planner; build one with "
                "make_planner_from_settings()."
            )
        legacy_narrator = make_narrator_from_settings(cfg)
        service = QueryService(engine, legacy_planner)
        return LegacyPipeline(service=service, narrator=legacy_narrator)
    raise ValueError(f"Unsupported QUERY_PIPELINE_MODE={mode!r}; expected 'legacy' or 'evidence'")


__all__ = [
    "EMPTY_QUESTION_RESPONSE",
    "EvidencePipeline",
    "LegacyPipeline",
    "Pipeline",
    "make_pipeline_from_settings",
]
