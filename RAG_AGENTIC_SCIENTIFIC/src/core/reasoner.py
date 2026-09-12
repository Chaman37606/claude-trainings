import json
import re
from typing import List, Tuple
from anthropic import Anthropic
from src.models import ResearchQuery, ResearchResponse, Citation, ConfidenceLevel, Source


class LLMReasoner:
    def __init__(self, model: str = "claude-opus-4-1-20250805", use_stub: bool = False):
        self.client = Anthropic() if not use_stub else None
        self.model = model
        self.use_stub = use_stub

    def reason(
        self, query: ResearchQuery, sources: List[Source], audit_id: str
    ) -> Tuple[ResearchResponse, bool]:
        """
        Generate answer grounded in provided sources.
        Returns (ResearchResponse, requires_review).

        If insufficient evidence, refuses to answer.
        """
        if not sources:
            return (
                ResearchResponse(
                    answer="Insufficient evidence. No approved sources found matching your query.",
                    confidence=ConfidenceLevel.LOW,
                    citations=[],
                    gaps=["No relevant sources available in approved corpus"],
                    audit_id=audit_id,
                    reviewer_required=True,
                ),
                True,
            )

        # Use stub mode if LLM not available
        if self.use_stub:
            return self._generate_stub_response(query, sources, audit_id)

        # Build context from sources
        source_text = self._build_source_context(sources)

        # Create system prompt enforcing citations
        system_prompt = """You are a research assistant analyzing scientific evidence.

CRITICAL RULES:
1. EVERY factual claim MUST cite exactly one source from the provided sources
2. Use [Source: source_id] format for citations (e.g., [Source: source_001])
3. If you cannot answer from the provided sources, say so explicitly
4. Identify any gaps in evidence - what additional information would strengthen the answer
5. Do NOT fabricate information or speculate beyond what sources support
6. If sources conflict, acknowledge the disagreement and cite both perspectives

Format your response as JSON with this structure:
{
  "answer": "Your answer here with citations [Source: source_id]",
  "confidence": "high/medium/low",
  "gaps": ["gap 1", "gap 2"],
  "citations": [
    {
      "source_id": "source_001",
      "claim": "What claim does this support?",
      "text": "Exact quote from the source"
    }
  ]
}

Confidence levels:
- HIGH: 3+ independent sources agree, strong evidence base
- MEDIUM: 1-2 sources, reasonable evidence but gaps remain
- LOW: Very limited sources, significant uncertainty"""

        user_prompt = f"""Based on the following approved sources, answer this research question:

QUESTION: {query.query_text}
CONTEXT: {query.context if query.context else "No additional context"}

APPROVED SOURCES:
{source_text}

Remember: Every claim must be cited. If you cannot adequately answer from these sources, say so."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            response_text = response.content[0].text

            # Parse JSON response
            try:
                parsed = json.loads(response_text)
            except json.JSONDecodeError:
                # Attempt to extract JSON if wrapped in markdown code blocks
                json_match = re.search(r"```(?:json)?\s*({.*?})\s*```", response_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(1))
                else:
                    raise ValueError(f"Could not parse response as JSON: {response_text}")

            # Extract citations from response
            citations = self._extract_citations_from_response(parsed, sources)

            # Determine confidence level
            confidence = ConfidenceLevel(parsed.get("confidence", "low").lower())

            # Create response object
            rag_response = ResearchResponse(
                answer=parsed.get("answer", "Unable to generate answer"),
                confidence=confidence,
                citations=citations,
                gaps=parsed.get("gaps", []),
                audit_id=audit_id,
                reviewer_required=False,  # Will be set by validator if needed
            )

            # Require review if:
            # - confidence is medium/low
            # - there are significant gaps
            # - any citation has low confidence
            requires_review = confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM] or len(
                rag_response.gaps
            ) > 2

            return rag_response, requires_review

        except Exception as e:
            return (
                ResearchResponse(
                    answer=f"Error during reasoning: {str(e)}",
                    confidence=ConfidenceLevel.LOW,
                    citations=[],
                    gaps=["Error processing sources"],
                    audit_id=audit_id,
                    reviewer_required=True,
                ),
                True,
            )

    def _build_source_context(self, sources: List[Source]) -> str:
        """Build formatted text of sources for LLM context."""
        context_parts = []
        for source in sources:
            context_parts.append(
                f"[Source: {source.id}]\nName: {source.name}\nType: {source.type.value}\n"
                f"Content: {source.content}\n"
            )
        return "\n".join(context_parts)

    def _extract_citations_from_response(self, parsed_response: dict, sources: List[Source]) -> List[Citation]:
        """Extract citations from parsed LLM response."""
        citations = []
        source_map = {s.id: s for s in sources}

        citation_data = parsed_response.get("citations", [])
        for cit in citation_data:
            source_id = cit.get("source_id")
            if source_id in source_map:
                citation = Citation(
                    source_id=source_id,
                    source_name=source_map[source_id].name,
                    text=cit.get("text", ""),
                    confidence=1.0,  # LLM-selected citations are high confidence
                    claim_supported=cit.get("claim", ""),
                    validated=False,  # Will be validated by validator
                )
                citations.append(citation)

        return citations

    def _generate_stub_response(
        self, query: ResearchQuery, sources: List[Source], audit_id: str
    ) -> Tuple[ResearchResponse, bool]:
        """Generate stub response for testing without LLM."""
        # Create stub citations from first 2 sources
        citations = []
        for i, source in enumerate(sources[:2]):
            # Extract first sentence from source as citation
            text = source.content.split(".")[0] + "."
            citation = Citation(
                source_id=source.id,
                source_name=source.name,
                text=text,
                confidence=0.95,
                claim_supported="Primary claim",
                validated=False,
            )
            citations.append(citation)

        # Create stub answer
        answer = (
            f"Based on the approved sources in our corpus, the evidence indicates that:\n\n"
            f"The primary finding from {sources[0].name} suggests drug X has demonstrated efficacy for condition Y. "
            f"This is further supported by data from {sources[1].name if len(sources) > 1 else 'additional sources'}. "
            f"\n\nThe evidence base appears moderate with {len(sources)} relevant sources found. "
            f"Additional prospective studies would strengthen the evidence base."
        )

        response = ResearchResponse(
            answer=answer,
            confidence=ConfidenceLevel.MEDIUM,
            citations=citations,
            gaps=["Long-term follow-up data limited", "Rare adverse events not well characterized"],
            audit_id=audit_id,
            reviewer_required=True,
        )

        return response, True
