from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import engine, get_db, Base
from models import User, QARecord, AuditLog
from schemas import QARecordCreate, QARecordUpdate, QARecord as QARecordSchema, AuditLogSchema, User as UserSchema
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Eli Lilly ALCOA+ QA System",
    description="Professional QA Data Management with Complete Audit Trail",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        user = crud.create_user(db, "analyst", "analyst@elililly.com", "QA Analyst", "password123", "analyst")
    return user

@app.get("/")
async def root():
    return {
        "message": "Eli Lilly ALCOA+ QA System API",
        "organization": "Eli Lilly",
        "version": "1.0.0",
        "features": ["ALCOA+ Compliance", "Audit Trail", "QA Data Entry", "Complete Traceability"]
    }

@app.get("/api/users", response_model=List[UserSchema])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    if not users:
        user = crud.create_user(db, "analyst", "analyst@elililly.com", "QA Analyst", "password123", "analyst")
        reviewer = crud.create_user(db, "reviewer", "reviewer@elililly.com", "QA Reviewer", "password123", "reviewer")
        users = [user, reviewer]
    return users

@app.post("/api/qa-records", response_model=QARecordSchema)
async def create_qa_record(
    record: QARecordCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = get_client_ip(request)
    db_record = crud.create_qa_record(db, record, current_user.id, ip_address)
    return db_record

@app.get("/api/qa-records", response_model=List[QARecordSchema])
async def list_qa_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    records = crud.get_qa_records(db, skip=skip, limit=limit)
    return records

@app.get("/api/qa-records/{record_id}", response_model=QARecordSchema)
async def get_qa_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_qa_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.put("/api/qa-records/{record_id}", response_model=QARecordSchema)
async def update_qa_record(
    record_id: int,
    update_data: QARecordUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = get_client_ip(request)
    record = crud.update_qa_record(db, record_id, update_data, current_user.id, ip_address)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.post("/api/qa-records/{record_id}/submit", response_model=QARecordSchema)
async def submit_qa_record(
    record_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = get_client_ip(request)
    record = crud.submit_qa_record(db, record_id, current_user.id, ip_address)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.post("/api/qa-records/{record_id}/approve", response_model=QARecordSchema)
async def approve_qa_record(
    record_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = get_client_ip(request)
    record = crud.approve_qa_record(db, record_id, current_user.id, ip_address)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.post("/api/qa-records/{record_id}/reject", response_model=QARecordSchema)
async def reject_qa_record(
    record_id: int,
    reason: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = get_client_ip(request)
    record = crud.reject_qa_record(db, record_id, current_user.id, reason, ip_address)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.get("/api/audit-logs/{record_id}", response_model=List[AuditLogSchema])
async def get_audit_logs(record_id: int, db: Session = Depends(get_db)):
    logs = crud.get_audit_logs(db, record_id)
    return logs

@app.get("/api/compliance/status")
async def compliance_status(db: Session = Depends(get_db)):
    total_records = db.query(QARecord).count()
    approved_records = db.query(QARecord).filter(QARecord.status == "approved").count()
    submitted_records = db.query(QARecord).filter(QARecord.status == "submitted").count()
    draft_records = db.query(QARecord).filter(QARecord.status == "draft").count()

    return {
        "total_records": total_records,
        "approved": approved_records,
        "submitted": submitted_records,
        "draft": draft_records,
        "compliance_rate": (approved_records / total_records * 100) if total_records > 0 else 0,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
