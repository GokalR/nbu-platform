# CERR Mahalla Analytics Platform

Flask server hosting a mirrored Next.js dashboard for the CERR (Central Economic Reform Recommendations) mahalla-level analytics. Iframed by the main NBU AI Hub at `/regions-v2`.

> Top-level docs: [../README.md](../README.md), [../DEPLOYMENT.md](../DEPLOYMENT.md).

---

## What this is

A **separate Railway service**, deployed alongside the main `bff_frontend` backend. It serves:

- The pre-built Next.js bundle (`platform/index.html` + `platform/static/`)
- A small Flask shim (`platform/server.py`) that:
  - Stubs `/api/auth/*` so the bundled login gate is bypassed
  - Serves region/mahalla JSON from either a **local path** or an **HTTP URL** (R2)
  - Reprojects WGS84 coordinates → Web Mercator EPSG:3857 (the bundle expects Mercator)
  - Caches every JSON read in-process

---

## Layout

```
region_analytics_platform_template/
├── platform/
│   ├── server.py                # Flask app — entry point
│   ├── index.html               # mirrored Next.js shell
│   ├── static/                  # Next.js _next/ chunks, fonts, icons
│   ├── data/                    # local fallback data (small samples)
│   ├── mirror_bundles.py        # rebuild the local mirror from upstream (rare)
│   ├── mirror_manifest.json     # manifest of mirrored assets
│   ├── requirements.txt         # Flask, waitress, httpx
│   └── Procfile                 # web: python server.py
│
└── cerr_runs/                   # 1.4 GB scraped JSON (gitignored — lives in R2)
    ├── 1703_andijon-viloyati/
    ├── 1706_buxoro-viloyati/
    ├── … (14 viloyats)
    └── manifest.json            # required when CERR_DATA_ROOT points at HTTP
```

`cerr_runs/` is **not** committed — too large. It's mirrored to Cloudflare R2 bucket `nbu-cerr-data` (public domain `cerr-data.devgokal.com`).

---

## Run locally

```bash
cd region_analytics_platform_template/platform
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

### Pick a data source

**Option A — point at R2 (no local data needed):**

```bash
# PowerShell
$env:CERR_DATA_ROOT = "https://cerr-data.devgokal.com"
python server.py                                  # http://localhost:5000
```

**Option B — use the local `cerr_runs/`** (if you have downloaded it):

```bash
$env:CERR_DATA_ROOT = "$pwd\..\cerr_runs"
python server.py
```

If `CERR_DATA_ROOT` is unset, the server falls back to `../cerr_runs/` relative to itself.

### Hook it into the main frontend

In `bff_frontend/frontend/.env.local`:

```env
VITE_CERR_BUNDLE_URL=http://localhost:5000
```

Then `/regions-v2` in the main app will iframe this server.

---

## How the data flow works

```
Browser  ──iframe──▶  CERR Flask  ──fetch──▶  R2 (JSON)
                          │
                          ├── reprojects coords WGS84 → EPSG:3857
                          ├── caches in-process (per-key)
                          └── stubs /api/auth/me to skip login
```

When `CERR_DATA_ROOT` is an HTTP URL, R2 listing isn't possible (S3-style hosts don't expose key listings over plain HTTP), so the server reads `manifest.json` at the root to know which region directories exist.

---

## Re-uploading data to R2

Use the top-level [../upload_to_r2.py](../upload_to_r2.py):

```bash
$env:AWS_ACCESS_KEY_ID = "..."
$env:AWS_SECRET_ACCESS_KEY = "..."
python ../upload_to_r2.py            # idempotent — skips files at same size
```

Bucket: `nbu-cerr-data`. Endpoint: `https://ef8577cf87d4e1bcf38b212576d87ba2.r2.cloudflarestorage.com` (Cloudflare account ID is hardcoded).

---

## Deployment

Separate Railway service, root dir: `region_analytics_platform_template/platform/`.

| Setting | Value |
|---|---|
| Builder | Buildpack (auto-detects Python via `requirements.txt`) |
| Start | `python server.py` (Procfile) |
| Env var | `CERR_DATA_ROOT=https://cerr-data.devgokal.com` |
| Port | Railway injects `$PORT`; Flask binds to it |

Then in the **main** Pages project (frontend), set `VITE_CERR_BUNDLE_URL=https://<this-service>.up.railway.app` and redeploy.

---

## Troubleshooting

- **Blank iframe / "no regions"**: `CERR_DATA_ROOT` likely points at a path with no `manifest.json`. Either run `mirror_bundles.py` to regenerate, or fix the URL.
- **CORS errors on the iframe**: ensure the bundled service's responses don't set `X-Frame-Options: DENY`. The Flask code in `server.py` deliberately omits frame headers.
- **Coordinates appear in the wrong place**: the WGS84→Mercator reprojection happens in `server.py`. If a new dataset already uses Mercator, set the appropriate flag rather than double-reprojecting.
