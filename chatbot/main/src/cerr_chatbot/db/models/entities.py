"""Region, District, Mahalla entity tables.

Surrogate primary keys protect against natural-key collisions:
- 3 duplicate `district_code` groups in source.
- 127 duplicate `mahalla_stir` groups; (region_code, district_code, stir) also
  has 74 duplicate groups.
Source rows are kept distinct via (import_run_id, source_file, source_*_index).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from cerr_chatbot.db.base import Base, BigIntPk, JsonbType


class Region(Base):
    __tablename__ = "regions"

    region_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_region_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    region_code: Mapped[int | None] = mapped_column(Integer)
    region_name_cyr: Mapped[str | None] = mapped_column(Text)

    declared_district_count: Mapped[int | None] = mapped_column(Integer)
    declared_mahalla_count: Mapped[int | None] = mapped_column(Integer)
    actual_district_count: Mapped[int | None] = mapped_column(Integer)
    actual_mahalla_count: Mapped[int | None] = mapped_column(Integer)

    source_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    raw_header_json: Mapped[Any | None] = mapped_column(JsonbType)
    raw_overview_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        UniqueConstraint(
            "import_run_id", "source_file", "source_region_index", name="uq_region_lineage"
        ),
        Index("ix_regions_region_code", "region_code"),
        Index("ix_regions_import_run_id", "import_run_id"),
    )


class District(Base):
    __tablename__ = "districts"

    district_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("regions.region_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_district_index: Mapped[int] = mapped_column(Integer, nullable=False)

    region_code: Mapped[int | None] = mapped_column(Integer)
    district_code: Mapped[int | None] = mapped_column(Integer)
    district_name_cyr: Mapped[str | None] = mapped_column(Text)
    declared_mahalla_count: Mapped[int | None] = mapped_column(Integer)
    actual_mahalla_count: Mapped[int | None] = mapped_column(Integer)

    macro_period_label_cyr: Mapped[str | None] = mapped_column(Text)

    raw_overview_json: Mapped[Any | None] = mapped_column(JsonbType)
    raw_macro_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        UniqueConstraint(
            "import_run_id",
            "source_file",
            "source_district_index",
            name="uq_district_lineage",
        ),
        Index("ix_districts_district_code", "district_code"),
        Index("ix_districts_region_code", "region_code"),
        Index("ix_districts_region_id", "region_id"),
        Index("ix_districts_import_run_id", "import_run_id"),
    )


class Mahalla(Base):
    __tablename__ = "mahallas"

    mahalla_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("districts.district_id"), nullable=False
    )
    region_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("regions.region_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_district_index: Mapped[int] = mapped_column(Integer, nullable=False)
    source_mahalla_index: Mapped[int] = mapped_column(Integer, nullable=False)

    region_code: Mapped[int | None] = mapped_column(Integer)
    district_code: Mapped[int | None] = mapped_column(Integer)
    mahalla_stir: Mapped[str | None] = mapped_column(String(32))
    mahalla_name_cyr: Mapped[str | None] = mapped_column(Text)
    rating_score: Mapped[float | None] = mapped_column(Float)

    district_rank_text: Mapped[str | None] = mapped_column(String(32))
    region_rank_text: Mapped[str | None] = mapped_column(String(32))
    category_label_cyr: Mapped[str | None] = mapped_column(Text)
    status_label_cyr: Mapped[str | None] = mapped_column(Text)
    specialization_residual_percent: Mapped[float | None] = mapped_column(Float)
    specialization_total_known_percent: Mapped[float | None] = mapped_column(Float)
    crop_total_homestead_area_sotkah: Mapped[float | None] = mapped_column(Float)

    peer_set_count: Mapped[int | None] = mapped_column(Integer)
    peer_set_description_cyr: Mapped[str | None] = mapped_column(Text)
    peer_fallback_to_district_flag: Mapped[bool | None] = mapped_column(Boolean)
    peer_indicator_count: Mapped[int | None] = mapped_column(Integer)
    peer_total_indicators_considered: Mapped[int | None] = mapped_column(Integer)

    raw_header_json: Mapped[Any | None] = mapped_column(JsonbType)
    raw_overview_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        UniqueConstraint(
            "import_run_id",
            "source_file",
            "source_district_index",
            "source_mahalla_index",
            name="uq_mahalla_lineage",
        ),
        Index("ix_mahallas_mahalla_stir", "mahalla_stir"),
        Index("ix_mahallas_district_code", "district_code"),
        Index("ix_mahallas_region_code", "region_code"),
        Index("ix_mahallas_district_id", "district_id"),
        Index("ix_mahallas_region_id", "region_id"),
        Index("ix_mahallas_import_run_id", "import_run_id"),
    )
