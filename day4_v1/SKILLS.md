# Project-specific Claude Code skills

This project doesn't yet ship a custom `.claude/skills/` skill of its own —
domain and tool behavior is data-driven (YAML configs + Python tool modules),
so most "how do I extend this" questions are answered by editing config
rather than by a skill. This file exists as the place to document one if that
changes (e.g. a skill that scaffolds a new domain YAML + tool stub together).

## Skills this project relies on (already installed, not project-specific)

- `claude-api` — reference for the Anthropic Python SDK patterns used
  throughout `backend/app/agent/` and `backend/app/tools/` (manual tool-use
  loop, structured outputs via `output_config.format`, model IDs).
- `graphify` — used in the Operations & Scaling phase to build a knowledge
  graph over the paper corpus / extracted entities (see
  `docs/observability_setup.md` and the AI-DLC plan's step 18).
- `code-review` — run against diffs before merge, per the delegation rules
  in `CLAUDE.md` (also see `.claude/agents/p3-triage-agent.md`).

## Conventions for future skills in this repo

If a project-specific skill is added (e.g. `add-domain`, `seed-corpus`),
document it here with: what it's for, its trigger phrase, and which files it
touches — so `p3-triage-agent` and the delegation table in `CLAUDE.md` can be
kept in sync.
