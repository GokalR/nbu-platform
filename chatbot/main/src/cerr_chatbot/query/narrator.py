"""AnswerNarrator: turn SQL result rows into a natural Uzbek Latin answer.

Hard rules enforced by this module:
- Numeric facts must come ONLY from the executed SQL result rows that are
  already in `QueryServiceResult.rows`. The narrator never invents numbers
  and never re-runs SQL.
- NULL must be rendered as the Uzbek Latin missing-value phrase, not 0.
- Source entity names (region_name_cyr, district_name_cyr, mahalla_name_cyr,
  Cyrillic labels) must pass through unchanged.
- Internal architecture words (sql_guard, planner, view, raw table) must
  not appear in user-facing prose.

Two implementations are provided:

`DeterministicNarrator` reuses the existing markdown-table composer prose
so the chatbot still works when no LLM key is configured.

`LlmNarrator` calls a `ProviderCall` (same shape as the planner adapter) to
turn the rows into a natural-language answer. The full row table and a list
of allowed numeric tokens are sent to the LLM. The LLM only sees rows; SQL
text is provided as hidden debug context only.

The selection is driven by `Settings.answer_narrator_mode`:
- "deterministic" (default): always use DeterministicNarrator.
- "llm":                     use LlmNarrator if a key is configured, else fall
                             back to DeterministicNarrator.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Protocol

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.query.answer import (
    NULL_DISPLAY,
    Answer,
    compose_answer,
)
from cerr_chatbot.query.llm_planner import ProviderCall, _resolve_provider
from cerr_chatbot.query.narrator_safety import (
    EnvelopeParseError,
    extract_row_numbers,
    is_answer_grounded,
    normalize_token,
    parse_envelope,
    verify_calculation,
)
from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG
from cerr_chatbot.query.service import QueryServiceResult

log = logging.getLogger(__name__)


class Narrator(Protocol):
    def narrate(self, result: QueryServiceResult, *, max_rows: int = 10) -> Answer: ...


# Forbidden internal terms. If the LLM leaks any of these, we fall back to
# the deterministic composer rather than ship leaky prose to the user.
_FORBIDDEN_INTERNAL_TERMS: tuple[str, ...] = (
    "sql_guard",
    "planner",
    "import_run",
    "semantic view",
    "raw table",
    "schema_link",
    "executor",
    "validated_sql",
    "expected_result_shape",
)


# ---------------------------------------------------------------------------
# Deterministic fallback
# ---------------------------------------------------------------------------


@dataclass
class DeterministicNarrator:
    """Wraps `compose_answer` so the API matches `Narrator`.

    Behavior is unchanged: prints intro + markdown table + truncation note
    in Uzbek Latin. Used when no LLM key is configured or when the LLM
    fallback path triggers.
    """

    def narrate(self, result: QueryServiceResult, *, max_rows: int = 10) -> Answer:
        return compose_answer(result, max_rows=max_rows)


# ---------------------------------------------------------------------------
# LLM-backed narrator
# ---------------------------------------------------------------------------


class NarratorError(RuntimeError):
    """LLM narrator failed; caller should fall back to deterministic."""


@dataclass
class LlmNarrator:
    """LLM-backed natural-language narrator.

    Inputs sent to the LLM:
    - original user question
    - service_kind
    - column names + plain descriptions (from semantic catalog if known)
    - row_count
    - the SQL result rows (not SQL text)
    - data quality / missing-value warnings as needed
    - strict factual rules

    Outputs are checked for forbidden internal terms and for any numeric
    tokens not present in the rows themselves; either condition causes a
    safe fallback to the deterministic composer.
    """

    settings: Settings | None = None
    provider_call: ProviderCall | None = None
    fallback: Narrator | None = None
    log_full_prompt: bool = False
    max_rows_in_prompt: int = 50

    def narrate(self, result: QueryServiceResult, *, max_rows: int = 10) -> Answer:
        fallback = self.fallback or DeterministicNarrator()

        # Conversational + non-SQL kinds are already user-friendly text.
        if result.kind != "sql_result":
            return fallback.narrate(result, max_rows=max_rows)

        cfg = self.settings or get_settings()
        try:
            provider, model, api_key = _resolve_provider(cfg, self.provider_call)
        except Exception as exc:  # noqa: BLE001 - missing key, etc.
            log.info("narrator falling back to deterministic: %s", exc)
            return fallback.narrate(result, max_rows=max_rows)

        prompt = build_narrator_prompt(result, max_rows=self.max_rows_in_prompt)
        if self.log_full_prompt:
            log.info("narrator prompt: %s", prompt)
        else:
            log.info("narrator prompt built (%d chars)", len(prompt))

        try:
            text = provider(model, prompt, api_key)
        except Exception as exc:  # noqa: BLE001 - any provider failure
            log.warning("narrator provider failed; falling back: %s", exc)
            return fallback.narrate(result, max_rows=max_rows)

        cleaned = (text or "").strip()
        if not cleaned:
            return fallback.narrate(result, max_rows=max_rows)

        # Envelope path (v2): JSON answer + verified derived calculations.
        answer_text = _process_envelope_answer(cleaned, result)
        if answer_text is None:
            # Plain-text path (back-compat): no derived calcs allowed.
            if not _is_safe_narrator_output(cleaned, result):
                log.warning("narrator output failed safety checks; falling back")
                return fallback.narrate(result, max_rows=max_rows)
            answer_text = cleaned

        if _has_internal_term(answer_text):
            log.warning("narrator output leaks internal terms; falling back")
            return fallback.narrate(result, max_rows=max_rows)

        return Answer(
            text=answer_text,
            kind=result.kind,
            sql=result.sql,
            row_count=result.row_count,
            columns=result.columns,
        )


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


_FEW_SHOT_EXAMPLE = """\
EXAMPLE
USER QUESTION: Qaysi viloyatda aholi eng ko'p?
ROWS:
[["A", 4000], ["B", 3000], ["C", 1000]]

