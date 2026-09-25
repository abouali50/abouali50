import hashlib
import hmac
import json
import time

import httpx
import pytest

import billing
from conftest import login

SECRET = "whsec_test"
ENV = dict(
    REGAM_DEV="1", STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET=SECRET,
    STRIPE_PRICE_CREATEUR="price_c", STRIPE_PRICE_PRO="price_p", STRIPE_PRICE_PRO_YEAR="price_py",
    REGAM_SITE_URL="https://regam.ai",
)


def sign(payload: bytes, secret=SECRET, ts=None) -> str:
    ts = ts or int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


def send_event(c, event):
    payload = json.dumps(event).encode()
    return c.post("/api/stripe/webhook", content=payload, headers={"stripe-signature": sign(payload)})


@pytest.fixture()
def stripe(make_client, monkeypatch):
    calls = []
    monkeypatch.setattr(billing, "create_customer", lambda email, uid: calls.append(("customer", email)) or "cus_1")
    monkeypatch.setattr(billing, "create_checkout", lambda cus, price, site: calls.append(("checkout", cus, price, site)) or "https://checkout.stripe.com/s")
    monkeypatch.setattr(billing, "create_portal", lambda cus, site: "https://billing.stripe.com/p")
    c = make_client(**ENV)
    c.calls = calls
    return c


def test_signature_verification():
    body = b'{"a":1}'
    assert billing.verify_signature(body, sign(body), SECRET)
    assert not billing.verify_signature(body, sign(body, "whsec_other"), SECRET)
    assert not billing.verify_signature(body + b" ", sign(body), SECRET)
    assert not billing.verify_signature(body, sign(body, ts=int(time.time()) - 3600), SECRET)
    assert not billing.verify_signature(body, "garbage", SECRET)


def test_invoice_price_handles_old_and_new_api_shapes():
    assert billing.invoice_price({"lines": {"data": [{"price": {"id": "price_old"}}]}}) == "price_old"
    new = {"lines": {"data": [{"pricing": {"price_details": {"price": "price_new"}}}]}}
    assert billing.invoice_price(new) == "price_new"
    assert billing.invoice_price({}) is None
    proration = {"lines": {"data": [
        {"price": {"id": "price_old"}, "amount": -500},
        {"price": {"id": "price_new"}, "amount": 1200},
    ]}}
    assert billing.invoice_price(proration) == "price_new"


