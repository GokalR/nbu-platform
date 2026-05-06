"""SQLAlchemy model for SME Profile (Business Questionnaire) submissions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db_sync import BaseSync


def _uuid() -> str:
    return str(uuid.uuid4())


class SmeProfileSubmission(BaseSync):
    __tablename__ = "sme_profile_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    user_email: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    pinfl_or_inn: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    sphere_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Snapshot of Руйхат-2 lookup at submission time (company_name, director,
    # turnovers, …). Stored as JSON so the schema doesn't need migration when
    # the lookup adds new fields.
    client_info: Mapped[dict | None] = mapped_column(JSON, default=None, nullable=True)

    # General form fields (extra free-form data the user entered alongside
    # the auto-filled lookup). Optional.
    general_form: Mapped[dict | None] = mapped_column(JSON, default=None, nullable=True)

    # Sphere-by-sphere answers — list of {sphere_number, category_id,
    # category_name_ru/uz, answers: [{question_id, question_text_ru/uz,
    # answer}, ...]}.
    spheres: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
