"""Tagged SQL example bank for prompt example selection.

Each `PromptExample` carries:
- the SQL string (must pass sql_guard at module import time, asserted by tests)
- views it touches
- semantic tags (top_n, distribution, missing_null, ...)
- keywords used for question-similarity matching

The selector picks the top-K most relevant examples by combining schema
overlap, tag overlap, and keyword hits.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Tag vocabulary. Keep small; prompt size matters.
TAG_DUPLICATE = "duplicate"
TAG_DATA_QUALITY = "data_quality"
TAG_TOP_N = "top_n"
TAG_GROUP_BY_REGION = "group_by_region"
TAG_GROUP_BY_DISTRICT = "group_by_district"
TAG_MISSING_NULL = "missing_null"
TAG_MACRO_INDICATOR = "macro_indicator"
TAG_PEER_FACTOR = "peer_factor"
TAG_SPECIALIZATION = "specialization"
TAG_SUBSIDY = "subsidy"
TAG_INFRASTRUCTURE = "infrastructure"
TAG_APPEALS = "appeals"
TAG_RATING = "rating"
TAG_CROPS = "crops"
TAG_DISTRIBUTION = "distribution"
TAG_SCALAR_COUNT = "scalar_count"
TAG_SAMPLE = "sample"
# Phase 2A — business directory tags
TAG_BUSINESS_COMPANY = "business_company"
TAG_BUSINESS_IMPORT = "business_import"
TAG_BUSINESS_TNVED = "business_tnved"
# Phase 2B — advisory mode
TAG_ADVISORY = "advisory"


@dataclass(frozen=True)
class PromptExample:
    title: str
    sql: str
    views: tuple[str, ...]
    tags: tuple[str, ...]
    keywords: tuple[str, ...] = field(default_factory=tuple)


EXAMPLES: tuple[PromptExample, ...] = (
    PromptExample(
        title="count imported entity rows",
        sql=(
            "SELECT (SELECT COUNT(*) FROM v_regions) AS region_count, "
            "(SELECT COUNT(*) FROM v_districts) AS district_count, "
            "(SELECT COUNT(*) FROM v_mahallas) AS mahalla_count"
        ),
        views=("v_regions", "v_districts", "v_mahallas"),
        tags=(TAG_SCALAR_COUNT,),
        keywords=("nechta", "soni", "import", "obyekt", "viloyat", "tuman", "mahalla"),
    ),
    PromptExample(
        title="regions with declared vs actual mahalla mismatch",
        sql=(
            "SELECT region_code, region_name_cyr, declared_mahalla_count, "
            "actual_mahalla_count FROM v_regions "
            "WHERE mahalla_count_mismatch_flag = 1 ORDER BY region_code LIMIT 100"
        ),
        views=("v_regions",),
        tags=(TAG_DATA_QUALITY,),
        keywords=("mos kelmaydi", "mismatch", "deklaratsiya", "declared", "actual"),
    ),
    PromptExample(
        title="top regions by population",
        sql=("SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5"),
        views=("v_regions",),
        tags=(TAG_TOP_N,),
        keywords=("aholi", "population", "viloyat", "eng yuqori", "top"),
    ),
    PromptExample(
        title="top regions by active businesses",
        sql=(
            "SELECT region_name_cyr, active_businesses FROM v_regions "
            "ORDER BY active_businesses DESC LIMIT 5"
        ),
        views=("v_regions",),
        tags=(TAG_TOP_N,),
        keywords=("active_businesses", "biznes", "eng yuqori", "yetakchi", "top"),
    ),
    PromptExample(
        title="duplicate district codes from data quality issues",
        sql=(
            "SELECT issue_code, district_code, message FROM v_data_quality_issues "
            "WHERE issue_code = 'DISTRICT_CODE_DUPLICATE_GLOBAL' "
            "ORDER BY district_code LIMIT 100"
        ),
        views=("v_data_quality_issues",),
        tags=(TAG_DUPLICATE, TAG_DATA_QUALITY),
        keywords=("takror", "duplicate", "district_code"),
    ),
    PromptExample(
        title="duplicate mahalla STIR count",
        sql=(
            "SELECT COUNT(*) AS duplicate_stir_groups FROM v_data_quality_issues "
            "WHERE issue_code = 'MAHALLA_STIR_DUPLICATE'"
        ),
        views=("v_data_quality_issues",),
        tags=(TAG_DUPLICATE, TAG_DATA_QUALITY, TAG_SCALAR_COUNT),
        keywords=("takror", "duplicate", "stir", "nechta"),
    ),
    PromptExample(
        title="sample duplicate STIR rows with deterministic order",
        sql=(
            "SELECT mahalla_stir, message FROM v_data_quality_issues "
            "WHERE issue_code = 'MAHALLA_STIR_DUPLICATE' "
            "ORDER BY mahalla_stir LIMIT 5"
        ),
        views=("v_data_quality_issues",),
        tags=(TAG_DUPLICATE, TAG_DATA_QUALITY, TAG_SAMPLE),
        keywords=("namuna", "example", "stir", "5 ta"),
    ),
    PromptExample(
        title="top mahallas by population",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, population "
            "FROM v_mahallas ORDER BY population DESC LIMIT 10"
        ),
        views=("v_mahallas",),
        tags=(TAG_TOP_N,),
        keywords=("mahalla", "aholi", "population", "eng yuqori", "top"),
    ),
    PromptExample(
        title="lowest mahalla rating score",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, rating_score "
            "FROM v_mahallas ORDER BY rating_score ASC LIMIT 10"
        ),
        views=("v_mahallas",),
        tags=(TAG_TOP_N, TAG_RATING),
        keywords=("rating_score", "rating", "eng past", "lowest"),
    ),
    PromptExample(
        title="mahalla category distribution",
        sql=(
            "SELECT category_label_cyr, COUNT(*) AS mahalla_count FROM v_mahallas "
            "GROUP BY category_label_cyr ORDER BY mahalla_count DESC LIMIT 100"
        ),
        views=("v_mahallas",),
        tags=(TAG_DISTRIBUTION,),
        keywords=("kategoriya", "category", "har bir", "distribution"),
    ),
    PromptExample(
        title="mahalla status distribution",
        sql=(
            "SELECT status_label_cyr, COUNT(*) AS mahalla_count FROM v_mahallas "
            "WHERE status_label_cyr IS NOT NULL GROUP BY status_label_cyr "
            "ORDER BY mahalla_count DESC LIMIT 100"
        ),
        views=("v_mahallas",),
        tags=(TAG_DISTRIBUTION,),
        keywords=("status", "holat", "og'ir mahalla"),
    ),
    PromptExample(
        title="macro indicators with most missing highlighted values + total districts",
        sql=(
            "SELECT h.indicator_key, h.indicator_label_cyr, COUNT(*) AS missing_count, "
            "(SELECT COUNT(*) FROM v_districts) AS total_districts "
            "FROM v_district_macro_highlights h "
            "WHERE h.highlighted_missing_flag = 1 "
            "GROUP BY h.indicator_key, h.indicator_label_cyr "
            "ORDER BY missing_count DESC LIMIT 10"
        ),
        views=("v_district_macro_highlights", "v_districts"),
        tags=(TAG_MACRO_INDICATOR, TAG_MISSING_NULL),
        keywords=("highlighted", "missing", "macro", "indikator", "yo'q"),
    ),
    PromptExample(
        title="top districts by industry_volume_bln_uzs (macro indicator key)",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, highlighted_value_num "
            "AS industry_volume_bln_uzs "
            "FROM v_district_macro_highlights "
            "WHERE indicator_key = 'industry_volume_bln_uzs' "
            "AND highlighted_value_num IS NOT NULL "
            "ORDER BY highlighted_value_num DESC LIMIT 10"
        ),
        views=("v_district_macro_highlights",),
        tags=(TAG_MACRO_INDICATOR, TAG_TOP_N),
        keywords=("industry_volume", "saneot", "tuman", "shahar"),
    ),
    PromptExample(
        title="top districts by export_volume_mln_usd (macro indicator key)",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, highlighted_value_num "
            "AS export_volume_mln_usd "
            "FROM v_district_macro_highlights "
            "WHERE indicator_key = 'export_volume_mln_usd' "
            "AND highlighted_value_num IS NOT NULL "
            "ORDER BY highlighted_value_num DESC LIMIT 10"
        ),
        views=("v_district_macro_highlights",),
        tags=(TAG_MACRO_INDICATOR, TAG_TOP_N),
        keywords=("export_volume", "eksport", "tuman"),
    ),
    PromptExample(
        title="extreme road length with both total and asphalt km",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, "
            "road_total_km, road_asphalt_km FROM v_mahalla_infrastructure "
            "WHERE road_total_km IS NOT NULL "
            "ORDER BY road_total_km DESC LIMIT 10"
        ),
        views=("v_mahalla_infrastructure",),
        tags=(TAG_INFRASTRUCTURE, TAG_TOP_N),
        keywords=("road", "yo'l", "asphalt", "km"),
    ),
    PromptExample(
        title="medical facility distance extremes",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, "
            "medical_facility_distance_km FROM v_mahalla_infrastructure "
            "WHERE medical_facility_distance_km IS NOT NULL "
            "ORDER BY medical_facility_distance_km DESC LIMIT 10"
        ),
        views=("v_mahalla_infrastructure",),
        tags=(TAG_INFRASTRUCTURE, TAG_TOP_N),
        keywords=("medical", "tibbiyot", "masofa", "km"),
    ),
    PromptExample(
        title="crime appeals grouped by region only",
        sql=(
            "SELECT region_name_cyr, "
            "SUM(crime_appeal_count) AS crime_appeal_count_sum "
            "FROM v_mahalla_appeals "
            "GROUP BY region_name_cyr "
            "ORDER BY crime_appeal_count_sum DESC LIMIT 10"
        ),
        views=("v_mahalla_appeals",),
        tags=(TAG_APPEALS, TAG_GROUP_BY_REGION),
        keywords=("crime", "jinoyat", "viloyat", "murojaat", "appeals"),
    ),
    PromptExample(
        title="top mahallas by employment appeal count",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, "
            "employment_appeal_count FROM v_mahalla_appeals "
            "WHERE employment_appeal_count IS NOT NULL "
            "ORDER BY employment_appeal_count DESC LIMIT 10"
        ),
        views=("v_mahalla_appeals",),
        tags=(TAG_APPEALS, TAG_TOP_N),
        keywords=("employment", "bandlik", "murojaat", "mahalla"),
    ),
    PromptExample(
        title="missing divorce appeal rows by region",
        sql=(
            "SELECT region_name_cyr, COUNT(*) AS total_mahallas, "
            "COUNT(*) - COUNT(divorce_appeal_count) AS missing_divorce_rows "
            "FROM v_mahalla_appeals GROUP BY region_name_cyr "
            "ORDER BY missing_divorce_rows DESC LIMIT 100"
        ),
        views=("v_mahalla_appeals",),
        tags=(TAG_APPEALS, TAG_MISSING_NULL, TAG_GROUP_BY_REGION),
        keywords=("divorce", "ajrim", "missing", "yo'q"),
    ),
    PromptExample(
        title="specialization type counts and population sums (full distribution)",
        sql=(
            "SELECT specialization_type_cyr, COUNT(*) AS rows, "
            "SUM(population_count) AS population_count_sum "
            "FROM v_mahalla_specializations "
            "GROUP BY specialization_type_cyr ORDER BY rows DESC LIMIT 100"
        ),
        views=("v_mahalla_specializations",),
        tags=(TAG_SPECIALIZATION, TAG_DISTRIBUTION),
        keywords=("ixtisoslashuv", "specialization", "type", "tur"),
    ),
    PromptExample(
        title="top specialization directions by population (top 10)",
        sql=(
            "SELECT specialization_direction_cyr, COUNT(*) AS rows, "
            "SUM(population_count) AS population_count_sum "
            "FROM v_mahalla_specializations "
            "GROUP BY specialization_direction_cyr "
            "ORDER BY population_count_sum DESC LIMIT 10"
        ),
        views=("v_mahalla_specializations",),
        tags=(TAG_SPECIALIZATION, TAG_TOP_N),
        keywords=("yo'nalish", "direction", "population"),
    ),
    PromptExample(
        title="crop rows missing total area + negative homestead area",
        sql=(
            "SELECT COUNT(*) AS crop_rows, "
            "COUNT(*) - COUNT(c.total_area_ha) AS missing_total_area_rows, "
            "(SELECT COUNT(*) FROM v_mahalla_crops c2 "
            "WHERE c2.homestead_area_ha < 0) AS negative_homestead_area_count, "
            "MIN(c.homestead_area_ha) AS min_homestead_area_ha "
            "FROM v_mahalla_crops c"
        ),
        views=("v_mahalla_crops",),
        tags=(TAG_CROPS, TAG_MISSING_NULL),
        keywords=("ekin", "crop", "manfiy", "negative", "missing", "yo'q"),
    ),
    PromptExample(
        title="top mahallas by crop_total_homestead_area_sotkah",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, mahalla_name_cyr, "
            "crop_total_homestead_area_sotkah FROM v_mahallas "
            "WHERE crop_total_homestead_area_sotkah IS NOT NULL "
            "ORDER BY crop_total_homestead_area_sotkah DESC LIMIT 10"
        ),
        views=("v_mahallas",),
        tags=(TAG_CROPS, TAG_TOP_N),
        keywords=("sotkah", "tomorqa", "homestead"),
    ),
    PromptExample(
        title="subsidy programs sums + null application rows",
        sql=(
            "SELECT subsidy_program_label_cyr, COUNT(*) AS rows, "
            "SUM(application_count) AS application_count_sum, "
            "COUNT(*) - COUNT(application_count) AS null_application_rows "
            "FROM v_mahalla_subsidy_programs "
            "GROUP BY subsidy_program_label_cyr "
            "ORDER BY application_count_sum DESC LIMIT 100"
        ),
        views=("v_mahalla_subsidy_programs",),
        tags=(TAG_SUBSIDY, TAG_DISTRIBUTION, TAG_MISSING_NULL),
        keywords=("subsidiya", "subsidy", "ariza", "application"),
    ),
    PromptExample(
        title="missing subsidy required amount rows",
        sql=(
            "SELECT COUNT(*) AS total_rows, "
            "COUNT(*) - COUNT(required_amount_mln_uzs) AS missing_required_amount_rows "
            "FROM v_mahalla_subsidy_programs"
        ),
        views=("v_mahalla_subsidy_programs",),
        tags=(TAG_SUBSIDY, TAG_MISSING_NULL),
        keywords=("required_amount", "subsidiya", "missing", "yo'q"),
    ),
    PromptExample(
        title="most frequent peer strength factor keys",
        sql=(
            "SELECT factor_key, factor_label_cyr, COUNT(*) AS row_count "
            "FROM v_mahalla_peer_factors WHERE factor_polarity = 'strength' "
            "GROUP BY factor_key, factor_label_cyr "
            "ORDER BY row_count DESC LIMIT 10"
        ),
        views=("v_mahalla_peer_factors",),
        tags=(TAG_PEER_FACTOR, TAG_TOP_N),
        keywords=("kuchli", "strength", "factor", "peer"),
    ),
    PromptExample(
        title="most frequent peer weakness factor keys",
        sql=(
            "SELECT factor_key, factor_label_cyr, COUNT(*) AS row_count "
            "FROM v_mahalla_peer_factors WHERE factor_polarity = 'weakness' "
            "GROUP BY factor_key, factor_label_cyr "
            "ORDER BY row_count DESC LIMIT 10"
        ),
        views=("v_mahalla_peer_factors",),
        tags=(TAG_PEER_FACTOR, TAG_TOP_N),
        keywords=("zaif", "weakness", "factor", "peer"),
    ),
    PromptExample(
        title="data-quality issue counts by code with grand total",
        sql=(
            "SELECT q.issue_code, COUNT(*) AS issue_count, "
            "(SELECT COUNT(*) FROM v_data_quality_issues) AS total_issues "
            "FROM v_data_quality_issues q "
            "GROUP BY q.issue_code ORDER BY issue_count DESC LIMIT 100"
        ),
        views=("v_data_quality_issues",),
        tags=(TAG_DATA_QUALITY, TAG_DISTRIBUTION),
        keywords=("data quality", "issue", "muammo", "issue_code"),
    ),
    # ----- Phase 2A: business directory examples -------------------------
    PromptExample(
        title="company count per region",
        sql=(
            "SELECT region_name_cyr, COUNT(*) AS company_count "
            "FROM v_companies "
            "WHERE region_name_cyr IS NOT NULL "
            "GROUP BY region_name_cyr "
            "ORDER BY company_count DESC LIMIT 20"
        ),
        views=("v_companies",),
        tags=(TAG_BUSINESS_COMPANY, TAG_GROUP_BY_REGION),
        keywords=("korxona", "kompaniya", "company", "biznes", "soni", "nechta"),
    ),
    PromptExample(
        title="company count per OKED activity in a single region",
        sql=(
            "SELECT oked_label_uz, COUNT(*) AS company_count "
            "FROM v_companies "
            "WHERE region_name_cyr LIKE '%Фарғона%' "
            "AND oked_label_uz IS NOT NULL "
            "GROUP BY oked_label_uz "
            "ORDER BY company_count DESC LIMIT 25"
        ),
        views=("v_companies",),
        tags=(TAG_BUSINESS_COMPANY, TAG_DISTRIBUTION),
        keywords=("faoliyat", "soha", "yo'nalish", "tadbirkorlik", "oked"),
    ),
    PromptExample(
        title="search companies in a specific industry (restaurant) in a region — include address",
        sql=(
            "SELECT company_name, district_name_cyr, oked_label_uz, address_raw "
            "FROM v_companies "
            "WHERE region_name_cyr LIKE '%Самарқанд%' "
            "AND (oked_label_ru LIKE '%ресторан%' OR oked_label_uz LIKE '%ресторан%') "
            "LIMIT 50"
        ),
        views=("v_companies",),
        tags=(TAG_BUSINESS_COMPANY, TAG_SAMPLE),
        keywords=("restoran", "kafe", "ресторан", "samarqand", "samarkand"),
    ),
    PromptExample(
        title="list suppliers in a region by OKED industry keyword — name + activity + address",
        sql=(
            "SELECT company_name, district_name_cyr, oked_label_uz, address_raw "
            "FROM v_companies "
            "WHERE region_name_cyr LIKE '%Тошкент%' "
            "AND (oked_label_uz LIKE '%улгуржи%' OR oked_label_ru LIKE '%оптовая%') "
            "LIMIT 20"
        ),
        views=("v_companies",),
        tags=(TAG_BUSINESS_COMPANY, TAG_SAMPLE, TAG_ADVISORY),
        keywords=(
            "qaysi kompaniyalar", "kompaniyalar ro'yxati", "yetkazib beruvchi",
            "supplier list", "korxonalar ro'yxati", "manzil", "address",
        ),
    ),
    PromptExample(
        title="top districts by retail-trade company density",
        sql=(
            "SELECT region_name_cyr, district_name_cyr, company_count "
            "FROM v_company_density_by_district "
            "WHERE oked_label_uz LIKE '%чакана%' "
            "ORDER BY company_count DESC LIMIT 20"
        ),
        views=("v_company_density_by_district",),
        tags=(TAG_BUSINESS_COMPANY, TAG_TOP_N),
        keywords=("chakana", "savdo", "zichlik", "density", "tuman"),
    ),
    PromptExample(
        title="top importers by total USD value",
        sql=(
            "SELECT company_name, total_import_usd "
            "FROM v_business_import_summaries "
            "WHERE total_import_usd IS NOT NULL "
            "ORDER BY total_import_usd DESC LIMIT 10"
        ),
        views=("v_business_import_summaries",),
        tags=(TAG_BUSINESS_IMPORT, TAG_TOP_N),
        keywords=("import", "importer", "yetkazib beruvchi", "eng katta", "top"),
    ),
    PromptExample(
        title="top food-product importers (pre-aggregated category column)",
        sql=(
            "SELECT company_name, value_food_products_usd "
            "FROM v_business_import_summaries "
            "WHERE value_food_products_usd IS NOT NULL "
            "ORDER BY value_food_products_usd DESC LIMIT 15"
        ),
        views=("v_business_import_summaries",),
        tags=(TAG_BUSINESS_IMPORT, TAG_TOP_N),
        keywords=("oziq-ovqat", "продукты", "food", "import"),
    ),
    PromptExample(
        title="top importing regions by total USD value",
        sql=(
            "SELECT region_name_cyr, SUM(value_usd) AS region_import_usd "
            "FROM v_business_imports "
            "WHERE region_name_cyr IS NOT NULL AND value_usd IS NOT NULL "
            "GROUP BY region_name_cyr "
            "ORDER BY region_import_usd DESC LIMIT 14"
        ),
        views=("v_business_imports",),
        tags=(TAG_BUSINESS_IMPORT, TAG_GROUP_BY_REGION),
        keywords=("region", "viloyat", "import", "summa"),
    ),
    PromptExample(
        title="imports by TN_VED chapter in a single region",
        sql=(
            "SELECT tnved_chapter, SUM(value_usd) AS chapter_total_usd "
            "FROM v_business_imports "
            "WHERE region_name_cyr LIKE '%Тошкент%' "
            "AND tnved_chapter IS NOT NULL AND value_usd IS NOT NULL "
            "GROUP BY tnved_chapter "
            "ORDER BY chapter_total_usd DESC LIMIT 20"
        ),
        views=("v_business_imports",),
        tags=(TAG_BUSINESS_IMPORT, TAG_BUSINESS_TNVED, TAG_DISTRIBUTION),
        keywords=("tnved", "tn ved", "chapter", "bob", "mahsulot"),
    ),
    PromptExample(
        title="look up TN_VED code description",
        sql=(
            "SELECT tnved_code, description_ru "
            "FROM v_tnved_categories "
            "WHERE chapter = '02' LIMIT 25"
        ),
        views=("v_tnved_categories",),
        tags=(TAG_BUSINESS_TNVED, TAG_SAMPLE),
        keywords=("tn ved", "tnved", "tovar kodi", "mahsulot kodi"),
    ),
    PromptExample(
        title="what does a single company import (by TN_VED chapter)",
        sql=(
            "SELECT tnved_chapter, SUM(value_usd) AS chapter_usd, "
            "COUNT(*) AS declaration_lines "
            "FROM v_business_imports "
            "WHERE company_name LIKE '%UzGasTrade%' "
            "AND tnved_chapter IS NOT NULL AND value_usd IS NOT NULL "
            "GROUP BY tnved_chapter "
            "ORDER BY chapter_usd DESC LIMIT 20"
        ),
        views=("v_business_imports",),
        tags=(TAG_BUSINESS_IMPORT, TAG_BUSINESS_TNVED),
        keywords=("kompaniya", "import", "nima", "qancha"),
    ),
    PromptExample(
        title="top countries of origin by import USD",
        sql=(
            "SELECT origin_country_code, SUM(value_usd) AS country_total_usd "
            "FROM v_business_imports "
            "WHERE origin_country_code IS NOT NULL AND value_usd IS NOT NULL "
            "GROUP BY origin_country_code "
            "ORDER BY country_total_usd DESC LIMIT 15"
        ),
        views=("v_business_imports",),
        tags=(TAG_BUSINESS_IMPORT, TAG_TOP_N),
        keywords=("davlat", "country", "kelib chiqgan", "origin"),
    ),
    PromptExample(
        title="grand total imports across all importers",
        sql=(
            "SELECT SUM(total_import_usd) AS grand_total_import_usd, "
            "COUNT(*) AS importer_count "
            "FROM v_business_import_summaries "
            "WHERE total_import_usd IS NOT NULL"
        ),
        views=("v_business_import_summaries",),
        tags=(TAG_BUSINESS_IMPORT, TAG_SCALAR_COUNT),
        keywords=("jami", "umumiy", "barcha", "total", "grand total"),
    ),
    # ----- Phase 2B: advisory mode examples ------------------------------
    PromptExample(
        title="advisory: top mahallas in a city by population (for biznes start)",
        sql=(
            "SELECT mahalla_name_cyr, population, rating_score "
            "FROM v_mahallas "
            "WHERE district_name_cyr LIKE '%Фарғона шаҳри%' "
            "AND population IS NOT NULL "
            "ORDER BY population DESC LIMIT 25"
        ),
        views=("v_mahallas",),
        tags=(TAG_ADVISORY, TAG_BUSINESS_COMPANY, TAG_TOP_N),
        keywords=(
            "tavsiya", "taklif", "qaysi mahallada", "biznes boshlash",
            "yo'nalish", "recommend", "where should",
        ),
    ),
    PromptExample(
        title="advisory: most/least represented industries per district",
        sql=(
            "SELECT oked_label_uz, company_count "
            "FROM v_company_density_by_district "
            "WHERE district_name_cyr LIKE '%Фарғона шаҳри%' "
            "ORDER BY company_count DESC LIMIT 15"
        ),
        views=("v_company_density_by_district",),
        tags=(TAG_ADVISORY, TAG_BUSINESS_COMPANY, TAG_DISTRIBUTION),
        keywords=(
            "tavsiya", "qaysi yo'nalish", "qaysi soha", "kam uchraydigan",
            "biznes boshlash", "recommend industry",
        ),
    ),
    PromptExample(
        title="advisory: suppliers for restaurant in a region (food OKED + importers)",
        sql=(
            "SELECT company_name, district_name_cyr, oked_label_uz "
            "FROM v_companies "
            "WHERE region_name_cyr LIKE '%Самарқанд%' "
            "AND (oked_label_ru LIKE '%продукт%питан%' "
            "OR oked_label_uz LIKE '%озиқ-овқат%' "
            "OR oked_label_uz LIKE '%улгуржи%' "
            "OR oked_label_ru LIKE '%оптовая%') "
            "LIMIT 100"
        ),
        views=("v_companies",),
        tags=(TAG_ADVISORY, TAG_BUSINESS_COMPANY),
        keywords=(
            "yetkazib beruvchi", "supplier", "restoran", "kafe", "biznes",
            "kerak", "tavsiya", "kim", "qanday",
        ),
    ),
    PromptExample(
        title="combined cross-view scalar counts (no joins)",
        sql=(
            "SELECT (SELECT COUNT(*) FROM v_regions r "
            "WHERE r.mahalla_count_mismatch_flag = 1) "
            "AS regions_with_mahalla_count_mismatch, "
            "(SELECT COUNT(*) FROM v_district_macro_highlights h "
            "WHERE h.highlighted_missing_flag = 1) AS macro_highlights_missing, "
            "(SELECT COUNT(*) FROM v_mahalla_infrastructure i "
            "WHERE i.road_total_km > 1000) "
            "AS mahallas_with_road_total_km_gt_1000, "
            "(SELECT COUNT(*) FROM v_mahalla_crops c "
            "WHERE c.homestead_area_ha < 0) "
            "AS crop_rows_with_negative_homestead_area_ha, "
            "(SELECT COUNT(*) FROM v_data_quality_issues) AS data_quality_issues_total"
        ),
        views=(
            "v_regions",
            "v_district_macro_highlights",
            "v_mahalla_infrastructure",
            "v_mahalla_crops",
            "v_data_quality_issues",
        ),
        tags=(TAG_SCALAR_COUNT, TAG_DATA_QUALITY),
        keywords=("umumiy", "summary", "kombinatsiya", "qisqacha"),
    ),
)


def select_examples(
    question: str,
    relevant_views: tuple[str, ...] = (),
    pattern: str | None = None,
    tag_hints: tuple[str, ...] = (),
    k: int = 5,
) -> list[PromptExample]:
    """Pick the top-k most relevant examples for a question.

    Scoring (per example):
    - +3 for every view in `relevant_views` that the example also touches
    - +2 if `pattern` matches one of the example's tags
    - +2 for every tag in `tag_hints` that the example also has
    - +1 for every keyword found in the lowercased question

    Examples with score 0 are filtered out unless `k > matched`. In that
    case the highest-scoring zero-score examples are filled in deterministic
    title order.
    """
    q_lower = question.lower()
    scored: list[tuple[int, PromptExample]] = []
    for ex in EXAMPLES:
        score = 0
        score += 3 * len(set(relevant_views) & set(ex.views))
        if pattern and pattern in ex.tags:
            score += 2
        score += 2 * len(set(tag_hints) & set(ex.tags))
        for kw in ex.keywords:
            if kw.lower() in q_lower:
                score += 1
        scored.append((score, ex))

    scored.sort(key=lambda s: (-s[0], s[1].title))
    matched = [ex for score, ex in scored if score > 0]
    if len(matched) >= k:
        return matched[:k]
    leftover = [ex for score, ex in scored if score == 0]
    return matched + leftover[: k - len(matched)]


__all__ = [
    "EXAMPLES",
    "PromptExample",
    "TAG_ADVISORY",
    "TAG_APPEALS",
    "TAG_BUSINESS_COMPANY",
    "TAG_BUSINESS_IMPORT",
    "TAG_BUSINESS_TNVED",
    "TAG_CROPS",
    "TAG_DATA_QUALITY",
    "TAG_DISTRIBUTION",
    "TAG_DUPLICATE",
    "TAG_GROUP_BY_DISTRICT",
    "TAG_GROUP_BY_REGION",
    "TAG_INFRASTRUCTURE",
    "TAG_MACRO_INDICATOR",
    "TAG_MISSING_NULL",
    "TAG_PEER_FACTOR",
    "TAG_RATING",
    "TAG_SAMPLE",
    "TAG_SCALAR_COUNT",
    "TAG_SPECIALIZATION",
    "TAG_SUBSIDY",
    "TAG_TOP_N",
    "select_examples",
]
