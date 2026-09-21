"""Moteur de campagnes : machine à états, validation du pasteur, envoi contrôlé.

Invariant fondamental (vérifié par les tests) :
    AUCUN message collectif ne part sans une validation explicite d'un utilisateur
    ayant le rôle PASTEUR. Une absence de réponse n'est jamais une validation.

Cycle de vie :
    DRAFT → READY_FOR_REVIEW → APPROVED → SCHEDULED → SENDING → SENT
    Annulation possible : DRAFT / READY_FOR_REVIEW / BLOCKED / SCHEDULED → CANCELLED
    Blocage : READY_FOR_REVIEW ← BLOCKED (contrôles pré-envoi) → DRAFT après modification
    Expiration : READY_FOR_REVIEW / BLOCKED → EXPIRED si la date d'envoi passe sans validation
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import audit
from ..channels import OutboundMessage, get_gateway
from ..config import get_settings
from ..models import ApprovalToken, Campaign, CampaignStatus, Channel, Delivery, Priority, Role, User, utcnow
from ..security import content_fingerprint, hash_token, new_approval_token
from . import personalization, preflight
from .members import resolve_audience

CONFIRMATION_PHRASE = "CONFIRMER L'ENVOI"

# Transitions autorisées (état source → états cibles)
TRANSITIONS: dict[str, set[str]] = {
    CampaignStatus.DRAFT.value: {CampaignStatus.READY_FOR_REVIEW.value, CampaignStatus.BLOCKED.value, CampaignStatus.CANCELLED.value, CampaignStatus.EXPIRED.value},
    CampaignStatus.READY_FOR_REVIEW.value: {CampaignStatus.APPROVED.value, CampaignStatus.DRAFT.value, CampaignStatus.BLOCKED.value, CampaignStatus.CANCELLED.value, CampaignStatus.EXPIRED.value},
    CampaignStatus.BLOCKED.value: {CampaignStatus.DRAFT.value, CampaignStatus.READY_FOR_REVIEW.value, CampaignStatus.CANCELLED.value, CampaignStatus.EXPIRED.value},
    CampaignStatus.APPROVED.value: {CampaignStatus.SCHEDULED.value, CampaignStatus.SENDING.value, CampaignStatus.DRAFT.value, CampaignStatus.CANCELLED.value},
    CampaignStatus.SCHEDULED.value: {CampaignStatus.SENDING.value, CampaignStatus.CANCELLED.value, CampaignStatus.DRAFT.value},
    CampaignStatus.SENDING.value: {CampaignStatus.SENT.value, CampaignStatus.FAILED.value},
    CampaignStatus.SENT.value: set(),
    CampaignStatus.FAILED.value: {CampaignStatus.DRAFT.value},
    CampaignStatus.CANCELLED.value: set(),
    CampaignStatus.EXPIRED.value: set(),
}

CANCELLABLE = {CampaignStatus.DRAFT.value, CampaignStatus.READY_FOR_REVIEW.value, CampaignStatus.BLOCKED.value, CampaignStatus.APPROVED.value, CampaignStatus.SCHEDULED.value}
EDITABLE = {CampaignStatus.DRAFT.value, CampaignStatus.READY_FOR_REVIEW.value, CampaignStatus.BLOCKED.value, CampaignStatus.APPROVED.value, CampaignStatus.SCHEDULED.value, CampaignStatus.FAILED.value}


class CampaignError(Exception):
    """Erreur métier lisible par le pasteur."""


class ApprovalRequired(CampaignError):
    """Levée si l'on tente d'envoyer une campagne non validée."""


# ────────────────────────────── Création & édition ──────────────────────────────


def next_ref(db: Session, year: int | None = None) -> str:
    year = year or utcnow().year
    prefix = f"CAM-{year}-"
    count = db.scalar(select(func.count()).select_from(Campaign).where(Campaign.ref.like(prefix + "%"))) or 0
    return f"{prefix}{count + 1:03d}"


def fingerprint(campaign: Campaign) -> str:
    return content_fingerprint(
        campaign.message, campaign.subject, campaign.channel, sorted(campaign.group_ids or []),
        sorted(campaign.explicit_member_ids or []), sorted(campaign.excluded_member_ids or []),
        campaign.send_at.isoformat() if campaign.send_at else None, campaign.event_id,
    )


def create_campaign(
    db: Session,
    *,
    name: str,
    message: str,
    channel: str = Channel.SMS.value,
    send_at: datetime | None = None,
    group_ids: list[int] | None = None,
    explicit_member_ids: list[int] | None = None,
    excluded_member_ids: list[int] | None = None,
    objective: str = "",
    style: str = "chaleureux",
    subject: str = "",
    event_id: int | None = None,
    automation_id: int | None = None,
    is_sensitive: bool = False,
    created_by: str = "DIRECTEUR IA",
) -> Campaign:
    campaign = Campaign(
        ref=next_ref(db), name=name.strip(), objective=objective, channel=channel, style=style, message=message, subject=subject,
        send_at=send_at, group_ids=list(group_ids or []), explicit_member_ids=list(explicit_member_ids or []),
        excluded_member_ids=list(excluded_member_ids or []), event_id=event_id, automation_id=automation_id,
        is_sensitive=is_sensitive, created_by=created_by, modified_by=created_by, status=CampaignStatus.DRAFT.value,
    )
    db.add(campaign)
    db.flush()
    campaign.content_hash = fingerprint(campaign)
    audit.log(db, created_by, "CAMPAIGN_CREATED", "campaign", campaign.ref, {"name": campaign.name, "channel": channel})
    return campaign


def _transition(db: Session, campaign: Campaign, target: str, actor: str, details: dict | None = None) -> None:
    if target not in TRANSITIONS.get(campaign.status, set()):
        raise CampaignError(f"Transition interdite : {campaign.status} → {target}")
    previous = campaign.status
    campaign.status = target
    campaign.updated_at = utcnow()
    audit.log(db, actor, "CAMPAIGN_STATUS", "campaign", campaign.ref, {"from": previous, "to": target, **(details or {})})


def update_campaign(db: Session, campaign: Campaign, actor: str, **changes) -> Campaign:
    """Toute modification invalide une validation antérieure : retour en DRAFT."""
    if campaign.status not in EDITABLE:
        raise CampaignError(f"Campagne {campaign.ref} non modifiable (statut {campaign.status})")
    allowed = {"name", "objective", "message", "subject", "channel", "style", "send_at", "group_ids", "explicit_member_ids", "excluded_member_ids", "event_id", "is_sensitive"}
    applied = {}
    for key, value in changes.items():
        if key in allowed and value is not None:
            setattr(campaign, key, value)
            applied[key] = value if key != "message" else value[:80]
    campaign.modified_by = actor
    new_hash = fingerprint(campaign)
    if campaign.status != CampaignStatus.DRAFT.value:
        # Une campagne validée puis modifiée redevient un brouillon : la validation ne vaut que pour le contenu validé.
        _transition(db, campaign, CampaignStatus.DRAFT.value, actor, {"reason": "modification après préparation"})
    campaign.approved_by, campaign.approved_at, campaign.approved_hash = "", None, ""
    campaign.pending_confirmation, campaign.confirmed_at = False, None
    campaign.content_hash = new_hash
    _invalidate_tokens(db, campaign)
    audit.log(db, actor, "CAMPAIGN_MODIFIED", "campaign", campaign.ref, {"fields": sorted(applied)})
    return campaign


# ────────────────────────────── Contrôle & mise en revue ──────────────────────────────


def submit_for_review(db: Session, campaign: Campaign, actor: str) -> preflight.PreflightReport:
    """Exécute les contrôles ; la campagne passe en READY_FOR_REVIEW ou BLOCKED."""
    if campaign.status not in (CampaignStatus.DRAFT.value, CampaignStatus.BLOCKED.value, CampaignStatus.READY_FOR_REVIEW.value):
        raise CampaignError(f"Campagne {campaign.ref} : contrôle impossible au statut {campaign.status}")
    report = preflight.run_preflight(db, campaign)
    preflight.apply_report(campaign, report)
    campaign.content_hash = fingerprint(campaign)
    if report.blocked:
        if campaign.status != CampaignStatus.BLOCKED.value:
            _transition(db, campaign, CampaignStatus.BLOCKED.value, actor, {"anomalies": [c.code for c in report.checks if not c.ok and c.level == "BLOCK"]})
        audit.notify(db, Priority.A_TRAITER, f"Campagne {campaign.ref} bloquée", "; ".join(f"{c.label} : {c.detail}" for c in report.checks if not c.ok and c.level == "BLOCK"), f"/campagnes/{campaign.ref}")
    else:
        if campaign.status != CampaignStatus.READY_FOR_REVIEW.value:
            _transition(db, campaign, CampaignStatus.READY_FOR_REVIEW.value, actor)
        audit.notify(db, Priority.A_VALIDER, f"Campagne « {campaign.name} » prête à valider", f"{campaign.recipient_count} destinataire(s) · {campaign.channel}", f"/campagnes/{campaign.ref}")
    return report


def preview(db: Session, campaign: Campaign) -> dict:
    """APERÇU DE LA CAMPAGNE présenté au pasteur avant toute validation."""
    report = campaign.preflight_report or preflight.run_preflight(db, campaign).as_dict()
    anomalies = [c for c in report["checks"] if not c["ok"]]
    groups = []
    from ..models import Group  # import local pour éviter un cycle

    for gid in campaign.group_ids or []:
        g = db.get(Group, gid)
        if g:
            groups.append(g.name)
    return {
        "ref": campaign.ref,
        "nom": campaign.name,
        "objectif": campaign.objective,
        "statut": campaign.status,
        "date_envoi": campaign.send_at.isoformat() if campaign.send_at else None,
        "date_envoi_texte": f"{personalization.format_date_fr(campaign.send_at)} — {campaign.send_at.strftime('%H:%M')}" if campaign.send_at else "non définie",
        "canal": campaign.channel,
        "style": campaign.style,
        "nombre_destinataires": report.get("recipient_count", 0),
        "groupes": groups,
        "membres_cibles": len(campaign.explicit_member_ids or []),
        "message": campaign.message,
        "objet": campaign.subject,
        "apercu_rendu": personalization.preview_render(campaign.message, campaign.event),
        "variables": ["{" + v + "}" for v in personalization.extract_variables(campaign.message)],
        "exclus": report.get("excluded", []),
        "cout_estime_eur": report.get("estimated_cost_eur", 0),
        "segments_sms": report.get("sms_segments", 0),
        "anomalies": anomalies,
        "bloquee": report.get("blocked", False),
        "double_validation": campaign.requires_double_confirmation,
        "confirmation_en_attente": campaign.pending_confirmation,
        "evenement": campaign.event.name if campaign.event else None,
        "cree_par": campaign.created_by,
        "modifie_par": campaign.modified_by,
        "valide_par": campaign.approved_by or None,
        "valide_le": campaign.approved_at.isoformat() if campaign.approved_at else None,
        "actions": {"valider": "🟢 VALIDER ET ENVOYER", "modifier": "🟡 MODIFIER", "annuler": "🔴 ANNULER"},
    }


# ────────────────────────────── Validation du pasteur ──────────────────────────────


def _require_pastor(user: User) -> None:
    if user is None or user.role != Role.PASTEUR.value or not user.is_active:
        raise ApprovalRequired("Seul le pasteur (rôle PASTEUR) peut valider un envoi collectif.")


def approve(db: Session, campaign: Campaign, user: User, expected_hash: str | None = None) -> Campaign:
    """Validation explicite. Si la campagne exige une double validation, elle reste en
    READY_FOR_REVIEW avec `pending_confirmation` jusqu'à `confirm()`."""
    _require_pastor(user)
    if campaign.status != CampaignStatus.READY_FOR_REVIEW.value:
        raise CampaignError(f"Campagne {campaign.ref} non validable (statut {campaign.status}). Relancez les contrôles.")
    current = fingerprint(campaign)
    if expected_hash and expected_hash != current:
        raise CampaignError("La campagne a été modifiée depuis l'aperçu présenté. Veuillez la relire avant de valider.")
    report = preflight.run_preflight(db, campaign)
    preflight.apply_report(campaign, report)
    if report.blocked:
        _transition(db, campaign, CampaignStatus.BLOCKED.value, user.name)
        raise CampaignError("Envoi bloqué : " + "; ".join(f"{c.label} — {c.detail}" for c in report.checks if not c.ok and c.level == "BLOCK"))
    if campaign.requires_double_confirmation and not campaign.pending_confirmation:
        campaign.pending_confirmation = True
        audit.log(db, user.name, "CAMPAIGN_APPROVAL_STEP1", "campaign", campaign.ref, {"recipients": campaign.recipient_count})
        return campaign
    if campaign.requires_double_confirmation and campaign.pending_confirmation and campaign.confirmed_at is None:
        raise CampaignError(f"Double validation requise : répondez exactement « {CONFIRMATION_PHRASE} ».")
    return _finalize_approval(db, campaign, user, current)


