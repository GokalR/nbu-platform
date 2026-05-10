from __future__ import annotations

from pathlib import Path

from cerr_chatbot.config import Settings


def test_default_cerr_source_dir_is_local_cerr_runs(monkeypatch, tmp_path: Path) -> None:
    """Default must point at ./cerr_runs (local), never ../cerr_runs (parent)."""
    monkeypatch.delenv("CERR_SOURCE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.cerr_source_dir == Path("./cerr_runs")


def test_resolved_database_url_default() -> None:
    s = Settings(
        postgres_host="db",
        postgres_port=5433,
        postgres_db="cerr_test",
        postgres_user="u",
        postgres_password="p",
    )
    assert s.resolved_database_url() == "postgresql+psycopg://u:p@db:5433/cerr_test"


def test_resolved_database_url_override_wins() -> None:
    explicit = "postgresql+psycopg://x:y@h:1/db"
    s = Settings(database_url=explicit)
    assert s.resolved_database_url() == explicit
