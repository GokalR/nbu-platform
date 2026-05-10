"""Phase 6E.1: scrub the old CERR brand acronym from public surfaces.

Allow lowercase `cerr_chatbot` (Python package name) and lowercase
`cerr_runs` / `cerr_region_*.json` (file-name convention from the source
pipeline). Only the uppercase brand acronym `CERR` is forbidden in
user-facing text.
"""

from __future__ import annotations

import re
from pathlib import Path

PUBLIC_FILES: tuple[str, ...] = (
    "README.md",
    "pyproject.toml",
    ".env.example",
    "docs/ARCHITECTURE.md",
    "docs/SCHEMA.md",
    "docs/SEMANTIC_VIEWS.md",
)

_BRAND_PAT = re.compile(r"\bCERR\b")


def test_no_brand_acronym_in_public_files() -> None:
    bad: list[tuple[str, int, str]] = []
    for f in PUBLIC_FILES:
        text = Path(f).read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if _BRAND_PAT.search(line):
                bad.append((f, i, line.strip()))
    assert not bad, f"forbidden CERR brand mention: {bad}"


def test_no_brand_acronym_in_cli_help_or_user_strings() -> None:
    """CLI prints + argparse description must not carry the old brand."""
    cli_text = Path("src/cerr_chatbot/cli.py").read_text(encoding="utf-8")
    # Check only print(...) lines and argparse description= line.
    lines = cli_text.splitlines()
    user_facing = [ln for ln in lines if "print(" in ln or "description=" in ln]
    bad = [ln.strip() for ln in user_facing if _BRAND_PAT.search(ln)]
    assert not bad, f"CERR in user-facing CLI text: {bad}"


def test_pyproject_description_neutral() -> None:
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "Regional analytics chatbot" in text
    assert not _BRAND_PAT.search(text)


def test_readme_status_section_is_current() -> None:
    text_lower = Path("README.md").read_text(encoding="utf-8").lower()
    assert "semantic sql views" in text_lower
    assert "sql safety guard" in text_lower or "sql guard" in text_lower
    assert "answer composer" in text_lower
    assert "foundation phase only" not in text_lower
