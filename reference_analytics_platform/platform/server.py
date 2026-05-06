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
/* Hide CERR logo + "CERR · Mahalla Analytics" text (preserve layout). */
.brand,
.chat-empty-brand,
.chat-empty-tagline {
  visibility: hidden !important;
}
.brand img,
.chat-empty-logo-img {
  display: none !important;
}

/* NBU blue palette — overrides CERR's #002060 navy. */
:root, :host, body, body.dark {
  --gov-navy: #1e3a8a !important;
  --gov-primary: #1d4ed8 !important;
  --gov-mid: #60a5fa !important;
  --gov-pale: #dbeafe !important;
}
body:not(.dark) {
  --bg: #f5f7fa !important;
  --accent: #1d4ed8 !important;
  --accent-hover: #1e3a8a !important;
  --accent-bg: #1d4ed817 !important;
  --accent-bg-hi: #60a5fa24 !important;
  --accent-solid: #1e3a8a !important;
  --shadow-card: 0 1px 3px #1e3a8a0a, 0 8px 24px #1e3a8a0d, 0 0 0 1px #1e3a8a06 !important;
  --shadow-hero: 0 3px 10px #1e3a8a0d, 0 18px 46px #1e3a8a14, 0 0 0 1px #1e3a8a08 !important;
  --zebra: #1d4ed806 !important;
}
body.dark {
  --bg: #0c1733 !important;
  --bg-surface: #122149 !important;
  --bg-elevated: #1a2c5e !important;
  --accent: #60a5fa !important;
  --accent-bg: #60a5fa2e !important;
  --accent-bg-hi: #dbeafe33 !important;
  --shadow-card: 0 1px 4px #00000038, 0 8px 28px #0000004d, 0 0 0 1px #dbeafe0d !important;
}

/* Slightly more rounded surfaces for visual differentiation. */
.card { border-radius: 16px !important; }
.kpi  { border-radius: 14px !important; }
.hero { border-radius: 18px !important; }
.chip { border-radius: 999px !important; }
""".strip()


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
