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

  kind                  : one of "sql_plan", "clarify", "no_data", "unsupported"
  user_message          : short generic intro (NOT the final analyst answer)
  primary_sql           : SELECT statement when kind=="sql_plan", else omitted/null
  context_queries       : array of 3..{max_ctx} {"purpose": str, "sql": str}
                          entries. REQUIRED: emit at least 3 unless the primary
                          already aggregates the whole answer (e.g. a single
                          COUNT(*) over a tiny domain).
  assumed_interpretation: short Uzbek Latin sentence explaining HOW you
                          interpreted the question. SET ONLY when the question
                          is genuinely ambiguous and you had to make a real
                          interpretive choice. LEAVE EMPTY ("") for direct,
                          unambiguous questions. When non-empty, the narrator
                          opens with a short disclosure so the user can refine.
                          WHEN TO SET (non-empty):
                            * vague profile request ("Andijon haqida",
                              "kompleks ma'lumot ber") — picked one of several
                              reasonable broad interpretations
                            * metric word with multiple catalog mappings
                              ("biznes" -> active_businesses vs specialization
                              vs subsidy)
                            * the user named ONE entity but multiple entities
                              match (e.g. "Yoyilma mahallasi" when several
                              mahallas share that name) — chose to show all
                              rather than ask which
                          WHEN TO LEAVE EMPTY (""):
                            * explicit "top N by <clear metric>"
                            * exact lookup ("Samarqand viloyati aholi soni")
                            * obvious metric word on a named entity (reyting,
                              aholi, kuchli tomon) — script conversion is
                              routine, not an interpretation worth disclosing
                            * counts of catalog things ("qancha tuman bor?")
  memory_use            : one of "used", "ignored", "unclear" (optional)
  resolved_question     : string (optional; the question after any future
                          memory-based resolution; if omitted or empty the
                          backend falls back to the current user question)

PRIMARY SQL policy:
  - METRIC-FOCUSED PRIMARY (CRITICAL when the question names ONE metric).
    If the user's question explicitly names a single specific metric —
    "ishsizlik" / "ишсизлик" / "unemployed", "aholi" / "population",
    "reyting" / "rating", "biznes" / "active_businesses", "tibbiyot
    masofa" / "medical_facility_distance_km", "asfalt yo'l" /
    "road_asphalt_km", "muammoli kredit" / "problem_loans", "kam
    ta'minlangan oila" / "poor_families", "ekin maydoni",
    "ixtisoslashuv", a specific macro indicator key, etc. — the
    primary_sql MUST be NARROWLY focused on that metric:

      SELECT <entity name columns>, <THE asked metric>
      FROM <appropriate view>
      WHERE <entity filter>
      ORDER BY <THE asked metric> DESC NULLS LAST   -- or appropriate
      LIMIT N;

    Do NOT bundle population, businesses, rating, loans and the metric
    together in the SELECT just because v_regions / v_districts has all
    of them. That kind of "profile dump" is reserved for VAGUE questions
    ("Andijon haqida"), not metric-named questions. The downstream
    narrator leads its answer with the FIRST value column in the primary
    row — so if you put population first when the user asked about
    unemployment, the headline becomes about population. Always put THE
    ASKED METRIC as the primary value column.

    Context queries then broaden the picture: population for share
    context, district-level distribution, NULL counts, etc. The primary
    stays focused.

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

CONTEXT QUERIES policy (REQUIRED when kind=="sql_plan"):
  - Emit AT LEAST 3 and UP TO {max_ctx} extra read-only SELECTs. The
    downstream answer agent is rewarded for rich, comparative answers — so
    pull ENOUGH context to support 4-7 paragraphs of analysis.
  - Cover MULTIPLE angles for the same question shape:
      * top-N            -> SUM(metric) for share-of-total, AVG cohort
                            baseline, MIN/MAX extremes, COUNT(*) of NULLs,
                            COUNT of entities above/below average.
      * lowest-K         -> COUNT(*) at floor value, COUNT NULLs, AVG of
                            the rest, distribution by region/district,
                            related secondary metrics for the same rows.
      * single value     -> ROUND(CAST(AVG(metric) AS NUMERIC), 2)
                            baseline, MIN, MAX, peer percentile, related
                            siblings (e.g. road_asphalt_km next to
                            road_total_km), COUNT NULLs.
      * profile / "X haqida" -> demographic totals, business count,
                            rating, infrastructure aggregates, appeals
                            totals, top specializations, etc — paint a
                            full picture.
      * data-quality     -> COUNT per related issue_code, severity split,
                            top affected entities.
  - 0 context queries is acceptable ONLY when the primary already
    aggregates the entire answer (e.g. a single COUNT(*) of a tiny domain).
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

