"""Webhooks entrants : réponses des membres (STOP / désinscription) et statuts de livraison.

Les réponses « STOP », « ARRET », « DESINSCRIRE » retirent immédiatement le
consentement du canal concerné (obligation légale et règle de la plateforme).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..db import get_db
from ..models import Channel, Delivery, Priority
from ..services import members as members_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

STOP_WORDS = {"stop", "arret", "arrêt", "desinscrire", "désinscrire", "desabonner", "désabonner", "unsubscribe", "fin"}
HELP_WORDS = {"aide", "help", "info"}


@router.post("/twilio/inbound", response_class=PlainTextResponse)
async def twilio_inbound(request: Request, db: Session = Depends(get_db)):
    """Message entrant SMS ou WhatsApp (format Twilio : From, Body)."""
    form = await request.form()
    sender = str(form.get("From", ""))
    body = str(form.get("Body", "")).strip()
    channel = Channel.WHATSAPP.value if sender.startswith("whatsapp:") else Channel.SMS.value
    member = members_service.find_member_by_contact(db, sender)
    word = body.lower().strip(" .!")
    if member is None:
        audit.log(db, "WEBHOOK", "INBOUND_UNKNOWN_SENDER", details={"channel": channel})
        db.commit()
        return ""
    if word in STOP_WORDS:
        members_service.unsubscribe(db, member, channel, source=f"réponse {body.upper()}")
        db.commit()
        return "Vous ne recevrez plus de messages de notre part sur ce canal. Répondez START pour vous réabonner."
    if word == "start":
        members_service.record_consent(db, member, **{"sms" if channel == Channel.SMS.value else "whatsapp": True}, actor="WEBHOOK")
        db.commit()
        return "Merci, vous recevrez à nouveau nos messages."
    if word in HELP_WORDS:
        return "Bureau de la communauté. Répondez STOP pour ne plus recevoir de messages."
    if word in {"oui", "yes", "ok", "présent", "present", "je viens"}:
        _confirm_latest_event(db, member)
    audit.notify(db, Priority.INFORMATION, f"Réponse de {member.full_name}", body[:300], f"/membres/{member.id}")
    audit.log(db, "WEBHOOK", "INBOUND_MESSAGE", "member", str(member.id), {"channel": channel, "length": len(body)})
    db.commit()
    return ""


def _confirm_latest_event(db: Session, member) -> None:
    """Un « OUI » confirme la présence pour la dernière campagne d'événement reçue."""
    from ..services import events as events_service

    last = db.scalar(select(Delivery).where(Delivery.member_id == member.id, Delivery.status == "SENT").order_by(Delivery.sent_at.desc()))
    if last and last.campaign and last.campaign.event:
        events_service.set_attendance(db, last.campaign.event, member, confirmed=True, actor="WEBHOOK")


@router.post("/twilio/status", response_class=PlainTextResponse)
def twilio_status(MessageSid: str = Form(""), MessageStatus: str = Form(""), db: Session = Depends(get_db)):
    """Accusés de livraison Twilio (queued, sent, delivered, failed, undelivered)."""
    d = db.scalar(select(Delivery).where(Delivery.provider_id == MessageSid))
    if d is not None:
        if MessageStatus == "delivered":
            d.status = "DELIVERED"
        elif MessageStatus in ("failed", "undelivered"):
            d.status, d.error = "FAILED", f"Statut Twilio : {MessageStatus}"
        db.commit()
    return ""
