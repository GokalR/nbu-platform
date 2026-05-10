"""Pre-SQL conversational intent router.

Classifies a raw user message into:
- greeting          (salom, assalomu alaykum, hello, ...)
- capability        ("nimalarni qila olasan", "what can you do")
- help              ("misol ko'rsat", "namuna", "example")
- out_of_scope      (clearly nothing to do with regional data)
- analytical        (default — let the SQL planner pipeline run)

Greeting / capability / help / out_of_scope are answered locally in Uzbek
Latin without calling the LLM planner or the database. `analytical` returns
no answer; the caller is expected to continue with planner+executor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ConversationKind = Literal[
    "greeting",
    "capability",
    "help",
    "out_of_scope",
    "analytical",
]


@dataclass(frozen=True)
class ConversationalResponse:
    kind: ConversationKind
    user_message: str = ""


# User-facing canned answers, Uzbek Latin. Generic, polite, no internal
# table or column names. Intentionally short — the AnswerNarrator (or
# deterministic composer) is reserved for SQL results.
GREETING_REPLY = (
    "Assalomu alaykum. Men viloyat, tuman va mahalla statistikasi bo'yicha "
    "savollarga javob beraman. Masalan: qaysi viloyatda aholi ko'p, qaysi "
    "tumanlarda biznes faolligi yuqori, yoki qaysi mahallalarda infratuzilma "
    "ko'rsatkichlari ajralib turadi."
)

CAPABILITY_REPLY = (
    "Quyidagi ma'lumotlar bo'yicha javob bera olaman:\n"
    "- Viloyatlar bo'yicha aholi, biznes, ishsizlik va reyting ko'rsatkichlari.\n"
    "- Tumanlar bo'yicha sanoat, eksport, investitsiya va byudjet ko'rsatkichlari.\n"
    "- Mahallalar bo'yicha infratuzilma (yo'l, suv, tibbiyot, maktab), "
    "murojaatlar, ixtisoslashuv, ekin maydonlari va subsidiya dasturlari.\n"
    "- Ma'lumot sifati muammolari (takror STIR yoki kodlar).\n"
    'Savolingizni oddiy tilda yozing, masalan: "Qaysi viloyatda aholi eng ko\'p?"'
)

HELP_REPLY = (
    "Misol uchun quyidagi savollarni so'rashingiz mumkin:\n"
    "- Qaysi viloyatlarda aholi eng ko'p?\n"
    "- Mahallalar reytingi eng past bo'lgan joylarni ko'rsat.\n"
    "- Tibbiyot muassasasigacha masofa eng uzoq bo'lgan mahalla qaysi?\n"
    "- Sanoat hajmi eng yuqori tumanlarni ko'rsat.\n"
    "- Subsidiya arizalari bo'yicha qaysi dasturlar faol?\n"
    "- Ma'lumotlarda takror STIR bormi?"
)

OUT_OF_SCOPE_REPLY = (
    "Bu savol mening ma'lumotlar to'plamimdan tashqarida. Men faqat O'zbekiston "
    "viloyat, tuman va mahalla statistikasi bo'yicha javob bera olaman. Iltimos, "
    "shu mavzudagi savol bering."
)


# Greetings: separate fixed phrases (substring match anywhere) and a single
# whole-word "salom" matcher so we don't trigger on "Assalomu" twice or on
# unrelated words containing the substring.
_GREETING_PHRASES: tuple[str, ...] = (
    "assalomu alaykum",
    "assalom alaykum",
    "salom alaykum",
    "vaalaykum assalom",
    "hayrli kun",
    "xayrli kun",
    "xayrli tong",
    "xayrli kech",
    "good morning",
    "good evening",
    "good afternoon",
)
_GREETING_WORDS: tuple[str, ...] = (
    "salom",
    "hello",
    "hi",
    "hey",
    "privet",
    "zdravstvuyte",
)

_CAPABILITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bnima(?:larni)?\b.*\b(qila|qilis[hь]|so'rash|so[’']rash|berish)", re.IGNORECASE),
    re.compile(r"\bnimaga\s+yorda(?:m\s+bera|m)\b", re.IGNORECASE),
    re.compile(r"\bsen\s+kim(?:san)?\b", re.IGNORECASE),
    re.compile(r"\bo'zing(ni)?\s+tanishtir", re.IGNORECASE),
    re.compile(r"\bwhat\s+can\s+you\s+do\b", re.IGNORECASE),
    re.compile(r"\bwho\s+are\s+you\b", re.IGNORECASE),
    re.compile(r"\bcapabilit", re.IGNORECASE),
    re.compile(r"\bchto\s+(?:ti|vy)\s+umee", re.IGNORECASE),
)

_HELP_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bmisol(?:lar)?\s+(?:ko'rsat|ber|keltir)", re.IGNORECASE),
    re.compile(r"\bnamuna(?:lar)?\b", re.IGNORECASE),
    re.compile(r"\byordam\b", re.IGNORECASE),
    re.compile(r"\bhelp\b", re.IGNORECASE),
    re.compile(r"\bexample(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bqanday\s+(?:savol|so'ra)", re.IGNORECASE),
)

# Domain hint words. If any of these appear, we treat the message as
# in-scope analytical even when out-of-scope keywords are present (e.g.
# "viloyat ob-havosi" — let planner handle/refuse).
_DOMAIN_HINTS: tuple[str, ...] = (
    "viloyat",
    "tuman",
    "mahalla",
    "aholi",
    "biznes",
    "tadbirkor",
    "korxon",
    "ishsiz",
    "bandlik",
    "reyting",
    "infratuzilma",
    "yo'l",
    "asfalt",
    "suv",
    "tibbiyot",
    "shifoxona",
    "poliklinika",
    "maktab",
    "bog'cha",
    "sport",
    "jinoyat",
    "ajrim",
    "divorce",
    "subsidiya",
    "ariza",
    "ixtisoslash",
    "specialization",
    "stir",
    "district_code",
    "sanoat",
    "eksport",
    "investitsiya",
    "byudjet",
    "qishloq",
    "ekin",
    "region",
    "district",
    "population",
    "rating",
)

# Out-of-scope topical markers. Match whole words/phrases only.
_OUT_OF_SCOPE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bob[-\s]?havo\b", re.IGNORECASE),
    re.compile(r"\bweather\b", re.IGNORECASE),
    re.compile(r"\bvalyuta\s+kurs", re.IGNORECASE),
    re.compile(r"\bcurrency\s+rate\b", re.IGNORECASE),
    re.compile(r"\bfutbol\b", re.IGNORECASE),
    re.compile(r"\bfootball\b", re.IGNORECASE),
    re.compile(r"\brecipe\b|\bretsept\b", re.IGNORECASE),
    re.compile(r"\bjoke\b|\blatifa\b|\bhazil\b", re.IGNORECASE),
    re.compile(r"\bpython\s+code\b|\bjavascript\b|\breact\b", re.IGNORECASE),
)

_WORD_RE = re.compile(r"[A-Za-z'’]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text)]


def _has_domain_hint(text_lower: str) -> bool:
    return any(h in text_lower for h in _DOMAIN_HINTS)


def _is_pure_greeting(text: str) -> bool:
    """True if the message is JUST a greeting (no analytical follow-up).

    A greeting embedded in a longer analytical question (e.g. "Salom, qaysi
    viloyatda aholi ko'p?") must NOT short-circuit; we only treat short
    greeting-only messages as the greeting intent.
    """
    text_lower = text.lower()
    for phrase in _GREETING_PHRASES:
        if phrase in text_lower:
            stripped = text_lower
            for p in _GREETING_PHRASES:
                stripped = stripped.replace(p, " ")
            stripped_tokens = [t for t in _tokens(stripped) if t not in _GREETING_WORDS]
            if not _has_domain_hint(stripped) and len(stripped_tokens) <= 2:
                return True
    toks = _tokens(text)
    return bool(toks) and all(t in _GREETING_WORDS for t in toks)


def classify(user_message: str) -> ConversationalResponse:
    text = (user_message or "").strip()
    if not text:
        return ConversationalResponse(kind="analytical")

    text_lower = text.lower()
    has_domain = _has_domain_hint(text_lower)

    if _is_pure_greeting(text):
        return ConversationalResponse(kind="greeting", user_message=GREETING_REPLY)

    if not has_domain:
        for pat in _CAPABILITY_PATTERNS:
            if pat.search(text):
                return ConversationalResponse(kind="capability", user_message=CAPABILITY_REPLY)
        for pat in _HELP_PATTERNS:
            if pat.search(text):
                return ConversationalResponse(kind="help", user_message=HELP_REPLY)
        for pat in _OUT_OF_SCOPE_PATTERNS:
            if pat.search(text):
                return ConversationalResponse(kind="out_of_scope", user_message=OUT_OF_SCOPE_REPLY)

    return ConversationalResponse(kind="analytical")


__all__ = [
    "CAPABILITY_REPLY",
    "ConversationKind",
    "ConversationalResponse",
    "GREETING_REPLY",
    "HELP_REPLY",
    "OUT_OF_SCOPE_REPLY",
    "classify",
]
