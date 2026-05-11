"""Real LLM adapter producing an evidence-pack plan.

The adapter renders a prompt that includes the semantic catalog, sql_guard
rules, and few-shot examples of (primary_sql, context_queries). It calls
the configured provider and returns the raw model text. The caller
(`evidence_ask`) is responsible for parsing the JSON envelope and running
each SQL through `sql_guard.validate` + the read-only executor.

The adapter does NOT touch the database, does NOT execute SQL, and does
NOT compose the user-facing answer. The Uzbek Latin language policy lives
on the EvidenceLlmNarrator, not here.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.query.evidence import MAX_CONTEXT_QUERIES
from cerr_chatbot.query.llm_planner import LlmPlannerError, ProviderCall, _resolve_provider
from cerr_chatbot.query.planner_prompt import (
    REFUSE_RULES,
    SQL_WRITING_GUIDE,
    _render_catalog,
)
from cerr_chatbot.query.semantic_catalog import GLOBAL_WARNINGS
from cerr_chatbot.query.session_memory import MemorySnapshot

log = logging.getLogger(__name__)


_HEADER = """\
You are a careful read-only SQL planner over curated semantic views. You do
NOT execute SQL; another component does. You do NOT write the final user
answer; a downstream agent does that from the data you fetch.

YOU MUST output exactly one JSON object and nothing else (no markdown, no
prose). The JSON object has these fields:

  kind             : one of "sql_plan", "clarify", "no_data", "unsupported"
  user_message     : short generic intro (NOT the final analyst answer)
  primary_sql      : SELECT statement when kind=="sql_plan", else omitted/null
  context_queries  : array of 0..N {"purpose": str, "sql": str} entries
  memory_use       : one of "used", "ignored", "unclear" (optional;
                     reserved for future conversation-memory support; if
                     omitted or invalid the backend treats it as "ignored")
  resolved_question: string (optional; the question after any future
                     memory-based resolution; if omitted or empty the
                     backend falls back to the current user question)

