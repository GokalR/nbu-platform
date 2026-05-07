"""
Deterministic question router.

Builds an in-memory index of all (viloyat, tuman, mahalla) names from the 14 MD files
on first call, then for each incoming question substring-matches against that index in
BOTH Cyrillic and Latin forms. Returns the list of viloyats that should receive the
question.

Why deterministic:
- Free (no LLM call).
- Instant (~1ms).
- Reliable: name appearing in the question is the strongest possible signal of relevance.

Behavior:
- If question matches names from N viloyats → fan out to those N only.
- If ZERO matches (global / cross-Uzbekistan query) → fan out to ALL 14.
"""
from __future__ import annotations
import re
from typing import Any

from .registry import RAG_DIR, VILOYATS


_CYR2LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'j',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 's',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': "'", 'ы': 'i', 'ь': '', 'э': 'e',
    'ю': 'yu', 'я': 'ya', 'ў': "o'", 'қ': 'q', 'ғ': "g'", 'ҳ': 'h',
}


def cyr_to_lat(s: str) -> str:
    return ''.join(_CYR2LAT.get(c, _CYR2LAT.get(c.lower(), c)) for c in s)


_APOS_VARIANTS = ["'", "’", "ʼ", "ʻ", "`", "´"]


def normalize(s: str) -> str:
    s = s.lower()
    for a in _APOS_VARIANTS:
        s = s.replace(a, "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s


_TUMAN_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*$", re.MULTILINE)
_MAHALLA_RE = re.compile(r"^####\s+\d+\.\s+(.+?)\s*$", re.MULTILINE)
_VIL_SUFFIX_RE = re.compile(
    r"\s+(вилояти|viloyati|шаҳри|shahri|республикаси|respublikasi|tumani|туман[иа]?)\s*$",
    re.IGNORECASE,
)

_INDEX: list[dict[str, Any]] | None = None


def build_index() -> list[dict[str, Any]]:
    global _INDEX
    if _INDEX is not None:
        return _INDEX

    index: list[dict[str, Any]] = []
    for v in VILOYATS:
        text = (RAG_DIR / v["file"]).read_text(encoding="utf-8")
        tumans = _TUMAN_RE.findall(text)
        mahallas = _MAHALLA_RE.findall(text)

        names: set[str] = set()
        for n in tumans + mahallas:
            n = n.strip()
            if not n:
                continue
            names.add(n)
            names.add(cyr_to_lat(n))
            stripped = _VIL_SUFFIX_RE.sub("", n).strip()
            if stripped:
                names.add(stripped)
                names.add(cyr_to_lat(stripped))

        for full in (v["name_cyrillic"], v["name_latin"]):
            names.add(full)
            short = _VIL_SUFFIX_RE.sub("", full).strip()
            if short:
                names.add(short)

        normalized = sorted(
            {normalize(n) for n in names if n and len(n) >= 4},
            key=lambda x: -len(x),
        )
        index.append({"viloyat": v, "names": normalized})

    _INDEX = index
    return _INDEX


def route(question: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (selected_viloyats, matched_terms).

    Empty match → returns ALL 14 viloyats (assume global query).
    """
    idx = build_index()
    q = normalize(question)

    selected: list[dict[str, Any]] = []
    matched_terms: list[str] = []
    seen_codes: set[str] = set()

    for entry in idx:
        for name in entry["names"]:
            if name in q:
                v = entry["viloyat"]
                if v["code"] not in seen_codes:
                    seen_codes.add(v["code"])
                    selected.append(v)
                    matched_terms.append(name)
                break

    if not selected:
        return list(VILOYATS), []
    return selected, matched_terms
