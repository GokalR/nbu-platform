"""Prompt builder for the SQL planner.

Renders a compact view of the semantic catalog plus hard rules and
JSON-only output schema. The LLM receives one user_question and must respond
with a single JSON object. SQL is NOT mandatory - clarify, refuse, and
no_data are first-class outcomes.
"""

from __future__ import annotations

from cerr_chatbot.query.semantic_catalog import (
    GLOBAL_WARNINGS,
    SEMANTIC_CATALOG,
    SemanticView,
)

PROMPT_HEADER = """\
You are a careful read-only SQL planner over a small set of curated
semantic views. You do NOT execute SQL; another component does.

YOU MUST output exactly one JSON object and nothing else (no markdown,
no prose). The JSON object has these fields:

  kind                   : one of "sql", "clarify", "refuse", "no_data"
  sql                    : SQL string when kind=="sql", otherwise null
  user_message           : short natural-language message for the user
  reasoning_notes        : array of short strings (debug)
  expected_result_shape  : short text or null (e.g. "one row per region")

LANGUAGE POLICY for `user_message`:
  - Default language is Uzbek Latin (o'zbek lotin alifbosi).
  - Use Uzbek Latin for clarify, refuse, no_data and the short intro of
    sql results unless the user explicitly asks for another language.
  - If the user writes in another language and explicitly requests it,
    answer in that language.
  - Do NOT translate or transliterate source entity names (region,
    district, mahalla, status, category, indicator labels). Quote them
    exactly as they appear in the database.
  - Do NOT translate SQL column names or KPI keys.
  - Numeric values must stay exact; do not round, format, or scale.

SQL is NOT mandatory. Choose the kind honestly:

  sql       - question is answerable from semantic views with one safe SELECT
  clarify   - location, entity, or metric is ambiguous
  refuse    - request is unsafe, write, admin, raw-table, or external
  no_data   - the requested metric/concept is not in the semantic catalog

GLOBAL WARNINGS (apply to every SQL):
"""

REFUSE_RULES = """\
REFUSE if the user asks for any of:
  - direct access to raw tables or source files
  - INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, TRUNCATE, PRAGMA, VACUUM
  - import / scrape / load / admin operations
  - schema introspection or system catalogs
  - geographic / map / coordinates data (geo not exposed)
  - AI insights, narrative summaries, or LLM-generated text
  - private/company data not in the catalog
  - external web data, news, weather, etc.
  - "estimate", "guess", "assume", "fill missing values", "infer hidden numbers"

CLARIFY if:
  - location is ambiguous (which region/district/mahalla?)
  - the metric word maps to several columns (e.g. "business" could be
    active_businesses KPI, mahalla_specializations, or mahalla_subsidy_programs)
  - the question is too generic ("tell me about this region")

USE no_data when the user asks for a real-sounding metric that does NOT
appear in the catalog below. Do NOT invent columns.

SQL RULES:
  - SELECT only; one statement; no comments; no SELECT *.
  - Only the v_* views below. No raw tables.
  - Joins MUST use surrogate ids (region_id, district_id, mahalla_id) only.
    Never join by region_code, district_code, mahalla_stir, or names.
  - Allowed functions: COUNT, SUM, AVG, MIN, MAX, ROUND.
  - LIMIT required when the result could be large; max 500.
  - NULL means source missing/unavailable. NEVER COALESCE source metrics to 0.
    Only COALESCE to 0 when the user explicitly asks for COUNT-of-rows.
  - Treat missing macro highlighted values as missing source data, not zero.
"""

