"""SQLAlchemy model for SME Business Plan submissions (sync engine)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db_sync import BaseSync


def _uuid() -> str:
    return str(uuid.uuid4())


class BusinessPlanSubmission(BaseSync):
    __tablename__ = "business_plan_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user_email: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    lang: Mapped[str] = mapped_column(String(2), default="uz", nullable=False)

    org_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    org_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    inputs: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommended_products: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # Optional: parsed Form №1 + Form №2 + computed credit score, set when
    # the user uploaded financial statements at Step 0.
    historical_financials: Mapped[dict | None] = mapped_column(JSON, default=None, nullable=True)

    model: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)
