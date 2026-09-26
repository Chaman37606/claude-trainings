from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.domains.loader import (
    DomainConfigError,
    DomainNotFoundError,
    load_domain,
)
from backend.app.rag.ingest_pipeline import ingest_paper
from backend.app.tools.pubmed_tool import pubmed_search
from backend.app.tools.schemas import PubmedSearchInput, SemanticScholarSearchInput
from backend.app.tools.semantic_scholar_tool import semantic_scholar_search

router = APIRouter()

SUPPORTED_SOURCES = {"pubmed", "semantic_scholar"}


class IngestRequest(BaseModel):
    domain: str
    source: str
    query: str
    max_results: int = 5


class IngestResponse(BaseModel):
    papers_fetched: int
    chunks_indexed: int


def _ingest_search_results(domain, results: list[dict], source: str, paper_id_fn) -> tuple[int, int]:
    """Shared fetch->ingest loop for both sources below: skip papers with no
    abstract to index, otherwise chunk+embed+upsert and count it.
    """
    papers_fetched = 0
    chunks_indexed = 0
    for paper in results:
        if not paper["abstract"]:
            continue
        chunks_indexed += ingest_paper(
            domain=domain,
            paper_id=paper_id_fn(paper),
            title=paper["title"],
            text=paper["abstract"],
            source=source,
            url=paper["url"],
        )
        papers_fetched += 1
    return papers_fetched, chunks_indexed


@router.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    try:
        domain = load_domain(req.domain)
    except DomainNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if req.source not in SUPPORTED_SOURCES:
        raise HTTPException(status_code=400, detail=f"source must be one of {sorted(SUPPORTED_SOURCES)}")

    if req.source == "pubmed":
        result = pubmed_search(PubmedSearchInput(query=req.query, max_results=req.max_results))
        papers_fetched, chunks_indexed = _ingest_search_results(
            domain, result["results"], "pubmed", lambda p: f"pubmed:{p['pmid']}"
        )
    else:
        result = semantic_scholar_search(
            SemanticScholarSearchInput(query=req.query, limit=req.max_results)
        )
        papers_fetched, chunks_indexed = _ingest_search_results(
            domain, result["results"], "semantic_scholar", lambda p: f"s2:{p['paper_id']}"
        )

    return IngestResponse(papers_fetched=papers_fetched, chunks_indexed=chunks_indexed)
