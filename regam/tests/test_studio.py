import httpx
import pytest

import generate
import mailer


# ---------------------------------------------------------------- e-mail

def test_welcome_email_content():
    msg = mailer.build_welcome("lea@example.com", "pro")
    assert msg["To"] == "lea@example.com"
    text = msg.get_body(("plain",)).get_content()
    html = msg.get_body(("html",)).get_content()
    assert "Pro" in text and "50 crédits" in text
    assert "Tester le studio" in html


def test_send_welcome_is_noop_without_smtp(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.setattr(mailer.smtplib, "SMTP", lambda *a, **k: pytest.fail("SMTP must not be used"))
    mailer.send_welcome("a@example.com", "decouverte")


def test_send_welcome_never_raises(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.invalid")

    def boom(*a, **k):
        raise OSError("connexion refusée")

    monkeypatch.setattr(mailer.smtplib, "SMTP", boom)
    mailer.send_welcome("a@example.com", "decouverte")  # ne lève pas


def test_signup_sends_welcome_once(client, monkeypatch):
    sent = []
    monkeypatch.setattr(mailer, "send_welcome", lambda to, plan: sent.append((to, plan)))
    client.post("/api/signup", json={"email": "Lea@Example.com", "plan": "pro"})
    client.post("/api/signup", json={"email": "lea@example.com"})
    client.post("/api/signup", json={"email": "bot@example.com", "website": "x"})
    assert sent == [("lea@example.com", "pro")]


# ---------------------------------------------------------------- génération

def test_build_prompt_avatar_is_fictional_and_styled():
    req = generate.GenerateIn(mode="avatar", prompt="femme, café parisien", style="cinema", morpho="athletique")
    prompt = generate.build_prompt(req)
    assert prompt.startswith("Portrait of a fictional person, athletic build")
    assert "femme, café parisien" in prompt and "cinematic" in prompt


def fal_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_generate_image_calls_fal(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "k-123")
    seen = {}

    def handler(request):
        seen["auth"] = request.headers["authorization"]
        seen["url"] = str(request.url)
        seen["body"] = request.read()
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


def test_studio_disabled_without_key(client):
    assert client.get("/api/studio").json() == {"enabled": False}
    assert client.post("/api/generate", json={"prompt": "un chat"}).status_code == 503


def test_generate_endpoint_and_daily_quota(make_client, monkeypatch):
    c = make_client(FAL_KEY="k", REGAM_GEN_PER_IP_DAY="2")
    monkeypatch.setattr(generate, "generate_image", lambda req: {"url": f"https://cdn/{req.mode}.png", "width": 1, "height": 1})

    assert c.get("/api/studio").json() == {"enabled": True, "modes": ["avatar", "image"], "remaining": 2}
    r = c.post("/api/generate", json={"mode": "avatar", "prompt": "un avatar"})
    assert r.status_code == 200 and r.json()["url"] == "https://cdn/avatar.png" and r.json()["remaining"] == 1
    assert c.post("/api/generate", json={"prompt": "une image"}).json()["remaining"] == 0
    r = c.post("/api/generate", json={"prompt": "encore"})
    assert r.status_code == 429 and "demain" in r.json()["detail"]


def test_generate_global_cap(make_client, monkeypatch):
    c = make_client(FAL_KEY="k", REGAM_GEN_DAILY_CAP="1")
    monkeypatch.setattr(generate, "generate_image", lambda req: {"url": "u", "width": 1, "height": 1})
    assert c.post("/api/generate", json={"prompt": "une image"}).status_code == 200
    assert c.post("/api/generate", json={"prompt": "une autre"}).status_code == 503


def test_generate_error_is_forwarded(make_client, monkeypatch):
    c = make_client(FAL_KEY="k")

    def fail(req):
        raise generate.GenerationError("Contenu refusé par le filtre de sécurité.", 422)

    monkeypatch.setattr(generate, "generate_image", fail)
    r = c.post("/api/generate", json={"prompt": "xxx"})
    assert r.status_code == 422 and "refusé" in r.json()["detail"]
    # Un échec ne consomme pas le quota.
    assert c.get("/api/studio").json()["remaining"] == 5


@pytest.mark.parametrize("body", [
    {"prompt": "ab"},
    {"prompt": "x" * 801},
    {"prompt": "ok ok", "mode": "video"},
    {"prompt": "ok ok", "ratio": "4:3"},
])
def test_generate_validation(make_client, body):
    c = make_client(FAL_KEY="k")
    assert c.post("/api/generate", json=body).status_code == 422
