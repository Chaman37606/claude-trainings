# Performance Review — Banner Health AI Clinical Assistant

Reviewed against the running app (`uvicorn main:app` on `http://127.0.0.1:8000`), using the
load-generation script in [`load_test.py`](load_test.py) (no external framework — threads +
`httpx`). Raw run data: [`results/`](results/).

## Summary

| Scenario | Concurrency | Throughput | p50 latency | p99 latency | Errors |
|---|---|---|---|---|---|
| Reads (`/patients`, `/timeline`, `/summary`) | 10 | 157 req/s | 55.8 ms | 106.5 ms | 0 |
| Reads | 8 | 192 req/s | 37.0 ms | 75.4 ms | 0 |
| Reads | 20 | 170 req/s | 98.7 ms | 187.5 ms | 0 |
| Write workflow (create → draft → edit → approve) | 8 | **11.0 req/s** | 412 ms | 2070 ms | 0 |
| Write workflow | 20 | **10.8 req/s** | 1214 ms | 4716 ms | 0 |

No errors at any concurrency tested — the app never falls over — but **write throughput is flat
at ~11 req/s regardless of concurrency, while write latency scales linearly with load**. That
combination (flat throughput + growing latency + zero errors) is the signature of requests
queuing behind a serialized resource rather than being processed in parallel.

## Root causes

1. **SQLite single-writer lock.** `database.py` points at one on-disk SQLite file
   (`sqlite:///banner_health.db`). SQLite allows many concurrent readers but only one writer at a
   time; every other writer blocks until the current transaction commits. At concurrency 20 the
   write path is 100% bottlenecked on this lock, not on CPU or the drafting logic itself — that's
   why adding more concurrent workers doesn't raise write throughput at all (10.95 → 10.83 req/s),
   it just makes each one wait longer in line (p99 2.07s → 4.72s).

2. **Two commits per logical write, doubling fsync cost.** Every write action does its state
   change and its audit-log write as two separate `db.commit()` calls (see
   `crud.generate_and_save_draft`, `update_draft`, `approve_draft`, each followed by its own
   `log_audit(...)` commit). SQLite's default durability mode fsyncs on every commit, so each
   logical action pays that cost twice. Wrapping the state change and its audit row in one
   transaction/commit would roughly halve this per-action overhead.

3. **Read cost is dominated by Python-side ranking, not the DB.** `get_ranked_timeline` and
   `get_patient_summary` (`crud.py`) fetch all of a patient's timeline events, then score and
   sort them in Python on *every* request — nothing is cached or precomputed. At the current demo
   scale (6–9 events/patient, from `seed.py`) that's why reads are fast (single-digit-ms DB work
   dominated by ~40-100ms of FastAPI/httpx/threadpool round-trip overhead in these numbers). It
   would not hold up at the population scale the original case study actually describes ("years
   of longitudinal history," "dozens of patients per week") — thousands of events per patient
   would make this O(n log n)-per-request scoring the dominant cost instead of a rounding error.

4. **`GET /api/audit` has no pagination or limit.** It returns the entire table, ordered by
   timestamp, on every call (`crud.list_audit_logs`). The write-workflow load test above alone
   added ~140 rows in a few seconds; this endpoint will get linearly slower as the demo
   accumulates history, with no way to page through it from the API today.

5. **Threadpool-bound concurrency, not asyncio.** Every route is a plain `def`, not `async def`
   (`main.py`), so FastAPI correctly runs each one in Starlette's worker threadpool rather than
   blocking the event loop — this was already done right and is why reads scale reasonably with
   concurrency. But it means true request-level parallelism is capped by the threadpool size
   (Starlette's default, currently unconfigured), which is fine for this demo's traffic but worth
   knowing if load ever increases.

## Recommendations, in priority order

1. **Merge the state-change commit and its audit-log commit into a single transaction** in
   `generate_and_save_draft` / `update_draft` / `approve_draft`. Cheapest fix here, roughly halves
   write-path fsync overhead, no architectural change.
2. **Add `limit`/`cursor` pagination to `GET /api/audit`** before it's exercised against
   anything beyond demo-scale history — right now it's an unbounded full-table read on every call.
3. **If this ever needs real concurrent writers** (multiple physicians charting simultaneously,
   which is the realistic version of the Banner Health case study), move off a single SQLite
   file to a server-based DB (Postgres) — SQLite's single-writer lock is the actual ceiling here,
   not the application code, and no amount of query tuning fixes that within SQLite for
   concurrent writes.
4. **Cache or incrementally maintain the relevance ranking** rather than recomputing it from
   scratch on every `timeline`/`summary` call, if/when per-patient event counts grow beyond the
   current demo's handful — matches the original case study's own LLD note about "delta
   processing" for recurring screening rather than full recomputation each time.

## Caveat

This is a demo app on SQLite with a single uvicorn worker on one machine — the goal of this
review is to catch real architectural bottlenecks and regressions early (the write-path
serialization above is a genuine one), not to establish a production capacity number. The
absolute req/s figures will vary run-to-run on shared/virtualized hardware; the *shape* of the
result (flat write throughput, linearly growing write latency, fast/scaling reads) is the
reliable finding, not the exact numbers.

## Reproducing

```bash
cd day5/banner-health-assistant
python3 performance/load_test.py --concurrency 10 --requests 200
python3 performance/load_test.py --include-writes --concurrency 20 --requests 200
```
