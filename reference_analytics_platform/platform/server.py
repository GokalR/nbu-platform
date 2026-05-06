"""CERR Mahalla Analytics — offline mock server, NBU AI HUB edition.

Serves the mirrored Next.js dashboard at the bound port. Data root is
configurable via CERR_DATA_ROOT and may be either:
  - A local filesystem path, OR
  - An HTTP(S) URL pointing at a static-asset host (e.g. Cloudflare R2:
    https://cerr-data.devgokal.com).

In HTTP mode a manifest.json at the root lists region directory names —
necessary because R2 (and any plain S3-style host exposed over HTTP) does
not provide key listings.

Auth endpoints (/api/auth/login, /api/auth/me) return a stub user so the
client bundle skips its login gate. AI Chat endpoints (/api/chats,
/api/models) return empty collections.

Geo coordinates are reprojected from WGS84 to Web Mercator EPSG:3857
because the bundled Next.js app expects Mercator.
"""
from __future__ import annotations

import json
import math
import os
import threading
from pathlib import Path
from typing import Any

from flask import Flask, request, send_from_directory, abort, make_response

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
INDEX_HTML = ROOT / "index.html"

app = Flask(__name__, static_folder=None)


# -----------------------------------------------------------------------------
# Reader: uniform JSON read over either a local path or an HTTP URL root,
# with in-process cache so each remote object is fetched at most once.
# -----------------------------------------------------------------------------

class _Reader:
    def __init__(self, root: str):
        self._is_http = root.startswith("http://") or root.startswith("https://")
        self._root = root.rstrip("/")
        self._cache: dict[str, Any] = {}
        self._cache_lock = threading.Lock()
        self._client = None
        if self._is_http:
            import httpx
            self._client = httpx.Client(timeout=30.0, follow_redirects=True)

    @property
    def is_http(self) -> bool:
        return self._is_http

    def read_json(self, rel: str) -> Any:
        rel = rel.lstrip("/")
        with self._cache_lock:
            if rel in self._cache:
                return self._cache[rel]
        data = self._fetch(rel)
        if data is not None:
            with self._cache_lock:
                self._cache[rel] = data
        return data

    def _fetch(self, rel: str) -> Any:
        if self._is_http:
            url = f"{self._root}/{rel}"
            try:
                r = self._client.get(url)
                if r.status_code == 404:
                    return None
                r.raise_for_status()
                return r.json()
            except Exception:
                return None
        p = Path(self._root) / rel
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_region_dirs(self) -> list[tuple[int, str]]:
        manifest = self.read_json("manifest.json")
        if manifest:
            out: list[tuple[int, str]] = []
            for r in manifest.get("regions", []):
                try:
                    out.append((int(r["code"]), r["dir"]))
                except (KeyError, ValueError, TypeError):
                    continue
            return out
        if self._is_http:
            return []
        root = Path(self._root)
        if not root.exists():
            return []
        out = []
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
            code_str = d.name.split("_", 1)[0]
            if code_str.isdigit():
                out.append((int(code_str), d.name))
        return out


# -----------------------------------------------------------------------------
# Index — built lazily on first request.
# -----------------------------------------------------------------------------

