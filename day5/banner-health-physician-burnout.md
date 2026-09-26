# Banner Health: Reducing Physician Burnout at Scale

### How an AI clinical assistant cut documentation time and gave physicians their evenings back

---

## Overview

Banner Health is one of the largest nonprofit health systems in the United States, operating dozens of hospitals and hundreds of clinics across multiple states. Like most large health systems, Banner faced a growing crisis: physicians were spending more hours on documentation than on direct patient care, driving burnout, attrition, and reduced quality of care.

Banner Health deployed an AI clinical assistant that drafts clinical documentation and summarizes patient records automatically — giving physicians back hours in their day and helping reverse a system-wide burnout trend.

> *This case study is illustrative, describing a representative deployment pattern for AI clinical assistants in large health systems.*

---

## The Challenge

Physician burnout has been called a public health crisis in its own right. At Banner Health, as at most health systems, the root causes were familiar:

- **Documentation overload** — physicians were spending an estimated 1.5–2 hours on EHR documentation for every 1 hour of direct patient care.
- **"Pajama time"** — a significant share of charting was happening after hours, at home, eating into personal and family time.
- **Record fragmentation** — reviewing a patient's history before a visit meant sifting through years of scattered notes, labs, and prior encounters across multiple providers.
- **Downstream effects** — burnout was contributing to physician turnover, reduced patient face-time, and increased risk of clinical errors from fatigue and rushed note-taking.

Leadership recognized that incremental fixes (scribes, template shortcuts, EHR training) were not enough to reverse the trend at the scale Banner needed.

---

## The Solution

Banner Health introduced an AI clinical assistant designed to sit alongside physicians in their existing workflow, with two core capabilities:

### 1. Automated clinical documentation
The assistant listens to (or ingests notes from) patient encounters and drafts structured clinical documentation — visit notes, discharge summaries, and referral letters — in the format physicians already use. Physicians review, edit, and sign off, rather than typing from scratch.

### 2. Patient record summarization
Before each visit, the assistant condenses a patient's longitudinal record — prior visits, labs, medications, specialist notes — into a concise, relevant summary. Physicians walk into the room already knowing the patient's story, instead of reconstructing it from a fragmented chart.

Both capabilities were built with a **human-in-the-loop** principle: the AI drafts and suggests, but the physician always reviews and has final authority over what enters the medical record.

---

## Implementation

Banner Health rolled out the assistant in phases:

1. **Pilot** — launched with a small group of primary care and hospitalist physicians to validate accuracy, workflow fit, and time savings.
2. **Department-level expansion** — extended to additional departments based on pilot feedback, with documentation templates tuned per specialty.
3. **System-wide rollout** — scaled across Banner's hospitals and clinics, paired with physician training on reviewing and editing AI-drafted notes efficiently.

Throughout the rollout, physician feedback loops were used to refine summarization quality and reduce edit burden, and IT/compliance teams validated that the assistant integrated securely with existing EHR systems.

---

## High-Level Design (HLD)

The assistant is architected as a set of services sitting between the encounter itself and the EHR, with the physician always in the loop before anything is finalized.

**Core components:**
- **Encounter Capture** — ingests the patient encounter (ambient audio or typed input) and produces a timestamped transcript/note source.
- **Drafting Engine** — an LLM-based service that turns the encounter source into structured clinical documentation (SOAP notes, discharge summaries, referral letters).
- **Patient Record Aggregator** — pulls a patient's longitudinal history from the EHR into a unified internal timeline.
- **Summarization Engine** — condenses the aggregated timeline into a concise, relevance-ranked pre-visit summary.
- **Physician Review UI** — presents drafts and summaries for edit and sign-off before anything is committed to the record.
- **EHR Integration & Audit Layer** — writes finalized notes back to the EHR and logs every AI-generated draft, edit, and approval for compliance.

**Data flow:**
`Encounter → Capture → Drafting Engine → Draft Note → Physician Review → EHR Write-Back`
`Longitudinal Record → Aggregator → Summarization Engine → Pre-Visit Summary → Physician UI`

## Low-Level Design (LLD)

- **Draft note model** — `DraftNote { encounterId, sections: [Subjective, Objective, Assessment, Plan], status, editHistory[] }`. Each physician edit is captured in `editHistory` and fed back as training signal to improve future drafts.
- **Record aggregation** — the aggregator queries structured EHR resources (encounters, observations, medications, conditions) via the EHR's API, normalizing them into a single `PatientTimeline { patientId, events[] }` object rather than requiring the physician to open multiple chart tabs.
- **Summarization ranking** — timeline events are scored by recency and clinical relevance (active problems and recent changes outrank stable, older history) before being rendered as a compact summary card.
- **Review & diffing** — the review UI renders a diff between the AI draft and the physician's final edit, so edit volume per note type can be tracked as a quality signal.
- **Write-back & audit** — finalized notes are written to the EHR via standard clinical data exchange (e.g., HL7/FHIR), with every write paired with an immutable audit log entry (who approved, what changed, when).

---

## Results / Impact

Illustrative outcomes from the deployment:

- **Reduced documentation time** — meaningful reduction in time spent per patient encounter on charting.
- **Less after-hours charting** — a marked drop in "pajama time," giving physicians back personal time in the evenings.
- **Faster chart review** — pre-visit summarization cut prep time per patient, especially for complex, multi-visit histories.
- **Improved physician satisfaction** — burnout survey scores trended upward following rollout, with physicians citing reduced administrative burden as a key factor.
- **More time with patients** — time reclaimed from documentation was redirected toward direct patient interaction.

---

## Key Takeaways

For other health systems considering a similar deployment:

- **Keep physicians in control.** Human-in-the-loop review builds trust and ensures the AI assistant augments judgment rather than replacing it.
- **Start narrow, expand deliberately.** A focused pilot surfaces workflow and accuracy issues before they compound at scale.
- **Measure what matters to physicians.** Time saved and reduced after-hours work resonate more directly with burnout than abstract efficiency metrics.
- **Documentation and summarization are a natural pairing.** Reducing the burden of writing notes and reducing the burden of reading old ones compound to free up significant physician time.

---

## Quote

> *"For the first time in years, I'm leaving the clinic at a reasonable hour without a stack of notes waiting for me at home. This gave me back time with my patients — and with my family."*
> — Illustrative quote, representative of physician feedback during rollout
