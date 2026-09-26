import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import crud
import schemas
import seed
from database import Base, SessionLocal, engine, get_db

app = FastAPI(
    title="Banner Health Clinical Assistant API",
    description="Demo API for AI-assisted clinical documentation drafting and patient record summarization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed.seed_if_empty(db)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------


@app.get("/api/patients", response_model=List[schemas.PatientOut])
def list_patients(db: Session = Depends(get_db)):
    return crud.list_patients(db)


@app.get("/api/patients/{patient_id}/timeline", response_model=schemas.TimelineResponse)
def get_patient_timeline(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    events = crud.get_ranked_timeline(db, patient_id)
    return {"patient_id": patient_id, "events": events}


@app.get("/api/patients/{patient_id}/summary", response_model=schemas.SummaryResponse)
def get_patient_summary(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    items = crud.get_patient_summary(db, patient_id, top_n=5)
    return {
        "patient_id": patient_id,
        "summary_items": items,
        "generated_at": datetime.utcnow(),
    }


# ---------------------------------------------------------------------------
# Encounters
# ---------------------------------------------------------------------------


@app.post("/api/patients/{patient_id}/encounters", response_model=schemas.EncounterOut)
def create_patient_encounter(
    patient_id: int, payload: schemas.EncounterCreate, db: Session = Depends(get_db)
):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_encounter(db, patient_id, payload.encounter_type, payload.transcript)


# ---------------------------------------------------------------------------
# Draft notes
# ---------------------------------------------------------------------------


@app.post("/api/encounters/{encounter_id}/draft", response_model=schemas.DraftNoteOut)
def generate_encounter_draft(encounter_id: int, db: Session = Depends(get_db)):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return crud.generate_and_save_draft(db, encounter_id)


@app.get("/api/encounters/{encounter_id}/draft", response_model=schemas.DraftNoteOut)
def read_encounter_draft(encounter_id: int, db: Session = Depends(get_db)):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    draft = crud.get_draft(db, encounter_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft note not found for this encounter")
    return draft


@app.put("/api/encounters/{encounter_id}/draft", response_model=schemas.DraftNoteOut)
def update_encounter_draft(
    encounter_id: int, payload: schemas.DraftNoteUpdate, db: Session = Depends(get_db)
):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    updates = payload.model_dump(exclude_unset=True)
    draft = crud.update_draft(db, encounter_id, updates)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft note not found for this encounter")
    return draft


@app.post("/api/encounters/{encounter_id}/approve", response_model=schemas.DraftNoteOut)
def approve_encounter_draft(
    encounter_id: int, payload: schemas.ApproveRequest, db: Session = Depends(get_db)
):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    draft = crud.approve_draft(db, encounter_id, payload.approved_by)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft note not found for this encounter")
    return draft


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


@app.get("/api/audit", response_model=List[schemas.AuditLogOut])
def list_audit(encounter_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.list_audit_logs(db, encounter_id=encounter_id)


# ---------------------------------------------------------------------------
# Static frontend (mounted last so API routes above always match first)
# ---------------------------------------------------------------------------

_FRONTEND_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
)

if os.path.isdir(_FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