class DataIndex:
    def __init__(self, root: str):
        self.reader = _Reader(root)
        self._lock = threading.Lock()
        self._loaded = False
        # region_code -> {code, name, mahalla_count, rel_dir}
        self.regions_by_code: dict[int, dict[str, Any]] = {}
        # public-shaped region records for /api/regions
        self.regions: list[dict[str, Any]] = []
        # district_code -> {code, name, region_code, region_name, mahalla_count, rel_dir}
        self.districts: dict[int, dict[str, Any]] = {}
        # region_code -> [district summary dicts ready for /api/districts]
        self.region_districts: dict[int, list[dict[str, Any]]] = {}

    def ensure_loaded(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            self._scan()
            self._loaded = True

    def _scan(self) -> None:
        for code, dir_name in self.reader.list_region_dirs():
            summary = self.reader.read_json(f"{dir_name}/summary.json")
            if not summary:
                continue
            region = self.reader.read_json(f"{dir_name}/region.json")
            mahalla_count = sum(d.get("mahalla_count", 0) for d in summary.get("districts", []))
            if region:
                mahalla_count = region.get("region_mahalla_count", mahalla_count)
            region_name = summary["region_name"]
            self.regions_by_code[code] = {
                "code": code,
                "name": region_name,
                "mahalla_count": mahalla_count,
                "rel_dir": dir_name,
            }

            district_list: list[dict[str, Any]] = []
            for d in summary.get("districts", []):
                dcode = int(d["code"])
                slug = d["slug"]
                drec = {
                    "code": dcode,
                    "name": d["name"],
                    "region_code": code,
                    "region_name": region_name,
                    "mahalla_count": d.get("mahalla_count", 0),
                    "rel_dir": f"{dir_name}/districts/{dcode}_{slug}",
                }
                self.districts[dcode] = drec
                district_list.append({k: v for k, v in drec.items() if k != "rel_dir"})
            self.region_districts[code] = district_list

        self.regions = sorted(
            ({k: v for k, v in r.items() if k != "rel_dir"} for r in self.regions_by_code.values()),
            key=lambda r: r["name"],
        )
        print(f"[idx] regions={len(self.regions)} districts={len(self.districts)}", flush=True)

    def district_mahalla_summaries(self, dcode: int) -> list[dict[str, Any]]:
        d = self.districts.get(dcode)
        if not d:
            return []
        data = self.reader.read_json(f"{d['rel_dir']}/mahallas.json")
        if not data:
            return []
        out: list[dict[str, Any]] = []
        for m in data.get("mahallas", []):
            stir = str(m.get("stir") or "")
            if not stir:
                continue
            out.append({
                "stir": stir,
                "name": m.get("name"),
                "district_name": d["name"],
                "region_name": d["region_name"],
                "district_oktmo": dcode,
                "region_oktmo": d["region_code"],
                "rating_score": m.get("rating_score"),
            })
        out.sort(key=lambda x: (x.get("rating_score") is None, x.get("rating_score") or 0))
        return out

    def find_mahalla_overview(self, stir: str) -> dict[str, Any] | None:
        self.ensure_loaded()
        for d in self.districts.values():
            data = self.reader.read_json(f"{d['rel_dir']}/mahallas.json")
            if not data:
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


def _resolve_data_root() -> str:
    v = (os.environ.get("CERR_DATA_ROOT") or "").strip()
    if v:
        return v
    # Local fallback: scraper/cerr_runs alongside the repo (legacy layout) OR
    # the in-repo reference_analytics_platform/cerr_runs/ tree.
    legacy = ROOT.parent / "scraper" / "cerr_runs"
    if legacy.exists():
        return str(legacy)
    return str(ROOT.parent / "cerr_runs")


IDX = DataIndex(_resolve_data_root())


# -----------------------------------------------------------------------------
# Web Mercator reprojection (EPSG:4326 -> EPSG:3857) for /geo/{D}.json
# -----------------------------------------------------------------------------

R = 6378137.0

def lonlat_to_merc(lon: float, lat: float) -> list[float]:
    x = R * math.radians(lon)
    y = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return [x, y]


def reproject_coords(coords):
    if isinstance(coords, list) and coords and isinstance(coords[0], (int, float)):
        if abs(coords[0]) <= 180 and abs(coords[1]) <= 90:
            return lonlat_to_merc(coords[0], coords[1])
        return coords
    return [reproject_coords(c) for c in coords]


def reproject_feature(feat: dict) -> dict:
    geom = feat.get("geometry")
    if not geom:
        return feat
    new = dict(feat)
    new["geometry"] = {
        **geom,
        "coordinates": reproject_coords(geom.get("coordinates", [])),
    }
    return new


# -----------------------------------------------------------------------------
# JSON helper preserving UTF-8
# -----------------------------------------------------------------------------

def jbody(obj, status=200):
    body = json.dumps(obj, ensure_ascii=False)
    resp = make_response(body, status)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


# -----------------------------------------------------------------------------
# Allow being framed by NBU AI HUB. Without this, Pages/browsers refuse the
# iframe with "X-Frame-Options: DENY" by default.
# -----------------------------------------------------------------------------

ALLOWED_FRAME_ANCESTORS = os.environ.get(
    "FRAME_ANCESTORS",
    "'self' https://*.pages.dev https://*.up.railway.app http://localhost:5173",
)


@app.after_request
def add_frame_headers(resp):
    # Drop the legacy header; modern browsers honour CSP frame-ancestors.
    resp.headers.pop("X-Frame-Options", None)
    resp.headers["Content-Security-Policy"] = f"frame-ancestors {ALLOWED_FRAME_ANCESTORS};"
    return resp


# -----------------------------------------------------------------------------
# Auth bypass — stub user only so client proceeds. Not data.
# -----------------------------------------------------------------------------

@app.post("/api/auth/login")
def auth_login():
    resp = jbody({"ok": True, "user": {"username": "offline", "role": "user"}})
    resp.set_cookie("v3rag_session", "offline-stub", httponly=True, samesite="Lax", path="/")
    return resp


@app.get("/api/auth/me")
def auth_me():
    return jbody({"username": "offline", "user_id": "offline-clone", "role": "user"})


# AI Chat — out of scope.
@app.get("/api/chats")
def chats(): return jbody([])

@app.get("/api/models")
def models(): return jbody([])


# -----------------------------------------------------------------------------
# Geography / hierarchy
# -----------------------------------------------------------------------------

@app.get("/api/regions")
def regions():
    IDX.ensure_loaded()
    return jbody(IDX.regions)


@app.get("/api/districts")
def districts():
    IDX.ensure_loaded()
    region_code = request.args.get("region_code", type=int)
    if region_code is None:
        all_d = []
        for arr in IDX.region_districts.values():
            all_d.extend(arr)
        return jbody(all_d)
    return jbody(IDX.region_districts.get(region_code, []))


@app.get("/api/mahallas")
def mahallas():
    IDX.ensure_loaded()
    q = request.args.get("q")
    district_code = request.args.get("district_code", type=int)
    limit = request.args.get("limit", default=500, type=int)
    sort = request.args.get("sort", default="rating_asc")

    if q:
        ql = q.casefold()
        hits: list[dict[str, Any]] = []
        for dcode in IDX.districts:
            for m in IDX.district_mahalla_summaries(dcode):
                if (m.get("name") and ql in m["name"].casefold()) or m["stir"].startswith(q):
                    hits.append(m)
                    if len(hits) >= limit:
                        return jbody(hits)
        hits.sort(key=lambda x: (x.get("name") or "").casefold())
        return jbody(hits)

    if district_code is not None:
        arr = IDX.district_mahalla_summaries(district_code)
        if sort == "rating_desc":
            arr = sorted(arr, key=lambda x: (x.get("rating_score") is None, -(x.get("rating_score") or 0)))
        return jbody(arr[:limit])

    flat: list[dict[str, Any]] = []
    for dcode in IDX.districts:
        flat.extend(IDX.district_mahalla_summaries(dcode))
        if len(flat) >= limit:
            break
    return jbody(flat[:limit])


# -----------------------------------------------------------------------------
# Entity endpoints
# -----------------------------------------------------------------------------

@app.get("/api/entity/district/<int:district_code>/overview")
def district_overview(district_code: int):
    IDX.ensure_loaded()
    d = IDX.districts.get(district_code)
    if not d:
        abort(404)
    data = IDX.reader.read_json(f"{d['rel_dir']}/district.json")
    return jbody((data or {}).get("overview") or {})


@app.get("/api/entity/district/<int:district_code>/macro")
def district_macro(district_code: int):
    IDX.ensure_loaded()
    d = IDX.districts.get(district_code)
    if not d:
        abort(404)
    data = IDX.reader.read_json(f"{d['rel_dir']}/district.json")
    macro = (data or {}).get("macro")
    if macro is None:
        abort(404)
    return jbody(macro)


@app.get("/api/entity/mahalla/<stir>/overview")
def mahalla_overview(stir: str):
    ov = IDX.find_mahalla_overview(stir)
    if ov is None:
        abort(404)
    return jbody(ov)


@app.get("/api/entity/mahalla/<stir>/ai_insights")
def mahalla_ai(stir: str):
    ov = IDX.find_mahalla_overview(stir) or {}
    ai = ov.get("ai_insights")
    if ai is None:
        abort(404)
    return jbody(ai)


@app.get("/api/entity/region/<int:region_code>/overview")
def region_overview(region_code: int):
    IDX.ensure_loaded()
    r = IDX.regions_by_code.get(region_code)
    if not r:
        abort(404)
    data = IDX.reader.read_json(f"{r['rel_dir']}/region.json")
    return jbody((data or {}).get("overview") or {})


# -----------------------------------------------------------------------------
# GeoJSON — reproject WGS84 -> Web Mercator on the fly.
# -----------------------------------------------------------------------------

@app.get("/geo/<int:district_code>.json")
def geo(district_code: int):
    IDX.ensure_loaded()
    d = IDX.districts.get(district_code)
    if not d:
        abort(404)
    fc = IDX.reader.read_json(f"{d['rel_dir']}/geo.geojson")
    if fc is None:
        abort(404)
    fc = dict(fc)
    fc["features"] = [reproject_feature(f) for f in fc.get("features", [])]
    return jbody(fc)


# -----------------------------------------------------------------------------
# Static + SPA fallback
# -----------------------------------------------------------------------------

@app.get("/_next/image")
def _next_image():
    src = request.args.get("url", "")
    w = request.args.get("w", "48")
    q = request.args.get("q", "75")
    src_path = src.lstrip("/")
    stem = Path(src_path).stem
    suffix = Path(src_path).suffix or ".png"
    leaf = f"{stem}_w{w}_q{q}{suffix}"
    target = STATIC_DIR / "_next" / "image" / leaf
    if target.is_file():
        return send_from_directory(target.parent, target.name)
    fallback = STATIC_DIR / src_path
    if fallback.is_file():
        return send_from_directory(fallback.parent, fallback.name)
    abort(404)


@app.get("/_next/<path:rest>")
def _next_static(rest):
    target = STATIC_DIR / "_next" / rest
    if target.is_file():
        return send_from_directory(target.parent, target.name)
    abort(404)


# A 1x1 transparent PNG — served instead of the CERR logo so the bundle's
# <img> tags resolve cleanly but render nothing visible.
import base64 as _b64
TRANSPARENT_PNG = _b64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


@app.get("/cerr_logo.png")
def logo():
    resp = make_response(TRANSPARENT_PNG)
    resp.headers["Content-Type"] = "image/png"
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp


@app.get("/favicon.ico")
def favicon():
    return send_from_directory(STATIC_DIR, "favicon.ico")


# -----------------------------------------------------------------------------
# Custom CSS — overrides CERR's palette with NBU blue, hides the CERR brand
# (logo + "CERR · Mahalla Analytics" text) and the chat empty-state CERR
# branding. Loaded after the bundle's own stylesheet so :root overrides win.
# -----------------------------------------------------------------------------

CUSTOM_CSS = """
/* ============================================================
   NBU AI HUB style overrides on top of the CERR bundle.
   - Removes top bar (.pg-top) and AI Chat content (.chat-shell)
   - Flips dashboard grid so the mahalla sidebar lives on the RIGHT
   - Adopts NBU's lighter, flatter look: slate-50 background, white
     cards with subtle shadows, blue-700 accents, rounded corners.
   ============================================================ */

/* 1. Hide the top bar visually but KEEP it in the DOM at zero height —
      our boot script needs to click the (invisible) Dashboard tab to
      activate that view, so display:none is too aggressive. */
.pg-top {
  visibility: hidden !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  overflow: hidden !important;
  pointer-events: none !important;
}

/* 2. Hide the AI Chat view content. Dashboard becomes the only view. */
.chat-shell, .chat-empty, .chat-empty-brand, .chat-empty-tagline { display: none !important; }

/* 3. Tighten top padding now that the top bar is gone. */
.pg-view { padding-top: 14px !important; max-width: 1320px !important; }

/* 4. Flip dashboard layout: main content on the LEFT, mahalla
      sidebar on the RIGHT. .site is the dashboard root grid. */
.site {
  grid-template-columns: 1fr 320px !important;
  align-items: start !important;
  gap: 18px !important;
}
.site > .main    { order: 1 !important; min-width: 0; }
.site > .sidebar { order: 2 !important; }

/* 5. NBU palette — replaces CERR's #002060 navy with NBU blue-900 etc. */
:root, :host, body, body.dark {
  --gov-navy: #1e3a8a !important;
  --gov-primary: #1d4ed8 !important;
  --gov-mid: #60a5fa !important;
  --gov-pale: #dbeafe !important;
}

/* 6. NBU AI HUB look: slate-50 bg, flatter cards, softer shadows,
      lighter borders, more breathing room. */
body:not(.dark) {
  --bg: #f8fafc !important;
  --bg-surface: #ffffff !important;
  --bg-elevated: #f1f5f9 !important;
  --bg-input: #f8fafc !important;
  --border: #e2e8f0 !important;
  --border-subtle: #f1f5f9 !important;
  --text-primary: #0f172a !important;
  --text-secondary: #334155 !important;
  --text-muted: #64748b !important;
  --text-faint: #94a3b8 !important;
  --accent: #1d4ed8 !important;
  --accent-hover: #1e3a8a !important;
  --accent-bg: #1d4ed80f !important;
  --accent-bg-hi: #60a5fa1f !important;
  --accent-solid: #1e3a8a !important;
  --zebra: #1d4ed806 !important;
  /* Flatter NBU-style shadows replacing CERR's deep navy stack */
  --shadow-card: 0 1px 2px rgba(15, 23, 42, .04), 0 4px 12px rgba(15, 23, 42, .04) !important;
  --shadow-hero: 0 1px 3px rgba(15, 23, 42, .05), 0 8px 24px rgba(15, 23, 42, .06) !important;
}
body.dark {
  --bg: #0b1220 !important;
  --bg-surface: #111a2e !important;
  --bg-elevated: #1a253f !important;
  --border: #1e293b !important;
  --border-subtle: #172033 !important;
  --accent: #60a5fa !important;
  --accent-bg: #60a5fa2e !important;
  --accent-bg-hi: #dbeafe33 !important;
}

/* 7. Hero panel — kill CERR's radial gradient on the right side, use
      flat NBU-style with a thin accent strip. */
.hero {
  border-radius: 18px !important;
  border: 1px solid var(--border-subtle) !important;
}
.hero-right {
  background: var(--bg-surface) !important;
  border-left: 1px solid var(--border-subtle) !important;
}

/* 8. Cards — flat, thin border, hover lifts subtly. */
.card, .kpi {
  border: 1px solid var(--border-subtle) !important;
  border-radius: 16px !important;
  transition: border-color .15s, box-shadow .15s, transform .15s !important;
}
.kpi:hover {
  border-color: var(--gov-mid) !important;
  box-shadow: 0 6px 18px rgba(30, 58, 138, .08) !important;
  transform: translateY(-1px) !important;
}
.kpi { padding: 18px 20px !important; }

/* 9. Card heads — bolder, NBU-style. */
.card-head {
  padding: 16px 20px 10px !important;
  border-bottom: 1px solid var(--border-subtle) !important;
}
.card-head h3, .card-head .title {
  font-weight: 800 !important;
  letter-spacing: -0.015em !important;
  color: #0f172a !important;
}

/* 10. Right-side mahalla list — fresh card look. */
.sidebar {
  border-radius: 18px !important;
  border: 1px solid var(--border-subtle) !important;
  box-shadow: var(--shadow-card) !important;
  padding: 14px 0 10px !important;
}
.tree-node {
  margin: 1px 8px !important;
  padding: 8px 14px !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  color: #334155 !important;
}
.tree-node:hover {
  background: var(--bg-elevated) !important;
  color: var(--accent-solid) !important;
}
.tree-node[aria-current="true"], .tree-node.active, .tree-node[aria-selected="true"] {
  background: var(--accent-bg) !important;
  color: var(--accent-solid) !important;
  font-weight: 700 !important;
}

/* 11. Chips — NBU-rounded, high-contrast. */
.chip { border-radius: 999px !important; font-weight: 700 !important; }

/* 12. Mobile: stack instead of split */
@media (max-width: 1024px) {
  .site { grid-template-columns: 1fr !important; }
  .site > .sidebar { order: 0 !important; max-height: 360px !important; overflow-y: auto !important; }
}

/* ============================================================
   Polish pass — hides remaining CERR branding, normalises KPI
   heights so labels of different lengths don't break alignment,
   tightens number rendering with Geist Mono.
   ============================================================ */

/* 13. Right-sidebar header still showed an "MA · Mahalla Analytics"
       block — remove it. Also tighten search-row padding. */
.logo-row { display: none !important; }
.sidebar { padding: 10px 0 8px !important; }
.mahalla-search-row, .sidebar-search {
  margin: 4px 8px 8px !important;
  border-radius: 10px !important;
  background: var(--bg-input) !important;
  border: 1px solid var(--border-subtle) !important;
}

/* 14. KPI card heights — give every card the same minimum height so
       2-word and 5-word labels line up. Reserve a 2-line slot for
       the label and clamp anything longer. Values stay anchored to
       the bottom of the card. */
.kpi {
  min-height: 124px !important;
  padding: 16px 18px !important;
  align-items: stretch !important;
  grid-template-columns: 56px 1fr !important;
  gap: 14px !important;
}
.kpi-icon {
  align-self: center !important;
  width: 56px !important;
  height: 56px !important;
  border-radius: 14px !important;
}
.kpi-body {
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  min-width: 0 !important;
}
.kpi-label {
  font-size: 10.5px !important;
  letter-spacing: 0.06em !important;
  line-height: 1.35 !important;
  font-weight: 600 !important;
  color: var(--text-muted) !important;
  display: -webkit-box !important;
  -webkit-line-clamp: 2 !important;
  -webkit-box-orient: vertical !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  min-height: 28px !important;
}

/* 15. Numbers — Geist Mono for that tabular dashboard feel. */
.kpi-value,
.stat-value,
.delta,
.num,
.rank,
.peer-rank {
  font-family: var(--font-geist-mono, 'Geist Mono'), 'Geist Mono', ui-monospace, monospace !important;
  font-variant-numeric: tabular-nums !important;
  letter-spacing: -0.02em !important;
}
.kpi-value {
  font-size: 24px !important;
  font-weight: 800 !important;
  color: var(--text-primary) !important;
  line-height: 1.1 !important;
  margin-top: 4px !important;
}

/* 16. Delta pill alignment — sit on its own row right under the
       value, not jammed next to it. */
.kpi-foot { margin-top: 6px !important; }
.delta {
  font-size: 10.5px !important;
  font-weight: 700 !important;
  padding: 2px 8px !important;
}

/* 17. Rank display ("1 / 15") — make the slash and total readable. */
.kpi-value .rank-num,
.kpi-value > strong {
  font-size: 26px !important;
}
.kpi-value .rank-tot,
.kpi-value > span {
  font-size: 14px !important;
  color: var(--text-muted) !important;
  font-weight: 600 !important;
  margin-left: 2px !important;
}

/* 18. Section card headers — softer divider, NBU spacing. */
.card-head {
  padding: 14px 20px 10px !important;
  border-bottom: 1px solid var(--border-subtle) !important;
}
""".strip()


# Boot script: keep clicking the Dashboard tab on a short interval until it
# actually becomes active. The first click can land before React has hydrated
# its event handlers (no-op), so we retry every 100ms for up to ~12s, using
# both .click() and a real MouseEvent for resilience. Stops as soon as
# aria-selected="true" or .active confirms the tab is now active.
DASH_BOOT_SCRIPT = (
    "<script>(function(){"
    "let tries=0;"
    "function isActive(el){return el && (el.classList.contains('active')"
    " || el.getAttribute('aria-selected')==='true');}"
    "function clickHard(el){"
    "  try{el.click();}catch(e){}"
    "  try{"
    "    const ev=new MouseEvent('click',{bubbles:true,cancelable:true,view:window});"
    "    el.dispatchEvent(ev);"
    "  }catch(e){}"
    "}"
    "const t=setInterval(function(){"
    "  tries++;"
    "  const dash=document.querySelector('[data-testid=\"pg-tab-dash\"]');"
    "  if(!dash){if(tries>120){clearInterval(t);}return;}"
    "  if(isActive(dash)){clearInterval(t);return;}"
    "  clickHard(dash);"
    "  if(tries>120){clearInterval(t);}"
    "},100);"
    "})();</script>"
)


@app.get("/custom.css")
def custom_css():
    resp = make_response(CUSTOM_CSS)
    resp.headers["Content-Type"] = "text/css; charset=utf-8"
    resp.headers["Cache-Control"] = "public, max-age=300"
    return resp


URL_FIX_SNIPPET = (
    "<script>(function(){try{"
    "localStorage.setItem('v3rag.devAuth','1');"
    "localStorage.setItem('v3rag.devUser','offline');"
    "localStorage.setItem('v3rag.devRole','user');"
    "if(location.pathname==='/login'){history.replaceState(null,'','/');}"
    "}catch(e){}})();</script>"
    '<link rel="stylesheet" href="/custom.css">'
    + DASH_BOOT_SCRIPT
)


# Text replacements applied to every served HTML page. Runs after URL_FIX_SNIPPET
# injection. CSS hides these visually too — replacement is for screen readers
# / accessibility / page-source cleanliness.
HTML_REPLACEMENTS = [
    ("CERR · Mahalla Analytics", ""),
    ("Mahalla Analytics · Ўзбекистон Республикаси", ""),
    ("Mahalla Analytics — CERR", "Аналитика"),
    ("Mahalla-level socioeconomic analytics", "Региональная аналитика"),
    ('alt="CERR"', 'alt=""'),
    ('aria-label="CERR — Бош dashboard"', 'aria-label="Аналитика"'),
]


@app.get("/")
@app.get("/<path:_>")
def spa_fallback(_=None):
    if "_rsc" in request.args:
        abort(404)
    if not INDEX_HTML.exists():
        abort(500, "index.html missing")
    html = INDEX_HTML.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>" + URL_FIX_SNIPPET, 1)
    for needle, replacement in HTML_REPLACEMENTS:
        html = html.replace(needle, replacement)
    resp = make_response(html, 200)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.set_cookie("v3rag_session", "offline-stub", httponly=True, samesite="Lax", path="/")
    return resp


@app.get("/health")
def health():
    return jbody({"status": "ok", "data_root": IDX.reader._root, "is_http": IDX.reader.is_http})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"[server] http://{host}:{port}  (data root: {IDX.reader._root})", flush=True)
    try:
        from waitress import serve
        serve(app, host=host, port=port, threads=16)
    except ImportError:
        app.run(host=host, port=port, debug=False, threaded=True)
