# Commure: Clinical Documentation Automation at Scale

### How an AI documentation platform automated note generation directly from patient encounters, saving clinicians millions of hours

---

## Overview

Commure builds infrastructure and applications for health systems, with a focus on removing the operational and administrative friction that keeps clinicians away from patient care. Documentation is one of the largest sources of that friction, consuming hours of clinician time every single day across every specialty.

Commure deployed clinical documentation automation that generates notes directly from patient encounters at scale, collectively saving clinicians millions of hours of documentation work.

> *This case study is illustrative, describing a representative deployment pattern for AI-driven clinical documentation automation at health-system scale.*

---

## The Challenge

Documentation burden is one of the most consistent, cross-specialty drivers of clinician time loss and burnout:

- **Every encounter requires a note.** Regardless of specialty or setting, each patient encounter generates documentation obligations — visit notes, orders, follow-up instructions — that must be captured accurately.
- **Manual note-writing doesn't scale with volume.** As patient volumes grow, the documentation burden grows linearly with it, with no natural efficiency gain from experience alone.
- **Inconsistent documentation quality.** Notes written under time pressure vary in completeness and structure, affecting downstream billing, care coordination, and continuity of care.
- **The scale of the problem is enormous.** Across a large health system — let alone many health systems — the aggregate clinician time spent on documentation reaches into the millions of hours annually.

Health systems needed documentation automation that could operate reliably across many specialties, encounter types, and clinicians simultaneously — not just within a single pilot department.

---

## The Solution

Commure built a clinical documentation automation platform centered on generating notes directly from the patient encounter itself:

### 1. Encounter-to-note generation
The platform captures the patient encounter and automatically generates a structured clinical note — capturing history, assessment, and plan — in the format clinicians and the health system already use, without clinicians needing to dictate or type from scratch.

### 2. Scale across specialties and settings
Rather than being tuned for a single use case, the platform is designed to generate documentation across a broad range of encounter types and specialties, enabling health systems to deploy it broadly rather than department by department.

As with other clinical AI deployments, clinicians retain **final review and sign-off** on every generated note — the platform accelerates drafting, but clinical accountability stays with the clinician.

---

## Implementation

Commure's rollout to health systems followed a phased approach:

1. **Specialty and encounter-type onboarding** — configuring documentation generation for the specific specialties and encounter types a health system needed first.
2. **Pilot with early-adopter clinicians** — validating note quality and clinician workflow fit with a smaller group before wider deployment.
3. **Health-system-wide scaling** — expanding automated documentation across departments and clinician groups, leveraging the platform's multi-specialty design.
4. **Ongoing quality monitoring** — tracking note quality, edit rates, and clinician feedback to continuously improve generation accuracy at scale.

---

## High-Level Design (HLD)

The platform is architected to generate documentation across many specialties, encounter types, and EHR vendors simultaneously, rather than being tuned for a single site or use case.

**Core components:**
- **Multi-Specialty Encounter Capture** — captures encounters across specialties and modalities (ambient audio, structured intake, typed notes).
- **Specialty-Aware Note Generation Engine** — generates structured notes using templates/prompts routed by specialty and encounter type.
- **Multi-EHR Integration Layer** — writes generated notes back into whichever EHR a given health system runs.
- **Per-Site Config Management** — holds site- and specialty-specific templates and terminology without requiring core engine redeploys.
- **Quality Monitoring Service** — tracks note quality and edit rates across the full deployed footprint.

**Data flow:**
`Encounter (any site/specialty) → Capture → Specialty-Aware Note Generation → Clinician Review → EHR Write-Back (per site) → Quality Monitoring`

## Low-Level Design (LLD)

- **Specialty/encounter-type routing** — each encounter is tagged by specialty and type, which determines which generation template and prompt configuration the note generation engine applies, rather than using one generic note format for every case.
- **Multi-EHR adapter pattern** — generated notes are produced in a common internal schema first, then translated to each EHR vendor's specific write-back format via a per-vendor adapter, so adding a new site's EHR doesn't require changing the core generation logic.
- **Per-site/specialty configuration** — templates, terminology, and formatting rules are stored as configuration rather than code, so onboarding a new specialty or site is a configuration change, not a redeployment.
- **Scalable processing** — encounters are processed through horizontally scaled generation workers behind a queue, so encounter volume spikes across many sites at once don't create backlogs.
- **Quality monitoring at scale** — edit rate and note completeness are tracked per specialty and per clinician, surfaced on a rollout-health dashboard used to catch quality regressions as new sites/specialties are added.

---

## Results / Impact

Illustrative outcomes from the deployment:

- **Millions of hours saved** — aggregated across clinicians and encounters, documentation automation saved millions of hours of clinician time.
- **Faster note turnaround** — notes were completed and available in the record more quickly after each encounter.
- **Broad specialty coverage** — automation scaled across multiple specialties and encounter types rather than remaining confined to a single pilot use case.
- **Reduced after-hours documentation** — clinicians spent less time finishing notes outside of clinical hours.

---

## Key Takeaways

For health systems considering documentation automation at scale:

- **Design for breadth from the start.** Building for multiple specialties and encounter types, not just one, is what enables true health-system-wide scale.
- **Clinician sign-off preserves accountability.** Automating the draft, not the final decision, keeps clinical responsibility where it belongs.
- **Aggregate time savings are the real story at scale.** Per-note savings look modest individually, but compound into millions of hours across a full health system's encounter volume.
- **Continuous monitoring sustains quality as volume grows.** Scaling automation requires ongoing tracking of note quality and clinician edits, not just a one-time validation.

---

## Quote

> *"When you're generating documentation across this many encounters, the individual minutes saved don't feel dramatic day to day. But when you add it up across the whole organization, it's millions of hours clinicians got back — time that went straight back into patient care."*
> — Illustrative quote, representative of health system leadership feedback during rollout
