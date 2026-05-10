# Regional analytics chatbot backend

PostgreSQL-backed read-only Q&A backend for regional, district, and mahalla
statistics. Default user-facing language: Uzbek Latin.

Runtime path:

```text
user question
  -> conversational router
  -> evidence planner LLM
  -> SQL safety guard
  -> read-only executor
  -> evidence narrator LLM
  -> Uzbek Latin answer
```

The database is the fact source. The planner can only execute SQL that passes
the semantic SQL guard. The narrator receives executor rows and writes the
final answer from that evidence. The deterministic answer composer remains
available as a fallback/table-style output path.

This repo does not ship a UI. The team lead can wrap the backend behind their
own HTTP service, Telegram bot, web app, or queue worker.

See [docs/HANDOFF.md](docs/HANDOFF.md) for deploy/handoff notes,
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module shape, and
[docs/SEMANTIC_VIEWS.md](docs/SEMANTIC_VIEWS.md) for the read surface.

## Requirements

- Python 3.11+
- PostgreSQL 15+ for production
- SQLite is fine for local dev/tests
- Source JSON files in `./cerr_runs/` by default

## Setup

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# bash:     source .venv/bin/activate

pip install -e ".[db,query,llm,dev]"

cp .env.example .env
# Edit .env: set DATABASE_URL or POSTGRES_* and a provider API key.
```

## Recommended runtime config

```dotenv
QUERY_PIPELINE_MODE=evidence
QUERY_MEMORY_MODE=ephemeral
ANSWER_NARRATOR_MODE=llm

LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-5.4

DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
SOURCE_DIR=./cerr_runs
```

`QUERY_MEMORY_MODE=ephemeral` is in-process per-session memory. Restarting the
server clears all sessions.

## Common commands

```bash
# Inspect resolved settings. Secrets are not printed.
python -m cerr_chatbot.cli config

# Discover source JSON files.
python -m cerr_chatbot.cli sources

# Source audit / shape profile / numeric profile.
python -m cerr_chatbot.cli audit
python -m cerr_chatbot.cli profile
python -m cerr_chatbot.cli numeric-profile

# Create schema and import source JSON into DATABASE_URL.
alembic upgrade head
python -m cerr_chatbot.cli import-json

# Deterministic eval over questions_uz_latn.md.
python -m cerr_chatbot.cli eval-questions
```

## Docker

This repo ships a CLI-oriented Docker image plus a PostgreSQL service. It does
not expose a web server. The container runs the same commands as the local CLI.

```bash
# Prepare local Docker variables. Edit POSTGRES_PASSWORD and provider key.
cp .env.docker.example .env

# Build the application image and start PostgreSQL.
docker compose build config
docker compose up -d postgres

# Show resolved settings inside the container.
docker compose run --rm config

# Create schema in the compose PostgreSQL service.
docker compose run --rm migrate

# Import mounted source JSON from ./cerr_runs.
docker compose run --rm import

# Run eval.
docker compose run --rm eval
```

`docker-compose.yml` mounts `./cerr_runs` read-only at `/data/cerr_runs`, keeps
PostgreSQL data in the `postgres_data` volume, and points `DATABASE_URL` at the
compose PostgreSQL service. `.env` is used for Compose variable interpolation
only; it is gitignored and `.dockerignore` keeps it out of the image.

## Tests / lint / types

```bash
pytest
ruff check src tests
mypy src
```

## Project layout

```text
.
|-- alembic/                    schema migrations
|-- Dockerfile
|-- docker-compose.yml
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- HANDOFF.md
|   |-- PROGRESS.md
|   |-- SCHEMA.md
|   `-- SEMANTIC_VIEWS.md
|-- src/cerr_chatbot/
|   |-- audit/                  source-data audit checks
|   |-- db/                     SQLAlchemy models and semantic view DDL
|   |-- eval/                   eval runner
|   |-- importer/               JSON to database importer
|   |-- numeric_profile/        numeric stats over source JSON
|   |-- profile/                JSON shape catalog
|   |-- query/                  query pipeline
|   |-- cli.py
|   |-- config.py
|   `-- sources.py
`-- tests/
```

## Safety guarantees

- `query/sql_guard.py` accepts only a single SELECT against curated `v_*`
  semantic SQL views.
- Raw tables, `SELECT *`, comments, multi-statements, dangerous functions, and
  unsafe joins are rejected before execution.
- The PostgreSQL executor opens reads in a read-only transaction.
- Session memory is planner context only. The narrator, SQL guard, and executor
  never see memory. Snapshots store no SQL and no executed rows.
- Source JSON is read-only input. Importer code should not repair, merge,
  deduplicate, or synthesize source facts.

## Generated artifacts

These are gitignored and should not be committed:

- `.env`
- `*.db`
- `cerr_runs/`, `data/`
- `audit_reports/`, `profile_reports/`, `eval_reports/`
- `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `__pycache__/`
- `.venv/`, build artifacts, logs
