# Biomedical Agentic RAG

Agentic RAG for literature review and drug-discovery intelligence, built as
a phased AI-DLC POC. See `docs/problem_statement.md` for scope, `CLAUDE.md`
for project/dev conventions, and `docs/demo_script.md` for what's built vs.
deferred.

## Quickstart

```bash
cp .env.example .env   # fill in ANTHROPIC_API_KEY at minimum
pip install -e ".[dev]"
pytest                  # 15 tests, no network/API key required

scripts/run_backend.sh   # FastAPI on :8000
scripts/run_frontend.sh  # Streamlit, in another terminal
```

Then open the Streamlit URL it prints, pick a domain, use "Fetch & index" to
seed the index on a topic, and ask a question.

## Layout

- `backend/app/domains/*.yaml` — per-domain config (prompt, allowed tools,
  extraction schema). Add a domain by adding a YAML file.
- `backend/app/tools/` — PubMed, Semantic Scholar, ChEMBL, and RAG-search
  tool implementations.
- `backend/app/rag/` — chunk/embed/index/retrieve pipeline (ChromaDB).
- `backend/app/agent/` — the manual tool-use loop and its context-trimming
  policy.
- `frontend/` — Streamlit UI, talks to the backend only through
  `frontend/api_client.py`.
- `.claude/agents/` — dev-time subagents (frontend/backend/triage) and their
  delegation rules (see `CLAUDE.md`).