SQL_WRITING_GUIDE = """\
HOW TO WRITE SQL FOR THIS DATABASE:
  - Use semantic views as the complete read surface. Do not ask for raw tables.
  - Select useful answer columns, not only the metric: include entity names
    (region_name_cyr, district_name_cyr, mahalla_name_cyr), codes when useful,
    the requested metric value, and count/sum aliases for grouped answers.
  - Do not include rank columns. Window functions are blocked; ORDER BY + LIMIT
    is enough for top-N questions.
  - For top-N: ORDER BY the requested metric DESC (or ASC for "lowest") + LIMIT.
  - For grouped totals: GROUP BY the displayed dimension and use COUNT/SUM/AVG.
  - For missing/null questions: use IS NULL or COUNT(*) - COUNT(column).
    Never COALESCE missing source metrics to 0.
  - For multiple independent counts, scalar subqueries are allowed:
    SELECT (SELECT COUNT(*) FROM v_regions) AS region_count, ...
  - Detail views already include region/district/mahalla names and ids; do not
    join back to v_mahallas unless a needed column exists only there.
  - Join only on surrogate ids. Examples: i.mahalla_id = m.mahalla_id,
    d.region_id = r.region_id. Never join on codes, STIR, labels, or names.
  - Macro indicators are key-value rows, NOT individual columns. Metrics such
    as industry_volume_bln_uzs, export_volume_mln_usd, investment_growth_pct,
    agriculture_growth_pct, export_growth_pct must use:
      v_district_macro_highlights WHERE indicator_key = '<metric_key>'
    Do NOT return no_data for a metric that exists as indicator_key.
  - Peer factors are key-value rows, NOT individual columns. Use:
      v_mahalla_peer_factors WHERE factor_polarity = 'strength'/'weakness'
    and group/filter by factor_key. Do NOT return no_data for known factor_key
    questions.
  - Data-quality and duplicate-key questions use v_data_quality_issues.
    Duplicate issue codes include MAHALLA_STIR_DUPLICATE and
    DISTRICT_CODE_DUPLICATE_GLOBAL.
  - If a requested metric appears neither as a catalog column nor as a key
    value pattern described above, then use no_data.

GROUPING RULES (read carefully - common mistake):
  - "by region" / "viloyatlar bo'yicha" -> GROUP BY region_name_cyr ONLY.
    Do NOT also group by district_name_cyr or mahalla_id.
  - "by district" / "tumanlar bo'yicha" -> GROUP BY region_name_cyr,
    district_name_cyr.
  - "by mahalla" / "mahallalar bo'yicha" -> no GROUP BY, or group by
    mahalla_id when joining detail rows.
  - When the requested grain is "by region" but you also display
    district_name_cyr, the SUM/COUNT will be per-district which is wrong.

TOP-N AND DISTRIBUTION LIMITS (do not use LIMIT 1):
  - "Top N ..." -> LIMIT N exactly. "Top 10" -> LIMIT 10. "Top 5" -> LIMIT 5.
  - "Eng yuqori 5 ...", "eng katta 10 ..." -> match the explicit number.
  - "Distribution", "counts by ...", "each ...", "qaysi ... eng ko'p
    uchraydi", "har bir ... uchun" -> return ALL groups, use LIMIT 100,
    not LIMIT 1.
  - When ranking grouped rows, ALWAYS include COUNT(*) AS rows alongside
    SUM/AVG, so the answer shows both row count and metric total.

SAMPLE / EXAMPLE QUERIES (for "5 ta namuna", "show me 5 examples"):
  - ALWAYS add a stable ORDER BY on a deterministic column (an id, a name,
    or the metric itself). Without ORDER BY the database can return
    different rows on different runs.

MISSING / NULL / NEGATIVE QUESTIONS:
  - Always include explicit count columns: missing_<col>_rows for nullable
    cols (use COUNT(*) - COUNT(<col>)), negative_<col>_count for negative
    values (use a scalar subquery with WHERE <col> < 0), and MIN/MAX of the
    metric when extremes are requested.
  - When the question is about missing source values, the user_message in
    your JSON output MUST include the phrase "ma'lumot yo'q" so the user
    sees explicit missing-value wording in the answer.

ANSWER COMPLETENESS HINTS:
  - "X bo'yicha eng yuqori N ..." -> include the metric value and the
    grouping/entity name; if a related secondary metric (e.g. road_asphalt_km
    next to road_total_km) helps explain the answer, include it.
  - When the question mentions both a per-key metric AND a per-key total
    (e.g. "har bir dasturning application_count yig'indisi"), include
    COUNT(*) AS rows AND COUNT(*) - COUNT(<col>) AS null_<col>_rows so the
    answer shows totals + missing context together.
  - When the question asks for total/grand-sum across categories together
    with per-category counts, include a scalar subquery
    `(SELECT COUNT(*) FROM <view>) AS total_<thing>` so both per-row and
    grand-total numbers are present.
"""


