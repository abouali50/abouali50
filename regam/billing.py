"""Abonnements Stripe (appels HTTP directs, sans SDK).

Variables d'environnement :
  STRIPE_SECRET_KEY           sk_live_… / sk_test_…
  STRIPE_WEBHOOK_SECRET       whsec_… (endpoint : /api/stripe/webhook)
  STRIPE_PRICE_CREATEUR       price_… mensuel 19 €
  STRIPE_PRICE_PRO            price_… mensuel 49 €
  STRIPE_PRICE_CREATEUR_YEAR  price_… annuel (optionnel)
  STRIPE_PRICE_PRO_YEAR       price_… annuel (optionnel)

Événements Stripe à activer sur le webhook :
  invoice.paid, customer.subscription.deleted

Crédits :
  - souscription et renouvellement → crédits du forfait (×12 en annuel) ;
  - changement de forfait en cours de période → seulement la différence en
    cas de montée en gamme payée (évite de cumuler des crédits en changeant
    de forfait en boucle) ;
  - résiliation → retour au forfait Découverte, les crédits restants sont conservés.
"""

import hashlib
import hmac
import os
import time

import httpx

API = "https://api.stripe.com/v1"
MONTHLY_CREDITS = {"createur": 600, "pro": 2000}
PAID_PLANS = ("createur", "pro")


class BillingError(Exception):
    pass


def is_enabled() -> bool:
    return bool(os.environ.get("STRIPE_SECRET_KEY"))


def price_id(plan: str, yearly: bool) -> str | None:
    suffix = "_YEAR" if yearly else ""
    return os.environ.get(f"STRIPE_PRICE_{plan.upper()}{suffix}") or None


def plan_for_price(price: str | None) -> tuple[str, bool] | None:
    """price_… → (forfait, annuel ?)"""
    if not price:
        return None
    for plan in PAID_PLANS:
        for yearly in (False, True):
            if price_id(plan, yearly) == price:
                return plan, yearly
    return None


def credits_for(plan: str, yearly: bool) -> int:
    return MONTHLY_CREDITS[plan] * (12 if yearly else 1)


# ---------------------------------------------------------------- API calls

def _post(path: str, data: dict, client: httpx.Client | None = None) -> dict:
    own = client is None
    client = client or httpx.Client(timeout=20)
    try:
        res = client.post(f"{API}{path}", data=data, auth=(os.environ["STRIPE_SECRET_KEY"], ""))
    except httpx.HTTPError as exc:
        raise BillingError("Stripe ne répond pas. Réessaie dans un instant.") from exc
    finally:
        if own:
            client.close()
    if res.status_code >= 400:
        raise BillingError("Le paiement n'a pas pu être initialisé.")
    return res.json()


def create_customer(email: str, user_id: int, client: httpx.Client | None = None) -> str:
    data = _post("/customers", {"email": email, "metadata[user_id]": str(user_id)}, client)
    return data["id"]


def create_checkout(customer: str, price: str, site: str, client: httpx.Client | None = None) -> str:
    data = _post(
        "/checkout/sessions",
        {
            "mode": "subscription",
            "customer": customer,
            "line_items[0][price]": price,
            "line_items[0][quantity]": "1",
            "allow_promotion_codes": "true",
            "success_url": f"{site}/compte.html?paiement=ok",
            "cancel_url": f"{site}/compte.html?paiement=annule",
        },
        client,
    )
    return data["url"]


def create_portal(customer: str, site: str, client: httpx.Client | None = None) -> str:
    data = _post("/billing_portal/sessions", {"customer": customer, "return_url": f"{site}/compte.html"}, client)
    return data["url"]


# ---------------------------------------------------------------- webhooks

def verify_signature(payload: bytes, header: str, secret: str, tolerance: int = 300) -> bool:
    parts = [p.split("=", 1) for p in header.split(",") if "=" in p]
    timestamp = next((v for k, v in parts if k == "t"), None)
    signatures = [v for k, v in parts if k == "v1"]
    if not timestamp or not signatures or not timestamp.isdigit():
        return False
    if abs(time.time() - int(timestamp)) > tolerance:
        return False
    expected = hmac.new(secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, sig) for sig in signatures)


def invoice_price(invoice: dict) -> str | None:
    """Prix principal de la facture (ligne au montant le plus élevé).

    Gère les deux formes de l'API Stripe (`line.price.id` et, depuis 2025,
    `line.pricing.price_details.price`). Sur une facture de changement de
    forfait, la ligne négative (temps non utilisé de l'ancien forfait) est ignorée.
    """
    best, best_amount = None, None
    for line in (invoice.get("lines") or {}).get("data") or []:
        price = line.get("price")
        pid = price.get("id") if isinstance(price, dict) else None
        pid = pid or ((line.get("pricing") or {}).get("price_details") or {}).get("price")
        amount = line.get("amount") or 0
        if pid and (best_amount is None or amount > best_amount):
            best, best_amount = pid, amount
    return best
