"""Generate manifest.json at the root of CERR_DATA_ROOT (local fs only).

R2 / any HTTP-static host doesn't expose key listings, so the data layer
needs an explicit manifest to know which region directories exist. This
script walks a local copy of cerr_runs/ and emits the manifest in-place.

Usage (from the repo root, default resolves to reference_analytics_platform/cerr_runs):
    python -m backend.scripts.build_cerr_manifest

Or override the path with an env var:
    CERR_DATA_ROOT=/some/other/cerr_runs python -m backend.scripts.build_cerr_manifest

Then upload the entire tree (manifest.json included) to your R2 bucket.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running as `python backend/scripts/build_cerr_manifest.py` too.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings  # noqa: E402


def main() -> int:
    root_str = get_settings().cerr_data_root_resolved
    if root_str.startswith("http://") or root_str.startswith("https://"):
        print(f"ERROR: CERR_DATA_ROOT is an HTTP URL ({root_str}); manifest must be built locally.", file=sys.stderr)
        return 2
    root = Path(root_str)
    if not root.exists() or not root.is_dir():
        print(f"ERROR: data root not found or not a directory: {root}", file=sys.stderr)
        return 1

    regions: list[dict[str, object]] = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        code_str = d.name.split("_", 1)[0]
        if not code_str.isdigit():
            continue
        # Sanity: skip dirs that don't look like a real region (no summary.json).
        if not (d / "summary.json").exists():
            print(f"  skip {d.name} (no summary.json)")
            continue
        regions.append({"code": int(code_str), "dir": d.name})
        print(f"  + {d.name}")

    manifest = {"version": 1, "regions": regions}
    out = root / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")
    print(f"  {len(regions)} regions indexed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
