from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..db import get_db
from ..models import Role, User
from ..schemas import LoginIn, UserIn, UserOut
from ..security import create_session_token, hash_password, verify_password
from .deps import current_user, pastor_only

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if user is None or not user.is_active or not verify_password(body.password, user.password_hash):
        audit.log(db, body.email[:120], "LOGIN_FAILED")
        db.commit()
        raise HTTPException(401, "Identifiants incorrects.")
    audit.log(db, user.name, "LOGIN", "user", str(user.id))
    db.commit()
    return {"token": create_session_token(user.id, user.role), "user": UserOut.model_validate(user)}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(pastor_only)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserIn, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    if body.role not in {r.value for r in Role}:
        raise HTTPException(400, "Rôle inconnu.")
    if db.scalar(select(User).where(User.email == body.email.lower())):
        raise HTTPException(409, "Un compte existe déjà avec cet e-mail.")
    user = User(email=body.email.lower(), name=body.name, password_hash=hash_password(body.password), role=body.role, phone=body.phone)
    db.add(user)
    db.flush()
    audit.log(db, actor.name, "USER_CREATED", "user", str(user.id), {"role": body.role})
    db.commit()
    return user


@router.delete("/users/{user_id}", status_code=204)
def deactivate_user(user_id: int, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404)
    if user.id == actor.id:
        raise HTTPException(400, "Vous ne pouvez pas désactiver votre propre compte.")
    user.is_active = False
    audit.log(db, actor.name, "USER_DEACTIVATED", "user", str(user.id))
    db.commit()
