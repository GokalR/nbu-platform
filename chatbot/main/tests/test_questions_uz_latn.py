"""Verify questions_uz_latn.md mirrors questions.md structure + numbers."""

from __future__ import annotations

import re
from pathlib import Path

UZ_PATH = Path("questions_uz_latn.md")
RU_PATH = Path("questions.md")


def _sections(text: str) -> list[str]:
    """Split body on `## N. ...` headers; return one chunk per section (excluding preamble)."""
    parts = re.split(r"^##\s+\d+\.\s.*$", text, flags=re.MULTILINE)
    return parts[1:]  # drop preamble


def _question_blocks(text: str) -> list[str]:
    return re.findall(r"\*\*Question:\*\*", text)


def _answer_blocks(text: str) -> list[str]:
    return re.findall(r"\*\*Expected answer:\*\*", text)


def _numeric_tokens(text: str) -> set[str]:
    return set(re.findall(r"-?\d+(?:\.\d+)?", text))


def test_file_exists() -> None:
    assert UZ_PATH.exists(), "questions_uz_latn.md is missing"


def test_has_thirty_questions_and_thirty_answers() -> None:
    text = UZ_PATH.read_text(encoding="utf-8")
    assert len(_question_blocks(text)) == 30
    assert len(_answer_blocks(text)) == 30


def test_no_brand_acronym_in_uz_latn_file() -> None:
    text = UZ_PATH.read_text(encoding="utf-8")
    assert not re.search(r"\bCERR\b", text), "external source brand must not appear"


def test_numeric_tokens_match_source_file() -> None:
    """Every number from the original answers must survive in the uz_latn copy."""
    ru_text = RU_PATH.read_text(encoding="utf-8")
    uz_text = UZ_PATH.read_text(encoding="utf-8")

    ru_answer_text = "\n".join(
        re.findall(r"\*\*Expected answer:\*\*.*?(?=\n## |\Z)", ru_text, flags=re.DOTALL)
    )
    uz_answer_text = "\n".join(
        re.findall(r"\*\*Expected answer:\*\*.*?(?=\n## |\Z)", uz_text, flags=re.DOTALL)
    )
    ru_nums = _numeric_tokens(ru_answer_text)
    uz_nums = _numeric_tokens(uz_answer_text)
    missing = ru_nums - uz_nums
    assert not missing, f"numeric tokens missing in uz_latn copy: {sorted(missing)[:10]}"


def test_source_entity_names_unchanged() -> None:
    """A sample of Cyrillic source names from questions.md must appear verbatim."""
    uz_text = UZ_PATH.read_text(encoding="utf-8")
    must_appear = (
        "Андижон вилояти",
        "Тошкент шаҳри",
        "Қашқадарё вилояти",
        "Самарқанд вилояти",
        "Фарғона вилояти",
        "Қорақалпоғистон Республикаси",
        "Бекобод шаҳри",
        "Мирзо Улуғбек тумани",
        "Подшобоғ",
        "Қоструба МФЙ",
        "3 паст",
        "2 ўрта",
        "1 юқори",
        "Оғир маҳалла",
        "Қишлоқ хўжалиги ҳажми (млрд. сўм)",
        "MAHALLA_STIR_DUPLICATE",
        "DISTRICT_CODE_DUPLICATE_GLOBAL",
        "industry_volume_bln_uzs",
        "crop_total_homestead_area_sotkah",
        "road_total_km",
    )
    missing = [name for name in must_appear if name not in uz_text]
    assert not missing, f"source entity names missing/transliterated: {missing}"


def test_known_section_titles_are_uz_latn() -> None:
    """A handful of titles must be Uzbek Latin, not the original Russian/English."""
    uz_text = UZ_PATH.read_text(encoding="utf-8")
    assert "## 1. Import qilingan obyektlar soni" in uz_text
    assert "## 16. road_total_km 1000 dan yuqori bo'lgan mahallalar" in uz_text
    # And the Russian first prose word must not survive in uz_latn.
    assert "Сколько" not in uz_text
    assert "Какие" not in uz_text


def test_uz_latn_specific_words_present_in_questions() -> None:
    uz_text = UZ_PATH.read_text(encoding="utf-8")
    uz_words = ("viloyat", "tuman", "mahalla", "qaysi", "nechta", "ko'rsat")
    for w in uz_words:
        assert w in uz_text.lower(), f"missing Uzbek Latin keyword: {w}"
