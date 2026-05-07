"""One-shot uploader: cerr_runs/ -> R2 bucket nbu-cerr-data.

Walks the local data tree, uploads each file with the right Content-Type,
parallelises across a thread pool, and skips files already present at the
same size. Idempotent — safe to re-run after a network blip.

Credentials come from env vars (set by the wrapper bash command); not
written to disk anywhere.

Skipped at the top level:
  - cerr_region_*.json  (standalone duplicates, not used by the backend)
  - .DS_Store / hidden files
"""
from __future__ import annotations

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

ROOT = Path("reference_analytics_platform/cerr_runs").resolve()
BUCKET = "nbu-cerr-data"
ENDPOINT = "https://ef8577cf87d4e1bcf38b212576d87ba2.r2.cloudflarestorage.com"
WORKERS = 16  # parallel uploads


def content_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "application/json; charset=utf-8"
    if suffix == ".geojson":
        return "application/geo+json; charset=utf-8"
    return "application/octet-stream"


def should_skip(path: Path) -> bool:
    name = path.name
    if name.startswith(".") or name.lower() == "thumbs.db":
        return True
    # Standalone top-level duplicates from the original Flask scrape — not used.
    if path.parent == ROOT and name.startswith("cerr_region_") and name.endswith(".json"):
        return True
    return False


def collect_files() -> list[tuple[Path, str]]:
    """Returns [(local_path, s3_key), ...]. s3_key uses forward slashes."""
    out: list[tuple[Path, str]] = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or should_skip(p):
            continue
        rel = p.relative_to(ROOT).as_posix()  # forward slashes
        out.append((p, rel))
    return out


def make_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(
            retries={"max_attempts": 5, "mode": "standard"},
            max_pool_connections=WORKERS * 2,
            signature_version="s3v4",
        ),
    )


def head_size(client, key: str) -> int | None:
    try:
        resp = client.head_object(Bucket=BUCKET, Key=key)
        return int(resp["ContentLength"])
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("404", "NoSuchKey", "NotFound"):
            return None
        raise


def upload_one(client, local: Path, key: str) -> tuple[str, str]:
    """Returns (key, status). status in {'uploaded', 'skipped', 'error:<msg>'}."""
    try:
        local_size = local.stat().st_size
        existing = head_size(client, key)
        if existing == local_size:
            return key, "skipped"
        client.upload_file(
            str(local), BUCKET, key,
            ExtraArgs={"ContentType": content_type_for(local)},
        )
        return key, "uploaded"
    except Exception as e:
        return key, f"error:{e}"


def main() -> int:
    if not ROOT.exists():
        print(f"ERROR: {ROOT} does not exist", file=sys.stderr)
        return 1
    if "R2_ACCESS_KEY_ID" not in os.environ or "R2_SECRET_ACCESS_KEY" not in os.environ:
        print("ERROR: R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY must be set", file=sys.stderr)
        return 1

    client = make_client()
    files = collect_files()
    total = len(files)
    total_bytes = sum(p.stat().st_size for p, _ in files)
    print(f"Discovered {total} files, {total_bytes / (1024**3):.2f} GiB total")
    print(f"Uploading to s3://{BUCKET}/  via {ENDPOINT}")
    print(f"Workers: {WORKERS}\n")

    uploaded = 0
    skipped = 0
    errors = 0
    bytes_done = 0
    t0 = time.time()
    last_print = t0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(upload_one, client, p, k): (p, k) for p, k in files}
        for fut in as_completed(futures):
            local, key = futures[fut]
            try:
                _, status = fut.result()
            except Exception as e:
                status = f"error:{e}"
            sz = local.stat().st_size
            if status == "uploaded":
                uploaded += 1
                bytes_done += sz
            elif status == "skipped":
                skipped += 1
                bytes_done += sz
            else:
                errors += 1
                print(f"  ERR {key}: {status}", flush=True)

            now = time.time()
            done = uploaded + skipped + errors
            if now - last_print > 3 or done == total:
                rate = bytes_done / max(now - t0, 0.001) / (1024 * 1024)
                pct = 100 * done / total
                print(
                    f"  [{done:>4}/{total}] {pct:5.1f}%  "
                    f"up={uploaded} skip={skipped} err={errors}  "
                    f"{bytes_done / (1024**3):.2f} GiB  "
                    f"{rate:.1f} MiB/s",
                    flush=True,
                )
                last_print = now

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s — uploaded={uploaded} skipped={skipped} errors={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
