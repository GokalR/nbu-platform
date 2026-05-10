"""Answer-style scorer."""

from __future__ import annotations

from cerr_chatbot.eval.style import style_issues


def test_pure_table_answer_flags_no_explanation() -> None:
    text = (
        "Qaytarilgan qatorlar: 2.\n\n"
        "| region_name_cyr | population |\n"
        "|---|---|\n"
        "| Andijon | 1234 |\n"
        "| Fargona | 5678 |"
    )
    issues = style_issues(text, service_kind="sql_result")
    assert any("explanatory sentence" in i for i in issues)


def test_answer_with_prose_passes() -> None:
    text = (
        "Andijon viloyatida aholi soni 1234, Fargona viloyatida 5678. "
        "Eng yuqori ko'rsatkich Fargona'da.\n\n"
        "| region_name_cyr | population |\n"
        "|---|---|\n"
        "| Andijon | 1234 |\n"
        "| Fargona | 5678 |"
    )
    assert style_issues(text, service_kind="sql_result") == []


def test_internal_terms_flagged() -> None:
    text = "Natija sql_guard tomonidan tasdiqlandi. Aholi 1234 ta."
    issues = style_issues(text, service_kind="sql_result")
    assert any("sql_guard" in i for i in issues)


def test_greeting_with_table_is_flagged() -> None:
    text = "Assalomu alaykum.\n\n| col | val |\n|---|---|\n| x | 1 |"
    issues = style_issues(text, service_kind="greeting")
    assert any("markdown table" in i for i in issues)


def test_no_latin_in_uzbek_answer_flagged() -> None:
    issues = style_issues("Тошкент 1234", service_kind="sql_result")
    assert any("Latin" in i for i in issues)


def test_missing_value_marker_counts_as_explanation() -> None:
    text = "Andijon: ma'lumot yo'q"
    assert style_issues(text, service_kind="sql_result") == []
