"""EAV table for KPI rows at all three entity levels."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from cerr_chatbot.db.base import Base, BigIntPk


class EntityKpi(Base):
    __tablename__ = "entity_kpis"

    entity_kpi_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    entity_level: Mapped[str] = mapped_column(String(16), nullable=False)
    # Surrogate FKs for each level - importer fills exactly one of these.
    region_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("regions.region_id"))
    district_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("districts.district_id"))
    mahalla_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("mahallas.mahalla_id"))

    kpi_key: Mapped[str] = mapped_column(String(64), nullable=False)
    kpi_label_cyr: Mapped[str | None] = mapped_column(Text)
    source_table_name: Mapped[str | None] = mapped_column(Text)
    source_column_name: Mapped[str | None] = mapped_column(Text)
    kpi_format: Mapped[str | None] = mapped_column(String(32))
    kpi_provenance: Mapped[str | None] = mapped_column(String(32))
    kpi_direction: Mapped[str | None] = mapped_column(String(8))
    kpi_value_num: Mapped[float | None] = mapped_column(Float)
    kpi_error_text: Mapped[str | None] = mapped_column(Text)
    change_percent: Mapped[float | None] = mapped_column(Float)
    district_average_value: Mapped[float | None] = mapped_column(Float)
    compare_scope: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        CheckConstraint(
            "entity_level IN ('region', 'district', 'mahalla')",
            name="entity_level_allowed",
        ),
        # Importer rule (enforced in code, not as DB constraint to keep
        # raw-import tolerance): exactly one of region_id/district_id/mahalla_id
        # is non-null for each row.
        Index("ix_entity_kpis_kpi_key", "kpi_key"),
        Index("ix_entity_kpis_entity_level_kpi_key", "entity_level", "kpi_key"),
        Index("ix_entity_kpis_region_id", "region_id"),
        Index("ix_entity_kpis_district_id", "district_id"),
        Index("ix_entity_kpis_mahalla_id", "mahalla_id"),
        Index("ix_entity_kpis_import_run_id", "import_run_id"),
    )
