from sqlalchemy.orm import Session
from datetime import datetime
from models import User, QARecord, AuditLog
from schemas import QARecordCreate, QARecordUpdate

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, username: str, email: str, full_name: str, password: str, role: str = "analyst"):
    user = User(username=username, email=email, full_name=full_name, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    return user

def create_qa_record(db: Session, record: QARecordCreate, user_id: int, ip_address: str = None):
    db_record = QARecord(**record.model_dump(), created_by=user_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    log_audit(db, db_record.id, user_id, "create", ip_address=ip_address)
    return db_record

def update_qa_record(db: Session, record_id: int, update_data: QARecordUpdate, user_id: int, ip_address: str = None):
    db_record = db.query(QARecord).filter(QARecord.id == record_id).first()
    if not db_record:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        old_value = getattr(db_record, field)
        if old_value != value:
            log_audit(db, record_id, user_id, "update", field, str(old_value), str(value), ip_address)
        setattr(db_record, field, value)

    db_record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)
    return db_record

def get_qa_record(db: Session, record_id: int):
    return db.query(QARecord).filter(QARecord.id == record_id).first()

def get_qa_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(QARecord).offset(skip).limit(limit).all()

def submit_qa_record(db: Session, record_id: int, user_id: int, ip_address: str = None):
    db_record = db.query(QARecord).filter(QARecord.id == record_id).first()
    if not db_record:
        return None

    db_record.status = "submitted"
    db_record.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)

    log_audit(db, record_id, user_id, "submit", ip_address=ip_address)
    return db_record

def approve_qa_record(db: Session, record_id: int, user_id: int, ip_address: str = None):
    db_record = db.query(QARecord).filter(QARecord.id == record_id).first()
    if not db_record:
        return None

    db_record.status = "approved"
    db_record.approved_by = user_id
    db_record.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)

    log_audit(db, record_id, user_id, "approve", ip_address=ip_address)
    return db_record

def reject_qa_record(db: Session, record_id: int, user_id: int, reason: str, ip_address: str = None):
    db_record = db.query(QARecord).filter(QARecord.id == record_id).first()
    if not db_record:
        return None

    db_record.status = "rejected"
    db.commit()
    db.refresh(db_record)

    log_audit(db, record_id, user_id, "reject", notes=reason, ip_address=ip_address)
    return db_record

def log_audit(db: Session, qa_record_id: int, user_id: int, action: str, field_name: str = None,
              old_value: str = None, new_value: str = None, ip_address: str = None, notes: str = None):
    audit_log = AuditLog(
        qa_record_id=qa_record_id,
        user_id=user_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        notes=notes,
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    return audit_log

def get_audit_logs(db: Session, qa_record_id: int):
    return db.query(AuditLog).filter(AuditLog.qa_record_id == qa_record_id).order_by(AuditLog.timestamp.desc()).all()
