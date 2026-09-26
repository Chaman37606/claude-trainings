# Architecture

Formalizes the case study's HLD/LLD into the actual system. For exact API/data contracts, see
[`../spec.md`](../spec.md) — this document is about how the pieces fit together, not the field-
level detail.

## Component diagram

```mermaid
flowchart LR
    subgraph Browser
        FE[frontend/ — vanilla HTML/CSS/JS]
    end

    subgraph "uvicorn process (single)"
        API[FastAPI app — backend/main.py]
        ENG["Drafting + relevance engine\n(backend/engine.py, pure functions)"]
        CRUD[backend/crud.py]
    end

    DB[(SQLite file\nbackend/banner_health.db)]

    FE -- "fetch /api/*" --> API
    FE -- "GET / (static)" --> API
    API --> CRUD
    CRUD --> ENG
    CRUD -- "SQLAlchemy ORM" --> DB
```

One process serves both the API and the static frontend (`StaticFiles` mounted at `/` in
`main.py`, registered *after* the API routes so they aren't shadowed) — there's no separate
frontend server or build step.

## Request flow: the core workflow

```mermaid
sequenceDiagram
    participant P as Physician (browser)
    participant API as FastAPI
    participant ENG as engine.py
    participant DB as SQLite

    P->>API: POST /api/patients/{id}/encounters {transcript}
    API->>DB: insert Encounter
    P->>API: POST /api/encounters/{id}/draft
    API->>ENG: generate_draft_note(transcript)
    ENG-->>API: {subjective, objective, assessment, plan}
    API->>DB: upsert DraftNote (status=draft) + insert AuditLog(generate_draft)
    P->>API: PUT /api/encounters/{id}/draft {plan: "..."}
    API->>DB: update DraftNote, append edit_history + insert AuditLog(edit_draft)
    P->>API: POST /api/encounters/{id}/approve {approved_by}
    API->>DB: DraftNote.status=approved, finalized_at + insert AuditLog(approve_note)
```

Each of the three write actions above is committed to the DB as its own transaction *plus* a
separate audit-log commit — see `performance/PERFORMANCE_REVIEW.md` §Root causes for the cost
implication of that.

## Why these choices

| Decision | Why | Trade-off accepted |
|---|---|---|
| Rule-based drafting/ranking, not a real LLM | Self-contained, offline, deterministic — reproducible in tests and demos | Not real clinical NLP; see `spec.md` §1 |
| SQLite, single file | Zero setup, matches the sibling `eli_lilly_alcoa_app/` convention in this workspace | Single-writer lock caps concurrent write throughput — see performance review |
| One process serves API + static frontend | Simplest possible local/Docker deployment — one port, one command | No CDN/edge caching for static assets; irrelevant at this scale |
| Flat imports in `backend/` (`from database import Base`) | Matches the sibling app's convention; `backend/` is meant to be the import root | `tests/conftest.py` must manually insert `backend/` onto `sys.path` — documented there |
| No auth | Out of scope for a demo (see `spec.md` §7) | Not safe to expose beyond localhost as-is — see `SECURITY.md` |

## Where to look for what

- **API/data contract**: `spec.md`
- **Operational how-to** (start/stop/troubleshoot/backup): `docs/RUNBOOK.md`
- **Performance characteristics and bottlenecks**: `performance/PERFORMANCE_REVIEW.md`
- **How this was built** (which subagent did what): `agents/README.md`
- **Config knobs**: `.env.example`, `backend/config.py`
