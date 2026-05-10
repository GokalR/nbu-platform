"""Natural-language alias resolution.

Users phrase questions in Uzbek/Russian/English without ever typing
column names. The resolver must still pick the right view/column.
"""

from __future__ import annotations

import pytest

from cerr_chatbot.query.metric_resolver import resolve


@pytest.mark.parametrize(
    "question,expected_view,expected_col",
    [
        ("Qaysi viloyatda aholi eng ko'p?", "v_regions", "population"),
        ("Korxonalar soni eng yuqori 5 viloyat", "v_regions", "active_businesses"),
        (
            "Qaysi mahallalarda yo'l infratuzilmasi katta",
            "v_mahalla_infrastructure",
            "road_total_km",
        ),
        ("Asfalt yo'l hajmi bo'yicha top 10", "v_mahalla_infrastructure", "road_asphalt_km"),
        (
            "Tibbiyot muassasasigacha masofa eng uzoq",
            "v_mahalla_infrastructure",
            "medical_facility_distance_km",
        ),
        ("Jinoyat murojaatlari ko'p mahallalar", "v_mahalla_appeals", "crime_appeal_count"),
        ("Ajrim arizalari eng ko'p", "v_mahalla_appeals", "divorce_appeal_count"),
        (
            "Sanoat hajmi eng yuqori tumanlar",
            "v_district_macro_highlights",
            "industry_volume_bln_uzs",
        ),
        ("Eksport hajmi katta tumanlar", "v_district_macro_highlights", "export_volume_mln_usd"),
        ("Reyting eng past mahallalar", "v_mahallas", "rating_score"),
    ],
)
def test_alias_resolves_to_expected_view_and_column(
    question: str, expected_view: str, expected_col: str
) -> None:
    hint = resolve(question)
    assert expected_view in hint.forced_views, (question, hint)
    assert expected_col in hint.forced_columns, (question, hint)


def test_subsidy_alias_routes_to_subsidy_view() -> None:
    hint = resolve("Subsidiya arizalari bo'yicha qaysi dasturlar faol?")
    assert "v_mahalla_subsidy_programs" in hint.forced_views
    assert "application_count" in hint.forced_columns


def test_specialization_alias_routes_to_specialization_view() -> None:
    hint = resolve("Mahallalar nimaga ixtisoslashgan?")
    assert "v_mahalla_specializations" in hint.forced_views


def test_takror_stir_alias_routes_to_data_quality_issue() -> None:
    hint = resolve("Ma'lumotlarda takror STIR bormi?")
    assert "v_data_quality_issues" in hint.forced_views
    assert "MAHALLA_STIR_DUPLICATE" in hint.issue_codes


def test_alias_does_not_force_column_when_unrelated_question() -> None:
    hint = resolve("Bugun nima yangiliklar?")
    assert hint.forced_views == ()
    assert hint.forced_columns == ()
