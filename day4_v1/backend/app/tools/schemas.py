"""Shared input/output contracts for agent tools.

Every tool module exposes:
  - TOOL_SPEC: the Anthropic tool definition dict (name/description/input_schema)
  - a handler function matching the name in TOOL_SPEC, taking a validated
    pydantic input model and returning a JSON-serializable dict
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PubmedSearchInput(BaseModel):
    query: str = Field(..., description="PubMed search query")
    max_results: int = Field(5, ge=1, le=20)


class SemanticScholarSearchInput(BaseModel):
    query: str = Field(..., description="Semantic Scholar search query")
    limit: int = Field(5, ge=1, le=20)


class ChemblLookupInput(BaseModel):
    query: str = Field(..., description="Compound name, ChEMBL ID, or target name")
    # Matches TOOL_SPEC's input_schema enum below — kept as a Literal (not
    # plain str) so a malformed value fails validation instead of silently
    # falling through to the compound-search branch in chembl_lookup().
    kind: Literal["compound", "target"] = Field("compound", description="One of: compound, target")


class RagSearchInput(BaseModel):
    query: str = Field(..., description="Natural-language search over indexed passages")
    domain: str = Field(..., description="Domain collection to search")
    top_k: int = Field(6, ge=1, le=20)
