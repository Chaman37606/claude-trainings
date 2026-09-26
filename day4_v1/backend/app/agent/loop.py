"""Manual agentic loop over the Anthropic Messages API.

Manual (not the SDK's beta tool runner) because context_manager.trim_history
must rewrite message history before every request — easiest to guarantee
when the loop is owned outright rather than driven through the runner's
per-turn hooks.
"""
from __future__ import annotations

import json
import time

import anthropic

from backend.app.agent import tool_registry
from backend.app.agent.context_manager import ContextBudget, trim_history
from backend.app.agent.prompts import build_system_prompt
from backend.app.config import settings
from backend.app.domains.loader import DomainConfig, DomainConfigError
from backend.app.observability.otel_setup import (
    llm_call_duration,
    llm_token_usage,
    tracer,
)

MAX_TOKENS = 16000
MAX_ITERATIONS = 8  # hard stop against runaway tool-call loops

# Anything other than "tool_use"/"pause_turn" ends the turn — including ones
# we don't expect to see with our tool surface (refusal, stop_sequence) —
# rather than falling through to the tool-dispatch branch with zero tool_use
# blocks, which silently burned iterations until MAX_ITERATIONS.
TERMINAL_STOP_REASONS = {"end_turn", "max_tokens", "stop_sequence", "refusal"}


def _raise_if_unknown_tools(domain: DomainConfig) -> list[dict]:
    try:
        return tool_registry.specs_for(domain.allowed_tools)
    except KeyError as exc:
        raise DomainConfigError(
            f"Domain '{domain.name}' references unknown tool(s): {exc}"
        ) from exc


class AnthropicNotConfiguredError(RuntimeError):
    pass


_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not settings.anthropic_api_key:
            # Passing api_key=None lets the SDK fall back to whatever
            # ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN/ANTHROPIC_BASE_URL happen
            # to be set in the ambient process environment — which, in a dev
            # shell, may be an unrelated session's own credential. Refuse
            # instead of silently making a real authenticated call with it.
            raise AnthropicNotConfiguredError(
                "ANTHROPIC_API_KEY is not set in this app's own .env — refusing to "
                "fall back to ambient environment credentials."
            )
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _create_message(client: anthropic.Anthropic, model: str, **kwargs) -> anthropic.types.Message:
    start = time.perf_counter()
    with tracer.start_as_current_span("llm.messages.create") as span:
        span.set_attribute("llm.model", model)
        response = client.messages.create(model=model, **kwargs)
        span.set_attribute("llm.stop_reason", response.stop_reason or "")

    llm_call_duration.record(time.perf_counter() - start, {"model": model})
    usage = getattr(response, "usage", None)
    if usage is not None:
        llm_token_usage.add(usage.input_tokens, {"model": model, "token_type": "input"})
        llm_token_usage.add(usage.output_tokens, {"model": model, "token_type": "output"})
    return response


class AgentResult:
    def __init__(self, answer_text: str, tool_calls: list[dict], raw_messages: list[dict]):
        self.answer_text = answer_text
        self.tool_calls = tool_calls
        self.raw_messages = raw_messages


def run_query(
    domain: DomainConfig,
    user_input: str,
    history: list[dict] | None = None,
    response_schema: dict | None = None,
    model: str | None = None,
    context_budget: ContextBudget | None = None,
) -> AgentResult:
    """Runs the agent loop for one user turn. `history` is prior turns (already
    in Messages API format) from the caller's session store, if any.
    """
    with tracer.start_as_current_span("agent.run_query") as run_span:
        run_span.set_attribute("domain", domain.name)

        client = get_client()
        tools = _raise_if_unknown_tools(domain)
        system_prompt = build_system_prompt(domain)
        resolved_model = model or settings.model_default

        messages = list(history or []) + [{"role": "user", "content": user_input}]
        messages = trim_history(messages, budget=context_budget)

        request_kwargs: dict = {
            "max_tokens": MAX_TOKENS,
            "system": system_prompt,
            "tools": tools,
            "messages": messages,
        }
        if response_schema is not None:
            request_kwargs["output_config"] = {"format": {"type": "json_schema", "schema": response_schema}}

        tool_call_log: list[dict] = []
        response = None

        for _ in range(MAX_ITERATIONS):
            response = _create_message(client, resolved_model, **request_kwargs)
            # Append the assistant's turn unconditionally — every branch below
            # needs it in history, including the terminal ones (previously
            # skipped on end_turn, which corrupted every stored session: the
            # next turn would send two consecutive "user" messages).
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason in TERMINAL_STOP_REASONS:
                break

            if response.stop_reason == "pause_turn":
                request_kwargs["messages"] = messages
                continue

            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

            tool_results = []
            for block in tool_use_blocks:
                try:
                    result = tool_registry.dispatch(block.name, block.input)
                    is_error = "error" in result
                except Exception as exc:  # noqa: BLE001 — never let a bad tool crash the loop
                    result, is_error = {"error": str(exc)}, True

                tool_call_log.append({"tool": block.name, "input": block.input, "output": result})
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                        "is_error": is_error,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
            request_kwargs["messages"] = messages
        else:
            raise RuntimeError(f"Agent loop exceeded {MAX_ITERATIONS} iterations without finishing")

        answer_text = ""
        if response is not None:
            text_blocks = [b.text for b in response.content if b.type == "text"]
            answer_text = "\n".join(text_blocks)

        run_span.set_attribute("tool_call_count", len(tool_call_log))

    return AgentResult(answer_text=answer_text, tool_calls=tool_call_log, raw_messages=messages)
