import httpx
import pytest

import generate
from conftest import login, set_plan

IMG = {"url": "https://cdn/x.png", "width": 1, "height": 1}


# ---------------------------------------------------------------- generate.py (fal mocké)

def fal_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_build_prompt_avatar_is_fictional_and_styled():
    req = generate.GenerateIn(mode="avatar", prompt="femme, café parisien", style="cinema", morpho="athletique")
    prompt = generate.build_prompt(req)
    assert prompt.startswith("Portrait of a fictional person, athletic build")
    assert "femme, café parisien" in prompt and "cinematic" in prompt


def test_costs():
    assert generate.GenerateIn(prompt="abc", mode="image").cost == 1
    assert generate.GenerateIn(prompt="abc", mode="avatar").cost == 2
    assert generate.GenerateIn(prompt="abc", mode="video").cost == 8
    assert generate.GenerateIn(prompt="abc", mode="video", duration="10").cost == 16


def test_generate_image_calls_fal(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "k-123")
    seen = {}

    def handler(request):
        seen.update(auth=request.headers["authorization"], url=str(request.url), body=request.read())
        return httpx.Response(200, json={"images": [{"url": "https://cdn/x.png", "width": 576, "height": 1024}]})

    out = generate.generate_image(generate.GenerateIn(prompt="un chat", ratio="16:9"), fal_client(handler))
    assert out == {"url": "https://cdn/x.png", "width": 576, "height": 1024}
    assert seen["auth"] == "Key k-123"
    assert seen["url"] == "https://fal.run/fal-ai/flux/schnell"
    assert b'"landscape_16_9"' in seen["body"] and b'"enable_safety_checker":true' in seen["body"]


@pytest.mark.parametrize("response, status", [
    (httpx.Response(200, json={"images": [{"url": "u"}], "has_nsfw_concepts": [True]}), 422),
    (httpx.Response(422, json={}), 422),
    (httpx.Response(500, json={}), 502),
    (httpx.Response(200, json={"images": []}), 502),
])
def test_generate_image_errors(monkeypatch, response, status):
    monkeypatch.setenv("FAL_KEY", "k")
    with pytest.raises(generate.GenerationError) as exc:
        generate.generate_image(generate.GenerateIn(prompt="un chat"), fal_client(lambda r: response))
    assert exc.value.status == status


def test_video_submit_and_poll(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "k")
    state = {"status": "IN_PROGRESS"}

    def handler(request):
        url = str(request.url)
        if request.method == "POST":
            assert url == "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/text-to-video"
            assert b'"duration":"10"' in request.read()
            return httpx.Response(200, json={"request_id": "r1", "status_url": "https://q/s", "response_url": "https://q/r"})
        if url == "https://q/s":
            return httpx.Response(200, json={"status": state["status"]})
        return httpx.Response(200, json={"video": {"url": "https://cdn/v.mp4"}})

    c = fal_client(handler)
    job = generate.submit_video(generate.GenerateIn(prompt="un chat", mode="video", duration="10"), c)
    assert job == {"status_url": "https://q/s", "response_url": "https://q/r"}
    assert generate.poll_video(job["status_url"], job["response_url"], c) is None
    state["status"] = "COMPLETED"
    assert generate.poll_video(job["status_url"], job["response_url"], c) == "https://cdn/v.mp4"


def test_video_poll_failure_and_transient(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "k")

    def failed(request):
        if str(request.url).endswith("/s"):
            return httpx.Response(200, json={"status": "COMPLETED"})
        return httpx.Response(422, json={"detail": "nsfw"})

    with pytest.raises(generate.GenerationError):
        generate.poll_video("https://q/s", "https://q/r", fal_client(failed))

    def down(request):
        raise httpx.ConnectError("réseau")

    assert generate.poll_video("https://q/s", "https://q/r", fal_client(down)) is None


# ---------------------------------------------------------------- /api/generate

@pytest.fixture()
def live(make_client, monkeypatch):
    monkeypatch.setattr(generate, "generate_image", lambda req: IMG)
    return make_client(FAL_KEY="k", REGAM_DEV="1", REGAM_GEN_PER_IP_DAY="2")


