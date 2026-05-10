# Handoff Notes

This file is for the  who will deploy or integrate the backend.
Start with `README.md`; this document expands the operational details.

## What This Repo Is

Read-only Q&A backend over regional, district, and mahalla statistics.

The current recommended runtime mode is:

```dotenv
QUERY_PIPELINE_MODE=evidence
QUERY_MEMORY_MODE=ephemeral
ANSWER_NARRATOR_MODE=llm
```

This repo does not ship a UI. Production should wrap
`EvidencePipeline.answer(...)` in the team's real transport layer.

## Required Environment

`.env.example` is the template.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` or `POSTGRES_*` | Database connection. PostgreSQL for production. |
| `SOURCE_DIR` | Source JSON directory. Defaults to `./cerr_runs`. |
| `LLM_PROVIDER` | `openai` or `anthropic`. |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Provider key. |
| `LLM_MODEL` | Model name. |
| `QUERY_PIPELINE_MODE` | Use `evidence` for the multi-SQL pipeline. |
| `QUERY_MEMORY_MODE` | Use `ephemeral` for in-process session memory. |
| `ANSWER_NARRATOR_MODE` | Use `llm` for natural Uzbek Latin answers. |

Settings are cached at process startup. Restart the process after changing
`.env`.

## Database Lifecycle

1. Provision PostgreSQL and set `DATABASE_URL` or the `POSTGRES_*` variables.
2. Run migrations:

   ```bash
   alembic upgrade head
   ```

3. Put source JSON files under `SOURCE_DIR`.
4. Import:

   ```bash
   python -m cerr_chatbot.cli import-json
   ```

Each import creates a new import run. Semantic views read the latest completed
run.

SQLite is supported for local development and tests.

## Docker

The Docker setup is CLI-oriented and Postgres-backed. It does not expose an
HTTP port because this repo does not ship a production API or UI.

Files:

- `Dockerfile`: builds the Python CLI/runtime image.
- `.dockerignore`: keeps local DBs, source dumps, reports, caches, and `.env`
  out of the build context.
- `.env.docker.example`: local Compose variable template.
- `docker-compose.yml`: starts PostgreSQL 15 and one-shot app command
  containers (`config`, `migrate`, `import`, `eval`).

Typical flow:

```bash
cp .env.docker.example .env
# Edit POSTGRES_PASSWORD and provider API key before running.
docker compose build config
docker compose up -d postgres
docker compose run --rm config
docker compose run --rm migrate
docker compose run --rm import
docker compose run --rm eval
```

Compose mounts `./cerr_runs` read-only into the app container as
`/data/cerr_runs` and keeps PostgreSQL files in the `postgres_data` volume. The
compose file overrides `DATABASE_URL` so app commands talk to the `postgres`
service. If the deploy target uses managed PostgreSQL, set `DATABASE_URL` in
the deployment environment instead of using the compose database.

Do not put production secrets in Git. Docker's own guidance recommends secrets
or platform-managed variables for sensitive values; Railway and similar
platforms should use their Variables/Secrets UI rather than committed files.

## Eval

```bash
python -m cerr_chatbot.cli eval-questions
```

Default input is `questions_uz_latn.md`. Reports are written to
`eval_reports/`, which is gitignored. Eval cases use `session_id=None`, so they
do not share memory.

Alternative question files:

- `questions.md`
- `questions_uz_latn.md`
- `questions_user_uz_latn.md`

## Tests

```bash
pytest
ruff check src tests
mypy src
```

Important test areas:

- `test_sql_guard.py`: SQL safety rules.
- `test_evidence.py` and `test_evidence_*`: evidence pipeline behavior.
- `test_session_memory.py`, `test_pipeline_memory.py`,
  `test_pending_clarify_memory.py`: memory lifecycle.
- `test_views.py`: semantic view DDL.
- `test_branding.py`, `test_language_policy.py`: public wording and language
  policy.

## Architecture Summary

```text
user question
  -> conversational router
  -> evidence planner LLM
  -> evidence plan parser
  -> SQL guard
  -> read-only executor
  -> evidence narrator LLM
  -> Uzbek Latin answer
```

Main modules:

| Module | Role |
| --- | --- |
| `audit/` | Source-data audit checks. |
| `profile/` and `numeric_profile/` | Source JSON profiling. |
| `importer/` | JSON to database importer. |
| `db/` | SQLAlchemy models and semantic view DDL. |
| `query/semantic_catalog.py` | Allowed views and columns. |
| `query/sql_guard.py` | SQL AST safety guard. |
| `query/executor.py` | Read-only execution. |
| `query/conversational_router.py` | Greeting/help/out-of-scope short-circuit. |
| `query/evidence.py` | Evidence orchestration. |
| `query/evidence_planner.py` | Planner prompt and provider adapter. |
| `query/evidence_narrator.py` | Narrator prompt and provider adapter. |
| `query/session_memory.py` | Per-session in-memory snapshots. |
| `query/pipeline.py` | Runtime pipeline factory. |
| `eval/` | Markdown eval runner. |

## Session Memory

`QUERY_MEMORY_MODE=ephemeral` attaches an in-process memory store to the
evidence pipeline.

After useful turns the pipeline stores:

- last question
- last resolved question
- answer type
- output columns
- row count
- compact result summary
- timestamp

The snapshot never stores SQL, executed rows, or narrator prose.

On the next turn with the same session id, memory is sent only to the planner.
The planner may use it to resolve a follow-up into a full standalone question.
The SQL is still freshly planned, validated, and executed.

Clarify turns are also stored as pending context. If the next message answers
that clarification, the planner can combine the two messages into a complete
question.

## Generated Artifacts

Do not commit:

- `.env`
- `*.db`
- `cerr_runs/`, `data/`
- `audit_reports/`, `profile_reports/`, `eval_reports/`
- caches: `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `__pycache__/`
- `.venv/`, build outputs, logs, temporary audit files

## Legacy / Back-Compat Surface

Kept intentionally:

- `query/service.py`
- `query/answer.py`
- `query/narrator.py`
- `query/llm_planner.py`
- `query/planner_*`
- `query/schema_linker.py`
- `query/metric_resolver.py`
- `query/example_bank.py`

These support the legacy single-SQL path and are covered by tests. Do not
delete them without first removing the config path and tests deliberately.

## Not Included

- Production HTTP API.
- Production frontend.
- Persistent memory.
- Vector database.
- External web data.
- Geometry/map UI.
