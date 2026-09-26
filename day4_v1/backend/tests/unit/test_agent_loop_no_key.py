"""get_client() must refuse to fall back to ambient environment credentials
(ANTHROPIC_AUTH_TOKEN/ANTHROPIC_BASE_URL) when this app's own
ANTHROPIC_API_KEY isn't set — those env vars may belong to an unrelated
session (e.g. the Claude Code session driving development), and silently
using them would make a real authenticated call nobody asked for.
"""
import pytest

from backend.app.agent import loop as loop_module
from backend.app.agent.loop import AnthropicNotConfiguredError, get_client


@pytest.fixture(autouse=True)
def _reset_client_cache(monkeypatch):
    monkeypatch.setattr(loop_module, "_client", None)
    yield
    loop_module._client = None


def test_get_client_refuses_when_no_api_key_configured(monkeypatch):
    monkeypatch.setattr(loop_module.settings, "anthropic_api_key", "")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://example-should-never-be-called.invalid")

    with pytest.raises(AnthropicNotConfiguredError):
        get_client()


def test_get_client_succeeds_when_api_key_configured(monkeypatch):
    monkeypatch.setattr(loop_module.settings, "anthropic_api_key", "sk-test-key")
    client = get_client()
    assert client is not None
