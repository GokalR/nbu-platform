"""Sync SQLAlchemy engine for analytics models (psycopg)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

settings = get_settings()
engine_sync = create_engine(settings.sync_database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False, future=True)
BaseSync = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
