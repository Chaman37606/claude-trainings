import api_client
import requests
import streamlit as st
from components.chat_panel import render_chat
from components.ingest_form import render_ingest_form
from theme import domain_badge, inject_theme

st.set_page_config(page_title="Literature Review", page_icon="📚", layout="wide")
inject_theme()
st.title("📚 Literature Review")
st.caption("Cross-subfield biomedical Q&A, grounded in PubMed and Semantic Scholar.")

# Data-driven, not a hardcoded domain-name check: this page shows domains
# that don't do structured extraction — the drug-discovery domain does.
try:
    domains = [d for d in api_client.list_domains() if not d["supports_extraction"]]
except requests.RequestException as exc:
    st.error(f"Could not reach the backend at {api_client.BASE_URL}: {exc}")
    st.stop()

domain_labels = {d["display_name"]: d["name"] for d in domains}

col1, col2 = st.columns([2, 1], gap="large")
with col2:
    domain_label = st.selectbox("Domain", list(domain_labels.keys()))
    domain_name = domain_labels[domain_label]
    domain_badge(domain_name)

    with st.container(border=True):
        st.subheader("Seed the index")
        render_ingest_form(domain=domain_name, key_prefix="lit", use_container_width=True)

with col1:
    render_chat(
        domain=domain_name,
        session_key="session_id",
        history_key="history",
        intro_message=(
            "Ask a question below — e.g. *\"What resistance mechanisms limit EGFR "
            "inhibitors in NSCLC?\"* Seed the index first if you want it grounded "
            "in specific papers."
        ),
        chat_input_placeholder="Ask a literature review question…",
    )
