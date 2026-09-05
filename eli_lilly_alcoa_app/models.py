from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="analyst")  # analyst, reviewer, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    qa_records = relationship("QARecord", foreign_keys="QARecord.created_by", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")

class QARecord(Base):
    __tablename__ = "qa_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, index=True)
    test_type = Column(String)  # Physical, Chemical, Microbial, etc.
    status = Column(String, default="draft")  # draft, submitted, approved, rejected
    result = Column(Float)
    specification_min = Column(Float)
    specification_max = Column(Float)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="qa_records")
    audit_logs = relationship("AuditLog", back_populates="qa_record")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    qa_record_id = Column(Integer, ForeignKey("qa_records.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # create, update, submit, approve, reject
    field_name = Column(String, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    qa_record = relationship("QARecord", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
