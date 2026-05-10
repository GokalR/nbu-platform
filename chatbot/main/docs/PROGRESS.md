# Progress

State file for cross-session continuity. Update at end of every working session.
Append, don't rewrite history.

---

## Phases

| # | Phase                | Status        | Notes |
|---|----------------------|---------------|-------|
| 0 | Foundation           | ✅ done       | Project skeleton, config, source discovery, CLI, tests. |
| 1 | Source discovery     | ✅ done       | `cerr sources` lists region files from `./cerr_runs`. Expect 14 files. |
| 2A | Critical source audit | ✅ done       | Counts, ID uniqueness, prefix, declared-vs-actual mismatch, STIR uniqueness/format. `cerr audit`. |
| 2B1 | JSON shape profile + naming catalog | ✅ done | `cerr profile`. JSON+MD reports, future SQL column names. |
| 2B2 | KPI/macro/peer/detail numeric profile | ✅ done | `cerr numeric-profile`. JSON+MD reports, high-risk findings. |
| 3 | DB schema + migrations | ✅ done       | 19-table schema, Alembic baseline `87897d559260`. No data loaded. |
| 4A | Importer: entities + KPIs + DQ issues | ✅ done | `cerr import-json`. Macro/detail/geo/AI deferred to 4B+. |
| 4B | Importer: macro indicators + points + rating histogram | ✅ done | Detail/geo/AI deferred to 4C+. |
| 4C0 | Schema/catalog sync: mahalla summary columns | ✅ done | status, specialization residual/total_known, crop sotkah promoted to columns. |
| 4C | Importer: mahalla details | ✅ done | infra/appeals/specializations/crops/subsidies/peer factors. Geo + AI deferred to 4D. |
| 4C1 | Mahalla peer_profile metadata columns | ✅ done | peer_set_count/description/fallback + indicator_count + total_indicators_considered. |
| 4D | Importer: geo + AI insights | ⬜ not started | region/district geometries, entity_ai_insights. |
| 5 | Semantic SQL views   | ✅ done       | 12 read-only views, all filter to latest completed run. |
| 5.1 | Semantic catalog + null-safe flag | ✅ done | docs/SEMANTIC_VIEWS.md + machine-readable catalog. mahalla_count_mismatch_flag is tri-state. |
| 6A | SQL safety guard + read-only executor | ✅ done | sqlglot AST validator; only v_* views; LIMIT enforced. |
| 6 | LLM query planner    | ⬜ not started | Intent → allowlisted parameterized SQL. |
| 7 | API endpoints        | ⬜ not started | FastAPI: `/ask`, `/facts`, `/health`. |
| 8 | Test suite           | 🟡 partial    | Unit tests for foundation only. CI not wired. |

## Known data expectations (source of truth: real audit, not memory)

- 14 region JSON files (`cerr_region_*.json`)
- 14 regions
- 212 districts
- 9088 mahallas

These numbers must be **confirmed by Phase 2 audit**, not trusted blindly.

## Session log

### 2026-05-10 — Foundation
- Created `pyproject.toml`, `.env.example`, `.gitignore`, `Makefile`.
- Added `src/cerr_chatbot/{__init__,config,sources,cli}.py`.
- Added unit tests for config and source discovery.
- Documented architecture and progress.

### 2026-05-10 — Default source dir alignment
- Default `cerr_source_dir`: `../cerr_runs` → `./cerr_runs`.
- Regression test guarding the default.

### 2026-05-10 — Phase 2A critical source audit
- `src/cerr_chatbot/audit/` (models, checks, runner) + `cerr audit` CLI.
- Read-only; uses stdlib `json` (no new deps — largest file ~86 MiB fits in RAM).
- Real-corpus run on `./cerr_runs`: 14/14 files, 14/14 regions, 212/212 districts, 9088/9088 mahallas.
- **138 critical issues** in real source — see latest report. Patterns:
  - 127× `MAHALLA_STIR_DUPLICATE` (STIR not globally unique across regions).
  - 5×   `REGION_MAHALLA_COUNT_MISMATCH` (declared `region_mahalla_count` ≠ Σ district mahallas: 1703, 1727, 1730, 1733, 1735).
  - 3×   `DISTRICT_CODE_PREFIX_MISMATCH` (codes 1727410/1727413/1727415 nested under regions 1730/1733/1735).
  - 3×   `DISTRICT_CODE_DUPLICATE_GLOBAL` (1727413 in regions 1727 & 1733; 1727415 in regions 1727 & 1735; 1730233 twice inside region 1730).
