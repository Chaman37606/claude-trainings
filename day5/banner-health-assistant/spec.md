# Spec — Banner Health AI Clinical Assistant

Formal specification of what's actually implemented under `backend/` and `frontend/`. The
narrative case study is in [`../banner-health-physician-burnout.md`](../banner-health-physician-burnout.md);
this document is the authoritative contract for the app itself — treat it as the source of truth
if code and prose ever disagree.

## 1. Purpose

A demo implementation of the Banner Health case study's HLD: a physician-facing tool that (a)
ranks a patient's history into a pre-visit summary, and (b) drafts a structured SOAP note from
an encounter transcript for physician review before anything is "signed" into the record.

**Explicitly not real clinical NLP/AI.** Both the ranking and the drafting are deterministic,
rule-based functions (`backend/engine.py`) — no external LLM call. This is a design decision,
not a placeholder: it keeps the app self-contained, offline, and reproducibly testable. See
`performance/PERFORMANCE_REVIEW.md` for what would need to change for real concurrent-write
scale, and `agents/README.md` for how this was built.

## 2. Functional requirements

| # | Requirement | Where |
|---|---|---|
| F1 | List all patients | `GET /api/patients`, sidebar in `frontend/` |
| F2 | Show a patient's history ranked by clinical relevance, top 5, each with a plain-language reason | `GET /api/patients/{id}/summary` |
| F3 | Show a patient's full history, same ranking, unbounded | `GET /api/patients/{id}/timeline` |
| F4 | Start an encounter by capturing a free-text transcript | `POST /api/patients/{id}/encounters` |
| F5 | Generate a structured SOAP draft from that transcript | `POST /api/encounters/{id}/draft` |
| F6 | Physician can edit any subset of the four SOAP sections before signing | `PUT /api/encounters/{id}/draft` |
| F7 | Physician can approve/sign a draft, after which it becomes read-only | `POST /api/encounters/{id}/approve` |
| F8 | Every generate/edit/approve action is recorded in an immutable audit trail, queryable globally or per-encounter | `POST *`, `GET /api/audit` |

## 3. Data model

`backend/models.py` is authoritative; this is the field-level contract.

```
Patient          { id, name, mrn (unique), dob }
TimelineEvent    { id, patient_id, category: condition|medication|lab|prior_visit,
                    description, event_date, is_active: bool, is_recent_change: bool }
Encounter        { id, patient_id, encounter_type, transcript, created_at }
DraftNote        { id, encounter_id (unique), subjective, objective, assessment, plan,
                    status: draft|approved, edit_history: [{timestamp, field, old_value, new_value}],
                    finalized_at, created_at, updated_at }
AuditLog         { id, timestamp, action: generate_draft|edit_draft|approve_note,
                    encounter_id, actor, detail }
```

Constraints: one `DraftNote` per `Encounter` (unique FK). `edit_history` only gains an entry
when a `PUT` actually changes a field's value (no-op edits are not logged). `status` only
transitions `draft → approved`, never back.

## 4. API contract

All request/response bodies are JSON. 404 with `{"detail": "..."}` for any unknown
`patient_id`/`encounter_id`.

| Method | Path | Request body | Response |
|---|---|---|---|
| GET | `/api/patients` | — | `[{id, name, mrn, dob}]` |
| GET | `/api/patients/{id}/timeline` | — | `{patient_id, events:[{id, type, category, description, date, relevance_score}]}`, sorted by `relevance_score` desc; `type == category` always |
| GET | `/api/patients/{id}/summary` | — | `{patient_id, summary_items:[{id, description, category, date, relevance_score, reason}], generated_at}`, top 5 |
| POST | `/api/patients/{id}/encounters` | `{encounter_type, transcript}` | `{id, patient_id, encounter_type, transcript, created_at}` |
| POST | `/api/encounters/{id}/draft` | — | `DraftNote` (creates on first call, regenerates+overwrites sections and resets to `draft` on repeat calls) |
| GET | `/api/encounters/{id}/draft` | — | `DraftNote`, 404 if none generated yet |
| PUT | `/api/encounters/{id}/draft` | any subset of `{subjective, objective, assessment, plan}` | updated `DraftNote` |
| POST | `/api/encounters/{id}/approve` | `{approved_by}` | `DraftNote` with `status: "approved"`, `finalized_at` set |
| GET | `/api/audit` | query param `encounter_id` optional | `[{id, timestamp, action, encounter_id, actor, detail}]`, newest first |

