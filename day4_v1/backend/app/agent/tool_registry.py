"""Maps domain-allowed tool names to their Anthropic tool spec + handler.

Adding a tool: implement it in backend/app/tools/<name>_tool.py exposing
TOOL_SPEC + a handler function, then register it in _REGISTRY below.
"""
from __future__ import annotations

import time

from pydantic import BaseModel

from backend.app.observability.otel_setup import (
    tool_call_counter,
    tool_call_duration,
    tracer,
)
from backend.app.tools import (
    chembl_tool,
    pubmed_tool,
    rag_search_tool,
    semantic_scholar_tool,
)
from backend.app.tools.schemas import (
    ChemblLookupInput,
    PubmedSearchInput,
    RagSearchInput,
    SemanticScholarSearchInput,
)


class ToolEntry:
    def __init__(self, spec: dict, handler, input_model: type[BaseModel]):
        self.spec = spec
        self.handler = handler
        self.input_model = input_model

    def run(self, raw_input: dict) -> dict:
        validated = self.input_model(**raw_input)
        return self.handler(validated)


_REGISTRY: dict[str, ToolEntry] = {
    "pubmed_search": ToolEntry(pubmed_tool.TOOL_SPEC, pubmed_tool.pubmed_search, PubmedSearchInput),
    "semantic_scholar_search": ToolEntry(
        semantic_scholar_tool.TOOL_SPEC,
        semantic_scholar_tool.semantic_scholar_search,
        SemanticScholarSearchInput,
    ),
    "chembl_lookup": ToolEntry(chembl_tool.TOOL_SPEC, chembl_tool.chembl_lookup, ChemblLookupInput),
    "rag_search": ToolEntry(rag_search_tool.TOOL_SPEC, rag_search_tool.rag_search, RagSearchInput),
}


def specs_for(tool_names: list[str]) -> list[dict]:
    missing = [n for n in tool_names if n not in _REGISTRY]
    if missing:
        raise KeyError(f"Unknown tool(s) requested by domain config: {missing}")
    return [_REGISTRY[n].spec for n in tool_names]


def dispatch(tool_name: str, tool_input: dict) -> dict:
    start = time.perf_counter()
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)

        if tool_name not in _REGISTRY:
            result, outcome = {"error": f"Unknown tool '{tool_name}'"}, "unknown_tool"
        else:
            try:
                result, outcome = _REGISTRY[tool_name].run(tool_input), "ok"
            except Exception as exc:  # noqa: BLE001 — surfaced to the model as a tool error, not raised
                result, outcome = {"error": str(exc)}, "error"

        span.set_attribute("tool.outcome", outcome)

    tool_call_counter.add(1, {"tool": tool_name, "outcome": outcome})
    tool_call_duration.record(time.perf_counter() - start, {"tool": tool_name})
    return result
