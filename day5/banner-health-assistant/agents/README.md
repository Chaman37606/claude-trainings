# Build Agents

This app was built by three background subagents working from one fixed API contract
(see the root [`README.md`](../README.md)), so the backend and frontend could be built
concurrently without waiting on each other. This is a record of what each one did — not
runtime code for the app itself.

## 1. backend-agent

**Scope**: everything under [`backend/`](../backend/) — models, schemas, CRUD, the
drafting/relevance engine, seed data, and the FastAPI app itself.

**Delivered**:
- `database.py`, `models.py` (`Patient`, `TimelineEvent`, `Encounter`, `DraftNote`, `AuditLog`), `schemas.py`
- `engine.py` — pure, DB-free functions: `score_relevance()` (category weight + recency decay +
  active/recent-change bonuses) and `generate_draft_note()` (cue-phrase SOAP-section extraction)
- `crud.py` — DB access, ranked timeline/summary construction, draft generate/update/approve with
  audit logging
- `seed.py` — 4 sample patients with 6–9 timeline events each, idempotent on repeat calls
- `main.py` — the FastAPI app, wired to serve `frontend/` as static files at `/` with API routes
  registered first so they aren't shadowed
- `requirements.txt`

**Self-check**: ran a full functional smoke test via FastAPI's `TestClient` against every
endpoint before handing off (patients → timeline ordering → summary reasons → full
encounter/draft/approve/audit workflow → 404s). All passed; no bugs found later by test-agent.

## 2. frontend-agent

**Scope**: everything under [`frontend/`](../frontend/) — plain HTML/CSS/JS, no build step,
built directly against the fixed API contract (didn't need the backend to exist yet).

**Delivered**: `index.html`, `app.js`, `styles.css` implementing the patient sidebar, pre-visit
summary cards, collapsible full timeline, new-encounter form, editable SOAP draft with an inline
(non-`window.prompt`) approval flow, and an audit trail table — all wired via `addEventListener`,
no inline `onclick`.

**Self-check**: `node --check app.js` passed; cross-referenced every `getElementById` call
against `index.html` ids to confirm no dangling references. Couldn't run against a live backend
yet at that point (backend-agent was still working), so it wasn't visually verified in a browser —
that gap is exactly what surfaced the later "data visualization not looking good" feedback (see below).

## 3. test-agent

**Scope**: [`tests/`](../tests/) — pytest coverage for the backend, run to green.

**Delivered**: `conftest.py` (isolates tests on an in-memory SQLite DB via a `get_db` dependency
override, since `backend/` uses flat imports and a real on-disk DB), `test_engine.py` (8 unit
tests for the relevance scoring and drafting logic), `test_api.py` (9 integration tests covering
the full create → draft → edit → approve → audit workflow, sort order, and 404s).

**Result**: 17/17 passing, no backend bugs found — verified deterministic by deleting the real
DB file and re-running twice.

## Known gap this workflow exposed

None of the three agents ever *looked* at the rendered page — backend and test coverage was
solid, but the actual UI (raw enum badges like `PRIOR_VISIT`, unrounded relevance floats like
`19.9091`, and a single flat accent color regardless of clinical urgency) wasn't caught until a
human reviewed it visually. That fix was done directly (not by a subagent) using a headless-Chrome
screenshot to see the real rendered output before and after — see the root README's "Fixed"
section in the conversation history. Takeaway for next time: a visual/screenshot check belongs in
the frontend-agent's own self-check step, not left until after hand-off.
