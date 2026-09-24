import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def make_client(tmp_path, monkeypatch):
    def _make(**env):
        monkeypatch.setenv("REGAM_DB", str(tmp_path / "test.db"))
        monkeypatch.setenv("REGAM_RATE_LIMIT", "100")
        for var in ("SMTP_HOST", "FAL_KEY"):
            monkeypatch.delenv(var, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        import server

        importlib.reload(server)
        return TestClient(server.app)

    return _make


@pytest.fixture()
def client(make_client):
    return make_client()
