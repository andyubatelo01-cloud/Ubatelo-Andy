"""Événements et calendrier de communication (agent EVENTS)."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..models import Attendance, Event, Group, Member, utcnow

# Calendrier de communication standard : (étiquette, type de message, décalage par rapport à l'événement)
COMMUNICATION_PLAN: list[tuple[str, str, timedelta]] = [
    ("J-14", "invitation", timedelta(days=-14)),
    ("J-7", "rappel", timedelta(days=-7)),
    ("J-3", "motivation", timedelta(days=-3)),
    ("J-1", "rappel", timedelta(days=-1)),
    ("H-3", "pratique", timedelta(hours=-3)),
    ("Après événement", "remerciement", timedelta(hours=+20)),
]

SUNDAY_PLAN: list[tuple[str, str, timedelta]] = [
    ("J-4", "invitation", timedelta(days=-4)),  # mercredi
    ("J-1", "rappel", timedelta(days=-1)),  # samedi
    ("H-3", "pratique", timedelta(hours=-3)),
    ("Après-culte", "remerciement", timedelta(hours=+6)),
]


def communication_calendar(event: Event, now: datetime | None = None, plan=None) -> list[dict]:
    """Retourne les étapes de communication encore à venir, avec leur date d'envoi (9h par défaut)."""
    now = now or utcnow()
    plan = plan or (SUNDAY_PLAN if event.is_recurring_sunday else COMMUNICATION_PLAN)
    steps = []
    for label, kind, offset in plan:
        send_at = event.starts_at + offset
        if abs(offset) >= timedelta(days=1):
            send_at = send_at.replace(hour=9, minute=0, second=0, microsecond=0)
        steps.append({"label": label, "kind": kind, "send_at": send_at, "future": send_at > now})
    return steps


def upcoming_events(db: Session, days: int = 14, now: datetime | None = None) -> list[Event]:
    now = now or utcnow()
    return db.scalars(select(Event).where(Event.starts_at >= now, Event.starts_at <= now + timedelta(days=days)).order_by(Event.starts_at)).all()


def next_sunday_service(db: Session, now: datetime | None = None) -> Event | None:
    now = now or utcnow()
    return db.scalar(select(Event).where(Event.is_recurring_sunday.is_(True), Event.starts_at >= now).order_by(Event.starts_at))


def find_event(db: Session, text: str, now: datetime | None = None) -> Event | None:
    """Recherche souple par mots du nom (ex. « retraite de prière »)."""
    now = now or utcnow()
    words = [w for w in text.lower().split() if len(w) > 3]
    best, best_score = None, 0
    for ev in db.scalars(select(Event).where(Event.starts_at >= now - timedelta(days=1)).order_by(Event.starts_at)).all():
        name = ev.name.lower()
        score = sum(1 for w in words if w in name)
        if score > best_score:
            best, best_score = ev, score
    return best


def missing_information(event: Event) -> list[str]:
    missing = []
    if not event.location:
        missing.append("lieu")
    if not event.responsible:
        missing.append("responsable de l'événement")
    if event.registration_required and event.capacity is None:
        missing.append("capacité (inscriptions obligatoires)")
    if not event.audience_group_id:
        missing.append("public concerné (groupe)")
    return missing


def create_event(db: Session, actor: str, **fields) -> Event:
    event = Event(**fields)
    db.add(event)
    db.flush()
    audit.log(db, actor, "EVENT_CREATED", "event", str(event.id), {"name": event.name, "starts_at": event.starts_at.isoformat()})
    return event


def set_attendance(db: Session, event: Event, member: Member, *, registered: bool | None = None, confirmed: bool | None = None, present: bool | None = None, actor: str = "EVENTS") -> Attendance:
    att = next((a for a in member.attendances if a.event_id == event.id), None)
    if att is None:
        att = Attendance(member=member, event=event)
        member.attendances.append(att)
        if att not in event.attendances:
            event.attendances.append(att)
    if registered is not None:
        att.registered = registered
    if confirmed is not None:
        att.confirmed = confirmed
    if present is not None:
        att.present = present
        if present and sum(1 for a in member.attendances if a.present) >= 2:
            member.is_new = False  # deux présences enregistrées : la personne n'est plus « à intégrer »
    att.recorded_at = utcnow()
    db.flush()
    return att


def campaigns_for_event(db: Session, event: Event) -> list:
    """Campagnes liées à un événement (requête directe : évite une collection périmée en session)."""
    from ..models import Campaign

    return db.scalars(select(Campaign).where(Campaign.event_id == event.id).order_by(Campaign.send_at)).all()


def event_stats(event: Event) -> dict:
    atts = event.attendances
    return {
        "inscrits": sum(1 for a in atts if a.registered),
        "confirmes": sum(1 for a in atts if a.confirmed),
        "presents": sum(1 for a in atts if a.present),
        "absents": sum(1 for a in atts if a.present is False),
        "capacite": event.capacity,
    }


def responsibles_missing(event: Event) -> list[str]:
    out = []
    if not event.responsible_welcome:
        out.append("accueil")
    if not event.responsible_media:
        out.append("média")
    if not event.responsible_intercession:
        out.append("intercession")
    return out


def group_name(db: Session, group_id: int | None) -> str:
    if not group_id:
        return "Membres"
    g = db.get(Group, group_id)
    return g.name if g else "Membres"
