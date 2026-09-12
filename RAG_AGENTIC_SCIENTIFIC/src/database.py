import uuid
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./audit.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class QueryRecord(Base):
    __tablename__ = "research_queries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approval_required = Column(Boolean, default=False)

    response = relationship("ResponseRecord", back_populates="query", uselist=False)
    audit_logs = relationship("AuditLogRecord", back_populates="query")


class ResponseRecord(Base):
    __tablename__ = "research_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(36), ForeignKey("research_queries.id"), nullable=False)
    audit_id = Column(String(36), nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    confidence = Column(String(20), nullable=False)  # high, medium, low
    gaps = Column(JSON, default=list)
    reviewer_required = Column(Boolean, default=False)
    reviewer_name = Column(String(255), nullable=True)
    reviewer_decision = Column(String(50), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    query = relationship("QueryRecord", back_populates="response")
    citations = relationship("CitationRecord", back_populates="response")
    audit_logs = relationship("AuditLogRecord", back_populates="response")


class CitationRecord(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id = Column(String(36), ForeignKey("research_responses.id"), nullable=False)
    source_id = Column(String(255), nullable=False)
    source_name = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0-1.0
    claim_supported = Column(Text, nullable=False)
    validated = Column(Boolean, default=False)

    response = relationship("ResponseRecord", back_populates="citations")


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_id = Column(String(36), nullable=False, index=True)
    query_id = Column(String(36), ForeignKey("research_queries.id"), nullable=False)
    response_id = Column(String(36), ForeignKey("research_responses.id"), nullable=True)
    action = Column(String(100), nullable=False)  # query_submitted, sources_retrieved, answer_generated, reviewed, decision_made
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(255), nullable=False)
    details = Column(JSON, default=dict)
    decision = Column(String(50), nullable=True)  # approved, rejected, escalated
    reviewer_id = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    query = relationship("QueryRecord", back_populates="audit_logs")
    response = relationship("ResponseRecord", back_populates="audit_logs")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