KIND choice (PREFER sql_plan ALWAYS — clarify is nearly forbidden):
  sql_plan    - question is answerable with one safe SELECT (plus REQUIRED
                3-{max_ctx} context queries). Provide primary_sql AND a short
                `assumed_interpretation` when the question was genuinely
                ambiguous. The downstream narrator shows the disclosure
                "Savolingizni shunday tushundim: <assumed_interpretation>.
                Boshqasi kerak bo'lsa, aniqroq yozing." so the user can
                refine without you blocking on a question. Also use this for
                ADVISORY questions (decompose into evidence-grounded
                sub-queries, never refuse the shape).
                THIS IS THE DEFAULT AND APPLIES TO ALMOST EVERY QUESTION.

  clarify     - NEARLY FORBIDDEN. Do NOT use clarify just because the
                question is broad, short, or vague. Pick the most
                reasonable interpretation, emit kind="sql_plan" with a
                clear `assumed_interpretation`, and let the user correct
                course via the disclaimer. Clarify is permitted only when:
                  (a) the message is literally a single ambiguous word
                      that maps to nothing in the catalog AND has no
                      reasonable default at all, or
                  (b) the user explicitly asks the assistant a meta
                      question ("nima qila olasan?") with no domain hint.
                In every other case use sql_plan + assumed_interpretation.
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
  * STEM AGGRESSIVELY. NEVER transliterate the user's spelling verbatim.
    Users typo Latin names all the time (Toshkent / Toshekent / Toshkeent
    / Toshkant — all the same place). The correct response is to extract
    the SHORTEST distinctive 3-5 char prefix (or root) and LIKE on that.
    Never embed the full user spelling in the LIKE pattern.
      "Toshkent" / "Toshekent" / "Toshkeent" -> LIKE '%Тошк%'
      "Andijon"  / "Andejon"   / "Андижан"   -> LIKE '%Андиж%'
      "Buxoro"   / "Buhoro"    / "Buxara"    -> LIKE '%Бухор%'
      "Marg'ilon" / "Margilon" / "Margilan"  -> LIKE '%Марғ%' OR LIKE '%Марг%'
      "Yoyilma"  / "Yayilma"                 -> LIKE '%Йойилма%' OR LIKE '%Ёйилма%'
      "Samarqand" / "Samarkand"              -> LIKE '%Самар%'
      "Farg'ona" / "Fergana"                 -> LIKE '%Фарғ%' OR LIKE '%Ферг%'
      "Qashqadaryo" / "Qashqadarya"          -> LIKE '%Қашқа%' OR LIKE '%Кашка%'
    The shorter the stem, the more typo-tolerant. As long as the stem is
    not a substring of any OTHER region/district name in the catalog (3-5
    chars is almost always safe), false positives are negligible.
  * For uncertain Cyrillic letter swaps (қ/к, ҳ/х, ў/у, ғ/г, ё/е), emit
    a 2-arm OR on the same column with both variants. Better to over-match
    than under-match.
  * LIKE filters in WHERE are allowed for this purpose. Do NOT JOIN on
    name columns — use the surrogate ids (mahalla_id, district_id,
    region_id) for joins, just like normal.
  * If the resulting SELECT returns 0 rows after stem-aggressive
    matching, that is a valid empty answer — the downstream agent will
    tell the user "topilmadi". Do not pre-emptively clarify.

  * MULTIPLE ENTITIES WITH THE SAME NAME (CRITICAL):
    Names like "Yoyilma", "Bog'", "Yangi hayot" exist in many districts.
    When the user names ONE such entity, you MUST:
    (a) ORDER BY <entity>_id FIRST so all rows of the same physical
        mahalla/district stay grouped — never let rows of different
        entities interleave. Example for peer_factors:
        `ORDER BY p.mahalla_id, p.factor_order`.
        For ranked top-N within named matches: keep the metric ORDER BY
        but always include the parent district_name_cyr in SELECT so
        each row is identifiable.
    (b) Always include enough parent context in the SELECT so different
        entities are distinguishable: region_name_cyr,
        district_name_cyr, mahalla_name_cyr together.
    (c) Add a context query that COUNTs distinct entities matching the
        same LIKE filter, so the answer can say "found N mahallas":
          SELECT COUNT(DISTINCT mahalla_id) AS distinct_matches
          FROM v_mahallas
          WHERE mahalla_name_cyr LIKE '%...%';
    (d) Set assumed_interpretation when the count is plural — explain
        you showed all matching entities. Empty when the user already
        gave full uniqueness (region + district + mahalla).

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
EXAMPLE A - top-N + rich context (5 context queries from different angles):
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "assumed_interpretation": "",
  "primary_sql": "SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5",
  "context_queries": [
    {"purpose": "total population for share calculation",
     "sql": "SELECT SUM(population) AS total_population FROM v_regions"},
    {"purpose": "average population baseline",
     "sql": "SELECT ROUND(CAST(AVG(population) AS NUMERIC), 1) AS avg_population FROM v_regions"},
    {"purpose": "median-ish population via MIN and MAX",
     "sql": "SELECT MIN(population) AS min_population, MAX(population) AS max_population FROM v_regions"},
    {"purpose": "regions with missing population data",
     "sql": "SELECT COUNT(*) AS missing_population FROM v_regions WHERE population IS NULL"},
    {"purpose": "active_businesses cross-metric for top-population regions context",
     "sql": "SELECT region_name_cyr, active_businesses FROM v_regions ORDER BY population DESC LIMIT 5"}
  ]
}

