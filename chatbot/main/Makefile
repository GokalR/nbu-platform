.PHONY: install install-dev install-db install-runtime install-all test lint fmt typecheck clean sources config migrate migrate-down docker-build docker-up-db docker-down docker-config docker-migrate docker-import docker-eval

PY ?= python

install:
	$(PY) -m pip install -e .

install-dev:
	$(PY) -m pip install -e ".[dev]"

install-db:
	$(PY) -m pip install -e ".[db,dev]"

install-runtime:
	$(PY) -m pip install -e ".[db,query,llm]"

install-all:
	$(PY) -m pip install -e ".[db,query,llm,dev]"

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests

fmt:
	$(PY) -m ruff format src tests
	$(PY) -m ruff check --fix src tests

typecheck:
	$(PY) -m mypy src

sources:
	$(PY) -m cerr_chatbot.cli sources

config:
	$(PY) -m cerr_chatbot.cli config

migrate:
	$(PY) -m alembic upgrade head

migrate-down:
	$(PY) -m alembic downgrade -1

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info

docker-build:
	docker compose build config

docker-up-db:
	docker compose up -d postgres

docker-down:
	docker compose down

docker-config:
	docker compose run --rm config

docker-migrate:
	docker compose run --rm migrate

docker-import:
	docker compose run --rm import

docker-eval:
	docker compose run --rm eval
