from backend.app.agent.context_manager import (
    ContextBudget,
    _default_summarize,
    estimate_tokens,
    trim_history,
)


def _synthetic_history(n_turns: int) -> list[dict]:
    messages = []
    for i in range(n_turns):
        messages.append({"role": "user", "content": f"question {i}"})
        messages.append({"role": "assistant", "content": f"answer {i}"})
    return messages


def test_short_history_is_untouched():
    history = _synthetic_history(5)
    budget = ContextBudget(keep_last_turns=9)
    assert trim_history(history, budget=budget) == history


def test_long_history_keeps_last_turns_verbatim():
    history = _synthetic_history(15)
    budget = ContextBudget(keep_last_turns=9)
    trimmed = trim_history(history, budget=budget)

    # last 9 user turns preserved verbatim, i.e. last 18 messages of the original
    assert trimmed[-18:] == history[-18:]
    # plus a 2-message summary block prepended
    assert len(trimmed) == 18 + 2
    assert trimmed[0]["role"] == "user"
    assert "Summary of the earlier" in trimmed[0]["content"]
    assert trimmed[1]["role"] == "assistant"


def test_summary_respects_token_budget():
    history = _synthetic_history(20)
    budget = ContextBudget(keep_last_turns=9, total_tokens=1000, summary_fraction=0.1)
    trimmed = trim_history(history, budget=budget)
    # strip the fixed "[Summary of the earlier N turns...]: " prefix — only the
    # actual summarized content is bound by the token budget
    summarized_content = trimmed[0]["content"].split("]: ", 1)[1]
    assert estimate_tokens(summarized_content) <= budget.summary_token_budget


def test_custom_summarize_callable_is_used():
    history = _synthetic_history(15)
    calls = []

    def fake_summarize(text: str, token_budget: int) -> str:
        calls.append((text, token_budget))
        return "CUSTOM SUMMARY"

    trimmed = trim_history(history, summarize=fake_summarize)
    assert calls, "custom summarizer should have been invoked"
    assert trimmed[0]["content"].endswith("CUSTOM SUMMARY")


def test_tool_result_messages_are_not_counted_as_turns():
    """A tool-heavy session (many {"role": "user", "content": [tool_result]}
    messages appended by the agent loop) must not trigger trimming just
    because the raw user-role count is high — only real questions count.
    """
    history = _synthetic_history(5)  # 5 real turns, well under keep_last_turns
    for i in range(20):
        history.append(
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": "{}"}],
            }
        )
        history.append({"role": "assistant", "content": f"followup {i}"})

    budget = ContextBudget(keep_last_turns=9)
    assert trim_history(history, budget=budget) == history


def test_trimming_a_tool_heavy_session_never_splits_a_tool_use_from_its_result():
    """Regression for the tool_result-miscounted-as-turn bug: once real
    turns exceed the budget, the split must not land between an assistant
    tool_use message and its paired tool_result.
    """
    history = _synthetic_history(3)
    for i in range(15):
        history.append(
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": f"t{i}", "name": "pubmed_search", "input": {}}],
            }
        )
        history.append(
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": "{}"}]}
        )
    for i in range(10):
        history.append({"role": "user", "content": f"question {100 + i}"})
        history.append({"role": "assistant", "content": f"answer {100 + i}"})

    budget = ContextBudget(keep_last_turns=9)
    trimmed = trim_history(history, budget=budget)

    # every tool_result in the trimmed output must have its tool_use still present
    tool_use_ids = {
        block["id"]
        for m in trimmed
        if m.get("role") == "assistant" and isinstance(m.get("content"), list)
        for block in m["content"]
        if isinstance(block, dict) and block.get("type") == "tool_use"
    }
    for m in trimmed:
        if m.get("role") == "user" and isinstance(m.get("content"), list):
            for block in m["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    assert block["tool_use_id"] in tool_use_ids


def test_repeated_trimming_does_not_nest_summaries():
    """Calling trim_history again on an already-trimmed, still-growing
    history must fold the prior summary into the new one rather than
    stacking a second "[Summary of the earlier ...]" prefix inside it.
    """
    budget = ContextBudget(keep_last_turns=9)

    history = _synthetic_history(15)
    once_trimmed = trim_history(history, budget=budget)

    # grow the conversation further, then trim again
    grown = once_trimmed + _synthetic_history(10)
    twice_trimmed = trim_history(grown, budget=budget)

    summary_text = twice_trimmed[0]["content"]
    # the prefix must appear exactly once — not nested inside itself
    assert summary_text.count("[Summary of the earlier") == 1


def test_default_summarize_handles_budget_smaller_than_truncation_marker():
    """Regression: a token_budget so small that char_budget is less than
    len(_TRUNCATION_MARKER) used to make `char_budget - len(marker)` go
    negative, which sliced from the *end* of the text instead of the start —
    returning almost the whole original text instead of a short summary.
    """
    text = "word " * 500
    summary = _default_summarize(text, token_budget=1)
    assert len(summary) < len(text) / 2
