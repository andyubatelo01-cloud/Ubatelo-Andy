"""Gestion des membres, des groupes et des audiences (agent MEMBRES)."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..models import Attendance, Channel, Delivery, Event, Group, Member, MemberNote, utcnow

DEFAULT_GROUPS = [
    ("Membres", "Tous les membres de la communauté"),
    ("Nouveaux membres", "Personnes arrivées récemment, à intégrer"),
    ("Jeunesse", ""),
    ("Couples", ""),
    ("Femmes", ""),
    ("Hommes", ""),
    ("Responsables", "Responsables de ministères et de départements"),
    ("Intercession", ""),
    ("Chorale", ""),
    ("Média", ""),
    ("Accueil", ""),
    ("Évangélisation", ""),
    ("Enfants", "Parents des enfants (les enfants ne sont jamais contactés directement)"),
]

PHONE_RE = re.compile(r"^\+[1-9]\d{7,14}$")  # format international E.164
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "groupe"


def normalize_phone(raw: str) -> str:
    """Normalise un numéro français ou international en E.164 (sans deviner l'indicatif)."""
    if not raw:
        return ""
    digits = re.sub(r"[\s().-]", "", raw)
    digits = re.sub(r"[\u200e\u200f\u202a-\u202e\u200b]", "", digits)  # marques de direction (copie WhatsApp)
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    if digits.startswith("0") and len(digits) == 10:  # numéro français national
        digits = "+33" + digits[1:]
    elif re.fullmatch(r"[67]\d{8}", digits):  # mobile français saisi sans le 0
        digits = "+33" + digits
    elif re.fullmatch(r"33[1-9]\d{8}", digits):  # indicatif sans le +
        digits = "+" + digits
    return digits


def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone or ""))


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def ensure_default_groups(db: Session) -> None:
    existing = {g.slug for g in db.scalars(select(Group)).all()}
    for name, desc in DEFAULT_GROUPS:
        slug = slugify(name)
        if slug not in existing:
            db.add(Group(name=name, slug=slug, description=desc, is_system=True))
    db.flush()


def get_group_by_name(db: Session, name: str) -> Group | None:
    slug = slugify(name)
    return db.scalar(select(Group).where(Group.slug == slug))


def create_group(db: Session, name: str, description: str = "", dynamic_rule: dict | None = None, actor: str = "MEMBRES") -> Group:
    group = Group(name=name.strip(), slug=slugify(name), description=description, dynamic_rule=dynamic_rule)
    db.add(group)
    db.flush()
    audit.log(db, actor, "GROUP_CREATED", "group", group.slug, {"name": group.name, "dynamic": bool(dynamic_rule)})
    return group


def evaluate_dynamic_rule(db: Session, rule: dict) -> list[Member]:
    """Règles supportées :
    - active_days: N  → a participé à au moins un événement dans les N derniers jours
    - consent: SMS|WHATSAPP|EMAIL
    - joined_within_days: N
    - not_confirmed_event_id: ID → inscrits ou public d'un événement sans confirmation
    - absent_since_days: N → aucune participation depuis N jours (mais actif)
    """
    members = db.scalars(select(Member).where(Member.is_active.is_(True), Member.anonymized.is_(False))).all()
    now = utcnow()
    result = []
    for m in members:
        ok = True
        if "consent" in rule and not m.has_consent(rule["consent"]):
            ok = False
        if ok and "active_days" in rule:
            since = now - timedelta(days=int(rule["active_days"]))
            ok = any(a.present and a.event and a.event.starts_at >= since for a in m.attendances)
        if ok and "absent_since_days" in rule:
            since = now - timedelta(days=int(rule["absent_since_days"]))
            ok = not any(a.present and a.event and a.event.starts_at >= since for a in m.attendances)
        if ok and "joined_within_days" in rule:
            since = now - timedelta(days=int(rule["joined_within_days"]))
            ok = bool(m.joined_at and m.joined_at >= since)
        if ok and "not_confirmed_event_id" in rule:
            eid = int(rule["not_confirmed_event_id"])
            att = next((a for a in m.attendances if a.event_id == eid), None)
            ok = att is None or not att.confirmed
        if ok:
            result.append(m)
    return result


