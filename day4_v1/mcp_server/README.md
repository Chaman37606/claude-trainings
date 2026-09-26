# biomed-rag MCP server

Exposes this app's RAG retrieval as MCP tools, so any MCP client — another
Claude Code session, a different agent, a different app entirely — can
query the indexed biomedical literature without going through the FastAPI
backend. Everything here calls straight into `backend.app.rag.retriever` /
`backend.app.domains.loader`; no retrieval logic is duplicated.

## Tools

- `list_domains()` — configured domains and whether each supports structured entity extraction.
- `search_literature(query, domain, top_k=6)` — searches the local index only (does **not** fetch new papers from PubMed/Semantic Scholar/ChEMBL — seed the index first via the app's `/ingest` endpoint or UI).
- `get_paper(paper_id, domain)` — every indexed chunk for one paper, in order.

All three return a controlled `{"error": "..."}` payload on a bad domain name rather than raising.

## Running it

Registered project-scoped in `.mcp.json` as `biomed-rag` (`python3 -m mcp_server.server`, stdio transport) — approve it the next time you start a `claude` session in this repo.

To run/test standalone:

```bash
python3 -m mcp_server.server
```

It speaks MCP over stdio, so it expects a client on the other end (Claude Code, or `mcp.client.stdio` in a script) — running it directly in a terminal will just sit waiting for input, which is expected.
