"""Declarative base + shared SQLAlchemy types."""

from __future__ import annotations

from sqlalchemy import JSON, BigInteger, Integer, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(table_name)s_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Use JSONB on PostgreSQL, JSON elsewhere (SQLite for tests).
JsonbType = JSON().with_variant(JSONB(), "postgresql")

# BIGINT primary keys: SQLite needs INTEGER PRIMARY KEY for the rowid-alias
# autoincrement to work; PostgreSQL keeps BIGINT (bigserial).
BigIntPk = BigInteger().with_variant(Integer(), "sqlite")
