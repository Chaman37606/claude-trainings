# Runbook

Operational how-to for running, checking, and troubleshooting this app. There's no CI/CD
pipeline (by design, for this project) — this document is the manual substitute for "how do I
know it's healthy" and "what do I do when it isn't."

## Starting it

**Local (no Docker):**
```bash
cd day5/banner-health-assistant
pip install -r requirements-dev.txt   # first time only
uvicorn backend.main:app --reload --port 8000
```

**Docker:**
```bash
cd day5/banner-health-assistant
docker compose up --build
```

Either way: **http://localhost:8000/** (frontend), **http://localhost:8000/docs** (interactive
API docs), **http://localhost:8000/api/health** (health check).

The SQLite DB auto-seeds 4 sample patients on first startup if empty — no separate seed step
needed.

## Stopping it

- Local: `Ctrl+C` in the terminal running uvicorn.
- Docker: `docker compose down` (add `-v` to also delete the persisted `banner_health_data`
  volume, i.e. wipe all data — see "Resetting to a clean state" below for why you'd want that
  without Docker too).

## Checking it's healthy

```bash
curl -s http://localhost:8000/api/health
# {"status": "ok", "db_connected": true}
```

`"status": "degraded"` (with `"db_connected": false`) means the process is up but can't reach
its database — check the DB file/volume exists and is writable, and check the process logs
(below) for the actual exception.

A quick smoke test of the full workflow:
```bash
curl -s http://localhost:8000/api/patients | python3 -m json.tool
```
Should return 4 seeded patients. If it returns `[]`, the DB exists but seeding didn't run or was
skipped — restart the process (seeding only runs against an empty `patients` table).

## Logs

Local: whatever terminal is running `uvicorn` — startup logs its DB URL and confirms seeding;
unhandled errors are logged with a full traceback (see `backend/main.py`'s exception handler)
before the client gets a generic 500.

Docker: `docker compose logs -f app`

Adjust verbosity with `LOG_LEVEL` (see `.env.example`) — e.g. `LOG_LEVEL=DEBUG`.

## Resetting to a clean state

The demo seed data and any encounters/drafts/audit history you've created live in one SQLite
file. To start over:

**Local:**
```bash
# stop the running server first
rm backend/banner_health.db
uvicorn backend.main:app --port 8000   # re-seeds automatically on startup
```

**Docker:**
```bash
docker compose down -v   # -v deletes the banner_health_data volume
docker compose up --build
```

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `curl: (7) Failed to connect` | Server not running, or wrong port | Check the process is up; confirm `--port`/`PORT` matches |
| `/api/health` returns `db_connected: false` | DB file/volume missing or not writable | Check `DATABASE_URL` path exists and the process has write access to its directory |
| Frontend loads but shows no patients | DB was reset but process wasn't restarted (seed only runs at startup) | Restart the process |
| Write requests (`POST`/`PUT`) get slow under load, but no errors | Expected — SQLite's single-writer lock; see `performance/PERFORMANCE_REVIEW.md` | Not a bug to "fix" at this scale; move to a server DB if you need real concurrent writers |
| `ModuleNotFoundError` when running tests | `backend/` not on `sys.path` | Run `pytest` from the project root (`tests/conftest.py` handles the path insertion) — don't `cd` into `tests/` first |
| Docker image builds but frontend 404s at `/` | `frontend/` wasn't copied into the image, or path mismatch | Confirm `Dockerfile` copies `frontend/` to `/app/frontend` and `backend/main.py`'s `_FRONTEND_DIR` resolves to the same place (`../frontend` relative to `backend/main.py`) |

## Backups

There is no automated backup job. The entire application state is the single SQLite file
(`backend/banner_health.db` locally, or the `banner_health_data` Docker volume) plus the audit
log inside it. To back it up: stop the process, copy the file (or `docker cp`/volume snapshot),
restart.

## Load/performance testing

See [`../performance/README.md`](../performance/README.md) — `python3 performance/load_test.py`
against a running instance. Read-only by default; pass `--include-writes` deliberately (it adds
real rows to whichever DB you point it at).
