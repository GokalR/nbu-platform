"""Per-session in-memory store for recent analytical context.

Nothing in this module reads from or writes to disk, calls an LLM, or
executes SQL. `EvidencePipeline` may pass a snapshot to the evidence
planner as optional context, but SQL guard, executor, and narrator do not
receive raw memory.

Snapshots intentionally exclude SQL, executed rows, and the narrator's
final prose. A successful SQL turn stores the result shape (columns +
row_count). A clarify turn stores a compact pending-clarification marker,
so the user can answer the bot's clarification in the next message without
losing the place/topic they originally mentioned.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Protocol

from cerr_chatbot.query.evidence import EvidenceServiceResult


@dataclass(frozen=True)
class MemorySnapshot:
    """Compact record of the most recent relevant turn."""

    last_question: str
    last_resolved_question: str
    last_answer_type: str | None
    last_columns: tuple[str, ...]
    last_row_count: int
    last_result_summary: str
    created_at: str


class SessionMemoryStore(Protocol):
    def get(self, session_id: str) -> MemorySnapshot | None: ...
    def set(self, session_id: str, snapshot: MemorySnapshot) -> None: ...
    def clear(self, session_id: str) -> None: ...


class InMemorySessionMemoryStore:
    """Dict-backed `SessionMemoryStore`.

    No persistence. No SQLite. No vector DB. No long-term memory. Cleared
    when the process exits. A single lock guards the dict so a future
    concurrent web layer doesn't see torn writes.
    """

    def __init__(self) -> None:
        self._data: dict[str, MemorySnapshot] = {}
        self._lock = Lock()

    def get(self, session_id: str) -> MemorySnapshot | None:
        with self._lock:
            return self._data.get(session_id)

    def set(self, session_id: str, snapshot: MemorySnapshot) -> None:
        with self._lock:
            self._data[session_id] = snapshot

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)


def _summarize(columns: tuple[str, ...], row_count: int) -> str:
    return f"row_count={row_count}; columns={','.join(columns)}"


def _summarize_clarify(message: str) -> str:
    compact = " ".join(message.split())[:240]
    return f"pending_clarification=true; assistant_asked={compact}"


def build_snapshot_from_evidence_result(
    *,
    original_question: str,
    resolved_question: str,
    result: EvidenceServiceResult,
) -> MemorySnapshot | None:
    """Build a snapshot for a successful or pending analytical turn.

    SQL result snapshots remember only the shape of the executed evidence.
    Clarify snapshots remember the pending topic so a user answer like
    "umumiy ma'lumot" can continue the previous question. Returns None for
    no_data / unsupported / planner_error / execution_error /
    conversational kinds. SQL text and executed rows are intentionally
    dropped.
    """
    if result.kind == "clarify":
        return MemorySnapshot(
            last_question=original_question,
            last_resolved_question=resolved_question or original_question,
            last_answer_type=result.kind,
            last_columns=(),
            last_row_count=0,
            last_result_summary=_summarize_clarify(result.user_message),
            created_at=datetime.now(UTC).isoformat(),
        )
    if result.kind != "sql_result" or result.pack is None:
        return None
    columns = tuple(result.pack.primary.columns)
    row_count = result.pack.primary.row_count
    return MemorySnapshot(
        last_question=original_question,
        last_resolved_question=resolved_question,
        last_answer_type=result.kind,
        last_columns=columns,
        last_row_count=row_count,
        last_result_summary=_summarize(columns, row_count),
        created_at=datetime.now(UTC).isoformat(),
    )


__all__ = [
    "InMemorySessionMemoryStore",
    "MemorySnapshot",
    "SessionMemoryStore",
    "build_snapshot_from_evidence_result",
]