def confirm(db: Session, campaign: Campaign, user: User, phrase: str) -> Campaign:
    """Seconde validation : le pasteur doit répondre exactement « CONFIRMER L'ENVOI »."""
    _require_pastor(user)
    if not campaign.pending_confirmation:
        raise CampaignError("Aucune confirmation n'est attendue pour cette campagne.")
    if (phrase or "").strip().upper().replace("’", "'") != CONFIRMATION_PHRASE:
        audit.log(db, user.name, "CAMPAIGN_CONFIRMATION_REJECTED", "campaign", campaign.ref, {"received": (phrase or "")[:40]})
        raise CampaignError(f"Confirmation refusée : la réponse attendue est exactement « {CONFIRMATION_PHRASE} ».")
    campaign.confirmed_at = utcnow()
    return _finalize_approval(db, campaign, user, fingerprint(campaign))


def _finalize_approval(db: Session, campaign: Campaign, user: User, content_hash: str) -> Campaign:
    campaign.approved_by = user.name
    campaign.approved_at = utcnow()
    campaign.approved_hash = content_hash
    campaign.pending_confirmation = False
    _transition(db, campaign, CampaignStatus.APPROVED.value, user.name, {"recipients": campaign.recipient_count, "double_validation": campaign.requires_double_confirmation})
    _invalidate_tokens(db, campaign)
    if campaign.send_at and campaign.send_at > utcnow() + timedelta(minutes=1):
        _transition(db, campaign, CampaignStatus.SCHEDULED.value, user.name, {"send_at": campaign.send_at.isoformat()})
        audit.notify(db, Priority.INFORMATION, f"Campagne {campaign.ref} programmée", f"Envoi prévu le {personalization.format_date_fr(campaign.send_at)} à {campaign.send_at.strftime('%H:%M')}")
    return campaign


