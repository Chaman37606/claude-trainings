#!/usr/bin/env python3
"""Simple concurrent load test for the Banner Health Assistant API.

No external load-testing framework required (no locust) — just threads + httpx.
Read endpoints (patients/timeline/summary) are hammered by default since they're
idempotent. The write workflow (create encounter -> draft -> edit -> approve) is
opt-in via --include-writes since each run leaves new rows in the SQLite DB.

Usage:
    python3 performance/load_test.py
    python3 performance/load_test.py --base-url http://127.0.0.1:8000 --concurrency 20 --requests 200
    python3 performance/load_test.py --include-writes --concurrency 5 --requests 25
"""
import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx


def timed_request(client: httpx.Client, method: str, path: str, **kwargs):
    start = time.perf_counter()
    error = None
    status = None
    try:
        resp = client.request(method, path, **kwargs)
        status = resp.status_code
        if resp.status_code >= 400:
            error = f"HTTP {resp.status_code}"
    except Exception as exc:  # noqa: BLE001 - report any failure as a data point
        error = str(exc)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"elapsed_ms": elapsed_ms, "status": status, "error": error}


def run_read_scenario(base_url: str, patient_ids: list[int], n: int) -> list[dict]:
    results = []
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        for i in range(n):
            pid = patient_ids[i % len(patient_ids)]
            endpoint = [
                "/api/patients",
                f"/api/patients/{pid}/timeline",
                f"/api/patients/{pid}/summary",
            ][i % 3]
            results.append(timed_request(client, "GET", endpoint))
    return results


def run_write_scenario(base_url: str, patient_ids: list[int], n: int) -> list[dict]:
    results = []
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        for i in range(n):
            pid = patient_ids[i % len(patient_ids)]
            t0 = time.perf_counter()
            error = None
            try:
                enc = client.post(
                    f"/api/patients/{pid}/encounters",
                    json={
                        "encounter_type": "Office Visit",
                        "transcript": "Patient reports fatigue. BP 118/76. Assessment: stable. Plan: recheck in 3 months.",
                    },
                ).raise_for_status().json()
                client.post(f"/api/encounters/{enc['id']}/draft").raise_for_status()
                client.put(
                    f"/api/encounters/{enc['id']}/draft",
                    json={"plan": "Recheck in 3 months; load-test generated."},
                ).raise_for_status()
                resp = client.post(
                    f"/api/encounters/{enc['id']}/approve",
                    json={"approved_by": "Load Test Bot"},
                )
                status = resp.status_code
                resp.raise_for_status()
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
                status = getattr(exc, "response", None) and exc.response.status_code
            elapsed_ms = (time.perf_counter() - t0) * 1000
            results.append({"elapsed_ms": elapsed_ms, "status": status, "error": error})
    return results


def summarize(label: str, results: list[dict], wall_seconds: float) -> dict:
    latencies = sorted(r["elapsed_ms"] for r in results)
    errors = [r for r in results if r["error"]]
    n = len(latencies)

    def pct(p):
        if not latencies:
            return 0.0
        idx = min(n - 1, int(round(p / 100 * n)) - 1)
        return latencies[max(0, idx)]

    summary = {
        "scenario": label,
        "requests": n,
        "errors": len(errors),
        "error_rate_pct": round(100 * len(errors) / n, 2) if n else 0.0,
        "wall_seconds": round(wall_seconds, 3),
        "throughput_rps": round(n / wall_seconds, 2) if wall_seconds > 0 else 0.0,
        "latency_ms": {
            "min": round(min(latencies), 2) if latencies else 0.0,
            "mean": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "p50": round(pct(50), 2),
            "p95": round(pct(95), 2),
            "p99": round(pct(99), 2),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
    }
    return summary


def print_summary(summary: dict):
    print(f"\n--- {summary['scenario']} ---")
    print(f"requests: {summary['requests']}  errors: {summary['errors']} ({summary['error_rate_pct']}%)")
    print(f"wall time: {summary['wall_seconds']}s  throughput: {summary['throughput_rps']} req/s")
    lat = summary["latency_ms"]
    print(f"latency ms  min={lat['min']}  mean={lat['mean']}  p50={lat['p50']}  p95={lat['p95']}  p99={lat['p99']}  max={lat['max']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--concurrency", type=int, default=10, help="parallel worker threads")
    parser.add_argument("--requests", type=int, default=100, help="total requests per scenario")
    parser.add_argument("--include-writes", action="store_true", help="also run the create/draft/edit/approve write workflow (adds rows to the DB)")
    parser.add_argument("--out", default=None, help="optional path to write JSON results")
    args = parser.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=10.0) as client:
        patients = client.get("/api/patients").raise_for_status().json()
    patient_ids = [p["id"] for p in patients]
    if not patient_ids:
        raise SystemExit("No patients found — is the server running and seeded?")

    all_summaries = []

    # Split total requests evenly across worker threads.
    per_worker = max(1, args.requests // args.concurrency)
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(run_read_scenario, args.base_url, patient_ids, per_worker) for _ in range(args.concurrency)]
        read_results = [r for f in as_completed(futures) for r in f.result()]
    wall = time.perf_counter() - start
    summary = summarize(f"Read endpoints (concurrency={args.concurrency})", read_results, wall)
    print_summary(summary)
    all_summaries.append(summary)

    if args.include_writes:
        write_n = min(args.requests, args.concurrency * 5)  # keep write volume sane
        per_worker_w = max(1, write_n // args.concurrency)
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [pool.submit(run_write_scenario, args.base_url, patient_ids, per_worker_w) for _ in range(args.concurrency)]
            write_results = [r for f in as_completed(futures) for r in f.result()]
        wall = time.perf_counter() - start
        summary = summarize(f"Write workflow (concurrency={args.concurrency})", write_results, wall)
        print_summary(summary)
        all_summaries.append(summary)

    out_path = args.out or str(Path(__file__).parent / "results" / f"run_{int(time.time())}.json")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(all_summaries, indent=2))
    print(f"\nSaved results to {out_path}")


if __name__ == "__main__":
    main()