def group_members(db: Session, group: Group) -> list[Member]:
    if group.dynamic_rule:
        return evaluate_dynamic_rule(db, group.dynamic_rule)
    return [m for m in group.members if m.is_active and not m.anonymized]


def resolve_audience(
    db: Session,
    group_ids: list[int],
    explicit_member_ids: list[int] | None = None,
    excluded_member_ids: list[int] | None = None,
) -> list[Member]:
    """Union des groupes + membres explicites, moins les exclusions. Dédoublonné par identifiant."""
    seen: dict[int, Member] = {}
    for gid in group_ids or []:
        group = db.get(Group, gid)
        if group is None:
            continue
        for m in group_members(db, group):
            seen.setdefault(m.id, m)
    for mid in explicit_member_ids or []:
        m = db.get(Member, mid)
        if m is not None and m.is_active and not m.anonymized:
            seen.setdefault(m.id, m)
    for mid in excluded_member_ids or []:
        seen.pop(mid, None)
    return list(seen.values())


def record_consent(db: Session, member: Member, sms: bool | None = None, whatsapp: bool | None = None, email: bool | None = None, actor: str = "MEMBRES") -> None:
    if sms is not None:
        member.consent_sms = sms
    if whatsapp is not None:
        member.consent_whatsapp = whatsapp
    if email is not None:
        member.consent_email = email
    member.consent_recorded_at = utcnow()
    if any(v for v in (sms, whatsapp, email)):
        member.unsubscribed = False
    audit.log(db, actor, "CONSENT_UPDATED", "member", str(member.id), {"sms": member.consent_sms, "whatsapp": member.consent_whatsapp, "email": member.consent_email})


def unsubscribe(db: Session, member: Member, channel: str | None = None, source: str = "STOP") -> None:
    """Désinscription : un mot-clé STOP retire le consentement du canal (ou de tous)."""
    if channel in (None, "", "ALL"):
        member.consent_sms = member.consent_whatsapp = member.consent_email = False
        member.unsubscribed = True
    elif channel == Channel.SMS.value:
        member.consent_sms = False
    elif channel == Channel.WHATSAPP.value:
        member.consent_whatsapp = False
    elif channel == Channel.EMAIL.value:
        member.consent_email = False
    member.consent_recorded_at = utcnow()
    audit.log(db, "SYSTEME", "MEMBER_UNSUBSCRIBED", "member", str(member.id), {"channel": channel or "ALL", "source": source})


def find_member_by_contact(db: Session, contact: str) -> Member | None:
    contact = normalize_phone(contact.replace("whatsapp:", "")) if "@" not in contact else contact.strip().lower()
    stmt = select(Member).where((Member.phone == contact) | (Member.whatsapp == contact) | (Member.email == contact))
    return db.scalar(stmt)


def export_member_data(db: Session, member: Member) -> dict:
    """Droit d'accès / portabilité : export complet des données d'un membre."""
    return {
        "membre": {
            "id": member.id,
            "prenom": member.first_name,
            "nom": member.last_name,
            "telephone": member.phone,
            "email": member.email,
            "whatsapp": member.whatsapp,
            "responsabilite": member.responsibility,
            "date_arrivee": member.joined_at.isoformat() if member.joined_at else None,
            "anniversaire": member.birthday,
            "canal_prefere": member.preferred_channel,
            "consentements": {"sms": member.consent_sms, "whatsapp": member.consent_whatsapp, "email": member.consent_email, "enregistre_le": member.consent_recorded_at.isoformat() if member.consent_recorded_at else None},
            "desinscrit": member.unsubscribed,
            "statut": "actif" if member.is_active else "inactif",
            "groupes": [g.name for g in member.groups],
            "notes_administratives": member.admin_notes,
        },
        "participations": [
            {"evenement": a.event.name, "date": a.event.starts_at.isoformat(), "inscrit": a.registered, "confirme": a.confirmed, "present": a.present}
            for a in member.attendances
        ],
        "notes": [{"date": n.created_at.isoformat(), "contenu": n.content} for n in member.notes],
    }


