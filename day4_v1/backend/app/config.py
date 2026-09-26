from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    model_default: str = "claude-opus-5"
    model_cheap: str = "claude-sonnet-5"

    ncbi_email: str = "you@example.com"
    ncbi_api_key: str = ""

    semantic_scholar_api_key: str = ""

    chroma_persist_dir: str = "backend/chroma_data"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_base_url: str = "http://localhost:8000"

    # Empty = observability disabled (default, so pytest never touches the
    # network). Set to an OTLP gRPC endpoint (e.g. http://localhost:4317) to
    # enable traces + metrics export.
    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "biomed-agentic-rag-backend"


settings = Settings()
