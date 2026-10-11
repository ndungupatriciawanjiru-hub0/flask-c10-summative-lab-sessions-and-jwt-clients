from conftest import signup


def test_signup_creates_user_and_logs_in(client):
    res = signup(client)
    assert res.status_code == 201
    assert res.get_json() == {"id": 1, "username": "alice"}
    assert client.get("/check_session").status_code == 200


def test_signup_never_returns_password(client):
    body = signup(client).get_json()
    assert "password" not in str(body).lower()


def test_signup_duplicate_username(client):
    signup(client)
    assert signup(client).status_code == 422


def test_signup_password_mismatch(client):
    res = client.post(
        "/signup",
        json={"username": "bob", "password": "secret123",
              "password_confirmation": "different"},
    )
    assert res.status_code == 422


def test_login_success_and_failure(client):
    signup(client)
    client.delete("/logout")
    bad = client.post("/login", json={"username": "alice", "password": "nope"})
    assert bad.status_code == 401
    ok = client.post("/login", json={"username": "alice", "password": "secret123"})
    assert ok.status_code == 200


def test_check_session_requires_login(client):
    assert client.get("/check_session").status_code == 401


def test_logout_clears_session(client):
    signup(client)
    assert client.delete("/logout").status_code == 204
    assert client.get("/check_session").status_code == 401
