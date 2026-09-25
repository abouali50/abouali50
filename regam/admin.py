"""Tableau de bord d'administration (/admin.html).

Accès réservé aux adresses listées dans REGAM_ADMIN_EMAILS (séparées par des
virgules), après connexion normale par lien magique.

Coûts IA estimés (en dollars, à ajuster selon vos tarifs fal.ai) :
  REGAM_COST_IMAGE_USD    par image ou avatar (défaut 0.003)
  REGAM_COST_VIDEO5_USD   par vidéo de 5 s (défaut 0.30)
  REGAM_COST_VIDEO10_USD  par vidéo de 10 s (défaut 0.60)
"""

import os
from contextlib import closing
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

import auth
import db

router = APIRouter(prefix="/api/admin")

PLAN_PRICES_EUR = {"createur": 19, "pro": 49}


def admin_emails() -> set[str]:
    raw = os.environ.get("REGAM_ADMIN_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def require_admin(user=Depends(auth.require_user)):
    if user["email"] not in admin_emails():
        raise HTTPException(status_code=403, detail="Accès réservé à l'équipe Regam.")
    return user


def _cost(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


def _since(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


@router.get("/stats")
def stats(_admin=Depends(require_admin)) -> dict:
    d30, d7 = _since(30), _since(7)
    with closing(db.connect()) as conn:
        one = lambda sql, *args: conn.execute(sql, args).fetchone()[0]  # noqa: E731

        plans = dict(conn.execute("SELECT plan, COUNT(*) FROM users GROUP BY plan").fetchall())
        gens = conn.execute(
            """SELECT mode, cost, status, user_id IS NULL AS anon, COUNT(*) AS n FROM generations
               WHERE created_at >= ? GROUP BY mode, cost, status, anon""",
            (d30,),
        ).fetchall()

        by_mode = {"image": 0, "avatar": 0, "video": 0}
        failed = anonymous = video5 = video10 = 0
        for g in gens:
            if g["status"] == "failed":
                failed += g["n"]
                continue
            by_mode[g["mode"]] = by_mode.get(g["mode"], 0) + g["n"]
            anonymous += g["n"] if g["anon"] else 0
            if g["mode"] == "video":
                if g["cost"] >= 16:
                    video10 += g["n"]
                else:
                    video5 += g["n"]

        cost_usd = (
            (by_mode["image"] + by_mode["avatar"]) * _cost("REGAM_COST_IMAGE_USD", 0.003)
            + video5 * _cost("REGAM_COST_VIDEO5_USD", 0.30)
            + video10 * _cost("REGAM_COST_VIDEO10_USD", 0.60)
        )

        # Activité quotidienne sur 30 jours (jours sans activité inclus).
        today = datetime.now(timezone.utc).date()
        days = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
        per_day = dict(conn.execute(
            """SELECT substr(created_at, 1, 10), COUNT(*) FROM generations
               WHERE created_at >= ? AND status != 'failed' GROUP BY 1""", (days[0],)).fetchall())
        users_per_day = dict(conn.execute(
            "SELECT substr(created_at, 1, 10), COUNT(*) FROM users WHERE created_at >= ? GROUP BY 1",
            (days[0],)).fetchall())

        recent = conn.execute(
            """SELECT u.email, u.plan, u.credits, u.created_at,
                      (SELECT COUNT(*) FROM generations g WHERE g.user_id = u.id AND g.status = 'done') AS generations
               FROM users u ORDER BY u.id DESC LIMIT 25"""
        ).fetchall()

        return {
            "users": {
                "total": one("SELECT COUNT(*) FROM users"),
                "new_7d": one("SELECT COUNT(*) FROM users WHERE created_at >= ?", d7),
                "waitlist": one("SELECT COUNT(*) FROM signups s WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.email = s.email)"),
                "by_plan": {p: plans.get(p, 0) for p in ("decouverte", "createur", "pro")},
            },
            # Estimation au prix mensuel affiché (un abonnement annuel compte pour son équivalent mensuel plein).
            "mrr_eur": sum(plans.get(p, 0) * price for p, price in PLAN_PRICES_EUR.items()),
            "credits_30d": {
                "granted": one("SELECT COALESCE(SUM(delta), 0) FROM credit_ledger WHERE delta > 0 AND reason != 'refund' AND created_at >= ?", d30),
                "spent": -one("SELECT COALESCE(SUM(delta), 0) FROM credit_ledger WHERE delta < 0 AND created_at >= ?", d30)
                - one("SELECT COALESCE(SUM(delta), 0) FROM credit_ledger WHERE reason = 'refund' AND created_at >= ?", d30),
            },
            "generations_30d": {**by_mode, "failed": failed, "anonymous": anonymous, "video_5s": video5, "video_10s": video10},
            "ai_cost_usd_30d": round(cost_usd, 2),
            "daily": [{"date": d, "generations": per_day.get(d, 0), "new_users": users_per_day.get(d, 0)} for d in days],
            "recent_users": [dict(r) for r in recent],
        }


class CreditGrant(BaseModel):
    email: EmailStr
    amount: int = Field(ge=-100_000, le=100_000)
    note: str = Field(default="", max_length=120)


@router.post("/credits", dependencies=[Depends(auth.require_json)])
def grant_credits(payload: CreditGrant, admin=Depends(require_admin)) -> dict:
    if payload.amount == 0:
        raise HTTPException(status_code=422, detail="Le montant ne peut pas être nul.")
    reason = f"admin:{admin['email']}" + (f":{payload.note}" if payload.note else "")
    with closing(db.connect()) as conn, conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Aucun compte avec cette adresse.")
        if payload.amount > 0:
            db.add_credits(conn, user["id"], payload.amount, reason)
        elif not db.spend_credits(conn, user["id"], -payload.amount, reason):
            raise HTTPException(status_code=400, detail="Solde insuffisant pour ce retrait.")
        credits = db.get_user(conn, user["id"])["credits"]
    return {"email": user["email"], "credits": credits}
