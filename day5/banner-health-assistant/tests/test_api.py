"""
Integration tests for the FastAPI backend, exercising the full documented
HTTP contract against an isolated, pre-seeded in-memory SQLite database
(see the `client` fixture in conftest.py). These tests never touch the real
backend/banner_health.db file's data.
"""


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------


def test_list_patients_returns_seeded_patients(client):
    resp = client.get("/api/patients")
    assert resp.status_code == 200
    patients = resp.json()
    assert len(patients) == 4
    mrns = {p["mrn"] for p in patients}
    assert mrns == {"BH-100234", "BH-100587", "BH-100812", "BH-101045"}
    for p in patients:
        assert set(p.keys()) >= {"id", "name", "mrn", "dob"}


def test_timeline_404_for_unknown_patient(client):
    resp = client.get("/api/patients/999999/timeline")
    assert resp.status_code == 404


def test_summary_404_for_unknown_patient(client):
    resp = client.get("/api/patients/999999/summary")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------


def test_timeline_sorted_descending_and_type_matches_category(client):
    patients = client.get("/api/patients").json()
    patient_id = patients[0]["id"]

    resp = client.get(f"/api/patients/{patient_id}/timeline")
    assert resp.status_code == 200
    body = resp.json()
    assert body["patient_id"] == patient_id

    events = body["events"]
    assert len(events) > 0

    scores = [e["relevance_score"] for e in events]
    assert scores == sorted(scores, reverse=True)

    for e in events:
        assert e["type"] == e["category"]


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_summary_items_have_non_empty_reason(client):
    patients = client.get("/api/patients").json()
    patient_id = patients[0]["id"]

    resp = client.get(f"/api/patients/{patient_id}/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["patient_id"] == patient_id
    assert len(body["summary_items"]) > 0

    for item in body["summary_items"]:
        assert isinstance(item["reason"], str)
        assert item["reason"].strip() != ""


# ---------------------------------------------------------------------------
# Full encounter -> draft -> edit -> approve workflow
# ---------------------------------------------------------------------------


def test_full_encounter_draft_workflow(client):
    patients = client.get("/api/patients").json()
    patient_id = patients[0]["id"]

    transcript = (
        "Patient reports mild headache for two days. "
        "BP 118/76, exam reveals no focal deficits. "
        "Assessment: consistent with tension headache. "
        "Plan: follow up in 2 weeks if symptoms persist."
    )

    # 1. Create the encounter.
    create_resp = client.post(
        f"/api/patients/{patient_id}/encounters",
        json={"encounter_type": "office_visit", "transcript": transcript},
    )
    assert create_resp.status_code == 200
    encounter = create_resp.json()
    encounter_id = encounter["id"]
    assert encounter["patient_id"] == patient_id
    assert encounter["transcript"] == transcript

    # 2. Generate the draft note.
    draft_resp = client.post(f"/api/encounters/{encounter_id}/draft")
    assert draft_resp.status_code == 200
    draft = draft_resp.json()
    for field in ("subjective", "objective", "assessment", "plan"):
        assert field in draft
        assert draft[field] != ""
    assert draft["status"] == "draft"
    assert draft["encounter_id"] == encounter_id

    # 3. Read the draft back and confirm it matches.
    read_resp = client.get(f"/api/encounters/{encounter_id}/draft")
    assert read_resp.status_code == 200
    read_draft = read_resp.json()
    assert read_draft["subjective"] == draft["subjective"]
    assert read_draft["objective"] == draft["objective"]
    assert read_draft["assessment"] == draft["assessment"]
    assert read_draft["plan"] == draft["plan"]
    assert read_draft["status"] == "draft"

    # 4. Edit exactly one field.
    old_plan = draft["plan"]
    new_plan = "Plan: follow up in 1 week and start ibuprofen as needed."
    update_resp = client.put(
        f"/api/encounters/{encounter_id}/draft", json={"plan": new_plan}
    )
    assert update_resp.status_code == 200
    updated_draft = update_resp.json()
    assert updated_draft["plan"] == new_plan
    # Other fields untouched.
    assert updated_draft["subjective"] == draft["subjective"]
    assert updated_draft["objective"] == draft["objective"]
    assert updated_draft["assessment"] == draft["assessment"]

    assert len(updated_draft["edit_history"]) == 1
    entry = updated_draft["edit_history"][0]
    assert set(entry.keys()) == {"timestamp", "field", "old_value", "new_value"}
    assert entry["field"] == "plan"
    assert entry["old_value"] == old_plan
    assert entry["new_value"] == new_plan

    # 5. Approve the draft.
    approve_resp = client.post(
        f"/api/encounters/{encounter_id}/approve", json={"approved_by": "Dr. Test"}
    )
    assert approve_resp.status_code == 200
    approved = approve_resp.json()
    assert approved["status"] == "approved"
    assert approved["finalized_at"] is not None

    # 6. Audit log covers the whole workflow, newest first.
    audit_resp = client.get(f"/api/audit?encounter_id={encounter_id}")
    assert audit_resp.status_code == 200
    audit_entries = audit_resp.json()

    actions = [e["action"] for e in audit_entries]
    assert "generate_draft" in actions
    assert "edit_draft" in actions
    assert "approve_note" in actions

    timestamps = [e["timestamp"] for e in audit_entries]
    assert timestamps == sorted(timestamps, reverse=True)

    for e in audit_entries:
        assert e["encounter_id"] == encounter_id


# ---------------------------------------------------------------------------
# 404s
# ---------------------------------------------------------------------------


def test_get_draft_404_for_unknown_encounter(client):
    resp = client.get("/api/encounters/999999/draft")
    assert resp.status_code == 404


def test_post_draft_404_for_unknown_encounter(client):
    resp = client.post("/api/encounters/999999/draft")
    assert resp.status_code == 404


def test_create_encounter_404_for_unknown_patient(client):
    resp = client.post(
        "/api/patients/999999/encounters",
        json={"encounter_type": "office_visit", "transcript": "Patient reports feeling fine."},
    )
    assert resp.status_code == 404
