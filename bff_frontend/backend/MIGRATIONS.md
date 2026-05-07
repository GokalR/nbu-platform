# Manual migration notes

The project does not use Alembic. Schema is kept in sync by SQLAlchemy's
`BaseSync.metadata.create_all()` at startup, which creates **new** tables but
never alters existing ones. Column changes, renames, and drops must be run by
hand against the Railway Postgres instance before (or during) the deploy that
ships the matching Python code.

Each section below documents a discrete migration. When adding one, follow the
pattern: headline with date, short "why", exact SQL, then the seed / backfill
command.

## 2026-04-21 — RS reference tables (Step 5 dynamic data)

Step 5 used to read districts, enterprises, and the NBU credit catalog from
hardcoded JS files in `frontend/src/data/regionalStrategist/`. Those files
locked the dashboard to Fergana + one sector and made adding a new region a
code change. They now live in Postgres and are fetched through
`GET /api/rs/reference/*` endpoints.

**New tables** (`backend/app/models_rs_ref.py`):

- `city_districts` — mahallas / tumans per pilot city (Fergana, Margilan)
- `city_enterprises` — anchor enterprises per city + sector
- `credit_products` — NBU "Kreditlar 2026" catalog with match rules

All three are additive — `create_all()` at startup will create them on first
boot. No SQL to run by hand. Seed them with:

```bash
cd backend
python seed_rs_reference.py
```

The script is idempotent (`db.merge()` everywhere), so re-running it safely
updates rows when the JSON in `backend/data/rs_seed/` changes.

## 2026-04-21 (later) — Dedup columns for Excel + Analysis

Two cache-key columns added so we stop re-sending identical work to Claude.
Both are **nullable** so old rows keep working — new rows get populated.

```sql
ALTER TABLE excel_uploads     ADD COLUMN file_hash    VARCHAR(64);
CREATE INDEX ix_excel_uploads_file_hash     ON excel_uploads(file_hash);

ALTER TABLE analysis_results  ADD COLUMN context_hash VARCHAR(64);
CREATE INDEX ix_analysis_results_context_hash ON analysis_results(context_hash);
```

**Semantics.**
- `excel_uploads.file_hash` — SHA-256 of the uploaded Excel blob. Upload route does
  `SELECT … WHERE submission_id=? AND kind=? AND file_hash=?` first; hit → return
  existing row, skip Claude parse entirely.
- `analysis_results.context_hash` — SHA-256 of canonical-JSON context (profile +
  finance + city + excel ratios + rulesScore, sorted keys). Analysis route returns
  the cached row when the same context has already produced a successful result.

**Why:** one user session loading Step 5 should not trigger a 2–4 second Claude
call every time the page mounts. Hash dedup makes repeated visits free and
protects against accidental duplicate uploads.

## Deferred / follow-up work

Items the Step 5 refactor left for a later session:

1. **Heatmap components still import hardcoded data**
   (`RsFerganaHeatmap.vue`, `RsMargilanHeatmap.vue` import from
   `@/data/regionalStrategist/fergana-districts.js` etc). They work because
   the backend JSON is seeded from the same source, but the heatmaps should
   accept `districts` / `enterprises` as props and be driven by
   `useRsReference()` like the rest of Step 5. The old frontend data files
   can be deleted only after that cut-over.

2. **Hardcoded demographic numbers** at the top of Section 3 (births 98 319,
   marriages 28 896, urban share 56.7%) are Fergana-region 2025 figures. Move
   them into `cities.data.demographics` in the seed and bind the template to
   `backendCity.value.data.demographics`.

3. **SWOT quadrants in Section 2** still render the static `t.SWOT` fallback.
   The Claude `analysis.output.strengths` / `.weaknesses` arrays are already
   generated — rewire the template to prefer them when present and fall back
   to `t.SWOT` only if Claude didn't run.

4. **Action Plan in Section 6** should pull `analysis.output.nextSteps` when
   present and fall back to `t.ACTION_STEPS` only for the demo seed path.