_SQL_EXAMPLES: tuple[tuple[str, str], ...] = (
    (
        "count imported entity rows",
        "SELECT (SELECT COUNT(*) FROM v_regions) AS region_count, "
        "(SELECT COUNT(*) FROM v_districts) AS district_count, "
        "(SELECT COUNT(*) FROM v_mahallas) AS mahalla_count",
    ),
    (
        "regions where declared and actual mahalla counts differ",
        "SELECT region_code, region_name_cyr, declared_mahalla_count, actual_mahalla_count "
        "FROM v_regions WHERE mahalla_count_mismatch_flag = 1 "
        "ORDER BY region_code LIMIT 100",
    ),
    (
        "top regions by population",
        "SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5",
    ),
    (
        "top regions by active businesses",
        "SELECT region_name_cyr, active_businesses FROM v_regions "
        "ORDER BY active_businesses DESC LIMIT 5",
    ),
    (
        "duplicate district-code groups from data-quality issues",
        "SELECT issue_code, district_code, message FROM v_data_quality_issues "
        "WHERE issue_code = 'DISTRICT_CODE_DUPLICATE_GLOBAL' "
        "ORDER BY district_code LIMIT 100",
    ),
    (
        "duplicate mahalla STIR issue count",
        "SELECT COUNT(*) AS duplicate_stir_groups FROM v_data_quality_issues "
        "WHERE issue_code = 'MAHALLA_STIR_DUPLICATE'",
    ),
    (
        "sample duplicate mahalla STIR issue rows (deterministic order)",
        "SELECT mahalla_stir, message FROM v_data_quality_issues "
        "WHERE issue_code = 'MAHALLA_STIR_DUPLICATE' "
        "ORDER BY mahalla_stir LIMIT 5",
    ),
    (
        "top mahallas by population",
        "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, population "
        "FROM v_mahallas ORDER BY population DESC LIMIT 10",
    ),
    (
        "lowest mahalla rating score",
        "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, rating_score "
        "FROM v_mahallas ORDER BY rating_score ASC LIMIT 10",
    ),
    (
        "mahalla category distribution",
        "SELECT category_label_cyr, COUNT(*) AS mahalla_count FROM v_mahallas "
        "GROUP BY category_label_cyr ORDER BY mahalla_count DESC LIMIT 100",
    ),
    (
        "mahalla status distribution",
        "SELECT status_label_cyr, COUNT(*) AS mahalla_count FROM v_mahallas "
        "GROUP BY status_label_cyr ORDER BY mahalla_count DESC LIMIT 100",
    ),
    (
        "macro indicators with many missing highlighted values (with total_districts)",
        "SELECT h.indicator_key, h.indicator_label_cyr, COUNT(*) AS missing_count, "
        "(SELECT COUNT(*) FROM v_districts) AS total_districts "
        "FROM v_district_macro_highlights h WHERE h.highlighted_missing_flag = 1 "
        "GROUP BY h.indicator_key, h.indicator_label_cyr ORDER BY missing_count DESC LIMIT 10",
    ),
    (
        "industry volume macro metric via indicator_key",
        "SELECT region_name_cyr, district_name_cyr, highlighted_value_num, indicator_unit "
        "FROM v_district_macro_highlights "
        "WHERE indicator_key = 'industry_volume_bln_uzs' "
        "AND highlighted_value_num IS NOT NULL "
        "ORDER BY highlighted_value_num DESC LIMIT 10",
    ),
    (
        "export volume macro metric via indicator_key",
        "SELECT region_name_cyr, district_name_cyr, highlighted_value_num, indicator_unit "
        "FROM v_district_macro_highlights "
        "WHERE indicator_key = 'export_volume_mln_usd' "
        "AND highlighted_value_num IS NOT NULL "
        "ORDER BY highlighted_value_num DESC LIMIT 10",
    ),
    (
        "road length extremes (include both total and asphalt km)",
        "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, "
        "road_total_km, road_asphalt_km "
        "FROM v_mahalla_infrastructure WHERE road_total_km IS NOT NULL "
        "ORDER BY road_total_km DESC LIMIT 10",
    ),
    (
        "medical facility distance extremes",
        "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, medical_facility_distance_km "
        "FROM v_mahalla_infrastructure WHERE medical_facility_distance_km IS NOT NULL "
        "ORDER BY medical_facility_distance_km DESC LIMIT 10",
    ),
    (
        "crime appeals by region with known/missing row counts",
        "SELECT region_name_cyr, SUM(crime_appeal_count) AS crime_appeal_count_sum, "
        "COUNT(crime_appeal_count) AS known_rows, "
        "COUNT(*) - COUNT(crime_appeal_count) AS missing_rows "
        "FROM v_mahalla_appeals GROUP BY region_name_cyr "
        "ORDER BY crime_appeal_count_sum DESC LIMIT 100",
    ),
    (
        "top mahallas by employment appeals",
        "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, employment_appeal_count "
        "FROM v_mahalla_appeals WHERE employment_appeal_count IS NOT NULL "
        "ORDER BY employment_appeal_count DESC LIMIT 10",
    ),
    (
        "missing divorce appeal rows by region",
        "SELECT region_name_cyr, COUNT(*) AS total_rows, "
        "COUNT(*) - COUNT(divorce_appeal_count) AS missing_divorce_rows "
        "FROM v_mahalla_appeals GROUP BY region_name_cyr "
        "ORDER BY missing_divorce_rows DESC LIMIT 100",
    ),
    (
        "specialization type counts and population sums",
        "SELECT specialization_type_cyr, COUNT(*) AS rows, "
        "SUM(population_count) AS population_count_sum "
        "FROM v_mahalla_specializations GROUP BY specialization_type_cyr "
        "ORDER BY rows DESC LIMIT 100",
    ),
    (
        "specialization directions by population",
        "SELECT specialization_direction_cyr, COUNT(*) AS rows, "
        "SUM(population_count) AS population_count_sum "
        "FROM v_mahalla_specializations GROUP BY specialization_direction_cyr "
        "ORDER BY population_count_sum DESC LIMIT 10",
    ),
    (
        "crop rows with missing total area and negative homestead area",
        "SELECT COUNT(*) AS crop_rows, "
        "COUNT(*) - COUNT(c.total_area_ha) AS missing_total_area_rows, "
        "(SELECT COUNT(*) FROM v_mahalla_crops c2 WHERE c2.homestead_area_ha < 0) "
        "AS negative_homestead_area_count, "
        "MIN(c.homestead_area_ha) AS min_homestead_area_ha "
        "FROM v_mahalla_crops c",
    ),
    (
        "top mahallas by crop_total_homestead_area_sotkah from v_mahallas",
        "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, "
        "crop_total_homestead_area_sotkah FROM v_mahallas "
        "WHERE crop_total_homestead_area_sotkah IS NOT NULL "
        "ORDER BY crop_total_homestead_area_sotkah DESC LIMIT 10",
    ),
    (
        "subsidy program totals with null application rows",
        "SELECT subsidy_program_label_cyr, COUNT(*) AS rows, "
        "SUM(application_count) AS application_count_sum, "
        "COUNT(*) - COUNT(application_count) AS null_application_rows "
        "FROM v_mahalla_subsidy_programs GROUP BY subsidy_program_label_cyr "
        "ORDER BY application_count_sum DESC LIMIT 100",
    ),
    (
        "missing subsidy required amount rows",
        "SELECT COUNT(*) AS total_rows, "
        "COUNT(*) - COUNT(required_amount_mln_uzs) AS missing_required_amount_rows "
        "FROM v_mahalla_subsidy_programs",
    ),
    (
        "most frequent peer strength factor keys",
        "SELECT factor_key, factor_label_cyr, COUNT(*) AS row_count "
        "FROM v_mahalla_peer_factors WHERE factor_polarity = 'strength' "
        "GROUP BY factor_key, factor_label_cyr ORDER BY row_count DESC LIMIT 10",
    ),
    (
        "most frequent peer weakness factor keys",
        "SELECT factor_key, factor_label_cyr, COUNT(*) AS row_count "
        "FROM v_mahalla_peer_factors WHERE factor_polarity = 'weakness' "
        "GROUP BY factor_key, factor_label_cyr ORDER BY row_count DESC LIMIT 10",
    ),
    (
        "data-quality issue counts by code (with total)",
        "SELECT q.issue_code, COUNT(*) AS issue_count, "
        "(SELECT COUNT(*) FROM v_data_quality_issues) AS total_issues "
        "FROM v_data_quality_issues q "
        "GROUP BY q.issue_code ORDER BY issue_count DESC LIMIT 100",
    ),
    (
        "combined independent counts without unsafe joins or union",
        "SELECT (SELECT COUNT(*) FROM v_regions r WHERE r.mahalla_count_mismatch_flag = 1) "
        "AS regions_with_mahalla_count_mismatch, "
        "(SELECT COUNT(*) FROM v_district_macro_highlights h WHERE h.highlighted_missing_flag = 1) "
        "AS macro_highlights_missing, "
        "(SELECT COUNT(*) FROM v_mahalla_infrastructure i WHERE i.road_total_km > 1000) "
        "AS mahallas_with_road_total_km_gt_1000, "
        "(SELECT COUNT(*) FROM v_mahalla_crops c WHERE c.homestead_area_ha < 0) "
        "AS crop_rows_with_negative_homestead_area_ha, "
        "(SELECT COUNT(*) FROM v_data_quality_issues) AS data_quality_issues_total",
    ),
    (
        "valid join by surrogate mahalla_id when a column exists only on v_mahallas",
        "SELECT m.region_name_cyr, m.district_name_cyr, m.mahalla_name_cyr, "
        "m.rating_score, i.road_total_km FROM v_mahallas m "
        "JOIN v_mahalla_infrastructure i ON i.mahalla_id = m.mahalla_id "
        "ORDER BY i.road_total_km DESC LIMIT 10",
    ),
)


