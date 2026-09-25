"""Regam — serveur du site.

Sert le site statique de `public/` et expose l'API :
  - comptes par lien magique (auth.py) et e-mails (mailer.py)
  - crédits (db.py) et abonnements Stripe (billing.py)
  - génération d'images et de vidéos IA (generate.py)

Lancement :  uvicorn server:app --reload --port 8080
Export CSV : python server.py export > inscriptions.csv
"""

import json
import logging
import os
import time
from collections import defaultdict, deque
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

import auth
import billing
import db
import generate
import mailer

log = logging.getLogger("regam")

PUBLIC_DIR = Path(__file__).parent / "public"
RATE_LIMIT = int(os.environ.get("REGAM_RATE_LIMIT", "5"))  # requêtes / minute / clé
RATE_WINDOW_S = 60
VIDEO_TIMEOUT = timedelta(minutes=30)

Plan = Literal["decouverte", "createur", "pro"]


# ---------------------------------------------------------------- helpers

def client_ip(request: Request) -> str:
    # Derrière un proxy, lancer uvicorn avec --proxy-headers (voir README).
    return request.client.host if request.client else "unknown"


_hits: dict[str, deque] = defaultdict(deque)


def rate_limited(key: str) -> bool:
    now = time.monotonic()
    hits = _hits[key]
    while hits and now - hits[0] > RATE_WINDOW_S:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        return True
    hits.append(now)
    return False


def dev_mode() -> bool:
    return os.environ.get("REGAM_DEV") == "1"


def user_json(user) -> dict:
    return {
        "email": user["email"],
        "plan": user["plan"],
        "credits": user["credits"],
        "has_billing": bool(user["stripe_customer_id"]),
    }


# ---------------------------------------------------------------- app

app = FastAPI(title="Regam", docs_url=None, redoc_url=None)
db.init()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------- comptes

class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=254)
    plan: Plan = "decouverte"
    next: str | None = Field(default=None, max_length=200)
    website: str = ""  # pot de miel : doit rester vide


class VerifyRequest(BaseModel):
    token: str = Field(min_length=20, max_length=100)


@app.post("/api/auth/request", dependencies=[Depends(auth.require_json)])
def auth_request(payload: LoginRequest, request: Request) -> dict:
    email = payload.email.lower()
    if rate_limited(f"auth:{client_ip(request)}") or rate_limited(f"auth:{email}"):
        raise HTTPException(status_code=429, detail="Trop de tentatives. Réessaie dans une minute.")
    # Un robot a rempli le champ caché : on répond comme si tout allait bien.
    if payload.website:
        return {"ok": True}
    if not mailer.is_configured() and not dev_mode():
        raise HTTPException(status_code=503, detail="La connexion ouvre très bientôt. Écris-nous à contact@regam.ai.")

    with closing(db.connect()) as conn, conn:
        conn.execute(
            "INSERT OR IGNORE INTO signups (email, plan, created_at) VALUES (?, ?, ?)",
            (email, payload.plan, db.now()),
        )
        is_new = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone() is None
        token = auth.create_login_token(conn, email, payload.next)

    link = auth.login_link(token)
    if mailer.is_configured():
        if not mailer.send(mailer.build_login(email, link, is_new)):
            raise HTTPException(status_code=502, detail="L'e-mail n'a pas pu être envoyé. Réessaie.")
        return {"ok": True}
    log.warning("REGAM_DEV : lien de connexion pour %s → %s", email, link)
    return {"ok": True, "dev_link": link}


@app.post("/api/auth/verify", dependencies=[Depends(auth.require_json)])
def auth_verify(payload: VerifyRequest, response: Response) -> dict:
    with closing(db.connect()) as conn, conn:
        row = auth.consume_login_token(conn, payload.token)
        if not row:
            raise HTTPException(status_code=400, detail="Ce lien a expiré ou a déjà été utilisé. Demande-en un nouveau.")
        user, _ = db.get_or_create_user(conn, row["email"])
        session = auth.create_session(conn, user["id"])
    auth.set_session_cookie(response, session)
    return {"ok": True, "next": row["next"], "user": user_json(user)}


