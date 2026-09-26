from typing import List
from difflib import SequenceMatcher
from src.models import Citation, Source


class CitationValidator:
    def __init__(self, exact_match_threshold: float = 0.95, fuzzy_match_threshold: float = 0.7):
        self.exact_match_threshold = exact_match_threshold
        self.fuzzy_match_threshold = fuzzy_match_threshold

    def validate_citations(self, citations: List[Citation], sources: List[Source]) -> List[Citation]:
        """
        Validate each citation against retrieved sources.
        Returns citations with confidence scores and validated flag set.
        """
        validated_citations = []
        source_map = {s.id: s for s in sources}

        for citation in citations:
            source = source_map.get(citation.source_id)
            if not source:
                # Source not found - zero confidence
                citation.confidence = 0.0
                citation.validated = False
            else:
                confidence = self._calculate_confidence(citation.text, source.content)
                citation.confidence = confidence
                citation.validated = confidence >= self.fuzzy_match_threshold

            validated_citations.append(citation)

        return validated_citations

    def _calculate_confidence(self, citation_text: str, source_content: str) -> float:
        """
        Calculate confidence that citation exists in source.
        - 1.0: Exact match found
        - 0.7-0.99: Fuzzy match (paraphrase detected)
        - <0.7: Citation not found or severely paraphrased
        """
        citation_lower = citation_text.lower().strip()
        content_lower = source_content.lower()

        # Check for exact match
        if citation_lower in content_lower:
            return 1.0

        # Check for substring match (citation is subset of source)
        if len(citation_lower) > 10:
            # For longer citations, look for key phrases
            words = citation_lower.split()
            if len(words) > 2:
                key_phrase = " ".join(words[: min(5, len(words))])
                if key_phrase in content_lower:
                    return 0.95

        # Fuzzy matching using SequenceMatcher
        ratio = SequenceMatcher(None, citation_lower, content_lower).ratio()
        if ratio >= self.exact_match_threshold:
            return 0.95

        # Check for major keywords presence
        words = citation_lower.split()
        important_words = [w for w in words if len(w) > 4]
        if important_words:
            word_match_count = sum(1 for w in important_words if w in content_lower)
            word_match_ratio = word_match_count / len(important_words)
            if word_match_ratio > 0.7:
                return 0.75

        # No match found
        return 0.0

    def should_require_review(self, citations: List[Citation]) -> bool:
        """
        Determine if response needs human review based on citation confidence.
        Returns True if any citation has confidence < fuzzy_match_threshold.
        """
        for citation in citations:
            if citation.confidence < self.fuzzy_match_threshold:
                return True
        return False

    def get_unvalidated_citations(self, citations: List[Citation]) -> List[Citation]:
        """Get list of citations that failed validation."""
        return [c for c in citations if not c.validated]

    def get_low_confidence_citations(self, citations: List[Citation], threshold: float = 0.75) -> List[Citation]:
        """Get citations below confidence threshold."""
        return [c for c in citations if c.confidence < threshold]
