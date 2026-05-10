"""Industry benchmarks for SME credit-scoring v2.

Maps free-form `organization.mainActivity` text (RU/UZ-Latin) to a
canonical category, and exposes the benchmark numbers used by
`credit_scoring.compute_wizard_score_v2` and `plausibility_checks`.

Caveats:
  • Numbers are seed values for the platform's self-diagnostic tool —
    not bank underwriting figures. Validate against CBU / State
    Statistics Committee data once we have a survey set.
  • Classification is regex-based (word-boundary aware). Falls back
    to "default" if no category matches.
"""
from __future__ import annotations

import re
from typing import Any, NamedTuple


class IndustryBenchmark(NamedTuple):
    category: str
    label_ru: str
    label_uz: str
    # Median EBITDA margin (%) for this industry — used by criterion 3
    # (Прибыльность: EBITDA margin vs. industry median).
    ebitda_margin_median: float
    # Plausible monthly revenue per employee (UZS), low-high range —
    # used by plausibility check #1.
    rev_per_employee: tuple[int, int]
    # Plausible monthly salary range per role (UZS) — used by
    # plausibility check #4 (salary outliers). One value covers all
    # roles; we don't try to distinguish CEO from cashier here.
    salary_range: tuple[int, int]

    def label(self, lang: str | None = None) -> str:
        """Return the language-appropriate label.
        Defaults to Russian; falls back to Russian if Uzbek missing."""
        if (lang or "ru").lower() == "uz" and self.label_uz:
            return self.label_uz
        return self.label_ru


# ---------- Classification patterns ----------
# Keys must match `_BENCHMARKS` below.
# Patterns match case-insensitively. We anchor on word START only (`\b`) and
# omit trailing word-boundary so Russian/Uzbek inflections match: "пекарн"
# catches "пекарня", "пекарни", "пекарнями"; "non" anchored on `\b` won't
# match "ножницы" (different start), but DOES match "Non mahsulotlari".
_PATTERNS: dict[str, re.Pattern] = {
    # Bakery — must come before retail_food and manufacturing so that
    # "Производство хлеба" classifies as bakery, not manufacturing.
    "bakery": re.compile(
        r"\b(?:пекарн|хлеб|хлебобулоч|кондитер|выпечк|"
        r"non(?:voy|vo[yi]chilik)?|nonchi|"
        r"qandolat|shirinlik|bulochka|piroj|tort)",
        re.IGNORECASE,
    ),
    "retail_food": re.compile(
        r"\b(?:магазин|продукт|розниц|супермаркет|маркет|торговл|"
        r"do['ʻ`]?kon|savdo|oziq[- ]ovqat|supermarket|chakana)",
        re.IGNORECASE,
    ),
    "manufacturing": re.compile(
        r"\b(?:произв[оо]д|изготовлен|фабрик|завод|переработк|"
        r"ishlab[ -]?chiq|fabrika|zavod|qayta[ -]?ishl)",
        re.IGNORECASE,
    ),
    "services": re.compile(
        r"\b(?:услуг|сервис|консалтинг|ремонт|салон|парикмахер|"
        r"xizmat|servis|ta['ʻ`]?mir|sartarosh)",
        re.IGNORECASE,
    ),
    "construction": re.compile(
        r"\b(?:строительств|строит|стройк|подрядчик|"
        r"qurilish|qurish|pudratchi)",
        re.IGNORECASE,
    ),
    "agriculture": re.compile(
        r"\b(?:сельск|фермер|агро|животновод|растениевод|"
        r"qishloq[ -]?xo|fermer|agro|chorvachilik|dehqonchilik)",
        re.IGNORECASE,
    ),
    "transport": re.compile(
        r"\b(?:транспорт|перевозк|логистик|такси|грузопер|"
        r"yuk[ -]?tash|tashish|logistika|taksi)",
        re.IGNORECASE,
    ),
}