def _render_sql_examples() -> str:
    lines = ["SQL COOKBOOK EXAMPLES (copy these patterns; adapt columns/filters only):"]
    for i, (title, sql) in enumerate(_SQL_EXAMPLES, start=1):
        lines.append(f"SQL EXAMPLE {i} - {title}:")
        lines.append(f"  {sql}")
    return "\n".join(lines)


def _render_view(view: SemanticView) -> list[str]:
    lines = [f"## {view.name}"]
    lines.append(f"  grain: {view.grain}")
    lines.append(f"  purpose: {view.purpose}")
    lines.append("  columns:")
    for col in view.columns:
        nullable = "" if col.nullable else " NOT NULL"
        lines.append(f"    - {col.name}{nullable}: {col.description}")
    if view.join_keys:
        lines.append(f"  join_keys: {', '.join(view.join_keys)}")
    if view.warnings:
        lines.append("  warnings:")
        for w in view.warnings:
            lines.append(f"    - {w}")
    return lines


def _render_catalog() -> str:
    lines: list[str] = []
    for name in sorted(SEMANTIC_CATALOG):
        lines.extend(_render_view(SEMANTIC_CATALOG[name]))
        lines.append("")
    return "\n".join(lines).rstrip()


_FEW_SHOT_EXAMPLES = """\
EXAMPLE 1 - clear numeric question:
  User: "Top 5 regions by population"
  Output:
    {"kind": "sql",
     "sql": "SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5",
     "user_message": "Aholi soni bo'yicha eng yuqori 5 viloyat.",
     "reasoning_notes": ["population is a base KPI on v_regions"],
     "expected_result_shape": "5 rows: region_name_cyr, population"}

EXAMPLE 2 - ambiguous metric:
  User: "Mahalladagi biznes nima?"
  Output:
    {"kind": "clarify",
     "sql": null,
     "user_message": "Qaysi ko'rsatkich kerak: active_businesses (KPI), ixtisoslashuv yoki subsidiya dasturi? Iltimos aniqlashtiring.",
     "reasoning_notes": ["metric 'biznes' maps to multiple columns"],
     "expected_result_shape": null}

EXAMPLE 3 - unsafe / write:
  User: "Delete all problem loans rows"
  Output:
    {"kind": "refuse",
     "sql": null,
     "user_message": "Yozish va o'chirish amallariga ruxsat berilmagan.",
     "reasoning_notes": ["DELETE rejected"],
     "expected_result_shape": null}

EXAMPLE 4 - metric not in catalog:
  User: "Viloyatning YIM ko'rsatkichi qancha?"
  Output:
    {"kind": "no_data",
     "sql": null,
     "user_message": "YIM ko'rsatkichi mavjud semantik ko'rinishlarda yo'q.",
     "reasoning_notes": ["no GDP column in catalog"],
     "expected_result_shape": null}
"""


