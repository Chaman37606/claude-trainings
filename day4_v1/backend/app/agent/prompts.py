from backend.app.domains.loader import DomainConfig


def build_system_prompt(domain: DomainConfig) -> str:
    return domain.system_prompt.strip()
