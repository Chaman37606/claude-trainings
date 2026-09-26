"""Integration tests for the full RAG loop."""

import pytest
from src.models import ResearchQuery, ConfidenceLevel
from src.core import ApprovedRetriever, CitationValidator, LLMReasoner, AuditTrail
from src.database import init_db, SessionLocal


def test_full_rag_loop():
    """Test complete query -> retrieval -> reasoning -> validation loop."""
    init_db()
    db = SessionLocal()

    try:
        # Create query
        query = ResearchQuery(
            query_text="What is the efficacy of drug X for condition Y?",
            domain="pharmacology",
            user_id="test_researcher",
        )

        # Retrieve sources
        retriever = ApprovedRetriever()
        sources = retriever.retrieve(query)
        assert len(sources) > 0, "Should retrieve at least one source"

        # Generate answer
        reasoner = LLMReasoner()
        auditor = AuditTrail(db)
        audit_id = auditor.create_audit_id()

        response, requires_review = reasoner.reason(query, sources, audit_id)
        assert response.answer is not None
        assert response.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]

        # Validate citations
        validator = CitationValidator()
        response.citations = validator.validate_citations(response.citations, sources)

        # Should have citations
        assert len(response.citations) > 0, "Response should have citations"

        # All citations should reference valid sources
        source_ids = {s.id for s in sources}
        for citation in response.citations:
            assert citation.source_id in source_ids

    finally:
        db.close()


def test_audit_trail_recording():
    """Test that audit trail is properly recorded."""
    init_db()
    db = SessionLocal()

    try:
        auditor = AuditTrail(db)
        audit_id = auditor.create_audit_id()

        query = ResearchQuery(
            query_text="Test question",
            domain="pharmacology",
            user_id="test_user",
        )

        # Log query
        query_id = auditor.log_query_submission(query, audit_id)
        assert query_id is not None

        # Export audit trail
        audit_data = auditor.export_audit_trail(audit_id)
        assert "audit_id" in audit_data
        assert audit_data["audit_id"] == audit_id
        assert len(audit_data["timeline"]) > 0

    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
