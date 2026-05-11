"""PostgreSQL schema (Phase 3 baseline).

Public surface: `Base.metadata` and the model classes. The package contains
no data-loading logic - the importer is a later phase.
"""

from cerr_chatbot.db.base import NAMING_CONVENTION, Base, JsonbType
from cerr_chatbot.db.models import (
    BusinessCompany,
    BusinessImport,
    BusinessImportSummary,
    DataQualityIssue,
    District,
    DistrictGeometry,
    DistrictMacroIndicator,
    DistrictMacroPoint,
    DistrictRatingHistogram,
    EntityAiInsight,
    EntityKpi,
    ImportRun,
    Mahalla,
    MahallaAppealRow,
    MahallaCropSeason,
    MahallaInfrastructureRow,
    MahallaPeerFactor,
    MahallaSpecializationItem,
    MahallaSubsidyProgram,
    Region,
    RegionGeometry,
    SourceRegionFile,
    TnvedCategory,
)

__all__ = [
    "Base",
    "BusinessCompany",
    "BusinessImport",
    "BusinessImportSummary",
    "DataQualityIssue",
    "District",
    "DistrictGeometry",
    "DistrictMacroIndicator",
    "DistrictMacroPoint",
    "DistrictRatingHistogram",
    "EntityAiInsight",
    "EntityKpi",
    "ImportRun",
    "JsonbType",
    "Mahalla",
    "MahallaAppealRow",
    "MahallaCropSeason",
    "MahallaInfrastructureRow",
    "MahallaPeerFactor",
    "MahallaSpecializationItem",
    "MahallaSubsidyProgram",
    "NAMING_CONVENTION",
    "Region",
    "RegionGeometry",
    "SourceRegionFile",
    "TnvedCategory",
]
