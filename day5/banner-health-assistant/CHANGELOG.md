# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project doesn't
follow semantic versioning tags yet (no releases have been cut) — entries are grouped by when
the work happened instead.

## [Unreleased]

### Added
- `backend/config.py` centralizing environment-based configuration (`DATABASE_URL`,
  `CORS_ALLOW_ORIGINS`, `LOG_LEVEL`, `HOST`, `PORT`) — every value defaults to the prior
  hardcoded behavior.
- `GET /api/health` liveness/readiness endpoint (checks DB connectivity).
- Structured logging (Python `logging`, configurable via `LOG_LEVEL`) and a global unhandled-
  exception handler that logs server-side and returns a generic 500 instead of leaking a
  traceback.
- `Dockerfile`, `docker-compose.yml`, `.dockerignore` for containerized runs, with the SQLite
  file persisted to a named volume.
- `.env.example`, `.gitignore` (scoped to this project directory), `requirements-dev.txt`.
- `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- `docs/ARCHITECTURE.md`, `docs/RUNBOOK.md`.
- `spec.md` — formal API/data-model/business-rule contract.
- `agents/README.md` — record of the subagents used to build the backend, frontend, and tests.
- `performance/` — `load_test.py` (threads + httpx, no external framework) and
  `PERFORMANCE_REVIEW.md`, with a real finding: write throughput is flat at ~11 req/s regardless
  of concurrency while write latency grows linearly, consistent with SQLite's single-writer
  lock, not an application bug.
- `.claude/settings.json` — a small permission allowlist for this project.
- Pinned `backend/requirements.txt` versions (previously unpinned).

### Fixed
- Frontend: category badges showed raw enum text (e.g. `PRIOR_VISIT`) — now humanized
  (`PRIOR VISIT`). Relevance scores showed unrounded floats (`19.9091`) — now rounded to 1
  decimal with a proportional visual meter. Every summary card used the same accent color
  regardless of clinical urgency — now color-coded by urgency (active+recent vs. active vs.
  stable/historical), parsed from the item's `reason` text.

## Initial build

- FastAPI + SQLAlchemy + SQLite backend implementing the Banner Health case study's HLD/LLD:
  patient timeline ranking, pre-visit summary, SOAP-note drafting from an encounter transcript,
  physician edit/approve workflow, and an audit trail (`backend/`).
- Vanilla HTML/CSS/JS frontend against that API, no build step, no framework (`frontend/`).
- Pytest suite: unit tests for the ranking/drafting logic, integration tests for the full API
  workflow (`tests/`) — 17 tests, all passing.
