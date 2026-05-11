"""Real LLM adapter implementing the Planner protocol.

Boundary rules (enforced by tests):
- LlmPlanner does NOT touch the database.
- LlmPlanner does NOT execute SQL.
- LlmPlanner does NOT compose final answers.
- It only renders the planner prompt for `user_question`, calls the provider,
  and returns the raw model text. All validation/execution stays downstream.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.query.planner_prompt import build_planner_prompt, build_sql_prompt
from cerr_chatbot.query.schema_linker import (
    SchemaLinkParseError,
    build_schema_linking_prompt,
    parse_schema_linking_response,
)

log = logging.getLogger(__name__)


class LlmPlannerError(RuntimeError):
    """Provider failed, was misconfigured, or returned no text."""


# A provider call takes the resolved (model, prompt, api_key) and returns
# the raw model text. Tests pass a stub; default impl is selected by settings.
ProviderCall = Callable[[str, str, str], str]
# Streaming variant: yields token deltas as they arrive. The narrator uses
# this for SSE; planner/schema-linker still use ProviderCall (need full JSON).
StreamingProviderCall = Callable[[str, str, str], Iterator[str]]


@dataclass
class LlmPlanner:
    settings: Settings | None = None
    provider_call: ProviderCall | None = None
    log_full_prompt: bool = False  # opt-in; default off so user data does not hit logs

    def plan(self, user_question: str) -> str:
        cfg = self.settings or get_settings()
        provider, model, api_key = _resolve_provider(cfg, self.provider_call)
        prompt = build_planner_prompt(user_question)
        if self.log_full_prompt:
            log.info("planner prompt: %s", prompt)
        else:
            log.info("planner prompt built (%d chars)", len(prompt))

        try:
            text = provider(model, prompt, api_key)
        except LlmPlannerError:
            raise
        except Exception as exc:  # noqa: BLE001 - any provider crash is opaque
            raise LlmPlannerError(f"LLM provider failed: {type(exc).__name__}: {exc}") from exc

        if not isinstance(text, str) or not text.strip():
            raise LlmPlannerError("LLM provider returned empty text")
        return text


def _resolve_provider(
    cfg: Settings,
    injected_provider: ProviderCall | None,
) -> tuple[ProviderCall, str, str]:
    provider_name = cfg.llm_provider.strip().lower()
    model = cfg.llm_model.strip()
    if not model:
        raise LlmPlannerError("LLM provider not configured: set LLM_MODEL")

    if provider_name == "anthropic":
        if not cfg.anthropic_api_key:
            raise LlmPlannerError("LLM provider not configured: set ANTHROPIC_API_KEY")
        return injected_provider or _anthropic_provider_call, model, cfg.anthropic_api_key

    if provider_name == "openai":
        if not cfg.openai_api_key:
            raise LlmPlannerError("LLM provider not configured: set OPENAI_API_KEY")
        if model.startswith("claude-"):
            raise LlmPlannerError("OpenAI provider requires an OpenAI LLM_MODEL, e.g. gpt-4o-mini")
        return injected_provider or _openai_provider_call, model, cfg.openai_api_key

    raise LlmPlannerError("Unsupported LLM_PROVIDER; expected 'anthropic' or 'openai'")


def resolve_streaming_provider(
    cfg: Settings,
    injected_provider: StreamingProviderCall | None = None,
) -> tuple[StreamingProviderCall, str, str]:
    """Pick the streaming provider matching `cfg.llm_provider`.

    Mirrors `_resolve_provider` but returns a generator-style callable. Used
    by the narrator's streaming path (planner stays on blocking calls — it
    needs the full JSON before any downstream step can run).
    """
    provider_name = cfg.llm_provider.strip().lower()
    model = cfg.llm_model.strip()
    if not model:
        raise LlmPlannerError("LLM provider not configured: set LLM_MODEL")
    if provider_name == "anthropic":
        if not cfg.anthropic_api_key:
            raise LlmPlannerError("LLM provider not configured: set ANTHROPIC_API_KEY")
        return (
            injected_provider or _anthropic_streaming_provider_call,
            model,
            cfg.anthropic_api_key,
        )
    if provider_name == "openai":
        if not cfg.openai_api_key:
            raise LlmPlannerError("LLM provider not configured: set OPENAI_API_KEY")
        if model.startswith("claude-"):
            raise LlmPlannerError("OpenAI provider requires an OpenAI LLM_MODEL, e.g. gpt-4o-mini")
        return injected_provider or _openai_streaming_provider_call, model, cfg.openai_api_key
    raise LlmPlannerError("Unsupported LLM_PROVIDER; expected 'anthropic' or 'openai'")


def _anthropic_provider_call(model: str, prompt: str, api_key: str) -> str:
    """Default provider: Anthropic Messages API.

    Lazy-imports the SDK so the rest of the package works without the
    optional `[llm]` extra installed.
    """
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - optional dep
        raise LlmPlannerError('anthropic SDK not installed; pip install -e ".[llm]"') from exc

    client = anthropic.Anthropic(api_key=api_key, timeout=30.0, max_retries=1)
    msg = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    # Concatenate all text blocks; planner prompt asks for JSON only, so a
    # well-behaved model returns one block. Robust against multi-block too.
    parts: list[str] = []
    for block in msg.content:
        text = getattr(block, "text", None)
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts).strip()


def _openai_provider_call(model: str, prompt: str, api_key: str) -> str:
    """OpenAI Chat Completions provider.

    Uses stdlib HTTPS instead of a mandatory SDK dependency. The planner still
    returns raw JSON text only; parser, SQL guard, and executor remain downstream.
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:  # pragma: no cover - real network only
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise LlmPlannerError(f"OpenAI provider failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - real network only
        raise LlmPlannerError(f"OpenAI provider failed: {exc.reason}") from exc

    data = json.loads(body)
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:  # pragma: no cover - provider contract
        raise LlmPlannerError("OpenAI provider returned unexpected response shape") from exc
    if not isinstance(text, str):
        raise LlmPlannerError("OpenAI provider returned non-text content")
    return text.strip()


def _anthropic_streaming_provider_call(
    model: str, prompt: str, api_key: str
) -> Iterator[str]:
    """Streaming Anthropic provider — yields each text delta as it arrives."""
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - optional dep
        raise LlmPlannerError('anthropic SDK not installed; pip install -e ".[llm]"') from exc

    client = anthropic.Anthropic(api_key=api_key, timeout=60.0, max_retries=1)
    with client.messages.stream(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            if isinstance(text, str) and text:
                yield text


def _openai_streaming_provider_call(
    model: str, prompt: str, api_key: str
) -> Iterator[str]:
    """Streaming OpenAI provider — parses SSE `data:` lines from chat completions.

    Uses stdlib only (no SDK dep). Reads chunks line by line and yields each
    `choices[0].delta.content` string as it arrives. `[DONE]` ends the stream.
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "stream": True,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)  # noqa: S310
    except urllib.error.HTTPError as exc:  # pragma: no cover
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise LlmPlannerError(f"OpenAI streaming failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover
        raise LlmPlannerError(f"OpenAI streaming failed: {exc.reason}") from exc

    try:
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line or not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            try:
                delta = event["choices"][0]["delta"].get("content")
            except (KeyError, IndexError, TypeError):
                continue
            if isinstance(delta, str) and delta:
                yield delta
    finally:
        resp.close()


@dataclass
class TwoStageLlmPlanner:
    """Two-stage planner: schema linking, then SQL generation.

    Stage 1: build_schema_linking_prompt -> provider -> parse_schema_linking_response.
    Stage 2: build_sql_prompt(question, schema_link) -> provider -> raw planner JSON.

    The returned text is the stage-2 raw JSON; QueryService still routes it
    through parse_planner_response + sql_guard before any execution.
    """

    settings: Settings | None = None
    provider_call: ProviderCall | None = None
    log_full_prompt: bool = False
    k_examples: int = 5

    def plan(self, user_question: str) -> str:
        cfg = self.settings or get_settings()
        provider, model, api_key = _resolve_provider(cfg, self.provider_call)

        # ----- Stage 1: schema linking -----
        link_prompt = build_schema_linking_prompt(user_question)
        if self.log_full_prompt:
            log.info("stage1 prompt: %s", link_prompt)
        else:
            log.info("stage1 prompt built (%d chars)", len(link_prompt))

        try:
            link_text = provider(model, link_prompt, api_key)
        except LlmPlannerError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise LlmPlannerError(f"stage1 provider failed: {type(exc).__name__}: {exc}") from exc
        if not isinstance(link_text, str) or not link_text.strip():
            raise LlmPlannerError("stage1 provider returned empty text")

        try:
            schema_link = parse_schema_linking_response(link_text)
        except SchemaLinkParseError as exc:
            raise LlmPlannerError(f"stage1 invalid schema-linking JSON: {exc}") from exc

        # ----- Stage 2: SQL generation -----
        sql_prompt = build_sql_prompt(user_question, schema_link, k_examples=self.k_examples)
        if self.log_full_prompt:
            log.info("stage2 prompt: %s", sql_prompt)
        else:
            log.info("stage2 prompt built (%d chars)", len(sql_prompt))

        try:
            sql_text = provider(model, sql_prompt, api_key)
        except LlmPlannerError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise LlmPlannerError(f"stage2 provider failed: {type(exc).__name__}: {exc}") from exc
        if not isinstance(sql_text, str) or not sql_text.strip():
            raise LlmPlannerError("stage2 provider returned empty text")
        return sql_text


def make_planner_from_settings(
    settings: Settings | None = None,
    *,
    provider_call: ProviderCall | None = None,
    log_full_prompt: bool = False,
) -> LlmPlanner | TwoStageLlmPlanner:
    """Pick the planner implementation according to `settings.llm_planner_mode`.

    Default `single_stage` keeps existing behavior; `two_stage` opts in to
    schema-link + SQL pipeline. Unknown modes raise.
    """
    cfg = settings or get_settings()
    mode = (cfg.llm_planner_mode or "single_stage").strip().lower()
    if mode == "single_stage":
        return LlmPlanner(
            settings=cfg, provider_call=provider_call, log_full_prompt=log_full_prompt
        )
    if mode == "two_stage":
        return TwoStageLlmPlanner(
            settings=cfg, provider_call=provider_call, log_full_prompt=log_full_prompt
        )
    raise LlmPlannerError(
        f"Unsupported LLM_PLANNER_MODE={mode!r}; expected 'single_stage' or 'two_stage'"
    )


__all__ = [
    "LlmPlanner",
    "LlmPlannerError",
    "ProviderCall",
    "StreamingProviderCall",
    "TwoStageLlmPlanner",
    "make_planner_from_settings",
    "resolve_streaming_provider",
]
