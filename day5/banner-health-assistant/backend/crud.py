from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from engine import generate_draft_note, score_relevance
from models import AuditLog, DraftNote, Encounter, Patient, TimelineEvent

# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------


def create_patient(db: Session, name: str, mrn: str, dob: date) -> Patient:
    patient = Patient(name=name, mrn=mrn, dob=dob)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patient_by_mrn(db: Session, mrn: str) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.mrn == mrn).first()


def list_patients(db: Session) -> List[Patient]:
    return db.query(Patient).order_by(Patient.id).all()


# ---------------------------------------------------------------------------
# Timeline events
# ---------------------------------------------------------------------------


def create_timeline_event(
    db: Session,
    patient_id: int,
    category: str,
    description: str,
    event_date: date,
    is_active: bool = False,
    is_recent_change: bool = False,
) -> TimelineEvent:
    event = TimelineEvent(
        patient_id=patient_id,
        category=category,
        description=description,
        event_date=event_date,
        is_active=is_active,
        is_recent_change=is_recent_change,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_timeline_events(db: Session, patient_id: int) -> List[TimelineEvent]:
    return (
        db.query(TimelineEvent)
        .filter(TimelineEvent.patient_id == patient_id)
        .all()
    )


def get_ranked_timeline(db: Session, patient_id: int) -> List[dict]:
    """Return this patient's timeline events sorted by relevance, descending."""
    events = list_timeline_events(db, patient_id)
    scored = [(score_relevance(e), e) for e in events]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        {
            "id": e.id,
            "type": e.category,
            "category": e.category,
            "description": e.description,
            "date": e.event_date,
            "relevance_score": score,
        }
        for score, e in scored
    ]


_CATEGORY_LABELS = {
    "condition": "condition",
    "medication": "medication",
    "lab": "lab result",
    "prior_visit": "prior visit",
}


def _build_reason(event: TimelineEvent) -> str:
    label = _CATEGORY_LABELS.get(event.category, event.category)
    if event.is_active and event.is_recent_change:
        return f"Active {label}, updated recently"
    if event.is_active:
        return f"Active {label}"
    if event.is_recent_change:
        return f"Recently changed {label}"
    return f"Stable/historical {label}"


def get_patient_summary(db: Session, patient_id: int, top_n: int = 5) -> List[dict]:
    """Return the top-N most relevant timeline events with a short reason."""
    events = list_timeline_events(db, patient_id)
    scored = [(score_relevance(e), e) for e in events]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = scored[:top_n]
    return [
        {
            "id": e.id,
            "description": e.description,
            "category": e.category,
            "date": e.event_date,
            "relevance_score": score,
            "reason": _build_reason(e),
        }
        for score, e in top
    ]


# ---------------------------------------------------------------------------
# Encounters
# ---------------------------------------------------------------------------


def create_encounter(
    db: Session, patient_id: int, encounter_type: str, transcript: str
) -> Encounter:
    encounter = Encounter(
        patient_id=patient_id, encounter_type=encounter_type, transcript=transcript
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    return encounter


def get_encounter(db: Session, encounter_id: int) -> Optional[Encounter]:
    return db.query(Encounter).filter(Encounter.id == encounter_id).first()


# ---------------------------------------------------------------------------
# Draft notes
# ---------------------------------------------------------------------------


def get_draft(db: Session, encounter_id: int) -> Optional[DraftNote]:
    return db.query(DraftNote).filter(DraftNote.encounter_id == encounter_id).first()


def generate_and_save_draft(
    db: Session, encounter_id: int, actor: str = "ai_drafting_engine"
) -> Optional[DraftNote]:
    """Run the drafting engine over the encounter transcript and upsert the DraftNote."""
    encounter = get_encounter(db, encounter_id)
    if not encounter:
        return None

    sections = generate_draft_note(encounter.transcript)

    draft = get_draft(db, encounter_id)
    if draft is None:
        draft = DraftNote(
            encounter_id=encounter_id,
            subjective=sections["subjective"],
            objective=sections["objective"],
            assessment=sections["assessment"],
            plan=sections["plan"],
            status="draft",
            edit_history=[],
        )
        db.add(draft)
    else:
        draft.subjective = sections["subjective"]
        draft.objective = sections["objective"]
        draft.assessment = sections["assessment"]
        draft.plan = sections["plan"]
        draft.status = "draft"
        draft.finalized_at = None
        draft.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(draft)

    log_audit(
        db,
        action="generate_draft",
        actor=actor,
        encounter_id=encounter_id,
        detail="Draft note generated from encounter transcript",
    )
    return draft


_EDITABLE_FIELDS = ("subjective", "objective", "assessment", "plan")


def update_draft(
    db: Session, encounter_id: int, updates: dict, actor: str = "physician"
) -> Optional[DraftNote]:
    """
    Apply a partial update to a draft note. Only fields present (and non-None)
    in `updates` are changed; each changed field is diffed into edit_history.
    """
    draft = get_draft(db, encounter_id)
    if not draft:
        return None

    history = list(draft.edit_history or [])
    now_iso = datetime.utcnow().isoformat()
    changed_fields = []

    for field in _EDITABLE_FIELDS:
        if field not in updates or updates[field] is None:
            continue
        new_value = updates[field]
        old_value = getattr(draft, field)
        if old_value != new_value:
            history.append(
                {
                    "timestamp": now_iso,
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )
            setattr(draft, field, new_value)
            changed_fields.append(field)

    if changed_fields:
        draft.edit_history = history
        draft.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(draft)

        log_audit(
            db,
            action="edit_draft",
            actor=actor,
            encounter_id=encounter_id,
            detail=f"Edited fields: {', '.join(changed_fields)}",
        )

    return draft


def approve_draft(
    db: Session, encounter_id: int, approved_by: str
) -> Optional[DraftNote]:
    draft = get_draft(db, encounter_id)
    if not draft:
        return None

    draft.status = "approved"
    draft.finalized_at = datetime.utcnow()
    draft.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(draft)

    log_audit(
        db,
        action="approve_note",
        actor=approved_by,
        encounter_id=encounter_id,
        detail="Draft note approved and finalized",
    )
    return draft


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


def log_audit(
    db: Session,
    action: str,
    actor: str,
    encounter_id: Optional[int] = None,
    detail: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(action=action, encounter_id=encounter_id, actor=actor, detail=detail)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_audit_logs(db: Session, encounter_id: Optional[int] = None) -> List[AuditLog]:
    query = db.query(AuditLog)
    if encounter_id is not None:
        query = query.filter(AuditLog.encounter_id == encounter_id)
    return query.order_by(AuditLog.timestamp.desc()).all()
