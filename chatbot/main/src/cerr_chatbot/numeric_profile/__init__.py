"""Phase 2B2: numeric profiler for KPI / macro / peer / detail fields."""

from cerr_chatbot.numeric_profile.runner import (
    run_numeric_profile,
    write_json,
    write_markdown,
)
from cerr_chatbot.numeric_profile.stats import NumericStats, ValueBag, compute_stats

__all__ = [
    "NumericStats",
    "ValueBag",
    "compute_stats",
    "run_numeric_profile",
    "write_json",
    "write_markdown",
]
