"""Authentification, rôles et jetons signés.

- Mots de passe : PBKDF2-HMAC-SHA256 (bibliothèque standard, aucun secret en clair).
- Sessions : jeton HMAC signé, durée limitée.
- Validation mobile : jeton aléatoire à usage unique, lié à l'empreinte du contenu validé.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from .config import get_settings

_PBKDF2_ROUNDS = 200_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2${_PBKDF2_ROUNDS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt_b64, digest_b64 = stored.split("$")
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
    except (ValueError, TypeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
    return hmac.compare_digest(candidate, expected)


# ── Jetons de session ─────────────────────────────────────────────────────────


def _sign(payload: bytes) -> str:
    key = get_settings().secret_key.encode()
    return base64.urlsafe_b64encode(hmac.new(key, payload, hashlib.sha256).digest()).decode().rstrip("=")


def create_session_token(user_id: int, role: str, ttl_seconds: int = 12 * 3600) -> str:
    payload = json.dumps({"uid": user_id, "role": role, "exp": int(time.time()) + ttl_seconds}).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"{body}.{_sign(payload)}"


def read_session_token(token: str) -> dict | None:
    try:
        body, sig = token.split(".", 1)
        payload = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
    except (ValueError, TypeError):
        return None
    if not hmac.compare_digest(_sign(payload), sig):
        return None
    data = json.loads(payload)
    if data.get("exp", 0) < time.time():
        return None
    return data


# ── Jetons de validation mobile ──────────────────────────────────────────────


def new_approval_token() -> tuple[str, str]:
    """Retourne (jeton en clair à envoyer au pasteur, empreinte à stocker)."""
    raw = secrets.token_urlsafe(32)
    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def content_fingerprint(*parts: object) -> str:
    """Empreinte stable du contenu d'une campagne (message, canal, cibles, date)."""
    canonical = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()
