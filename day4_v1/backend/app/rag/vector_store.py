"""ChromaDB wrapper — one persistent collection per domain."""
from __future__ import annotations

from functools import cache

import chromadb

from backend.app.config import settings
from backend.app.rag.embedder import get_embedding_function

_client = None


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


@cache
def get_collection(collection_name: str):
    return get_client().get_or_create_collection(
        name=collection_name,
        embedding_function=get_embedding_function(),
    )


def upsert_chunks(
    collection_name: str,
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    if not ids:
        return
    get_collection(collection_name).upsert(ids=ids, documents=documents, metadatas=metadatas)


def query(collection_name: str, query_text: str, top_k: int = 6) -> dict:
    collection = get_collection(collection_name)
    if collection.count() == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
    return collection.query(query_texts=[query_text], n_results=min(top_k, collection.count()))


def collection_count(collection_name: str) -> int:
    return get_collection(collection_name).count()


def existing_ids_for_paper(collection_name: str, paper_id: str) -> list[str]:
    collection = get_collection(collection_name)
    if collection.count() == 0:
        return []
    return collection.get(where={"paper_id": paper_id}).get("ids", [])


def chunks_for_paper(collection_name: str, paper_id: str) -> list[dict]:
    """All indexed chunks for one paper, ordered by chunk_index — used by the
    custom MCP server's get_paper tool (backend/app/routers has no equivalent
    "fetch one paper" route; this is retriever-adjacent, so it lives here
    rather than being reimplemented against Chroma a second time).
    """
    collection = get_collection(collection_name)
    if collection.count() == 0:
        return []
    result = collection.get(where={"paper_id": paper_id})
    rows = [
        {"text": doc, **meta}
        for doc, meta in zip(result.get("documents", []), result.get("metadatas", []))
    ]
    return sorted(rows, key=lambda r: r.get("chunk_index", 0))


def delete_ids(collection_name: str, ids: list[str]) -> None:
    if not ids:
        return
    get_collection(collection_name).delete(ids=ids)