def cancel(db: Session, campaign: Campaign, actor: str, reason: str = "") -> Campaign:
    if campaign.status not in CANCELLABLE:
        raise CampaignError(f"Campagne {campaign.ref} non annulable (statut {campaign.status})")
    _transition(db, campaign, CampaignStatus.CANCELLED.value, actor, {"reason": reason})
    _invalidate_tokens(db, campaign)
    return campaign


def expire_stale(db: Session, now: datetime | None = None) -> list[Campaign]:
    """Une campagne non validée dont la date d'envoi est passée EXPIRE : elle n'est jamais envoyée."""
    now = now or utcnow()
    stale = db.scalars(
        select(Campaign).where(
            Campaign.status.in_([CampaignStatus.DRAFT.value, CampaignStatus.READY_FOR_REVIEW.value, CampaignStatus.BLOCKED.value]),
            Campaign.send_at.is_not(None),
            Campaign.send_at < now - timedelta(hours=1),
        )
    ).all()
    for c in stale:
        _transition(db, c, CampaignStatus.EXPIRED.value, "SYSTEME", {"reason": "date d'envoi dépassée sans validation du pasteur"})
        audit.notify(db, Priority.INFORMATION, f"Campagne {c.ref} expirée sans envoi", "La date d'envoi est passée sans validation. Aucun message n'a été envoyé.")
    return stale