PRIMARY SQL policy:
  - Always project a human-readable label column for each row when the
    view exposes one (region_name_cyr, district_name_cyr, mahalla_name_cyr,
    issue_code, etc). Never return only an opaque numeric value.
  - For COMPANY LIST queries against v_companies (questions like "qaysi
    kompaniyalar", "yetkazib beruvchilar ro'yxati", "what suppliers /
    companies exist") — ALWAYS include `address_raw` in the SELECT list
    alongside company_name + district_name_cyr + oked_label_uz. The
    downstream answer agent renders address as a dedicated `Manzil` column
    and it is the single most useful field for the user.

  - PRODUCT-CATEGORY FILTERS — STRICT MATCHING REQUIRED. When the user
    asks for suppliers of a specific product category (drinks, meat,
    vegetables, clothing, electronics, vehicles, pharma, tobacco, etc),
    you MUST filter narrowly. The user does NOT want every retailer who
    might also sell that product. Two rules:
      (a) The OKED LIKE pattern MUST contain a word that is directly
          about the product itself (Uzbek/Russian root), NOT a broad
          umbrella like 'boshqa tovarlar' / 'прочие товары' / 'other
          goods'. Forbidden patterns (these match everything and are
          useless): '%boshqa tovarlar%', '%прочие товары%',
          '%прочие виды%', '%other%'. They produce noise like rows whose
          OKED is 'retail of other goods' — that does NOT answer the
          user's question.
      (b) PATH CHOICE for product-category supplier questions:

          For "qaysi kompaniyalar / yetkazib beruvchilar bor" type
          questions, v_companies is the PRIMARY source (it has all
          167k registered businesses with their primary OKED). The
          v_business_imports / tnved_chapter path is a CONTEXT query
          showing customs IMPORTERS only — that's ~3000 companies
          nationwide and most regions have zero importers for any
          given chapter, so it cannot be primary.

          STRUCTURE for these questions:

            primary_sql: v_companies with STRICT OKED filter:
              SELECT company_name, district_name_cyr, oked_label_uz,
                     address_raw
              FROM v_companies
              WHERE region_name_cyr LIKE '%<region>%'
                AND (oked_label_uz LIKE '%<product-root>%'
                     OR oked_label_ru LIKE '%<product-root-ru>%')
                AND oked_label_uz NOT LIKE '%бошқа товарлар%'
                AND oked_label_uz NOT LIKE '%boshqa tovarlar%'
                AND oked_label_ru NOT LIKE '%прочие товары%'
              ORDER BY company_name ASC
              LIMIT 20

            context_query 1: TOTAL count of strict matches in the region
              SELECT COUNT(*) AS total_strict_matches FROM v_companies
              WHERE region_name_cyr LIKE '%<region>%'
                AND (oked_label_uz LIKE '%<product-root>%'
                     OR oked_label_ru LIKE '%<product-root-ru>%')
                AND oked_label_uz NOT LIKE '%бошқа товарлар%'
                AND oked_label_uz NOT LIKE '%boshqa tovarlar%'

            context_query 2: importers of the matching TN_VED chapter
              in the region (may return 0 rows for many region+chapter
              combos — that's fine, it just signals "no importers")
              SELECT company_name, district_name_cyr,
                     ROUND(CAST(SUM(value_usd) AS NUMERIC), 2) AS total_usd
              FROM v_business_imports
              WHERE region_name_cyr LIKE '%<region>%'
                AND tnved_chapter = '<chapter>'
                AND value_usd IS NOT NULL
              GROUP BY company_name, district_name_cyr
              ORDER BY total_usd DESC LIMIT 10

          Use this product-category -> TN_VED chapter map for the
          chapter context query (and rough Uzbek/Russian roots for the
          OKED filter):

            drinks / ichimliklar / напитки  -> chapter 22
            meat / go'sht / мясо            -> chapter 02
            fish / baliq / рыба             -> chapter 03
            dairy + eggs / sut, tuxum       -> chapter 04
            vegetables / sabzavot           -> chapter 07
            fruits / mevalar / фрукты       -> chapter 08
            coffee / tea / spices           -> chapter 09
            cereals / don / зерно           -> chapter 10
            sugar / shakar                  -> chapter 17
            cocoa / kakao                   -> chapter 18
            pasta / cereals prep            -> chapter 19
            preserved food                  -> chapter 20
            mixed prepared food             -> chapter 21
            tobacco / tamaki                -> chapter 24
            mineral fuel / yoqilg'i         -> chapter 27
            pharma / dori / лекарства       -> chapter 30
            plastics / plastmassa           -> chapter 39
            wood / yog'och                  -> chapter 44
            paper / qog'oz                  -> chapter 48
            knitted clothes / trikotaj      -> chapter 61
            clothes / kiyim / одежда        -> chapter 62
            footwear / poyabzal             -> chapter 64
            iron & steel                    -> chapter 72-73
            machines / mashina              -> chapter 84
            electronics / elektr            -> chapter 85
            vehicles / transport            -> chapter 87

          Concrete example — "Farg'onada ichimliklar yetkazib beruvchilar":
            product-root (uz): ичимлик
            product-root (ru): напит
            chapter: 22

            primary_sql: v_companies WHERE region LIKE '%Фарғ%' AND
                         (oked_label_uz LIKE '%ичимлик%' OR
                          oked_label_ru LIKE '%напит%') AND
                         oked_label_uz NOT LIKE '%бошқа товарлар%'
                         ORDER BY company_name LIMIT 20
                         -> returns the actual drink retailers/sellers.

            context: COUNT(*) of strict matches (for the totals section).
            context: top-10 importers in chapter 22 in the region
                     (likely 0 rows in Fergana — that's a valid signal).
  - When the view has a period or label column (e.g. macro_period_label_cyr),
    INCLUDE it so the downstream answer can quote the correct period
    instead of inventing one.
  - Round noisy row-level float metrics with ROUND(metric, 2). For AVG/SUM
    expressions that may be double precision in PostgreSQL, use
    ROUND(CAST(AVG(metric) AS NUMERIC), 2), not ROUND(AVG(metric), 2).
    Source identifiers (codes, IDs, names) must never be transformed.

CONTEXT QUERIES policy (only when kind=="sql_plan"):
  - Add 0 to {max_ctx} extra read-only SELECTs that help the downstream
    answer agent reason. Pick what fits THIS question shape:
      * top-N            -> SUM(metric) for share-of-total, optional AVG
                            for cohort baseline.
      * lowest-K         -> COUNT(*) at the floor value, COUNT(*) of NULLs.
      * single value     -> ROUND(CAST(AVG(metric) AS NUMERIC), 2) baseline
                            + COUNT(*) for percentile context.
      * data-quality     -> COUNT per related issue_code.
    Do NOT always emit AVG. Skip context_queries entirely when the
    primary result is self-explanatory.
  - Wrap any aggregate that can produce long floats with PostgreSQL-safe
    ROUND(CAST(expr AS NUMERIC), 2). Never write ROUND(AVG(metric), 2).
  - Each context query MUST be a single SELECT against the same v_* views.
  - The same sql_guard rules apply to every context query.

ADVISORY MODE — recommendation / supplier / "where to start" questions:
  When the user asks for advice, recommendation, or a prescriptive direction
  (Uzbek: "tavsiya", "taklif ber", "qaysi mahallada biznes boshlash",
   "yetkazib beruvchi"; Russian: "рекомендация", "посоветуй";
   English: "recommend", "where should I start", "what suppliers"), TREAT
  IT AS sql_plan, NEVER as unsupported.

  Decompose the request into the EVIDENCE the downstream answer agent needs
  to ground its recommendation. Typical decompositions:

  * "Where to start a business in <city>?" — emit:
      primary: list mahallas in the target district sorted by population
               (v_mahallas WHERE district_name_cyr LIKE '%<city>%')
      context: counts/density per OKED in the target district
               (v_company_density_by_district or aggregated v_companies)
      context: overall company count baselines for context.

  * "What suppliers do I need for <business> in <region>?" — emit:
      primary: companies with OKED matching wholesale/distribution of
               relevant goods in the target region
               (v_companies WHERE region_name_cyr LIKE '%<region>%'
                AND oked_label_uz/ru LIKE '%<supply category>%')
      context: importers in that region for related TN_VED chapters
               (v_business_imports filtered by tnved_chapter + region).

  The answer agent is allowed to synthesize a recommendation FROM the rows.
  It will never invent rows. Your job is to fetch the right evidence.

KIND choice (PREFER sql_plan whenever a reasonable attempt is possible):
  sql_plan    - question is answerable with one safe SELECT (plus optional
                context). Provide primary_sql. This is the DEFAULT. Use it
                also for ADVISORY questions (decompose into evidence-grounded
                sub-queries, never refuse the shape).

  clarify     - LAST RESORT. Use it only when no reasonable interpretation
                exists. Specifically:
                  (a) the user asked for a metric that does not exist in the
                      catalog and you genuinely cannot guess the intent,
                  (b) the user asked for a comparison but no metric is
                      identifiable at all,
                  (c) multiple distinct entity types are explicitly
                      requested and choosing one would meaningfully change
                      the answer.
                STRONG defaults to AVOID clarify:
                  * "reyting" / "reyting o'rni" / "reytingi" -> use the
                    rating_score KPI on v_mahallas / v_districts /
                    v_regions. Do NOT ask which rating column.
                  * "aholi" / "aholisi" -> population KPI. Do NOT ask.
                  * "biznes" / "tadbirkorlik" -> active_businesses KPI.
                  * "ishsiz" / "ishsizlar" -> unemployed KPI.
                  * Place names typed in Latin/mixed script -> use LIKE
                    against *_name_cyr (see NAME MATCHING below). NEVER
                    clarify spelling.
                  * If two related columns could both fit, just PICK the
                    primary one and proceed. The downstream answer agent
                    will explain.
                user_message hygiene for clarify (CRITICAL):
                  * MUST be plain Uzbek Latin for a non-technical user.
                  * MUST NOT mention any column name, view name, snake_case
                    identifier, KPI key, table, SQL, or schema concept.
                  * Refer to metrics by everyday Uzbek words (reyting bali,
                    aholi soni, faoliyatdagi tadbirkorlik subyektlari ...),
                    never as `rating_score`, `district_rank_text`, etc.

  no_data     - the requested metric/concept is not in the semantic catalog.
  unsupported - request is unsafe, write, admin, raw-table, or external.

NAME MATCHING when the user typed a Latin or mixed-script place name:
  * Source name columns (region_name_cyr, district_name_cyr,
    mahalla_name_cyr) are stored in Cyrillic. The user may type Latin
    (Marg'ilon, Yoyilma) or mixed forms.
  * Take the most distinctive Cyrillic-likely fragment from the name
    (e.g. "Yoyilma" -> "Йойилма" / "Ёйилма") and use a LIKE filter on
    the relevant *_name_cyr column. When unsure of the exact spelling,
    stem it: "Marg'ilon" -> WHERE district_name_cyr LIKE '%Марғ%' OR
    district_name_cyr LIKE '%Марг%'.
  * LIKE filters in WHERE are allowed for this purpose. Do NOT JOIN on
    name columns — use the surrogate ids (mahalla_id, district_id,
    region_id) for joins, just like normal.
  * If the resulting SELECT returns 0 rows, that is a valid empty
    answer — the downstream agent will tell the user "topilmadi". Do
    not pre-emptively clarify.

STRENGTHS / WEAKNESSES of a mahalla:
  * "kuchli tomonlari" / "strengths"  -> v_mahalla_peer_factors WHERE
    factor_polarity = 'strength'.
  * "kuchsiz tomonlari" / "weaknesses" -> factor_polarity = 'weakness'.
  * Always include factor_label_cyr, entity_value_num,
    comparison_average_value, percentile in the SELECT so the answer
    layer can summarise. Order by factor_order ASC.
  * If a mahalla / district name fragment is provided, JOIN
    v_mahallas via mahalla_id and filter mahalla_name_cyr LIKE
    '%fragment%' (and district_name_cyr LIKE '%city%' when given).

GLOBAL WARNINGS (apply to every SQL):
"""


_FEW_SHOT = """\
EXAMPLE A - top-N + context for share/ baseline:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "primary_sql": "SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5",
  "context_queries": [
    {"purpose": "total population for share calculation",
     "sql": "SELECT SUM(population) AS total_population FROM v_regions"},
    {"purpose": "average population baseline",
     "sql": "SELECT ROUND(CAST(AVG(population) AS NUMERIC), 1) AS avg_population FROM v_regions"}
  ]
}

EXAMPLE B - lowest rating mahallas + peer-cohort context:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "primary_sql": "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, rating_score FROM v_mahallas WHERE rating_score IS NOT NULL ORDER BY rating_score ASC LIMIT 10",
  "context_queries": [
    {"purpose": "median-ish rating baseline",
     "sql": "SELECT ROUND(CAST(AVG(rating_score) AS NUMERIC), 1) AS avg_rating FROM v_mahallas WHERE rating_score IS NOT NULL"},
    {"purpose": "count of mahallas without rating",
     "sql": "SELECT COUNT(*) AS missing_rating FROM v_mahallas WHERE rating_score IS NULL"}
  ]
}

EXAMPLE C - no context needed:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "primary_sql": "SELECT COUNT(*) AS total_issues FROM v_data_quality_issues WHERE issue_code='MAHALLA_STIR_DUPLICATE'",
  "context_queries": []
}

