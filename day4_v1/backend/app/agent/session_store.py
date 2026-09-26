"""In-memory session history store — POC scope only (lost on process restart).

Keyed by session_id; holds raw Messages-API-format history per session so the
agent loop's context_manager can trim/summarize it turn over turn.
"""
from __future__ import annotations

_sessions: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def set_history(session_id: str, messages: list[dict]) -> None:
    _sessions[session_id] = messages


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