def anonymize_member(db: Session, member: Member, actor: str) -> None:
    """Droit à l'effacement : suppression des données personnelles, conservation des statistiques agrégées."""
    member.first_name = "Membre"
    member.last_name = f"supprimé #{member.id}"
    member.phone = member.email = member.whatsapp = member.responsibility = member.birthday = member.admin_notes = ""
    member.consent_sms = member.consent_whatsapp = member.consent_email = False
    member.unsubscribed = True
    member.is_active = False
    member.anonymized = True
    member.groups = []
    for note in list(member.notes):
        db.delete(note)
    audit.log(db, actor, "MEMBER_ANONYMIZED", "member", str(member.id))


def has_history(db: Session, member: Member) -> bool:
    """Un membre a un historique s'il a déjà reçu un message ou a une participation enregistrée."""
    if any(a.registered or a.confirmed or a.present for a in member.attendances):
        return True
    return db.scalar(select(Delivery.id).where(Delivery.member_id == member.id).limit(1)) is not None


def remove_member(db: Session, member: Member, actor: str) -> str:
    """Supprime une fiche : suppression définitive si elle n'a aucun historique (mauvaise entrée, doublon
    d'import), sinon anonymisation RGPD (statistiques agrégées conservées). Retourne « supprime » ou « anonymise »."""
    if has_history(db, member):
        anonymize_member(db, member, actor)
        return "anonymise"
    audit.log(db, actor, "MEMBER_DELETED", "member", str(member.id), {"name": member.full_name})
    db.delete(member)
    return "supprime"


def add_note(db: Session, member: Member, content: str, author_id: int | None, actor: str) -> MemberNote:
    note = MemberNote(member_id=member.id, author_id=author_id, content=content.strip())
    db.add(note)
    db.flush()
    audit.log(db, actor, "MEMBER_NOTE_ADDED", "member", str(member.id))
    return note


def last_participation(member: Member) -> Attendance | None:
    present = [a for a in member.attendances if a.present]
    if not present:
        return None
    return max(present, key=lambda a: a.event.starts_at)


def absent_members(db: Session, days: int = 30) -> list[tuple[Member, datetime | None]]:
    """Membres actifs sans présence enregistrée depuis N jours, à partir des données disponibles."""
    since = utcnow() - timedelta(days=days)
    out = []
    for m in db.scalars(select(Member).where(Member.is_active.is_(True), Member.anonymized.is_(False))).all():
        last = last_participation(m)
        if last is None or last.event.starts_at < since:
            out.append((m, last.event.starts_at if last else None))
    return out


def upcoming_birthdays(db: Session, within_days: int = 7) -> list[tuple[Member, int]]:
    today = utcnow().date()
    out = []
    for m in db.scalars(select(Member).where(Member.is_active.is_(True), Member.birthday != "")).all():
        try:
            day, month = (int(x) for x in m.birthday.split("-"))
            candidate = today.replace(month=month, day=day)
        except ValueError:
            continue
        if candidate < today:
            candidate = candidate.replace(year=today.year + 1)
        delta = (candidate - today).days
        if delta <= within_days:
            out.append((m, delta))
    return sorted(out, key=lambda t: t[1])


def members_of_event(db: Session, event: Event) -> list[Member]:
    if event.audience_group_id:
        group = db.get(Group, event.audience_group_id)
        if group:
            return group_members(db, group)
    all_members = get_group_by_name(db, "Membres")
    return group_members(db, all_members) if all_members else []