def build_planner_prompt(user_question: str) -> str:
    """Render the full planner prompt for one user question."""
    parts: list[str] = []
    parts.append(PROMPT_HEADER)
    for w in GLOBAL_WARNINGS:
        parts.append(f"  - {w}")
    parts.append("")
    parts.append(REFUSE_RULES)
    parts.append("")
    parts.append(SQL_WRITING_GUIDE)
    parts.append("")
    parts.append("SEMANTIC CATALOG:")
    parts.append("")
    parts.append(_render_catalog())
    parts.append("")
    parts.append(_render_sql_examples())
    parts.append("")
    parts.append(_FEW_SHOT_EXAMPLES)
    parts.append("")
    parts.append(f"User question: {user_question}")
    parts.append("")
    parts.append("Reply with one JSON object only.")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Stage-2 SQL prompt builder (paired with schema_linker.build_schema_linking_prompt).
# Compact: only relevant catalog views + tag-selected examples + JSON output schema.
# Designed to keep token count low and focus the LLM on the right patterns.
# ---------------------------------------------------------------------------

from cerr_chatbot.query.example_bank import (  # noqa: E402  - end-of-file by design
    PromptExample,
    select_examples,
)
from cerr_chatbot.query.metric_resolver import (  # noqa: E402
    METRIC_TO_VIEW,
    ResolverHint,
    augment_schema_link,
    resolve,
)
from cerr_chatbot.query.schema_linker import SchemaLink  # noqa: E402

