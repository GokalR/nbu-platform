"""District-level macro indicator + indicator-point tables."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from cerr_chatbot.db.base import Base, BigIntPk


class DistrictMacroIndicator(Base):
    __tablename__ = "district_macro_indicators"

    macro_indicator_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("districts.district_id"), nullable=False
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    indicator_key: Mapped[str] = mapped_column(String(64), nullable=False)
    indicator_label_cyr: Mapped[str | None] = mapped_column(Text)
    indicator_unit: Mapped[str | None] = mapped_column(String(64))
    indicator_direction: Mapped[str | None] = mapped_column(String(8))
    period_label_cyr: Mapped[str | None] = mapped_column(Text)

    # Derived: highlighted point value extracted into a column for fast joins.
    # Carries two flags so the answer layer can distinguish "no highlighted
    # point at all" from "highlighted point present, value is null".
    highlighted_value_num: Mapped[float | None] = mapped_column(Float)
    highlighted_missing_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    highlighted_value_null_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __table_args__ = (
        Index("ix_district_macro_indicators_indicator_key", "indicator_key"),
        Index("ix_district_macro_indicators_district_id", "district_id"),
        Index("ix_district_macro_indicators_import_run_id", "import_run_id"),
    )


class DistrictMacroPoint(Base):
    __tablename__ = "district_macro_points"

    macro_point_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    macro_indicator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("district_macro_indicators.macro_indicator_id"),
        nullable=False,
    )
    # Importer must copy this from the parent DistrictMacroIndicator. Carrying
    # it on the child row enables run-scoped queries without joining the
    # indicator parent.
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )

    point_order: Mapped[int] = mapped_column(Integer, nullable=False)
    point_district_name_cyr: Mapped[str | None] = mapped_column(Text)
    point_value_num: Mapped[float | None] = mapped_column(Float)
    is_highlighted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_district_macro_points_macro_indicator_id", "macro_indicator_id"),
        Index("ix_district_macro_points_import_run_id", "import_run_id"),
    )
