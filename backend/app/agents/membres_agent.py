"""AGENT 04 — MEMBRES : fiches, groupes, consentements (CRM pastoral)."""
from __future__ import annotations

from ..models import Group, Member
from ..services import members as members_service
from ..services.personalization import format_date_fr
from .base import Agent


class MembresAgent(Agent):
    name = "MEMBRES"
    icon = "👥"
    description = "Gère les fiches membres, les groupes et les consentements."

    def card(self, member: Member) -> dict:
        """Fiche CRM (section 10)."""
        last = members_service.last_participation(member)
        return {
            "id": member.id, "prenom": member.first_name, "nom": member.last_name, "telephone": member.phone, "email": member.email,
            "whatsapp": member.whatsapp or member.phone, "groupes": [{"id": g.id, "nom": g.name} for g in member.groups],
            "responsabilite": member.responsibility, "statut": "Actif" if member.is_active else "Inactif", "nouveau": member.is_new,
            "date_arrivee": format_date_fr(member.joined_at) if member.joined_at else None, "anniversaire": member.birthday,
            "derniere_participation": format_date_fr(last.event.starts_at) if last else None, "dernier_evenement": last.event.name if last else None,
            "dernier_contact": member.last_contact_at.isoformat() if member.last_contact_at else None,
            "communication": " + ".join(ch for ch, ok in (("SMS", member.consent_sms), ("WhatsApp", member.consent_whatsapp), ("E-mail", member.consent_email)) if ok) or "Aucune",
            "canal_prefere": member.preferred_channel,
            "consentement": {"sms": member.consent_sms, "whatsapp": member.consent_whatsapp, "email": member.consent_email, "enregistre_le": member.consent_recorded_at.isoformat() if member.consent_recorded_at else None},
            "desinscrit": member.unsubscribed, "notes_administratives": member.admin_notes,
            "notes": [{"id": n.id, "date": n.created_at.isoformat(), "contenu": n.content} for n in sorted(member.notes, key=lambda n: n.created_at, reverse=True)],
            "participations": [{"evenement": a.event.name, "date": a.event.starts_at.isoformat(), "inscrit": a.registered, "confirme": a.confirmed, "present": a.present} for a in sorted(member.attendances, key=lambda a: a.event.starts_at, reverse=True)[:20]],
            "actions": ["Envoyer message", "Ajouter une note", "Ajouter à un groupe", "Créer rappel", "Voir historique"],
        }

    def group_summary(self, group: Group) -> dict:
        members = members_service.group_members(self.db, group)
        return {"id": group.id, "nom": group.name, "slug": group.slug, "description": group.description, "dynamique": group.dynamic_rule, "systeme": group.is_system, "effectif": len(members), "membres": [{"id": m.id, "nom": m.full_name} for m in members]}