- These must be triaged with the data owner before Phase 4 importer.

### 2026-05-10 — Phase 2A patch: global district uniqueness
- Added `check_district_code_global_uniqueness` and `_collect_districts`.
- Removed misleading per-region `DISTRICT_CODE_DUPLICATE` (subsumed by global to avoid double-counting).
- Hardened CLI stdout to UTF-8 (Windows cp1251 console crashed on Cyrillic district names).
- Updated runner docstring (no hardcoded file size).

### 2026-05-10 — Phase 2B1 source profile + naming catalog
- New `src/cerr_chatbot/profile/` (`models`, `walker`, `catalog`, `runner`).
- `cerr profile` writes `profile_reports/profile_<ts>.{json,md}`.
- Walker prunes `.geo`/`.region_geo` subtrees (geometry is opaque blob).
- Catalog (~120 entries) maps JSON paths → future SQL column + table group + description.
- Real-corpus run: 14 regions / 212 districts / 9088 mahallas, 241 observed paths.
- Catalog corrections during this phase: `mahalla.ai_insights` actually nests as `ai_insights.ai_insights.{pros[],cons[],model,generated_at}` plus a sibling `.ai_insights.status`; same content mirrored under `overview.ai_insights`.

### 2026-05-10 — Phase 2B1 quality patch
- Catalog descriptions converted to ASCII-only English (mojibake-safe).
- Added factory helpers `_kpi(prefix)` and `_peer_factor(prefix, polarity)` so district / mahalla KPI metadata and peer strengths/weaknesses share one definition.
- Added `IGNORED_PATHS` registry with reasons; runner classifies observed paths as cataloged / ignored / important-uncataloged.
- Markdown report split into "Recommended Future Column Names", "Important uncataloged paths", "Ignored paths".
- Tests added: catalog descriptions are ASCII; required KPI/weakness/metadata paths are cataloged; generated MD catalog section has no mojibake markers.
- Real coverage now: 158 cataloged + 83 ignored = 241 observed; 0 important-uncataloged; 0 cataloged-unseen.

## Next recommended task

### 2026-05-10 — Phase 2B2 patch: row-id completeness + natural-key diagnostics
- Bug fix: completeness counts were keyed on natural keys (district_code, stir), so duplicates collapsed and rows looked "missing".
- New row-id model: region row id = file name; district row id = (file, district_idx); mahalla row id = (file, district_idx, mahalla_idx).
- All KPI/macro completeness now uses row ids. Real data now reports 0 KPI/macro row gaps (was 6 phantom KPI gaps + 17 phantom macro gaps).
- New `NaturalKeyDiagnostics`: unique counts and duplicate-group counts for region_code, district_code, mahalla_stir, and (region_code, district_code, stir). Reported as separate findings (`REGION_CODE_COLLISION`, `DISTRICT_CODE_COLLISION`, `MAHALLA_STIR_COLLISION`, `MAHALLA_COMPOSITE_KEY_COLLISION`).
- New macro field `highlighted_missing_count`: districts where the indicator is present but no point is flagged highlighted. New finding `MACRO_HIGHLIGHTED_MISSING` (17 indicators flagged on real data).
- New `null_free_numeric_fields` list and revised schema cautions: do not assume every numeric field is null; recommend surrogate PK + source lineage rather than natural keys.
- Added 6 tests covering row-id completeness, collision diagnostics, highlighted-missing detection.
- Real corpus diagnostics confirm manual numbers: district_code unique=209, dup groups=3; stir unique=8961, dup groups=127; (region,district,stir) unique=9014, dup groups=74.

### 2026-05-10 — Phase 2B2 numeric profile
- New `src/cerr_chatbot/numeric_profile/` (`stats`, `models`, `collectors`, `runner`).
- `cerr numeric-profile` writes `profile_reports/numeric_profile_<ts>.{json,md}`.
- `NumericStats`: total/null/null%, type distribution, min/max/mean/median/p01/p99, neg/zero counts, bad-value examples (bool + non-numeric).
- Profiles 18 KPI key/level rows, 17 macro indicator keys, 62 peer factor keys, 27 mahalla detail fields.
- Real-corpus run: 31 high-risk findings.

