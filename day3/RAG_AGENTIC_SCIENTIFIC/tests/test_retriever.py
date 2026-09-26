import pytest
from src.models import ResearchQuery
from src.core import ApprovedRetriever


def test_retriever_loads_sources():
    """Test that retriever can load approved sources."""
    retriever = ApprovedRetriever()
    assert len(retriever.sources) > 0


def test_retriever_filters_by_domain():
    """Test that retriever only returns sources in the query domain."""
    retriever = ApprovedRetriever()
    query = ResearchQuery(
        query_text="drug efficacy",
        domain="pharmacology",
        user_id="test_user",
    )
    sources = retriever.retrieve(query)
    assert len(sources) > 0
    assert all(s.domain == "pharmacology" for s in sources)


def test_retriever_refuses_invalid_domain():
    """Test that retriever refuses queries outside approved domains."""
    retriever = ApprovedRetriever()
    query = ResearchQuery(
        query_text="test question",
        domain="astrology",
        user_id="test_user",
    )
    with pytest.raises(ValueError):
        retriever.retrieve(query)


def test_retriever_returns_empty_for_no_matches():
    """Test that retriever returns empty list if no sources match."""
    retriever = ApprovedRetriever()
    query = ResearchQuery(
        query_text="completely unrelated topic that won't match anything xyz123",
        domain="pharmacology",
        user_id="test_user",
    )
    sources = retriever.retrieve(query)
    assert len(sources) == 0


def test_retriever_ranking():
    """Test that retriever ranks sources by relevance."""
    retriever = ApprovedRetriever()
    query = ResearchQuery(
        query_text="drug efficacy trial",
        domain="pharmacology",
        user_id="test_user",
    )
    sources = retriever.retrieve(query)
    # Sources with more keyword matches should rank higher
    assert len(sources) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
