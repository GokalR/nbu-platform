"""Pydantic schemas for the analytics backend."""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    finance: dict[str, Any] = Field(default_factory=dict)
    city_id: Optional[str] = None
    lang: str = "ru"


class SubmissionOut(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    profile: dict[str, Any]
    finance: dict[str, Any]
    city_id: Optional[str]
    lang: str

    class Config:
        from_attributes = True


class UploadOut(BaseModel):
    id: str
    kind: Literal["balance", "pnl"]
    original_filename: str
    size_bytes: int
    parsed: dict[str, Any]

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    id: str
    submission_id: str
    created_at: datetime
    model: str
    input_tokens: int
    output_tokens: int
    output: dict[str, Any]
    error: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    lang: Optional[str] = None
    model: Optional[str] = None