_SQL_PROMPT_HEADER = """\
You are stage 2 of a 2-stage SQL planner. Stage 1 already named the
relevant views, columns, and metric keys. Your job is to emit ONE JSON
object describing the answer.

Output schema (return JSON only, no markdown, no prose around it):

  kind                  : one of "sql", "clarify", "refuse", "no_data"
  sql                   : SQL string when kind=="sql", otherwise null
  user_message          : short user-facing message
  reasoning_notes       : array of short strings (debug)
  expected_result_shape : short text or null

LANGUAGE POLICY for `user_message`:
  - Default Uzbek Latin. Source entity names (region, district, mahalla,
    indicator labels) and SQL column names are NOT translated. Numbers
    stay exact.
  - For missing/null/negative questions, INCLUDE the phrase "ma'lumot yo'q"
    in user_message so the user sees explicit missing-value wording.

HARD SQL RULES (sql_guard enforces; the LLM MUST already obey):
  - SELECT only; one statement; no comments; no SELECT *.
  - Only the v_* views shown below; no raw tables; no schema-qualified names.
  - JOIN ON / USING surrogate ids ONLY: region_id, district_id, mahalla_id.
    Never join on natural keys (region_code, district_code, mahalla_stir,
    names).
  - Allowed functions: COUNT, SUM, AVG, MIN, MAX, ROUND. No window funcs.
  - LIMIT required (max 500). Default 100 when in doubt.

ANSWER-COMPLETENESS HINTS:
  - "Top N" -> ORDER BY metric DESC LIMIT N. NEVER LIMIT 1 for top-N or
    distribution requests.
  - "by region" -> GROUP BY region_name_cyr ONLY (not region+district).
    "by district" -> GROUP BY region_name_cyr, district_name_cyr.
  - Sample/example queries: ALWAYS include a deterministic ORDER BY.
  - Missing/null counts: use COUNT(*) - COUNT(<col>) AS missing_<col>_rows;
    for negative counts use a scalar subquery WHERE col < 0.
  - When a question implies a grand total, add a scalar subquery
    (SELECT COUNT(*) FROM <view>) AS total_<thing>.
  - Macro indicators are key-value rows:
      v_district_macro_highlights WHERE indicator_key = '<key>'
    Peer factors are key-value rows:
      v_mahalla_peer_factors WHERE factor_polarity = 'strength'/'weakness'
"""


def _render_relevant_views(view_names: tuple[str, ...]) -> str:
    if not view_names:
        # No schema link available; fall back to a compact list of all views.
        view_names = tuple(sorted(SEMANTIC_CATALOG))
    lines: list[str] = []
    for name in view_names:
        view = SEMANTIC_CATALOG.get(name)
        if view is None:
            continue
        lines.extend(_render_view(view))
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_examples_block(examples: list[PromptExample]) -> str:
    out: list[str] = ["RELEVANT SQL EXAMPLES (copy these patterns; adapt columns/filters only):"]
    for i, ex in enumerate(examples, start=1):
        out.append(f"EXAMPLE {i} - {ex.title}:")
        out.append(f"  {ex.sql}")
    return "\n".join(out)


