from fastapi import FastAPI

from backend.app.observability.otel_setup import setup_observability
from backend.app.routers import domains, extraction, health, ingest, query


def create_app() -> FastAPI:
    app = FastAPI(
        title="Biomedical Agentic RAG",
        description="Literature review & drug-discovery intelligence backend",
    )
    setup_observability(app)  # no-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set
    app.include_router(health.router)
    app.include_router(domains.router)
    app.include_router(query.router)
    app.include_router(ingest.router)
    app.include_router(extraction.router)

    @app.get("/")
    def root() -> dict:
        return {
            "service": "Biomedical Agentic RAG",
            "docs": "/docs",
            "health": "/health",
            "domains": "/domains",
        }

    return app


app = create_app()
