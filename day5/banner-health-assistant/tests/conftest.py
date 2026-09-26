"""
Shared pytest fixtures for the Banner Health Clinical Assistant backend tests.

The backend (backend/main.py, database.py, models.py, schemas.py, engine.py,
crud.py, seed.py) uses flat/absolute imports (e.g. `from database import Base`,
`import crud`), meaning it expects `backend/` itself to be on sys.path as the
import root. We insert that path here, before any test module imports `main`,
`database`, etc. as bare top-level modules.

For API tests we also override FastAPI's `get_db` dependency with a fresh
in-memory SQLite database (seeded deterministically), so tests never touch or
depend on the real backend/banner_health.db file.
"""

import os
import sys

BACKEND_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import database
import seed
from database import Base, get_db
from main import app


@pytest.fixture()
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def TestingSessionLocal(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db_session(TestingSessionLocal):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(TestingSessionLocal):
    """A TestClient wired to an isolated, pre-seeded in-memory SQLite DB."""

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    # Seed the in-memory DB deterministically before any requests are made.
    seed_session = TestingSessionLocal()
    try:
        seed.seed_if_empty(seed_session)
    finally:
        seed_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def auth_headers(client):
    """Logs in as one of the seeded demo users and returns a ready-to-use
    Authorization header, for tests that need to call a protected route."""
    resp = client.post(
        "/api/auth/login",
        data={"username": "dr.chen", "password": "demo1234"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
