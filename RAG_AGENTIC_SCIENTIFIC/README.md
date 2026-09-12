# RAG Agentic Scientific Research System

A Python-based Retrieval-Augmented Generation system that answers research questions with evidence-grounded responses, structured output, and complete audit trails. Designed for R&D teams that need trustworthy, traceable evidence synthesis.

## Features

✅ **Evidence-Grounded Answers** — Every claim resolves to an approved source  
✅ **Structured Output** — Answer + confidence (high/medium/low) + citations + gaps  
✅ **Approved Source Allowlist** — Only retrieves from curated corpus  
✅ **Citation Validation** — Confidence scoring with fuzzy matching  
✅ **Immutable Audit Trails** — Complete record of query → retrieval → reasoning → review → decision  
✅ **Governance Hooks** — Claude Code integration for policy enforcement  
✅ **CLI Interface** — Easy-to-use command-line for researchers  

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### 1. Submit a Research Query

```bash
python -m src.api.cli submit-query \
  --question "What is the efficacy of drug X for condition Y?" \
  --domain pharmacology \
  --user researcher_01 \
  --context "Adult patients aged 18-65"
```

**Output:**
- Retrieves approved sources matching the query
- Generates evidence-grounded answer
- Validates citations
- Returns audit_id for tracking

```
🔖 Audit ID: audit_c08a9dea3823
✓ Retrieved 10 approved sources
✓ Answer generated (confidence: medium)
✓ Response logged

📊 RESEARCH RESPONSE
Question: What is the efficacy of drug X for condition Y?
Confidence: MEDIUM

Answer:
Based on the approved sources in our corpus, the evidence indicates that:
[grounded evidence with citations]

📖 Citations:
  1. ✓ [source_007] Cochrane Review Database 2024
     Confidence: 1.00
  2. ✓ [source_004] WHO Expert Committee Report
     Confidence: 1.00

⚠ Knowledge Gaps:
  - Long-term follow-up data limited
  - Rare adverse events not well characterized

⚠ REVIEWER SIGN-OFF REQUIRED
```

### 2. Review the Response

```bash
python -m src.api.cli review-response \
  --audit-id audit_c08a9dea3823 \
  --reviewer dr_smith@research.org \
  --decision approved \
  --notes "Evidence well-grounded, citations validated"
```

### 3. Export Complete Audit Trail

```bash
python -m src.api.cli export-audit \
  --audit-id audit_c08a9dea3823 \
  --output audit_trail.json
```

**Immutable record includes:**
- Original query + context + submitter
- All sources retrieved with IDs
- Generated answer + confidence + gaps
- Each citation with confidence scores
- Reviewer decision with timestamp + notes
- Complete timeline of all operations

## System Architecture

### Agentic Loop

```
Query Submission
    ↓
Approved Source Retrieval (hook-enforced)
    ↓
Evidence Grounding Check (refuse if no match)
    ↓
LLM Reasoning with Citations
    ↓
Citation Validation (confidence scoring)
    ↓
Audit Trail Recording
    ↓
Reviewer Sign-off (if required)
    ↓
Structured JSON Response
```

### Core Modules

- **`src/core/retriever.py`** — Keyword search over approved sources
- **`src/core/reasoner.py`** — LLM-based answer generation with citation extraction
- **`src/core/validator.py`** — Citation validation (fuzzy matching, confidence scoring)
- **`src/core/auditor.py`** — Immutable audit trail management
- **`src/database.py`** — SQLAlchemy ORM for persistence

### Governance

- **`.claude/hooks/`** — Claude Code governance hooks
- **`data/sources_approved.json`** — Curated source corpus
- **`src/config.py`** — Approved domains, source allowlist

## Configuration

### Environment Variables

```bash
export APPROVED_SOURCES_FILE=data/sources_approved.json
export DATABASE_URL=sqlite:///./audit.db
export REVIEWER_ID=dr_default@research.org
export ANTHROPIC_API_KEY=<your-key>  # Optional: for real LLM calls
```

### Adding Sources

Edit `data/sources_approved.json`:

```json
{
  "sources": [
    {
      "id": "source_001",
      "name": "Nature Medicine 2024",
      "type": "journal",
      "domain": "pharmacology",
      "approved": true,
      "content": "Study shows drug X reduces symptoms by 40%...",
      "metadata": {
        "authors": ["Smith et al."],
        "date": "2024-03-15"
      }
    }
  ]
}
```

### Approved Domains

Configure in `src/config.py`:

```python
APPROVED_DOMAINS = [
    "pharmacology",
    "immunology",
    "oncology",
    "infectious_disease",
    "cardiology",
    "neurology",
]
```

## Confidence Scoring

**High Confidence (≥3 sources)**: Consistent agreement across independent sources  
**Medium Confidence (1-2 sources)**: Reasonable evidence with identifiable gaps  
**Low Confidence (<1 source)**: Insufficient evidence, escalate to reviewer  

Citations scored on:
- **1.0**: Exact text match in source
- **0.95**: Key phrase found
- **0.7-0.9**: Fuzzy match with major keywords
- **<0.7**: Citation not found, flagged for review

## CLI Commands

```bash
# Submit query
python -m src.api.cli submit-query --help

# Review response
python -m src.api.cli review-response --help

# Export audit trail
python -m src.api.cli export-audit --help

# List available sources
python -m src.api.cli list-sources [--domain pharmacology]
```

## Testing

```bash
# Unit tests
pytest tests/test_retriever.py -v
pytest tests/test_validator.py -v

# Integration test
pytest tests/test_integration.py::test_full_rag_loop -v

# Full test suite
pytest tests/ -v
```

## Database Schema

### Tables

- **`research_queries`** — Original research questions
- **`research_responses`** — Generated answers with confidence + gaps
- **`citations`** — Evidence citations (source_id, text, confidence)
- **`audit_logs`** — Immutable timeline of all operations

All records linked by `audit_id` for complete traceability.

## Design Principles

1. **No Hallucination** — Refuse to answer rather than guess
2. **Audit Everything** — Complete record for compliance
3. **Grade Evidence** — Quantitative confidence scores
4. **Human Override** — Reviewer approval for uncertain responses
5. **Graceful Failure** — Clear errors, never silent falsehoods

## Deployment

### Standalone CLI

Already ready for single-researcher use:

```bash
python -m src.api.cli submit-query ...
```

### As Python Library

```python
from src.core import ApprovedRetriever, LLMReasoner, AuditTrail
from src.database import SessionLocal, init_db

init_db()
db = SessionLocal()

retriever = ApprovedRetriever()
reasoner = LLMReasoner()
auditor = AuditTrail(db)

sources = retriever.retrieve(query)
response, requires_review = reasoner.reason(query, sources, audit_id)
auditor.log_response(audit_id, query_id, response, user_id)
```

### With Real LLM

Replace stub mode in `src/api/cli.py`:

```python
reasoner = LLMReasoner(use_stub=False)  # Uses Claude API
```

## Failure Modes

| Scenario | Behavior |
|----------|----------|
| No matching sources | Return low confidence, populate gaps |
| <2 sources found | Flag for reviewer approval |
| Citation not validated | Lower confidence, mark for review |
| Query outside domain | Refuse with reason |
| Reviewer rejects | Log decision, suggest refinement |
| LLM unavailable | Use stub mode or error |

## Contributing

To extend the system:

1. Add new sources to `data/sources_approved.json`
2. Add new domains to `src/config.py`
3. Update validator thresholds in `src/core/validator.py`
4. Write tests for new features

## References

See [CLAUDE.md](./CLAUDE.md) for architecture, governance, and implementation details.
