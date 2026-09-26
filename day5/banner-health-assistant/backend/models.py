from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mrn = Column(String, unique=True, index=True, nullable=False)
    dob = Column(Date, nullable=False)

    timeline_events = relationship(
        "TimelineEvent", back_populates="patient", cascade="all, delete-orphan"
    )
    encounters = relationship(
        "Encounter", back_populates="patient", cascade="all, delete-orphan"
    )


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    category = Column(String, nullable=False)  # condition | medication | lab | prior_visit
    description = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_recent_change = Column(Boolean, default=False, nullable=False)

    patient = relationship("Patient", back_populates="timeline_events")


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_type = Column(String, nullable=False)
    transcript = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="encounters")
    draft_note = relationship(
        "DraftNote",
        back_populates="encounter",
        uselist=False,
        cascade="all, delete-orphan",
    )


class DraftNote(Base):
    __tablename__ = "draft_notes"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(
        Integer, ForeignKey("encounters.id"), unique=True, nullable=False, index=True
    )
    subjective = Column(Text, default="", nullable=False)
    objective = Column(Text, default="", nullable=False)
    assessment = Column(Text, default="", nullable=False)
    plan = Column(Text, default="", nullable=False)
    status = Column(String, default="draft", nullable=False)  # draft | approved
    edit_history = Column(JSON, default=list, nullable=False)
    finalized_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    encounter = relationship("Encounter", back_populates="draft_note")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action = Column(String, nullable=False)
    encounter_id = Column(Integer, nullable=True, index=True)
    actor = Column(String, nullable=False)
    detail = Column(String, nullable=True)
