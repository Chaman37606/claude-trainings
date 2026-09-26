import pytest
from src.models import Citation, Source, SourceType
from src.core import CitationValidator


def test_exact_match_citation():
    """Test that exact matches get full confidence."""
    validator = CitationValidator()
    source = Source(
        id="test_001",
        name="Test Source",
        type=SourceType.JOURNAL,
        domain="pharmacology",
        content="The drug reduced symptoms by 40% in clinical trials.",
        approved=True,
    )

    citation = Citation(
        source_id="test_001",
        source_name="Test Source",
        text="The drug reduced symptoms by 40% in clinical trials.",
        confidence=0.0,
        claim_supported="Drug efficacy",
    )

    validated = validator.validate_citations([citation], [source])
    assert validated[0].confidence == 1.0
    assert validated[0].validated is True


def test_missing_citation():
    """Test that missing citations get zero confidence."""
    validator = CitationValidator()
    source = Source(
        id="test_001",
        name="Test Source",
        type=SourceType.JOURNAL,
        domain="pharmacology",
        content="Some content here",
        approved=True,
    )

    citation = Citation(
        source_id="test_001",
        source_name="Test Source",
        text="This text does not appear in the source",
        confidence=0.0,
        claim_supported="Some claim",
    )

    validated = validator.validate_citations([citation], [source])
    assert validated[0].confidence == 0.0
    assert validated[0].validated is False


def test_fuzzy_match_citation():
    """Test that fuzzy matches get partial confidence."""
    validator = CitationValidator()
    source = Source(
        id="test_001",
        name="Test Source",
        type=SourceType.JOURNAL,
        domain="pharmacology",
        content="The medication demonstrated a 40% reduction in symptoms during the trial.",
        approved=True,
    )

    citation = Citation(
        source_id="test_001",
        source_name="Test Source",
        text="The drug reduced symptoms by 40% in trials.",
        confidence=0.0,
        claim_supported="Drug efficacy",
    )

    validated = validator.validate_citations([citation], [source])
    # Should have partial confidence for close match
    assert 0.5 < validated[0].confidence < 1.0
    assert validated[0].validated is True


def test_should_require_review():
    """Test that low-confidence citations trigger review."""
    validator = CitationValidator()

    citations = [
        Citation(
            source_id="test_001",
            source_name="Source 1",
            text="Some text",
            confidence=0.5,  # Below threshold
            claim_supported="Claim",
        ),
    ]

    assert validator.should_require_review(citations) is True


def test_no_review_needed():
    """Test that high-confidence citations don't require review."""
    validator = CitationValidator()

    citations = [
        Citation(
            source_id="test_001",
            source_name="Source 1",
            text="Some text",
            confidence=0.95,  # Above threshold
            claim_supported="Claim",
            validated=True,
        ),
    ]

    assert validator.should_require_review(citations) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
