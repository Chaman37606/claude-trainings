# Contributing

This is a demo/educational project (see [`spec.md`](spec.md) §1 for what it deliberately is and
isn't), but it follows normal project hygiene so it's a reasonable template to build from.

## Getting set up

```bash
cd day5/banner-health-assistant
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # optional — every setting has a working default
uvicorn backend.main:app --reload --port 8000   # or: cd backend && uvicorn main:app --reload
```

Backend modules use flat imports (`from database import Base`, not `from .database import Base`)
and expect `backend/` itself as the import root — see the note at the top of
`tests/conftest.py` if you're adding a new module there.

## Before opening a PR

1. **Run the test suite**: `pytest tests -v` — all tests must pass. Add tests for new behavior;
   see `tests/test_engine.py` (pure-function unit tests) and `tests/test_api.py` (integration
   tests via `TestClient`) for the existing patterns.
2. **Run the load test** if you touched `backend/crud.py` or the DB schema:
   `python3 performance/load_test.py --include-writes` — compare against
   `performance/PERFORMANCE_REVIEW.md`'s baseline numbers and update that doc if the shape of
   the result changed (not just the exact numbers, which vary run to run).
3. **Keep `spec.md` in sync.** It's the authoritative contract for the API, data model, and
   business rules (relevance scoring, drafting cue-phrases, audit logging). If your change
   alters any of those, update `spec.md` in the same PR — don't let it drift from the code.
4. **No new external LLM/network calls** without discussion — the drafting/summarization
   engines are deliberately deterministic and offline (see `spec.md` §1). If you're adding a
   real model-backed engine, that's a design change, not a drop-in patch.

## Code style

- Backend: standard PEP 8, type hints on new function signatures where practical. No enforced
  formatter/linter is wired up yet — match the existing style in the file you're editing.
- Frontend: plain HTML/CSS/JS, no build step, no framework, no external CDN dependencies (see
  `agents/README.md` for why). Wire events via `addEventListener` in `app.js`, not inline
  `onclick=` in `index.html`.

## Reporting bugs / proposing features

Open an issue describing the current behavior, expected behavior, and (for bugs) how to
reproduce it locally. There's no CI pipeline on this project — a PR is expected to include
evidence it was actually run (test output, or a `curl`/screenshot showing the fix) rather than
relying on an automated check to catch problems.

## Security issues

Don't open a public issue — see [`SECURITY.md`](SECURITY.md).
