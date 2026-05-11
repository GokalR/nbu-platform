"""LLM answer agent that reasons over an `EvidencePack`.

Design (after the "search-tab" regression):

- LLM is trusted to reason. No paranoid numeric-token validator. The model
  may compute additional comparisons FROM the rows on its own.
- All numeric cells are pre-formatted (`format_rows`) before serialization
  so the LLM never sees raw float tails like `67611.4667952569`.
- `compute_derived_metrics` ships a rich menu of pre-computed analytical
  numbers (top vs second/last, share, dispersion, ties at extremes,
  concentration, above/below average counts, cross-metrics vs each
  scalar context). The prompt asks the model to PICK the 2-3 insights
  that best fit THIS question instead of always reciting the average.
- Hard hygiene fallbacks (only catastrophic regressions trigger one):
    * snake_case identifier in user prose → fallback
      (catches column-name leaks like `rating_score`)
    * scratchpad markers (Wait, Actually, Hmm, Let me compute, …) → fallback
    * internal architecture words (sql_guard, schema_link, …) → fallback
    * Empty / unparseable provider output → fallback to deterministic table
  NULL → "ma'lumot yo'q" is enforced by the prompt only; no automatic
  fallback fires for it.
- The `AnswerBrief` is ADVISORY, not restrictive. The narrator is free to
  reason from the evidence and add ratios, densities, shares,
  comparisons, plain-language interpretations.

SQL guard, the read-only executor, and the source data are unchanged.
The final answer prompt asks the LLM to transliterate Cyrillic source names
into Uzbek Latin for the user-visible text.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.query.answer import NULL_DISPLAY, Answer, compose_answer
from cerr_chatbot.query.answer_brief import (
    AnswerBrief,
    build_answer_brief,
    render_brief_for_prompt,
)
from cerr_chatbot.query.evidence import (
    EvidencePack,
    EvidenceQueryResult,
    EvidenceServiceResult,
)
from cerr_chatbot.query.llm_planner import (
    ProviderCall,
    _resolve_provider,
    resolve_streaming_provider,
)
from cerr_chatbot.query.narrator_format import (
    compute_derived_metrics,
    format_cell,
    format_rows,
)
from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG
from cerr_chatbot.query.service import QueryServiceResult
from cerr_chatbot.query.transliterate import uz_cyrillic_to_latin

log = logging.getLogger(__name__)

_FORBIDDEN_INTERNAL_TERMS: tuple[str, ...] = (
    "sql_guard",
    "schema_link",
    "import_run",
    "raw table",
    "raw tables",
    "validated_sql",
    "expected_result_shape",
    "executor",
)

# Stream-of-consciousness / scratchpad leaks. The screenshots showed real
# user-visible damage from "Wait" mid-sentence and "Let me compute". We
# treat any of these as a hard fallback signal.
_SCRATCHPAD_MARKERS: tuple[str, ...] = (
    "wait,",
    "wait.",
    " wait ",
    "wait\n",
    "wait!",
    "actually,",
    "actually.",
    " actually ",
    "hmm,",
    "hmm.",
    " hmm ",
    "let me compute",
    "let me recalculate",
    "let me reconsider",
    "on second thought",
    "i mean,",
    "i mean ",
    "scratchpad",
    "chain of thought",
    "need fix",
    "need sum",
)

# Bare snake_case-with-underscore tokens are almost always internal column
# names or schema identifiers leaking into user prose ("rating_score = 0.0",
# "macro_period_label_cyr", …). Real Uzbek/English narration has no
# underscored tokens.
_SNAKE_CASE_LEAK_RE = re.compile(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b")


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


def _column_descriptions(columns: tuple[str, ...]) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for view in SEMANTIC_CATALOG.values():
        for col in view.columns:
            if col.name not in found:
                found[col.name] = col.description
    return [(c, found.get(c, "(no description)")) for c in columns]


__all__ = [
    "EvidenceLlmNarrator",
    "build_evidence_prompt",
    "build_evidence_stream_prompt",
]


def _query_payload(qr: EvidenceQueryResult, *, max_rows: int) -> str:
    if qr.error:
        return f"## {qr.purpose}\n(unavailable: {qr.error})"
    columns_block = (
        "\n".join(f"- {n}: {d}" for n, d in _column_descriptions(qr.columns)) or "- (none)"
    )
    truncated = qr.rows[:max_rows]
    note = (
        f"\n(only first {max_rows} of {qr.row_count} rows shown)" if qr.row_count > max_rows else ""
    )
    formatted = format_rows(truncated)
    rows_json = json.dumps([list(r) for r in formatted], ensure_ascii=False, default=str)
    return (
        f"## {qr.purpose}\n"
        f"row_count: {qr.row_count}\n"
        f"columns:\n{columns_block}\n"
        f"rows: {rows_json}{note}"
    )


def _metrics_block(metrics: dict[str, object]) -> str:
    if not metrics:
        return "(none)"
    return "\n".join(f"- {k}: {v}" for k, v in metrics.items())


def build_evidence_prompt(pack: EvidencePack, brief: AnswerBrief | None = None) -> str:
    primary_payload = _query_payload(pack.primary, max_rows=50)
    contexts = "\n\n".join(_query_payload(c, max_rows=30) for c in pack.context) or "(none)"
    metrics = compute_derived_metrics(pack.primary, pack.context)
    metrics_block = _metrics_block(metrics)
    if brief is None:
        brief = build_answer_brief(pack.question, pack.primary, pack.context)
    brief_block = render_brief_for_prompt(brief)

    return (
        "You are a senior regional analyst writing in Uzbek Latin script.\n"
        "Write a USEFUL, informative answer for a non-technical user. Reason\n"
        "FREELY over the evidence: compute ratios, densities, shares, "
        "comparisons, plain-language interpretations — whatever genuinely\n"
        "helps the reader understand the result. The ANSWER BRIEF below is\n"
        "ADVISORY guidance about what fits THIS question shape; use it as a\n"
        "hint, not a cage.\n"
        "\n"
        f"USER QUESTION:\n{pack.question}\n"
        "\n"
        "ANSWER BRIEF (advisory, not restrictive):\n"
        f"{brief_block}\n"
        "\n"
        "PRIMARY RESULT (numbers already formatted for display):\n"
        f"{primary_payload}\n"
        "\n"
        "CONTEXT EVIDENCE:\n"
        f"{contexts}\n"
        "\n"
        "PRE-COMPUTED METRICS (use any that help the answer):\n"
        f"{metrics_block}\n"
        "\n"
        "INSIGHT POLICY (lightweight):\n"
        "  * Reason from the evidence. You may compute simple derived\n"
        "    insights (ratios between returned values, density per unit,\n"
        "    shares, comparisons, practical interpretations).\n"
        "  * Use the ANSWER BRIEF's allowed_insight_modes as inspiration\n"
        "    for what is most relevant — not as a strict menu.\n"
        "  * Skip insights from the BRIEF's forbidden_insight_modes when\n"
        "    they would be useless single-row artefacts: e.g. never write\n"
        "    \"100% of shown results\" for one row, never write \"highest\n"
        "    and lowest are the same\", never write \"gap is 0\".\n"
        "  * Do not invent facts that are not in the evidence (no outside\n"
        "    knowledge, no fabricated numbers, no made-up time periods).\n"
        "\n"
        "HARD RULES (the only things you MUST NOT do):\n"
        "1. Default language: Uzbek Latin. In the final answer, transliterate\n"
        "   every Cyrillic source name/label into Uzbek Latin. Do not show\n"
        "   Cyrillic names to the user unless the user explicitly asks for the\n"
        "   original source spelling. Examples: Самарқанд вилояти -> Samarqand\n"
        "   viloyati; Фарғона вилояти -> Farg'ona viloyati; Тошкент шаҳри ->\n"
        "   Toshkent shahri; Ёйилма -> Yoyilma; Марғилон шаҳри -> Marg'ilon shahri.\n"
        "2. Numbers from the rows must appear EXACTLY as shown. Derived numbers\n"
        "   you compute yourself must be correct — recheck before writing.\n"
        f'3. Render NULL as "{NULL_DISPLAY}". NEVER use 0 for a missing value.\n'
        "4. NEVER write snake_case identifiers (rating_score, region_code,\n"
        "   industry_volume_bln_uzs, …) in the prose. Use natural Uzbek words.\n"
        "5. NEVER think aloud. No 'Wait', 'Actually', 'Hmm', 'Let me compute',\n"
        "   no self-correction, no questions to yourself. If unsure, omit.\n"
        "6. NEVER invent facts, time periods, numbers, or entities that are\n"
        "   NOT in the evidence rows. You MAY synthesize a recommendation or\n"
        "   prescriptive direction (e.g. 'mahalla X has high population + few\n"
        "   restaurants, so opening a restaurant there has strong demand'),\n"
        "   but every concrete claim — population, company count, USD value,\n"
        "   district name — MUST come from the rows. No outside knowledge.\n"
        "   When the user asked for advice / a recommendation (tavsiya, taklif,\n"
        "   posoveti, recommend), give a clear ranked recommendation grounded\n"
        "   in the rows; do NOT refuse, do NOT hedge with 'I cannot recommend'.\n"
        "7. NEVER mention SQL, planner, sql_guard, semantic views, or internals.\n"
        "8. NEVER attach a suffix letter directly to a closing bold marker.\n"
        "   `**80%**i` is invalid markdown — bold closes only when followed\n"
        "   by whitespace or punctuation, so a stuck-on letter renders the\n"
        "   asterisks literally. Write `**80%** ulushi`, `**80%** ga`,\n"
        "   `**5 tadan 4 tasi**`, `**80 foiz** ulushi` — always put a space\n"
        "   between `**` and the next letter. Same rule for Russian, Uzbek\n"
        "   Cyrillic, and English suffixes after `**X**`.\n"
        "9. NEVER emit naked classification codes the user cannot decode.\n"
        "   The user does NOT see the database. So:\n"
        "   * TN_VED chapter codes (`02`, `08`, `21`, `Глава 02`, `02-bob`,\n"
        "     `chapter 02`) — translate to plain Uzbek using the HS\n"
        "     classification you already know, e.g. 02 -> 'go'sht mahsulotlari',\n"
        "     08 -> 'meva va yong'oqlar', 21 -> 'turli oziq-ovqat',\n"
        "     22 -> 'ichimliklar', 84 -> 'mashina va uskunalar',\n"
        "     85 -> 'elektr asboblari', 87 -> 'transport vositalari',\n"
        "     30 -> 'farmatsevtika', 39 -> 'plastmassalar', 48 -> 'qog'oz',\n"
        "     61 -> 'trikotaj kiyim', 62 -> 'kiyim'. If you must show a code,\n"
        "     pair it with the friendly name in parentheses.\n"
        "   * OKED labels, indicator_key strings, ISO country codes, ISO\n"
        "     currency codes — same rule: translate '156' -> 'Xitoy',\n"
        "     '840' -> 'AQSh dollar', etc. The user must NEVER see a bare code.\n"
        "\n"
        "STRUCTURE & FORMAT — REQUIRED for any answer with 3+ ranked items.\n"
        "Do NOT write a wall of prose. Use proper markdown structure:\n"
        "  * Start with a one-line **bold** headline containing the key\n"
        "    number (e.g. **Toshkent shahrida 36,108 ta kompaniya bor.**).\n"
        "  * For 3+ ranked items: USE A MARKDOWN TABLE. Inline comma-separated\n"
        "    lists like \"X — 1,585 ta, Y — 923 ta, Z — 362 ta\" are FORBIDDEN.\n"
        "    Right-align numeric columns with `---:`.\n"
        "  * BE HONEST about which rows match the user's category. If the\n"
        "    user asked about drinks (`ichimlik`), and a returned row has\n"
        "    OKED text like `bo'lqa tovarlar chakana savdosi` ('retail of\n"
        "    other goods') — that row does NOT plainly answer the question.\n"
        "    DO NOT include it in the table. Mention in one short sentence\n"
        "    that the strict match returned fewer rows than the broader\n"
        "    catalog, and offer a clarifying follow-up question. The user\n"
        "    must trust that every row in your table actually matches what\n"
        "    they asked. NEVER include 'umbrella' OKED rows (other goods,\n"
        "    other categories, non-specialised, прочие, boshqa) when the\n"
        "    user asked for a specific product.\n"
        "\n"
        "  * COMPANY LIST QUESTIONS (\"qaysi kompaniyalar\", \"yetkazib beruvchilar\",\n"
        "    \"ro'yxat\", \"qanday firmalar\") — the LIST IS THE ANSWER. Show as\n"
        "    many rows as the rows payload contains (up to 20). The table MUST\n"
        "    have these columns whenever address_raw / district_name_cyr are\n"
        "    present in the payload:\n"
        "      | # | Nomi | Faoliyati | Manzil |\n"
        "      |---:|---|---|---|\n"
        "      | 1 | ABDULLO AGRO EXPORT | Meva-sabzavot ulgurji | *Samarqand tumani, Hudayqul mahallasi* |\n"
        "      | 2 | ABDUALIMOV MEGA TAMINOT | Oziq-ovqat ulgurji | *Payariq tumani, Mustaqillik ko'chasi* |\n"
        "    Wrap each address in `*…*` (italic) so it visually separates from\n"
        "    the activity column. If district_name_cyr is in the rows but\n"
        "    address_raw is missing/NULL, fall back to the district name in the\n"
        "    Manzil column (still italicised). Never omit the Manzil column when\n"
        "    the user asked for a list of companies — it is the most useful\n"
        "    piece of information for them.\n"
        "  * NON-COMPANY ranking questions (top regions, top mahallas, top\n"
        "    OKED categories) — keep the simpler 3-column table:\n"
        "      | # | Nomi | Soni / qiymati |\n"
        "      |---:|---|---:|\n"
        "      | 1 | Meva yetishtirish | 1,585 |\n"
        "      | 2 | Boshqa oziq-ovqat | 923 |\n"
        "  * For multi-section answers, use `## Section title` headings\n"
        "    (`## Ro'yxat`, `## Foydali kuzatuv`). 2–3 sections max.\n"
        "  * When the user asked a list-type question, keep analytical prose\n"
        "    SHORT (1–2 sentences max). The user wants the list, not commentary.\n"
        "  * Short paragraphs (2–3 sentences). Bold every key number.\n"
        "\n"
        "CLOSING SECTIONS — REQUIRED whenever the answer is a ranking, filter,\n"
        "or comparison (anything with multiple rows). Skip ONLY for a single\n"
        "scalar lookup like 'X soni qancha?'. Append BOTH sections below the\n"
        "main answer, separated by a blank line. Use the EXACT headings.\n"
        "\n"
        "  **Umumiy ko'rsatkichlar**\n"
        "  Two or three bullet lines pulling totals/baselines from the context\n"
        "  queries (SUM, AVG, COUNT(*) etc). Examples — adapt to the question:\n"
        "    * Jami yozuvlar: **N ta**\n"
        "    * Ko'rsatilgan top ulushi: **X%**\n"
        "    * O'rtacha qiymat: **Y**\n"
        "  If a useful total/baseline isn't available in the context queries,\n"
        "  pick a sensible derived number from the primary rows (max, min,\n"
        "  ratio of top to bottom) — never invent one.\n"
        "\n"
        "  **Keyingi savollar**\n"
        "  Exactly 2 or 3 short Uzbek follow-up questions naming concrete\n"
        "  entities from the answer above (specific company name, viloyat,\n"
        "  mahalla, OKED). Each must be a complete standalone question the\n"
        "  chatbot can answer with the data it already has. Format as a\n"
        "  bulleted list, one question per line. Examples:\n"
        "    * \"Toshkent shahrining qaysi tumanida eng ko'p restoran bor?\"\n"
        "    * \"AO UzGasTrade qaysi davlatlardan import qiladi?\"\n"
        "    * \"Samarqand viloyatida go'sht yetishtirish bo'yicha eng yirik\n"
        "       korxonalar qaysi?\"\n"
        "\n"
        "OUTPUT CONTRACT:\n"
        "Return exactly one JSON object and nothing else:\n"
        '{"answer_markdown": "<final user-facing answer in markdown>"}\n'
    )


def build_evidence_stream_prompt(pack: EvidencePack, brief: AnswerBrief | None = None) -> str:
    """Streaming-friendly prompt: emit raw markdown, NO JSON wrapper.

    Identical reasoning + safety to `build_evidence_prompt`, except the
    OUTPUT CONTRACT changes so each streamed token is part of the final
    user-facing markdown directly. Used only by `narrate_stream`.
    """
    base = build_evidence_prompt(pack, brief=brief)
    return base.replace(
        "OUTPUT CONTRACT:\n"
        "Return exactly one JSON object and nothing else:\n"
        '{"answer_markdown": "<final user-facing answer in markdown>"}\n',
        "OUTPUT CONTRACT (STREAMING MODE):\n"
        "Write the user-facing markdown answer DIRECTLY. No JSON wrapper.\n"
        "No code fences, no preface, no <answer> tags. Just the markdown\n"
        "the user should read.\n",
    )


# ---------------------------------------------------------------------------
# Narrator
# ---------------------------------------------------------------------------


@dataclass
class EvidenceLlmNarrator:
    """LLM narrator that reasons over an EvidencePack.

    Falls back to the deterministic markdown composer (built from the
    primary result) when the LLM is unavailable, returns nothing, leaks
    internal terminology, leaks scratchpad markers, leaks snake_case
    identifiers, or quotes numbers that are not in the rows / pre-computed
    metrics.
    """

    settings: Settings | None = None
    provider_call: ProviderCall | None = None
    log_full_prompt: bool = False

    def narrate_stream(self, result: EvidenceServiceResult) -> Iterator[dict[str, Any]]:
        """Yield SSE-friendly events while the narrator LLM streams its answer.

        Event shapes:
          {"type": "status",   "stage": "narrating", "message": "..."}
          {"type": "token",    "text": "..."}                     # delta from LLM
          {"type": "done",     "kind": "...", "answer": "<full>",
           "sql": "...", "row_count": N, "columns": [...]}

        Non-sql_result paths short-circuit to a single done event so the caller
        always sees a terminator. Provider/SDK failures fall back to the
        deterministic markdown composer and emit it as a single token.
        """
        if result.kind != "sql_result" or result.pack is None:
            yield {
                "type": "done",
                "kind": result.kind,
                "answer": result.user_message,
                "sql": None,
                "row_count": 0,
                "columns": [],
            }
            return

        cfg = self.settings or get_settings()
        try:
            stream_provider, model, api_key = resolve_streaming_provider(cfg)
        except Exception as exc:  # noqa: BLE001 — missing key / wrong provider
            log.info("evidence narrator streaming unavailable, falling back: %s", exc)
            ans = self.narrate(result)
            yield {"type": "token", "text": ans.text}
            yield {
                "type": "done",
                "kind": result.kind,
                "answer": ans.text,
                "sql": ans.sql,
                "row_count": ans.row_count,
                "columns": list(ans.columns),
            }
            return

        brief = build_answer_brief(result.pack.question, result.pack.primary, result.pack.context)
        prompt = build_evidence_stream_prompt(result.pack, brief=brief)
        if self.log_full_prompt:
            log.info("evidence stream prompt: %s", prompt)
        else:
            log.info("evidence stream prompt built (%d chars)", len(prompt))

        yield {"type": "status", "stage": "narrating", "message": "Javob yozilmoqda..."}

        accumulated: list[str] = []
        had_provider_error = False
        try:
            for delta in stream_provider(model, prompt, api_key):
                if not isinstance(delta, str) or not delta:
                    continue
                accumulated.append(delta)
                yield {"type": "token", "text": delta}
        except Exception as exc:  # noqa: BLE001
            had_provider_error = True
            log.warning("evidence streaming provider failed: %s", exc)

        cleaned = "".join(accumulated).strip()
        if not cleaned or had_provider_error:
            # Provider died with no output. Fall back to the deterministic
            # composer (the user has nothing useful yet).
            if not accumulated:
                ans = self.narrate(result)
                yield {"type": "token", "text": ans.text}
                yield {
                    "type": "done",
                    "kind": result.kind,
                    "answer": ans.text,
                    "sql": ans.sql,
                    "row_count": ans.row_count,
                    "columns": list(ans.columns),
                }
                return
            # Partial output already streamed — keep what we have but flag it
            # in debug notes via the done event.
        cleaned_for_done = uz_cyrillic_to_latin(cleaned) if cleaned else ""
        yield {
            "type": "done",
            "kind": result.kind,
            "answer": cleaned_for_done,
            "sql": result.pack.primary.sql,
            "row_count": result.pack.primary.row_count,
            "columns": list(result.pack.primary.columns),
        }

    def narrate(self, result: EvidenceServiceResult) -> Answer:
        if result.kind != "sql_result" or result.pack is None:
            return Answer(
                text=result.user_message,
                kind=result.kind,
                sql=None,
                row_count=0,
                columns=(),
            )

        cfg = self.settings or get_settings()
        try:
            provider, model, api_key = _resolve_provider(cfg, self.provider_call)
        except Exception as exc:  # noqa: BLE001 - missing key, etc.
            log.info("evidence narrator falling back to deterministic: %s", exc)
            return _fallback_answer(result.pack)

        brief = build_answer_brief(
            result.pack.question, result.pack.primary, result.pack.context
        )
        prompt = build_evidence_prompt(result.pack, brief=brief)
        if self.log_full_prompt:
            log.info("evidence prompt: %s", prompt)
        else:
            log.info("evidence prompt built (%d chars)", len(prompt))

        try:
            text = provider(model, prompt, api_key)
        except Exception as exc:  # noqa: BLE001
            log.warning("evidence provider failed; falling back: %s", exc)
            return _fallback_answer(result.pack)

        cleaned = _extract_answer_text(text).strip()
        if not cleaned:
            return _fallback_answer(result.pack)

        # Hard fallback — never trim scratchpad tails; the surrounding prose
        # is almost always wrong too (the screenshot 3 incident).
        if _has_scratchpad_marker(cleaned):
            log.warning("evidence narrator output leaked scratchpad; falling back")
            return _fallback_answer(result.pack)

        if _has_internal_term(cleaned):
            log.warning("evidence narrator output leaked internal terms; falling back")
            return _fallback_answer(result.pack)

        if _SNAKE_CASE_LEAK_RE.search(cleaned):
            log.warning("evidence narrator output leaked snake_case identifier; falling back")
            return _fallback_answer(result.pack)

        # Final guarantee: any Cyrillic source name still in the answer is
        # transliterated to Uzbek Latin server-side. The prompt asks the LLM
        # to do this, but compliance is unreliable across runs.
        return Answer(
            text=uz_cyrillic_to_latin(cleaned),
            kind=result.kind,
            sql=result.pack.primary.sql,
            row_count=result.pack.primary.row_count,
            columns=result.pack.primary.columns,
        )


# ---------------------------------------------------------------------------
# Output sanitization helpers
# ---------------------------------------------------------------------------


def _extract_answer_text(text: str | None) -> str:
    """Return the user-facing text from common provider output shapes."""
    raw = (text or "").strip()
    if not raw:
        return ""
    if raw.startswith("```"):
        raw = _strip_code_fence(raw)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(parsed, str):
        return parsed.strip()
    if isinstance(parsed, dict):
        for key in (
            "answer_markdown",
            "output",
            "text",
            "answer",
            "answer_text",
            "final_answer",
        ):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return raw


def _strip_code_fence(text: str) -> str:
    lines = text.strip().splitlines()
    if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def _has_internal_term(text: str) -> bool:
    lower = text.lower()
    return any(t in lower for t in _FORBIDDEN_INTERNAL_TERMS)


def _has_scratchpad_marker(text: str) -> bool:
    lower = f" {text.lower()} "
    return any(marker in lower for marker in _SCRATCHPAD_MARKERS)


def _fallback_answer(pack: EvidencePack) -> Answer:
    """Deterministic markdown table built from the primary result.

    The fallback path also transliterates the rendered text so users never
    see Cyrillic source labels in the no-LLM path either.
    """
    fake = QueryServiceResult(
        kind="sql_result",
        user_message="Natijani topdim.",
        sql=pack.primary.sql,
        columns=tuple(_humanize_column(c) for c in pack.primary.columns),
        rows=tuple(tuple(format_cell(c) for c in row) for row in pack.primary.rows),
        row_count=pack.primary.row_count,
    )
    base = compose_answer(fake)
    return Answer(
        text=uz_cyrillic_to_latin(base.text),
        kind=base.kind,
        sql=base.sql,
        row_count=base.row_count,
        columns=base.columns,
    )


def _humanize_column(name: str) -> str:
    known = {
        "region_name_cyr": "Hudud",
        "district_name_cyr": "Tuman/shahar",
        "mahalla_name_cyr": "Mahalla",
        "population": "Aholi soni",
        "rating_score": "Reyting",
        "rating_position": "Reyting pozitsiyasi",
        "issue_code": "Muammo turi",
        "total_issues": "Muammolar soni",
        "missing_rating": "Reytingi yo'q mahallalar",
    }
    if name in known:
        return known[name]
    return name.replace("_", " ").strip().title()


__all__ = [
    "EvidenceLlmNarrator",
    "build_evidence_prompt",
]