# ────────────────────────────── Jetons de validation mobile ──────────────────────────────


def issue_approval_token(db: Session, campaign: Campaign) -> str:
    raw, digest = new_approval_token()
    ttl = get_settings().approval_link_ttl_hours
    db.add(ApprovalToken(token_hash=digest, campaign_ref=campaign.ref, content_hash=fingerprint(campaign), expires_at=utcnow() + timedelta(hours=ttl)))
    db.flush()
    return raw


def resolve_approval_token(db: Session, raw: str) -> tuple[Campaign, ApprovalToken]:
    token = db.scalar(select(ApprovalToken).where(ApprovalToken.token_hash == hash_token(raw)))
    if token is None:
        raise CampaignError("Lien de validation invalide.")
    if token.used_at is not None:
        raise CampaignError("Ce lien de validation a déjà été utilisé.")
    if token.expires_at < utcnow():
        raise CampaignError("Ce lien de validation a expiré. Demandez un nouveau lien depuis le tableau de bord.")
    campaign = db.scalar(select(Campaign).where(Campaign.ref == token.campaign_ref))
    if campaign is None:
        raise CampaignError("Campagne introuvable.")
    if fingerprint(campaign) != token.content_hash:
        raise CampaignError("La campagne a été modifiée depuis l'envoi de ce lien. Relisez-la avant de valider.")
    return campaign, token


def _invalidate_tokens(db: Session, campaign: Campaign) -> None:
    for t in db.scalars(select(ApprovalToken).where(ApprovalToken.campaign_ref == campaign.ref, ApprovalToken.used_at.is_(None))).all():
        t.used_at = utcnow()


