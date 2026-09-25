"""Base SQLite : schéma, comptes et crédits.

Les crédits sont tenus dans un journal (`credit_ledger`) : chaque mouvement
est une ligne, et `users.credits` n'est que le solde mis en cache. La colonne
`ref` (unique) rend les crédits idempotents : un même paiement Stripe ou un
même remboursement ne peut pas être compté deux fois.
"""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
WELCOME_CREDITS = 50


def db_path() -> Path:
    return Path(os.environ.get("REGAM_DB", ROOT / "data" / "regam.db"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS signups (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT NOT NULL UNIQUE,
    plan       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    email              TEXT NOT NULL UNIQUE,
    plan               TEXT NOT NULL DEFAULT 'decouverte',
    credits            INTEGER NOT NULL DEFAULT 0 CHECK (credits >= 0),
    stripe_customer_id TEXT UNIQUE,
    created_at         TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS credit_ledger (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    delta      INTEGER NOT NULL,
    reason     TEXT NOT NULL,
    ref        TEXT UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_tokens (
    token_hash TEXT PRIMARY KEY,
    email      TEXT NOT NULL,
    next       TEXT,
    expires_at TEXT NOT NULL,
    used_at    TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS generations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ip         TEXT NOT NULL,
    user_id    INTEGER REFERENCES users(id),
    mode       TEXT NOT NULL,
    prompt     TEXT NOT NULL,
    url        TEXT,
    status     TEXT NOT NULL DEFAULT 'done',
    cost       INTEGER NOT NULL DEFAULT 0,
    status_url TEXT,
    result_url TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS generations_day ON generations (created_at);
CREATE INDEX IF NOT EXISTS generations_user ON generations (user_id, id);
"""

# Colonnes ajoutées après la première version (bases existantes).
MIGRATIONS = [
    ("generations", "user_id", "INTEGER REFERENCES users(id)"),
    ("generations", "status", "TEXT NOT NULL DEFAULT 'done'"),
    ("generations", "cost", "INTEGER NOT NULL DEFAULT 0"),
    ("generations", "status_url", "TEXT"),
    ("generations", "result_url", "TEXT"),
]


def _url_is_required(db: sqlite3.Connection) -> bool:
    return any(r["name"] == "url" and r["notnull"] for r in db.execute("PRAGMA table_info(generations)"))


def init() -> None:
    with closing(connect()) as db, db:
        # Première version : `generations.url` était NOT NULL, incompatible avec
        # les vidéos en cours. SQLite ne sait pas retirer la contrainte : on
        # reconstruit la table en conservant les lignes.
        if _url_is_required(db):
            db.execute("ALTER TABLE generations RENAME TO generations_v1")
            db.execute("DROP INDEX IF EXISTS generations_day")
        # Anciennes bases : ajouter les colonnes manquantes avant de créer les index.
        for table, column, decl in MIGRATIONS:
            cols = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
            if cols and column not in cols:
                db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
        db.executescript(SCHEMA)
        if db.execute("SELECT 1 FROM sqlite_master WHERE name = 'generations_v1'").fetchone():
            db.execute(
                """INSERT INTO generations (id, ip, mode, prompt, url, status, created_at)
                   SELECT id, ip, mode, prompt, url, 'done', created_at FROM generations_v1"""
            )
            db.execute("DROP TABLE generations_v1")


# ---------------------------------------------------------------- users

def get_user(db: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_or_create_user(db: sqlite3.Connection, email: str) -> tuple[sqlite3.Row, bool]:
    """Renvoie (utilisateur, créé ?). Un nouveau compte reçoit les crédits de bienvenue."""
    row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row:
        return row, False
    cur = db.execute("INSERT INTO users (email, created_at) VALUES (?, ?)", (email, now()))
    add_credits(db, cur.lastrowid, WELCOME_CREDITS, "welcome", ref=f"welcome:{cur.lastrowid}")
    return get_user(db, cur.lastrowid), True


# ---------------------------------------------------------------- credits

def add_credits(db: sqlite3.Connection, user_id: int, amount: int, reason: str, ref: str | None = None) -> bool:
    """Ajoute des crédits. Renvoie False si `ref` a déjà été compté (idempotence)."""
    try:
        db.execute(
            "INSERT INTO credit_ledger (user_id, delta, reason, ref, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, reason, ref, now()),
        )
    except sqlite3.IntegrityError:
        return False
    db.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (amount, user_id))
    return True


def spend_credits(db: sqlite3.Connection, user_id: int, amount: int, reason: str, ref: str | None = None) -> bool:
    """Débite si le solde suffit (opération atomique). Renvoie False sinon."""
    cur = db.execute(
        "UPDATE users SET credits = credits - ? WHERE id = ? AND credits >= ?",
        (amount, user_id, amount),
    )
    if cur.rowcount == 0:
        return False
    db.execute(
        "INSERT INTO credit_ledger (user_id, delta, reason, ref, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, -amount, reason, ref, now()),
    )
    return True
