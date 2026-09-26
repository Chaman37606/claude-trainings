"""Retrieval over a domain's indexed chunks: query -> cited chunks.

This is the shared retrieval core reused by the rag_search tool, the custom
MCP server (mcp_server/server.py), and knowledge-vault export — none of
those should reimplement Chroma access directly.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from backend.app.domains.loader import DomainConfig
from backend.app.observability.otel_setup import rag_retrieve_duration, tracer
from backend.app.rag import vector_store


@dataclass
class RetrievedChunk:
    text: str
    paper_id: str
    title: str
    source: str
    url: str
    distance: float


def retrieve(domain: DomainConfig, query_text: str, top_k: int | None = None) -> list[RetrievedChunk]:
    start = time.perf_counter()
    with tracer.start_as_current_span("rag.retrieve") as span:
        span.set_attribute("domain", domain.name)
        span.set_attribute("top_k", top_k or domain.top_k)

        raw = vector_store.query(domain.collection_name, query_text, top_k or domain.top_k)

        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        results = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            results.append(
                RetrievedChunk(
                    text=doc,
                    paper_id=meta.get("paper_id", ""),
                    title=meta.get("title", ""),
                    source=meta.get("source", ""),
                    url=meta.get("url", ""),
                    distance=dist,
                )
            )
        span.set_attribute("result_count", len(results))

    rag_retrieve_duration.record(time.perf_counter() - start, {"domain": domain.name})
    return results


def get_paper(domain: DomainConfig, paper_id: str) -> list[dict]:
    """All indexed chunks for one paper, in order — empty list if not indexed."""
    return vector_store.chunks_for_paper(domain.collection_name, paper_id)
