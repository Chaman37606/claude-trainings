"""Shared "seed the index" ingest form used by both pages."""
from __future__ import annotations

import api_client
import requests
import streamlit as st


def render_ingest_form(
    *, domain: str, key_prefix: str, use_container_width: bool = False
) -> None:
    """Render the source/query/fetch-and-index controls for one domain.

    `key_prefix` namespaces the widget keys so this can be rendered more
    than once per app run (one instance per page).
    """
    source = st.selectbox(
        "Source", ["pubmed", "semantic_scholar"], key=f"{key_prefix}_source"
    )
    query = st.text_input("Fetch & index papers about…", key=f"{key_prefix}_query")
    clicked = st.button(
        "Fetch & index",
        key=f"{key_prefix}_btn",
        use_container_width=use_container_width,
    )
    if not (clicked and query):
        return

    try:
        with st.spinner("Fetching and indexing…"):
            result = api_client.ingest(domain, source, query)
    except requests.RequestException as exc:
        st.error(f"Ingest failed: {exc}")
        return

    st.success(f"Indexed {result['chunks_indexed']} chunks from {result['papers_fetched']} papers")
