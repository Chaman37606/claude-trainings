"""Shared chat panel for the literature-review and drug-discovery pages.

Both pages render an identical chat history / input / query / rerun loop,
differing only in which `st.session_state` keys and domain they use — this
factors that loop out so it isn't duplicated per page.
"""
from __future__ import annotations

import api_client
import requests
import streamlit as st
from components.citation_view import render_tool_calls


def render_chat(
    *,
    domain: str,
    session_key: str,
    history_key: str,
    intro_message: str,
    chat_input_placeholder: str,
    chat_input_key: str | None = None,
) -> None:
    """Render chat history, an empty-state hint, and the chat input box.

    Reads/writes `st.session_state[session_key]` (the backend session id)
    and `st.session_state[history_key]` (the list of turns), initializing
    them on first use.
    """
    st.session_state.setdefault(session_key, None)
    st.session_state.setdefault(history_key, [])
    history = st.session_state[history_key]

    if not history:
        st.info(intro_message, icon="💬")

    for turn in history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])
            if turn.get("tool_calls"):
                render_tool_calls(turn["tool_calls"])

    question = st.chat_input(chat_input_placeholder, key=chat_input_key)
    if not question:
        return

    history.append({"role": "user", "content": question})
    try:
        with st.spinner("Researching…"):
            resp = api_client.query(question, domain, st.session_state[session_key])
    except requests.RequestException as exc:
        history.append(
            {"role": "assistant", "content": f"⚠ Could not reach the backend: {exc}"}
        )
        st.rerun()
        return

    st.session_state[session_key] = resp["session_id"]
    history.append(
        {"role": "assistant", "content": resp["answer"], "tool_calls": resp["tool_calls"]}
    )
    st.rerun()
