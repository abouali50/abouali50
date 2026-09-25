import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ENV_VARS = (
    "SMTP_HOST", "FAL_KEY", "REGAM_DEV", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PRICE_CREATEUR", "STRIPE_PRICE_PRO", "STRIPE_PRICE_CREATEUR_YEAR", "STRIPE_PRICE_PRO_YEAR",
    "REGAM_SITE_URL",
)


@pytest.fixture()
def make_client(tmp_path, monkeypatch):
    def _make(**env):
        monkeypatch.setenv("REGAM_DB", str(tmp_path / "test.db"))
        monkeypatch.setenv("REGAM_RATE_LIMIT", "100")
        for var in ENV_VARS:
            monkeypatch.delenv(var, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        import server

        importlib.reload(server)
        return TestClient(server.app, base_url="https://testserver")

    return _make


@pytest.fixture()
def client(make_client):
    return make_client()


def login(client, email="lea@example.com"):
    """Connexion complète en mode dev ; renvoie l'utilisateur."""
    r = client.post("/api/auth/request", json={"email": email})
    assert r.status_code == 200, r.text
    token = r.json()["dev_link"].split("#token=")[1]
    r = client.post("/api/auth/verify", json={"token": token})
    assert r.status_code == 200, r.text
    return r.json()["user"]


def set_plan(email, plan, credits=None):
    from contextlib import closing

    import db

    with closing(db.connect()) as conn, conn:
        conn.execute("UPDATE users SET plan = ? WHERE email = ?", (plan, email))
        if credits is not None:
            conn.execute("UPDATE users SET credits = ? WHERE email = ?", (credits, email))