def test_studio_disabled_without_key(client):
    assert client.get("/api/studio").json() == {"enabled": False}
    assert client.post("/api/generate", json={"prompt": "un chat"}).status_code == 503


def test_anonymous_daily_quota(live):
    s = live.get("/api/studio").json()
    assert s["enabled"] and s["remaining"] == 2 and s["user"] is None
    assert live.post("/api/generate", json={"prompt": "une image"}).json()["remaining"] == 1
    assert live.post("/api/generate", json={"prompt": "une image"}).json()["remaining"] == 0
    r = live.post("/api/generate", json={"prompt": "encore"})
    assert r.status_code == 429 and "compte" in r.json()["detail"]


def test_anonymous_global_cap(make_client, monkeypatch):
    c = make_client(FAL_KEY="k", REGAM_GEN_DAILY_CAP="1")
    monkeypatch.setattr(generate, "generate_image", lambda req: IMG)
    assert c.post("/api/generate", json={"prompt": "une image"}).status_code == 200
    assert c.post("/api/generate", json={"prompt": "une autre"}).status_code == 503


def test_logged_in_user_spends_credits_not_quota(live):
    login(live)
    for _ in range(3):  # au-delà du quota visiteur (2)
        r = live.post("/api/generate", json={"prompt": "un avatar", "mode": "avatar"})
        assert r.status_code == 200
    assert r.json()["credits"] == 50 - 3 * 2
    history = live.get("/api/me/generations").json()
    assert len(history) == 3 and history[0]["url"] == IMG["url"] and history[0]["cost"] == 2


def test_insufficient_credits(live):
    login(live)
    set_plan("lea@example.com", "decouverte", credits=1)
    r = live.post("/api/generate", json={"prompt": "un avatar", "mode": "avatar"})
    assert r.status_code == 402
    assert live.get("/api/me").json()["credits"] == 1
    assert live.get("/api/me/generations").json() == []


def test_failed_generation_is_refunded(live, monkeypatch):
    login(live)

    def fail(req):
        raise generate.GenerationError("Contenu refusé par le filtre de sécurité.", 422)

    monkeypatch.setattr(generate, "generate_image", fail)
    r = live.post("/api/generate", json={"prompt": "xxx"})
    assert r.status_code == 422 and "refusé" in r.json()["detail"]
    assert live.get("/api/me").json()["credits"] == 50


def test_failed_anonymous_generation_does_not_use_quota(live, monkeypatch):
    def fail(req):
        raise generate.GenerationError("boom")

    monkeypatch.setattr(generate, "generate_image", fail)
    live.post("/api/generate", json={"prompt": "xxx"})
    assert live.get("/api/studio").json()["remaining"] == 2


@pytest.mark.parametrize("body", [
    {"prompt": "ab"},
    {"prompt": "x" * 801},
    {"prompt": "ok ok", "mode": "gif"},
    {"prompt": "ok ok", "ratio": "4:3"},
    {"prompt": "ok ok", "duration": "7"},
])
def test_generate_validation(live, body):
    assert live.post("/api/generate", json=body).status_code == 422


# ---------------------------------------------------------------- vidéo

def test_video_access_rules(live):
    body = {"prompt": "une vidéo", "mode": "video"}
    assert live.post("/api/generate", json=body).status_code == 401
    login(live)
    r = live.post("/api/generate", json=body)
    assert r.status_code == 403 and "Créateur" in r.json()["detail"]
    set_plan("lea@example.com", "createur")
    r = live.post("/api/generate", json={**body, "duration": "10"})
    assert r.status_code == 403 and "Pro" in r.json()["detail"]


def test_video_job_lifecycle(live, monkeypatch):
    login(live)
    set_plan("lea@example.com", "pro", credits=100)
    monkeypatch.setattr(generate, "submit_video", lambda req, image_url=None: {"status_url": "s", "response_url": "r"})
    polls = iter([None, "https://cdn/v.mp4"])
    monkeypatch.setattr(generate, "poll_video", lambda s, r: next(polls))

    r = live.post("/api/generate", json={"prompt": "une vidéo", "mode": "video", "duration": "10"})
    assert r.status_code == 200
    job = r.json()
    assert job["status"] == "pending" and job["credits"] == 84

    assert live.get(f"/api/jobs/{job['id']}").json()["status"] == "pending"
    done = live.get(f"/api/jobs/{job['id']}").json()
    assert done == {"id": job["id"], "status": "done", "url": "https://cdn/v.mp4", "error": None, "credits": 84}
    # Terminé : plus d'appel à fal.
    assert live.get(f"/api/jobs/{job['id']}").json()["status"] == "done"