EXPECTED REPLY (this exact JSON shape):
{
  "answer": "A eng katta hudud: 4000 kishi. B dan 1000 kishiga, ya'ni 33.3% ko'p. Top uchtalik jami 8000 kishini tashkil qiladi va A bu yig'indining 50% ulushiga ega.",
  "derived_calculations": [
    {"output_value": "1000", "formula": "4000 - 3000", "input_values": [4000, 3000]},
    {"output_value": "33.3", "formula": "(4000 - 3000) / 3000 * 100", "input_values": [4000, 3000]},
    {"output_value": "8000", "formula": "4000 + 3000 + 1000", "input_values": [4000, 3000, 1000]},
    {"output_value": "50", "formula": "4000 / (4000 + 3000 + 1000) * 100", "input_values": [4000, 3000, 1000]}
  ]
}
"""


def build_narrator_prompt(result: QueryServiceResult, *, max_rows: int = 50) -> str:
    """Render the v2 narrator prompt.

    Sends user_question, columns + descriptions, row_count, and up to
    `max_rows` JSON-encoded rows. Asks for a structured JSON envelope so the
    backend can verify any derived numbers (percentages, ratios, totals) the
    LLM puts in the prose. SQL is included only as hidden debug context
    labelled "INTERNAL CONTEXT — DO NOT mention".
    """
    descriptions = _column_descriptions(result.columns)
    truncated = result.rows[:max_rows]
    rows_payload = [list(r) for r in truncated]
    truncation_note = ""
    if result.row_count > max_rows:
        truncation_note = (
            f"\nNote: only the first {max_rows} of {result.row_count} rows are shown above."
        )

    descriptions_block = (
        "\n".join(f"- {name}: {desc}" for name, desc in descriptions)
        or "- (no descriptions available)"
    )

    rows_json = json.dumps(rows_payload, ensure_ascii=False, default=str)

    return (
        "You are an analyst writing a short answer in Uzbek Latin script for a non-technical user.\n"
        "Default language is Uzbek Latin. Source entity names stay in their original Cyrillic form.\n"
        "\n"
        "USER QUESTION:\n"
        f"{result.user_question or '(not provided)'}\n"
        "\n"
        f"ROW COUNT: {result.row_count}\n"
        "\n"
        "COLUMNS (name : description):\n"
        f"{descriptions_block}\n"
        "\n"
        "RESULT ROWS (JSON; nulls mean source data missing):\n"
        f"{rows_json}{truncation_note}\n"
        "\n"
        "INTERNAL CONTEXT (debug only — DO NOT mention any of this in the answer):\n"
        f"  service_kind = {result.kind}\n"
        f"  sql = {result.sql or '(none)'}\n"
        "\n"
        "RULES:\n"
        "1. Reply in Uzbek Latin. 2-5 sentences. Friendly analyst tone.\n"
        "2. Source numbers from RESULT ROWS must be quoted exactly when used.\n"
        "3. You MAY add simple derived numbers computed FROM the rows: differences,\n"
        "   percentages, ratios, totals, shares, gaps between top entries. Each\n"
        "   such number MUST be declared in `derived_calculations` so it can be\n"
        "   verified. Allowed operators: + - * / and parentheses. Allowed\n"
        "   scaffolding constants in formulas: 0, 1, 2, 10, 100, 1000.\n"
        "4. Do NOT invent any numbers, causes, recommendations, or context that\n"
        "   is not visible in the rows.\n"
        f'5. Render NULL / missing values as "{NULL_DISPLAY}". Never use 0 for missing.\n'
        "6. Keep entity names exactly as written (Cyrillic).\n"
        "7. Do not mention SQL, planner, sql_guard, semantic views, raw tables,\n"
        "   or any internal architecture.\n"
        "8. Markdown table is optional — only include one when it adds value.\n"
        "\n"
        "Return ONLY a single JSON object with this exact shape:\n"
        '{"answer": "<Uzbek Latin prose>", "derived_calculations": [\n'
        '  {"output_value": "<number you cited>", "formula": "<arithmetic>", "input_values": [<row numbers used>]}\n'
        "]}\n"
        "No preamble, no commentary, no code fences.\n"
        "\n"
        f"{_FEW_SHOT_EXAMPLE}"
    )


def _column_descriptions(columns: tuple[str, ...]) -> list[tuple[str, str]]:
    """Look up plain descriptions for `columns` from the semantic catalog.

    Falls back to a generic placeholder for column names that are not
    catalogued (e.g. SQL aggregate aliases like `n` or `total`).
    """
    found: dict[str, str] = {}
    for view in SEMANTIC_CATALOG.values():
        for col in view.columns:
            if col.name in found:
                continue
            found[col.name] = col.description
    return [(c, found.get(c, "(no description)")) for c in columns]


# ---------------------------------------------------------------------------
# Output safety checks
# ---------------------------------------------------------------------------

_NUMERIC_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def _normalize_num(s: str) -> str:
    s = s.replace(",", ".")
    try:
        f = float(s)
    except ValueError:
        return s
    if f.is_integer():
        return str(int(f))
    return f"{f:.10f}".rstrip("0").rstrip(".")


def _allowed_numeric_tokens(result: QueryServiceResult) -> set[str]:
    """Numeric tokens the narrator is allowed to print.

    Source rows may store numbers as int / float / decimal / string.
    Each numeric substring inside any cell counts; both the original and
    normalized form are accepted so the LLM can format `1234.0` as `1234`.
    """
    allowed: set[str] = set()
    for row in result.rows:
        for cell in row:
            if cell is None:
                continue
            for tok in _NUMERIC_RE.findall(str(cell)):
                allowed.add(tok)
                allowed.add(_normalize_num(tok))
    # row_count is permitted prose context.
    allowed.add(str(result.row_count))
    return allowed


def _has_internal_term(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in _FORBIDDEN_INTERNAL_TERMS)


def _is_safe_narrator_output(text: str, result: QueryServiceResult) -> bool:
    """Strict back-compat path: every numeric token must come from rows.

    Used when the LLM returns plain text instead of the v2 JSON envelope.
    """
    if _has_internal_term(text):
        return False
    allowed = _allowed_numeric_tokens(result)
    for tok in _NUMERIC_RE.findall(text):
        if tok in allowed:
            continue
        if _normalize_num(tok) in allowed:
            continue
        return False
    return True


def _process_envelope_answer(text: str, result: QueryServiceResult) -> str | None:
    """Try to interpret `text` as a v2 narrator envelope.

    Returns the verified answer string, or None when the envelope cannot be
    parsed or the answer references numbers that are neither row values nor
    outputs of a verified derived calculation. Calls back to the strict
    plain-text path when it returns None.
    """
    try:
        env = parse_envelope(text)
    except EnvelopeParseError:
        return None

    row_numbers = extract_row_numbers(result.rows)
    verified_outputs: set[float] = set()
    for calc in env.derived:
        if not verify_calculation(calc, row_numbers):
            continue
        v = normalize_token(calc.output_value)
        if v is not None:
            verified_outputs.add(v)

    if not is_answer_grounded(
        env.answer,
        row_numbers=row_numbers,
        verified_outputs=verified_outputs,
        row_count=result.row_count,
    ):
        return None
    return env.answer


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def make_narrator_from_settings(
    settings: Settings | None = None,
    *,
    provider_call: ProviderCall | None = None,
    fallback: Narrator | None = None,
) -> Narrator:
    """Return narrator implementation based on `Settings.answer_narrator_mode`.

    - "deterministic" (default): `DeterministicNarrator`.
    - "llm":                     `LlmNarrator` (with deterministic fallback).
    """
    cfg = settings or get_settings()
    mode = (
        (getattr(cfg, "answer_narrator_mode", "deterministic") or "deterministic").strip().lower()
    )
    if mode == "llm":
        return LlmNarrator(
            settings=cfg,
            provider_call=provider_call,
            fallback=fallback or DeterministicNarrator(),
        )
    return fallback or DeterministicNarrator()


__all__ = [
    "DeterministicNarrator",
    "LlmNarrator",
    "Narrator",
    "NarratorError",
    "build_narrator_prompt",
    "make_narrator_from_settings",
]
