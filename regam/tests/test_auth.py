import pytest

import mailer
from conftest import login


@pytest.fixture()
def dev(make_client):
    return make_client(REGAM_DEV="1")


def test_login_is_unavailable_without_smtp_outside_dev(client):
    r = client.post("/api/auth/request", json={"email": "a@example.com"})
    assert r.status_code == 503


def test_full_login_flow_gives_welcome_credits(dev):
    assert dev.get("/api/me").status_code == 401
    user = login(dev, "Lea@Example.com")
    assert user == {"email": "lea@example.com", "plan": "decouverte", "credits": 50, "has_billing": False}
    assert dev.get("/api/me").json()["credits"] == 50
    # Deuxième connexion : pas de nouveaux crédits.
    dev.post("/api/auth/logout", json={})
    assert dev.get("/api/me").status_code == 401
    assert login(dev, "lea@example.com")["credits"] == 50


def test_token_is_single_use(dev):
    link = dev.post("/api/auth/request", json={"email": "a@example.com"}).json()["dev_link"]
    token = link.split("#token=")[1]
    assert "/compte.html#token=" in link
    assert dev.post("/api/auth/verify", json={"token": token}).status_code == 200
    assert dev.post("/api/auth/verify", json={"token": token}).status_code == 400


def test_bad_token(dev):
    assert dev.post("/api/auth/verify", json={"token": "x" * 40}).status_code == 400


def test_next_path_is_kept_but_only_if_relative(dev):
    for nxt, expected in (("/#studio", "/#studio"), ("https://evil.com", None), ("//evil.com", None)):
        link = dev.post("/api/auth/request", json={"email": "a@example.com", "next": nxt}).json()["dev_link"]
        r = dev.post("/api/auth/verify", json={"token": link.split("#token=")[1]})
        assert r.json()["next"] == expected


def test_session_cookie_flags(dev):
    link = dev.post("/api/auth/request", json={"email": "a@example.com"}).json()["dev_link"]
    r = dev.post("/api/auth/verify", json={"token": link.split("#token=")[1]})
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_post_requires_json_content_type(dev):
    login(dev)
    r = dev.post("/api/auth/logout", content="{}", headers={"content-type": "text/plain"})
    assert r.status_code == 415


def test_honeypot(dev):
    r = dev.post("/api/auth/request", json={"email": "bot@example.com", "website": "spam"})
    assert r.json() == {"ok": True}


@pytest.mark.parametrize("body", [{"email": "pas-un-email"}, {"email": "a@b.co", "plan": "inconnu"}, {}])
def test_request_validation(dev, body):
    assert dev.post("/api/auth/request", json=body).status_code == 422


def test_login_email_sent_via_smtp(make_client, monkeypatch):
    c = make_client(SMTP_HOST="smtp.example.com", REGAM_SITE_URL="https://regam.ai")
    sent = []
    monkeypatch.setattr(mailer, "send", lambda msg: sent.append(msg) or True)
    r = c.post("/api/auth/request", json={"email": "new@example.com"})
    assert r.json() == {"ok": True}  # pas de lien dans la réponse hors mode dev
    assert "Bienvenue" in sent[0]["Subject"]
    assert "https://regam.ai/compte.html#token=" in sent[0].get_body(("plain",)).get_content()


def test_smtp_failure_is_reported(make_client, monkeypatch):
    c = make_client(SMTP_HOST="smtp.example.com")
    monkeypatch.setattr(mailer, "send", lambda msg: False)
    assert c.post("/api/auth/request", json={"email": "a@example.com"}).status_code == 502


def test_mailer_send_never_raises(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.invalid")

    def boom(*a, **k):
        raise OSError("connexion refusée")

    monkeypatch.setattr(mailer.smtplib, "SMTP", boom)
    assert mailer.send(mailer.build_login("a@example.com", "https://x/#token=t", True)) is False


def test_session_cookie_is_secure_on_https_site(make_client):
    c = make_client(REGAM_DEV="1", REGAM_SITE_URL="https://regam.ai")
    link = c.post("/api/auth/request", json={"email": "a@example.com"}).json()["dev_link"]
    r = c.post("/api/auth/verify", json={"token": link.split("#token=")[1]})
    assert "secure" in r.headers["set-cookie"].lower()
