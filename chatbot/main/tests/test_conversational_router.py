"""Conversational intent router tests.

The router runs *before* the SQL planner. Greeting, capability, help, and
out-of-scope intents must be answered locally without DB or LLM contact.
"""

from __future__ import annotations

import pytest

from cerr_chatbot.query.conversational_router import (
    CAPABILITY_REPLY,
    GREETING_REPLY,
    HELP_REPLY,
    OUT_OF_SCOPE_REPLY,
    classify,
)


@pytest.mark.parametrize(
    "msg",
    [
        "Salom",
        "  salom!  ",
        "assalomu alaykum",
        "Assalomu alaykum.",
        "hello",
        "Hi",
        "Privet",
        "Xayrli kun",
    ],
)
def test_pure_greeting_returns_greeting_intent(msg: str) -> None:
    res = classify(msg)
    assert res.kind == "greeting"
    assert res.user_message == GREETING_REPLY


def test_greeting_reply_is_uzbek_latin_and_self_descriptive() -> None:
    assert "Assalomu alaykum" in GREETING_REPLY
    assert "viloyat" in GREETING_REPLY.lower()
    assert "mahalla" in GREETING_REPLY.lower()


def test_greeting_with_followup_question_is_analytical() -> None:
    """Greeting glued onto an analytical question must not short-circuit."""
    res = classify("Salom, qaysi viloyatda aholi eng ko'p?")
    assert res.kind == "analytical"


@pytest.mark.parametrize(
    "msg",
    [
        "nimalarni qila olasan?",
        "Sen kim san?",
        "What can you do?",
        "Who are you?",
        "Chto ti umeesh",
    ],
)
def test_capability_questions_route_to_capability(msg: str) -> None:
    res = classify(msg)
    assert res.kind == "capability"
    assert res.user_message == CAPABILITY_REPLY


@pytest.mark.parametrize(
    "msg",
    [
        "Misol ko'rsat",
        "namuna bering",
        "Yordam",
        "help me",
        "Show me an example",
    ],
)
def test_help_questions_route_to_help(msg: str) -> None:
    res = classify(msg)
    assert res.kind == "help"
    assert res.user_message == HELP_REPLY


@pytest.mark.parametrize(
    "msg",
    [
        "Bugun ob-havo qanday?",
        "Tashkentda weather?",
        "Eng yaxshi futbol jamoasi qaysi?",
        "Tell me a joke",
        "Kerakli retsept ber",
    ],
)
def test_out_of_scope_messages_route_to_out_of_scope(msg: str) -> None:
    res = classify(msg)
    assert res.kind == "out_of_scope"
    assert res.user_message == OUT_OF_SCOPE_REPLY


@pytest.mark.parametrize(
    "msg",
    [
        "Qaysi viloyatda aholi eng ko'p?",
        "Mahallalar reytingi eng past bo'lgan joylar",
        "industry_volume_bln_uzs bo'yicha eng yuqori 10 tuman",
        "Subsidiya arizalari bo'yicha qaysi dasturlar faol?",
    ],
)
def test_analytical_questions_pass_through(msg: str) -> None:
    res = classify(msg)
    assert res.kind == "analytical"
    assert res.user_message == ""
