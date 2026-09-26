import uuid
import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.models import ResearchQuery, ResearchResponse, Source, AuditLogEntry
from src.database import (
    QueryRecord,
    ResponseRecord,
    CitationRecord,
    AuditLogRecord,
)


class AuditTrail:
    def __init__(self, db: Session):
        self.db = db

    def create_audit_id(self) -> str:
        """Generate unique audit ID."""
        return f"audit_{uuid.uuid4().hex[:12]}"

    def log_query_submission(self, query: ResearchQuery, audit_id: str) -> str:
        """Log initial query submission."""
        query_record = QueryRecord(
            id=query.id or str(uuid.uuid4()),
            query_text=query.query_text,
            context=query.context,
            user_id=query.user_id,
            domain=query.domain,
            submitted_at=datetime.utcnow(),
            approval_required=query.approval_required,
        )
        self.db.add(query_record)
        self.db.commit()

        # Create audit log entry
        log_entry = AuditLogRecord(
            audit_id=audit_id,
            query_id=query_record.id,
            action="query_submitted",
            user_id=query.user_id,
            details={
                "query_text": query.query_text,
                "domain": query.domain,
                "context": query.context,
            },
        )
        self.db.add(log_entry)
        self.db.commit()

        return query_record.id

    def log_retrieval(self, audit_id: str, query_id: str, sources: List[Source], user_id: str):
        """Log source retrieval step."""
        log_entry = AuditLogRecord(
            audit_id=audit_id,
            query_id=query_id,
            action="sources_retrieved",
            user_id=user_id,
            details={
                "sources_retrieved": len(sources),
                "source_ids": [s.id for s in sources],
                "domains": list(set(s.domain for s in sources)),
            },
        )
        self.db.add(log_entry)
        self.db.commit()

    def log_response(
        self, audit_id: str, query_id: str, response: ResearchResponse, user_id: str
    ) -> str:
        """Log generated response."""
        response_record = ResponseRecord(
            id=response.id or str(uuid.uuid4()),
            query_id=query_id,
            audit_id=audit_id,
            answer=response.answer,
            confidence=response.confidence.value,
            gaps=response.gaps,
            reviewer_required=response.reviewer_required,
        )
        self.db.add(response_record)
        self.db.flush()

        # Log citations
        for citation in response.citations:
            citation_record = CitationRecord(
                response_id=response_record.id,
                source_id=citation.source_id,
                source_name=citation.source_name,
                text=citation.text,
                confidence=citation.confidence,
                claim_supported=citation.claim_supported,
                validated=citation.validated,
            )
            self.db.add(citation_record)

        self.db.commit()

        # Create audit log entry
        log_entry = AuditLogRecord(
            audit_id=audit_id,
            query_id=query_id,
            response_id=response_record.id,
            action="answer_generated",
            user_id=user_id,
            details={
                "confidence": response.confidence.value,
                "num_citations": len(response.citations),
                "num_gaps": len(response.gaps),
                "reviewer_required": response.reviewer_required,
            },
        )
        self.db.add(log_entry)
        self.db.commit()

        return response_record.id

    def log_review(
        self, audit_id: str, query_id: str, response_id: str, reviewer_id: str, decision: str, notes: str = ""
    ):
        """Log reviewer decision."""
        # Update response with review decision
        response_record = self.db.query(ResponseRecord).filter(ResponseRecord.id == response_id).first()
        if response_record:
            response_record.reviewer_name = reviewer_id
            response_record.reviewer_decision = decision
            response_record.reviewed_at = datetime.utcnow()
            self.db.commit()

        # Create audit log entry
        log_entry = AuditLogRecord(
            audit_id=audit_id,
            query_id=query_id,
            response_id=response_id,
            action="reviewed",
            user_id=reviewer_id,
            decision=decision,
            reviewer_id=reviewer_id,
            notes=notes,
            details={"decision": decision, "notes": notes},
        )
        self.db.add(log_entry)
        self.db.commit()

    def export_audit_trail(self, audit_id: str) -> Dict[str, Any]:
        """Export complete immutable audit trail."""
        # Get all logs for this audit
        logs = self.db.query(AuditLogRecord).filter(AuditLogRecord.audit_id == audit_id).all()

        if not logs:
            return {"error": f"No audit trail found for {audit_id}"}

        # Get query details
        query_id = logs[0].query_id
        query_record = self.db.query(QueryRecord).filter(QueryRecord.id == query_id).first()

        # Get response details
        response_logs = [l for l in logs if l.response_id]
        response_id = response_logs[0].response_id if response_logs else None
        response_record = None
        citations = []
        if response_id:
            response_record = self.db.query(ResponseRecord).filter(ResponseRecord.id == response_id).first()
            citations = self.db.query(CitationRecord).filter(CitationRecord.response_id == response_id).all()

        # Build audit trail
        audit_trail = {
            "audit_id": audit_id,
            "query": {
                "id": query_record.id,
                "text": query_record.query_text,
                "context": query_record.context,
                "user_id": query_record.user_id,
                "domain": query_record.domain,
                "submitted_at": query_record.submitted_at.isoformat() if query_record.submitted_at else None,
            },
            "response": (
                {
                    "id": response_record.id,
                    "answer": response_record.answer,
                    "confidence": response_record.confidence,
                    "gaps": response_record.gaps,
                    "reviewer_required": response_record.reviewer_required,
                    "reviewer_name": response_record.reviewer_name,
                    "reviewer_decision": response_record.reviewer_decision,
                    "reviewed_at": response_record.reviewed_at.isoformat()
                    if response_record.reviewed_at
                    else None,
                    "created_at": response_record.created_at.isoformat() if response_record.created_at else None,
                }
                if response_record
                else None
            ),
            "citations": [
                {
                    "source_id": c.source_id,
                    "source_name": c.source_name,
                    "text": c.text,
                    "confidence": c.confidence,
                    "validated": c.validated,
                }
                for c in citations
            ],
            "timeline": [
                {
                    "action": log.action,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "user_id": log.user_id,
                    "decision": log.decision,
                    "notes": log.notes,
                    "details": log.details,
                }
                for log in sorted(logs, key=lambda x: x.timestamp)
            ],
        }

        return audit_trail
