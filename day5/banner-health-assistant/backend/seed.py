"""
Demo data seeding for the Banner Health clinical assistant backend.

seed_if_empty(db) only inserts data when the patients table is empty, so it
is safe to call on every app startup without creating duplicates. run() is a
convenience entry point that opens its own session (useful for `python
seed.py` or one-off scripts).
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

import crud
from database import SessionLocal
from models import Patient


def _days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


# Each patient tuple: (name, mrn, dob)
_PATIENTS = [
    ("Eleanor Whitfield", "BH-100234", date(1958, 3, 14)),
    ("Marcus Chen", "BH-100587", date(1972, 11, 2)),
    ("Priya Nandakumar", "BH-100812", date(1990, 6, 23)),
    ("Robert Alvarez", "BH-101045", date(1965, 9, 30)),
]

# Each event tuple: (category, description, days_ago, is_active, is_recent_change)
_TIMELINE_EVENTS = {
    "BH-100234": [
        ("condition", "Type 2 diabetes mellitus", 10, True, True),
        ("condition", "Essential hypertension", 400, True, False),
        ("condition", "Osteoarthritis, resolved post knee replacement", 1200, False, False),
        ("medication", "Metformin 1000mg twice daily", 10, True, True),
        ("medication", "Lisinopril 20mg daily", 400, True, False),
        ("lab", "HbA1c 8.2% (elevated)", 5, True, True),
        ("lab", "Lipid panel within normal limits", 300, False, False),
        ("prior_visit", "Annual physical exam", 365, False, False),
    ],
    "BH-100587": [
        ("condition", "Asthma, well controlled", 600, True, False),
        ("condition", "Seasonal allergic rhinitis", 20, True, True),
        ("medication", "Albuterol inhaler PRN", 600, True, False),
        ("medication", "Fluticasone nasal spray", 20, True, True),
        ("lab", "Spirometry stable", 500, False, False),
        ("prior_visit", "Follow-up for allergy symptoms", 20, False, False),
        ("prior_visit", "Sports physical", 900, False, False),
    ],
    "BH-100812": [
        ("condition", "Major depressive disorder", 30, True, True),
        ("condition", "Migraine without aura", 800, True, False),
        ("condition", "Iron deficiency anemia, resolved", 1000, False, False),
        ("medication", "Sertraline 100mg daily (dose increased)", 15, True, True),
        ("medication", "Sumatriptan PRN", 800, True, False),
        ("lab", "CBC within normal limits", 15, True, True),
        ("lab", "Ferritin low, improving", 950, False, False),
        ("prior_visit", "Psychiatric medication follow-up", 15, False, False),
        ("prior_visit", "Neurology consult for migraines", 800, False, False),
    ],
    "BH-101045": [
        ("condition", "Chronic kidney disease, stage 3", 60, True, False),
        ("condition", "Gout, acute flare", 7, True, True),
        ("medication", "Allopurinol 300mg daily", 60, True, False),
        ("medication", "Colchicine started for acute flare", 7, True, True),
        ("lab", "Creatinine 1.8 mg/dL, stable", 60, True, False),
        ("prior_visit", "Nephrology follow-up", 60, False, False),
    ],
}


def seed_if_empty(db: Session) -> None:
    """Insert demo patients + timeline events only if the DB has no patients yet."""
    if db.query(Patient).count() > 0:
        return

    for name, mrn, dob in _PATIENTS:
        patient = crud.create_patient(db, name=name, mrn=mrn, dob=dob)
        for category, description, days_ago, is_active, is_recent_change in _TIMELINE_EVENTS[mrn]:
            crud.create_timeline_event(
                db,
                patient_id=patient.id,
                category=category,
                description=description,
                event_date=_days_ago(days_ago),
                is_active=is_active,
                is_recent_change=is_recent_change,
            )


def run() -> None:
    """Open a standalone session and seed the DB if it's empty. Safe to call repeatedly."""
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()
