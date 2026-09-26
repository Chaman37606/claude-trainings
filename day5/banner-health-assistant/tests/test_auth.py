"""
Auth-specific tests: register, login, /api/auth/me, and that protected routes
actually reject requests without (or with an invalid) bearer token.
"""


def test_register_creates_user_and_returns_token(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "new.doc", "full_name": "Dr. New Doc", "password": "supersecret1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_rejects_duplicate_username(client):
    payload = {"username": "dupe.doc", "full_name": "Dr. Dupe", "password": "supersecret1"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 200
    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 400


def test_login_with_seeded_demo_user_succeeds(client):
    resp = client.post(
        "/api/auth/login", data={"username": "dr.chen", "password": "demo1234"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_fails(client):
    resp = client.post(
        "/api/auth/login", data={"username": "dr.chen", "password": "wrong-password"}
    )
    assert resp.status_code == 401


def test_login_with_unknown_username_fails(client):
    resp = client.post(
        "/api/auth/login", data={"username": "nobody", "password": "whatever"}
    )
    assert resp.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_current_user_with_valid_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "dr.chen"
    assert body["full_name"] == "Dr. Sarah Chen"
    assert "hashed_password" not in body


def test_protected_route_rejects_garbage_token(client):
    resp = client.get("/api/patients", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_protected_route_accepts_freshly_registered_users_token(client):
    register_resp = client.post(
        "/api/auth/register",
        json={"username": "another.doc", "full_name": "Dr. Another", "password": "supersecret1"},
    )
    token = register_resp.json()["access_token"]
    resp = client.get("/api/patients", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
