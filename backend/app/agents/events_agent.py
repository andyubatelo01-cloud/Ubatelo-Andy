"""AGENT 05 — EVENTS : organisation des événements et rétroplanning de communication."""
from __future__ import annotations

from datetime import datetime

from ..models import Channel, Event, MessageStyle, utcnow
from ..services import campaign_engine
from ..services import events as events_service
from ..services.members import get_group_by_name
from ..services.personalization import format_date_fr
from .base import Agent, AgentResult
from .communication import KIND_LABELS, CommunicationAgent


class EventsAgent(Agent):
    name = "EVENTS"
    icon = "📅"
    description = "Organise les événements et génère automatiquement le calendrier de communication."

    def plan_communications(self, event: Event, channel: str = Channel.SMS.value, style: str = MessageStyle.CHALEUREUX.value, steps: list[str] | None = None, now: datetime | None = None) -> AgentResult:
        """Crée une campagne par étape du calendrier (J-14, J-7, J-3, J-1, H-3, après).
        Chaque campagne est soumise aux contrôles et attend la validation du pasteur."""
        now = now or utcnow()
        missing = events_service.missing_information(event)
        group_ids = [event.audience_group_id] if event.audience_group_id else []
        if not group_ids:
            all_members = get_group_by_name(self.db, "Membres")
            group_ids = [all_members.id] if all_members else []
        audience = events_service.group_name(self.db, event.audience_group_id)
        writer = CommunicationAgent(self.db, self.actor, self.llm)
        refs, skipped = [], []
        existing_kinds = {(c.name.split(" — ")[0]) for c in events_service.campaigns_for_event(self.db, event) if c.status not in ("CANCELLED", "EXPIRED")}
        for step in events_service.communication_calendar(event, now):
            if steps and step["label"] not in steps:
                continue
            label = f"{step['label']} {KIND_LABELS[step['kind']]}"
            if not step["future"]:
                skipped.append(f"{label} (date déjà passée)")
                continue
            if label in existing_kinds:
                skipped.append(f"{label} (déjà préparée)")
                continue
            draft = writer.draft(step["kind"], style, channel, event, audience)
            campaign = campaign_engine.create_campaign(
                self.db, name=f"{label} — {event.name}", message=draft.data["message"], channel=channel, send_at=step["send_at"],
                group_ids=group_ids, objective=f"{KIND_LABELS[step['kind']]} pour {event.name}", style=style, subject=draft.data["subject"],
                event_id=event.id, created_by=self.actor,
            )
            campaign_engine.submit_for_review(self.db, campaign, self.actor)
            refs.append(campaign.ref)
        summary = f"{len(refs)} campagne(s) préparée(s) pour « {event.name} » ({format_date_fr(event.starts_at)}) — toutes en attente de validation."
        if skipped:
            summary += f" Ignorées : {', '.join(skipped)}."
        result = AgentResult(agent=self.name, summary=summary, campaign_refs=refs, missing_info=missing, data={"event_id": event.id, "audience": audience, "channel": channel, "skipped": skipped})
        self.trace(f"plan {event.name}", "plan_communications", result)
        return result

    def describe(self, event: Event) -> dict:
        stats = events_service.event_stats(event)
        return {
            "id": event.id, "nom": event.name, "description": event.description, "date": event.starts_at.isoformat(),
            "date_texte": format_date_fr(event.starts_at), "lieu": event.location, "intervenant": event.speaker,
            "public": events_service.group_name(self.db, event.audience_group_id), "capacite": event.capacity,
            "inscription": event.registration_required, "responsable": event.responsible,
            "responsables": {"accueil": event.responsible_welcome, "media": event.responsible_media, "intercession": event.responsible_intercession},
            "echeances": event.deadlines or [], "statistiques": stats,
            "communications": [{**s, "send_at": s["send_at"].isoformat()} for s in events_service.communication_calendar(event)],
            "campagnes": [{"ref": c.ref, "name": c.name, "status": c.status, "send_at": c.send_at.isoformat() if c.send_at else None} for c in events_service.campaigns_for_event(self.db, event)],
            "informations_manquantes": events_service.missing_information(event),
        }
