"""Contrôles pré-envoi (section 17 du cahier des charges).

Chaque contrôle produit une ligne du rapport. Une anomalie de niveau BLOCK
empêche la campagne d'être présentée à la validation.
"""
from __future__ import annotations

import math
from datetime import timedelta
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Campaign, Channel, Event, Group, Member, utcnow
from . import members as members_service
from . import personalization

SMS_SEGMENT_GSM = 160
SMS_SEGMENT_MULTIPART = 153
SMS_SEGMENT_UCS2 = 70
SMS_SEGMENT_UCS2_MULTIPART = 67


@dataclass
class Check:
    code: str
    label: str
    ok: bool
    level: str = "BLOCK"  # BLOCK | WARN | INFO
    detail: str = ""

    def as_dict(self) -> dict:
        return {"code": self.code, "label": self.label, "ok": self.ok, "level": self.level, "detail": self.detail}


@dataclass
class PreflightReport:
    checks: list[Check] = field(default_factory=list)
    recipients: list[Member] = field(default_factory=list)
    excluded: list[dict] = field(default_factory=list)
    estimated_cost_eur: float = 0.0
    sms_segments: int = 0

    @property
    def blocked(self) -> bool:
        return any(not c.ok and c.level == "BLOCK" for c in self.checks)

    @property
    def warnings(self) -> list[Check]:
        return [c for c in self.checks if not c.ok and c.level == "WARN"]

    def as_dict(self) -> dict:
        return {
            "blocked": self.blocked,
            "checks": [c.as_dict() for c in self.checks],
            "recipient_count": len(self.recipients),
            "excluded": self.excluded,
            "estimated_cost_eur": round(self.estimated_cost_eur, 2),
            "sms_segments": self.sms_segments,
            "generated_at": utcnow().isoformat(),
        }


def sms_segments(text: str) -> int:
    if not text:
        return 0
    is_unicode = any(ord(ch) > 127 for ch in text)
    single, multi = (SMS_SEGMENT_UCS2, SMS_SEGMENT_UCS2_MULTIPART) if is_unicode else (SMS_SEGMENT_GSM, SMS_SEGMENT_MULTIPART)
    return 1 if len(text) <= single else math.ceil(len(text) / multi)


