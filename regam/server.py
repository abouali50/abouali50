"""Regam — serveur du site vitrine.

Sert le site statique de `public/` et expose l'API :
  - inscriptions (SQLite) + e-mail de bienvenue (voir mailer.py)
  - génération d'images IA pour le studio (voir generate.py)

Lancement :  uvicorn server:app --reload --port 8080
Export CSV : python server.py export > inscriptions.csv
"""

import os
import sqlite3
import time
from collections import defaultdict, deque
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

import generate
import mailer

ROOT = Path(__file__).parent
PUBLIC_DIR = ROOT / "public"
DB_PATH = Path(os.environ.get("REGAM_DB", ROOT / "data" / "regam.db"))

RATE_LIMIT = int(os.environ.get("REGAM_RATE_LIMIT", "5"))  # requêtes / fenêtre / IP
RATE_WINDOW_S = 60

Plan = Literal["decouverte", "createur", "pro"]


# ---------------------------------------------------------------- database

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with closing(connect()) as db, db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS signups (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                email      TEXT NOT NULL UNIQUE,
                plan       TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                ip         TEXT NOT NULL,
                mode       TEXT NOT NULL,
                prompt     TEXT NOT NULL,
                url        TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        db.execute("CREATE INDEX IF NOT EXISTS generations_day ON generations (created_at)")


# ---------------------------------------------------------------- rate limit

_hits: dict[str, deque] = defaultdict(deque)


def client_ip(request: Request) -> str:
    # Derrière un proxy, lancer uvicorn avec --proxy-headers (voir README).
    return request.client.host if request.client else "unknown"


def rate_limited(key: str) -> bool:
    now = time.monotonic()
    hits = _hits[key]
    while hits and now - hits[0] > RATE_WINDOW_S:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        return True
    hits.append(now)
    return False


# ---------------------------------------------------------------- app

app = FastAPI(title="Regam", docs_url=None, redoc_url=None)
init_db()


class SignupIn(BaseModel):
    email: EmailStr = Field(max_length=254)
    plan: Plan = "decouverte"
    website: str = ""  # pot de miel : doit rester vide


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/signup", status_code=201)
def signup(
    payload: SignupIn, request: Request, response: Response, background: BackgroundTasks
) -> dict:
    if rate_limited(client_ip(request)):
        raise HTTPException(status_code=429, detail="Trop de tentatives.")

    # Un robot a rempli le champ caché : on répond comme si tout allait bien.
    if payload.website:
        return {"ok": True, "already": False}

    email = payload.email.lower()
    with closing(connect()) as db, db:
        cur = db.execute(
            "INSERT OR IGNORE INTO signups (email, plan, created_at) VALUES (?, ?, ?)",
            (email, payload.plan, datetime.now(timezone.utc).isoformat()),
        )
    if cur.rowcount == 0:
        response.status_code = 200
        return {"ok": True, "already": True}
    background.add_task(mailer.send_welcome, email, payload.plan)
    return {"ok": True, "already": False}


# ---------------------------------------------------------------- studio IA

def today_start() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


def usage_today(ip: str) -> tuple[int, int]:
    """(générations de cette IP aujourd'hui, générations totales aujourd'hui)"""
    with closing(connect()) as db:
        mine, total = db.execute(
            "SELECT COALESCE(SUM(ip = ?), 0), COUNT(*) FROM generations WHERE created_at >= ?",
            (ip, today_start()),
        ).fetchone()
    return mine, total


@app.get("/api/studio")
def studio_status(request: Request) -> dict:
    if not generate.is_enabled():
        return {"enabled": False}
    mine, _ = usage_today(client_ip(request))
    return {"enabled": True, "modes": ["avatar", "image"], "remaining": max(0, generate.per_ip_limit() - mine)}


@app.post("/api/generate")
def generate_endpoint(payload: generate.GenerateIn, request: Request) -> dict:
    if not generate.is_enabled():
        raise HTTPException(status_code=503, detail="Le studio est en mode démo.")
    ip = client_ip(request)
    if rate_limited(f"gen:{ip}"):
        raise HTTPException(status_code=429, detail="Trop de tentatives. Patiente une minute.")
    mine, total = usage_today(ip)
    if mine >= generate.per_ip_limit():
        raise HTTPException(status_code=429, detail="Tu as utilisé toutes tes générations gratuites du jour. Reviens demain !")
    if total >= generate.daily_cap():
        raise HTTPException(status_code=503, detail="Le studio est très demandé aujourd'hui. Reviens demain !")

    try:
        image = generate.generate_image(payload)
    except generate.GenerationError as exc:
        raise HTTPException(status_code=exc.status, detail=str(exc)) from exc

    with closing(connect()) as db, db:
        db.execute(
            "INSERT INTO generations (ip, mode, prompt, url, created_at) VALUES (?, ?, ?, ?, ?)",
            (ip, payload.mode, payload.prompt, image["url"], datetime.now(timezone.utc).isoformat()),
        )
    return {**image, "remaining": max(0, generate.per_ip_limit() - mine - 1)}


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
    writer.writerow(["email", "plan", "created_at"])
    with closing(connect()) as db:
        writer.writerows(db.execute("SELECT email, plan, created_at FROM signups ORDER BY id"))
