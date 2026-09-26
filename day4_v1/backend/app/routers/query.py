import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.agent.loop import AnthropicNotConfiguredError, run_query
from backend.app.agent.session_store import get_history, set_history
from backend.app.domains.loader import (
    DomainConfigError,
    DomainNotFoundError,
    load_domain,
)

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    domain: str
    session_id: str | None = None


class ToolCallView(BaseModel):
    tool: str
    input: dict
    output: dict


class QueryResponse(BaseModel):
    session_id: str
    answer: str
    tool_calls: list[ToolCallView]


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    try:
        domain = load_domain(req.domain)
        session_id = req.session_id or str(uuid.uuid4())
        history = get_history(session_id)
        result = run_query(domain=domain, user_input=req.question, history=history)
    except DomainNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AnthropicNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    set_history(session_id, result.raw_messages)

    return QueryResponse(
        session_id=session_id,
        answer=result.answer_text,
        tool_calls=[ToolCallView(**tc) for tc in result.tool_calls],
    )
