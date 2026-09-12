# RAG Agentic Scientific Research System

This project implements a Retrieval-Augmented Generation (RAG) system for answering research questions with evidence-grounded answers, structured output, and complete audit trails.

## Overview

The system follows this agentic loop:

1. **Query Submission** — Research question is submitted with domain and context
2. **Approved Source Retrieval** — Query is matched against approved sources (hook-enforced allowlist)
3. **LLM Reasoning** — Claude LLM generates answer grounded in retrieved sources
4. **Citation Validation** — Each citation is validated against source content
5. **Audit Trail Recording** — All operations logged immutably
6. **Reviewer Sign-off** — High-confidence responses skip review; lower-confidence require human review
7. **Decision Delivery** — Structured JSON response with answer, citations, gaps, confidence

## Key Commitments

✅ **Retrieve only from approved sources** — Allowlist enforced by governance hooks  
✅ **Ground every claim** — Each factual statement resolves to a citation  
✅ **Return structured output** — Answer + confidence + citations + gaps  
✅ **Fail gracefully** — Refuse or escalate rather than fabricate  

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Submit a Query

```bash
python -m src.api.cli submit-query \
  --question "What is the efficacy of drug X for condition Y?" \
  --domain pharmacology \
  --user researcher_01 \
  --context "Patient population: adults 18-65"
```

The system will:
1. Search approved sources
2. Generate answer with citations
3. Validate citations against sources
4. Either approve immediately or flag for reviewer

### Review a Response

```bash
python -m src.api.cli review-response \
  --audit-id <audit_id> \
  --reviewer dr_smith@research.org \
  --decision approved \
  --notes "Evidence well-grounded, confidence justified"
```

### Export Audit Trail

```bash
python -m src.api.cli export-audit \
  --audit-id <audit_id> \
  --output audit_trail.json
```

## Project Structure

- **`src/models.py`** — Pydantic data models for queries, responses, citations
- **`src/database.py`** — SQLAlchemy ORM for audit trail persistence
- **`src/config.py`** — Configuration, approved sources, validated domains
- **`src/core/retriever.py`** — Approved source lookup with keyword ranking
- **`src/core/reasoner.py`** — LLM reasoning with citation enforcement
- **`src/core/validator.py`** — Citation validation + confidence scoring
- **`src/core/auditor.py`** — Audit trail recording + export
- **`src/api/cli.py`** — Click-based CLI interface
- **`.claude/hooks/`** — Governance hooks (approve/deny retrieval, log operations)
- **`data/sources_approved.json`** — Approved source corpus (mock data)
- **`tests/`** — Unit and integration tests

## Governance

### Approved Sources Allowlist

Sources are defined in `data/sources_approved.json` with metadata:
- `id`: Unique identifier
- `name`: Human-readable name
- `type`: journal | regulatory | report | database
- `domain`: pharmacology | immunology | oncology | etc.
- `approved`: Boolean flag
- `content`: Actual evidence text

Only sources with `approved: true` can be retrieved.

### Audit Trail

Every operation is logged to SQLite:
- Query submission
- Source retrieval
- Answer generation
- Citation validation
- Reviewer decisions

Immutable records with timestamps, user_id, decisions, and full details.

### Confidence Scoring

**High**: 3+ independent approved sources agree, strong evidence base  
**Medium**: 1-2 sources available, reasonable evidence with gaps  
**Low**: Very limited sources, significant uncertainty  

Responses with medium/low confidence automatically flag for reviewer sign-off.

### Citation Validation

Citations are scored on confidence (0.0-1.0):
- **1.0**: Exact match in source
- **0.95**: Near-exact, key phrase found
- **0.7-0.9**: Fuzzy match, major keywords present
- **<0.7**: Citation not found, flagged for review

Citations with confidence < 0.7 trigger mandatory reviewer approval.

## Graceful Failure

The system refuses to answer in these scenarios:

| Scenario | Response | Action |
|----------|----------|--------|
| No matching sources | Low confidence, gaps populated | Log + flag for review |
| Insufficient evidence | Refuse to answer | Escalate to reviewer |
| Citation not found | Low confidence | Flag citation, require review |
| Query outside domain | Refuse with reason | Escalate as out_of_scope |
| Invalid domain | Error | Reject upfront |

## Testing

Run unit tests:

```bash
pytest tests/test_retriever.py -v
pytest tests/test_validator.py -v
pytest tests/test_integration.py -v
```

Run full integration test:

```bash
pytest tests/test_integration.py::test_full_rag_loop -v
```

## API Design

### CLI Commands

- `submit-query` — Submit research question → returns audit_id
- `review-response` — Approve/reject response with notes
- `export-audit` — Export immutable audit trail as JSON
- `list-sources` — List available approved sources

### Data Flow

```
ResearchQuery
  ↓
ApprovedRetriever.retrieve() → List[Source]
  ↓
LLMReasoner.reason() → ResearchResponse
  ↓
CitationValidator.validate_citations() → validated_citations
  ↓
AuditTrail.log_response() → audit_id + response_id
  ↓
(If requires_review) → Manual reviewer approval
  ↓
Response ready for decision
```

## Configuration

Environment variables:

- `APPROVED_SOURCES_FILE` — Path to sources JSON (default: `data/sources_approved.json`)
- `DATABASE_URL` — SQLAlchemy database URL (default: `sqlite:///./audit.db`)
- `REVIEWER_ID` — Default reviewer email (default: `dr_default@research.org`)

## Example Flow

```bash
# 1. Submit query
$ python -m src.api.cli submit-query \
    --question "Efficacy of drug X?" \
    --domain pharmacology \
    --user jane_smith

📋 Submitting query: Efficacy of drug X?...
🔖 Audit ID: audit_a1b2c3d4e5f6
✓ Query logged
🔍 Retrieving approved sources...
✓ Retrieved 7 approved sources
🤔 Generating evidence-grounded answer...
⚠ REVIEWER SIGN-OFF REQUIRED

# 2. Review response
$ python -m src.api.cli review-response \
    --audit-id audit_a1b2c3d4e5f6 \
    --decision approved \
    --notes "All citations validated"

✓ Review recorded
✅ REVIEW COMPLETE

# 3. Export audit trail
$ python -m src.api.cli export-audit \
    --audit-id audit_a1b2c3d4e5f6 \
    --output trail.json

✓ Audit trail exported to: trail.json
```

## Validation Strategy

The system validates through multiple layers:

1. **Domain validation** — Query must be in approved domain list
2. **Source approval** — Only approved sources can be retrieved
3. **Citation grounding** — Every claim must cite a source
4. **Confidence scoring** — Evidence quality assessed quantitatively
5. **Manual review** — Low-confidence responses require human approval
6. **Audit trail** — All decisions immutably logged

This multi-layer approach ensures evidence integrity without manual intervention on every query.
