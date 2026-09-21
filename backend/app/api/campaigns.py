from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..agents import AnalyticsAgent, CommunicationAgent
from ..agents.communication import KIND_LABELS, TEMPLATES
from ..db import get_db
from ..models import Campaign, CampaignStatus, Event, MessageStyle, User
from ..schemas import ApproveIn, CampaignIn, CampaignPatch, CancelIn, ConfirmIn, DraftIn
from ..services import campaign_engine as engine
from ..services import notifications
from .deps import anyone, pastor_only, staff

router = APIRouter(prefix="/api/campagnes", tags=["campagnes"])


def _get(db: Session, ref: str) -> Campaign:
    c = engine.get_by_ref(db, ref)
    if c is None:
        raise HTTPException(404, f"Campagne {ref} introuvable.")
    return c


def _err(exc: Exception) -> HTTPException:
    return HTTPException(409 if isinstance(exc, engine.CampaignError) else 500, str(exc))


@router.get("")
def list_campaigns(status: str | None = None, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(anyone)):
    stmt = select(Campaign).order_by(Campaign.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(Campaign.status.in_(status.split(",")))
    return [engine.preview(db, c) for c in db.scalars(stmt).all()]


@router.get("/a-valider")
def to_validate(db: Session = Depends(get_db), _: User = Depends(anyone)):
    return [engine.preview(db, c) for c in engine.pending_review(db)]


@router.get("/statuts")
def statuses(_: User = Depends(anyone)):
    return {"statuts": [s.value for s in CampaignStatus], "transitions": {k: sorted(v) for k, v in engine.TRANSITIONS.items()}, "styles": [s.value for s in MessageStyle], "types": KIND_LABELS}


@router.post("/rediger")
def draft(body: DraftIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """Demande à l'agent COMMUNICATION une proposition de message (sans créer de campagne)."""
    event = db.get(Event, body.event_id) if body.event_id else None
    if body.kind not in TEMPLATES:
        raise HTTPException(400, f"Type inconnu. Types : {', '.join(TEMPLATES)}")
    res = CommunicationAgent(db, actor.name).draft(body.kind, body.style, body.channel, event, body.audience, body.instructions)
    db.commit()
    return res.as_dict()


@router.get("/variantes")
def variants(kind: str = "invitation", channel: str = "SMS", event_id: int | None = None, db: Session = Depends(get_db), actor: User = Depends(staff)):
    event = db.get(Event, event_id) if event_id else None
    out = CommunicationAgent(db, actor.name).variants(kind, channel, event)
    db.commit()
    return out


@router.post("", status_code=201)
def create(body: CampaignIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    c = engine.create_campaign(db, created_by=actor.name, **body.model_dump())
    engine.submit_for_review(db, c, actor.name)
    db.commit()
    return engine.preview(db, c)


@router.get("/{ref}")
def get_campaign(ref: str, db: Session = Depends(get_db), _: User = Depends(anyone)):
    return engine.preview(db, _get(db, ref))


@router.get("/{ref}/rapport")
def report(ref: str, db: Session = Depends(get_db), _: User = Depends(anyone)):
    return AnalyticsAgent(db).campaign_report(_get(db, ref))


@router.patch("/{ref}")
def modify(ref: str, body: CampaignPatch, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """🟡 MODIFIER — toute modification annule une validation antérieure et relance les contrôles."""
    c = _get(db, ref)
    try:
        engine.update_campaign(db, c, actor.name, **body.model_dump(exclude_unset=True))
        engine.submit_for_review(db, c, actor.name)
    except engine.CampaignError as exc:
        db.rollback()
        raise _err(exc)
    db.commit()
    return engine.preview(db, c)


@router.post("/{ref}/controler")
def recheck(ref: str, db: Session = Depends(get_db), actor: User = Depends(staff)):
    c = _get(db, ref)
    try:
        report = engine.submit_for_review(db, c, actor.name)
    except engine.CampaignError as exc:
        raise _err(exc)
    db.commit()
    return {"preview": engine.preview(db, c), "report": report.as_dict()}


@router.post("/{ref}/valider")
def approve(ref: str, body: ApproveIn | None = None, db: Session = Depends(get_db), pastor: User = Depends(pastor_only)):
    """🟢 VALIDER ET ENVOYER — réservé au rôle PASTEUR."""
    c = _get(db, ref)
    try:
        engine.approve(db, c, pastor, body.content_hash if body else None)
    except engine.CampaignError as exc:
        db.commit()  # conserve l'éventuel passage en BLOCKED et l'audit
        raise _err(exc)
    db.commit()
    if c.pending_confirmation:
        return {"preview": engine.preview(db, c), "double_validation": True, "message": f"⚠️ Cette campagne concerne {c.recipient_count} personnes. Confirmez-vous l'envoi ? Répondez exactement : {engine.CONFIRMATION_PHRASE}"}
    if c.status == CampaignStatus.APPROVED.value:
        engine.dispatch(db, c, pastor.name)
        db.commit()
    return {"preview": engine.preview(db, c), "double_validation": False, "resultat": c.result}


@router.post("/{ref}/confirmer")
def confirm(ref: str, body: ConfirmIn, db: Session = Depends(get_db), pastor: User = Depends(pastor_only)):
    c = _get(db, ref)
    try:
        engine.confirm(db, c, pastor, body.phrase)
    except engine.CampaignError as exc:
        db.commit()
        raise _err(exc)
    db.commit()
    if c.status == CampaignStatus.APPROVED.value:
        engine.dispatch(db, c, pastor.name)
        db.commit()
    return {"preview": engine.preview(db, c), "resultat": c.result}


@router.post("/{ref}/annuler")
def cancel(ref: str, body: CancelIn | None = None, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """🔴 ANNULER"""
    c = _get(db, ref)
    try:
        engine.cancel(db, c, actor.name, body.reason if body else "")
    except engine.CampaignError as exc:
        raise _err(exc)
    db.commit()
    return engine.preview(db, c)


@router.post("/{ref}/envoyer-lien-validation")
def send_link(ref: str, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """Envoie (ou renvoie) le lien de validation mobile au pasteur."""
    c = _get(db, ref)
    if c.status != CampaignStatus.READY_FOR_REVIEW.value:
        raise HTTPException(409, "Seule une campagne prête à valider peut recevoir un lien de validation.")
    out = notifications.send_validation_request(db, c)
    db.commit()
    return out