EXAMPLE B - lowest rating mahallas + peer-cohort context (rich set):
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "assumed_interpretation": "",
  "primary_sql": "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, rating_score FROM v_mahallas WHERE rating_score IS NOT NULL ORDER BY rating_score ASC LIMIT 10",
  "context_queries": [
    {"purpose": "average rating baseline",
     "sql": "SELECT ROUND(CAST(AVG(rating_score) AS NUMERIC), 1) AS avg_rating FROM v_mahallas WHERE rating_score IS NOT NULL"},
    {"purpose": "rating extremes",
     "sql": "SELECT MIN(rating_score) AS min_rating, MAX(rating_score) AS max_rating FROM v_mahallas WHERE rating_score IS NOT NULL"},
    {"purpose": "count of mahallas without rating",
     "sql": "SELECT COUNT(*) AS missing_rating FROM v_mahallas WHERE rating_score IS NULL"},
    {"purpose": "regions with most low-rating mahallas (bottom quartile)",
     "sql": "SELECT region_name_cyr, COUNT(*) AS low_rating_count FROM v_mahallas WHERE rating_score IS NOT NULL AND rating_score < 25 GROUP BY region_name_cyr ORDER BY low_rating_count DESC LIMIT 10"},
    {"purpose": "total mahalla count for share context",
     "sql": "SELECT COUNT(*) AS total_mahallas FROM v_mahallas"}
  ]
}

EXAMPLE C - tiny domain, primary already aggregates, 0 context allowed:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "assumed_interpretation": "",
  "primary_sql": "SELECT COUNT(*) AS total_issues FROM v_data_quality_issues WHERE issue_code='MAHALLA_STIR_DUPLICATE'",
  "context_queries": []
}

EXAMPLE C2 - broad "tell me about <region>" — DO NOT clarify; build full profile with assumed_interpretation:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "assumed_interpretation": "Andijon viloyati bo'yicha umumiy ko'rsatkichlarni (aholi, biznes, ishsizlik, reyting) va tumanlar ro'yxatini ko'rsatdim. Aniqroq savol berishingiz mumkin.",
  "primary_sql": "SELECT region_name_cyr, population, active_businesses, unemployed, rating_score, problem_loans, poor_families FROM v_regions WHERE region_name_cyr LIKE '%Андижон%'",
  "context_queries": [
    {"purpose": "districts in the region with KPIs",
     "sql": "SELECT district_name_cyr, population, active_businesses, rating_score FROM v_districts WHERE region_name_cyr LIKE '%Андижон%' ORDER BY population DESC LIMIT 50"},
    {"purpose": "mahalla count in the region",
     "sql": "SELECT COUNT(*) AS mahalla_count FROM v_mahallas WHERE region_name_cyr LIKE '%Андижон%'"},
    {"purpose": "top 10 mahallas by rating",
     "sql": "SELECT district_name_cyr, mahalla_name_cyr, rating_score FROM v_mahallas WHERE region_name_cyr LIKE '%Андижон%' AND rating_score IS NOT NULL ORDER BY rating_score DESC LIMIT 10"},
    {"purpose": "average mahalla rating in the region",
     "sql": "SELECT ROUND(CAST(AVG(rating_score) AS NUMERIC), 1) AS avg_rating FROM v_mahallas WHERE region_name_cyr LIKE '%Андижон%' AND rating_score IS NOT NULL"},
    {"purpose": "infrastructure aggregates",
     "sql": "SELECT ROUND(CAST(AVG(road_total_km) AS NUMERIC), 2) AS avg_road_km, ROUND(CAST(AVG(medical_facility_distance_km) AS NUMERIC), 2) AS avg_medical_km, SUM(school_count) AS total_schools FROM v_mahalla_infrastructure WHERE region_name_cyr LIKE '%Андижон%'"},
    {"purpose": "appeal totals",
     "sql": "SELECT SUM(crime_appeal_count) AS crime_total, SUM(employment_appeal_count) AS employment_total, SUM(social_aid_appeal_count) AS social_total FROM v_mahalla_appeals WHERE region_name_cyr LIKE '%Андижон%'"},
    {"purpose": "top specialization types by population",
     "sql": "SELECT specialization_type_cyr, SUM(population_count) AS pop_sum FROM v_mahalla_specializations WHERE region_name_cyr LIKE '%Андижон%' GROUP BY specialization_type_cyr ORDER BY pop_sum DESC LIMIT 5"}
  ]
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

