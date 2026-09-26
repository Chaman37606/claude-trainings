"""Coverage for retriever.get_paper / vector_store.chunks_for_paper — the
lookup the custom MCP server's get_paper tool relies on.
"""
import uuid

import pytest

from backend.app.domains.loader import load_domain
from backend.app.rag.ingest_pipeline import ingest_paper
from backend.app.rag.retriever import get_paper


@pytest.fixture
def domain():
    return load_domain("general_biomedical")


@pytest.fixture(autouse=True)
def _isolated_collection(isolated_chroma):
    yield


def test_get_paper_returns_chunks_in_order(domain):
    paper_id = f"test:{uuid.uuid4()}"
    long_text = "EGFR inhibitors show efficacy in NSCLC. " * 80  # multiple chunks
    n_chunks = ingest_paper(domain=domain, paper_id=paper_id, title="v1", text=long_text, source="pubmed")
    assert n_chunks > 1

    chunks = get_paper(domain, paper_id)
    assert len(chunks) == n_chunks
    assert [c["chunk_index"] for c in chunks] == sorted(c["chunk_index"] for c in chunks)
    assert all(c["paper_id"] == paper_id for c in chunks)


def test_get_paper_returns_empty_for_unknown_paper(domain):
    assert get_paper(domain, "does-not-exist") == []
