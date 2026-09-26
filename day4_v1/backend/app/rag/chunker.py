"""Splits fetched text (abstracts, full text) into overlapping chunks for embedding."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[Chunk]:
    """Character-based sliding-window chunking.

    Good enough for abstract-length text (the MVP corpus); swap for a
    token-aware or sentence-boundary splitter if/when full-text ingestion
    (fetch_fulltext_tool) is added.
    """
    text = text.strip()
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(text=piece, chunk_index=index))
            index += 1
        if end == len(text):
            break
        start = end - overlap
    return chunks
