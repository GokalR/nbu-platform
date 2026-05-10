"""Phase 4A: JSON importer (entities + KPIs + data quality issues).

Macro indicators, detail tables, geometries, and AI insights are NOT
imported in this phase.
"""

from cerr_chatbot.importer.runner import run_import
from cerr_chatbot.importer.summary import ImportSummary

__all__ = ["ImportSummary", "run_import"]
