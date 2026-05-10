"""Counts surfaced by the importer for CLI / test inspection."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ImportSummary:
    import_run_id: int = 0
    status: str = "running"
    files: int = 0
    regions: int = 0
    districts: int = 0
    mahallas: int = 0
    entity_kpis: int = 0
    district_macro_indicators: int = 0
    district_macro_points: int = 0
    district_rating_histogram_rows: int = 0
    mahalla_infrastructure_rows: int = 0
    mahalla_appeal_rows: int = 0
    mahalla_specialization_rows: int = 0
    mahalla_crop_rows: int = 0
    mahalla_subsidy_program_rows: int = 0
    mahalla_peer_factor_rows: int = 0
    issues_total: int = 0
    issues_by_severity: dict[str, int] = field(default_factory=dict)
    issues_by_code: dict[str, int] = field(default_factory=dict)
    error_message: str | None = None

    def add_issues(self, severities: list[str], codes: list[str]) -> None:
        self.issues_total += len(severities)
        sev = Counter(severities)
        cod = Counter(codes)
        for k, v in sev.items():
            self.issues_by_severity[k] = self.issues_by_severity.get(k, 0) + v
        for k, v in cod.items():
            self.issues_by_code[k] = self.issues_by_code.get(k, 0) + v
