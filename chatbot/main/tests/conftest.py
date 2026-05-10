"""Test isolation: stop pydantic-settings from reading the developer's .env.

Local developers keep `.env` populated with real runtime values (Postgres,
LLM provider, planner mode). Without this fixture pytest reads those values
into every `Settings()` constructed inside a test, even when the test passes
explicit kwargs — pydantic-settings env-file values can override defaults
the test relied on. Symptoms include `LLM_PROVIDER=openai` masking
`Settings(anthropic_api_key=...)` and `DATABASE_URL=sqlite:///scratch.db`
overriding the host/port/db/user/password kwargs.

This fixture:
1. Points `Settings.model_config["env_file"]` at a path that does not exist
   so pydantic-settings finds no env file during the entire test session.
2. Removes the set of environment variable names `Settings` reads from
   `os.environ`, in case the developer also exported them.
3. Resets the lru_cache on `get_settings` so any earlier collected import
   does not return a polluted instance.

Runtime behavior is unchanged: app/CLI imports `Settings` directly and the
patch only runs under pytest. Tests that explicitly want to read a real
`.env` should construct a `Settings(_env_file="path/to/.env")` of their own.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from cerr_chatbot.config import Settings, get_settings

# Keep this list aligned with `Settings` fields + their `validation_alias`es.
# Anything pydantic-settings would resolve from `os.environ` must appear here
# so the test session can shed leakage from the developer's shell.
_LEAKABLE_ENV_VARS: tuple[str, ...] = (
    "SOURCE_DIR",
    "CERR_SOURCE_DIR",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "DATABASE_URL",
    "LLM_PROVIDER",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "LLM_MODEL",
    "LLM_PLANNER_MODE",
    "ANSWER_NARRATOR_MODE",
    "APP_ENV",
    "LOG_LEVEL",
)


@pytest.fixture(autouse=True, scope="session")
def _isolate_settings_from_dotenv() -> Iterator[None]:
    original_env_file = Settings.model_config.get("env_file")
    Settings.model_config["env_file"] = "/__nonexistent__.env.do.not.read"

    saved: dict[str, str] = {}
    for name in _LEAKABLE_ENV_VARS:
        if name in os.environ:
            saved[name] = os.environ.pop(name)

    get_settings.cache_clear()

    try:
        yield
    finally:
        Settings.model_config["env_file"] = original_env_file
        os.environ.update(saved)
        get_settings.cache_clear()