## 5. Business rules / algorithms

### 5.1 Relevance scoring (`engine.score_relevance`)

`score = category_weight + recency_decay + active_bonus + recent_change_bonus`

- Category weight: `condition (10) > lab (7) > medication (5) > prior_visit (3)`
- Recency decay: `10 / (days_ago + 1)` — strictly monotonic, newer always outranks older within
  the same category/flags
- `+4` if `is_active`, `+5` if `is_recent_change` (stacks with active)

This directly implements the case study LLD's "active problems and recent changes outrank
stable, older history."

### 5.2 Reason text (`crud._build_reason`)

Deterministic from the same two flags: `"Active {label}, updated recently"` →
`"Active {label}"` → `"Recently changed {label}"` → `"Stable/historical {label}"`, in that
priority order. The frontend also derives its card accent color from this same text (see §6).

### 5.3 Draft note generation (`engine.generate_draft_note`)

Splits the transcript into sentences, routes each into a SOAP section by cue phrase, checked in
this order (first match wins): **Plan** (`plan`, `follow up`/`follow-up`, `prescribe`, `refer`,
`schedule`, `recommend`) → **Assessment** (`diagnosis`, `assessment`, `impression`, `consistent
with`) → **Objective** (`bp`, `hr`, `temp`, `exam reveals`, `auscultation`, vitals patterns) →
**Subjective** (`reports`, `denies`, `complains of`, `states`). A sentence matching none of the
above falls back to **Subjective**. Never raises on empty input; always returns all four keys
(possibly empty strings).

### 5.4 Audit logging

Every `generate_draft`, `edit_draft` (only when a field actually changed), and `approve_note`
action writes one `AuditLog` row inside the same request, actor defaults to
`"ai_drafting_engine"` / `"physician"` / the supplied `approved_by` respectively. See
`performance/PERFORMANCE_REVIEW.md` §Root causes for the current cost of this (a separate commit
per action, not batched).

## 6. Frontend behavior contract

- Category badges render the humanized label (`prior_visit` → `PRIOR VISIT`), never the raw
  enum value.
- Relevance score displays rounded to 1 decimal with a proportional mini meter, never the raw
  float.
- A summary card's left-border accent reflects urgency parsed from `reason`: contains
  "recently"/"recent" → red (urgent); else contains "active" → blue; else contains
  "stable"/"historical"/"resolved" → gray. This is a client-side derivation from `reason` text,
  not a separate API field — if the wording in §5.2 changes, this classifier must change with it.
- Draft textareas become `readOnly` once `status === "approved"`; the approval prompt is inline
  (no `window.prompt`).

## 7. Out of scope (by design, not oversight)

- Real LLM-backed drafting/summarization (see §1)
- Multi-user auth/sessions — single implicit "physician" actor per action
- EHR interoperability (HL7/FHIR) — `AuditLog` stands in for the "EHR write-back" the case
  study describes
- Pagination on `GET /api/audit` (flagged as a real gap in `performance/PERFORMANCE_REVIEW.md`)
- Concurrent-writer scale beyond SQLite's single-writer lock (same doc)

## 8. Verification

- `pytest tests -v` — 17 tests, unit (scoring/drafting logic) + integration (full API workflow,
  sort order, 404s). See `tests/`.
- `performance/load_test.py` — read/write throughput and latency under concurrency.
- No automated UI test exists; the frontend has been visually spot-checked via headless-Chrome
  screenshots (see `agents/README.md`'s "known gap" note) but not covered by an automated suite.
