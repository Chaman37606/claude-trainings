# Banner Health AI Clinical Assistant (Demo)

A working demo app implementing the **Banner Health: Reducing Physician Burnout** case study
(see [`../banner-health-physician-burnout.md`](../banner-health-physician-burnout.md) for the
original narrative, HLD, and LLD).

> The "AI" drafting and summarization logic here is a **deterministic, rule-based stand-in**
> (keyword/cue-phrase extraction for note drafting, category+recency scoring for ranking) —
> not a live LLM call. This keeps the demo self-contained, offline, and reproducibly testable
> while implementing the same mechanism the case study's LLD describes.

## Documentation map

| Doc | What's in it |
|---|---|
| [`spec.md`](spec.md) | Authoritative API/data-model/business-rule contract |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Component/sequence diagrams, why-these-choices |
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Start/stop/health-check/troubleshoot/backup |
| [`performance/PERFORMANCE_REVIEW.md`](performance/PERFORMANCE_REVIEW.md) | Load-test findings (SQLite write bottleneck) |
| [`agents/README.md`](agents/README.md) | How this was built (backend/frontend/test subagents) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md) | Standard project policies |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed and when |
| [`.env.example`](.env.example) | Configurable environment variables |

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
(served as static files by the same FastAPI process — one process, one port). See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for diagrams and the reasoning behind each choice.

## Running it

**Local:**
```bash
cd day5/banner-health-assistant
pip install -r requirements-dev.txt
uvicorn backend.main:app --reload --port 8000
```

**Docker:**
```bash
cd day5/banner-health-assistant
docker compose up --build
```

Either way: **http://localhost:8000/** (frontend) · **http://localhost:8000/docs** (interactive
API docs) · **http://localhost:8000/api/health** (health check). The DB auto-seeds sample
patients on first startup. Every config value (`DATABASE_URL`, `CORS_ALLOW_ORIGINS`, `LOG_LEVEL`,
`HOST`/`PORT`) has a working default — see [`.env.example`](.env.example) to override any of
them. Full operational detail (stopping, logs, resetting, troubleshooting table): [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## Tests

```bash
cd day5/banner-health-assistant
pytest tests -v
```

17 tests: unit coverage for the relevance-scoring and drafting logic
(`tests/test_engine.py`), integration coverage for the full API workflow
(`tests/test_api.py`), isolated from the real DB via an in-memory SQLite override
(`tests/conftest.py`).

## Performance

```bash
python3 performance/load_test.py --include-writes
```

See [`performance/PERFORMANCE_REVIEW.md`](performance/PERFORMANCE_REVIEW.md) for the actual
finding: write throughput is flat regardless of concurrency while write latency grows linearly —
SQLite's single-writer lock, not application code. Read-only by default; `--include-writes` is
opt-in since it adds real rows to whichever DB it's pointed at.

## API

Full contract with request/response shapes: [`spec.md`](spec.md) §4. Routes:

- `GET /api/health`
- `GET /api/patients`
- `GET /api/patients/{id}/timeline`
- `GET /api/patients/{id}/summary`
- `POST /api/patients/{id}/encounters`
- `POST /api/encounters/{id}/draft`
- `GET /api/encounters/{id}/draft`
- `PUT /api/encounters/{id}/draft`
- `POST /api/encounters/{id}/approve`
- `GET /api/audit`

## License

[MIT](LICENSE)
