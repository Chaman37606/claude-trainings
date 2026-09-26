import api_client
import requests
import streamlit as st
from components.chat_panel import render_chat
from components.ingest_form import render_ingest_form
from theme import domain_badge, inject_theme

st.set_page_config(page_title="Drug Discovery", page_icon="💊", layout="wide")
inject_theme()
st.title("💊 Drug Discovery Intelligence")
st.caption("Compounds, targets, and mechanisms — grounded in ChEMBL and the literature.")
domain_badge("drug_discovery")

DOMAIN = "drug_discovery"

tab_chat, tab_extract, tab_seed = st.tabs(["💬 Ask", "🧪 Extract entities", "📥 Seed the index"])

with tab_chat:
    render_chat(
        domain=DOMAIN,
        session_key="dd_session_id",
        history_key="dd_history",
        intro_message=(
            "Try *\"What is the mechanism of action of osimertinib, and what "
            "resistance mutations limit it?\"*"
        ),
        chat_input_placeholder="Ask about a compound, target, or mechanism…",
        chat_input_key="dd_chat",
    )

with tab_extract:
    st.markdown(
        "Extract structured **targets / compounds / trial phases** as JSON — the "
        "agent still uses its tools to gather evidence, but the final answer is "
        "schema-constrained rather than prose to re-parse."
    )
    extract_question = st.text_area(
        "Question to extract entities from",
        placeholder="e.g. What targets and compounds are involved in KRAS G12C inhibition, and what trial phases are they in?",
    )
    if st.button("Extract", type="primary") and extract_question:
        try:
            with st.spinner("Extracting…"):
                result = api_client.extract(extract_question, DOMAIN)
        except requests.RequestException as exc:
            st.error(f"Extraction failed: {exc}")
        else:
            st.json(result["entities"])

with tab_seed:
    st.markdown("Fetch and index papers into this domain's collection before asking about them.")
    render_ingest_form(domain=DOMAIN, key_prefix="dd")
