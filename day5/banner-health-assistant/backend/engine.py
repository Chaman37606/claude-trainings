"""
Pure, DB-free logic for the Banner Health clinical assistant demo.

Two responsibilities live here, deliberately separated from crud.py so they
can be unit-tested without touching SQLAlchemy or a database session:

1. score_relevance(event)      -- ranks a patient's timeline events by
                                   clinical relevance for pre-visit summaries.
2. generate_draft_note(text)   -- turns a raw encounter transcript into a
                                   naive SOAP-structured draft note.

Both functions are deterministic: no randomness, no network/LLM calls, no
current-time-of-day sensitivity beyond "today's date" for recency decay.
"""

import re
from datetime import date, datetime

# ---------------------------------------------------------------------------
# 1. Relevance scoring
# ---------------------------------------------------------------------------

# Clinical category weights: active problems/conditions outrank labs, which
# outrank medications, which outrank plain historical visit notes.
CATEGORY_WEIGHTS = {
    "condition": 10.0,
    "lab": 7.0,
    "medication": 5.0,
    "prior_visit": 3.0,
}

DEFAULT_CATEGORY_WEIGHT = 1.0
ACTIVE_BONUS = 4.0
RECENT_CHANGE_BONUS = 5.0
RECENCY_SCALE = 10.0  # numerator for the 1/(days_ago + 1) decay term


def _coerce_date(value) -> date:
    """Accept a date, datetime, or ISO-format string and return a date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise TypeError(f"Unsupported date value for scoring: {value!r}")


def _get(event, field, default=None):
    """Read `field` off a dict or an attribute-based object (e.g. ORM row)."""
    if isinstance(event, dict):
        return event.get(field, default)
    return getattr(event, field, default)


def score_relevance(event, as_of: date = None) -> float:
    """
    Score a single timeline event's relevance for a pre-visit summary.

    `event` may be a TimelineEvent ORM instance or any dict/object exposing
    `category`, `event_date`, `is_active`, and `is_recent_change`.

    Higher is more relevant. The score combines:
      - a category weight (condition > lab > medication > prior_visit)
      - a recency decay term (more recent event_date -> higher score)
      - a bonus if the item is currently active
      - a bonus if the item changed recently

    This produces a deterministic ordering where, e.g., an active condition
    that changed recently will always outrank an old, resolved/stable item.
    """
    if as_of is None:
        as_of = date.today()

    category = _get(event, "category")
    event_date = _coerce_date(_get(event, "event_date"))
    is_active = bool(_get(event, "is_active", False))
    is_recent_change = bool(_get(event, "is_recent_change", False))

    category_score = CATEGORY_WEIGHTS.get(category, DEFAULT_CATEGORY_WEIGHT)

    days_ago = max((as_of - event_date).days, 0)
    recency_score = RECENCY_SCALE / (days_ago + 1)

    bonus = 0.0
    if is_active:
        bonus += ACTIVE_BONUS
    if is_recent_change:
        bonus += RECENT_CHANGE_BONUS

    return round(category_score + recency_score + bonus, 4)


# ---------------------------------------------------------------------------
# 2. Draft note generation (SOAP routing)
# ---------------------------------------------------------------------------

SUBJECTIVE_CUES = [
    "reports",
    "denies",
    "complains of",
    "complaining of",
    "states",
    "describes",
    "feels",
    "notes that",
    "endorses",
]

OBJECTIVE_CUES = [
    "bp",
    "hr",
    "temp",
    "temperature",
    "exam reveals",
    "auscultation",
    "vitals",
    "vital signs",
    "pulse",
    "respiratory rate",
    "spo2",
    "o2 sat",
    "physical exam",
    "on examination",
    "heart rate",
    "blood pressure",
]

ASSESSMENT_CUES = [
    "diagnosis",
    "assessment",
    "impression",
    "consistent with",
    "likely represents",
    "differential",
    "suggestive of",
]

PLAN_CUES = [
    "plan",
    "follow up",
    "follow-up",
    "prescribe",
    "refer",
    "referral",
    "schedule",
    "recommend",
    "will start",
    "will continue",
    "return to clinic",
]

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(transcript: str):
    """Split a transcript into non-empty, whitespace-normalized sentences."""
    if not transcript:
        return []
    text = re.sub(r"\s+", " ", transcript).strip()
    if not text:
        return []
    parts = _SENTENCE_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def _matches_any(sentence_lower: str, cues) -> bool:
    for cue in cues:
        pattern = r"\b" + re.escape(cue) + r"\b"
        if re.search(pattern, sentence_lower):
            return True
    return False


def generate_draft_note(transcript: str) -> dict:
    """
    Route each sentence of a raw encounter transcript into a SOAP section
    using simple, deterministic cue-phrase heuristics.

    Checked in order: plan cues, then assessment cues, then objective cues,
    then subjective cues. Any sentence matching no cue falls back to
    subjective. Never raises on empty or single-sentence input.
    """
    sections = {"subjective": [], "objective": [], "assessment": [], "plan": []}

    for sentence in _split_sentences(transcript):
        lowered = sentence.lower()
        if _matches_any(lowered, PLAN_CUES):
            sections["plan"].append(sentence)
        elif _matches_any(lowered, ASSESSMENT_CUES):
            sections["assessment"].append(sentence)
        elif _matches_any(lowered, OBJECTIVE_CUES):
            sections["objective"].append(sentence)
        elif _matches_any(lowered, SUBJECTIVE_CUES):
            sections["subjective"].append(sentence)
        else:
            sections["subjective"].append(sentence)

    return {
        "subjective": " ".join(sections["subjective"]),
        "objective": " ".join(sections["objective"]),
        "assessment": " ".join(sections["assessment"]),
        "plan": " ".join(sections["plan"]),
    }
