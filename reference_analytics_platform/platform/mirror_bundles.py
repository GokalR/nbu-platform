"""
Mirror all Next.js static assets from ai.cerr.uz to clone/static/.
Reads URL list from recon_full.txt, fetches each unique /_next/* + root asset,
writes to mirroring path under clone/static/.
"""
import os
import re
import sys
import json
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
RECON_LOG = ROOT.parent / "recon_full.txt"
INDEX_RAW = ROOT.parent / "index_raw.txt"
ORIGIN = "http://ai.cerr.uz"

# Static URL prefixes to mirror (not API, not chat).
KEEP_PREFIXES = (
    "/_next/static/",
    "/_next/image",
    "/cerr_logo.png",
    "/favicon.ico",
)


def parse_urls(log_path: Path) -> list[str]:
    seen = set()
    urls = []
    rx = re.compile(r"\[GET\]\s+(\S+)\s+=>")
    for line in log_path.read_text(encoding="utf-8").splitlines():
        m = rx.search(line)
        if not m:
            continue
        url = m.group(1)
        if not url.startswith(ORIGIN):
            continue
        path = url[len(ORIGIN):]
        if not path.startswith(KEEP_PREFIXES):
            continue
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def url_to_local(url: str) -> Path:
    """Map remote URL → local path under STATIC_DIR.
    For /_next/image?url=... we save at the query-encoded leaf so the bundle's
    same URL string resolves to it.
    """
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    query = parsed.query

    if path == "/_next/image":
        # Encode params into a stable filename, store under _next/image/
        qs = urllib.parse.parse_qs(query)
        src = qs.get("url", ["unknown"])[0]
        w = qs.get("w", ["0"])[0]
        q = qs.get("q", ["75"])[0]
        leaf = f"{Path(src).stem}_w{w}_q{q}{Path(src).suffix or '.png'}"
        return STATIC_DIR / "_next" / "image" / leaf

    # /favicon.ico?cachebuster — drop the query (Windows can't have ? in filenames)
    rel = path.lstrip("/")
    return STATIC_DIR / rel


def main():
    if not RECON_LOG.exists():
        print(f"ERR: {RECON_LOG} missing — re-run playwright recon first.", file=sys.stderr)
        sys.exit(1)

    urls = parse_urls(RECON_LOG)
    print(f"[mirror] {len(urls)} unique static URLs queued")

    sess = requests.Session()
    sess.headers["User-Agent"] = "cerr-clone-mirror/1.0"

    manifest = []
    for i, url in enumerate(urls, 1):
        local = url_to_local(url)
        local.parent.mkdir(parents=True, exist_ok=True)
        try:
            r = sess.get(url, timeout=30)
            r.raise_for_status()
            local.write_bytes(r.content)
            manifest.append({"url": url, "local": str(local.relative_to(ROOT)), "bytes": len(r.content)})
            print(f"  [{i:2}/{len(urls)}] {len(r.content):>8}b  {url}")
        except Exception as e:
            print(f"  [{i:2}/{len(urls)}] FAIL {url}  {e}", file=sys.stderr)
        time.sleep(0.05)

    # Save index.html — strip the JSON-string wrapping playwright produced
    if INDEX_RAW.exists():
        raw = INDEX_RAW.read_text(encoding="utf-8")
        try:
            html = json.loads(raw)  # raw is a JSON-encoded string
        except Exception:
            html = raw
        (ROOT / "index.html").write_text(html, encoding="utf-8")
        print(f"[mirror] index.html written ({len(html)} chars)")

    (ROOT / "mirror_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[mirror] manifest -> {ROOT / 'mirror_manifest.json'}")


if __name__ == "__main__":
    main()