_BENCHMARKS: dict[str, IndustryBenchmark] = {
    "bakery": IndustryBenchmark(
        category="bakery",
        label_ru="Хлебопечение / кондитерское",
        label_uz="Non / qandolat",
        ebitda_margin_median=10.0,
        rev_per_employee=(8_000_000, 15_000_000),
        salary_range=(2_500_000, 8_000_000),
    ),
    "retail_food": IndustryBenchmark(
        category="retail_food",
        label_ru="Розничная торговля продуктами",
        label_uz="Oziq-ovqat chakana savdo",
        ebitda_margin_median=6.0,
        rev_per_employee=(10_000_000, 25_000_000),
        salary_range=(2_500_000, 7_000_000),
    ),
    "manufacturing": IndustryBenchmark(
        category="manufacturing",
        label_ru="Производство",
        label_uz="Ishlab chiqarish",
        ebitda_margin_median=12.0,
        rev_per_employee=(12_000_000, 30_000_000),
        salary_range=(3_000_000, 9_000_000),
    ),
    "services": IndustryBenchmark(
        category="services",
        label_ru="Услуги",
        label_uz="Xizmatlar",
        ebitda_margin_median=18.0,
        rev_per_employee=(5_000_000, 20_000_000),
        salary_range=(2_500_000, 10_000_000),
    ),
    "construction": IndustryBenchmark(
        category="construction",
        label_ru="Строительство",
        label_uz="Qurilish",
        ebitda_margin_median=8.0,
        rev_per_employee=(15_000_000, 40_000_000),
        salary_range=(3_500_000, 12_000_000),
    ),
    "agriculture": IndustryBenchmark(
        category="agriculture",
        label_ru="Сельское хозяйство",
        label_uz="Qishloq xoʻjaligi",
        ebitda_margin_median=10.0,
        rev_per_employee=(6_000_000, 18_000_000),
        salary_range=(2_000_000, 6_000_000),
    ),
    "transport": IndustryBenchmark(
        category="transport",
        label_ru="Транспорт и логистика",
        label_uz="Transport va logistika",
        ebitda_margin_median=9.0,
        rev_per_employee=(10_000_000, 30_000_000),
        salary_range=(3_000_000, 9_000_000),
    ),
    "default": IndustryBenchmark(
        category="default",
        label_ru="Прочее (общая категория)",
        label_uz="Boshqa (umumiy kategoriya)",
        ebitda_margin_median=12.0,
        rev_per_employee=(5_000_000, 20_000_000),
        salary_range=(2_500_000, 10_000_000),
    ),
}


def classify(
    activity_text: str | None,
    category_hint: str | None = None,
) -> IndustryBenchmark:
    """Classify a free-form activity description into a benchmark category.

    If `category_hint` is a known category name (from the wizard dropdown),
    it wins — deterministic input is always preferred over regex guessing.
    Otherwise we match patterns against `activity_text`, falling back to
    "default" if nothing matches. Matching is greedy in declaration order
    — declare more specific categories first if you add new ones.
    """
    if category_hint and category_hint in _BENCHMARKS:
        return _BENCHMARKS[category_hint]
    if not activity_text:
        return _BENCHMARKS["default"]
    for category, pattern in _PATTERNS.items():
        if pattern.search(activity_text):
            return _BENCHMARKS[category]
    return _BENCHMARKS["default"]


# Public catalog so the frontend dropdown can render the same labels we
# use server-side. Returned in a stable order.
def list_categories() -> list[dict[str, str]]:
    """Return [{category, label_ru}, ...] for every concrete category, in
    a stable display order. Excludes 'default' (it's the fallback, not a
    user choice)."""
    order = [
        "bakery", "retail_food", "manufacturing", "services",
        "construction", "agriculture", "transport",
    ]
    return [
        {"category": c, "label_ru": _BENCHMARKS[c].label_ru}
        for c in order if c in _BENCHMARKS
    ]


def get_benchmark(category: str) -> IndustryBenchmark:
    """Look up a benchmark by category name. Falls back to default."""
    return _BENCHMARKS.get(category, _BENCHMARKS["default"])
