import logging
import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

import auth
import config
import crud
import schemas
import seed
from database import Base, SessionLocal, engine, get_db
from models import User

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("banner_health")

app = FastAPI(
    title="Banner Health Clinical Assistant API",
    description="Demo API for AI-assisted clinical documentation drafting and patient record summarization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch anything an HTTPException/validation error didn't already handle.

    Logs the full traceback server-side but never leaks it to the client — just a
    generic 500. FastAPI/Starlette's built-in handling for HTTPException and request
    validation errors runs first and is unaffected by this.
    """
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Starting up — database URL: %s", config.DATABASE_URL)
    if config.JWT_IS_DEFAULT_SECRET:
        logger.warning(
            "JWT_SECRET_KEY is not set — using the built-in dev-only default. "
            "Set JWT_SECRET_KEY before deploying this anywhere beyond local/demo use."
        )
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed.seed_if_empty(db)
    finally:
        db.close()
    logger.info("Startup complete")


@app.get("/api/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """Liveness/readiness probe: confirms the process is up and the DB is reachable."""
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:  # noqa: BLE001 - a health check must never itself crash
        logger.exception("Health check DB connectivity failure")
        db_connected = False
    return {"status": "ok" if db_connected else "degraded", "db_connected": db_connected}


# ---------------------------------------------------------------------------
# Auth
#
# Self-registration is open here for demo convenience — gate this behind admin
# provisioning before any real deployment (see SECURITY.md).
# ---------------------------------------------------------------------------


@app.post("/api/auth/register", response_model=schemas.Token, tags=["auth"])
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    user = crud.create_user(
        db,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=auth.hash_password(payload.password),
    )
    token = auth.create_access_token(subject=user.username)
    return schemas.Token(access_token=token)


@app.post("/api/auth/login", response_model=schemas.Token, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(subject=user.username)
    return schemas.Token(access_token=token)


@app.get("/api/auth/me", response_model=schemas.UserOut, tags=["auth"])
def read_current_user(current_user: User = Depends(auth.get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------


@app.get("/api/patients", response_model=List[schemas.PatientOut])
def list_patients(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    return crud.list_patients(db)


@app.get("/api/patients/{patient_id}/timeline", response_model=schemas.TimelineResponse)
def get_patient_timeline(
    patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)
):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    events = crud.get_ranked_timeline(db, patient_id)
    return {"patient_id": patient_id, "events": events}


@app.get("/api/patients/{patient_id}/summary", response_model=schemas.SummaryResponse)
def get_patient_summary(
    patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)
):
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
    patient_id: int,
    payload: schemas.EncounterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_encounter(db, patient_id, payload.encounter_type, payload.transcript)


# ---------------------------------------------------------------------------
# Draft notes
# ---------------------------------------------------------------------------


@app.post("/api/encounters/{encounter_id}/draft", response_model=schemas.DraftNoteOut)
def generate_encounter_draft(
    encounter_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)
):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return crud.generate_and_save_draft(db, encounter_id)


@app.get("/api/encounters/{encounter_id}/draft", response_model=schemas.DraftNoteOut)
def read_encounter_draft(
    encounter_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)
):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    draft = crud.get_draft(db, encounter_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft note not found for this encounter")
    return draft


@app.put("/api/encounters/{encounter_id}/draft", response_model=schemas.DraftNoteOut)
def update_encounter_draft(
    encounter_id: int,
    payload: schemas.DraftNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    updates = payload.model_dump(exclude_unset=True)
    draft = crud.update_draft(db, encounter_id, updates, actor=current_user.username)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft note not found for this encounter")
    return draft


@app.post("/api/encounters/{encounter_id}/approve", response_model=schemas.DraftNoteOut)
def approve_encounter_draft(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Approves and signs the draft as the authenticated user.

    Previously this took a client-supplied `approved_by` string with no verification at
    all — anyone could type any name. Now the signer is always the real logged-in
    account; there is no body to this request.
    """
    encounter = crud.get_encounter(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    draft = crud.approve_draft(db, encounter_id, current_user.full_name)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft note not found for this encounter")
    return draft


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


@app.get("/api/audit", response_model=List[schemas.AuditLogOut])
def list_audit(
    encounter_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
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
