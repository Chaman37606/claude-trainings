"""PubMed / NCBI E-utilities search tool: metadata + abstracts, no full text."""
from __future__ import annotations

import requests

from backend.app.config import settings
from backend.app.tools.schemas import PubmedSearchInput

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

TOOL_SPEC = {
    "name": "pubmed_search",
    "description": (
        "Search PubMed for biomedical literature. Returns paper titles, PubMed "
        "IDs, and abstracts for the top matches."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "PubMed search query"},
            "max_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
        },
        "required": ["query"],
    },
}


def _eutils_params() -> dict:
    params = {"retmode": "json", "email": settings.ncbi_email}
    if settings.ncbi_api_key:
        params["api_key"] = settings.ncbi_api_key
    return params


def pubmed_search(input: PubmedSearchInput) -> dict:
    search_resp = requests.get(
        f"{EUTILS_BASE}/esearch.fcgi",
        params={**_eutils_params(), "db": "pubmed", "term": input.query, "retmax": input.max_results},
        timeout=15,
    )
    search_resp.raise_for_status()
    ids = search_resp.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return {"results": []}

    summary_resp = requests.get(
        f"{EUTILS_BASE}/esummary.fcgi",
        params={**_eutils_params(), "db": "pubmed", "id": ",".join(ids)},
        timeout=15,
    )
    summary_resp.raise_for_status()
    summaries = summary_resp.json().get("result", {})

    fetch_resp = requests.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        params={
            **_eutils_params(),
            "db": "pubmed",
            "id": ",".join(ids),
            "rettype": "abstract",
            "retmode": "text",
        },
        timeout=15,
    )
    fetch_resp.raise_for_status()
    abstracts_blob = fetch_resp.text
    abstract_chunks = [c.strip() for c in abstracts_blob.split("\n\n\n") if c.strip()]

    results = []
    for i, pmid in enumerate(ids):
        summary = summaries.get(pmid, {})
        results.append(
            {
                "pmid": pmid,
                "title": summary.get("title", "").rstrip("."),
                "journal": summary.get("fulljournalname", ""),
                "pubdate": summary.get("pubdate", ""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "abstract": abstract_chunks[i] if i < len(abstract_chunks) else "",
            }
        )
    return {"results": results}
