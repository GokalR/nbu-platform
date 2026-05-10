"""Parse questions_uz_latn.md (or any compatible file) into EvalCase rows.

Format expected per section:

    ## N. Title
    **Question:** ...
    **Expected answer:** ...

The expected answer block runs from `**Expected answer:**` to the next `## `
header or end of file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_SECTION_RE = re.compile(
    r"^##\s+(?P<num>\d+)\.\s+(?P<title>.+?)\s*$",
    re.MULTILINE,
)
_QUESTION_RE = re.compile(
    r"\*\*Question:\*\*\s*(?P<q>.+?)(?=\n\*\*Expected answer:\*\*|\Z)",
    re.DOTALL,
)
_ANSWER_RE = re.compile(
    r"\*\*Expected answer:\*\*\s*(?P<a>.+)",
    re.DOTALL,
)


@dataclass(frozen=True)
class EvalCase:
    case_number: int
    title: str
    question: str
    expected_answer: str


def parse_questions_md(path: str | Path) -> list[EvalCase]:
    text = Path(path).read_text(encoding="utf-8")
    headers = list(_SECTION_RE.finditer(text))
    if not headers:
        return []

    cases: list[EvalCase] = []
    for idx, m in enumerate(headers):
        start = m.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        body = text[start:end].strip()
        q = _QUESTION_RE.search(body)
        a = _ANSWER_RE.search(body)
        if q is None or a is None:
            # Skip malformed sections rather than crash; counted by caller.
            continue
        cases.append(
            EvalCase(
                case_number=int(m.group("num")),
                title=m.group("title").strip(),
                question=q.group("q").strip(),
                expected_answer=a.group("a").strip(),
            )
        )
    return cases


__all__ = ["EvalCase", "parse_questions_md"]
