# Performance

Start with [`PERFORMANCE_REVIEW.md`](PERFORMANCE_REVIEW.md) — the actual findings (SQLite's
single-writer lock is the real bottleneck here, not application code) and recommendations.
`load_test.py` below is the tool used to produce the numbers in that review, kept here so the
review is reproducible rather than a one-off.

## The load test tool

A lightweight concurrent load test for the running app — no external load-testing framework
(no locust), just threads + `httpx` (already a project dependency via `tests/`).

## Run it

The app must already be running (`uvicorn main:app` from `backend/`, or via the root README's
instructions).

```bash
cd day5/banner-health-assistant
python3 performance/load_test.py
```

By default it only hits the read endpoints (`/api/patients`, `/api/patients/{id}/timeline`,
`/api/patients/{id}/summary`) — safe to run repeatedly since they don't write anything.

To also exercise the write workflow (create encounter → generate draft → edit → approve),
opt in explicitly — this adds real rows to `backend/banner_health.db` each run:

```bash
python3 performance/load_test.py --include-writes
```

Useful flags: `--concurrency N` (parallel worker threads, default 10), `--requests N` (total
requests per scenario, default 100), `--base-url` (default `http://127.0.0.1:8000`), `--out`
(where to save the JSON summary; defaults under `performance/results/`).

## What it reports

Per scenario: request count, error count/rate, wall-clock throughput (req/s), and latency
percentiles (min/mean/p50/p95/p99/max) in milliseconds. Results are also written as JSON to
`performance/results/run_<timestamp>.json` for later comparison.

## Why this shape

This is a demo app on SQLite with a single uvicorn worker — the point of this script isn't to
find a production capacity ceiling, it's to catch obvious regressions (e.g. an endpoint that
used to respond in 5ms suddenly taking 500ms) and to make relative comparisons (read vs. write
cost) visible with a single command, without pulling in a heavier tool.
