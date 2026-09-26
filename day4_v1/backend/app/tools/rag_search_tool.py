"""Agent-facing wrapper around backend.app.rag.retriever — the RAG search tool."""
from __future__ import annotations

from backend.app.domains.loader import load_domain
from backend.app.rag.retriever import retrieve
from backend.app.tools.schemas import RagSearchInput

TOOL_SPEC = {
    "name": "rag_search",
    "description": (
        "Search the local index of previously fetched papers for this domain. "
        "Use this before re-fetching from PubMed/Semantic Scholar/ChEMBL when "
        "the answer may already be indexed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Natural-language search query"},
            "domain": {"type": "string", "description": "Domain collection to search"},
            "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 6},
        },
        "required": ["query", "domain"],
    },
}


def rag_search(input: RagSearchInput) -> dict:
    domain = load_domain(input.domain)
    chunks = retrieve(domain, input.query, top_k=input.top_k)
    return {
        "results": [
            {
                "text": c.text,
                "paper_id": c.paper_id,
                "title": c.title,
                "source": c.source,
                "url": c.url,
                "distance": c.distance,
            }
            for c in chunks
        ]
    }
