"""
Unit tests for the two pure, DB-free functions in backend/engine.py:
  - score_relevance
  - generate_draft_note

These are plain function tests -- no FastAPI app, no database.
"""

from datetime import date, timedelta

from engine import generate_draft_note, score_relevance


# ---------------------------------------------------------------------------
# score_relevance
# ---------------------------------------------------------------------------


def _event(category, event_date, is_active=False, is_recent_change=False):
    return {
        "category": category,
        "event_date": event_date,
        "is_active": is_active,
        "is_recent_change": is_recent_change,
    }


def test_active_recent_condition_outranks_old_inactive_medication():
    today = date(2026, 1, 1)

    active_condition = _event(
        "condition", today - timedelta(days=5), is_active=True, is_recent_change=True
    )
    old_resolved_medication = _event(
        "medication", today - timedelta(days=1000), is_active=False, is_recent_change=False
    )

    active_score = score_relevance(active_condition, as_of=today)
    old_score = score_relevance(old_resolved_medication, as_of=today)

    assert active_score > old_score


def test_recency_alone_moves_the_score():
    today = date(2026, 1, 1)

    recent = _event("lab", today - timedelta(days=1))
    older = _event("lab", today - timedelta(days=100))

    recent_score = score_relevance(recent, as_of=today)
    older_score = score_relevance(older, as_of=today)

    assert recent_score > older_score


def test_is_active_bonus_changes_score():
    today = date(2026, 1, 1)
    event_date = today - timedelta(days=50)

    inactive = _event("condition", event_date, is_active=False, is_recent_change=False)
    active = _event("condition", event_date, is_active=True, is_recent_change=False)

    assert score_relevance(active, as_of=today) > score_relevance(inactive, as_of=today)


def test_is_recent_change_bonus_changes_score():
    today = date(2026, 1, 1)
    event_date = today - timedelta(days=50)

    unchanged = _event("medication", event_date, is_active=False, is_recent_change=False)
    changed = _event("medication", event_date, is_active=False, is_recent_change=True)

    assert score_relevance(changed, as_of=today) > score_relevance(unchanged, as_of=today)


def test_both_bonuses_stack():
    today = date(2026, 1, 1)
    event_date = today - timedelta(days=50)

    base = _event("lab", event_date, is_active=False, is_recent_change=False)
    active_only = _event("lab", event_date, is_active=True, is_recent_change=False)
    both = _event("lab", event_date, is_active=True, is_recent_change=True)

    base_score = score_relevance(base, as_of=today)
    active_score = score_relevance(active_only, as_of=today)
    both_score = score_relevance(both, as_of=today)

    assert active_score > base_score
    assert both_score > active_score


# ---------------------------------------------------------------------------
# generate_draft_note
# ---------------------------------------------------------------------------


def test_generate_draft_note_routes_each_soap_section():
    transcript = (
        "Patient reports worsening shortness of breath over the last week. "
        "BP 120/80, exam reveals mild wheezing on auscultation. "
        "Assessment: consistent with an asthma exacerbation. "
        "Plan: follow up in 2 weeks and start a short course of steroids."
    )

    sections = generate_draft_note(transcript)

    assert set(sections.keys()) == {"subjective", "objective", "assessment", "plan"}

    assert "Patient reports worsening shortness of breath" in sections["subjective"]
    assert "BP 120/80, exam reveals mild wheezing" in sections["objective"]
    assert "consistent with an asthma exacerbation" in sections["assessment"]
    assert "follow up in 2 weeks" in sections["plan"]

    # And each sentence should have landed in exactly the section we expect,
    # not leaked into another one.
    assert "wheezing" not in sections["subjective"]
    assert "asthma exacerbation" not in sections["objective"]
    assert "steroids" not in sections["assessment"]


def test_generate_draft_note_empty_string_does_not_throw():
    sections = generate_draft_note("")

    assert set(sections.keys()) == {"subjective", "objective", "assessment", "plan"}
    assert sections["subjective"] == ""
    assert sections["objective"] == ""
    assert sections["assessment"] == ""
    assert sections["plan"] == ""


def test_generate_draft_note_no_cue_phrases_falls_back_and_does_not_throw():
    transcript = "The weather was nice today and we talked about the garden."

    sections = generate_draft_note(transcript)

    assert set(sections.keys()) == {"subjective", "objective", "assessment", "plan"}
    # No cues at all -> fallback into subjective, other sections stay empty.
    assert sections["subjective"] == transcript
    assert sections["objective"] == ""
    assert sections["assessment"] == ""
    assert sections["plan"] == ""
