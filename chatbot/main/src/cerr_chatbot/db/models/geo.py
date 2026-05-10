"""Geometry storage as JSONB blobs for now.

A future phase may convert to PostGIS `geometry` columns; the column type is
isolated here so the change is local.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from cerr_chatbot.db.base import Base, BigIntPk, JsonbType


class RegionGeometry(Base):
    __tablename__ = "region_geometries"

    region_geometry_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("regions.region_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    region_geometry_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        Index("ix_region_geometries_region_id", "region_id"),
        Index("ix_region_geometries_import_run_id", "import_run_id"),
    )


class DistrictGeometry(Base):
    __tablename__ = "district_geometries"

    district_geometry_id: Mapped[int] = mapped_column(
        BigIntPk, primary_key=True, autoincrement=True
    )
    district_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("districts.district_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    district_geometry_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        Index("ix_district_geometries_district_id", "district_id"),
        Index("ix_district_geometries_import_run_id", "import_run_id"),
    )
