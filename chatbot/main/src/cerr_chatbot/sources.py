"""Source data discovery.

Locates cerr_region_*.json files under the configured source dir.
Read-only: never modifies, copies, or rewrites source JSON.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from cerr_chatbot.config import Settings, get_settings

_REGION_FILE_RE = re.compile(r"^cerr_region_(?P<region_id>\d+)\.json$")


@dataclass(frozen=True)
class RegionFile:
    region_id: int
    path: Path
    size_bytes: int


def _resolve_source_dir(settings: Settings) -> Path:
    raw = settings.cerr_source_dir
    return raw if raw.is_absolute() else (Path.cwd() / raw).resolve()


def discover_region_files(settings: Settings | None = None) -> list[RegionFile]:
    """Return RegionFile entries sorted by region_id.

    Raises FileNotFoundError if the source dir is missing.
    Empty list is a valid result (caller decides whether that is an error).
    """
    cfg = settings or get_settings()
    source_dir = _resolve_source_dir(cfg)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source dir not found: {source_dir}")

    found: list[RegionFile] = []
    for entry in source_dir.iterdir():
        if not entry.is_file():
            continue
        match = _REGION_FILE_RE.match(entry.name)
        if not match:
            continue
        found.append(
            RegionFile(
                region_id=int(match.group("region_id")),
                path=entry,
                size_bytes=entry.stat().st_size,
            )
        )
    found.sort(key=lambda r: r.region_id)
    return found
