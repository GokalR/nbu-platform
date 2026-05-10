"""Import run, source-file, and data-quality issue tables.

These tables make every loaded row replayable and auditable. They never
mutate source values; they record what was loaded and what was wrong.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cerr_chatbot.db.base import Base, BigIntPk, JsonbType


class ImportRun(Base):
    __tablename__ = "import_runs"

    import_run_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_dir: Mapped[str] = mapped_column(Text, nullable=False)
    source_file_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'completed', 'failed', 'aborted')",
            name="status_allowed",
        ),
    )


class SourceRegionFile(Base):
    __tablename__ = "source_region_files"

    source_file_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    region_code_from_filename: Mapped[int | None] = mapped_column(Integer)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    file_sha256: Mapped[str | None] = mapped_column(String(64))
    # raw_json is intentionally not stored here in the baseline schema. Region
    # files are tens of megabytes; persisting them as a JSONB blob would bloat
    # the database without a current consumer. Re-read from disk via
    # source_dir + source_file when needed; if a future phase needs in-DB raw
    # bodies, add a separate `source_region_file_blobs` table.

    __table_args__ = (
        UniqueConstraint("import_run_id", "source_file", name="uq_run_file"),
        Index("ix_source_region_files_region_code_from_filename", "region_code_from_filename"),
        Index("ix_source_region_files_import_run_id", "import_run_id"),
    )


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    issue_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    issue_code: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_file: Mapped[str | None] = mapped_column(Text)
    region_code: Mapped[int | None] = mapped_column(Integer)
    district_code: Mapped[int | None] = mapped_column(Integer)
    mahalla_stir: Mapped[str | None] = mapped_column(String(32))
    source_json_path: Mapped[str | None] = mapped_column(Text)
    details_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        CheckConstraint("severity IN ('critical', 'warning', 'info')", name="severity_allowed"),
        Index("ix_data_quality_issues_issue_code", "issue_code"),
        Index("ix_data_quality_issues_import_run_id", "import_run_id"),
        Index("ix_data_quality_issues_region_code", "region_code"),
        Index("ix_data_quality_issues_district_code", "district_code"),
        Index("ix_data_quality_issues_mahalla_stir", "mahalla_stir"),
    )


# Lightweight back-references for ergonomic queries; not required by importer.
ImportRun.source_files = relationship(
    "SourceRegionFile",
    primaryjoin="ImportRun.import_run_id == SourceRegionFile.import_run_id",
    viewonly=True,
)
ImportRun.issues = relationship(
    "DataQualityIssue",
    primaryjoin="ImportRun.import_run_id == DataQualityIssue.import_run_id",
    viewonly=True,
)
