# Banner Health AI Clinical Assistant (Demo)

A working demo app implementing the **Banner Health: Reducing Physician Burnout** case study
(see [`../banner-health-physician-burnout.md`](../banner-health-physician-burnout.md) for the
original narrative, HLD, and LLD).

> The "AI" drafting and summarization logic here is a **deterministic, rule-based stand-in**
> (keyword/cue-phrase extraction for note drafting, category+recency scoring for ranking) —
> not a live LLM call. This keeps the demo self-contained, offline, and reproducibly testable
> while implementing the same mechanism the case study's LLD describes.

## Architecture

Maps onto the case study's HLD components:

| HLD component | Implementation |
|---|---|
| Encounter Capture | `POST /api/patients/{id}/encounters` |
| Drafting Engine | `engine.generate_draft_note()` + `POST /api/encounters/{id}/draft` |
| Patient Record Aggregator | `TimelineEvent` table + `GET /api/patients/{id}/timeline` |
| Summarization Engine | `engine.score_relevance()` + `GET /api/patients/{id}/summary` |
| Physician Review UI | `frontend/` draft editor panel |
| EHR Integration & Audit Layer | `AuditLog` table + `GET /api/audit`, `POST /api/encounters/{id}/approve` |

Stack: FastAPI + SQLAlchemy + SQLite backend, single-file vanilla HTML/CSS/JS frontend
(served as static files by the same FastAPI process — one process, one port).

## Running locally

```bash
cd "day5/banner-health-assistant"
uvicorn backend.main:app --reload --port 8000
```

Then open **http://localhost:8000/**. API docs at http://localhost:8000/docs.

The SQLite DB (`backend/banner_health.db`) is seeded automatically with sample patients and
timeline history on first startup.

## Tests

```bash
cd "day5/banner-health-assistant"
pytest tests -v
```

## API

See the contract in `tests/test_api.py` and `backend/main.py` for the authoritative routes;
summary:

- `GET /api/patients`
- `GET /api/patients/{id}/timeline`
- `GET /api/patients/{id}/summary`
- `POST /api/patients/{id}/encounters`
- `POST /api/encounters/{id}/draft`
- `GET /api/encounters/{id}/draft`
- `PUT /api/encounters/{id}/draft`
- `POST /api/encounters/{id}/approve`
- `GET /api/audit`
