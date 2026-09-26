"""Semantic Scholar Graph API search tool."""
from __future__ import annotations

import requests

from backend.app.config import settings
from backend.app.tools.schemas import SemanticScholarSearchInput

S2_BASE = "https://api.semanticscholar.org/graph/v1"

TOOL_SPEC = {
    "name": "semantic_scholar_search",
    "description": (
        "Search Semantic Scholar for papers (broader coverage than PubMed, "
        "includes preprints and citation counts). Returns title, abstract, "
        "year, and citation count for the top matches."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Semantic Scholar search query"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
        },
        "required": ["query"],
    },
}

FIELDS = "title,abstract,year,citationCount,externalIds,url"


def semantic_scholar_search(input: SemanticScholarSearchInput) -> dict:
    headers = {}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key

    resp = requests.get(
        f"{S2_BASE}/paper/search",
        params={"query": input.query, "limit": input.limit, "fields": FIELDS},
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    papers = resp.json().get("data", [])

    results = [
        {
            "paper_id": p.get("paperId"),
            "title": p.get("title", ""),
            "abstract": p.get("abstract") or "",
            "year": p.get("year"),
            "citation_count": p.get("citationCount"),
            "doi": (p.get("externalIds") or {}).get("DOI"),
            "url": p.get("url"),
        }
        for p in papers
    ]
    return {"results": results}
