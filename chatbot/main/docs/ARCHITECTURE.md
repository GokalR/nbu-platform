# Architecture

This backend answers analytical questions over regional, district, and mahalla
statistics stored in a relational database.

## Runtime Flow

```text
user question
  -> conversational_router.classify()
  -> EvidenceLlmPlanner.plan()
  -> parse_evidence_plan()
  -> sql_guard.validate()
  -> executor.execute()
  -> EvidenceLlmNarrator.narrate()
  -> final Uzbek Latin answer
```

This repo does not ship a UI. Production should wrap the same pipeline in the
team's real transport layer.

## Data Flow

```text
source JSON files in SOURCE_DIR
  -> source discovery
  -> source audit / profile / numeric profile
  -> Alembic schema
  -> importer
  -> normalized tables
  -> semantic v_* views
  -> guarded SQL reads
```

Source JSON is read-only input. The importer preserves source values and does
not repair, deduplicate, merge, or synthesize facts.

## Main Modules

| Module | Role |
| --- | --- |
| `config.py` | Pydantic settings from `.env` and environment variables. |
| `sources.py` | Source JSON discovery. |
| `audit/` | Source-data integrity checks. |
| `profile/` | JSON shape profile. |
| `numeric_profile/` | Numeric source profile. |
| `importer/` | JSON to database import runs. |
| `db/` | SQLAlchemy models, sessions, and semantic view DDL. |
| `query/semantic_catalog.py` | Allowed view/column catalog. |
| `query/sql_guard.py` | SQL AST validator and safety boundary. |
| `query/executor.py` | Read-only SQL execution. |
| `query/conversational_router.py` | Greeting/help/out-of-scope short-circuit. |
| `query/evidence.py` | Multi-SQL evidence orchestration. |
| `query/evidence_planner.py` | LLM planner prompt and provider adapter. |
| `query/evidence_narrator.py` | LLM narrator prompt and provider adapter. |
| `query/session_memory.py` | Ephemeral per-session memory snapshots. |
| `query/pipeline.py` | Runtime pipeline factory and adapters. |
| `eval/` | Markdown-based eval runner. |

## Planner Contract

The evidence planner returns JSON with:

- `kind`: `sql_plan`, `clarify`, `no_data`, or `unsupported`
- `user_message`
- `primary_sql`
- optional `context_queries`
- optional `memory_use`: `used`, `ignored`, or `unclear`
- optional `resolved_question`

Only `sql_plan` reaches the SQL guard and executor.

## Session Memory

When `QUERY_MEMORY_MODE=ephemeral`, the evidence pipeline stores a compact
`MemorySnapshot` per browser/session id after useful turns.

Memory contains:

- last question and resolved question
- answer type
- output column names
- row count
- compact result summary
- timestamp

Memory does not contain SQL, executed rows, or narrator prose. It is sent only
to the planner so follow-up questions can be resolved into a complete
standalone question. The SQL is still freshly planned and validated.

## Legacy Surface

The legacy single-SQL path is still present:

- `query/service.py`
- `query/answer.py`
- `query/narrator.py`
- `query/llm_planner.py`
- `query/planner_*`
- `query/schema_linker.py`
- `query/metric_resolver.py`
- `query/example_bank.py`

It remains because tests and compatibility paths still cover it. The current
recommended runtime mode is `QUERY_PIPELINE_MODE=evidence`.

## Non-Goals

This repo does not ship:

- production HTTP API
- production frontend
- persistent cross-process memory
- vector database
- external web search
- geometry/map UI
