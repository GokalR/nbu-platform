"""Profile result models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FieldProfile(BaseModel):
    path: str
    observed_types: list[str] = Field(default_factory=list)
    presence_count: int = 0
    null_count: int = 0
    example_values: list[Any] = Field(default_factory=list)
    proposed_column_name: str | None = None
    proposed_table_group: str | None = None
    semantic_description: str | None = None
    is_ignored: bool = False
    ignored_reason: str | None = None
    notes_or_warnings: list[str] = Field(default_factory=list)


class EntityCounts(BaseModel):
    region_files: int = 0
    regions: int = 0
    districts: int = 0
    mahallas: int = 0


class ProfileReport(BaseModel):
    run_at: str
    source_dir: str
    source_files: list[str]
    entity_counts: EntityCounts
    field_paths: list[FieldProfile] = Field(default_factory=list)
    catalog_coverage: dict[str, int] = Field(default_factory=dict)
