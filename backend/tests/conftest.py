"""Shared pytest fixtures and environment setup for backend tests."""

import os

# Ensure test environment variables are set before any app imports
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("APP_ENV", "test")
