"""Embedding function for the vector store.

MVP: use ChromaDB's bundled local embedding function (ONNX MiniLM) — no
separate embeddings API key needed. Upgrade path: swap in a Voyage AI
embedding function (Anthropic's recommended embeddings partner) for better
retrieval quality; the vector_store module is the only caller, so the swap
is contained to one place.
"""
from __future__ import annotations

from chromadb.utils import embedding_functions

_default_ef = None


def get_embedding_function():
    global _default_ef
    if _default_ef is None:
        _default_ef = embedding_functions.DefaultEmbeddingFunction()
    return _default_ef
