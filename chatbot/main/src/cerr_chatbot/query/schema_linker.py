"""Stage-1 prompt + parser: schema linking.

The LLM receives a compact summary of all views (one line per view, key
columns hint) and is asked to return a small JSON document naming the
specific views, columns, metric/indicator/factor keys, the answer pattern,
and any ambiguity it sees.

Stage 2 (build_sql_prompt) then receives only the relevant catalog slice +
selected examples. Two-stage design keeps each prompt small and on-task.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG

ALLOWED_PATTERNS: tuple[str, ...] = (
    "top_n",
    "distribution",
    "scalar_count",
    "missing_null",
    "duplicate",
    "macro_indicator",
    "peer_factor",
    "sample",
    "group_by_region",
    "group_by_district",
    "unknown",
)


@dataclass(frozen=True)
class SchemaLink:
    relevant_views: tuple[str, ...] = field(default_factory=tuple)
    relevant_columns: tuple[str, ...] = field(default_factory=tuple)
    metric_keys: tuple[str, ...] = field(default_factory=tuple)
    pattern: str = "unknown"
    ambiguity_notes: tuple[str, ...] = field(default_factory=tuple)


class SchemaLinkParseError(ValueError):
    """LLM stage-1 output could not be parsed into a SchemaLink."""


_LINKER_HEADER = """\
You are stage 1 of a 2-stage SQL planner. Your job is schema linking, NOT
SQL generation. Read the user question and pick the most relevant views,
columns, and (where applicable) metric/indicator/factor key values.

Output exactly one JSON object with these fields and nothing else:

  relevant_views     : array of view names from the list below (1-3 typically)
  relevant_columns   : array of column names you expect to use
  metric_keys        : array of indicator_key / factor_key / kpi_key string
                       constants the question implies (e.g. "industry_volume_bln_uzs")
  pattern            : one of "top_n", "distribution", "scalar_count",
                       "missing_null", "duplicate", "macro_indicator",
                       "peer_factor", "sample", "group_by_region",
                       "group_by_district", "unknown"
  ambiguity_notes    : array of short strings if entity/metric is ambiguous

LANGUAGE: question may be Uzbek Latin, Russian, or English.
DO NOT write SQL here. DO NOT add prose around the JSON.
"""


def _render_compact_views() -> str:
    """One concise paragraph per view: name, grain, top columns."""
    lines: list[str] = []
    for name in sorted(SEMANTIC_CATALOG):
        v = SEMANTIC_CATALOG[name]
        cols = ", ".join(c.name for c in v.columns[:8])
        if len(v.columns) > 8:
            cols += ", ..."
        lines.append(f"- {name} ({v.grain}): {cols}")
    return "\n".join(lines)


def build_schema_linking_prompt(user_question: str) -> str:
    parts: list[str] = []
    parts.append(_LINKER_HEADER)
    parts.append("")
    parts.append("AVAILABLE VIEWS (compact):")
    parts.append(_render_compact_views())
    parts.append("")
    parts.append("KNOWN METRIC/INDICATOR/FACTOR KEY EXAMPLES:")
    parts.append(
        "  KPI keys (entity_kpis): population, active_businesses, unemployed, "
        "rating_score, problem_loans, poor_families."
    )
    parts.append(
        "  macro indicator_key examples: industry_volume_bln_uzs, "
        "industry_growth_pct, export_volume_mln_usd, export_growth_pct, "
        "investment_volume_mln_usd, investment_growth_pct, "
        "agriculture_volume_bln, agriculture_growth_pct, budget_revenue_bln, "
        "budget_revenue_growth_pct, market_services_volume_bln, "
        "market_services_growth_pct, poverty_rate_pct_2026_01_01, "
        "poverty_rate_pct_2026_04_01, unemployment_rate_pct_2026_01_01, "
        "unemployment_rate_pct_2026_04_01, industry_per_capita_uzs."
    )
    parts.append(
        "  data quality issue_code values: MAHALLA_STIR_DUPLICATE, "
        "DISTRICT_CODE_DUPLICATE_GLOBAL, DISTRICT_CODE_PREFIX_MISMATCH, "
        "REGION_MAHALLA_COUNT_MISMATCH."
    )
    parts.append("")
    parts.append(f"User question: {user_question}")
    parts.append("")
    parts.append("Reply with one JSON object only.")
    return "\n".join(parts)


def parse_schema_linking_response(text: str) -> SchemaLink:
    if not isinstance(text, str) or not text.strip():
        raise SchemaLinkParseError("empty schema-linking response")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SchemaLinkParseError(f"not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SchemaLinkParseError("response must be a JSON object")

    relevant_views = _coerce_str_list(data.get("relevant_views"), "relevant_views")
    relevant_columns = _coerce_str_list(data.get("relevant_columns"), "relevant_columns")
    metric_keys = _coerce_str_list(data.get("metric_keys"), "metric_keys")
    ambiguity_notes = _coerce_str_list(data.get("ambiguity_notes"), "ambiguity_notes")
    pattern = data.get("pattern", "unknown")
    if not isinstance(pattern, str) or pattern not in ALLOWED_PATTERNS:
        raise SchemaLinkParseError(f"pattern must be one of {ALLOWED_PATTERNS}, got {pattern!r}")

    # Strip any view names not in the catalog so stage 2 cannot be fooled.
    safe_views = tuple(v for v in relevant_views if v in SEMANTIC_CATALOG)
    return SchemaLink(
        relevant_views=safe_views,
        relevant_columns=tuple(relevant_columns),
        metric_keys=tuple(metric_keys),
        pattern=pattern,
        ambiguity_notes=tuple(ambiguity_notes),
    )


def _coerce_str_list(raw: object, field_name: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SchemaLinkParseError(f"{field_name} must be a list of strings or absent")
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise SchemaLinkParseError(f"{field_name} entries must be strings")
        out.append(item)
    return out


__all__ = [
    "ALLOWED_PATTERNS",
    "SchemaLink",
    "SchemaLinkParseError",
    "build_schema_linking_prompt",
    "parse_schema_linking_response",
]