EXAMPLE D0 - district ranking by rating (PICK rating_score, do NOT clarify;
also include both the rating value and the human-readable rank text):
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "primary_sql": "SELECT d.district_name_cyr, d.rating_score, d.region_rank_text FROM v_districts d JOIN v_regions r ON r.region_id = d.region_id WHERE r.region_name_cyr LIKE '%Андижон%' ORDER BY d.rating_score DESC LIMIT 10",
  "context_queries": [
    {"purpose": "average rating across all districts",
     "sql": "SELECT ROUND(CAST(AVG(rating_score) AS NUMERIC), 1) AS avg_rating FROM v_districts WHERE rating_score IS NOT NULL"}
  ]
}

EXAMPLE D - mahalla strengths with Latin name fragments (PREFER sql_plan,
NOT clarify, even though the user typed Latin while DB is Cyrillic):
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "primary_sql": "SELECT m.mahalla_name_cyr, m.district_name_cyr, p.factor_label_cyr, p.entity_value_num, p.comparison_average_value, p.percentile FROM v_mahalla_peer_factors p JOIN v_mahallas m ON m.mahalla_id = p.mahalla_id WHERE p.factor_polarity = 'strength' AND (m.mahalla_name_cyr LIKE '%Йойилма%' OR m.mahalla_name_cyr LIKE '%Ёйилма%') AND (m.district_name_cyr LIKE '%Марғ%' OR m.district_name_cyr LIKE '%Марг%') ORDER BY p.factor_order ASC",
  "context_queries": []
}

