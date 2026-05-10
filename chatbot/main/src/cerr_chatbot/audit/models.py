"""Audit result models. Pydantic for safe JSON serialization."""

from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["critical", "warning", "info"]


class Issue(BaseModel):
    severity: Severity
    code: str
    message: str
    region_code: int | None = None
    district_code: int | None = None
    stir: str | None = None
    source_file: str | None = None


class RegionCounts(BaseModel):
    region_code: int | None
    source_file: str
    declared_districts: int | None = None
    actual_districts: int = 0
    declared_mahallas: int | None = None
    actual_mahallas: int = 0


class ExpectedCounts(BaseModel):
    region_files: int = 14
    regions: int = 14
    districts: int = 212
    mahallas: int = 9088


class ActualCounts(BaseModel):
    region_files: int = 0
    regions: int = 0
    districts: int = 0
    mahallas: int = 0


class AuditReport(BaseModel):
    run_at: str
    source_dir: str
    source_files: list[str] = Field(default_factory=list)
    expected: ExpectedCounts = Field(default_factory=ExpectedCounts)
    actual: ActualCounts = Field(default_factory=ActualCounts)
    per_region: list[RegionCounts] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    issue_counts: dict[str, int] = Field(default_factory=dict)

    def finalize(self) -> None:
        c: Counter[str] = Counter(i.severity for i in self.issues)
        self.issue_counts = {
            "critical": c.get("critical", 0),
            "warning": c.get("warning", 0),
            "info": c.get("info", 0),
            "total": sum(c.values()),
        }

    @property
    def has_critical(self) -> bool:
        return any(i.severity == "critical" for i in self.issues)