EXAMPLE D - multi-entity case. User said only "Yoyilma" with no parent
district — multiple mahallas share the name. ORDER BY entity id first so
rows of the same mahalla stay together; include COUNT DISTINCT context;
non-empty assumed_interpretation because multiple entities match:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "assumed_interpretation": "Bir nechta mahalla shu nom bilan topilgani uchun barchasini ko'rsatdim. Aniq mahallani tanlash uchun tuman nomini ham kiriting.",
  "primary_sql": "SELECT m.region_name_cyr, m.district_name_cyr, m.mahalla_name_cyr, p.factor_label_cyr, p.entity_value_num, p.comparison_average_value, p.percentile FROM v_mahalla_peer_factors p JOIN v_mahallas m ON m.mahalla_id = p.mahalla_id WHERE p.factor_polarity = 'strength' AND (m.mahalla_name_cyr LIKE '%Йойилма%' OR m.mahalla_name_cyr LIKE '%Ёйилма%') ORDER BY p.mahalla_id, p.factor_order ASC LIMIT 200",
  "context_queries": [
    {"purpose": "count of distinct mahallas with this name",
     "sql": "SELECT COUNT(DISTINCT mahalla_id) AS distinct_matches FROM v_mahallas WHERE mahalla_name_cyr LIKE '%Йойилма%' OR mahalla_name_cyr LIKE '%Ёйилма%'"},
    {"purpose": "parent district and region for each matching mahalla",
     "sql": "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, population, rating_score FROM v_mahallas WHERE mahalla_name_cyr LIKE '%Йойилма%' OR mahalla_name_cyr LIKE '%Ёйилма%' ORDER BY mahalla_id LIMIT 50"},
    {"purpose": "count of strength factors per matching mahalla",
     "sql": "SELECT m.mahalla_id, m.district_name_cyr, COUNT(*) AS strength_count FROM v_mahalla_peer_factors p JOIN v_mahallas m ON m.mahalla_id = p.mahalla_id WHERE p.factor_polarity = 'strength' AND (m.mahalla_name_cyr LIKE '%Йойилма%' OR m.mahalla_name_cyr LIKE '%Ёйилма%') GROUP BY m.mahalla_id, m.district_name_cyr ORDER BY strength_count DESC"}
  ]
}

EXAMPLE D1 - same shape but user gave the parent district too, so the
result is a single mahalla — assumed_interpretation stays empty:
{
  "kind": "sql_plan",
  "user_message": "Natijani topdim.",
  "assumed_interpretation": "",
  "primary_sql": "SELECT m.region_name_cyr, m.district_name_cyr, m.mahalla_name_cyr, p.factor_label_cyr, p.entity_value_num, p.comparison_average_value, p.percentile FROM v_mahalla_peer_factors p JOIN v_mahallas m ON m.mahalla_id = p.mahalla_id WHERE p.factor_polarity = 'strength' AND (m.mahalla_name_cyr LIKE '%Йойилма%' OR m.mahalla_name_cyr LIKE '%Ёйилма%') AND (m.district_name_cyr LIKE '%Марғ%' OR m.district_name_cyr LIKE '%Марг%') ORDER BY p.mahalla_id, p.factor_order ASC",
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