EXAMPLE E - clarify (truly vague: no entity, no metric).
The user_message MUST be plain Uzbek — no column names, no view names,
no snake_case identifiers:
{"kind": "clarify", "user_message": "Qaysi mahalla yoki tumanning kuchli tomonlari kerak? Iltimos, joy nomini kiriting."}

WRONG clarify message (DO NOT do this — leaks column names like
rating_score / district_rank_text to a non-technical user):
{"kind": "clarify", "user_message": "Reyting o'rni deganda rating_score ni nazarda tutyapsizmi yoki district_rank_text ni?"}

EXAMPLE F - unsupported:
{"kind": "unsupported", "user_message": "Bu so'rov xavfsiz emas; faqat o'qish ruxsat etilgan."}

EXAMPLE G - advisory: "Where in Fergana city should I start a business + which
industries?" — decompose into evidence for the answer agent (PREFER sql_plan,
NOT unsupported). The user_message is a short Uzbek intro; the answer agent
writes the actual recommendation from the rows:
{
  "kind": "sql_plan",
  "user_message": "Tavsiya uchun zarur ma'lumotlarni yig'dim.",
  "primary_sql": "SELECT mahalla_name_cyr, population, rating_score FROM v_mahallas WHERE district_name_cyr LIKE '%Фарғона шаҳри%' AND population IS NOT NULL ORDER BY population DESC LIMIT 25",
  "context_queries": [
    {"purpose": "top industries by company count in the target district",
     "sql": "SELECT oked_label_uz, company_count FROM v_company_density_by_district WHERE district_name_cyr LIKE '%Фарғона шаҳри%' ORDER BY company_count DESC LIMIT 15"},
    {"purpose": "least-represented industries in the target district",
     "sql": "SELECT oked_label_uz, company_count FROM v_company_density_by_district WHERE district_name_cyr LIKE '%Фарғона шаҳри%' ORDER BY company_count ASC LIMIT 15"},
    {"purpose": "total companies in the target district for share context",
     "sql": "SELECT SUM(company_count) AS total_companies FROM v_company_density_by_district WHERE district_name_cyr LIKE '%Фарғона шаҳри%'"}
  ]
}

