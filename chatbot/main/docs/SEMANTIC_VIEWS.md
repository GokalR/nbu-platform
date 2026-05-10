# Semantic SQL views (Phase 5 / 5.1)

Read-only curated layer for chatbot queries. Every view filters to the latest
completed `import_run`. Defined in `src/cerr_chatbot/db/views.py`; structured
catalog in `src/cerr_chatbot/query/semantic_catalog.py`.

## Global rules

- **Join only on surrogate ids** (`mahalla_id`, `district_id`, `region_id`).
- **NEVER join on natural keys**: `mahalla_stir`, `district_code`, `region_code`, names.
  - 127 duplicate `mahalla_stir` groups.
  - 3 duplicate `district_code` groups.
  - 74 duplicate `(region_code, district_code, mahalla_stir)` groups.
- **NULL means source missing/unavailable**, not zero. Do not `COALESCE(...,0)` defensively.
- **AI insights and geometries are not exposed** in this catalog.
- Every view is automatically scoped to the latest completed import run.

---

## v_latest_import_run

- **Purpose:** show snapshot timestamp; diagnose stale data.
- **Grain:** exactly one row.
- **Columns:** `import_run_id`, `started_at`, `completed_at`, `source_dir`, `source_file_count`.
- **Example:**
  ```sql
  SELECT import_run_id, completed_at FROM v_latest_import_run;
  ```

## v_regions

- **Purpose:** region overview with 6 base KPIs and count-mismatch flag.
- **Grain:** one row per region (14 in current corpus).
- **Important columns:**
  - `region_id` - surrogate; safe join key.
  - `declared_district_count` / `actual_district_count`, `declared_mahalla_count` / `actual_mahalla_count` - source-stated vs nested actual.
  - `mahalla_count_mismatch_flag` - **tri-state**: `1` if declared `<>` actual, `0` if equal, **`NULL` when either side unknown**.
  - `population`, `active_businesses`, `unemployed`, `rating_score`, `problem_loans`, `poor_families` - KPI EAV pivot.
- **Examples:**
  ```sql
  -- Top 5 regions by population
  SELECT region_name_cyr, population FROM v_regions ORDER BY population DESC LIMIT 5;

  -- Regions whose declared mahalla count is wrong
  SELECT region_name_cyr, declared_mahalla_count, actual_mahalla_count
    FROM v_regions WHERE mahalla_count_mismatch_flag = 1;
  ```
- **Warnings:** treat `mahalla_count_mismatch_flag = NULL` distinctly from `0`.

## v_districts

- **Purpose:** district entity row joined with parent region + 6 base KPIs.
- **Grain:** one row per district (212).
- **Join keys:** `district_id`, `region_id`.
- **Important columns:** `region_code`, `region_name_cyr`, `district_code`, `district_name_cyr`, `declared_mahalla_count`, `actual_mahalla_count`, `macro_period_label_cyr`, plus 6 KPI columns.
- **Example:**
  ```sql
  SELECT district_name_cyr, rating_score
  FROM v_districts WHERE region_id = 1 ORDER BY rating_score DESC;
  ```

## v_mahallas

- **Purpose:** mahalla entity row plus parents, summary scalars, and KPIs.
- **Grain:** one row per mahalla (9088).
- **Join keys:** `mahalla_id`, `district_id`, `region_id`.
- **Notable columns:**
  - `rating_score` - mahalla KPI score on the 0-100 scale. Use this for reyting/quality questions.
  - `rating_position` - raw source position/rank-like value from the mahalla row. This is not the 0-100 score.
  - `status_label_cyr` - status badge value lifted from `header.meta` where the label exactly equals the source word for "status" (Cyrillic "Статус"). NULL when absent.
  - `specialization_residual_percent`, `specialization_total_known_percent` - promoted scalars.
  - `peer_set_count`, `peer_set_description_cyr`, `peer_fallback_to_district_flag`, `peer_indicator_count`, `peer_total_indicators_considered` - peer-profile metadata.
  - 6 KPI columns: `population`, `active_businesses`, `unemployed`, `rating_score`, `problem_loans`, `poor_families`.
- **Example:**
  ```sql
  SELECT mahalla_name_cyr, rating_score
  FROM v_mahallas WHERE region_id = 1 ORDER BY rating_score DESC LIMIT 10;
  ```

## v_district_macro_highlights

- **Purpose:** district macro indicator with the highlighted (current-district) value pre-extracted.
- **Grain:** one row per (district, indicator).
- **Important columns:**
  - `highlighted_value_num` - value of the source point flagged `highlighted=true`. NULL when missing or value-null.
  - `highlighted_missing_flag` - true when source had no point flagged highlighted=true. **Row is kept; do not filter out.**
  - `highlighted_value_null_flag` - true when highlighted point exists but its value is null/non-numeric.
- **Example:**
  ```sql
  SELECT district_name_cyr, indicator_key, highlighted_value_num, highlighted_missing_flag
  FROM v_district_macro_highlights
  WHERE indicator_key = 'industry_volume_bln_uzs';
  ```
- **Warnings:**
  - `highlighted_value_num` is **never** inferred from a non-highlighted point.
  - Distinguish `highlighted_missing_flag = TRUE` (no current value at all) from `highlighted_value_null_flag = TRUE` (current point present, value null).

## v_mahalla_infrastructure

- **Purpose:** mahalla infra scalars + parent identifiers.
- **Grain:** one row per mahalla infra block (9088).
- **Notable:** `road_total_km` etc. include extreme values (e.g. 32170). Range-clip at the answer layer if needed; do not filter at view layer.
- **Example:**
  ```sql
  SELECT mahalla_name_cyr, road_total_km
  FROM v_mahalla_infrastructure ORDER BY road_total_km DESC LIMIT 10;
  ```

## v_mahalla_appeals

- **Purpose:** appeal counts per mahalla per reporting period.
- **Grain:** one row per mahalla appeal block (9088).
- **NULL semantics:** `divorce_appeal_count` and `registry_appeal_count` are often NULL; treat as unknown.

## v_mahalla_specializations

- **Purpose:** specialization slots per mahalla, in source order.
- **Grain:** one row per (mahalla, slot). 24628 in current corpus.
- **Order:** `item_order`.

## v_mahalla_crops

- **Purpose:** per-season crop summary per mahalla.
- **Grain:** one row per (mahalla, season). 22105 rows.
- **Warnings:** `total_area_ha` is 100% NULL in the current source; `crops_text_cyr` mostly NULL.

## v_mahalla_subsidy_programs

- **Purpose:** subsidy program enrollment per mahalla.
- **Grain:** one row per (mahalla, program). 50256 rows.
- **NULL semantics:** `application_count` ~80% NULL, `required_amount_mln_uzs` ~84% NULL. Treat NULL as unknown, not 0.

## v_mahalla_peer_factors

- **Purpose:** peer-comparison factors (strengths and weaknesses).
- **Grain:** one row per (mahalla, polarity, factor_order). 90860 rows.
- **Important columns:**
  - `factor_polarity` - `'strength'` or `'weakness'`.
  - `entity_value_num`, `comparison_average_value`, `peer_rank`, `peer_count`, `percentile`.

## v_data_quality_issues

- **Purpose:** surface source data problems for caveats and audits.
- **Grain:** one row per issue raised during the latest completed run (138 in current corpus).
- **Example:**
  ```sql
  SELECT issue_code, COUNT(*) FROM v_data_quality_issues GROUP BY issue_code;
  ```
- **Warnings:** issue rows reference natural keys; those keys are NOT unique by design.
