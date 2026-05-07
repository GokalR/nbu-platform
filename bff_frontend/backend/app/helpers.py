"""Shared helpers for education route handlers."""

from __future__ import annotations

from typing import Any

from .config import get_settings


def translate_field(field: Any, lang: str) -> str:
    """Pick the right language from a {ru: ..., uz: ...} dict, or return as-is."""
    if isinstance(field, dict):
        return field.get(lang, field.get("ru", ""))
    return field or ""


def asset_url(path: str | None) -> str | None:
    """Prepend VIDEO_BASE_URL to relative paths."""
    if not path:
        return path
    if path.startswith("http"):
        return path
    base = get_settings().video_base_url_stripped
    return f"{base}{path}" if base else path


def translate_content(obj: Any, lang: str) -> Any:
    """Recursively resolve {ru, uz} dicts in nested content (quiz/flashcard JSON)."""
    if isinstance(obj, dict):
        if "ru" in obj and "uz" in obj and len(obj) == 2:
            return obj.get(lang, obj.get("ru", ""))
        return {k: translate_content(v, lang) for k, v in obj.items()}
    if isinstance(obj, list):
        return [translate_content(item, lang) for item in obj]
    return obj
