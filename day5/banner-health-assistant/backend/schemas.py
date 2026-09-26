from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Auth ----------

class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str = Field(min_length=8, max_length=72)  # 72 bytes is bcrypt's hard limit


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Patients ----------

class PatientOut(BaseModel):
    id: int
    name: str
    mrn: str
    dob: date

    model_config = ConfigDict(from_attributes=True)


# ---------- Timeline ----------

class TimelineEventOut(BaseModel):
    id: int
    type: str
    description: str
    date: date
    category: str
    relevance_score: float

    model_config = ConfigDict(from_attributes=True)


class TimelineResponse(BaseModel):
    patient_id: int
    events: List[TimelineEventOut]


# ---------- Summary ----------

class SummaryItemOut(BaseModel):
    id: int
    description: str
    category: str
    date: date
    relevance_score: float
    reason: str

    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    patient_id: int
    summary_items: List[SummaryItemOut]
    generated_at: datetime


# ---------- Encounters ----------

class EncounterCreate(BaseModel):
    encounter_type: str
    transcript: str


class EncounterOut(BaseModel):
    id: int
    patient_id: int
    encounter_type: str
    transcript: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Draft notes ----------

class EditHistoryEntry(BaseModel):
    timestamp: str
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class DraftNoteOut(BaseModel):
    id: int
    encounter_id: int
    subjective: str
    objective: str
    assessment: str
    plan: str
    status: str
    edit_history: List[Dict[str, Any]] = []
    finalized_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DraftNoteUpdate(BaseModel):
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None


# ---------- Audit log ----------

class AuditLogOut(BaseModel):
    id: int
    timestamp: datetime
    action: str
    encounter_id: Optional[int] = None
    actor: str
    detail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