def test_stripe_http_calls(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    seen = []

    def handler(request):
        seen.append((str(request.url), request.headers["authorization"], request.read().decode()))
        return httpx.Response(200, json={"id": "cs_1", "url": "https://checkout.stripe.com/s"})

    c = httpx.Client(transport=httpx.MockTransport(handler))
    assert billing.create_checkout("cus_1", "price_p", "https://regam.ai", c) == "https://checkout.stripe.com/s"
    url, authz, body = seen[0]
    assert url == "https://api.stripe.com/v1/checkout/sessions"
    assert authz.startswith("Basic ")
    assert "mode=subscription" in body and "customer=cus_1" in body and "price_p" in body

    def fail(request):
        return httpx.Response(400, json={"error": {}})

    with pytest.raises(billing.BillingError):
        billing.create_customer("a@b.co", 1, httpx.Client(transport=httpx.MockTransport(fail)))


def test_billing_status(stripe, client):
    assert client.get("/api/billing").json() == {"enabled": False, "plans": []}


def test_billing_status_lists_configured_prices(stripe):
    plans = stripe.get("/api/billing").json()["plans"]
    assert {"plan": "pro", "yearly": True} in plans and {"plan": "createur", "yearly": True} not in plans


def invoice(inv_id, price, reason="subscription_create", amount_paid=1900, lines=None):
    return {"type": "invoice.paid", "data": {"object": {
        "id": inv_id, "customer": "cus_1", "billing_reason": reason, "amount_paid": amount_paid,
        "lines": {"data": lines or [{"price": {"id": price}, "amount": amount_paid}]}}}}


def test_checkout_requires_login_and_creates_customer_once(stripe):
    assert stripe.post("/api/billing/checkout", json={"plan": "pro"}).status_code == 401
    login(stripe)
    r = stripe.post("/api/billing/checkout", json={"plan": "pro"})
    assert r.json() == {"url": "https://checkout.stripe.com/s"}
    stripe.post("/api/billing/checkout", json={"plan": "createur"})
    assert [c[0] for c in stripe.calls] == ["customer", "checkout", "checkout"]
    assert stripe.calls[1] == ("checkout", "cus_1", "price_p", "https://regam.ai")
    assert stripe.get("/api/me").json()["has_billing"] is True


def test_checkout_unavailable_price(stripe):
    login(stripe)
    r = stripe.post("/api/billing/checkout", json={"plan": "createur", "yearly": True})
    assert r.status_code == 400


def test_invoice_paid_upgrades_and_credits_once(stripe):
    login(stripe)
    stripe.post("/api/billing/checkout", json={"plan": "pro"})
    event = invoice("in_1", "price_p")
    assert send_event(stripe, event).status_code == 200
    assert send_event(stripe, event).status_code == 200  # rejouée par Stripe
    me = stripe.get("/api/me").json()
    assert me["plan"] == "pro" and me["credits"] == 50 + 2000

    send_event(stripe, invoice("in_2", "price_py", reason="subscription_cycle"))
    assert stripe.get("/api/me").json()["credits"] == 50 + 2000 + 24000


def test_already_subscribed_cannot_checkout_again(stripe):
    login(stripe)
    stripe.post("/api/billing/checkout", json={"plan": "createur"})
    send_event(stripe, invoice("in_1", "price_c"))
    r = stripe.post("/api/billing/checkout", json={"plan": "pro"})
    assert r.status_code == 409 and "Gérer mon abonnement" in r.json()["detail"]


def test_plan_switches_cannot_farm_credits(stripe):
    login(stripe)
    stripe.post("/api/billing/checkout", json={"plan": "createur"})
    send_event(stripe, invoice("in_1", "price_c"))  # 50 + 600
    # Montée en gamme payée au prorata : seulement la différence (2000 - 600).
    upgrade = [
        {"price": {"id": "price_c"}, "amount": -900},
        {"pricing": {"price_details": {"price": "price_p"}}, "amount": 2400},
    ]
    send_event(stripe, invoice("in_2", None, reason="subscription_update", amount_paid=1500, lines=upgrade))
    me = stripe.get("/api/me").json()
    assert me["plan"] == "pro" and me["credits"] == 50 + 600 + 1400
    # Retour à Créateur (avoir, rien payé) : forfait mis à jour, aucun crédit.
    send_event(stripe, invoice("in_3", "price_c", reason="subscription_update", amount_paid=0))
    me = stripe.get("/api/me").json()
    assert me["plan"] == "createur" and me["credits"] == 2050


def test_subscription_deleted_downgrades(stripe):
    login(stripe)
    stripe.post("/api/billing/checkout", json={"plan": "pro"})
    send_event(stripe, invoice("in_1", "price_p"))
    send_event(stripe, {"type": "customer.subscription.deleted", "data": {"object": {"customer": "cus_1"}}})
    me = stripe.get("/api/me").json()
    assert me["plan"] == "decouverte" and me["credits"] == 2050  # les crédits achetés restent


def test_webhook_rejects_bad_signature(stripe):
    payload = b'{"type":"invoice.paid"}'
    r = stripe.post("/api/stripe/webhook", content=payload, headers={"stripe-signature": sign(payload, "whsec_bad")})
    assert r.status_code == 400


def test_webhook_unknown_customer_is_ignored(stripe):
    r = send_event(stripe, {"type": "invoice.paid", "data": {"object": {"id": "in_9", "customer": "cus_x"}}})
    assert r.status_code == 200


def test_portal(stripe):
    login(stripe)
    assert stripe.post("/api/billing/portal", json={}).status_code == 400
    stripe.post("/api/billing/checkout", json={"plan": "pro"})
    assert stripe.post("/api/billing/portal", json={}).json() == {"url": "https://billing.stripe.com/p"}
