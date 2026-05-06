"""CERR Mahalla Analytics v2 — read-only file-backed data layer.

Mirrors the endpoints originally served by reference_analytics_platform/platform/server.py
but adapted for FastAPI and lazy-loading: at startup we only scan the small per-region
summary.json + region.json files (~28 files, a few hundred KB total). Heavier per-district
files (district.json, mahallas.json, geo.geojson) are loaded on first request and cached
in memory for the process lifetime.

Coordinates stay in WGS84 (lon/lat) — MapLibre GL consumes them natively, so unlike the
original Flask server we do NOT reproject to Web Mercator.
"""
from __future__ import annotations

import json
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..config import get_settings


class CerrDataIndex:
    """Lazy index over the cerr_runs/ JSON tree."""

    def __init__(self, data_root: Path):
        self.data_root = data_root
        self._lock = threading.Lock()
        self._loaded = False
        # region_code -> {code, name, mahalla_count, dir}
        self.regions: dict[int, dict[str, Any]] = {}
        # ordered list for /api/cerr/regions
        self.regions_ordered: list[dict[str, Any]] = []
        # district_code -> {code, name, region_code, region_name, mahalla_count, dir}
        self.districts: dict[int, dict[str, Any]] = {}
        # region_code -> [district summary]
        self.region_districts: dict[int, list[dict[str, Any]]] = {}

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            self._scan()
            self._loaded = True

    def _scan(self) -> None:
        if not self.data_root.exists():
            return
        for region_dir in sorted(self.data_root.iterdir()):
            if not region_dir.is_dir():
                continue
            summary_p = region_dir / "summary.json"
            region_p = region_dir / "region.json"
            if not summary_p.exists():
                continue
            try:
                summary = json.loads(summary_p.read_text(encoding="utf-8"))
            except Exception:
                continue
            region_code = int(summary["region_code"])
            region_name = summary["region_name"]
            mahalla_count = sum(d.get("mahalla_count", 0) for d in summary.get("districts", []))
            if region_p.exists():
                try:
                    rdata = json.loads(region_p.read_text(encoding="utf-8"))
                    mahalla_count = rdata.get("region_mahalla_count", mahalla_count)
                except Exception:
                    pass
            entry = {
                "code": region_code,
                "name": region_name,
                "mahalla_count": mahalla_count,
                "districts_count": len(summary.get("districts", [])),
                "dir": region_dir,
            }
            self.regions[region_code] = entry

            districts_dir = region_dir / "districts"
            district_list: list[dict[str, Any]] = []
            if districts_dir.exists():
                for d in summary.get("districts", []):
                    code = int(d["code"])
                    slug = d["slug"]
                    dist_dir = districts_dir / f"{code}_{slug}"
                    if not dist_dir.exists():
                        continue
                    drec = {
                        "code": code,
                        "name": d["name"],
                        "region_code": region_code,
                        "region_name": region_name,
                        "mahalla_count": d.get("mahalla_count", 0),
                        "has_macro": d.get("has_macro", False),
                        "has_geo": d.get("has_geo", False),
                        "dir": dist_dir,
                    }
                    self.districts[code] = drec
                    district_list.append({k: v for k, v in drec.items() if k != "dir"})
            self.region_districts[region_code] = district_list

        self.regions_ordered = sorted(
            ({k: v for k, v in r.items() if k != "dir"} for r in self.regions.values()),
            key=lambda r: r["name"],
        )

    # ------------------------------------------------------------------
    # Public read API
    # ------------------------------------------------------------------

    def list_regions(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return self.regions_ordered

    def get_region(self, region_code: int) -> dict[str, Any] | None:
        self._ensure_loaded()
        r = self.regions.get(region_code)
        if not r:
            return None
        return {k: v for k, v in r.items() if k != "dir"}

    def get_region_overview(self, region_code: int) -> dict[str, Any] | None:
        self._ensure_loaded()
        r = self.regions.get(region_code)
        if not r:
            return None
        p = r["dir"] / "region.json"
        if not p.exists():
            return None
        data = _read_json_cached(str(p))
        return data.get("overview") or {}

    def list_region_districts(self, region_code: int) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return self.region_districts.get(region_code, [])

    def get_district(self, district_code: int) -> dict[str, Any] | None:
        self._ensure_loaded()
        d = self.districts.get(district_code)
        if not d:
            return None
        return {k: v for k, v in d.items() if k != "dir"}

    def get_district_overview(self, district_code: int) -> dict[str, Any] | None:
        self._ensure_loaded()
        d = self.districts.get(district_code)
        if not d:
            return None
        p = d["dir"] / "district.json"
        if not p.exists():
            return None
        data = _read_json_cached(str(p))
        return data.get("overview") or {}

    def get_district_macro(self, district_code: int) -> dict[str, Any] | None:
        self._ensure_loaded()
        d = self.districts.get(district_code)
        if not d:
            return None
        p = d["dir"] / "district.json"
        if not p.exists():
            return None
        data = _read_json_cached(str(p))
        return data.get("macro")

    def get_district_geo(self, district_code: int) -> dict[str, Any] | None:
        """Returns raw GeoJSON FeatureCollection in WGS84 (lon/lat)."""
        self._ensure_loaded()
        d = self.districts.get(district_code)
        if not d:
            return None
        p = d["dir"] / "geo.geojson"
        if not p.exists():
            return None
        return _read_json_cached(str(p))

    def list_district_mahallas(
        self, district_code: int, sort: str = "rating_asc", limit: int = 500
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()
        d = self.districts.get(district_code)
        if not d:
            return []
        sums = _district_mahalla_summaries(str(d["dir"]), d["region_code"], d["region_name"], d["name"], district_code)
        if sort == "rating_desc":
            arr = sorted(sums, key=lambda x: (x.get("rating_score") is None, -(x.get("rating_score") or 0)))
        else:
            arr = sorted(sums, key=lambda x: (x.get("rating_score") is None, x.get("rating_score") or 0))
        return arr[:limit]

    def search_mahallas(self, q: str, limit: int = 100) -> list[dict[str, Any]]:
        """Linear search across all districts. Triggers full mahalla load on first call."""
        self._ensure_loaded()
        ql = q.casefold().strip()
        if not ql:
            return []
        hits: list[dict[str, Any]] = []
        for code, d in self.districts.items():
            sums = _district_mahalla_summaries(str(d["dir"]), d["region_code"], d["region_name"], d["name"], code)
            for m in sums:
                name = (m.get("name") or "").casefold()
                stir = m.get("stir") or ""
                if ql in name or stir.startswith(q):
                    hits.append(m)
                    if len(hits) >= limit:
                        return hits
        return hits

    def get_mahalla_overview(self, stir: str) -> dict[str, Any] | None:
        ov = _mahalla_overview_lookup(self, stir)
        return ov

    def get_mahalla_ai_insights(self, stir: str) -> dict[str, Any] | None:
        ov = _mahalla_overview_lookup(self, stir)
        if ov is None:
            return None
        return ov.get("ai_insights")


# ----------------------------------------------------------------------
# Module-level caches — keyed by file path string so lru_cache stays valid
# across the process lifetime.
# ----------------------------------------------------------------------

@lru_cache(maxsize=2048)
def _read_json_cached(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


@lru_cache(maxsize=512)
def _district_mahalla_summaries(
    dist_dir: str, region_code: int, region_name: str, district_name: str, district_code: int
) -> list[dict[str, Any]]:
    """Summary list for a district's mahallas. Cached on first call."""
    p = Path(dist_dir) / "mahallas.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for m in data.get("mahallas", []):
        stir = str(m.get("stir") or "")
        if not stir:
            continue
        out.append({
            "stir": stir,
            "name": m.get("name"),
            "district_name": district_name,
            "region_name": region_name,
            "district_oktmo": district_code,
            "region_oktmo": region_code,
            "rating_score": m.get("rating_score"),
        })
    return out


def _mahalla_overview_lookup(idx: CerrDataIndex, stir: str) -> dict[str, Any] | None:
    """Find a mahalla's full overview by its STIR. Walks districts on demand."""
    idx._ensure_loaded()
    for code, d in idx.districts.items():
        p = Path(d["dir"]) / "mahallas.json"
        if not p.exists():
            continue
        try:
            data = _read_json_cached(str(p))
        except Exception:
            continue
        for m in data.get("mahallas", []):
            if str(m.get("stir") or "") != stir:
                continue
            ov = m.get("overview")
            if ov is None:
                return None
            if "ai_insights" not in ov and m.get("ai_insights") is not None:
                ov = dict(ov)
                ov["ai_insights"] = m["ai_insights"]
            return ov
    return None


# ----------------------------------------------------------------------
# Singleton accessor
# ----------------------------------------------------------------------

_singleton: CerrDataIndex | None = None
_singleton_lock = threading.Lock()


def get_cerr_index() -> CerrDataIndex:
    global _singleton
    if _singleton is not None:
        return _singleton
    with _singleton_lock:
        if _singleton is None:
            root = Path(get_settings().cerr_data_root_resolved)
            _singleton = CerrDataIndex(root)
    return _singleton
