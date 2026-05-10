"""Deterministic metric/column resolver.

Maps known metric column names and Uzbek/English/Russian intent keywords to
the owning semantic view, the right `issue_code` for data-quality questions,
and explicit anti-hallucination constraints (e.g. "do not derive sotkah by
multiplication; column already exists").

Used between stage-1 schema linking and stage-2 SQL generation. The resolver
augments the LLM's `SchemaLink`; it never replaces the LLM, but it forces
the right view/column even when the LLM forgets where a column lives.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from cerr_chatbot.query.schema_linker import SchemaLink

# Column -> owning view. Treat as the single source of truth for "where
# does this metric live". Detail tables already include region/district/
# mahalla names so chatbot does not need a JOIN.
METRIC_TO_VIEW: dict[str, str] = {
    # Mahalla infrastructure
    "road_total_km": "v_mahalla_infrastructure",
    "road_asphalt_km": "v_mahalla_infrastructure",
    "road_dirt_km": "v_mahalla_infrastructure",
    "households_without_drinking_water_count": "v_mahalla_infrastructure",
    "power_outage_count": "v_mahalla_infrastructure",
    "power_outage_hours_text": "v_mahalla_infrastructure",
    "medical_facility_distance_km": "v_mahalla_infrastructure",
    "school_count": "v_mahalla_infrastructure",
    "sports_facility_count": "v_mahalla_infrastructure",
    "kindergarten_count": "v_mahalla_infrastructure",
    # Mahalla appeals
    "crime_appeal_count": "v_mahalla_appeals",
    "divorce_appeal_count": "v_mahalla_appeals",
    "social_aid_appeal_count": "v_mahalla_appeals",
    "employment_appeal_count": "v_mahalla_appeals",
    "gas_appeal_count": "v_mahalla_appeals",
    "registry_appeal_count": "v_mahalla_appeals",
    # Mahalla specializations
    "specialization_type_cyr": "v_mahalla_specializations",
    "specialization_direction_cyr": "v_mahalla_specializations",
    # Mahalla crops
    "total_area_ha": "v_mahalla_crops",
    "homestead_area_ha": "v_mahalla_crops",
    # Mahalla subsidies
    "subsidy_program_label_cyr": "v_mahalla_subsidy_programs",
    "application_count": "v_mahalla_subsidy_programs",
    "required_amount_mln_uzs": "v_mahalla_subsidy_programs",
    # Promoted scalars on v_mahallas (kept here intentionally so the
    # resolver knows where they live and forbids derivation).
    "crop_total_homestead_area_sotkah": "v_mahallas",
    "specialization_residual_percent": "v_mahallas",
    "specialization_total_known_percent": "v_mahallas",
    "rating_score": "v_mahallas",
    # Region-level KPIs
    "population": "v_regions",
    "active_businesses": "v_regions",
    "unemployed": "v_regions",
    "problem_loans": "v_regions",
    "poor_families": "v_regions",
    # Macro indicators
    "industry_volume_bln_uzs": "v_district_macro_highlights",
    "industry_growth_pct": "v_district_macro_highlights",
    "industry_per_capita_uzs": "v_district_macro_highlights",
    "export_volume_mln_usd": "v_district_macro_highlights",
    "export_growth_pct": "v_district_macro_highlights",
    "investment_volume_mln_usd": "v_district_macro_highlights",
    "investment_growth_pct": "v_district_macro_highlights",
    "agriculture_volume_bln": "v_district_macro_highlights",
    "agriculture_growth_pct": "v_district_macro_highlights",
    "budget_revenue_bln": "v_district_macro_highlights",
    "budget_revenue_growth_pct": "v_district_macro_highlights",
    "market_services_volume_bln": "v_district_macro_highlights",
    "market_services_growth_pct": "v_district_macro_highlights",
}

# Natural-language aliases users actually type. Each alias resolves to one
# or more canonical metric columns. Aliases are matched as whole substrings
# (case-insensitive). Order is irrelevant — multiple aliases may fire for
# one question. The mapped columns then flow through METRIC_TO_VIEW so the
# resolver can force the correct semantic view.
#
# Keys are kept short, lowercased, and language-mixed (Uzbek Latin / Russian
# Cyrillic / English) intentionally so a single resolver run handles all
# three input languages without an LLM.
METRIC_ALIASES: dict[str, tuple[str, ...]] = {
    # Population
    "aholi": ("population",),
    "aholisi": ("population",),
    "odamlar soni": ("population",),
    "odam soni": ("population",),
    "naselenie": ("population",),
    "население": ("population",),
    "people count": ("population",),
    # Business / entrepreneurship
    "biznes": ("active_businesses",),
    "tadbirkor": ("active_businesses",),
    "tadbirkorlik": ("active_businesses",),
    "korxona": ("active_businesses",),
    "korxonalar": ("active_businesses",),
    "biznes faol": ("active_businesses",),
    "active business": ("active_businesses",),
    # Unemployment / employment appeals
    "ishsiz": ("unemployed",),
    "ishsizlar": ("unemployed",),
    "ishsizlik": ("unemployed",),
    "bandlik muammo": ("employment_appeal_count",),
    "ish bilan band": ("employment_appeal_count",),
    "bandlikka oid": ("employment_appeal_count",),
    "employment appeal": ("employment_appeal_count",),
    # Rating
    "reyting": ("rating_score",),
    "reytingi": ("rating_score",),
    "ball": ("rating_score",),
    "baholash": ("rating_score",),
    "rating": ("rating_score",),
    # Roads / asphalt
    "yo'l uzunligi": ("road_total_km",),
    "yo'l hajmi": ("road_total_km",),
    "yo'llar": ("road_total_km",),
    "yo'l infratuzilma": ("road_total_km", "road_asphalt_km"),
    "yo'l infratuzilmasi": ("road_total_km", "road_asphalt_km"),
    "asfalt": ("road_asphalt_km",),
    "asfaltlangan": ("road_asphalt_km",),
    "tuproq yo'l": ("road_dirt_km",),
    # Medical
    "tibbiyot": ("medical_facility_distance_km",),
    "shifoxona masofa": ("medical_facility_distance_km",),
    "shifoxonagacha": ("medical_facility_distance_km",),
    "poliklinika": ("medical_facility_distance_km",),
    "tibbiyot muassasa": ("medical_facility_distance_km",),
    "medical facility": ("medical_facility_distance_km",),
    # Crime / divorce / social aid / gas / registry appeals
    "jinoyat": ("crime_appeal_count",),
    "jinoyat murojaat": ("crime_appeal_count",),
    "ajrim": ("divorce_appeal_count",),
    "ajralish": ("divorce_appeal_count",),
    "oila ajrim": ("divorce_appeal_count",),
    "divorce": ("divorce_appeal_count",),
    "ijtimoiy yordam": ("social_aid_appeal_count",),
    "gaz murojaat": ("gas_appeal_count",),
    "fhdyo": ("registry_appeal_count",),
    # Subsidy / applications
    "subsidiya": ("application_count", "required_amount_mln_uzs"),
    "subsidiya dastur": ("application_count", "required_amount_mln_uzs"),
    "ariza": ("application_count",),
    "arizalar": ("application_count",),
    # Specialization
    "ixtisoslash": ("specialization_type_cyr", "specialization_direction_cyr"),
    "ixtisoslashuv": ("specialization_type_cyr", "specialization_direction_cyr"),
    "nimaga ixtisoslash": ("specialization_direction_cyr",),
    # Crops / homestead
    "ekin maydon": ("total_area_ha",),
    "tomorqa": ("homestead_area_ha", "crop_total_homestead_area_sotkah"),
    "tomorqa maydon": ("homestead_area_ha", "crop_total_homestead_area_sotkah"),
    "sotix": ("crop_total_homestead_area_sotkah",),
    "sotkah": ("crop_total_homestead_area_sotkah",),
    # Macro indicators
    "sanoat hajmi": ("industry_volume_bln_uzs",),
    "sanoat ishlab chiqarish": ("industry_volume_bln_uzs",),
    "sanoat o'sish": ("industry_growth_pct",),
    "eksport hajmi": ("export_volume_mln_usd",),
    "eksport o'sish": ("export_growth_pct",),
    "investitsiya": ("investment_volume_mln_usd",),
    "investitsiya o'sish": ("investment_growth_pct",),
    "qishloq xo'jaligi": ("agriculture_volume_bln",),
    "byudjet daromadi": ("budget_revenue_bln",),
    "bozor xizmat": ("market_services_volume_bln",),
    # Infrastructure scalars
    "maktab": ("school_count",),
    "bog'cha": ("kindergarten_count",),
    "sport inshoot": ("sports_facility_count",),
    "ichimlik suv": ("households_without_drinking_water_count",),
    "elektr uzilish": ("power_outage_count",),
    # Loans / poverty
    "muammoli kredit": ("problem_loans",),
    "kambag'al oila": ("poor_families",),
    "ehtiyojmand oila": ("poor_families",),
    # Data quality
    "takror stir": ("__issue:MAHALLA_STIR_DUPLICATE",),
    "takror kod": ("__issue:DISTRICT_CODE_DUPLICATE_GLOBAL",),
    "takrorlangan stir": ("__issue:MAHALLA_STIR_DUPLICATE",),
    "duplicate stir": ("__issue:MAHALLA_STIR_DUPLICATE",),
}


# Columns that already exist in source and must NEVER be derived/computed
# in SQL (e.g. multiplying another column by a constant). The forbidden
# value is a short human note shown to the LLM.
FORBIDDEN_DERIVATIONS: dict[str, str] = {
    "crop_total_homestead_area_sotkah": (
        "do NOT compute as (homestead_area_ha * 10); use the existing "
        "v_mahallas.crop_total_homestead_area_sotkah column directly."
    ),
}


@dataclass(frozen=True)
class ResolverHint:
    forced_views: tuple[str, ...] = field(default_factory=tuple)
    forced_columns: tuple[str, ...] = field(default_factory=tuple)
    forced_metric_keys: tuple[str, ...] = field(default_factory=tuple)
    issue_codes: tuple[str, ...] = field(default_factory=tuple)
    forbidden_calculations: tuple[str, ...] = field(default_factory=tuple)
    pattern_hint: str | None = None
    limit_hint: int | None = None
    extra_notes: tuple[str, ...] = field(default_factory=tuple)


# Issue-code intents detected from question prose.
_DUPLICATE_DISTRICT_PAT = re.compile(
    r"(takror.*district_code|duplicate\s+district_code|district_code.*takror)",
    re.IGNORECASE,
)
_DUPLICATE_STIR_PAT = re.compile(
    r"(takror.*stir|duplicate\s+stir|stir.*takror|stir.*qiymati.*ko'p)",
    re.IGNORECASE,
)
_DQ_TOTAL_PAT = re.compile(
    r"(data quality|sifat muammo|jami muammo|total issues|issue.*total|"
    r"barcha muammo)",
    re.IGNORECASE,
)
_REGION_MAHALLA_MISMATCH_PAT = re.compile(
    r"(region_mahalla_count_mismatch|mahalla soni mos kelma|mismatch)",
    re.IGNORECASE,
)

# Distribution markers (require returning many groups, not one).
_DISTRIBUTION_PAT = re.compile(
    r"(har bir|taqsimot|distribution|nechta\s+\w+\s+toifa|nechta.*da|"
    r"counts? by|each\s+\w+|qaysi.*eng ko'p uchraydi|how many.*per|"
    r"har.*toifa)",
    re.IGNORECASE,
)
# Top-N marker; capture explicit N when present.
_TOP_N_PAT = re.compile(
    r"(?:top|eng\s+(?:yuqori|katta|past|kichik)|qaysi)\s*(\d+)",
    re.IGNORECASE,
)
# Sample marker; capture explicit N.
_SAMPLE_PAT = re.compile(
    r"(?:(\d+)\s*ta\s+namuna|namuna.*?(\d+)|(\d+)\s*examples)",
    re.IGNORECASE,
)


def resolve(user_question: str) -> ResolverHint:
    q = user_question
    q_lower = q.lower()
    forced_views: set[str] = set()
    forced_columns: set[str] = set()
    metric_keys: set[str] = set()
    issue_codes: set[str] = set()
    forbidden: list[str] = []
    notes: list[str] = []
    pattern: str | None = None
    limit: int | None = None

    # 1. Column-by-name detection. Substring is enough since planner echoes
    #    column names verbatim (e.g. "road_total_km bo'yicha eng katta").
    for col, view in METRIC_TO_VIEW.items():
        if col.lower() in q_lower:
            forced_views.add(view)
            forced_columns.add(col)
            # Macro indicator key columns also act as metric_key constants.
            if view == "v_district_macro_highlights":
                metric_keys.add(col)
            if col in FORBIDDEN_DERIVATIONS:
                forbidden.append(FORBIDDEN_DERIVATIONS[col])

    # 1b. Natural-language alias detection. Maps Uzbek/Russian/English phrases
    #     to the canonical column(s); aliases prefixed with `__issue:` route
    #     to v_data_quality_issues with the named issue_code.
    for alias, cols in METRIC_ALIASES.items():
        if alias not in q_lower:
            continue
        for col in cols:
            if col.startswith("__issue:"):
                code = col.split(":", 1)[1]
                forced_views.add("v_data_quality_issues")
                issue_codes.add(code)
                continue
            owning_view = METRIC_TO_VIEW.get(col)
            if not owning_view:
                continue
            forced_views.add(owning_view)
            forced_columns.add(col)
            if owning_view == "v_district_macro_highlights":
                metric_keys.add(col)
            if col in FORBIDDEN_DERIVATIONS:
                forbidden.append(FORBIDDEN_DERIVATIONS[col])

    # 2. Issue-code routing (questions about data quality).
    if _DUPLICATE_DISTRICT_PAT.search(q):
        forced_views.add("v_data_quality_issues")
        issue_codes.add("DISTRICT_CODE_DUPLICATE_GLOBAL")
        pattern = pattern or "duplicate"
        notes.append(
            "duplicate district_code questions MUST query "
            "v_data_quality_issues WHERE issue_code='DISTRICT_CODE_DUPLICATE_GLOBAL'."
        )
    if _DUPLICATE_STIR_PAT.search(q):
        forced_views.add("v_data_quality_issues")
        issue_codes.add("MAHALLA_STIR_DUPLICATE")
        pattern = pattern or "duplicate"
        notes.append(
            "duplicate STIR questions MUST query v_data_quality_issues "
            "WHERE issue_code='MAHALLA_STIR_DUPLICATE'. Do NOT GROUP BY "
            "mahalla_stir on v_mahallas."
        )
    if _REGION_MAHALLA_MISMATCH_PAT.search(q):
        forced_views.add("v_regions")
        notes.append(
            "mahalla_count_mismatch questions MUST use v_regions "
            "WHERE mahalla_count_mismatch_flag = 1."
        )
    if _DQ_TOTAL_PAT.search(q):
        forced_views.add("v_data_quality_issues")
        notes.append(
            "data-quality-total questions MUST include the scalar "
            "(SELECT COUNT(*) FROM v_data_quality_issues) AS total_issues."
        )

    # 3. Pattern + limit detection.
    if _DISTRIBUTION_PAT.search(q):
        pattern = pattern or "distribution"
        limit = max(limit or 0, 100)
    top_match = _TOP_N_PAT.search(q)
    if top_match:
        try:
            n = int(top_match.group(1))
        except (TypeError, ValueError):
            n = 0
        if n > 0 and n <= 500:
            pattern = pattern or "top_n"
            limit = max(limit or 0, n)
    sample_match = _SAMPLE_PAT.search(q)
    if sample_match:
        for grp in sample_match.groups():
            if grp:
                try:
                    n = int(grp)
                except (TypeError, ValueError):
                    continue
                if 0 < n <= 500:
                    pattern = pattern or "sample"
                    limit = max(limit or 0, n)
                    break

    return ResolverHint(
        forced_views=tuple(sorted(forced_views)),
        forced_columns=tuple(sorted(forced_columns)),
        forced_metric_keys=tuple(sorted(metric_keys)),
        issue_codes=tuple(sorted(issue_codes)),
        forbidden_calculations=tuple(forbidden),
        pattern_hint=pattern,
        limit_hint=limit,
        extra_notes=tuple(notes),
    )


def augment_schema_link(link: SchemaLink, hint: ResolverHint) -> SchemaLink:
    """Merge resolver hint into the LLM-produced SchemaLink.

    - forced_views / metric_keys / columns are added (deduplicated, deterministic order).
    - link.pattern is only overridden when it is "unknown".
    - issue_codes are exposed via metric_keys so stage-2 can use them as
      string constants in WHERE clauses.
    """
    views = list(link.relevant_views)
    for v in hint.forced_views:
        if v not in views:
            views.append(v)
    columns = list(link.relevant_columns)
    for c in hint.forced_columns:
        if c not in columns:
            columns.append(c)
    metric_keys = list(link.metric_keys)
    for k in list(hint.forced_metric_keys) + list(hint.issue_codes):
        if k not in metric_keys:
            metric_keys.append(k)
    pattern = link.pattern
    if pattern == "unknown" and hint.pattern_hint:
        pattern = hint.pattern_hint
    return SchemaLink(
        relevant_views=tuple(views),
        relevant_columns=tuple(columns),
        metric_keys=tuple(metric_keys),
        pattern=pattern,
        ambiguity_notes=link.ambiguity_notes,
    )


__all__ = [
    "FORBIDDEN_DERIVATIONS",
    "METRIC_ALIASES",
    "METRIC_TO_VIEW",
    "ResolverHint",
    "augment_schema_link",
    "resolve",
]
