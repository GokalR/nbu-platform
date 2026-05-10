"""Classify each question into an answer archetype + insight contract.

The narrator used to apply one "rich analyst" template to every question,
which produced absurd insights for exact-lookup answers (`100% of shown
results`, `gap = 0`, `highest and lowest are the same`). This module
maps `(question, primary_result, context_results) -> AnswerBrief` so the
narrator prompt can be told *which* kinds of insight are appropriate for
*this* question.

Pure transformation. No LLM, no DB. Classification uses lightweight
keyword regexes over the question plus the row-count of the primary
result. The brief is then injected into the narrator prompt as an
`ANSWER BRIEF` section with allowed / forbidden insight modes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

AnswerType = Literal[
    "exact_lookup",
    "top_n_ranking",
    "comparison",
    "distribution",
    "entity_profile",
    "data_quality",
    "no_rows",
    "generic_analytical",
]


@dataclass(frozen=True)
class AnswerBrief:
    answer_type: AnswerType
    user_goal: str
    allowed_insight_modes: tuple[str, ...] = field(default_factory=tuple)
    forbidden_insight_modes: tuple[str, ...] = field(default_factory=tuple)
    style_rules: tuple[str, ...] = field(default_factory=tuple)
    reason: str = ""


# ---------------------------------------------------------------------------
# Keyword matchers (Uzbek Latin + a few English fallbacks)
# ---------------------------------------------------------------------------

# Exact lookup phrasing: how many / count / show me / value of …
_EXACT_LOOKUP_PAT = re.compile(
    r"\b("
    r"qancha|nechta|necha\s*ta|qiymati(?:ni)?|"
    r"soni\s+qancha|soni\s+nechta|soni\s+ko'rsat|"
    r"ko'rsat(?:ing)?|ko'rsatib|"
    r"value\s+of|how\s+many|how\s+much|count\s+of"
    r")\b",
    re.IGNORECASE,
)

# Top-N / extreme / leader phrasing.
_TOP_N_PAT = re.compile(
    r"\b("
    r"eng\s+ko'p|eng\s+yuqori|eng\s+past|eng\s+katta|eng\s+kichik|"
    r"eng\s+yaxshi|eng\s+yomon|"
    r"top(?:[-\s]?\d+)?|reyting|leader|highest|lowest|maximum|minimum|"
    r"birinchi(?:\s+\d+)?|oxirgi(?:\s+\d+)?"
    r")\b",
    re.IGNORECASE,
)

# Comparison phrasing.
_COMPARISON_PAT = re.compile(
    r"\b("
    r"taqqoslash|taqqosla|farq(?:i)?|vs\b|qaysi(?:si)?\s+yuqoriroq|"
    r"qaysi(?:si)?\s+pastroq|qaysi(?:si)?\s+ko'proq|qaysi(?:si)?\s+kamroq|"
    r"compare|difference\s+between"
    r")\b",
    re.IGNORECASE,
)

# Distribution phrasing.
_DISTRIBUTION_PAT = re.compile(
    r"\b("
    r"har\s+bir|taqsimot|bo'yicha\s+nechta|nechta\s+\w+\s+bo'yicha|"
    r"counts?\s+by|distribution|breakdown|histogram"
    r")\b",
    re.IGNORECASE,
)

# Entity-profile phrasing (single entity overview).
_ENTITY_PROFILE_PAT = re.compile(
    r"("
    r"\bkuchli\s+tomon|"
    r"\bkuchsiz\s+tomon|"
    r"\bhaqida\b|"
    r"\bprofil(?:e)?\b|"
    r"\boverview\b|"
    r"\bstrengths?\b|"
    r"\bweaknesses?\b|"
    r"\bumumiy\s+ma'lumot"
    r")",
    re.IGNORECASE,
)

# Data-quality phrasing.
_DATA_QUALITY_PAT = re.compile(
    r"\b("
    r"takror|takrorlangan|duplicate|"
    r"mos\s+kelma(?:ydi|gan)|mismatch|"
    r"data\s+quality|sifat\s+muammo|import\s+muammo|"
    r"issue_code|issue\s+code|muammo(?:lar)?\s+soni"
    r")\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Insight-mode catalogues + style rules
# ---------------------------------------------------------------------------


def _no_rows_brief(question: str) -> AnswerBrief:
    return AnswerBrief(
        answer_type="no_rows",
        user_goal=(
            "Tell the user that no matching data was found, briefly suggest "
            "checking the spelling of the entity name or trying a broader query."
        ),
        allowed_insight_modes=(
            "say_no_data_found",
            "suggest_check_spelling",
            "suggest_broader_query",
        ),
        forbidden_insight_modes=(
            "ranking",
            "share_of_shown",
            "comparison",
            "invented_alternatives",
            "highest_lowest",
            "gap_zero",
        ),
        style_rules=(
            "1-2 short sentences in Uzbek Latin. No table. No invented numbers.",
        ),
        reason="primary result returned 0 rows",
    )


def _exact_lookup_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="exact_lookup",
        user_goal=(
            "Answer the specific value(s) the user asked for. Then add a "
            "short useful interpretation when the evidence supports one — "
            "e.g. ratio between the returned values, density per unit, or a "
            "short plain-Uzbek explanation of what the numbers mean for the "
            "reader. Reason FROM the evidence, do not invent outside facts."
        ),
        allowed_insight_modes=(
            "direct_fact",
            "ratio_between_returned_values",
            "density_per_unit_using_returned_values",
            "average_per_mahalla_or_district_using_returned_values",
            "practical_interpretation",
            "short_meaning_or_significance",
            "period_note",
            "missing_data_note",
            "comparison_to_context_if_context_rows_exist",
        ),
        forbidden_insight_modes=(
            # Only the truly useless single-row artefacts. Anything else is
            # fair game when the evidence supports it.
            "100_percent_of_shown_result",
            "highest_and_lowest_are_the_same",
            "gap_is_zero",
            "ranking_against_rows_that_were_not_returned",
        ),
        style_rules=(
            "1-2 short paragraphs in Uzbek Latin.",
            "It is GOOD to add one practical interpretation: e.g. for "
            "1,070 mahallas + 53,382 active businesses, you may say "
            "\"o'rtacha har bir mahallaga taxminan 50 ta faol tadbirkorlik \"\n"
            "\"subyekti to'g'ri keladi\".",
            "Optional tiny markdown table only when there are several distinct facts.",
            "Skip the useless single-row artefacts (100% of shown, highest "
            "equals lowest, gap is 0).",
        ),
        reason="single direct fact requested (qancha/nechta/soni/ko'rsat) or row_count==1",
    )


def _top_n_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="top_n_ranking",
        user_goal=(
            "Surface the leader, list the top rows, and add ONE useful "
            "ranking insight when the evidence supports it."
        ),
        allowed_insight_modes=(
            "winner",
            "top_rows",
            "gap_first_to_second",
            "ratio_first_to_second",
            "share_of_total_if_context_has_total",
            "concentration_if_top_n_sum_available",
        ),
        forbidden_insight_modes=(
            "exact_lookup_wording",
            "overexplain_missing_values",
            "single_row_artefacts",
        ),
        style_rules=(
            "Mention the leader first.",
            "Then a compact list or table of the top rows.",
            "Then 1 useful insight (gap or share). Stop there.",
        ),
        reason="ranking keywords (eng ko'p / eng yuqori / top / leader)",
    )


def _comparison_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="comparison",
        user_goal=(
            "Compare the requested entities or metrics. State which is higher "
            "and by how much."
        ),
        allowed_insight_modes=(
            "difference",
            "ratio",
            "percent_difference",
            "winner_loser",
            "caveat_missing",
        ),
        forbidden_insight_modes=(
            "top_n_concentration",
            "single_row_artefacts",
        ),
        style_rules=(
            "Lead with the verdict (which side wins).",
            "Quote the absolute difference and the % difference.",
        ),
        reason="comparison keywords (taqqoslash / farq / vs / qaysi yuqoriroq)",
    )


def _distribution_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="distribution",
        user_goal=(
            "Describe the breakdown across categories. Identify the largest "
            "category and any obvious skew."
        ),
        allowed_insight_modes=(
            "category_counts",
            "largest_category",
            "share_if_total_available",
        ),
        forbidden_insight_modes=(
            "limit_1_style_answer",
            "single_row_conclusion",
        ),
        style_rules=(
            "Use a small table when there are >3 categories.",
            "Name the largest category and its share if a total is available.",
        ),
        reason="distribution keywords (har bir / taqsimot / bo'yicha nechta)",
    )


def _entity_profile_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="entity_profile",
        user_goal=(
            "Summarize the most important signals for ONE entity. Group "
            "related points; mention missing values; keep it focused."
        ),
        allowed_insight_modes=(
            "strongest_signals",
            "group_related_points",
            "missing_values_note",
            "peer_comparison_if_context_has_baseline",
        ),
        forbidden_insight_modes=(
            "ranking_against_unrelated_regions",
            "share_of_total_unless_context_has_total",
        ),
        style_rules=(
            "2-4 short paragraphs grouped by theme (infrastructure, social, "
            "economic, …) when applicable.",
        ),
        reason="entity-profile keywords (kuchli tomon / haqida / profile / overview)",
    )


def _data_quality_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="data_quality",
        user_goal=(
            "Report data-quality issue counts and which codes/entities are "
            "affected. Explain the impact, not a fix."
        ),
        allowed_insight_modes=(
            "issue_counts",
            "affected_codes",
            "explain_impact",
        ),
        forbidden_insight_modes=(
            "claim_issues_fixed",
            "deduping_language",
            "source_repair_language",
        ),
        style_rules=(
            "Be neutral. Do not promise a fix.",
            "Cite issue counts exactly as in the rows.",
        ),
        reason="data-quality keywords (takror / duplicate / mismatch / sifat muammo)",
    )


def _generic_brief() -> AnswerBrief:
    return AnswerBrief(
        answer_type="generic_analytical",
        user_goal="Answer the question directly, then add one useful insight.",
        allowed_insight_modes=(
            "direct_answer",
            "one_useful_insight_from_evidence",
        ),
        forbidden_insight_modes=(
            "irrelevant_template_insights",
            "single_row_artefacts",
        ),
        style_rules=(
            "Be concrete. 2-3 short paragraphs.",
            "Skip insights that do not actually add information.",
        ),
        reason="no specialised archetype matched",
    )


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


def build_answer_brief(
    question: str,
    primary_result: Any,
    context_results: tuple[Any, ...] = (),
) -> AnswerBrief:
    """Pick the right archetype for `question` given the primary result.

    Order of precedence:
      1. no_rows         (row_count == 0)
      2. data_quality    (keywords match)
      3. entity_profile  (keywords match)
      4. distribution    (keywords match)
      5. comparison      (keywords match AND row_count >= 2)
      6. top_n_ranking   (keywords match AND row_count >= 2)
      7. exact_lookup    (lookup keywords OR row_count == 1, and few rows)
      8. generic_analytical (fallback)
    """
    text = (question or "").strip()

    row_count = int(getattr(primary_result, "row_count", 0) or 0)
    if row_count == 0:
        return _no_rows_brief(text)

    if _DATA_QUALITY_PAT.search(text):
        return _data_quality_brief()
    if _ENTITY_PROFILE_PAT.search(text):
        return _entity_profile_brief()
    if _DISTRIBUTION_PAT.search(text):
        return _distribution_brief()
    if _COMPARISON_PAT.search(text) and row_count >= 2:
        return _comparison_brief()
    if _TOP_N_PAT.search(text) and row_count >= 2:
        return _top_n_brief()

    is_lookup_phrasing = bool(_EXACT_LOOKUP_PAT.search(text))
    if row_count == 1 or (is_lookup_phrasing and row_count <= 3):
        return _exact_lookup_brief()

    return _generic_brief()


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------


def render_brief_for_prompt(brief: AnswerBrief) -> str:
    allowed = ", ".join(brief.allowed_insight_modes) or "(none)"
    forbidden = ", ".join(brief.forbidden_insight_modes) or "(none)"
    style = "\n".join(f"  * {rule}" for rule in brief.style_rules) or "  * (none)"
    return (
        f"answer_type: {brief.answer_type}\n"
        f"user_goal: {brief.user_goal}\n"
        f"allowed_insight_modes: {allowed}\n"
        f"forbidden_insight_modes: {forbidden}\n"
        "style_rules:\n"
        f"{style}\n"
        f"reason: {brief.reason}"
    )


__all__ = [
    "AnswerBrief",
    "AnswerType",
    "build_answer_brief",
    "render_brief_for_prompt",
]
