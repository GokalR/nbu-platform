"""Tests for app.config — Settings property conversions."""

from app.config import Settings


class TestAsyncDatabaseUrl:
    def test_converts_postgresql_to_asyncpg(self):
        s = Settings(database_url="postgresql://user:pass@host:5432/db")
        assert s.async_database_url == "postgresql+asyncpg://user:pass@host:5432/db"

    def test_converts_postgres_heroku_shorthand_to_asyncpg(self):
        s = Settings(database_url="postgres://user:pass@host:5432/db")
        assert s.async_database_url == "postgresql+asyncpg://user:pass@host:5432/db"

    def test_does_not_double_convert_if_already_asyncpg(self):
        s = Settings(database_url="postgresql+asyncpg://user:pass@host:5432/db")
        assert s.async_database_url == "postgresql+asyncpg://user:pass@host:5432/db"


class TestSyncDatabaseUrl:
    def test_converts_postgresql_to_psycopg(self):
        s = Settings(database_url="postgresql://user:pass@host:5432/db")
        assert s.sync_database_url == "postgresql+psycopg://user:pass@host:5432/db"

    def test_converts_postgres_heroku_shorthand_to_psycopg(self):
        s = Settings(database_url="postgres://user:pass@host:5432/db")
        assert s.sync_database_url == "postgresql+psycopg://user:pass@host:5432/db"

    def test_does_not_double_convert_if_already_psycopg(self):
        s = Settings(database_url="postgresql+psycopg://user:pass@host:5432/db")
        assert s.sync_database_url == "postgresql+psycopg://user:pass@host:5432/db"


class TestCorsOriginList:
    def test_parses_comma_separated_origins(self):
        s = Settings(cors_origins="http://localhost:3000,https://example.com")
        assert s.cors_origin_list == ["http://localhost:3000", "https://example.com"]

    def test_strips_whitespace(self):
        s = Settings(cors_origins="  http://a.com , http://b.com  ")
        assert s.cors_origin_list == ["http://a.com", "http://b.com"]

    def test_single_origin(self):
        s = Settings(cors_origins="http://localhost:5173")
        assert s.cors_origin_list == ["http://localhost:5173"]

    def test_ignores_empty_segments(self):
        s = Settings(cors_origins="http://a.com,,http://b.com,")
        assert s.cors_origin_list == ["http://a.com", "http://b.com"]


class TestVideoBaseUrlStripped:
    def test_removes_trailing_slash(self):
        s = Settings(video_base_url="https://cdn.example.com/")
        assert s.video_base_url_stripped == "https://cdn.example.com"

    def test_removes_multiple_trailing_slashes(self):
        s = Settings(video_base_url="https://cdn.example.com///")
        assert s.video_base_url_stripped == "https://cdn.example.com"

    def test_no_change_when_no_trailing_slash(self):
        s = Settings(video_base_url="https://cdn.example.com")
        assert s.video_base_url_stripped == "https://cdn.example.com"

    def test_empty_string_stays_empty(self):
        s = Settings(video_base_url="")
        assert s.video_base_url_stripped == ""
