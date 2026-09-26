"""Fetch -> chunk -> embed -> upsert orchestration for a single paper's text."""
from __future__ import annotations

from backend.app.domains.loader import DomainConfig
from backend.app.rag import vector_store
from backend.app.rag.chunker import chunk_text


def ingest_paper(
    domain: DomainConfig,
    paper_id: str,
    title: str,
    text: str,
    source: str,
    url: str | None = None,
) -> int:
    """Chunk and index one paper's text under the domain's collection.

    Idempotent: chunk IDs are deterministic (paper_id + chunk_index), and
    re-ingestion is a full replace — any chunk id left over from a prior
    ingestion of this paper_id that isn't in the new chunk set is deleted,
    so a paper re-ingested with fewer chunks doesn't leave stale, permanently
    retrievable chunks behind.
    Returns the number of chunks indexed.
    """
    chunks = chunk_text(text, chunk_size=domain.chunk_size, overlap=domain.chunk_overlap)

    ids = [f"{paper_id}:{c.chunk_index}" for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [
        {
            "paper_id": paper_id,
            "title": title,
            "source": source,
            "url": url or "",
            "chunk_index": c.chunk_index,
        }
        for c in chunks
    ]

    existing_ids = vector_store.existing_ids_for_paper(domain.collection_name, paper_id)
    stale_ids = [i for i in existing_ids if i not in set(ids)]

    if ids:
        vector_store.upsert_chunks(domain.collection_name, ids, documents, metadatas)
    vector_store.delete_ids(domain.collection_name, stale_ids)

    return len(chunks)