# ────────────────────────────── Envoi ──────────────────────────────


def assert_sendable(campaign: Campaign) -> None:
    """Barrière unique avant tout appel à un canal. Toute violation lève ApprovalRequired."""
    if campaign.status not in (CampaignStatus.APPROVED.value, CampaignStatus.SCHEDULED.value):
        raise ApprovalRequired(f"Campagne {campaign.ref} : statut {campaign.status}, envoi interdit.")
    if not campaign.approved_by or campaign.approved_at is None:
        raise ApprovalRequired(f"Campagne {campaign.ref} : aucune validation du pasteur enregistrée.")
    if campaign.approved_hash != fingerprint(campaign):
        raise ApprovalRequired(f"Campagne {campaign.ref} : le contenu a changé depuis la validation.")
    if campaign.requires_double_confirmation and campaign.confirmed_at is None:
        raise ApprovalRequired(f"Campagne {campaign.ref} : double validation non confirmée.")


def dispatch(db: Session, campaign: Campaign, actor: str = "SYSTEME") -> dict:
    """Envoie une campagne validée, conformément aux paramètres validés. Retourne le rapport."""
    assert_sendable(campaign)
    _transition(db, campaign, CampaignStatus.SENDING.value, actor)
    db.flush()
    gateway = get_gateway(campaign.channel)
    ev_ctx = personalization.event_context(campaign.event)
    report = preflight.run_preflight(db, campaign)  # re-vérification : consentements retirés entre-temps, etc.
    sent = failed = 0
    errors: list[str] = []
    for member in report.recipients:
        ctx = {**personalization.member_context(member), **ev_ctx}
        body = personalization.render(campaign.message, ctx)
        delivery = Delivery(campaign_id=campaign.id, member_id=member.id, channel=campaign.channel, recipient=member.contact_for(campaign.channel), rendered_message=body)
        db.add(delivery)
        result = gateway.send(OutboundMessage(channel=campaign.channel, to=delivery.recipient, body=body, subject=personalization.render(campaign.subject or "", ctx), metadata={"campaign": campaign.ref}))
        delivery.sent_at = utcnow()
        if result.ok:
            delivery.status, delivery.provider_id = "SENT", result.provider_id
            member.last_contact_at = utcnow()
            sent += 1
        else:
            delivery.status, delivery.error = "FAILED", result.error
            failed += 1
            if len(errors) < 5:
                errors.append(f"{member.full_name} : {result.error}")
    campaign.sent_at = utcnow()
    campaign.result = {"sent": sent, "failed": failed, "provider": gateway.name, "errors": errors, "excluded": len(report.excluded)}
    final = CampaignStatus.SENT.value if sent > 0 or (sent == 0 and failed == 0) else CampaignStatus.FAILED.value
    _transition(db, campaign, final, actor, {"sent": sent, "failed": failed})
    level = Priority.INFORMATION if final == CampaignStatus.SENT.value else Priority.URGENT
    audit.notify(db, level, f"Campagne {campaign.ref} : {sent} envoyé(s), {failed} échec(s)", campaign.name, f"/campagnes/{campaign.ref}")
    return campaign.result


def dispatch_due(db: Session, now: datetime | None = None) -> list[Campaign]:
    """Appelé par le planificateur : envoie les campagnes SCHEDULED/APPROVED dont l'heure est venue."""
    now = now or utcnow()
    due = db.scalars(
        select(Campaign).where(
            Campaign.status.in_([CampaignStatus.SCHEDULED.value, CampaignStatus.APPROVED.value]),
            (Campaign.send_at.is_(None)) | (Campaign.send_at <= now),
        )
    ).all()
    done = []
    for c in due:
        try:
            dispatch(db, c, actor="PLANIFICATEUR")
            done.append(c)
        except ApprovalRequired as exc:  # défense en profondeur : jamais d'envoi sans validation
            audit.log(db, "PLANIFICATEUR", "DISPATCH_REFUSED", "campaign", c.ref, {"reason": str(exc)})
    return done


def pending_review(db: Session) -> list[Campaign]:
    return db.scalars(select(Campaign).where(Campaign.status == CampaignStatus.READY_FOR_REVIEW.value).order_by(Campaign.send_at)).all()


def get_by_ref(db: Session, ref: str) -> Campaign | None:
    return db.scalar(select(Campaign).where(Campaign.ref == ref))


def recipients_for(db: Session, campaign: Campaign):
    return resolve_audience(db, campaign.group_ids or [], campaign.explicit_member_ids or [], campaign.excluded_member_ids or [])
