"""SQLAlchemy models for analytics reference data (regions, region_data)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_sync import BaseSync


class Region(BaseSync):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name_ru: Mapped[str] = mapped_column(String(128), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(128), nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)  # national, region, city, district
    parent_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("regions.id"), nullable=True
    )
    kind: Mapped[str | None] = mapped_column(String(16), nullable=True)  # city or district
    population_k: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    area_km2: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    data_year: Mapped[int] = mapped_column(Integer, default=2025)
    kpis: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    parent: Mapped["Region | None"] = relationship("Region", remote_side=[id], foreign_keys=[parent_id])
    data_entries: Mapped[list["RegionData"]] = relationship(
        back_populates="region", cascade="all, delete-orphan"
    )


class RegionData(BaseSync):
    __tablename__ = "region_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_year: Mapped[int] = mapped_column(Integer, default=2025, nullable=False)

    profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    analytics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enterprises: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (UniqueConstraint("region_id", "data_year", name="uq_region_data_year"),)

    region: Mapped[Region] = relationship(back_populates="data_entries")
