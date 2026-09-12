import click
import json
from datetime import datetime
from pathlib import Path

from src.models import ResearchQuery, ConfidenceLevel
from src.core import ApprovedRetriever, CitationValidator, LLMReasoner, AuditTrail
from src.database import init_db, SessionLocal
from src.config import REVIEWER_ID


@click.group()
def cli():
    """RAG Agentic Scientific Research System CLI."""
    pass


@cli.command()
@click.option("--question", required=True, help="Research question to answer")
@click.option("--domain", required=True, help="Research domain (e.g., pharmacology)")
@click.option("--user", required=True, help="User ID submitting the query")
@click.option("--context", default="", help="Additional context for the query")
def submit_query(question: str, domain: str, user: str, context: str):
    """Submit a research query and get evidence-grounded answer."""
    click.echo(f"📋 Submitting query: {question[:50]}...")

    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Create audit trail
        auditor = AuditTrail(db)
        audit_id = auditor.create_audit_id()
        click.echo(f"🔖 Audit ID: {audit_id}")

        # Create query
        query = ResearchQuery(query_text=question, domain=domain, user_id=user, context=context)

        # Log query submission
        query_id = auditor.log_query_submission(query, audit_id)
        click.echo(f"✓ Query logged (ID: {query_id})")

        # Retrieve sources
        click.echo("🔍 Retrieving approved sources...")
        retriever = ApprovedRetriever()
        sources = retriever.retrieve(query)
        click.echo(f"✓ Retrieved {len(sources)} approved sources")

        if not sources:
            click.echo("❌ No approved sources found matching your query.")
            auditor.log_retrieval(audit_id, query_id, [], user)
            db.close()
            return

        auditor.log_retrieval(audit_id, query_id, sources, user)

        # Show sources
        click.echo("\n📚 Sources retrieved:")
        for s in sources[:3]:
            click.echo(f"  - [{s.id}] {s.name}")

        # Generate answer with LLM (use stub for testing)
        click.echo("\n🤔 Generating evidence-grounded answer...")
        reasoner = LLMReasoner(use_stub=True)
        response, requires_review = reasoner.reason(query, sources, audit_id)
        click.echo(f"✓ Answer generated (confidence: {response.confidence.value})")

        # Validate citations
        click.echo("✓ Validating citations...")
        validator = CitationValidator()
        response.citations = validator.validate_citations(response.citations, sources)
        response.reviewer_required = validator.should_require_review(response.citations) or requires_review

        # Log response
        response_id = auditor.log_response(audit_id, query_id, response, user)
        click.echo(f"✓ Response logged (ID: {response_id})")

        # Display results
        click.echo("\n" + "=" * 80)
        click.echo("📊 RESEARCH RESPONSE")
        click.echo("=" * 80)
        click.echo(f"\nQuestion: {question}")
        click.echo(f"Domain: {domain}")
        click.echo(f"Confidence: {response.confidence.value.upper()}")
        click.echo(f"\nAnswer:\n{response.answer}\n")

        if response.citations:
            click.echo("📖 Citations:")
            for i, cit in enumerate(response.citations, 1):
                status = "✓" if cit.validated else "⚠"
                click.echo(f"  {i}. {status} [{cit.source_id}] {cit.source_name}")
                click.echo(f"     Confidence: {cit.confidence:.2f}")
                click.echo(f"     Claim: {cit.claim_supported}")

        if response.gaps:
            click.echo(f"\n⚠ Knowledge Gaps:")
            for gap in response.gaps:
                click.echo(f"  - {gap}")

        if response.reviewer_required:
            click.echo(f"\n⚠ REVIEWER SIGN-OFF REQUIRED")
            click.echo(f"   Use: rag-system review-response --audit-id {audit_id}")
        else:
            click.echo(f"\n✓ Response approved (no review needed)")

        click.echo(f"\n🔖 Full audit trail: rag-system export-audit --audit-id {audit_id}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
@click.option("--audit-id", required=True, help="Audit ID of the response to review")
@click.option("--reviewer", default=REVIEWER_ID, help="Reviewer ID")
@click.option("--decision", required=True, type=click.Choice(["approved", "rejected", "escalated"]))
@click.option("--notes", default="", help="Reviewer notes")
def review_response(audit_id: str, reviewer: str, decision: str, notes: str):
    """Review and approve/reject a research response."""
    click.echo(f"👤 Reviewer: {reviewer}")
    click.echo(f"🔖 Audit ID: {audit_id}")
    click.echo(f"📋 Decision: {decision.upper()}")

    init_db()
    db = SessionLocal()

    try:
        auditor = AuditTrail(db)

        # Get audit trail to find response
        audit_data = auditor.export_audit_trail(audit_id)
        if "error" in audit_data:
            click.echo(f"❌ {audit_data['error']}", err=True)
            return

        response = audit_data.get("response")
        if not response:
            click.echo(f"❌ No response found for audit {audit_id}", err=True)
            return

        query_id = audit_data["query"]["id"]
        response_id = response["id"]

        # Log review
        auditor.log_review(audit_id, query_id, response_id, reviewer, decision, notes)
        click.echo(f"✓ Review recorded")

        click.echo("\n" + "=" * 80)
        click.echo("✅ REVIEW COMPLETE")
        click.echo("=" * 80)
        click.echo(f"Decision: {decision.upper()}")
        if notes:
            click.echo(f"Notes: {notes}")
        click.echo(f"\nExport full trail: rag-system export-audit --audit-id {audit_id}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
@click.option("--audit-id", required=True, help="Audit ID to export")
@click.option("--output", default=None, help="Output file (default: stdout)")
def export_audit(audit_id: str, output: str):
    """Export complete immutable audit trail."""
    click.echo(f"📤 Exporting audit trail: {audit_id}")

    init_db()
    db = SessionLocal()

    try:
        auditor = AuditTrail(db)
        audit_data = auditor.export_audit_trail(audit_id)

        if "error" in audit_data:
            click.echo(f"❌ {audit_data['error']}", err=True)
            return

        # Output as JSON
        json_output = json.dumps(audit_data, indent=2, default=str)

        if output:
            Path(output).write_text(json_output)
            click.echo(f"✓ Audit trail exported to: {output}")
        else:
            click.echo("\n" + "=" * 80)
            click.echo(json_output)
            click.echo("=" * 80)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
@click.option("--approved-only", is_flag=True, help="Show only approved sources")
@click.option("--domain", default=None, help="Filter by domain")
def list_sources(approved_only: bool, domain: str):
    """List available approved sources."""
    click.echo("📚 Available Approved Sources\n")

    retriever = ApprovedRetriever()

    filtered_sources = retriever.sources
    if approved_only:
        filtered_sources = [s for s in filtered_sources if s.approved]
    if domain:
        filtered_sources = [s for s in filtered_sources if s.domain == domain]

    for source in filtered_sources:
        status = "✓" if source.approved else "✗"
        click.echo(f"{status} [{source.id}] {source.name}")
        click.echo(f"   Type: {source.type.value} | Domain: {source.domain}")
        click.echo(f"   Content preview: {source.content[:80]}...")
        click.echo()


if __name__ == "__main__":
    cli()
