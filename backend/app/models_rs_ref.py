"""SQLAlchemy models for Regional Strategist reference data."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db_sync import BaseSync


class City(BaseSync):
    __tablename__ = "cities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name_ru: Mapped[str] = mapped_column(String(128), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(128), nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)  # province or city
    supported: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_year: Mapped[int] = mapped_column(Integer, default=2025)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class PeerBenchmarkSet(BaseSync):
    __tablename__ = "peer_benchmarks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    region: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str | None] = mapped_column(String(256), nullable=True)
    benchmarks: Mapped[dict] = mapped_column(JSON, nullable=False)
    companies: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class CityDistrict(BaseSync):
    __tablename__ = "city_districts"

    id: Mapped[str] = mapped_column(String(96), primary_key=True)  # e.g. "fergana:margilon"
    city_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name_ru: Mapped[str] = mapped_column(String(128), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(128), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class CityEnterprise(BaseSync):
    __tablename__ = "city_enterprises"

    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    city_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    district_id: Mapped[str | None] = mapped_column(String(96), nullable=True)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class CreditProduct(BaseSync):
    __tablename__ = "credit_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tier: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # easy | standard
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