def run_preflight(db: Session, campaign: Campaign) -> PreflightReport:
    settings = get_settings()
    report = PreflightReport()
    checks = report.checks
    channel = campaign.channel

    # ☑ canal
    checks.append(Check("channel", "Canal correct", channel in (Channel.SMS.value, Channel.WHATSAPP.value, Channel.EMAIL.value), detail=channel))

    # ☑ groupe correct
    missing_groups = [gid for gid in (campaign.group_ids or []) if db.get(Group, gid) is None]
    has_target = bool(campaign.group_ids) or bool(campaign.explicit_member_ids)
    checks.append(Check("group", "Groupe correct", has_target and not missing_groups, detail="Aucun groupe ciblé" if not has_target else (f"Groupes introuvables : {missing_groups}" if missing_groups else "")))

    # ☑ message correct
    msg = (campaign.message or "").strip()
    checks.append(Check("message", "Message non vide", bool(msg)))
    if channel == Channel.EMAIL.value:
        checks.append(Check("subject", "Objet de l'e-mail renseigné", bool((campaign.subject or "").strip())))
    if channel == Channel.SMS.value and msg:
        segs = sms_segments(personalization.preview_render(msg, campaign.event))
        report.sms_segments = segs
        checks.append(Check("sms_length", "Longueur SMS raisonnable", segs <= 3, level="WARN", detail=f"{segs} segment(s)"))

    # ☑ variables
    unknown = personalization.unknown_variables(msg)
    checks.append(Check("variables_known", "Variables reconnues", not unknown, detail=f"Inconnues : {', '.join('{' + v + '}' for v in unknown)}" if unknown else ", ".join("{" + v + "}" for v in personalization.extract_variables(msg)) or "aucune"))
    ev_ctx = personalization.event_context(campaign.event)
    needs_event = [v for v in personalization.extract_variables(msg) if v in ("DATE", "HEURE", "LIEU", "EVENEMENT")]
    missing_ev = [v for v in needs_event if not ev_ctx.get(v)]
    checks.append(Check("variables_event", "Variables d'événement résolues", not missing_ev, detail=f"Manquantes : {', '.join('{' + v + '}' for v in missing_ev)}" if missing_ev else ""))

    # ☑ date / heure
    now = utcnow()
    if campaign.send_at is None:
        checks.append(Check("date", "Date d'envoi définie", False, detail="Aucune date d'envoi"))
    else:
        checks.append(Check("date", "Date correcte", campaign.send_at >= now - timedelta(minutes=5), detail="La date d'envoi est dans le passé" if campaign.send_at < now else campaign.send_at.strftime("%d/%m/%Y")))
        checks.append(Check("time", "Heure correcte", 6 <= campaign.send_at.hour <= 22, level="WARN", detail="Envoi en dehors de 6h–22h" if not (6 <= campaign.send_at.hour <= 22) else campaign.send_at.strftime("%H:%M")))
        if campaign.event is not None and campaign.send_at > campaign.event.starts_at and "remerci" not in (campaign.name + campaign.objective).lower():
            checks.append(Check("after_event", "Envoi avant l'événement", False, level="WARN", detail="La date d'envoi est postérieure à l'événement"))

    # ☑ destinataires, consentement, doublons, numéros
    audience = members_service.resolve_audience(db, campaign.group_ids or [], campaign.explicit_member_ids or [], campaign.excluded_member_ids or [])
    valid: list[Member] = []
    seen_contacts: set[str] = set()
    no_consent = invalid_contact = duplicates = missing_var = 0
    for m in audience:
        contact = m.contact_for(channel)
        if not m.has_consent(channel):
            no_consent += 1
            report.excluded.append({"member_id": m.id, "name": m.full_name, "reason": "Pas de consentement " + channel})
            continue
        contact_ok = members_service.is_valid_email(contact) if channel == Channel.EMAIL.value else members_service.is_valid_phone(contact)
        if not contact_ok:
            invalid_contact += 1
            report.excluded.append({"member_id": m.id, "name": m.full_name, "reason": "Coordonnée invalide ou absente"})
            continue
        key = contact.lower()
        if key in seen_contacts:
            duplicates += 1
            report.excluded.append({"member_id": m.id, "name": m.full_name, "reason": "Doublon (même coordonnée)"})
            continue
        ctx = {**personalization.member_context(m), **ev_ctx}
        if personalization.missing_variables(msg, ctx):
            missing_var += 1
            report.excluded.append({"member_id": m.id, "name": m.full_name, "reason": "Variable non résolvable : " + ", ".join(personalization.missing_variables(msg, ctx))})
            continue
        seen_contacts.add(key)
        valid.append(m)

    for mid in campaign.excluded_member_ids or []:
        m = db.get(Member, mid)
        if m:
            report.excluded.append({"member_id": m.id, "name": m.full_name, "reason": "Exclu manuellement"})

    report.recipients = valid
    checks.append(Check("recipients", "Destinataires valides", len(valid) > 0, detail=f"{len(valid)} destinataire(s) valide(s) sur {len(audience)}"))
    checks.append(Check("consent", "Consentement vérifié", True, level="INFO" if no_consent == 0 else "WARN", detail=f"{no_consent} personne(s) sans consentement {channel} exclue(s)" if no_consent else "Tous les destinataires ont donné leur consentement"))
    if no_consent:
        checks[-1].ok = False
    checks.append(Check("duplicates", "Doublons", duplicates == 0, level="WARN", detail=f"{duplicates} doublon(s) retiré(s)" if duplicates else "Aucun doublon"))
    checks.append(Check("contacts", "Numéros / adresses corrects", invalid_contact == 0, level="WARN", detail=f"{invalid_contact} coordonnée(s) invalide(s) exclue(s)" if invalid_contact else ""))
    checks.append(Check("variables_members", "Variables membres résolues", missing_var == 0, level="WARN", detail=f"{missing_var} membre(s) exclu(s) faute de donnée" if missing_var else ""))

    # ☑ coût estimé
    if channel == Channel.SMS.value:
        report.estimated_cost_eur = len(valid) * max(report.sms_segments, 1) * settings.sms_unit_cost_eur
    elif channel == Channel.WHATSAPP.value:
        report.estimated_cost_eur = len(valid) * 0.05
    return report


def apply_report(campaign: Campaign, report: PreflightReport) -> None:
    campaign.preflight_report = report.as_dict()
    campaign.recipient_count = len(report.recipients)
    campaign.estimated_cost_eur = round(report.estimated_cost_eur, 2)
    campaign.requires_double_confirmation = campaign.is_sensitive or len(report.recipients) >= get_settings().double_confirmation_threshold
