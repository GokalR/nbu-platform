"""
One-time ingestion script.

Run from the `backend/` directory:
    python -m app.services.regional_chat.ingest

Creates an OpenAI vector store, uploads the 14 regional MD files with per-file
metadata (viloyat_code, viloyat_latin, viloyat_cyrillic), waits until indexing
finishes, and prints the resulting VECTOR_STORE_ID.

Then add the printed line to your env:
    VECTOR_STORE_ID=vs_xxxxxxxxxxxxxxxx
"""
from __future__ import annotations
import os
import sys
import time

from openai import OpenAI

# Allow running this file directly (`python ingest.py`) by ensuring the
# `backend/` package root is on sys.path.
if __package__ in (None, ""):
    HERE = os.path.dirname(os.path.abspath(__file__))
    BACKEND_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if BACKEND_ROOT not in sys.path:
        sys.path.insert(0, BACKEND_ROOT)

from app.config import get_settings
from app.services.regional_chat.registry import RAG_DIR, VILOYATS

VECTOR_STORE_NAME = os.getenv("VECTOR_STORE_NAME", "uzbekistan-regional-analytics")

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _vs_api(client: OpenAI):
    if hasattr(client, "vector_stores"):
        return client.vector_stores
    return client.beta.vector_stores


def _safe_filename(viloyat: dict) -> str:
    base = viloyat["name_latin"].replace("'", "").replace(" ", "_")
    return f"{viloyat['code']}_{base}.md"


def main() -> None:
    settings = get_settings()
    api_key = settings.openai_api_key_clean
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not configured. Set it in your env first.")

    existing = settings.vector_store_id_clean
    if existing:
        print(f"Note: VECTOR_STORE_ID already set: {existing}")
        print("This script will create a NEW vector store. Replace the env var afterwards "
              "if you want to use the new one.")
        print()

    # Sanity: every md exists.
    for v in VILOYATS:
        p = RAG_DIR / v["file"]
        if not p.exists():
            raise SystemExit(f"Missing md: {p}")

    client = OpenAI(api_key=api_key)
    vs_api = _vs_api(client)

    print(f"Creating vector store '{VECTOR_STORE_NAME}'...")
    vs = vs_api.create(name=VECTOR_STORE_NAME)
    print(f"  vector_store id: {vs.id}")
    print()

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
    print("Add that line to your env, then restart uvicorn.")
    print("=" * 60)


if __name__ == "__main__":
    main()