EXAMPLE H - advisory: "Restaurant suppliers in Samarkand" — companies whose
OKED matches food wholesale/distribution + importers of food products
(PREFER sql_plan with multiple slices):
{
  "kind": "sql_plan",
  "user_message": "Tavsiya uchun yetkazib beruvchilar ma'lumotlarini yig'dim.",
  "primary_sql": "SELECT company_name, district_name_cyr, oked_label_uz FROM v_companies WHERE region_name_cyr LIKE '%Самарқанд%' AND (oked_label_ru LIKE '%продукт%питан%' OR oked_label_uz LIKE '%озиқ-овқат%' OR oked_label_uz LIKE '%улгуржи%' OR oked_label_ru LIKE '%оптовая%') LIMIT 100",
  "context_queries": [
    {"purpose": "top food-products importers in Samarkand region",
     "sql": "SELECT company_name, value_food_products_usd FROM v_business_import_summaries s WHERE value_food_products_usd IS NOT NULL ORDER BY value_food_products_usd DESC LIMIT 10"},
    {"purpose": "top imports of food (TN_VED chapters 02-22) in Samarkand region",
     "sql": "SELECT tnved_chapter, SUM(value_usd) AS chapter_total_usd FROM v_business_imports WHERE region_name_cyr LIKE '%Самарқанд%' AND tnved_chapter BETWEEN '02' AND '22' AND value_usd IS NOT NULL GROUP BY tnved_chapter ORDER BY chapter_total_usd DESC LIMIT 10"}
  ]
}
"""


_MEMORY_HEADER = """\
OPTIONAL CONVERSATION CONTEXT
This is a short summary of the previous turn in the same chat session.
It may help if the current message is a continuation. If the current
message is already a complete question, treat it as a new question.

Previous turn:
"""

_MEMORY_USAGE_GUIDE = """\
Use this naturally:
- If the current message continues the previous focus, set memory_use="used"
  and make resolved_question a complete standalone question.
- If the current message already has its own place/metric/topic, set
  memory_use="ignored" and answer the current message.
- If the current message cannot be understood even with this context, set
  memory_use="unclear" and return kind="clarify".
- Do not reuse previous SQL.
- Do not reuse previous numeric answers.
- Plan fresh SQL for the resolved_question.
"""

_PENDING_CLARIFY_GUIDE = """\
The previous turn was a CLARIFICATION request from the assistant
(last_answer_type="clarify"). The current user message is most likely an
ANSWER to that clarification, not a new standalone question.

When this is the case:
- Combine the previous user question (the place/topic the user originally
  named) with the current message (which usually supplies the missing
  metric, grain, or scope).
