import pytest

import generate
from conftest import login, set_plan

IMG = {"url": "https://cdn/x.png", "width": 1, "height": 1}


@pytest.fixture()
def adm(make_client, monkeypatch):
    monkeypatch.setattr(generate, "generate_image", lambda req: IMG)
    monkeypatch.setattr(generate, "submit_video", lambda req, image_url=None: {"status_url": "s", "response_url": "r"})
    return make_client(REGAM_DEV="1", FAL_KEY="k", REGAM_ADMIN_EMAILS="boss@regam.ai, Other@Regam.ai")


def test_admin_requires_admin_email(adm):
    assert adm.get("/api/admin/stats").status_code == 401
    login(adm, "lea@example.com")
    assert adm.get("/api/admin/stats").status_code == 403
    assert adm.post("/api/admin/credits", json={"email": "lea@example.com", "amount": 999}).status_code == 403
    assert adm.get("/api/me").json()["credits"] == 50


def test_admin_emails_are_case_insensitive(adm):
    login(adm, "other@regam.ai")
    assert adm.get("/api/admin/stats").status_code == 200


def test_stats(adm):
    adm.post("/api/generate", json={"prompt": "anonyme"})  # essai visiteur
    login(adm, "lea@example.com")
    set_plan("lea@example.com", "pro", credits=100)
    adm.post("/api/generate", json={"prompt": "un avatar", "mode": "avatar"})
    adm.post("/api/generate", json={"prompt": "une vidéo", "mode": "video", "duration": "10"})
    adm.post("/api/auth/logout", json={})
    adm.post("/api/auth/request", json={"email": "waiting@example.com"})  # jamais activé
    login(adm, "boss@regam.ai")

    s = adm.get("/api/admin/stats").json()
    assert s["users"]["total"] == 2 and s["users"]["new_7d"] == 2 and s["users"]["waitlist"] == 1
    assert s["users"]["by_plan"] == {"decouverte": 1, "createur": 0, "pro": 1}
    assert s["mrr_eur"] == 49
    g = s["generations_30d"]
    assert (g["image"], g["avatar"], g["video"], g["anonymous"], g["video_10s"]) == (1, 1, 1, 1, 1)
    assert s["ai_cost_usd_30d"] == round(2 * 0.003 + 0.60, 2)
    assert s["credits_30d"] == {"granted": 100, "spent": 18}
    assert len(s["daily"]) == 30 and s["daily"][-1]["generations"] == 3 and s["daily"][-1]["new_users"] == 2
    assert s["recent_users"][0]["email"] == "boss@regam.ai"
    assert s["recent_users"][1]["generations"] == 1  # la vidéo est encore en cours


def test_grant_and_remove_credits(adm):
    login(adm, "lea@example.com")
    adm.post("/api/auth/logout", json={})
    login(adm, "boss@regam.ai")
    r = adm.post("/api/admin/credits", json={"email": "LEA@example.com", "amount": 25, "note": "geste commercial"})
    assert r.json() == {"email": "lea@example.com", "credits": 75}
    assert adm.post("/api/admin/credits", json={"email": "lea@example.com", "amount": -75}).json()["credits"] == 0
    assert adm.post("/api/admin/credits", json={"email": "lea@example.com", "amount": -1}).status_code == 400
    assert adm.post("/api/admin/credits", json={"email": "lea@example.com", "amount": 0}).status_code == 422
    assert adm.post("/api/admin/credits", json={"email": "nobody@example.com", "amount": 5}).status_code == 404


def test_admin_page_is_served(adm):
    assert adm.get("/admin.html").status_code == 200