Real findings:
- `KPI_MISSING_ENTITIES` mahalla level: 127 missing per key — matches Phase 2A 127 duplicate STIRs (duplicates collapse to one entity_id in the seen-set).
- `KPI_MISSING_ENTITIES` district level: 3 missing per key — matches Phase 2A 3 duplicate district codes.
- `MACRO_MISSING_DISTRICTS`: same 3-district gap on every macro indicator.
- `DETAIL_NULL_HEAVY`:
  - `mahalla_crops.total_area_ha` 100% null (never populated).
  - `mahalla_subsidy_programs.required_amount_mln_uzs` 83.57% null.
- Suspicious extremes flagged but not in findings:
  - `road_asphalt_km` / `road_total_km` max = 32170 (impossible).
  - `mahalla_infrastructure.homestead_area_ha` max = 75917.
  - `medical_facility_distance_km` max = 160 (likely unit error).
  - `mahalla_crops.homestead_area_ha` min = -0.0151 (negative area).
  - `total_known_percent` max = 100.01 (rounding).
- No `KPI_BAD_VALUES`, `PEER_RANK_EXCEEDS_COUNT`, or `PEER_PERCENTILE_OUT_OF_RANGE` triggered on real data.

### 2026-05-10 — Phase 3 hardening patch
- Added `import_run_id` BigInteger FK NOT NULL on `district_macro_points` + `ix_district_macro_points_import_run_id`. Importer must copy from parent indicator.
- Added direct `ix_*_import_run_id` indexes on: source_region_files, region_geometries, district_geometries, district_rating_histogram, mahalla_infrastructure, mahalla_appeals, mahalla_specializations, mahalla_crops, mahalla_subsidy_programs, mahalla_peer_factors, entity_ai_insights.
- Added FK indexes on entity_ai_insights for district_id and region_id (mahalla_id index already existed).
- Baseline migration regenerated as `87897d559260` (no production DB exists yet).
- 4 new tests; sqlite upgrade+downgrade roundtrip green.
- Invariants preserved: no UNIQUE on natural keys, no NOT NULL on raw value columns, no CHECK rejecting source values, no merge/dedup/backfill/impute.

### 2026-05-10 — Phase 3 schema baseline
- New `src/cerr_chatbot/db/` (`base`, `session`, `models/{runs,entities,kpis,macro,details,geo}`).
- 19 tables: import_runs, source_region_files, data_quality_issues, regions, districts, mahallas, entity_kpis, district_macro_indicators, district_macro_points, district_rating_histogram, mahalla_infrastructure, mahalla_appeals, mahalla_specializations, mahalla_crops, mahalla_subsidy_programs, mahalla_peer_factors, entity_ai_insights, region_geometries, district_geometries.
- Surrogate `BigInteger` PKs everywhere; natural keys are non-unique columns; lineage uniqueness on (import_run_id, source_file, source_*_index).
- Alembic env + baseline revision `ec94dd8c4cba`. Roundtrip verified on sqlite (upgrade head + downgrade base).
- Schema doc at `docs/SCHEMA.md`.
- 11 schema tests added: required tables, single-column surrogate PKs, no unique on district_code/stir, lineage uniqueness on districts/mahallas/source_region_files, data_quality_issues columns, entity_kpis level FKs, alembic file presence, alembic upgrade runs on sqlite.

## Next recommended task

**Phase 3 - DB schema + Alembic baseline (DONE).**

### 2026-05-10 - Phase 4A importer (entities + KPIs + DQ issues)
- New `src/cerr_chatbot/importer/` (`runner`, `summary`).
- CLI: `cerr import-json` (uses `DATABASE_URL` settings).
- Inserts SourceRegionFile, Region, District, Mahalla, EntityKpi rows.
- Hierarchy linked exclusively by surrogate IDs from JSON nesting; never by name/code/STIR.
- Reuses Phase 2A audit; persists each Issue as `data_quality_issues` row.
- ImportRun lifecycle: started=running, success=completed, exception=failed; never partial-completed.
- Schema patch: `BigInteger` PKs now `BigIntPk = BigInteger().with_variant(Integer(), "sqlite")` so sqlite tests use rowid-alias autoincrement; PostgreSQL keeps `BIGINT bigserial`.
- Baseline migration regenerated as `4157692879f3`.
- Real run vs `./cerr_runs` against scratch sqlite: 14 regions, 212 districts, 9088 mahallas, 55884 entity_kpis (84+1272+54528), 138 critical DQ issues (127 STIR dups, 5 region-mahalla-count mismatches, 3 district-code prefix mismatches, 3 global district-code dups).
- 8 importer tests cover happy path, duplicate district_code/STIR/name fidelity, KPI null/error fidelity, exactly-one entity FK, audit issues persisted, failed-run safety.

