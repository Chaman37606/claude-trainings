# Qualified Health: Identifying Patients for Life-Saving Treatment

### How an AI screening system surfaced hidden candidates for evidence-based interventions across fragmented medical records

---

## Overview

Qualified Health works with health systems to close critical gaps in care — finding patients who qualify for life-saving, evidence-based treatments but who fall through the cracks because their medical history is scattered across incompatible systems, formats, and providers.

Qualified Health deployed an AI system that screens large patient populations against fragmented medical records to surface candidates for evidence-based interventions — treatments and screenings that patients qualified for, but had never received.

> *This case study is illustrative, describing a representative deployment pattern for AI-driven population health screening.*

---

## The Challenge

Even when a proven, evidence-based treatment exists, many eligible patients never receive it. The reasons are structural, not clinical:

- **Fragmented records** — a single patient's relevant history (labs, imaging, prior diagnoses, medications, family history) is often spread across multiple EHRs, referring providers, and unstructured notes that don't talk to each other.
- **Manual chart review doesn't scale** — identifying eligible patients one chart at a time is prohibitively slow across populations of hundreds of thousands of patients.
- **Rigid rule-based screening misses nuance** — simple keyword or code-based queries miss patients whose eligibility is documented in free-text notes, non-standard coding, or across disconnected encounters.
- **The cost of missing a patient is high** — for time-sensitive, life-saving interventions, every missed or delayed identification is a patient who doesn't get treated in time.

Health systems needed a way to screen entire populations at once, reliably, without relying on a clinician manually reviewing every chart.

---

## The Solution

Qualified Health built an AI screening system with two core capabilities:

### 1. Population-scale screening
The system ingests and reconciles fragmented medical records — structured data (labs, codes, medications) and unstructured data (clinical notes, reports) — across a health system's full patient population, rather than requiring manual, patient-by-patient chart pulls.

### 2. Evidence-based eligibility matching
Each patient's consolidated record is evaluated against the clinical criteria for specific evidence-based interventions. The system surfaces a ranked list of candidates who meet eligibility criteria but have no record of having received — or been referred for — the treatment.

As with clinical documentation tools, the system is built around **clinician oversight**: it surfaces candidates for review, not automated treatment decisions. A clinician confirms eligibility and initiates outreach or referral.

---

## Implementation

Qualified Health's deployment followed a phased approach:

1. **Target intervention selection** — partnering with the health system to define which evidence-based interventions to screen for first, based on clinical impact and data availability.
2. **Record reconciliation** — connecting to and normalizing data from the health system's EHRs and other clinical data sources to build a unified view per patient.
3. **Pilot screening run** — running the eligibility model against a subset of the population and validating candidate lists with clinicians before scaling.
4. **Population-wide rollout** — expanding screening across the full patient population, with a recurring cadence to catch newly eligible patients as records update.
5. **Clinical workflow integration** — routing surfaced candidates into existing outreach, referral, and care-coordination workflows so eligible patients could be efficiently contacted and scheduled.

---

## High-Level Design (HLD)

The system is architected as a population-scale pipeline that reconciles fragmented records first, then screens the unified result against intervention criteria.

**Core components:**
- **Data Ingestion & Reconciliation** — connects to multiple EHRs and data sources and resolves records belonging to the same patient into one view.
- **Unified Patient Record Store** — a patient-centric store holding both structured (codes, labs) and unstructured (notes) data per patient.
- **Eligibility Matching Engine** — evaluates each unified record against the clinical criteria for a target intervention.
- **Candidate Ranking Service** — orders eligible patients by clinical urgency and confidence in the underlying data.
- **Clinician Review Queue** — a worklist where clinicians confirm, reject, or defer surfaced candidates.
- **Outreach/Referral Integration** — routes confirmed candidates into existing care-coordination and scheduling workflows.

**Data flow:**
`Multi-Source EHR Data → Ingestion & Reconciliation → Unified Patient Record → Eligibility Matching → Ranked Candidate List → Clinician Review → Outreach`

## Low-Level Design (LLD)

- **Entity resolution** — incoming records are matched to a single patient identity using probabilistic matching on demographics and available identifiers, since the same patient rarely has one consistent ID across source systems.
- **Eligibility rules + NLP** — each intervention's clinical criteria are encoded as computable rules (structured codes, lab thresholds) where possible; criteria only present in free text are extracted via NLP and attached a confidence score rather than treated as certain.
- **Ranking logic** — candidates are scored on a combination of clinical urgency (how time-sensitive the intervention is) and data confidence (how certain the eligibility signal is), so clinicians see the highest-value cases first.
- **Review queue mechanics** — each candidate record links back to the source snippet(s) that triggered eligibility, so a clinician can verify in seconds rather than re-reviewing the full chart; accept/reject/defer actions are logged as feedback signal.
- **Recurring screening** — rather than a single pass, the pipeline re-runs on a scheduled cadence, processing only new/changed records (delta processing) so newly eligible patients are caught as their data updates.

---

## Results / Impact

Illustrative outcomes from the deployment:

- **Previously hidden patients identified** — a meaningful number of eligible patients were surfaced who had no prior record of treatment or referral, despite meeting clinical criteria.
- **Faster time-to-identification** — population screening that would have taken manual reviewers months was completed in a fraction of the time.
- **Higher-yield clinician review** — clinicians spent their limited review time on a pre-qualified, ranked list instead of searching broadly across the population.
- **Improved intervention rates** — a higher share of eligible patients were reached, referred, and treated compared to prior manual or rule-based screening approaches.

---

## Key Takeaways

For other health systems considering a similar deployment:

- **Fragmentation is the real bottleneck, not clinical uncertainty.** Most eligible patients are identifiable from data that already exists — the challenge is reconciling it into one usable view.
- **Keep clinicians as the final decision-maker.** AI-surfaced candidates should be confirmed by a clinician before outreach, preserving clinical judgment and trust.
- **Start with one high-impact intervention.** Narrowing scope to a single, well-defined evidence-based treatment makes validation and rollout tractable before expanding to others.
- **Screening should be recurring, not one-time.** Patient records update constantly; ongoing screening catches newly eligible patients as new data arrives.

---

## Quote

> *"We had assumed we were reaching most eligible patients. The screening showed us hundreds we'd simply never seen — not because anyone made a mistake, but because their history was scattered across records that never came together in one place."*
> — Illustrative quote, representative of clinical leadership feedback during rollout
