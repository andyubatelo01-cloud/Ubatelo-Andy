"""Dépendances communes : session, utilisateur courant, contrôle des rôles."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Role, User
from ..security import read_session_token


def current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise.")
    data = read_session_token(authorization[7:].strip())
    if not data:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session invalide ou expirée.")
    user = db.get(User, data["uid"])
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Compte inactif.")
    return user


def require_roles(*roles: Role):
    allowed = {r.value for r in roles}

    def _check(user: User = Depends(current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Action réservée aux rôles : {', '.join(sorted(allowed))}.")
        return user

    return _check


pastor_only = require_roles(Role.PASTEUR)
staff = require_roles(Role.PASTEUR, Role.SECRETAIRE)
anyone = require_roles(Role.PASTEUR, Role.SECRETAIRE, Role.LECTEUR)