### 2026-05-10 - Phase 4B importer (macro + rating histogram)
- Extended `_import_district` with `_import_macro` and `_import_rating_histogram`.
- District macro indicators copied with key/label/unit/direction; period from parent district; surrogate FK only.
- Highlighted derivation: `highlighted_value_num` populated only from a source point with `highlighted=true`. No name-based lookup. Flags: `highlighted_missing_flag` true when no highlighted point; `highlighted_value_null_flag` true when highlighted point exists but value is null/non-numeric.
- All `points[]` inserted in source order with `point_district_name_cyr`, `point_value_num` (numeric/null only), `is_highlighted` (bool only).
- Rating histogram inserted with `bucket_order` from source order.
- Summary fields: `district_macro_indicators`, `district_macro_points`, `district_rating_histogram_rows`.
- Real run vs `./cerr_runs`: macro_indicators=3604, macro_points=51578, rating_histogram=1060. Phase 4A counts (14/14/212/9088/55884/138) unchanged.
- 8 macro/histogram tests added.

### 2026-05-10 - Phase 4C.0 schema/catalog sync
- Added 3 nullable columns to `mahallas`: `specialization_residual_percent`, `specialization_total_known_percent`, `crop_total_homestead_area_sotkah`. `status_label_cyr` already existed; importer now populated.
- Importer extracts status from `header.meta[]` where `label == "Статус"` via `_extract_meta_value`.
- Profile catalog updated to use the new column names.
- Baseline migration regenerated as `1e4b4eb3b1b2`.
- Real run vs `./cerr_runs`: status_label_cyr populated 9088/9088; residual_percent 9088/9088; total_known_percent 9088/9088; crop_sotkah 9019/9088 (matches 2B2 0.76% null rate). Phase 4A/4B counts unchanged.
- 4 new tests cover status meta extraction, missing meta NULL, residual/total/crop fidelity, suspicious >100% kept as-is.

### 2026-05-10 - Phase 4C importer (mahalla details)
- New `_import_mahalla_details` plus 6 helpers: infra, appeals, specializations, crops, subsidies, peer factors.
- All children attached only via parent Mahalla surrogate from JSON nesting; never by name/STIR/code.
- Source-order indices preserved (`item_order`, `season_order`, `program_order`, `factor_order`).
- Subsidies: parent `year` + `data_date` copied per program row; `has_amount_source_flag` strict bool only (`"yes"` -> NULL).
- Peer factors split by `factor_polarity` ('strength'/'weakness'); `factor_order` is per-polarity source order.
- Crops: `raw_crops_json` preserves full season dict including `crops[]`; not parsed further.
- Infra `power_outage_hours_text` strict text only; never coerced.
- Suspicious source values (road=32170, homestead=-0.0151, total_known=100.01) preserved (test asserted).
- 6 new summary counters; 3 new tests.
- Real run vs `./cerr_runs`: infra=9088, appeals=9088, specializations=24628, crops=22105, subsidies=50256, peer factors=90860. Phase 4A/4B/4C.0 counts unchanged.

### 2026-05-10 - Phase 4C.1 mahalla peer metadata
- 5 nullable columns on `mahallas`: `peer_set_count`, `peer_set_description_cyr`, `peer_fallback_to_district_flag` (Boolean), `peer_indicator_count`, `peer_total_indicators_considered`.
- Importer reads from `mahalla.overview.peer_profile.peer_set.*` and `peer_profile.{indicator_count,total_indicators_considered}`. Strict bool only on fallback flag (`"yes"` -> NULL).
- Catalog updated: paths now map to `mahallas` group with new column names.
- Baseline migration regenerated as `770ec9ae0fcc`.
- Real run vs `./cerr_runs`: all 5 columns populated 9088/9088. Phase 4A/4B/4C counts unchanged.
- 4 new tests cover copy fidelity, missing peer_profile NULL, non-bool fallback NULL, duplicate-STIR isolation.

