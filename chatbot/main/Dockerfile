FROM python:3.11-slim

LABEL org.opencontainers.image.title="regional-analytics-chatbot-backend" \
      org.opencontainers.image.description="Read-only regional analytics chatbot backend CLI/runtime"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic
COPY src ./src
COPY questions.md questions_uz_latn.md questions_user_uz_latn.md ./

RUN python -m pip install --upgrade pip \
    && python -m pip install ".[db,query,llm,api]" \
    && useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/audit_reports /app/profile_reports /app/eval_reports \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn cerr_chatbot.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
