import api_client
import requests
import streamlit as st
from theme import hero, inject_theme

st.set_page_config(page_title="Biomedical Agentic RAG", page_icon="🧬", layout="wide")
inject_theme()

try:
    domains = api_client.list_domains()
    n_domains = len(domains)
    n_extraction = sum(1 for d in domains if d.get("supports_extraction"))
except requests.RequestException:
    # backend not reachable yet — show the hero with placeholders rather than crash
    domains, n_domains, n_extraction = [], "—", "—"

hero(
    kicker="Agentic RAG · Literature Review & Drug-Discovery Intelligence",
    title="Ask the literature. Get the citations.",
    lede=(
        "A Claude-powered research agent that searches PubMed, Semantic Scholar, "
        "and ChEMBL live, indexes what it finds, and answers with sources you can "
        "check — across biomedical subfields and a dedicated drug-discovery mode."
    ),
    stats=[
        (str(n_domains), "Domains configured"),
        (str(n_extraction), "With structured extraction"),
        ("3", "Live data sources"),
    ],
)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.subheader("📚 Literature Review")
    st.markdown(
        "Cross-subfield biomedical Q&A — oncology, cardiology, neurology, general "
        "biomedicine. Every answer is grounded in PubMed / Semantic Scholar "
        "abstracts it fetched and indexed, with citations you can click through."
    )
    st.page_link("pages/1_literature_review.py", label="Open Literature Review →")

with col2:
    st.subheader("💊 Drug Discovery")
    st.markdown(
        "Compound, target, and mechanism questions backed by ChEMBL bioactivity "
        "data alongside literature evidence — plus structured entity extraction "
        "(targets, compounds, trial phases) as JSON, not prose to re-parse."
    )
    st.page_link("pages/2_drug_discovery.py", label="Open Drug Discovery →")

st.html('<hr class="section-rule">')
st.caption(
    "Backend must be running (`scripts/run_backend.sh`) for domains, search, and "
    "chat to work. Add `ANTHROPIC_API_KEY` to `.env` before asking questions."
)
