"""Personnalisation des messages : {PRENOM}, {NOM}, {DATE}, {HEURE}, {LIEU}, {EVENEMENT}.

Le système vérifie TOUJOURS les variables avant l'envoi : une variable inconnue ou
non résolvable bloque la campagne.
"""
from __future__ import annotations

import re
from datetime import datetime

from ..models import Event, Member

VARIABLE_PATTERN = re.compile(r"\{([A-Z_]+)\}")
SUPPORTED_VARIABLES = ("PRENOM", "NOM", "DATE", "HEURE", "LIEU", "EVENEMENT")

_FR_DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
_FR_MONTHS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def format_date_fr(dt: datetime) -> str:
    return f"{_FR_DAYS[dt.weekday()]} {dt.day} {_FR_MONTHS[dt.month - 1]}"


def format_time_fr(dt: datetime) -> str:
    return f"{dt.hour}h{dt.minute:02d}" if dt.minute else f"{dt.hour}h"


def extract_variables(message: str) -> list[str]:
    return sorted(set(VARIABLE_PATTERN.findall(message or "")))


def unknown_variables(message: str) -> list[str]:
    return [v for v in extract_variables(message) if v not in SUPPORTED_VARIABLES]


def event_context(event: Event | None) -> dict[str, str]:
    if event is None:
        return {}
    return {
        "DATE": format_date_fr(event.starts_at),
        "HEURE": format_time_fr(event.starts_at),
        "LIEU": event.location or "",
        "EVENEMENT": event.name or "",
    }


def member_context(member: Member | None) -> dict[str, str]:
    if member is None:
        return {}
    return {"PRENOM": member.first_name or "", "NOM": member.last_name or ""}


def missing_variables(message: str, context: dict[str, str]) -> list[str]:
    """Variables présentes dans le message mais vides ou absentes du contexte."""
    return [v for v in extract_variables(message) if v in SUPPORTED_VARIABLES and not context.get(v)]


def render(message: str, context: dict[str, str]) -> str:
    def _sub(match: re.Match) -> str:
        return context.get(match.group(1), match.group(0))

    return VARIABLE_PATTERN.sub(_sub, message or "")


def preview_render(message: str, event: Event | None = None) -> str:
    """Aperçu avec un membre fictif, sans exposer de données réelles."""
    ctx = {"PRENOM": "Marie", "NOM": "Dupont", **event_context(event)}
    return render(message, ctx)