### 2026-05-10 - Phase 5 semantic views
- New `src/cerr_chatbot/db/views.py` with 12 view DDLs as source of truth.
- New alembic migration `4d6923012422_semantic_views.py` (down_revision `770ec9ae0fcc`) executes `CREATE_VIEW_STATEMENTS` / `DROP_VIEW_STATEMENTS`. Baseline kept untouched.
- Every view filters to `(SELECT max(import_run_id) FROM import_runs WHERE status='completed')` so older completed and failed runs are invisible.
- Views: v_latest_import_run, v_regions, v_districts, v_mahallas, v_district_macro_highlights, v_mahalla_infrastructure, v_mahalla_appeals, v_mahalla_specializations, v_mahalla_crops, v_mahalla_subsidy_programs, v_mahalla_peer_factors, v_data_quality_issues.
- KPI pivot (population, active_businesses, unemployed, rating_score, problem_loans, poor_families) joined per level via `MAX(CASE WHEN kpi_key=...)`.
- `v_district_macro_highlights` keeps rows where `highlighted_missing_flag=true` (no row drop).
- Detail views carry `region_code`, `region_name_cyr`, `district_code`, `district_name_cyr`, `mahalla_stir`, `mahalla_name_cyr` plus source-order columns.
- 8 view tests cover existence, latest-run filtering, KPI pivot at 3 levels, duplicate-key non-collapse, missing-highlighted survival, order-column presence, raw-row-count invariance, drop roundtrip.
- Real run vs `./cerr_runs`: views match raw counts: regions=14, districts=212, mahallas=9088, macro highlights=3604, infra=9088, appeals=9088, specializations=24628, crops=22105, subsidies=50256, peer factors=90860, dq issues=138.

### 2026-05-10 - Phase 5.1 catalog + null-safe flag
- `v_regions.mahalla_count_mismatch_flag` is now tri-state: NULL when either side unknown, 1 when declared <> actual, 0 when equal.
- New `docs/SEMANTIC_VIEWS.md` documents purpose, grain, columns, NULL semantics, examples, warnings for all 12 views.
- New `src/cerr_chatbot/query/semantic_catalog.py` with `SemanticView` / `SemanticViewColumn` dataclasses and `SEMANTIC_CATALOG` dict.
- Tests: catalog covers all 12 views, every catalog column exists in the real view, every catalog example executes on sqlite, mismatch flag NULL/0/1 cases verified, doc lists every view.
- Real corpus smoke: regions with mismatch_flag NULL=0, 1=5, 0=9 (matches Phase 2A 5 region mismatches). macro_highlights total=3604, missing-highlighted=373. DQ totals: STIR=127, district global dup=3, prefix=3, region mahalla mismatch=5 (sum=138).

### 2026-05-10 - Phase 6A SQL safety guard + read-only executor
- New optional dependency: `sqlglot>=25,<27` (extras `[query]`). Reason: AST-driven validation is harder to bypass than regex; zero runtime deps; actively maintained.
- `src/cerr_chatbot/query/sql_guard.py` rejects: comments, multi-statement, non-SELECT, SELECT *, raw tables, unknown views, LIMIT > 500, LIMIT <= 0. Appends `LIMIT 100` when absent. Allows `COUNT(*)`. Allows CTEs only if every referenced table is in SEMANTIC_CATALOG.
- `src/cerr_chatbot/query/executor.py` validates first, then executes via SQLAlchemy `text()`. Sets `SET TRANSACTION READ ONLY` on PostgreSQL; SQLite is read-only by virtue of validation.
- `QueryResult` returns validated_sql, referenced_views, limit_appended, columns, rows, row_count.
- 25 tests cover all reject paths, accept paths, and DML-after-validate-blocked safety.

**Phase 4D - Geo + AI insights importer.**
Use 2A triage + 2B1 column catalog + 2B2 numeric findings as inputs:
- Composite keys for entities (region_code, district_code, mahalla_stir not globally unique).
- All numeric KPI / detail columns nullable (every level shows nulls).
- Quarantine row pattern for duplicate STIR / duplicate district codes.
- LEFT JOIN semantics for macro indicators (3-district gap).
- Treat `road_*_km`, `medical_facility_distance_km`, `homestead_area_ha` as nullable + add range-check at view layer.

Do not start schema until 2A triage decisions are confirmed with data owner.
