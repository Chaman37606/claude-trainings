"""Regression coverage for ingest_pipeline's re-ingestion semantics — a paper
re-ingested with fewer chunks must not leave stale chunks behind in Chroma.
"""
import uuid

import pytest

from backend.app.domains.loader import load_domain
from backend.app.rag import vector_store
from backend.app.rag.ingest_pipeline import ingest_paper
from backend.app.rag.retriever import retrieve


@pytest.fixture
def domain():
    return load_domain("general_biomedical")


@pytest.fixture(autouse=True)
def _isolated_collection(isolated_chroma):
    yield


def test_reingesting_with_fewer_chunks_removes_stale_ones(domain):
    paper_id = f"test:{uuid.uuid4()}"

    long_text = "EGFR inhibitors show efficacy in NSCLC. " * 80  # many chunks
    n_chunks_first = ingest_paper(
        domain=domain, paper_id=paper_id, title="v1", text=long_text, source="pubmed"
    )
    assert n_chunks_first > 1

    short_text = "EGFR inhibitors show efficacy in NSCLC."  # one chunk
    n_chunks_second = ingest_paper(
        domain=domain, paper_id=paper_id, title="v2", text=short_text, source="pubmed"
    )
    assert n_chunks_second == 1

    remaining_ids = vector_store.existing_ids_for_paper(domain.collection_name, paper_id)
    assert remaining_ids == [f"{paper_id}:0"]

    # the stale chunks must not still be retrievable
    hits = retrieve(domain, "EGFR inhibitors NSCLC", top_k=10)
    matching = [h for h in hits if h.paper_id == paper_id]
    assert len(matching) == 1
    assert matching[0].title == "v2"