@app.post("/api/auth/logout", dependencies=[Depends(auth.require_json)])
def auth_logout(request: Request, response: Response) -> dict:
    auth.end_session(request, response)
    return {"ok": True}


@app.get("/api/me")
def me(user=Depends(auth.require_user)) -> dict:
    return user_json(user)


@app.get("/api/me/generations")
def my_generations(user=Depends(auth.require_user)) -> list[dict]:
    with closing(db.connect()) as conn:
        rows = conn.execute(
            """SELECT id, mode, prompt, url, status, cost, created_at FROM generations
               WHERE user_id = ? ORDER BY id DESC LIMIT 60""",
            (user["id"],),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- studio IA

def today_start() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


def anonymous_usage_today(ip: str) -> tuple[int, int]:
    """(essais gratuits de cette IP aujourd'hui, essais gratuits totaux aujourd'hui)"""
    with closing(db.connect()) as conn:
        mine, total = conn.execute(
            """SELECT COALESCE(SUM(ip = ?), 0), COUNT(*) FROM generations
               WHERE user_id IS NULL AND status != 'failed' AND created_at >= ?""",
            (ip, today_start()),
        ).fetchone()
    return mine, total


@app.get("/api/studio")
def studio_status(request: Request) -> dict:
    if not generate.is_enabled():
        return {"enabled": False}
    user = auth.current_user(request)
    mine, _ = anonymous_usage_today(client_ip(request))
    return {
        "enabled": True,
        "costs": generate.COSTS,
        "remaining": max(0, generate.per_ip_limit() - mine),
        "user": user_json(user) if user else None,
    }


def refund(conn, user_id: int, gen_id: int, amount: int) -> None:
    db.add_credits(conn, user_id, amount, "refund", ref=f"refund:{gen_id}")


def check_video_access(user, req: generate.GenerateIn) -> None:
    if user is None:
        raise HTTPException(status_code=401, detail="Connecte-toi pour créer des vidéos.")
    if user["plan"] == "decouverte":
        raise HTTPException(status_code=403, detail="La vidéo est incluse dès le forfait Créateur.")
    if req.duration == "10" and user["plan"] != "pro":
        raise HTTPException(status_code=403, detail="Les vidéos de 10 s sont incluses dans le forfait Pro.")


@app.post("/api/generate")
def generate_endpoint(payload: generate.GenerateIn, request: Request) -> dict:
    if not generate.is_enabled():
        raise HTTPException(status_code=503, detail="Le studio est en mode démo.")
    ip = client_ip(request)
    if rate_limited(f"gen:{ip}"):
        raise HTTPException(status_code=429, detail="Trop de tentatives. Patiente une minute.")
    user = auth.current_user(request)
    if payload.mode == "video":
        check_video_access(user, payload)

    # --- réserve : crédits (compte) ou essai gratuit (visiteur)
    cost = payload.cost if user else 0
    with closing(db.connect()) as conn, conn:
        if not user:
            mine, total = anonymous_usage_today(ip)
            if mine >= generate.per_ip_limit():
                raise HTTPException(status_code=429, detail="Tu as utilisé tes essais gratuits du jour. Crée un compte pour recevoir 50 crédits !")
            if total >= generate.daily_cap():
                raise HTTPException(status_code=503, detail="Le studio est très demandé aujourd'hui. Crée un compte pour continuer !")
        cur = conn.execute(
            "INSERT INTO generations (ip, user_id, mode, prompt, status, cost, created_at) VALUES (?, ?, ?, ?, 'pending', ?, ?)",
            (ip, user["id"] if user else None, payload.mode, payload.prompt, cost, db.now()),
        )
        gen_id = cur.lastrowid
        if user and not db.spend_credits(conn, user["id"], cost, payload.mode, ref=f"gen:{gen_id}"):
            conn.execute("DELETE FROM generations WHERE id = ?", (gen_id,))
            raise HTTPException(status_code=402, detail="Crédits insuffisants. Recharge ton compte pour continuer.")

    # --- appel au modèle (hors transaction : peut prendre du temps)
    try:
        if payload.mode == "video":
            job = generate.submit_video(payload)
        else:
            image = generate.generate_image(payload)
    except generate.GenerationError as exc:
        with closing(db.connect()) as conn, conn:
            conn.execute("UPDATE generations SET status = 'failed' WHERE id = ?", (gen_id,))
            if user:
                refund(conn, user["id"], gen_id, cost)
        raise HTTPException(status_code=exc.status, detail=str(exc)) from exc

    with closing(db.connect()) as conn, conn:
        if payload.mode == "video":
            conn.execute(
                "UPDATE generations SET status_url = ?, result_url = ? WHERE id = ?",
                (job["status_url"], job["response_url"], gen_id),
            )
        else:
            conn.execute("UPDATE generations SET status = 'done', url = ? WHERE id = ?", (image["url"], gen_id))
        credits = db.get_user(conn, user["id"])["credits"] if user else None

    result = {"id": gen_id, "status": "pending" if payload.mode == "video" else "done", "credits": credits}
    if payload.mode != "video":
        result.update(image)
    if not user:
        mine, _ = anonymous_usage_today(ip)
        result["remaining"] = max(0, generate.per_ip_limit() - mine)
    return result


@app.get("/api/jobs/{gen_id}")
def job_status(gen_id: int, user=Depends(auth.require_user)) -> dict:
    with closing(db.connect()) as conn:
        gen = conn.execute("SELECT * FROM generations WHERE id = ? AND user_id = ?", (gen_id, user["id"])).fetchone()
    if not gen:
        raise HTTPException(status_code=404, detail="Génération introuvable.")
    if gen["status"] != "pending" or not gen["status_url"]:
        return {"id": gen_id, "status": gen["status"], "url": gen["url"], "error": None, "credits": user["credits"]}

    url = error = None
    if datetime.fromisoformat(gen["created_at"]) < datetime.now(timezone.utc) - VIDEO_TIMEOUT:
        error = "La vidéo a pris trop de temps. Tes crédits ont été remboursés."
    else:
        try:
            url = generate.poll_video(gen["status_url"], gen["result_url"])
        except generate.GenerationError as exc:
            error = f"{exc} Tes crédits ont été remboursés."

    with closing(db.connect()) as conn, conn:
        if url:
            conn.execute("UPDATE generations SET status = 'done', url = ? WHERE id = ? AND status = 'pending'", (url, gen_id))
        elif error:
            cur = conn.execute("UPDATE generations SET status = 'failed' WHERE id = ? AND status = 'pending'", (gen_id,))
            if cur.rowcount:
                refund(conn, user["id"], gen_id, gen["cost"])
        gen = conn.execute("SELECT * FROM generations WHERE id = ?", (gen_id,)).fetchone()
        credits = db.get_user(conn, user["id"])["credits"]
    return {"id": gen_id, "status": gen["status"], "url": gen["url"], "error": error, "credits": credits}


# ---------------------------------------------------------------- abonnements

class CheckoutRequest(BaseModel):
    plan: Literal["createur", "pro"]
    yearly: bool = False


@app.get("/api/billing")
def billing_status() -> dict:
    """Formules réellement disponibles à l'achat (prix Stripe configurés)."""
    if not billing.is_enabled():
        return {"enabled": False, "plans": []}
    plans = [
        {"plan": plan, "yearly": yearly}
        for plan in billing.PAID_PLANS
        for yearly in (False, True)
        if billing.price_id(plan, yearly)
    ]
    return {"enabled": True, "plans": plans}


@app.post("/api/billing/checkout", dependencies=[Depends(auth.require_json)])
def billing_checkout(payload: CheckoutRequest, user=Depends(auth.require_user)) -> dict:
    if not billing.is_enabled():
        raise HTTPException(status_code=503, detail="Les abonnements ouvrent très bientôt.")
    if user["plan"] != "decouverte":
        raise HTTPException(
            status_code=409,
            detail="Tu as déjà un abonnement : change de forfait depuis « Gérer mon abonnement ».",
        )
    price = billing.price_id(payload.plan, payload.yearly)
    if not price:
        raise HTTPException(status_code=400, detail="Cette formule n'est pas encore disponible.")
    try:
        customer = user["stripe_customer_id"]
        if not customer:
            customer = billing.create_customer(user["email"], user["id"])
            with closing(db.connect()) as conn, conn:
                conn.execute("UPDATE users SET stripe_customer_id = ? WHERE id = ?", (customer, user["id"]))
        return {"url": billing.create_checkout(customer, price, auth.site_url())}
    except billing.BillingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/billing/portal", dependencies=[Depends(auth.require_json)])
def billing_portal(user=Depends(auth.require_user)) -> dict:
    if not billing.is_enabled() or not user["stripe_customer_id"]:
        raise HTTPException(status_code=400, detail="Aucun abonnement à gérer.")
    try:
        return {"url": billing.create_portal(user["stripe_customer_id"], auth.site_url())}
    except billing.BillingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def handle_invoice_paid(conn, user, invoice: dict) -> None:
    match = billing.plan_for_price(billing.invoice_price(invoice))
    if not match:
        log.warning("Webhook Stripe : prix inconnu sur la facture %s", invoice.get("id"))
        return
    plan, yearly = match
    reason = invoice.get("billing_reason")
    old_plan = user["plan"]
    conn.execute("UPDATE users SET plan = ? WHERE id = ?", (plan, user["id"]))

    if reason in ("subscription_create", "subscription_cycle"):
        amount = billing.credits_for(plan, yearly)
    elif reason == "subscription_update" and (invoice.get("amount_paid") or 0) > 0:
        previous = billing.credits_for(old_plan, yearly) if old_plan in billing.PAID_PLANS else 0
        amount = billing.credits_for(plan, yearly) - previous
    else:
        amount = 0
    if amount > 0:
        db.add_credits(conn, user["id"], amount, f"plan:{plan}", ref=f"invoice:{invoice['id']}")


@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request) -> dict:
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    payload = await request.body()
    if not secret or not billing.verify_signature(payload, request.headers.get("stripe-signature", ""), secret):
        raise HTTPException(status_code=400, detail="Signature invalide.")

    event = json.loads(payload)
    obj = event.get("data", {}).get("object", {})
    with closing(db.connect()) as conn, conn:
        user = conn.execute("SELECT * FROM users WHERE stripe_customer_id = ?", (obj.get("customer"),)).fetchone()
        if not user:
            log.warning("Webhook Stripe %s : client inconnu %s", event.get("type"), obj.get("customer"))
            return {"received": True}

        if event.get("type") == "invoice.paid":
            handle_invoice_paid(conn, user, obj)
        elif event.get("type") == "customer.subscription.deleted":
            conn.execute("UPDATE users SET plan = 'decouverte' WHERE id = ?", (user["id"],))
    return {"received": True}


# ---------------------------------------------------------------- fin

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail="Route inconnue.")


# Monté en dernier pour ne pas masquer les routes /api.
# En mode html, StaticFiles sert automatiquement 404.html pour les pages absentes.
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="site")


if __name__ == "__main__":
    import csv
    import sys

    if sys.argv[1:] != ["export"]:
        sys.exit("Usage : python server.py export > inscriptions.csv")
    writer = csv.writer(sys.stdout)
    writer.writerow(["email", "forfait", "inscrit_le", "compte_active", "credits"])
    with closing(db.connect()) as conn:
        writer.writerows(conn.execute(
            """SELECT s.email, COALESCE(u.plan, s.plan), s.created_at,
                      CASE WHEN u.id IS NULL THEN 'non' ELSE 'oui' END, COALESCE(u.credits, '')
               FROM signups s LEFT JOIN users u ON u.email = s.email ORDER BY s.id"""
        ))
