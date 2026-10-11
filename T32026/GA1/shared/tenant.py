from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import closing
from pathlib import Path
from urllib.parse import quote

_REDIS_LOCK = threading.Lock()
_REDIS_CLIENT = None
_REDIS_URL = None


def normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def _database_path() -> Path:
    configured = os.environ.get("GA1_TENANT_DB_PATH")
    if configured:
        return Path(configured)
    # Unlike the OS temp directory, this location can be mounted as a persistent
    # volume by a single-instance deployment. For replicas, set GA1_REDIS_URL.
    return Path(__file__).resolve().parents[3] / "work" / "t32026_ga1_tenants.sqlite3"


def _redis_client():
    global _REDIS_CLIENT, _REDIS_URL
    url = os.environ.get("GA1_REDIS_URL")
    if not url:
        return None
    with _REDIS_LOCK:
        if _REDIS_CLIENT is not None and _REDIS_URL == url:
            return _REDIS_CLIENT
        try:
            from redis import Redis

            client = Redis.from_url(url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
            client.ping()
            _REDIS_CLIENT, _REDIS_URL = client, url
            return client
        except Exception as exc:
            _REDIS_CLIENT, _REDIS_URL = None, None
            raise RuntimeError("GA1_REDIS_UNAVAILABLE") from exc


def _connect() -> sqlite3.Connection:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=8, isolation_level="IMMEDIATE")
    db.execute("PRAGMA busy_timeout = 8000")
    db.execute("PRAGMA journal_mode = WAL")
    db.execute("CREATE TABLE IF NOT EXISTS tenants (email TEXT PRIMARY KEY, config_json TEXT NOT NULL)")
    return db


def get_config(email: str) -> dict[str, str]:
    key = normalize_email(email)
    if not key:
        return {}
    client = _redis_client()
    if client is not None:
        redis_key = f"t32026:ga1:tenant:{key}"
        values = client.hgetall(redis_key)
        if values:
            return values
        # Read and migrate a previous JSON-string record, if present.
        raw = client.get(redis_key)
        if raw:
            data = json.loads(raw)
            if isinstance(data, dict):
                client.hset(redis_key, mapping={str(k): str(v) for k, v in data.items()})
                client.delete(redis_key + ":legacy")
                return {str(k): str(v) for k, v in data.items()}
        return {}
    with closing(_connect()) as connection:
        with connection as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT config_json FROM tenants WHERE email = ?", (key,)).fetchone()
    if not row:
        return {}
    data = json.loads(row[0])
    return data if isinstance(data, dict) else {}


def set_config(email: str, values: dict[str, str]) -> dict[str, str]:
    key = normalize_email(email)
    if not key:
        raise ValueError("VALID_EMAIL_REQUIRED")
    client = _redis_client()
    if client is not None:
        redis_key = f"t32026:ga1:tenant:{key}"
        client.hset(redis_key, mapping={str(k): str(v) for k, v in values.items()})
        return {str(k): str(v) for k, v in client.hgetall(redis_key).items()}
    with closing(_connect()) as connection:
        with connection as db:
            row = db.execute("SELECT config_json FROM tenants WHERE email = ?", (key,)).fetchone()
            current = json.loads(row[0]) if row else {}
            if not isinstance(current, dict):
                current = {}
            current.update(values)
            db.execute(
                "INSERT INTO tenants(email, config_json) VALUES(?, ?) "
                "ON CONFLICT(email) DO UPDATE SET config_json = excluded.config_json",
                (key, json.dumps(current, ensure_ascii=False)),
            )
    return current


def tenant_prefix(base_url: str, email: str) -> str:
    return f"{base_url.rstrip('/')}/ga1/{quote(normalize_email(email), safe='')}"
