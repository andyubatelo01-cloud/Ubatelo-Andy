"""Centre de validation mobile : le pasteur reçoit sur son téléphone un lien de
validation à usage unique pour chaque campagne prête.

Ce message est adressé au pasteur lui-même (pas un envoi collectif) : il ne
requiert donc pas de validation préalable.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..channels import OutboundMessage, get_gateway
from ..config import get_settings
from ..models import ApprovalToken, Campaign, CampaignStatus, Channel, User, Role
from . import campaign_engine
from .personalization import format_date_fr


def validation_message(campaign: Campaign, link: str) -> str:
    when = f"{format_date_fr(campaign.send_at)} — {campaign.send_at.strftime('%H:%M')}" if campaign.send_at else "non définie"
    preview = campaign.message if len(campaign.message) <= 200 else campaign.message[:197] + "…"
    extra = "\n⚠️ Double validation requise (répondez « CONFIRMER L'ENVOI » sur la page)." if campaign.requires_double_confirmation else ""
    return (
        f"🔔 BUREAU DU PASTEUR\nCampagne prête : {campaign.name}\n"
        f"👥 {campaign.recipient_count} destinataires · 📱 {campaign.channel}\n🗓️ {when}\n"
        f"Message : « {preview} »{extra}\n"
        f"🟢 Valider / ✏️ Modifier / 🔴 Annuler : {link}"
    )


def pastor_contacts(db: Session) -> list[tuple[str, str]]:
    """(canal, destinataire) où joindre le pasteur : téléphone du compte PASTEUR ou PASTOR_PHONE."""
    s = get_settings()
    out: list[tuple[str, str]] = []
    for u in db.scalars(select(User).where(User.role == Role.PASTEUR.value, User.is_active.is_(True))).all():
        if u.phone:
            out.append((Channel.SMS.value, u.phone))
    if s.pastor_phone and not any(p == s.pastor_phone for _, p in out):
        out.append((Channel.SMS.value, s.pastor_phone))
    return out


def send_validation_request(db: Session, campaign: Campaign) -> dict:
    """Émet un jeton et envoie le lien au pasteur. Retourne le lien (utile si aucun canal n'est configuré)."""
    raw = campaign_engine.issue_approval_token(db, campaign)
    link = f"{get_settings().base_url.rstrip('/')}/valider/{raw}"
    body = validation_message(campaign, link)
    delivered = []
    for channel, to in pastor_contacts(db):
        result = get_gateway(channel).send(OutboundMessage(channel=channel, to=to, body=body, metadata={"kind": "validation", "campaign": campaign.ref}))
        delivered.append({"channel": channel, "to": to[-4:].rjust(len(to), "•"), "ok": result.ok, "error": result.error})
    audit.log(db, "SYSTEME", "VALIDATION_LINK_SENT", "campaign", campaign.ref, {"delivered": delivered})
    return {"link": link, "delivered": delivered}


def notify_pastor_of_pending(db: Session) -> list[str]:
    """Pour chaque campagne prête sans lien de validation actif, en envoyer un."""
    sent = []
    for c in db.scalars(select(Campaign).where(Campaign.status == CampaignStatus.READY_FOR_REVIEW.value)).all():
        active = db.scalar(select(ApprovalToken).where(ApprovalToken.campaign_ref == c.ref, ApprovalToken.used_at.is_(None)))
        if active is None:
            send_validation_request(db, c)
            sent.append(c.ref)
    return sent
