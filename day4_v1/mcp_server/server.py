"""Custom MCP server exposing this app's RAG retrieval as reusable tools —
so any MCP client (another Claude Code session, a different agent, a
different app) can query the indexed literature without going through the
FastAPI backend. Backed entirely by backend.app.rag.retriever /
backend.app.domains.loader — no retrieval logic is reimplemented here.

Run standalone: python -m mcp_server.server (stdio transport)
Registered project-scoped in .mcp.json as "biomed-rag".
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from backend.app.domains.loader import (
    DomainConfigError,
    DomainNotFoundError,
    list_domain_names,
    load_domain,
)
from backend.app.rag.retriever import get_paper as retriever_get_paper
from backend.app.rag.retriever import retrieve

server = MCPServer(
    name="biomed-rag",
    instructions=(
        "Search and inspect the indexed biomedical literature this app has "
        "already fetched from PubMed/Semantic Scholar/ChEMBL. Call "
        "list_domains first if you don't know which domain to search."
    ),
)


@server.tool()
def list_domains() -> list[dict]:
    """List configured research domains, with whether each supports structured entity extraction."""
    domains = []
    for name in list_domain_names():
        try:
            cfg = load_domain(name)
        except DomainConfigError:
            continue
        domains.append(cfg.summary())
    return domains


@server.tool()
def search_literature(query: str, domain: str, top_k: int = 6) -> list[dict]:
    """Search the local index of already-fetched papers for one domain.

    Returns cited chunks (text, paper_id, title, source, url, distance) — does
    NOT fetch new papers from PubMed/Semantic Scholar/ChEMBL; use the app's
    own /ingest endpoint or UI to seed the index first.
    """
    try:
        domain_cfg = load_domain(domain)
    except (DomainNotFoundError, DomainConfigError) as exc:
        return [{"error": str(exc)}]

    chunks = retrieve(domain_cfg, query, top_k=top_k)
    return [
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


@server.tool()
def get_paper(paper_id: str, domain: str) -> list[dict]:
    """Fetch every indexed chunk for one paper_id (as returned by search_literature), in order."""
    try:
        domain_cfg = load_domain(domain)
    except (DomainNotFoundError, DomainConfigError) as exc:
        return [{"error": str(exc)}]
    return retriever_get_paper(domain_cfg, paper_id)


if __name__ == "__main__":
    server.run()
