"""Uzbek Cyrillic → Uzbek Latin transliteration."""

from __future__ import annotations

import pytest

from cerr_chatbot.query.transliterate import uz_cyrillic_to_latin

# ---------- region / district / mahalla names ----------


@pytest.mark.parametrize(
    "cyr,latin",
    [
        ("Қашқадарё", "Qashqadaryo"),
        ("Сурхондарё", "Surxondaryo"),
        ("Самарқанд", "Samarqand"),
        ("Навоий", "Navoiy"),
        ("Тошкент шаҳри", "Toshkent shahri"),
        ("Андижон вилояти", "Andijon viloyati"),
        ("Фарғона вилояти", "Farg'ona viloyati"),
        ("Жиззах", "Jizzax"),
        ("Хоразм", "Xorazm"),
    ],
)
def test_region_names_transliterate(cyr: str, latin: str) -> None:
    assert uz_cyrillic_to_latin(cyr) == latin


def test_marg_ilon_and_yoyilma() -> None:
    assert uz_cyrillic_to_latin("Марғилон шаҳри") == "Marg'ilon shahri"
    assert uz_cyrillic_to_latin("Ёйилма") == "Yoyilma"
    assert uz_cyrillic_to_latin("Ёйилма маҳалласи") == "Yoyilma mahallasi"


# ---------- preserved content ----------


def test_markdown_table_pipes_preserved() -> None:
    cyr = (
        "| Hudud | Aholi |\n"
        "|---|---|\n"
        "| Самарқанд вилояти | 4,330,143 |\n"
        "| Фарғона вилояти | 4,204,055 |"
    )
    latin = uz_cyrillic_to_latin(cyr)
    assert "| Samarqand viloyati | 4,330,143 |" in latin
    assert "| Farg'ona viloyati | 4,204,055 |" in latin
    # Header row, separator, and pipe count unchanged.
    assert latin.startswith("| Hudud | Aholi |")
    assert "|---|---|" in latin


def test_numbers_unchanged() -> None:
    src = "Самарқандда 4,330,143 kishi yashaydi, ulushi 23.05%."
    out = uz_cyrillic_to_latin(src)
    assert "4,330,143" in out
    assert "23.05%" in out


def test_existing_latin_unchanged() -> None:
    src = "Andijon viloyatida aholi soni 1,234,567 kishi (top-3)."
    assert uz_cyrillic_to_latin(src) == src


def test_empty_and_none_safe() -> None:
    assert uz_cyrillic_to_latin("") == ""
    assert uz_cyrillic_to_latin("   ") == "   "


# ---------- letter-by-letter coverage ----------


@pytest.mark.parametrize(
    "cyr,latin",
    [
        ("Ғ", "G'"), ("ғ", "g'"),
        ("Ў", "O'"), ("ў", "o'"),
        ("Қ", "Q"), ("қ", "q"),
        ("Ҳ", "H"), ("ҳ", "h"),
        ("Ё", "Yo"), ("ё", "yo"),
        ("Ю", "Yu"), ("ю", "yu"),
        ("Я", "Ya"), ("я", "ya"),
        ("Ш", "Sh"), ("ш", "sh"),
        ("Ч", "Ch"), ("ч", "ch"),
        ("Ц", "Ts"), ("ц", "ts"),
        ("Й", "Y"), ("й", "y"),
        ("Ы", "I"), ("ы", "i"),
        ("Э", "E"), ("э", "e"),
        ("Ъ", "'"), ("ъ", "'"),
    ],
)
def test_letter_mapping(cyr: str, latin: str) -> None:
    assert uz_cyrillic_to_latin(cyr) == latin


def test_e_word_start_becomes_ye() -> None:
    # Word-start: Ye/ye.
    assert uz_cyrillic_to_latin("Европа") == "Yevropa"
    assert uz_cyrillic_to_latin("Елена") == "Yelena"


def test_e_after_consonant_stays_e() -> None:
    # After a consonant: plain E/e (Eshmat, not Yeshmat).
    assert uz_cyrillic_to_latin("Эшмат") == "Eshmat"
    assert uz_cyrillic_to_latin("берди") == "berdi"


# ---------- idempotence ----------


def test_idempotent_on_already_latin() -> None:
    s = "Samarqand viloyati va Farg'ona viloyati"
    assert uz_cyrillic_to_latin(uz_cyrillic_to_latin(s)) == s
