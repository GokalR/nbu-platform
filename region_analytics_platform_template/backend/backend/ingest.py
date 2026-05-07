"""
One-time ingestion script.

Usage:
  python -m backend.ingest

Creates an OpenAI vector store, uploads the 14 regional MD files with per-file
metadata (viloyat_code, viloyat_latin, viloyat_cyrillic), waits until indexing finishes,
and prints the resulting VECTOR_STORE_ID.

After this finishes, add the id to your .env:
  VECTOR_STORE_ID=vs_xxxxxxxxxxxxxxxx
"""
from __future__ import annotations
import sys
import time
from openai import OpenAI

from config import (
    OPENAI_API_KEY, RAG_DIR, VILOYATS, VECTOR_STORE_NAME, VECTOR_STORE_ID,
)

# Force UTF-8 stdout on Windows console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _vs_api(client: OpenAI):
    """Return the vector_stores namespace, falling back to the beta path on older SDKs."""
    if hasattr(client, "vector_stores"):
        return client.vector_stores
    return client.beta.vector_stores


def _safe_filename(viloyat: dict) -> str:
    base = viloyat["name_latin"].replace("'", "").replace(" ", "_")
    return f"{viloyat['code']}_{base}.md"


def main() -> None:
    if VECTOR_STORE_ID:
        print(f"Note: VECTOR_STORE_ID already set in .env: {VECTOR_STORE_ID}")
        print("This script will create a NEW vector store. Replace the env var afterwards "
              "if you want to use the new one.")
        print()

    client = OpenAI(api_key=OPENAI_API_KEY)
    vs_api = _vs_api(client)

    print(f"Creating vector store '{VECTOR_STORE_NAME}'...")
    vs = vs_api.create(name=VECTOR_STORE_NAME)
    print(f"  vector_store id: {vs.id}")
    print()

    # Upload each file, then attach to the vector store with attributes.
    print("Uploading and attaching 14 files...")
    for i, v in enumerate(VILOYATS, 1):
        path = RAG_DIR / v["file"]
        safe = _safe_filename(v)
        print(f"  [{i:>2}/14] {safe}  ({path.stat().st_size:,} bytes)")
        with open(path, "rb") as fp:
            content = fp.read()
        f = client.files.create(file=(safe, content), purpose="assistants")
        vs_api.files.create(
            vector_store_id=vs.id,
            file_id=f.id,
            attributes={
                "viloyat_code": v["code"],
                "viloyat_latin": v["name_latin"],
                "viloyat_cyrillic": v["name_cyrillic"],
            },
        )

    # Wait for indexing.
    print()
    print("Waiting for indexing to complete...")
    while True:
        status = vs_api.retrieve(vs.id)
        c = status.file_counts
        print(
            f"  in_progress={c.in_progress}  completed={c.completed}  "
            f"failed={c.failed}  cancelled={c.cancelled}  total={c.total}"
        )
        if c.in_progress == 0:
            break
        time.sleep(3)

    print()
    print("=" * 60)
    print("DONE.")
    print(f"VECTOR_STORE_ID={vs.id}")
    print("Add that line to your .env, then restart uvicorn.")
    print("=" * 60)


if __name__ == "__main__":
    main()
