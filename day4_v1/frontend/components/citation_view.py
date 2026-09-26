import html

import streamlit as st
from theme import source_pill_html


def render_tool_calls(tool_calls: list[dict]) -> None:
    if not tool_calls:
        return
    with st.expander(f"📎 Sources & tool calls ({len(tool_calls)})"):
        for call in tool_calls:
            st.html(
                f'<span class="tool-call-label">{html.escape(call["tool"])}'
                f'  ·  {html.escape(str(call["input"]))}</span>'
            )
            output = call.get("output", {})
            results = output.get("results") if isinstance(output, dict) else None

            if results:
                for r in results[:5]:
                    title = r.get("title") or r.get("pref_name") or (r.get("text", "")[:80] + "…")
                    url = r.get("url")
                    snippet = r.get("abstract") or r.get("text") or ""
                    source = r.get("source") or (
                        "chembl" if "chembl_id" in r else "rag_index" if "distance" in r else ""
                    )
                    pill = source_pill_html(source) if source else ""
                    title_html = (
                        f'<a href="{html.escape(url)}" target="_blank">{html.escape(title)}</a>'
                        if url
                        else html.escape(title)
                    )
                    snippet_html = (
                        f'<div class="ref-snippet">{html.escape(snippet[:180])}{"…" if len(snippet) > 180 else ""}</div>'
                        if snippet
                        else ""
                    )
                    st.html(
                        f'<div class="ref-card">{pill}<div class="ref-title">{title_html}</div>{snippet_html}</div>'
                    )
            elif isinstance(output, dict) and output.get("error"):
                st.html(f'<div class="ref-card"><span class="ref-error">⚠ {html.escape(output["error"])}</span></div>')
            st.html('<hr class="section-rule">')
