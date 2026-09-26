from fastapi import APIRouter, HTTPException

from backend.app.domains.loader import (
    DomainConfigError,
    DomainNotFoundError,
    list_domain_names,
    load_domain,
)

router = APIRouter()


@router.get("/domains")
def list_domains() -> dict:
    """Lists every domain that loads cleanly. A single malformed YAML file
    is reported in `errors` rather than crashing the whole listing for every
    other (valid) domain.
    """
    domains = []
    errors = []
    for name in list_domain_names():
        try:
            cfg = load_domain(name)
        except DomainConfigError as exc:
            errors.append({"name": name, "error": str(exc)})
            continue
        domains.append(cfg.summary())
    return {"domains": domains, "errors": errors}


@router.get("/domains/{name}")
def get_domain(name: str) -> dict:
    try:
        cfg = load_domain(name)
    except DomainNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return cfg.model_dump()
