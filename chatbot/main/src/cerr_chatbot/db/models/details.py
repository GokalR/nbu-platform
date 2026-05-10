"""Mahalla detail tables: rating histogram, infra, appeals, specializations,
crops, subsidy programs, peer factors. Plus entity AI insights.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from cerr_chatbot.db.base import Base, BigIntPk, JsonbType


class DistrictRatingHistogram(Base):
    __tablename__ = "district_rating_histogram"

    histogram_row_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("districts.district_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    bucket_order: Mapped[int] = mapped_column(Integer, nullable=False)
    rating_bucket_label_cyr: Mapped[str | None] = mapped_column(Text)
    mahalla_count: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("ix_district_rating_histogram_district_id", "district_id"),
        Index("ix_district_rating_histogram_import_run_id", "import_run_id"),
    )


class MahallaInfrastructureRow(Base):
    __tablename__ = "mahalla_infrastructure"

    infrastructure_row_id: Mapped[int] = mapped_column(
        BigIntPk, primary_key=True, autoincrement=True
    )
    mahalla_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("mahallas.mahalla_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    road_total_km: Mapped[float | None] = mapped_column(Float)
    road_dirt_km: Mapped[float | None] = mapped_column(Float)
    road_asphalt_km: Mapped[float | None] = mapped_column(Float)
    households_without_drinking_water_count: Mapped[int | None] = mapped_column(Integer)
    power_outage_count: Mapped[int | None] = mapped_column(Integer)
    power_outage_hours_text: Mapped[str | None] = mapped_column(Text)
    medical_facility_distance_km: Mapped[float | None] = mapped_column(Float)
    school_count: Mapped[int | None] = mapped_column(Integer)
    sports_facility_count: Mapped[int | None] = mapped_column(Integer)
    kindergarten_count: Mapped[int | None] = mapped_column(Integer)
    homestead_area_ha: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        Index("ix_mahalla_infrastructure_mahalla_id", "mahalla_id"),
        Index("ix_mahalla_infrastructure_import_run_id", "import_run_id"),
    )


class MahallaAppealRow(Base):
    __tablename__ = "mahalla_appeals"

    appeal_row_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    mahalla_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("mahallas.mahalla_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    crime_appeal_count: Mapped[int | None] = mapped_column(Integer)
    divorce_appeal_count: Mapped[int | None] = mapped_column(Integer)
    social_aid_appeal_count: Mapped[int | None] = mapped_column(Integer)
    employment_appeal_count: Mapped[int | None] = mapped_column(Integer)
    gas_appeal_count: Mapped[int | None] = mapped_column(Integer)
    registry_appeal_count: Mapped[int | None] = mapped_column(Integer)
    appeals_year: Mapped[int | None] = mapped_column(Integer)
    appeals_period_label_cyr: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("ix_mahalla_appeals_mahalla_id", "mahalla_id"),
        Index("ix_mahalla_appeals_import_run_id", "import_run_id"),
    )


class MahallaSpecializationItem(Base):
    __tablename__ = "mahalla_specializations"

    specialization_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    mahalla_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("mahallas.mahalla_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    item_order: Mapped[int] = mapped_column(Integer, nullable=False)
    specialization_slot: Mapped[str | None] = mapped_column(String(32))
    specialization_slot_label_cyr: Mapped[str | None] = mapped_column(Text)
    specialization_type_cyr: Mapped[str | None] = mapped_column(Text)
    specialization_direction_cyr: Mapped[str | None] = mapped_column(Text)
    household_count: Mapped[float | None] = mapped_column(Float)
    population_count: Mapped[float | None] = mapped_column(Float)
    share_percent: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        Index("ix_mahalla_specializations_mahalla_id", "mahalla_id"),
        Index("ix_mahalla_specializations_import_run_id", "import_run_id"),
    )


class MahallaCropSeason(Base):
    __tablename__ = "mahalla_crops"

    crop_season_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    mahalla_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("mahallas.mahalla_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    season_order: Mapped[int] = mapped_column(Integer, nullable=False)
    season_key: Mapped[str | None] = mapped_column(String(32))
    season_label_cyr: Mapped[str | None] = mapped_column(Text)
    crops_text_cyr: Mapped[str | None] = mapped_column(Text)
    total_area_ha: Mapped[float | None] = mapped_column(Float)
    homestead_area_ha: Mapped[float | None] = mapped_column(Float)
    household_count: Mapped[int | None] = mapped_column(Integer)
    raw_crops_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        Index("ix_mahalla_crops_mahalla_id", "mahalla_id"),
        Index("ix_mahalla_crops_import_run_id", "import_run_id"),
    )


class MahallaSubsidyProgram(Base):
    __tablename__ = "mahalla_subsidy_programs"

    subsidy_program_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    mahalla_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("mahallas.mahalla_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    program_order: Mapped[int] = mapped_column(Integer, nullable=False)
    subsidy_program_label_cyr: Mapped[str | None] = mapped_column(Text)
    application_count: Mapped[float | None] = mapped_column(Float)
    required_amount_mln_uzs: Mapped[float | None] = mapped_column(Float)
    has_amount_source_flag: Mapped[bool | None] = mapped_column(Boolean)
    subsidies_year: Mapped[int | None] = mapped_column(Integer)
    subsidies_data_date: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        Index("ix_mahalla_subsidy_programs_mahalla_id", "mahalla_id"),
        Index("ix_mahalla_subsidy_programs_import_run_id", "import_run_id"),
    )


class MahallaPeerFactor(Base):
    __tablename__ = "mahalla_peer_factors"

    peer_factor_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    mahalla_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("mahallas.mahalla_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    factor_polarity: Mapped[str] = mapped_column(String(16), nullable=False)
    factor_order: Mapped[int] = mapped_column(Integer, nullable=False)
    factor_key: Mapped[str | None] = mapped_column(Text)
    factor_label_cyr: Mapped[str | None] = mapped_column(Text)
    factor_unit: Mapped[str | None] = mapped_column(String(64))
    factor_direction: Mapped[str | None] = mapped_column(String(8))
    entity_value_num: Mapped[float | None] = mapped_column(Float)
    comparison_average_value: Mapped[float | None] = mapped_column(Float)
    peer_rank: Mapped[int | None] = mapped_column(Integer)
    peer_count: Mapped[int | None] = mapped_column(Integer)
    percentile: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        CheckConstraint(
            "factor_polarity IN ('strength', 'weakness')", name="factor_polarity_allowed"
        ),
        Index("ix_mahalla_peer_factors_mahalla_id", "mahalla_id"),
        Index("ix_mahalla_peer_factors_factor_key", "factor_key"),
        Index("ix_mahalla_peer_factors_import_run_id", "import_run_id"),
    )


class EntityAiInsight(Base):
    __tablename__ = "entity_ai_insights"

    insight_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    mahalla_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("mahallas.mahalla_id"))
    district_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("districts.district_id"))
    region_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("regions.region_id"))

    polarity: Mapped[str] = mapped_column(String(8), nullable=False)
    bullet_order: Mapped[int] = mapped_column(Integer, nullable=False)
    bullet_text: Mapped[str | None] = mapped_column(Text)
    ai_model_name: Mapped[str | None] = mapped_column(Text)
    ai_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ai_insights_status: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        CheckConstraint("polarity IN ('pro', 'con')", name="ai_polarity_allowed"),
        Index("ix_entity_ai_insights_mahalla_id", "mahalla_id"),
        Index("ix_entity_ai_insights_district_id", "district_id"),
        Index("ix_entity_ai_insights_region_id", "region_id"),
        Index("ix_entity_ai_insights_import_run_id", "import_run_id"),
    )
