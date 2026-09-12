import os
import json
from pathlib import Path
from typing import List, Dict

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_FILE = os.getenv("APPROVED_SOURCES_FILE", str(PROJECT_DIR / "data" / "sources_approved.json"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///" + str(PROJECT_DIR / "audit.db"))
REVIEWER_ID = os.getenv("REVIEWER_ID", "dr_default@research.org")

APPROVED_DOMAINS = [
    "pharmacology",
    "immunology",
    "oncology",
    "infectious_disease",
    "cardiology",
    "neurology",
]


def load_approved_sources() -> Dict:
    with open(SOURCES_FILE, "r") as f:
        return json.load(f)


def get_approved_source_ids() -> List[str]:
    sources_data = load_approved_sources()
    return [s["id"] for s in sources_data["sources"] if s.get("approved", True)]


def is_approved_source(source_id: str) -> bool:
    approved_ids = get_approved_source_ids()
    return source_id in approved_ids


def is_valid_domain(domain: str) -> bool:
    return domain.lower() in APPROVED_DOMAINS
