# Biomedical Agentic RAG — project conventions

Agentic RAG app for biomedical literature review and drug-discovery intelligence.
See `docs/problem_statement.md` for the product scope and `.claude/plans/` (or
the session's plan) for the full 20-step AI-DLC build phasing.

## Stack

- Backend: FastAPI + a manual Anthropic tool-use loop (`backend/app/agent/loop.py`) — not LangChain, not the Claude Agent SDK product.
- Frontend: Streamlit, calling the backend over HTTP only (`frontend/api_client.py`).
- Vector store: ChromaDB, one collection per domain, under `backend/chroma_data/`.
- Domain behavior (prompts, allowed tools, extraction schema) is config-driven — see `backend/app/domains/*.yaml` and `loader.py`. Add a new domain by adding a YAML file, not by branching code.

## Delegation rules for subagents

| Task touches | Delegate to |
|---|---|
| `frontend/**` | `frontend-agent` |
| `backend/**`, `mcp_server/**`, `evals/**` | `backend-agent` |
| Reviewing a diff/PR before merge | `p3-triage-agent` |
| `.claude/**`, `pyproject.toml`, infra/CI config | main session only — subagents should not modify their own permissions or the project's dev tooling |

Frontend and backend agents run in fresh, isolated contexts by default (no
shared conversation history). When both are dispatched in parallel on the
same feature, use `isolation: "worktree"` so their file edits can't collide.

## Context management

The backend's own runtime agent loop trims conversation history via
`backend/app/agent/context_manager.py`: the last 8-10 turns are kept
verbatim, everything older is summarized into a single block capped at
12-15% of the context token budget. This is a runtime policy for the RAG
app's own agent, distinct from Claude Code's own compaction.

## Running it

```
scripts/run_backend.sh    # FastAPI on :8000
scripts/run_frontend.sh   # Streamlit, talks to the backend over HTTP
```

Requires `ANTHROPIC_API_KEY` in `.env` (copy from `.env.example`).

## Tests

`pytest` from the repo root. Unit tests mock outbound HTTP with `responses`
(the tools use `requests`, not `httpx`) and mock the Anthropic client
directly for the agent-loop integration test — no live network or API key
needed to run the suite.
