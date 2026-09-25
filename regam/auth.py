"""Connexion sans mot de passe par lien magique.

1. POST /api/auth/request {email}   → e-mail avec un lien /compte.html#token=…
2. La page compte envoie le jeton :  POST /api/auth/verify {token}
   → cookie de session HttpOnly (30 jours).

Le jeton est dans le fragment (#) de l'URL et échangé par JavaScript : les
antivirus d'e-mail qui « visitent » les liens ne peuvent donc pas le consommer.
On ne stocke que des empreintes SHA-256 des jetons.
"""

import hashlib
import os
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, Response

import db

COOKIE = "regam_session"
LOGIN_TTL = timedelta(minutes=30)
SESSION_TTL = timedelta(days=30)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _expires(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


def site_url() -> str:
    return os.environ.get("REGAM_SITE_URL", "http://localhost:8080").rstrip("/")


def safe_next(value: str | None) -> str | None:
    """N'accepte qu'un chemin relatif du site (pas de redirection ouverte)."""
    if value and value.startswith("/") and not value.startswith("//") and "\\" not in value:
        return value[:200]
    return None


# ---------------------------------------------------------------- login links

def create_login_token(conn: sqlite3.Connection, email: str, next_path: str | None) -> str:
    token = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO login_tokens (token_hash, email, next, expires_at) VALUES (?, ?, ?, ?)",
        (_hash(token), email, safe_next(next_path), _expires(LOGIN_TTL)),
    )
    return token


def login_link(token: str) -> str:
    return f"{site_url()}/compte.html#token={token}"


def consume_login_token(conn: sqlite3.Connection, token: str) -> sqlite3.Row | None:
    """Marque le jeton comme utilisé. Renvoie la ligne, ou None si invalide/expiré/déjà utilisé."""
    cur = conn.execute(
        "UPDATE login_tokens SET used_at = ? WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?",
        (db.now(), _hash(token), db.now()),
    )
    if cur.rowcount == 0:
        return None
    return conn.execute("SELECT * FROM login_tokens WHERE token_hash = ?", (_hash(token),)).fetchone()


# ---------------------------------------------------------------- sessions

def create_session(conn: sqlite3.Connection, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (_hash(token), user_id, _expires(SESSION_TTL)),
    )
    return token


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE,
        token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=site_url().startswith("https://"),
        path="/",
    )


def current_user(request: Request) -> sqlite3.Row | None:
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    with closing(db.connect()) as conn:
        return conn.execute(
            """SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id
               WHERE sessions.token_hash = ? AND sessions.expires_at > ?""",
            (_hash(token), db.now()),
        ).fetchone()


def require_user(request: Request) -> sqlite3.Row:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Connecte-toi pour continuer.")
    return user


def end_session(request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE)
    if token:
        with closing(db.connect()) as conn, conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_hash(token),))
    response.delete_cookie(COOKIE, path="/")


def require_json(request: Request) -> None:
    """Protection CSRF : un site tiers ne peut pas envoyer du JSON sans pré-vol CORS."""
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise HTTPException(status_code=415, detail="Content-Type application/json requis.")
