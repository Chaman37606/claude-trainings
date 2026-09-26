# Demo script (AI-DLC Step 20)

## Status

**Built (Phase A/B):** domain-config-driven RAG engine, PubMed/Semantic
Scholar/ChEMBL tools, agent loop with context trimming, FastAPI backend,
Streamlit frontend (literature review + drug discovery pages), unit +
integration tests, dev-time subagents/hooks.

**Deferred (Phase C/D/E — not built yet):** additional domain YAMLs
(oncology/cardiology/neurology), MCP server registration/custom MCP server,
observability (OpenTelemetry/SigNoz), load testing (k6), knowledge-vault
export, graphify over the corpus, formal eval/hillclimb loop. Call this out
explicitly to the audience rather than implying it's all live.

## Setup (before the audience joins)

1. `cp .env.example .env` and fill in `ANTHROPIC_API_KEY` (and optionally
   `NCBI_EMAIL`/`NCBI_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY` for higher rate
   limits — ChEMBL needs no key).
2. `pip install -e ".[dev]"`
3. `scripts/run_backend.sh` (leave running)
4. `scripts/run_frontend.sh` (leave running)
5. Sanity check: `curl localhost:8000/health` and `curl localhost:8000/domains`.

## Walkthrough

1. **General biomedical literature review** — open the Streamlit app,
   Literature Review page, domain = General Biomedical. Use "Fetch & index"
   to seed on a topic (e.g. "EGFR inhibitors NSCLC resistance"), then ask a
   question about it in the chat. Point out the citations in the "Sources &
   tool calls" expander.
2. **Cross-domain** — switch domain to Oncology/Cardiology/Neurology if those
   YAMLs exist yet; otherwise note they're a config-only follow-up (copy
   `general_biomedical.yaml`, change the prompt/description).
3. **Drug discovery mode** — Drug Discovery page, Ask tab: ask about a named
   compound's mechanism. Show it pulling from ChEMBL alongside PubMed.
4. **Structured extraction** — Drug Discovery page, Extract entities tab:
   ask a question about a compound/target and show the JSON output
   conforming to the domain's `extraction_schema` (targets/compounds/trial
   phases) — this is `output_config.format` constraining the final answer
   while the agent still used its tools to gather evidence.
5. **Multi-turn context** — ask a follow-up question in the same session to
   show conversation continuity; mention (don't need to demo live) that past
   8-10 turns this trims/summarizes automatically per `context_manager.py`.

## What to say if asked about the rest of the 20 steps

"Steps 13-18 (MCP servers, observability, load testing, knowledge vault,
graphify) and the formal eval/hillclimb loop (step 19) are scoped and
sequenced in the plan but intentionally deferred past this first demo — the
RAG engine and the dev workflow around it were the priority for a
defensible first POC."
