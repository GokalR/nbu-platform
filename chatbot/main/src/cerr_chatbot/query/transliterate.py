"""Deterministic Uzbek Cyrillic → Uzbek Latin transliteration.

Used as the last step before final Answer.text leaves the narrator. The
prompt asks the LLM to transliterate, but model compliance is unreliable
across runs; this server-side pass guarantees no Cyrillic characters reach
the user when the source row data was Cyrillic.

Scope: pure string transformation. Does NOT touch SQL, DB, evidence rows,
debug notes — only the user-facing markdown answer.

Notes on the mapping:
- Multi-character outputs use the official Uzbek Latin orthography:
  Ғ→G' / ғ→g', Ў→O' / ў→o', Ъ→' (apostrophe), Ь→'' (drops in modern Uzbek
  Latin; we render it as a doubled apostrophe so the source intent is
  preserved without losing a character).
- Ye/ye for Е/е is used at the start of a word and right after a vowel,
  Cyrillic special character (ъ, ь) or whitespace; otherwise E/e. This
  matches modern Uzbek Latin practice (Eshmat, but Yelena, Yevropa).
- Ц/ц → Ts/ts. Modern Uzbek Latin sometimes uses S; Ts is unambiguous.
- Markdown table pipes, numbers, punctuation, ASCII letters all pass
  through unchanged.
"""

from __future__ import annotations

# Most letters are 1:1 (or 1:2). Build a single dispatch table; for the
# context-sensitive case (Е/е), we run a small post-process below.
_DIRECT_MAP: dict[str, str] = {
    "А": "A", "а": "a",
    "Б": "B", "б": "b",
    "В": "V", "в": "v",
    "Г": "G", "г": "g",
    "Ғ": "G'", "ғ": "g'",
    "Д": "D", "д": "d",
    # Е / е handled in the post-process so we can decide E vs Ye by context.
    "Ё": "Yo", "ё": "yo",
    "Ж": "J", "ж": "j",
    "З": "Z", "з": "z",
    "И": "I", "и": "i",
    "Й": "Y", "й": "y",
    "К": "K", "к": "k",
    "Қ": "Q", "қ": "q",
    "Л": "L", "л": "l",
    "М": "M", "м": "m",
    "Н": "N", "н": "n",
    "О": "O", "о": "o",
    "Ў": "O'", "ў": "o'",
    "П": "P", "п": "p",
    "Р": "R", "р": "r",
    "С": "S", "с": "s",
    "Т": "T", "т": "t",
    "У": "U", "у": "u",
    "Ф": "F", "ф": "f",
    "Х": "X", "х": "x",
    "Ҳ": "H", "ҳ": "h",
    "Ц": "Ts", "ц": "ts",
    "Ч": "Ch", "ч": "ch",
    "Ш": "Sh", "ш": "sh",
    "Ъ": "'", "ъ": "'",
    "Ь": "''", "ь": "''",
    "Э": "E", "э": "e",
    "Ю": "Yu", "ю": "yu",
    "Я": "Ya", "я": "ya",
    "Ы": "I", "ы": "i",
}

# Vowels in Cyrillic that promote a following Е/е to Ye/ye.
_CYR_VOWELS_LOWER: frozenset[str] = frozenset("аеёиоуыэюяўӯ")
# Trigger characters BEFORE Е/е that should produce Ye/ye:
#   - line start
#   - whitespace
#   - any Cyrillic vowel (including the lowercase mapping of Cyrillic
#     uppercase vowels)
#   - the soft/hard sign (ъ, ь)
_TRIGGER_CHARS: frozenset[str] = _CYR_VOWELS_LOWER | frozenset("ъь")


def _is_word_start(prev_char: str | None) -> bool:
    if prev_char is None:
        return True
    if prev_char.isspace():
        return True
    # Punctuation / markdown table pipes / parentheses also count as word
    # boundaries. Anything that is NOT a Cyrillic or Latin letter is
    # treated as a boundary.
    return not prev_char.isalpha()


def _ye_context(prev_char: str | None) -> bool:
    """True when Cyrillic Е/е at this position should become Ye/ye.

    Heuristic: word start, after a vowel, or after ъ/ь.
    """
    if _is_word_start(prev_char) or prev_char is None:
        return True
    return prev_char.lower() in _TRIGGER_CHARS


def uz_cyrillic_to_latin(text: str) -> str:
    """Transliterate Uzbek Cyrillic in `text` into Uzbek Latin.

    Non-Cyrillic characters (Latin, digits, punctuation, markdown table
    pipes, whitespace) pass through unchanged. The function is idempotent
    on already-Latin input.
    """
    if not text:
        return text

    out: list[str] = []
    prev: str | None = None
    for ch in text:
        if ch in ("Е", "е"):
            ye = _ye_context(prev)
            if ch == "Е":
                out.append("Ye" if ye else "E")
            else:
                out.append("ye" if ye else "e")
            prev = ch
            continue
        mapped = _DIRECT_MAP.get(ch)
        if mapped is None:
            out.append(ch)
        else:
            out.append(mapped)
        prev = ch
    return "".join(out)


__all__ = ["uz_cyrillic_to_latin"]