- Set memory_use="used" and put the combined standalone question into
  resolved_question.
- Plan fresh SQL for that combined question. Do NOT ask the same
  clarification again.
- If the combined question still leaves a real ambiguity, ask a NEW,
  narrower clarification — do not repeat the previous one verbatim.
- If the current message is clearly a brand-new full question with its own
  place and metric, set memory_use="ignored" and answer it as a new
  question.
"""


def render_memory_snapshot_for_prompt(snapshot: MemorySnapshot) -> str:
    """Serialize a MemorySnapshot into a compact JSON block for the prompt.

    Includes only the fields stored on the snapshot itself: question,
    resolved question, answer kind, columns, row count, summary,
    timestamp. Never SQL, never executed rows, never narrator prose.
    """
    payload = {
        "last_question": snapshot.last_question,
        "last_resolved_question": snapshot.last_resolved_question,
        "last_answer_type": snapshot.last_answer_type,
        "last_columns": list(snapshot.last_columns),
        "last_row_count": snapshot.last_row_count,
        "last_result_summary": snapshot.last_result_summary,
        "created_at": snapshot.created_at,
    }
    # Sanity check: dataclass fields cover the same set, no extra leakage.
    declared = set(asdict(snapshot))
    assert declared == set(payload), declared.symmetric_difference(payload)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_evidence_planner_prompt(
    user_question: str,
    memory_snapshot: MemorySnapshot | None = None,
) -> str:
    header = _HEADER.replace("{max_ctx}", str(MAX_CONTEXT_QUERIES))
    parts: list[str] = [header]
    for w in GLOBAL_WARNINGS:
        parts.append(f"  - {w}")
    parts.append("")
    parts.append(REFUSE_RULES.strip())
    parts.append("")
    parts.append(SQL_WRITING_GUIDE.strip())
    parts.append("")
    parts.append("SEMANTIC CATALOG:")
    parts.append(_render_catalog())
    parts.append("")
    parts.append(_FEW_SHOT)
    parts.append("")
    if memory_snapshot is not None:
        parts.append(_MEMORY_HEADER + render_memory_snapshot_for_prompt(memory_snapshot))
        parts.append("")
        if memory_snapshot.last_answer_type == "clarify":
            parts.append(_PENDING_CLARIFY_GUIDE)
            parts.append("")
        parts.append(_MEMORY_USAGE_GUIDE)
        parts.append("")
    parts.append("USER QUESTION:")
    parts.append(user_question.strip())
    parts.append("")
    parts.append("Return ONLY the JSON object.")
    return "\n".join(parts)


@dataclass
class EvidenceLlmPlanner:
    """Calls the configured provider and returns the raw plan JSON text.

    Returns the raw text untouched; downstream `parse_evidence_plan` is
    responsible for JSON validation and `sql_guard.validate` for SQL safety.
    """

    settings: Settings | None = None
    provider_call: ProviderCall | None = None
    log_full_prompt: bool = False

    def plan(
        self,
        user_question: str,
        *,
        memory_snapshot: MemorySnapshot | None = None,
    ) -> str:
        cfg = self.settings or get_settings()
        provider, model, api_key = _resolve_provider(cfg, self.provider_call)
        prompt = build_evidence_planner_prompt(user_question, memory_snapshot)
        if self.log_full_prompt:
            log.info("evidence-planner prompt: %s", prompt)
        else:
            log.info("evidence-planner prompt built (%d chars)", len(prompt))

        try:
            text = provider(model, prompt, api_key)
        except LlmPlannerError:
            raise
        except Exception as exc:  # noqa: BLE001 - any provider crash is opaque
            raise LlmPlannerError(
                f"evidence planner provider failed: {type(exc).__name__}: {exc}"
            ) from exc
        if not isinstance(text, str) or not text.strip():
            raise LlmPlannerError("evidence planner returned empty text")
        return text


def make_evidence_planner_from_settings(
    settings: Settings | None = None,
    *,
    provider_call: ProviderCall | None = None,
    log_full_prompt: bool = False,
) -> EvidenceLlmPlanner:
    cfg = settings or get_settings()
    return EvidenceLlmPlanner(
        settings=cfg, provider_call=provider_call, log_full_prompt=log_full_prompt
    )


__all__ = [
    "EvidenceLlmPlanner",
    "build_evidence_planner_prompt",
    "make_evidence_planner_from_settings",
    "render_memory_snapshot_for_prompt",
]
