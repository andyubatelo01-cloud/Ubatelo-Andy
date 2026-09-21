"""AGENT 03 — BERGER, suivi pastoral.

Travaille UNIQUEMENT à partir de faits enregistrés : présences, dates d'arrivée,
anniversaires, notes administratives. Il ne déduit jamais un état spirituel,
émotionnel ou médical. Il propose ; le pasteur décide.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from ..models import Channel, Member, MessageStyle, Priority, utcnow
from ..services import campaign_engine
from ..services import members as members_service
from ..services.personalization import format_date_fr
from .base import Agent, AgentResult
from .communication import CommunicationAgent


class BergerAgent(Agent):
    name = "BERGER"
    icon = "❤️"
    description = "Suivi : nouveaux membres, absences répétées, anniversaires, propositions de contact."

    def people_to_contact(self, absence_days: int = 30, now: datetime | None = None) -> AgentResult:
        now = now or utcnow()
        suggestions: list[dict] = []
        for m, last in members_service.absent_members(self.db, absence_days):
            if m.is_new and not last:
                continue  # traité dans la catégorie « nouveaux »
            suggestions.append({
                "member_id": m.id, "name": m.full_name, "reason": "absence",
                "fact": f"Dernière présence enregistrée : {format_date_fr(last) if last else 'aucune'}",
                "suggested_action": "Message d'encouragement ou appel",
            })
        for m in self.db.query(Member).filter(Member.is_new.is_(True), Member.is_active.is_(True), Member.anonymized.is_(False)).all():
            since = (now - m.joined_at).days if m.joined_at else None
            suggestions.append({
                "member_id": m.id, "name": m.full_name, "reason": "nouveau",
                "fact": f"Arrivé(e) il y a {since} jour(s)" if since is not None else "Nouveau membre à intégrer",
                "suggested_action": "Message de bienvenue et proposition de rencontre",
            })
        for m, in_days in members_service.upcoming_birthdays(self.db, 7):
            suggestions.append({
                "member_id": m.id, "name": m.full_name, "reason": "anniversaire",
                "fact": "Anniversaire aujourd'hui" if in_days == 0 else f"Anniversaire dans {in_days} jour(s)",
                "suggested_action": "Message d'anniversaire",
            })
        result = AgentResult(
            agent=self.name,
            summary=f"{len(suggestions)} personne(s) à recontacter (faits enregistrés uniquement, décision du pasteur).",
            data={"suggestions": suggestions, "absence_threshold_days": absence_days},
        )
        self.trace(f"suivi {absence_days}j", "people_to_contact", result)
        return result

    def prepare_individual_message(self, member: Member, kind: str = "encouragement", style: str = MessageStyle.PASTORAL.value, channel: str | None = None, send_at: datetime | None = None) -> AgentResult:
        """Prépare une campagne individuelle (1 destinataire) — soumise à validation comme toute campagne."""
        channel = channel or member.preferred_channel or Channel.SMS.value
        draft = CommunicationAgent(self.db, self.actor, self.llm).draft(kind, style, channel, None, member.first_name)
        campaign = campaign_engine.create_campaign(
            self.db, name=f"{draft.data['kind'].capitalize()} — {member.full_name}", message=draft.data["message"], channel=channel,
            send_at=send_at or (utcnow() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0),
            explicit_member_ids=[member.id], objective=f"Suivi individuel ({kind})", style=style, subject=draft.data["subject"], created_by=self.actor,
        )
        campaign_engine.submit_for_review(self.db, campaign, self.actor)
        result = AgentResult(agent=self.name, summary=f"Message {kind} préparé pour {member.full_name} ({channel}), en attente de validation.", campaign_refs=[campaign.ref], data={"member_id": member.id, "campaign": campaign.ref, "status": campaign.status})
        self.trace(f"message {kind} → membre {member.id}", "individual_message", result)
        return result

    def prepare_followup_batch(self, absence_days: int = 30, style: str = MessageStyle.PASTORAL.value, channel: str = Channel.SMS.value) -> AgentResult:
        """Prépare UNE campagne d'encouragement vers les personnes absentes (validation obligatoire)."""
        absent = [m for m, _ in members_service.absent_members(self.db, absence_days) if not (m.is_new)]
        if not absent:
            return AgentResult(agent=self.name, summary="Aucune absence prolongée détectée dans les données enregistrées.")
        draft = CommunicationAgent(self.db, self.actor, self.llm).draft("encouragement", style, channel, None, "les personnes absentes")
        campaign = campaign_engine.create_campaign(
            self.db, name=f"Encouragement — absents depuis {absence_days} jours", message=draft.data["message"], channel=channel,
            send_at=(utcnow() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0),
            explicit_member_ids=[m.id for m in absent], objective="Reprendre contact avec les personnes absentes", style=style, subject=draft.data["subject"], created_by=self.actor,
        )
        campaign_engine.submit_for_review(self.db, campaign, self.actor)
        result = AgentResult(agent=self.name, summary=f"Campagne d'encouragement préparée pour {len(absent)} personne(s) — en attente de validation.", campaign_refs=[campaign.ref])
        self.trace(f"relance absents {absence_days}j", "followup_batch", result)
        return result

    def new_members_to_integrate(self) -> list[Member]:
        return self.db.query(Member).filter(Member.is_new.is_(True), Member.is_active.is_(True), Member.anonymized.is_(False)).all()

    def alert_pastor(self) -> None:
        news = self.new_members_to_integrate()
        if news:
            from .. import audit

            audit.notify(self.db, Priority.A_TRAITER, f"{len(news)} nouveau(x) membre(s) à intégrer", ", ".join(m.full_name for m in news[:5]) + (" …" if len(news) > 5 else ""), "/suivi")
