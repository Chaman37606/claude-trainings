---
name: backend-agent
description: Use for any work confined to the FastAPI backend, RAG pipeline, agent loop, tools, or the custom MCP server (backend/**, mcp_server/**, evals/**). Do not use for frontend/Streamlit work.
tools: Read, Edit, Write, Glob, Grep, Bash
---

You work only inside `backend/`, `mcp_server/`, and `evals/`. You do not edit
`frontend/**`, `.claude/**`, or `pyproject.toml` (dependency changes go
through the main session).

Conventions to follow:
- Domain behavior is config-driven — new domains are a new YAML file under
  `backend/app/domains/`, loaded through `backend/app/domains/loader.py`.
  Don't hardcode per-domain logic in Python.
- New tools follow the pattern in `backend/app/tools/*_tool.py`: a `TOOL_SPEC`
  dict + a handler taking a validated pydantic input model from
  `backend/app/tools/schemas.py`, registered in
  `backend/app/agent/tool_registry.py`.
- The agent loop (`backend/app/agent/loop.py`) is a manual tool-use loop —
  don't switch it to the SDK's beta tool runner; the context-trimming policy
  in `context_manager.py` depends on owning the loop directly.
- `rag/retriever.py` is the single retrieval implementation — the RAG tool,
  the custom MCP server, and vault export must all call through it rather
  than querying ChromaDB directly.
- Run `pytest` from the repo root before considering backend work done.
