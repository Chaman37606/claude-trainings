# Local Deployment Guide

This guide walks through setting up and running the RAG system locally.

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- SQLite3 (usually included with Python)

## Setup

### 1. Clone/Download the Project

```bash
cd /home/labuser/claude_training/RAG_AGENTIC_SCIENTIFIC
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -m src.api.cli list-sources --domain pharmacology
```

You should see 10 approved sources listed.

## Running Locally

### Quick Start (3 Steps)

**Step 1: Submit a Query**

```bash
python -m src.api.cli submit-query \
  --question "What is the efficacy of drug X for condition Y?" \
  --domain pharmacology \
  --user "researcher_01" \
  --context "Adult patients, 18-65 years"
```

Note the `Audit ID` in the output (e.g., `audit_abc123def456`).

**Step 2: Review the Response**

```bash
python -m src.api.cli review-response \
  --audit-id audit_abc123def456 \
  --reviewer "dr_smith@company.org" \
  --decision approved \
  --notes "Evidence well-grounded and citations validated"
```

**Step 3: Export the Audit Trail**

```bash
python -m src.api.cli export-audit \
  --audit-id audit_abc123def456 \
  --output my_decision_audit.json
```

View the complete audit trail:

```bash
cat my_decision_audit.json | python -m json.tool
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Module

```bash
pytest tests/test_retriever.py -v
pytest tests/test_validator.py -v
pytest tests/test_integration.py -v
```

### Run Specific Test

```bash
pytest tests/test_integration.py::test_full_rag_loop -v
```

## Using the Python API Directly

Instead of CLI, you can use the system programmatically:

```python
from src.models import ResearchQuery
from src.core import ApprovedRetriever, CitationValidator, LLMReasoner, AuditTrail
from src.database import init_db, SessionLocal

# Initialize
init_db()
db = SessionLocal()

# Create query
query = ResearchQuery(
    query_text="What is efficacy of drug X?",
    domain="pharmacology",
    user_id="user_123"
)

# Retrieve sources
retriever = ApprovedRetriever()
sources = retriever.retrieve(query)
print(f"Retrieved {len(sources)} sources")

# Generate answer
reasoner = LLMReasoner(use_stub=True)
auditor = AuditTrail(db)
audit_id = auditor.create_audit_id()

response, requires_review = reasoner.reason(query, sources, audit_id)

# Validate citations
validator = CitationValidator()
response.citations = validator.validate_citations(response.citations, sources)

# Log and export
query_id = auditor.log_query_submission(query, audit_id)
auditor.log_retrieval(audit_id, query_id, sources, query.user_id)
auditor.log_response(audit_id, query_id, response, query.user_id)

# View audit
audit_data = auditor.export_audit_trail(audit_id)
print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence}")
print(f"Citations: {len(response.citations)}")

db.close()
```

## Database

### View Database Contents

```bash
sqlite3 audit.db
```

Query example:

```sql
-- See all queries
SELECT id, query_text, user_id, submitted_at FROM research_queries;

-- See all responses
SELECT id, answer, confidence FROM research_responses;

-- See audit timeline
SELECT action, timestamp, user_id, decision FROM audit_logs ORDER BY timestamp;
```

### Reset Database

```bash
rm audit.db
python -c "from src.database import init_db; init_db(); print('✓ Database reset')"
```

## Configuration

### Environment Variables

```bash
# Use mock sources
export APPROVED_SOURCES_FILE=data/sources_approved.json

# SQLite database location
export DATABASE_URL=sqlite:///./audit.db

# Default reviewer
export REVIEWER_ID=dr_default@research.org

# For real LLM calls (optional)
export ANTHROPIC_API_KEY=sk-...
```

### Adding Custom Sources

Edit `data/sources_approved.json`:

```json
{
  "sources": [
    {
      "id": "source_custom_001",
      "name": "My Custom Source",
      "type": "report",
      "domain": "pharmacology",
      "approved": true,
      "content": "Research finding: drug X shows efficacy...",
      "metadata": {
        "date": "2026-01-01",
        "source": "internal-research"
      }
    }
  ]
}
```

Restart the system:

```bash
python -m src.api.cli list-sources
```

### Adding New Domains

Edit `src/config.py`:

```python
APPROVED_DOMAINS = [
    "pharmacology",
    "immunology",
    "oncology",
    "infectious_disease",
    "cardiology",
    "neurology",
    "your_new_domain",  # Add here
]
```

## Troubleshooting

### Issue: "No module named 'src'"

**Solution:** Make sure you're running from the project root:

```bash
cd /home/labuser/claude_training/RAG_AGENTIC_SCIENTIFIC
python -m src.api.cli list-sources
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:** The system uses stub mode by default (no API key needed). For real LLM calls:

```bash
export ANTHROPIC_API_KEY=your_key_here
# Edit src/api/cli.py and change:
# reasoner = LLMReasoner(use_stub=True)
# to:
# reasoner = LLMReasoner(use_stub=False)
```

### Issue: "Database is locked"

**Solution:** Another process is using the database. Try:

```bash
ps aux | grep python
# Kill any other processes if needed
lsof | grep audit.db
```

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:** Reinstall dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## Performance Tips

1. **Cache sources**: Retriever loads all sources into memory on init. For large corpora, consider lazy loading.

2. **Database indexes**: Already set on `audit_id` and `query_id`. Add more if querying large datasets:

```python
from sqlalchemy import text
db.execute(text("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_logs(user_id)"))
```

3. **Batch operations**: For multiple queries, keep one session open:

```python
db = SessionLocal()
for query in queries:
    # Process query
    pass
db.close()
```

## Extending the System

### Add New CLI Command

Edit `src/api/cli.py`:

```python
@cli.command()
@click.option("--param", required=True)
def my_command(param):
    """My new command."""
    click.echo(f"Running with {param}")
```

Run:

```bash
python -m src.api.cli my-command --param value
```

### Custom Source Filter

Edit `src/core/retriever.py`:

```python
def retrieve_by_type(self, query: ResearchQuery, source_type: str) -> List[Source]:
    """Retrieve sources of specific type."""
    sources = self.retrieve(query)
    return [s for s in sources if s.type.value == source_type]
```

### Custom Confidence Calculation

Edit `src/core/validator.py`:

```python
def calculate_confidence(self, citation_text: str, source_content: str) -> float:
    # Your custom scoring logic
    pass
```

## Next Steps

1. **Add Real Data**: Update `data/sources_approved.json` with your research corpus
2. **Configure Domains**: Edit `src/config.py` for your specific research areas
3. **Set Up Workflows**: Automate with cron jobs or webhooks
4. **Connect to Documentation**: Link responses to your internal wiki/knowledge base
5. **Monitor Audit Trails**: Set up alerts on reviewer decisions

## Support

For issues or questions:
- Check [CLAUDE.md](./CLAUDE.md) for architecture details
- Review test cases in `tests/` for usage examples
- Check logs in `audit.db` for operation history