def test_failed_video_is_refunded_once(live, monkeypatch):
    login(live)
    set_plan("lea@example.com", "createur", credits=20)
    monkeypatch.setattr(generate, "submit_video", lambda req, image_url=None: {"status_url": "s", "response_url": "r"})

    def fail(s, r):
        raise generate.GenerationError("La vidéo a échoué.")

    monkeypatch.setattr(generate, "poll_video", fail)
    job = live.post("/api/generate", json={"prompt": "une vidéo", "mode": "video"}).json()
    assert job["credits"] == 12
    r = live.get(f"/api/jobs/{job['id']}").json()
    assert r["status"] == "failed" and "remboursés" in r["error"] and r["credits"] == 20
    assert live.get(f"/api/jobs/{job['id']}").json()["credits"] == 20


def test_jobs_are_private(live, monkeypatch):
    login(live, "a@example.com")
    set_plan("a@example.com", "pro")
    monkeypatch.setattr(generate, "submit_video", lambda req, image_url=None: {"status_url": "s", "response_url": "r"})
    job = live.post("/api/generate", json={"prompt": "une vidéo", "mode": "video"}).json()
    live.post("/api/auth/logout", json={})
    login(live, "b@example.com")
    assert live.get(f"/api/jobs/{job['id']}").status_code == 404


# ---------------------------------------------------------------- image → vidéo

def test_i2v_submit_uses_image_model_and_motion_prompt(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "k")
    seen = {}

    def handler(request):
        seen.update(url=str(request.url), body=request.read())
        return httpx.Response(200, json={"status_url": "s", "response_url": "r"})

    req = generate.GenerateIn(prompt="elle sourit et tourne la tête", mode="video", source_id=3)
    generate.submit_video(req, fal_client(handler), image_url="https://cdn/a.png")
    assert seen["url"] == "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video"
    body = seen["body"].decode()
    assert '"image_url":"https://cdn/a.png"' in body and "aspect_ratio" not in body
    assert "elle sourit" in body and "Portrait of a fictional" not in body


def test_animate_own_image(live, monkeypatch):
    login(live)
    set_plan("lea@example.com", "createur", credits=100)
    submitted = {}
    monkeypatch.setattr(generate, "submit_video", lambda req, image_url=None: submitted.update(url=image_url) or {"status_url": "s", "response_url": "r"})
    img = live.post("/api/generate", json={"prompt": "un avatar", "mode": "avatar"}).json()
    r = live.post("/api/generate", json={"prompt": "elle sourit", "mode": "video", "source_id": img["id"]})
    assert r.status_code == 200 and r.json()["status"] == "pending"
    assert submitted["url"] == IMG["url"]


def test_cannot_animate_someone_elses_image_or_a_video(live, monkeypatch):
    monkeypatch.setattr(generate, "submit_video", lambda req, image_url=None: {"status_url": "s", "response_url": "r"})
    login(live, "a@example.com")
    set_plan("a@example.com", "pro", credits=100)
    img = live.post("/api/generate", json={"prompt": "une image"}).json()
    vid = live.post("/api/generate", json={"prompt": "une vidéo", "mode": "video"}).json()
    r = live.post("/api/generate", json={"prompt": "anime", "mode": "video", "source_id": vid["id"]})
    assert r.status_code == 404
    live.post("/api/auth/logout", json={})

    login(live, "b@example.com")
    set_plan("b@example.com", "pro", credits=100)
    r = live.post("/api/generate", json={"prompt": "anime", "mode": "video", "source_id": img["id"]})
    assert r.status_code == 404
    assert live.get("/api/me").json()["credits"] == 100  # rien débité


def test_source_id_only_for_video(live):
    login(live)
    r = live.post("/api/generate", json={"prompt": "une image", "source_id": 1})
    assert r.status_code == 422
