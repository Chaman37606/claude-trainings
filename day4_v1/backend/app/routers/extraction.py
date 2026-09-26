import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.agent.loop import AnthropicNotConfiguredError, run_query
from backend.app.domains.loader import (
    DomainConfigError,
    DomainNotFoundError,
    load_domain,
)

router = APIRouter()


class ExtractRequest(BaseModel):
    question: str
    domain: str = "drug_discovery"


class ExtractResponse(BaseModel):
    domain: str
    entities: dict


@router.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest) -> ExtractResponse:
    try:
        domain = load_domain(req.domain)
        if domain.extraction_schema is None:
            raise HTTPException(status_code=400, detail=f"Domain '{req.domain}' has no extraction_schema")

        result = run_query(
            domain=domain,
            user_input=req.question,
            response_schema=domain.extraction_schema,
        )
    except DomainNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AnthropicNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        entities = json.loads(result.answer_text) if result.answer_text else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502, detail=f"Model returned non-JSON output: {exc}"
        ) from exc

    return ExtractResponse(domain=domain.name, entities=entities)
