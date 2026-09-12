"""FastAPI HTTP server for RAG system."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from datetime import datetime

from src.models import ResearchQuery, ConfidenceLevel
from src.core import ApprovedRetriever, CitationValidator, LLMReasoner, AuditTrail
from src.database import init_db, SessionLocal

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="RAG Agentic Scientific Research System",
    description="Evidence-grounded research answers with complete audit trails",
    version="1.0.0",
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API documentation."""
    return {
        "name": "RAG Agentic Scientific Research System",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/query": "Submit research query",
            "GET /api/response/{audit_id}": "Get response by audit ID",
            "POST /api/review/{audit_id}": "Review and approve/reject response",
            "GET /api/audit/{audit_id}": "Export complete audit trail",
            "GET /api/sources": "List approved sources",
        },
    }


@app.get("/api/sources")
def list_sources(domain: str = None):
    """List available approved sources."""
    retriever = ApprovedRetriever()
    sources = retriever.sources

    if domain:
        sources = [s for s in sources if s.domain == domain]

    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type.value,
                "domain": s.domain,
                "approved": s.approved,
            }
            for s in sources
        ],
    }


@app.post("/api/query")
def submit_query(
    question: str,
    domain: str,
    user_id: str,
    context: str = "",
):
    """Submit research query and get evidence-grounded answer."""
    db = SessionLocal()

    try:
        # Create audit trail
        auditor = AuditTrail(db)
        audit_id = auditor.create_audit_id()

        # Create query
        query = ResearchQuery(
            query_text=question,
            domain=domain,
            user_id=user_id,
            context=context,
        )

        # Log query submission
        query_id = auditor.log_query_submission(query, audit_id)

        # Retrieve sources
        retriever = ApprovedRetriever()
        sources = retriever.retrieve(query)

        if not sources:
            return {
                "audit_id": audit_id,
                "error": "No approved sources found matching your query",
                "status": "no_sources",
            }

        auditor.log_retrieval(audit_id, query_id, sources, user_id)

        # Generate answer
        reasoner = LLMReasoner(use_stub=True)
        response, requires_review = reasoner.reason(query, sources, audit_id)

        # Validate citations
        validator = CitationValidator()
        response.citations = validator.validate_citations(response.citations, sources)
        response.reviewer_required = validator.should_require_review(
            response.citations
        ) or requires_review

        # Log response
        response_id = auditor.log_response(audit_id, query_id, response, user_id)

        return {
            "audit_id": audit_id,
            "response_id": response_id,
            "query_id": query_id,
            "answer": response.answer,
            "confidence": response.confidence.value,
            "citations": [
                {
                    "source_id": c.source_id,
                    "source_name": c.source_name,
                    "text": c.text,
                    "confidence": c.confidence,
                    "validated": c.validated,
                }
                for c in response.citations
            ],
            "gaps": response.gaps,
            "reviewer_required": response.reviewer_required,
            "status": "success",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/response/{audit_id}")
def get_response(audit_id: str):
    """Get response by audit ID."""
    db = SessionLocal()

    try:
        auditor = AuditTrail(db)
        audit_data = auditor.export_audit_trail(audit_id)

        if "error" in audit_data:
            raise HTTPException(status_code=404, detail=audit_data["error"])

        return audit_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/review/{audit_id}")
def review_response(
    audit_id: str,
    reviewer_id: str,
    decision: str,
    notes: str = "",
):
    """Review and approve/reject response."""
    if decision not in ["approved", "rejected", "escalated"]:
        raise HTTPException(status_code=400, detail="Invalid decision")

    db = SessionLocal()

    try:
        auditor = AuditTrail(db)

        # Get audit trail to find response
        audit_data = auditor.export_audit_trail(audit_id)
        if "error" in audit_data:
            raise HTTPException(status_code=404, detail=audit_data["error"])

        response = audit_data.get("response")
        if not response:
            raise HTTPException(status_code=404, detail="No response found")

        query_id = audit_data["query"]["id"]
        response_id = response["id"]

        # Log review
        auditor.log_review(audit_id, query_id, response_id, reviewer_id, decision, notes)

        return {
            "audit_id": audit_id,
            "decision": decision,
            "reviewer_id": reviewer_id,
            "notes": notes,
            "reviewed_at": datetime.utcnow().isoformat(),
            "status": "reviewed",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/audit/{audit_id}")
def export_audit(audit_id: str):
    """Export complete audit trail."""
    db = SessionLocal()

    try:
        auditor = AuditTrail(db)
        audit_data = auditor.export_audit_trail(audit_id)

        if "error" in audit_data:
            raise HTTPException(status_code=404, detail=audit_data["error"])

        return audit_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 80)
    print("🚀 RAG Agentic Scientific Research System - HTTP Server")
    print("=" * 80)
    print("\n📍 Local URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 ReDoc: http://localhost:8000/redoc")
    print("\n" + "=" * 80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
