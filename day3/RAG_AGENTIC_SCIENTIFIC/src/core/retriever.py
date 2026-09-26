import json
from typing import List
from pathlib import Path
from src.models import Source, ResearchQuery, SourceType
from src.config import load_approved_sources, is_approved_source, is_valid_domain


class ApprovedRetriever:
    def __init__(self):
        self.sources_data = load_approved_sources()
        self.sources = self._parse_sources()

    def _parse_sources(self) -> List[Source]:
        sources = []
        for s in self.sources_data["sources"]:
            source = Source(
                id=s["id"],
                name=s["name"],
                type=SourceType(s["type"]),
                domain=s["domain"],
                approved=s.get("approved", True),
                content=s["content"],
                metadata=s.get("metadata", {}),
            )
            sources.append(source)
        return sources

    def retrieve(self, query: ResearchQuery) -> List[Source]:
        """
        Retrieve evidence from approved sources matching the query.
        Only returns approved sources in the query's domain.
        Raises exception if query is outside approved domains.
        """
        # Validate domain
        if not is_valid_domain(query.domain):
            raise ValueError(
                f"Domain '{query.domain}' is not in approved domains: {', '.join(['pharmacology', 'immunology', 'oncology'])}"
            )

        # Filter by domain and approved status
        matching_sources = [
            s
            for s in self.sources
            if s.domain == query.domain and s.approved and is_approved_source(s.id)
        ]

        if not matching_sources:
            return []

        # Simple keyword matching: rank by relevance
        ranked_sources = self._rank_by_relevance(query.query_text, matching_sources)
        return ranked_sources

    def _rank_by_relevance(self, query_text: str, sources: List[Source]) -> List[Source]:
        """
        Simple ranking: count keyword matches in source content.
        Higher match count = higher relevance.
        """
        query_words = set(query_text.lower().split())

        def relevance_score(source: Source) -> int:
            content_lower = source.content.lower()
            return sum(1 for word in query_words if word in content_lower)

        ranked = sorted(sources, key=relevance_score, reverse=True)
        return ranked

    def get_source_by_id(self, source_id: str) -> Source:
        """Retrieve a specific source by ID."""
        for source in self.sources:
            if source.id == source_id:
                return source
        raise ValueError(f"Source {source_id} not found")
