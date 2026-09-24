import importlib

import pytest
from fastapi.testclient import TestClient


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_signup_then_duplicate_is_case_insensitive(client):
    r = client.post("/api/signup", json={"email": "Lea@Example.com", "plan": "pro"})
    assert r.status_code == 201
    assert r.json() == {"ok": True, "already": False}

    r = client.post("/api/signup", json={"email": "lea@example.com"})
    assert r.status_code == 200
    assert r.json()["already"] is True


@pytest.mark.parametrize("body", [
    {"email": "pas-un-email"},
    {"email": "a@b.co", "plan": "inconnu"},
    {},
])
def test_signup_rejects_invalid_input(client, body):
    assert client.post("/api/signup", json=body).status_code == 422


def test_honeypot_is_accepted_but_not_stored(client):
    r = client.post("/api/signup", json={"email": "bot@example.com", "website": "spam"})
    assert r.status_code == 201
    # Not stored: a real signup with the same address is new.
    r = client.post("/api/signup", json={"email": "bot@example.com"})
    assert r.json()["already"] is False


def test_rate_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("REGAM_DB", str(tmp_path / "rl.db"))
    monkeypatch.setenv("REGAM_RATE_LIMIT", "2")
    import server

    importlib.reload(server)
    c = TestClient(server.app)
    codes = [c.post("/api/signup", json={"email": f"u{i}@example.com"}).status_code for i in range(3)]
    assert codes == [201, 201, 429]


def test_static_pages_and_404(client):
    assert "Regam" in client.get("/").text
    for page in ("mentions-legales.html", "cgu.html", "confidentialite.html"):
        assert client.get(f"/{page}").status_code == 200
    r = client.get("/nexiste-pas")
    assert r.status_code == 404
    assert "404" in r.text
    assert client.get("/api/nope").status_code == 404
    assert client.get("/api/nope").headers["content-type"].startswith("application/json")


def test_server_source_not_served(client):
    assert client.get("/server.py").status_code == 404
