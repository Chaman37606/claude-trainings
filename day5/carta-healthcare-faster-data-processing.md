# Carta Healthcare: 66% Faster Clinical Data Processing

### How an AI extraction system cut clinical data processing time by 66% while maintaining 99% accuracy

---

## Overview

Carta Healthcare specializes in transforming raw clinical data — buried in charts, registries, and unstructured records — into structured, analysis-ready data that health systems depend on for quality reporting, research, and compliance.

Carta Healthcare deployed an AI system that automates the extraction and structuring of clinical data from health records, cutting processing time by 66% while maintaining 99% accuracy.

> *This case study is illustrative, describing a representative deployment pattern for AI-driven clinical data abstraction.*

---

## The Challenge

Health systems are required to report structured clinical data for quality registries, regulatory compliance, and research — but that data rarely starts out structured:

- **Manual abstraction is slow.** Clinical data abstractors read through charts line by line, manually pulling and coding data points into registry-ready fields.
- **Volume keeps growing.** Registry requirements, quality measures, and research demands keep expanding, but abstraction teams don't scale at the same rate.
- **Accuracy is non-negotiable.** Registry submissions and compliance reporting require near-perfect accuracy — errors can mean incorrect quality scores, failed audits, or flawed research conclusions.
- **Backlogs delay everything downstream.** Slow abstraction delays quality reporting, research timelines, and the insights health systems need to act on.

Health systems needed a way to abstract clinical data dramatically faster — without sacrificing the accuracy that manual review was relied upon to guarantee.

---

## The Solution

Carta Healthcare built an AI-driven abstraction system with two core capabilities:

### 1. Automated extraction
The system reads unstructured and semi-structured clinical records — notes, reports, charts — and automatically extracts the specific data elements required for a given registry, quality measure, or research protocol.

### 2. Automated structuring with accuracy safeguards
Extracted data is mapped into standardized, registry-ready fields. A validation layer flags low-confidence extractions for human abstractor review, ensuring the system's speed doesn't come at the expense of the accuracy abstraction teams are accountable for.

As with other clinical AI deployments, human abstractors remain **in the loop**: the system handles the high-volume, high-confidence extraction work, while abstractors focus their expertise on validation and the edge cases the system flags.

---

## Implementation

Carta Healthcare's rollout followed a phased approach:

1. **Registry/use-case selection** — identifying which registries or quality measures to automate first, based on volume and abstraction burden.
2. **Model validation against gold-standard data** — running the extraction system against previously abstracted, human-verified charts to confirm accuracy before go-live.
3. **Parallel run** — operating the AI system alongside manual abstraction for a defined period, comparing outputs to build confidence.
4. **Production rollout** — shifting abstraction teams to a review-and-validate workflow, with the AI system handling first-pass extraction at scale.
5. **Continuous monitoring** — tracking accuracy against sampled human review on an ongoing basis to catch drift and maintain the 99% accuracy bar.

---

## High-Level Design (HLD)

The system is architected as an extraction-then-structuring pipeline with a confidence gate that decides what needs a human abstractor and what doesn't.

**Core components:**
- **Document Ingestion (OCR)** — accepts charts in multiple formats (PDF, HL7, CCD/CCDA, scanned images) and produces machine-readable text, using OCR where source documents are scanned.
- **NLP Extraction Engine** — identifies the specific clinical data elements (diagnoses, procedures, lab values, dates) required for a given registry or measure.
- **Field Mapping/Structuring Layer** — maps extracted entities into standardized, registry-ready schema fields with unit/format normalization.
- **Confidence-Based Validation Queue** — routes low-confidence extractions to human abstractors; high-confidence extractions proceed automatically.
- **Registry Export** — packages validated, structured records for registry or compliance submission.

**Data flow:**
`Raw Chart → Ingestion (OCR) → NLP Extraction → Field Mapping → Confidence Check → (Auto-Accept | Human Review) → Structured Registry Record`

## Low-Level Design (LLD)

- **Per-element extraction models** — a dedicated extraction model/prompt exists per data element type (diagnosis, procedure code, lab value, date), since each has distinct source patterns and validation rules.
- **Schema mapping** — extracted entities are mapped to the target registry's schema (e.g., a cardiovascular or surgical registry spec), including unit normalization (e.g., lab values reported in different units) and date/format standardization.
- **Confidence scoring & routing** — each extracted field carries a confidence score; fields below a defined threshold are routed to the validation queue rather than auto-accepted, keeping the accuracy bar at 99% without requiring 100% manual review.
- **Abstractor review UI** — presents the extracted value alongside a highlighted snippet from the source document, so an abstractor can confirm or correct in seconds rather than re-reading the full chart.
- **Accuracy monitoring** — a sampling job periodically pulls a subset of auto-accepted records and compares them against fresh gold-standard human abstraction, feeding an accuracy dashboard used to detect model drift before it affects registry submissions.

---

## Results / Impact

Illustrative outcomes from the deployment:

- **66% faster processing** — clinical data processing time dropped by 66% compared to fully manual abstraction.
- **99% accuracy maintained** — automated extraction matched human-abstractor-level accuracy, validated against gold-standard chart review.
- **Reduced abstraction backlog** — registries and quality reports that previously lagged behind schedule caught up to real-time submission timelines.
- **Abstractor time reallocated** — abstraction teams shifted from repetitive data pulling to higher-value validation and complex-case review.

---

## Key Takeaways

For other health systems or registries considering a similar deployment:

- **Speed and accuracy aren't a trade-off when validation is built in.** A confidence-based review layer lets the system move fast on clear cases while routing uncertain ones to humans.
- **Validate against gold-standard data before go-live.** Parallel runs against previously verified charts build the evidence needed to trust automated extraction in production.
- **Abstractors become validators, not replaced.** The highest-value use of automation is removing repetitive extraction work, not removing clinical/abstraction expertise from the process.
- **Continuous accuracy monitoring matters as much as the initial rollout.** Sustained accuracy requires ongoing sampling and review, not a one-time validation.

---

## Quote

> *"We were skeptical that automation could hit our accuracy bar — abstraction accuracy is something we don't compromise on. Seeing it match our best abstractors, at more than half the processing time, changed how we think about where our team's time is best spent."*
> — Illustrative quote, representative of abstraction team leadership feedback during rollout
