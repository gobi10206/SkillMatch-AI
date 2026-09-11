"""Tests for registration, login, and JWT-protected access."""


def test_register_creates_user_and_profile(client):
    resp = client.post("/auth/register", json={
        "email": "seeker@example.com", "password": "password123",
        "full_name": "Test Seeker", "role": "job_seeker",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "seeker@example.com"
    assert body["role"] == "job_seeker"


def test_duplicate_registration_rejected(client):
    payload = {"email": "dupe@example.com", "password": "password123", "full_name": "Dupe", "role": "job_seeker"}
    assert client.post("/auth/register", json=payload).status_code == 201
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_and_access_protected_route(client):
    client.post("/auth/register", json={
        "email": "login@example.com", "password": "password123",
        "full_name": "Login Test", "role": "job_seeker",
    })
    login_resp = client.post("/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "login@example.com"


def test_wrong_password_rejected(client):
    client.post("/auth/register", json={
        "email": "wrongpw@example.com", "password": "password123",
        "full_name": "WrongPW", "role": "job_seeker",
    })
    resp = client.post("/auth/login", json={"email": "wrongpw@example.com", "password": "nope"})
    assert resp.status_code == 401


def test_protected_route_without_token_rejected(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
