"""Runtime configuration. Reads .env via pydantic-settings.

Settings are read once at import time. Do not mutate the returned object;
construct a new Settings() if you need overrides in tests.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Source data. Public env var is SOURCE_DIR; the legacy CERR_SOURCE_DIR
    # name is still accepted for backward compatibility. Internal Python
    # attribute keeps its existing name; renaming it is a deferred refactor.
    cerr_source_dir: Path = Field(
        default=Path("./cerr_runs"),
        validation_alias=AliasChoices("SOURCE_DIR", "CERR_SOURCE_DIR", "cerr_source_dir"),
    )

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "cerr"
    postgres_user: str = "cerr"
    postgres_password: str = "change_me"
    database_url: str | None = None

    # LLM
    llm_provider: str = "anthropic"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    llm_model: str = "claude-opus-4-7"
    # "single_stage" (default) routes through LlmPlanner; "two_stage" uses
    # TwoStageLlmPlanner (schema link -> SQL prompt). Backward compatible.
    llm_planner_mode: str = "single_stage"
    # "deterministic" (default) keeps the markdown-table composer. "llm"
    # opts in to AnswerNarrator (LLM rewrites the SQL rows into prose).
    answer_narrator_mode: str = "deterministic"
    # "legacy" (default) wires QueryService + Narrator. "evidence" wires the
    # multi-SQL evidence_ask pipeline + EvidenceLlmNarrator. Affects runtime
    # and eval-questions; tests inject pipelines directly.
    query_pipeline_mode: str = "legacy"
    # "off" (default) disables conversation memory. "ephemeral" attaches an
    # in-process per-session memory store to the EvidencePipeline. Snapshots
    # are compact session context for the evidence planner only; SQL guard,
    # executor, and narrator do not receive raw memory.
    query_memory_mode: str = "off"

    # Runtime
    app_env: str = "dev"
    log_level: str = "INFO"

    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
