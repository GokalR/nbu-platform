# PostgreSQL schema (Phase 3 baseline)

Read-only summary of the SQLAlchemy models in `src/cerr_chatbot/db/models/`.
The database holds **exact source values plus lineage**. Nothing is imputed,
deduplicated, repaired, or merged. Quality issues are recorded in a separate
`data_quality_issues` table.

## Layered design

| Layer | Purpose |
|---|---|
| Run + lineage | `import_runs`, `source_region_files`, `data_quality_issues` |
| Entities | `regions`, `districts`, `mahallas` |
| EAV facts | `entity_kpis` (region/district/mahalla level) |
| District macro | `district_macro_indicators`, `district_macro_points` |
| Mahalla detail | `mahalla_infrastructure`, `mahalla_appeals`, `mahalla_specializations`, `mahalla_crops`, `mahalla_subsidy_programs`, `mahalla_peer_factors`, `district_rating_histogram` |
| Narrative | `entity_ai_insights` (never authoritative for numbers) |
| Geometry | `region_geometries`, `district_geometries` (jsonb blobs) |

19 tables total.

## Identity model

- **All primary keys are surrogate `BigInteger`** (`region_id`, `district_id`, `mahalla_id`, etc.).
- **Natural keys are columns**, never PKs. `district_code`, `mahalla_stir`, `region_code` are NOT unique in source data:
  - 3 duplicate `district_code` groups
  - 127 duplicate `mahalla_stir` groups
  - 74 duplicate `(region_code, district_code, stir)` composite groups
- **Source lineage** uniqueness is enforced via:
  - `regions(import_run_id, source_file, source_region_index)`
  - `districts(import_run_id, source_file, source_district_index)`
  - `mahallas(import_run_id, source_file, source_district_index, source_mahalla_index)`

This guarantees idempotent re-import per run without overwriting source rows.

## Foreign keys

```
regions   <- districts.region_id
districts <- mahallas.district_id
regions   <- mahallas.region_id
import_runs <- (every fact table).import_run_id
districts <- district_macro_indicators / district_geometries / district_rating_histogram
mahallas  <- mahalla_* / entity_ai_insights
regions/districts/mahallas <- entity_kpis (one of three nullable FKs)
```

## Mahalla summary columns

Promoted scalars stored directly on `mahallas` for fast lookups (in addition to the raw JSON blobs):
- `status_label_cyr` — value of `header.meta[]` item where `label == "Статус"`. NULL when absent.
- `specialization_residual_percent` — `overview.detail.specialization.residual_percent`.
- `specialization_total_known_percent` — `overview.detail.specialization.total_known_percent`.
- `crop_total_homestead_area_sotkah` — `overview.detail.crops.total_homestead_area_sotikh` (source key `sotikh`).

All four nullable. Suspicious source values (e.g. `total_known_percent = 100.01`) preserved as-is.

## Raw JSON preservation

JSONB blobs preserved per row for auditability:
- `regions.raw_header_json`, `regions.raw_overview_json`
- `districts.raw_overview_json`, `districts.raw_macro_json`
- `mahallas.raw_header_json`, `mahallas.raw_overview_json`
- `mahalla_crops.raw_crops_json`
- `region_geometries.region_geometry_json`, `district_geometries.district_geometry_json`
- `data_quality_issues.details_json`

The full raw region body is intentionally NOT mirrored into a JSONB column on
`source_region_files` to avoid 700+ MiB of bloat. Re-read from disk via
`source_dir + source_file`.

## Constraints

- Surrogate PK on every table.
- CHECK constraints on small enum-like columns: `import_runs.status`, `data_quality_issues.severity`, `entity_kpis.entity_level`, `mahalla_peer_factors.factor_polarity`, `entity_ai_insights.polarity`.
- No UNIQUE constraint on `district_code`, `mahalla_stir`, `(region_code, district_code, stir)`, etc.
- Lineage UNIQUE constraints listed above.
- Many non-unique indexes for lookup (`region_code`, `district_code`, `mahalla_stir`, `kpi_key`, `entity_level + kpi_key`, `indicator_key`, `factor_key`, FKs, `import_run_id` on every fact/detail/geometry table). `district_macro_points` carries `import_run_id` as FK NOT NULL (importer copies from parent `district_macro_indicators`) so run-scoped queries skip the indicator join.

## Macro highlighted-value semantics

`district_macro_indicators.highlighted_value_num` holds the highlighted point
value when present. Two flags distinguish the failure modes the answer layer
must handle:

- `highlighted_missing_flag = TRUE` -> indicator row exists, but no point was
  flagged highlighted in source.
- `highlighted_value_null_flag = TRUE` -> highlighted point exists but its
  value is null.

The full point list lives in `district_macro_points` for direct query.

## What this phase does NOT include

- No JSON importer.
- No data loaded.
- No semantic / curated views.
- No PostGIS conversion (geometries kept as JSONB).
- No row-level security, no partitioning, no materialized views.
- No application of integrity-violating cleanup; raw values preserved.
