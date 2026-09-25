import importlib

from fastapi.testclient import TestClient

from conftest import login


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_static_pages_and_404(client):
    assert "Regam" in client.get("/").text
    for page in ("compte.html", "mentions-legales.html", "cgu.html", "confidentialite.html"):
        assert client.get(f"/{page}").status_code == 200
    r = client.get("/nexiste-pas")
    assert r.status_code == 404 and "404" in r.text
    r = client.get("/api/nope")
    assert r.status_code == 404 and r.headers["content-type"].startswith("application/json")


def test_server_source_not_served(client):
    for path in ("/server.py", "/db.py", "/data/regam.db"):
        assert client.get(path).status_code == 404


def test_rate_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("REGAM_DB", str(tmp_path / "rl.db"))
    monkeypatch.setenv("REGAM_RATE_LIMIT", "2")
    monkeypatch.setenv("REGAM_DEV", "1")
    import server

    importlib.reload(server)
    c = TestClient(server.app)
    codes = [c.post("/api/auth/request", json={"email": f"u{i}@example.com"}).status_code for i in range(3)]
    assert codes == [200, 200, 429]


def test_export(client, capsys, monkeypatch):
    import runpy
    import sys

    c = client
    monkeypatch.setenv("REGAM_DEV", "1")
    login(c, "a@example.com")
    c.post("/api/auth/request", json={"email": "b@example.com", "plan": "pro"})
    monkeypatch.setattr(sys, "argv", ["server.py", "export"])
    runpy.run_module("server", run_name="__main__")
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "email,forfait,inscrit_le,compte_active,credits"
    assert out[1].startswith("a@example.com,decouverte,") and out[1].endswith(",oui,50")
    assert out[2].startswith("b@example.com,pro,") and out[2].endswith(",non,")


def test_migrates_first_version_database(tmp_path, monkeypatch):
    import sqlite3

    import db

    path = tmp_path / "v1.db"
    old = sqlite3.connect(path)
    old.executescript("""
        CREATE TABLE signups (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE,
                              plan TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE generations (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT NOT NULL, mode TEXT NOT NULL,
                                  prompt TEXT NOT NULL, url TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE INDEX generations_day ON generations (created_at);
        INSERT INTO signups (email, plan, created_at) VALUES ('a@b.co', 'pro', 't');
        INSERT INTO generations (ip, mode, prompt, url, created_at) VALUES ('1.2.3.4', 'image', 'p', 'u', 't');
    """)
    old.commit()
    old.close()

    monkeypatch.setenv("REGAM_DB", str(path))
    db.init()
    db.init()  # idempotent
    conn = db.connect()
    assert [tuple(r) for r in conn.execute("SELECT ip, url, status, cost FROM generations")] == [("1.2.3.4", "u", "done", 0)]
    conn.execute("INSERT INTO generations (ip, mode, prompt, status, created_at) VALUES ('x', 'video', 'p', 'pending', 't')")
    assert conn.execute("SELECT COUNT(*) FROM signups").fetchone()[0] == 1
