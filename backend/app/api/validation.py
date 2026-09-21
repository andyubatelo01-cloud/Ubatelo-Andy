"""Centre de validation mobile : /valider/{token}.

Le lien reçu par SMS ouvre une page qui affiche l'APERÇU DE LA CAMPAGNE et les
trois actions. Le jeton est à usage unique, lié au contenu exact validé, et ne
suffit pas à lui seul : la validation exige en plus le mot de passe du pasteur.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..db import get_db
from ..models import CampaignStatus, Role, User, utcnow
from ..security import verify_password
from ..services import campaign_engine as engine

router = APIRouter(tags=["validation-mobile"])
FRONTEND = Path(__file__).resolve().parents[3] / "frontend"


class MobileDecision(BaseModel):
    action: str  # VALIDER | CONFIRMER | ANNULER
    email: str
    password: str
    phrase: str = ""


@router.get("/valider/{token}", response_class=HTMLResponse)
def validation_page(token: str):
    page = FRONTEND / "valider.html"
    return HTMLResponse(page.read_text(encoding="utf-8") if page.exists() else "<h1>Page de validation indisponible</h1>")


@router.get("/api/valider/{token}")
def validation_preview(token: str, db: Session = Depends(get_db)):
    try:
        campaign, _ = engine.resolve_approval_token(db, token)
    except engine.CampaignError as exc:
        raise HTTPException(410, str(exc))
    return engine.preview(db, campaign) | {"content_hash": engine.fingerprint(campaign)}


@router.post("/api/valider/{token}")
def validation_decide(token: str, body: MobileDecision, db: Session = Depends(get_db)):
    try:
        campaign, tok = engine.resolve_approval_token(db, token)
    except engine.CampaignError as exc:
        raise HTTPException(410, str(exc))
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if user is None or not verify_password(body.password, user.password_hash) or user.role != Role.PASTEUR.value:
        audit.log(db, body.email[:120], "MOBILE_VALIDATION_AUTH_FAILED", "campaign", campaign.ref)
        db.commit()
        raise HTTPException(401, "Identifiants du pasteur incorrects.")
    action = body.action.upper()
    try:
        if action == "ANNULER":
            engine.cancel(db, campaign, user.name, "annulée depuis le téléphone")
            tok.used_at = utcnow()
        elif action == "VALIDER":
            engine.approve(db, campaign, user, tok.content_hash)
            if campaign.pending_confirmation:
                db.commit()
                return {"preview": engine.preview(db, campaign), "double_validation": True, "message": f"⚠️ Cette campagne concerne {campaign.recipient_count} personnes. Répondez exactement « {engine.CONFIRMATION_PHRASE} » pour confirmer."}
            tok.used_at = utcnow()
        elif action == "CONFIRMER":
            engine.confirm(db, campaign, user, body.phrase)
            tok.used_at = utcnow()
        else:
            raise HTTPException(400, "Action inconnue.")
    except engine.CampaignError as exc:
        db.commit()
        raise HTTPException(409, str(exc))
    db.commit()
    if campaign.status == CampaignStatus.APPROVED.value:
        engine.dispatch(db, campaign, user.name)
        db.commit()
    return {"preview": engine.preview(db, campaign), "double_validation": False, "resultat": campaign.result}
