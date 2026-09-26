# Problem Statement (AI-DLC Step 1) & AIDLC Plan (Step 2)

## Problem

Biomedical researchers and drug-discovery teams need to synthesize findings
across a fast-moving literature (PubMed, preprints, ChEMBL bioactivity data)
without either (a) manually searching three separate systems, or (b) trusting
an LLM's un-cited recall. They also frequently need structured facts —
targets, compounds, mechanisms, trial phases — pulled out of prose, not just
a prose summary.

## Who this is for

- A researcher doing a literature review across a biomedical subfield
  (oncology, cardiology, neurology, or general biomedicine), who wants a
  cited, current answer rather than a static pre-trained-knowledge response.
- A drug-discovery analyst who additionally wants structured entity
  extraction (targets/compounds/mechanisms/trial phases) grounded in
  ChEMBL and literature evidence.

## What the product is

An agentic RAG app: a Claude-powered agent with tools to search PubMed,
Semantic Scholar, and ChEMBL live, an index (ChromaDB) of what it has already
fetched so repeat questions don't re-fetch, and a domain-config layer so
"which tools, which prompt, which extraction schema" is data, not code.
FastAPI backend, Streamlit frontend, one Chroma collection per domain.

## AIDLC plan (step 2)

The full 20-step build plan (5 phases: Planning, Agent Setup, Platform
Engineering, Operations & Scaling, Validation & Rollout) is captured in the
session's approved plan file and reflected in this repo's structure — see
`CLAUDE.md` for the delegation rules and `.claude/agents/` for the
frontend/backend/triage subagents it set up. Build order actually followed:
MVP (domain configs → tools → RAG engine → agent loop → FastAPI → Streamlit
→ tests) first, dev-workflow scaffolding (subagents, hooks) alongside it,
with MCP servers, observability, load testing, knowledge vault, graphify,
and eval/hillclimb as explicitly deferred follow-on phases (see `docs/demo_script.md`
for what's demoable today vs. what's still pending).
