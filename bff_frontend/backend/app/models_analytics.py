"""SQLAlchemy models for the analytics/regional-strategist backend (sync engine)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_sync import BaseSync


def _uuid() -> str:
    return str(uuid.uuid4())


class Submission(BaseSync):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    profile: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    finance: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    city_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lang: Mapped[str] = mapped_column(String(8), default="ru", nullable=False)

    uploads: Mapped[list["ExcelUpload"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["AnalysisResult"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )


class ExcelUpload(BaseSync):
    __tablename__ = "excel_uploads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    submission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(256), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    parsed: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    raw_blob: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    submission: Mapped[Submission] = relationship(back_populates="uploads")


class AnalysisResult(BaseSync):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    submission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    context: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    context_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    output: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    model: Mapped[str] = mapped_column(String(64), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    submission: Mapped[Submission] = relationship(back_populates="analyses")
