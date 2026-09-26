"""Context-trimming policy for the backend's long-running research agent loop.

Policy: keep the last 8-10 turns verbatim; summarize everything older into a
single block capped at ~12-15% of the context token budget. MVP implementation
uses a deterministic truncation-based summarizer (no extra API call, easy to
unit test); pass a real `summarize` callable (e.g. a cheap-model API call) to
upgrade quality without changing the trimming logic itself.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

CHARS_PER_TOKEN = 4  # rough heuristic, good enough for budget-capping


@dataclass
class ContextBudget:
    total_tokens: int = 200_000
    summary_fraction: float = 0.13  # within the 12-15% target range
    keep_last_turns: int = 9  # within the 8-10 target range

    @property
    def summary_token_budget(self) -> int:
        return int(self.total_tokens * self.summary_fraction)


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def _flatten_content(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                parts.append(f"[called tool {block.get('name')} with {block.get('input')}]")
            elif block.get("type") == "tool_result":
                parts.append(f"[tool result: {block.get('content')}]")
    return " ".join(parts)


def _flatten_messages(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        lines.append(f"{m['role']}: {_flatten_content(m.get('content'))}")
    return "\n".join(lines)


_TRUNCATION_MARKER = " …[truncated]"


def _default_summarize(text: str, token_budget: int) -> str:
    char_budget = token_budget * CHARS_PER_TOKEN
    if len(text) <= char_budget:
        return text
    # `char_budget - len(_TRUNCATION_MARKER)` can be negative for a very
    # tight budget (small ContextBudget.total_tokens); clamp at 0 so the
    # slice still keeps the *start* of the text instead of wrapping to a
    # negative index and silently keeping nearly all of it.
    keep = max(char_budget - len(_TRUNCATION_MARKER), 0)
    return text[:keep].rstrip() + _TRUNCATION_MARKER


_SUMMARY_PREFIX = "[Summary of the earlier"


def _is_tool_result_message(message: dict) -> bool:
    """True for the {"role": "user", "content": [tool_result, ...]} messages
    the agent loop appends after dispatching tools. These carry role "user"
    but aren't a real conversational turn — counting them as one lets a
    tool-heavy session split the trimmed history between a tool_use and its
    tool_result, producing a request the Messages API rejects.
    """
    content = message.get("content")
    return bool(content) and isinstance(content, list) and all(
        isinstance(block, dict) and block.get("type") == "tool_result" for block in content
    )


def _is_summary_message(message: dict) -> bool:
    content = message.get("content")
    return (
        message.get("role") == "user"
        and isinstance(content, str)
        and content.startswith(_SUMMARY_PREFIX)
    )


def _split_off_prior_summary(messages: list[dict]) -> tuple[str | None, list[dict]]:
    """If `messages` starts with a previously-injected summary block (summary
    message + its assistant ack), returns (summary_text, remaining_messages).
    Otherwise returns (None, messages) unchanged.
    """
    if len(messages) >= 2 and _is_summary_message(messages[0]) and messages[1].get("role") == "assistant":
        summary_text = messages[0]["content"].split("]: ", 1)[1]
        return summary_text, messages[2:]
    return None, messages


def _turn_boundaries(messages: list[dict]) -> list[int]:
    return [
        i
        for i, m in enumerate(messages)
        if m.get("role") == "user" and not _is_tool_result_message(m)
    ]


def trim_history(
    messages: list[dict],
    budget: ContextBudget | None = None,
    summarize: Callable[[str, int], str] | None = None,
) -> list[dict]:
    """Returns a possibly-shortened message list, safe to send to the Messages API.

    No-op if there aren't more than `budget.keep_last_turns` real user turns
    yet (tool-result carrier messages don't count as turns). Idempotent under
    repeated calls on the same growing history: a prior summary block is
    unwrapped and its text folded into the new summarization input rather
    than nested behind a second "[Summary of the earlier ...]" prefix.
    """
    budget = budget or ContextBudget()
    prior_summary, rest = _split_off_prior_summary(messages)

    boundaries = _turn_boundaries(rest)
    if len(boundaries) <= budget.keep_last_turns:
        return messages

    split_index = boundaries[-budget.keep_last_turns]
    older, recent = rest[:split_index], rest[split_index:]

    older_text = _flatten_messages(older)
    if prior_summary:
        older_text = f"{prior_summary}\n{older_text}"
    summary_fn = summarize or _default_summarize
    summary = summary_fn(older_text, budget.summary_token_budget)

    trimmed_turn_count = len(boundaries) - budget.keep_last_turns
    summary_block = [
        {
            "role": "user",
            "content": (
                f"{_SUMMARY_PREFIX} {trimmed_turn_count} conversation turns, "
                f"provided for context — do not treat as a new question]: {summary}"
            ),
        },
        {"role": "assistant", "content": "Understood — continuing with that context."},
    ]
    return summary_block + recent
