"""End-to-end /query test with the Anthropic client and PubMed HTTP mocked out —
no live network calls, no API key required.
"""
from itertools import pairwise
from unittest.mock import MagicMock

import pytest
import responses
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.tools.pubmed_tool import EUTILS_BASE


def _text_block(text: str):
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _tool_use_block(name: str, input_: dict, id_: str = "toolu_1"):
    block = MagicMock()
    block.type = "tool_use"
    block.name = name
    block.input = input_
    block.id = id_
    return block


def _usage(input_tokens: int = 100, output_tokens: int = 50):
    usage = MagicMock()
    usage.input_tokens = input_tokens
    usage.output_tokens = output_tokens
    return usage


@pytest.fixture
def client():
    return TestClient(app)


@responses.activate
def test_query_end_to_end_with_pubmed_tool_call(client, monkeypatch):
    responses.get(
        f"{EUTILS_BASE}/esearch.fcgi",
        json={"esearchresult": {"idlist": ["999"]}},
    )
    responses.get(
        f"{EUTILS_BASE}/esummary.fcgi",
        json={"result": {"999": {"title": "EGFR Inhibitors in NSCLC.", "fulljournalname": "J", "pubdate": "2024"}}},
    )
    responses.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        body="EGFR inhibitors show efficacy in NSCLC.",
    )

    tool_call_response = MagicMock()
    tool_call_response.stop_reason = "tool_use"
    tool_call_response.content = [_tool_use_block("pubmed_search", {"query": "EGFR inhibitors", "max_results": 1})]
    tool_call_response.usage = _usage()

    final_response = MagicMock()
    final_response.stop_reason = "end_turn"
    final_response.content = [_text_block("EGFR inhibitors are effective in NSCLC (PMID 999).")]
    final_response.usage = _usage()

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [tool_call_response, final_response]

    import backend.app.agent.loop as loop_module

    monkeypatch.setattr(loop_module, "get_client", lambda: mock_client)

    resp = client.post(
        "/query",
        json={"question": "What do we know about EGFR inhibitors in NSCLC?", "domain": "general_biomedical"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "EGFR" in body["answer"]
    assert body["tool_calls"][0]["tool"] == "pubmed_search"
    assert body["tool_calls"][0]["output"]["results"][0]["pmid"] == "999"
    assert body["session_id"]


def test_second_turn_sees_first_turns_answer_in_history(client, monkeypatch):
    """Regression test: the agent loop must append its own final assistant
    message to history on end_turn. Previously it didn't, so a second turn
    in the same session sent two consecutive "user" messages, which the
    real Anthropic API rejects.
    """
    first_response = MagicMock()
    first_response.stop_reason = "end_turn"
    first_response.content = [_text_block("First answer.")]
    first_response.usage = _usage()

    second_response = MagicMock()
    second_response.stop_reason = "end_turn"
    second_response.content = [_text_block("Second answer.")]
    second_response.usage = _usage()

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [first_response, second_response]

    import backend.app.agent.loop as loop_module

    monkeypatch.setattr(loop_module, "get_client", lambda: mock_client)

    first = client.post("/query", json={"question": "First question", "domain": "general_biomedical"})
    session_id = first.json()["session_id"]

    second = client.post(
        "/query",
        json={"question": "Second question", "domain": "general_biomedical", "session_id": session_id},
    )
    assert second.status_code == 200
    assert second.json()["answer"] == "Second answer."

    # inspect what the second call actually sent — roles must strictly alternate,
    # and the first turn's assistant answer must be present in history
    second_call_messages = mock_client.messages.create.call_args_list[1].kwargs["messages"]
    roles = [m["role"] for m in second_call_messages]
    for prev, nxt in pairwise(roles):
        assert prev != nxt, f"consecutive same-role messages: {roles}"
    assert any(
        m["role"] == "assistant" and m["content"] is first_response.content for m in second_call_messages
    )
