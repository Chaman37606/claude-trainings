"""Thin requests wrapper around the FastAPI backend — the frontend's only
coupling point to the backend, so the backend's internals can change freely.
"""
from __future__ import annotations

import os

import requests

BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")


def list_domains() -> list[dict]:
    resp = requests.get(f"{BASE_URL}/domains", timeout=10)
    resp.raise_for_status()
    return resp.json()["domains"]


def query(question: str, domain: str, session_id: str | None = None) -> dict:
    resp = requests.post(
        f"{BASE_URL}/query",
        json={"question": question, "domain": domain, "session_id": session_id},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def ingest(domain: str, source: str, query: str, max_results: int = 5) -> dict:
    resp = requests.post(
        f"{BASE_URL}/ingest",
        json={"domain": domain, "source": source, "query": query, "max_results": max_results},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def extract(question: str, domain: str = "drug_discovery") -> dict:
    resp = requests.post(
        f"{BASE_URL}/extract",
        json={"question": question, "domain": domain},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()
