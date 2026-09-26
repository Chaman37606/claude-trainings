"""Loads and validates per-domain configuration YAML files.

Every other module (tools, RAG pipeline, agent loop, routers) reads domain
behavior through DomainConfig rather than hardcoding per-domain logic.
"""
from __future__ import annotations

import re
from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

DOMAINS_DIR = Path(__file__).parent
_SAFE_DOMAIN_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


class DomainConfig(BaseModel):
    name: str
    display_name: str
    description: str
    system_prompt: str
    allowed_tools: list[str] = Field(default_factory=list)
    collection_name: str
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 6
    extraction_schema: dict | None = None

    @field_validator("allowed_tools")
    @classmethod
    def _non_empty_tools(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("allowed_tools must list at least one tool")
        return v

    def summary(self) -> dict:
        """The subset of fields shown in domain-listing views (the /domains
        router and the custom MCP server's list_domains tool) — kept here so
        both stay in sync rather than each hardcoding the same field list.
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "supports_extraction": self.extraction_schema is not None,
        }


class DomainNotFoundError(KeyError):
    pass


class DomainConfigError(ValueError):
    pass


def list_domain_names() -> list[str]:
    return sorted(p.stem for p in DOMAINS_DIR.glob("*.yaml"))


@cache
def load_domain(name: str) -> DomainConfig:
    # `name` comes straight from request bodies (QueryRequest.domain, etc.) —
    # reject anything but a plain identifier before it reaches the filesystem,
    # otherwise "../../../etc/passwd"-style values would probe outside DOMAINS_DIR.
    if not _SAFE_DOMAIN_NAME.match(name):
        raise DomainNotFoundError(f"Invalid domain name '{name}'")
    path = DOMAINS_DIR / f"{name}.yaml"
    if not path.exists():
        raise DomainNotFoundError(
            f"Unknown domain '{name}'. Available: {list_domain_names()}"
        )
    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise DomainConfigError(f"Invalid YAML in {path}: {exc}") from exc

    try:
        return DomainConfig(**raw)
    except Exception as exc:  # pydantic ValidationError, etc.
        raise DomainConfigError(f"Invalid domain config in {path}: {exc}") from exc


def clear_cache() -> None:
    """Test/dev helper — drop cached DomainConfig instances."""
    load_domain.cache_clear()
