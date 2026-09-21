"""Journal d'audit et centre de notifications."""
from __future__ import annotations

from sqlalchemy.orm import Session

from .models import AuditLog, Notification, Priority

SYSTEM_ACTOR = "SYSTEME"


def log(
    db: Session,
    actor: str,
    action: str,
    entity_type: str = "",
    entity_ref: str = "",
    details: dict | None = None,
) -> AuditLog:
    entry = AuditLog(actor=actor or SYSTEM_ACTOR, action=action, entity_type=entity_type, entity_ref=entity_ref, details=details)
    db.add(entry)
    db.flush()
    return entry


def notify(
    db: Session,
    level: Priority | str,
    title: str,
    body: str = "",
    link: str = "",
) -> Notification:
    lvl = level.value if isinstance(level, Priority) else level
    note = Notification(level=lvl, title=title, body=body, link=link)
    db.add(note)
    db.flush()
    return note


LEVEL_ICON = {
    Priority.URGENT.value: "🔴",
    Priority.A_TRAITER.value: "🟠",
    Priority.A_VALIDER.value: "🟡",
    Priority.INFORMATION.value: "🟢",
}
