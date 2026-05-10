"""Answer-style checks layered on top of `score_case`.

The deterministic scorer (`scorer.score_case`) already validates numeric
facts and NULL markers. This module adds *style* assertions on top so we
can also flag answers that are factually correct but read like a raw table
dump or leak internal terminology.

Returns a list of issue strings; an empty list means the answer passed all
style checks. The list is intentionally not boolean so callers can fold the
issues into the existing eval report.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from cerr_chatbot.query.answer import NULL_DISPLAY

# Internal architecture words that must never reach the user.
INTERNAL_TERMS: tuple[str, ...] = (
    "sql_guard",
    "schema_link",
    "import_run",
    "raw table",
    "raw tables",
    "planner",
    "validated_sql",
    "expected_result_shape",
    "executor",
)

# Latin alphabet check used to enforce default Uzbek Latin language. Cyrillic
# is allowed (source entity names) but the prose around them must be Latin.
_LATIN_RE = re.compile(r"[A-Za-z]")
_CYRILLIC_RE = re.compile(r"[Ѐ-ӿ]")
_TABLE_LINE_RE = re.compile(r"^\s*\|.*\|\s*$")
_SENTENCE_END_RE = re.compile(r"[.!?]")


def style_issues(
    actual_text: str,
    *,
    service_kind: str,
    user_question: str = "",
) -> list[str]:
    """Return list of style violations; empty means all checks passed."""
    issues: list[str] = []
    text = actual_text or ""
    lower = text.lower()

    # 1. Default user-facing language is Uzbek Latin. We require that at least
    #    one Latin character is present in any non-empty answer.
    if text.strip() and not _LATIN_RE.search(text):
        issues.append("answer has no Latin characters; expected Uzbek Latin prose")

    # 2. No internal architecture words.
    for term in INTERNAL_TERMS:
        if term in lower:
            issues.append(f"answer leaks internal term {term!r}")

    # 3. SQL result must include at least one explanatory sentence outside the
    #    markdown table; otherwise the answer is a raw table dump.
    if service_kind == "sql_result" and not _has_prose_sentence(text):
        issues.append("sql_result has no explanatory sentence outside the markdown table")

    # 4. Greetings must skip table/SQL output completely. Tables/code fences
    #    in a greeting answer are a strong sign the planner got involved.
    if service_kind == "greeting":
        if any(_TABLE_LINE_RE.match(line) for line in text.splitlines()):
            issues.append("greeting answer should not contain a markdown table")
        if "```" in text:
            issues.append("greeting answer should not contain a code block")

    return issues


def _has_prose_sentence(text: str) -> bool:
    """True if any non-table line has at least a few words AND ends a sentence
    or contains the missing-value marker.
    """
    for raw in text.splitlines():
        line = raw.strip()
        if not line or _TABLE_LINE_RE.match(line):
            continue
        # Skip lines that are headings / metadata / pure number summaries we
        # consider part of the table envelope.
        if line.startswith("Qaytarilgan qatorlar") or line.startswith("Faqat birinchi"):
            continue
        if NULL_DISPLAY in line:
            return True
        if _LATIN_RE.search(line) or _CYRILLIC_RE.search(line):
            words = [w for w in re.split(r"\s+", line) if w]
            if len(words) >= 3 and _SENTENCE_END_RE.search(line):
                return True
    return False


def merge_style_issues(base_reasons: Iterable[str], style_reasons: Iterable[str]) -> list[str]:
    return list(base_reasons) + [f"style: {r}" for r in style_reasons]


__all__ = ["INTERNAL_TERMS", "merge_style_issues", "style_issues"]
