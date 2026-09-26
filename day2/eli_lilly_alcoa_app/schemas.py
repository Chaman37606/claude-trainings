from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    full_name: str
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogSchema(BaseModel):
    id: int
    qa_record_id: int
    user_id: int
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class QARecordBase(BaseModel):
    batch_number: str
    test_type: str
    result: float
    specification_min: float
    specification_max: float
    notes: Optional[str] = None

class QARecordCreate(QARecordBase):
    pass

class QARecordUpdate(BaseModel):
    test_type: Optional[str] = None
    result: Optional[float] = None
    specification_min: Optional[float] = None
    specification_max: Optional[float] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class QARecord(QARecordBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    audit_logs: List[AuditLogSchema] = []

    class Config:
        from_attributes = True

class QARecordWithAudit(QARecord):
    created_by_user: User
    audit_logs: List[AuditLogSchema] = []