def _render_schema_link_summary(link: SchemaLink) -> str:
    parts = [
        f"  pattern              : {link.pattern}",
        f"  relevant_views       : {list(link.relevant_views)}",
        f"  relevant_columns     : {list(link.relevant_columns)}",
        f"  metric_keys          : {list(link.metric_keys)}",
    ]
    if link.ambiguity_notes:
        parts.append(f"  ambiguity_notes      : {list(link.ambiguity_notes)}")
    return "\n".join(parts)


_RESOLVER_RULES_HEADER = """\
DETERMINISTIC RESOLVER RULES (highest priority - obey even if examples disagree):
  - NEVER move a column to another view. Each column lives on exactly one
    view; the resolver lists those view-column pairs explicitly below.
    Example: road_total_km, road_asphalt_km, medical_facility_distance_km
    live on v_mahalla_infrastructure ONLY. Do NOT write
    v_mahallas.road_total_km. v_mahallas does not have those columns.
  - NEVER calculate a source column that already exists. If the resolver
    says a column is forbidden_to_derive, SELECT it directly. Example:
    crop_total_homestead_area_sotkah is a real column on v_mahallas.
    Do NOT compute it as (homestead_area_ha * 10).
  - For "duplicate STIR / district_code" questions, query
    v_data_quality_issues filtered by the issue_code constant the resolver
    lists. Do NOT GROUP BY natural keys on the entity views.
  - When the resolver supplies a limit_hint, use exactly that LIMIT.
    distribution => LIMIT 100, top-N => LIMIT N, sample => LIMIT N.
"""


def _render_resolver_block(hint: ResolverHint) -> str:
    lines: list[str] = ["RESOLVER OVERRIDES (apply before stage-1 hints):"]
    if hint.forced_views:
        lines.append(f"  forced_views          : {list(hint.forced_views)}")
    if hint.forced_columns:
        lines.append(
            "  view_for_column       : "
            + ", ".join(f"{c} -> {METRIC_TO_VIEW.get(c, '?')}" for c in hint.forced_columns)
        )
    if hint.forced_metric_keys:
        lines.append(f"  forced_metric_keys    : {list(hint.forced_metric_keys)}")
    if hint.issue_codes:
        lines.append(f"  issue_codes           : {list(hint.issue_codes)}")
    if hint.pattern_hint:
        lines.append(f"  pattern_hint          : {hint.pattern_hint}")
    if hint.limit_hint:
        lines.append(f"  limit_hint            : {hint.limit_hint}")
    if hint.forbidden_calculations:
        lines.append("  forbidden_calculations:")
        for f in hint.forbidden_calculations:
            lines.append(f"    - {f}")
    if hint.extra_notes:
        lines.append("  notes:")
        for n in hint.extra_notes:
            lines.append(f"    - {n}")
    if len(lines) == 1:
        lines.append("  (no overrides; trust stage-1 schema link)")
    return "\n".join(lines)


def build_sql_prompt(
    user_question: str,
    schema_link: SchemaLink,
    *,
    k_examples: int = 5,
) -> str:
    """Stage-2 prompt: schema-link + deterministic resolver overrides + examples.

    The resolver runs first and merges its hints into the link, so the LLM
    sees authoritative view/column placements even if stage 1 missed them.
    """
    hint = resolve(user_question)
    effective_link = augment_schema_link(schema_link, hint)
    examples = select_examples(
        user_question,
        relevant_views=effective_link.relevant_views,
        pattern=effective_link.pattern if effective_link.pattern != "unknown" else None,
        k=k_examples,
    )

    parts: list[str] = []
    parts.append(_SQL_PROMPT_HEADER)
    parts.append("")
    parts.append(_RESOLVER_RULES_HEADER)
    parts.append("")
    parts.append(_render_resolver_block(hint))
    parts.append("")
    parts.append("STAGE-1 SCHEMA-LINKING SUMMARY (after resolver merge):")
    parts.append(_render_schema_link_summary(effective_link))
    parts.append("")
    parts.append("RELEVANT VIEWS (full column detail; only these may appear in FROM/JOIN):")
    parts.append("")
    parts.append(_render_relevant_views(effective_link.relevant_views))
    parts.append("")
    parts.append(_render_examples_block(examples))
    parts.append("")
    parts.append(f"User question: {user_question}")
    parts.append("")
    parts.append("Reply with one JSON object only.")
    return "\n".join(parts)


__all__ = ["build_planner_prompt", "build_sql_prompt"]
