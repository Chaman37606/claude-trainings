from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceType(str, Enum):
    JOURNAL = "journal"
    REGULATORY = "regulatory"
    REPORT = "report"
    DATABASE = "database"


class Source(BaseModel):
    id: str
    name: str
    type: SourceType
    domain: str
    approved: bool = True
    content: str
    retrieval_timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchQuery(BaseModel):
    id: Optional[str] = None
    query_text: str
    context: Optional[str] = None
    user_id: str
    domain: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    approval_required: bool = False


class Citation(BaseModel):
    source_id: str
    source_name: str
    text: str
    confidence: float  # 0.0-1.0
    claim_supported: str
    validated: bool = False


class ResearchResponse(BaseModel):
    id: Optional[str] = None
    answer: str
    confidence: ConfidenceLevel
    citations: List[Citation] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    audit_id: str
    reviewer_required: bool = False
    reviewer_name: Optional[str] = None
    reviewer_decision: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLogEntry(BaseModel):
    id: Optional[str] = None
    audit_id: str
    query_id: str
    action: str  # "query_submitted", "sources_retrieved", "answer_generated", "reviewed", "decision_made"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    decision: Optional[str] = None  # "approved", "rejected", "escalated"
    reviewer_id: Optional[str] = None
    notes: Optional[str] = None


class ReviewRequest(BaseModel):
    response_id: str
    reviewer_id: str
    decision: str  # "approved", "rejected", "escalated"
    notes: Optional[str] = None
