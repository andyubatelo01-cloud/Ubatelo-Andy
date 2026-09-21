"""AGENT 06 — TABLEAU DE BORD : statistiques membres, communication, événements, tâches."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select

from ..models import Campaign, CampaignStatus, Delivery, Event, Group, Member, utcnow
from ..services import events as events_service
from ..services import members as members_service
from .base import Agent
from .sarah import SarahAgent


class AnalyticsAgent(Agent):
    name = "TABLEAU DE BORD"
    icon = "📊"
    description = "Tableau de bord et rapports pour le pasteur."

    def dashboard(self, now: datetime | None = None) -> dict:
        now = now or utcnow()
        db = self.db
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        members = db.scalars(select(Member).where(Member.anonymized.is_(False))).all()
        active = [m for m in members if m.is_active]
        new = [m for m in active if m.is_new]
        to_contact = len(members_service.absent_members(db, 30)) + len(members_service.upcoming_birthdays(db, 7))
        groups = db.scalars(select(Group)).all()

        def count(status: str) -> int:
            return db.scalar(select(func.count()).select_from(Campaign).where(Campaign.status == status)) or 0

        sent_month = db.scalar(select(func.count()).select_from(Delivery).where(Delivery.status == "SENT", Delivery.sent_at >= month_start)) or 0
        campaigns_month = db.scalar(select(func.count()).select_from(Campaign).where(Campaign.created_at >= month_start)) or 0
        upcoming = events_service.upcoming_events(db, 30, now)
        past = db.scalars(select(Event).where(Event.starts_at < now, Event.starts_at >= now - timedelta(days=90))).all()
        presences = sum(events_service.event_stats(e)["presents"] for e in past)
        absences = sum(events_service.event_stats(e)["absents"] for e in past)
        participation = round(100 * presences / (presences + absences)) if (presences + absences) else None
        scheduled = count(CampaignStatus.SCHEDULED.value)
        return {
            "membres": {
                "total": len(members), "actifs": len(active), "nouveaux": len(new), "a_recontacter": to_contact,
                "groupes": [{"id": g.id, "nom": g.name, "effectif": len(members_service.group_members(db, g)), "dynamique": bool(g.dynamic_rule)} for g in groups],
                "consentement_sms": sum(1 for m in active if m.consent_sms), "consentement_whatsapp": sum(1 for m in active if m.consent_whatsapp), "consentement_email": sum(1 for m in active if m.consent_email),
            },
            "communication": {
                "preparees": count(CampaignStatus.DRAFT.value) + count(CampaignStatus.READY_FOR_REVIEW.value) + count(CampaignStatus.BLOCKED.value),
                "a_valider": count(CampaignStatus.READY_FOR_REVIEW.value), "bloquees": count(CampaignStatus.BLOCKED.value),
                "validees": count(CampaignStatus.APPROVED.value) + scheduled + count(CampaignStatus.SENT.value),
                "programmees": scheduled, "envoyees": count(CampaignStatus.SENT.value), "annulees": count(CampaignStatus.CANCELLED.value), "expirees": count(CampaignStatus.EXPIRED.value),
                "messages_envoyes_ce_mois": sent_month, "campagnes_ce_mois": campaigns_month, "taux_participation_90j": participation,
            },
            "evenements": {
                "a_venir": len(upcoming),
                "liste": [{"id": e.id, "nom": e.name, "date": e.starts_at.isoformat(), **events_service.event_stats(e)} for e in upcoming[:8]],
                "inscriptions": sum(events_service.event_stats(e)["inscrits"] for e in upcoming),
                "rappels_programmes": scheduled,
            },
            "taches": SarahAgent(db, self.actor, self.llm).task_overview(now),
            "genere_le": now.isoformat(),
        }

    def campaign_report(self, campaign: Campaign) -> dict:
        deliveries = campaign.deliveries
        return {
            "ref": campaign.ref, "nom": campaign.name, "statut": campaign.status, "canal": campaign.channel,
            "cree_par": campaign.created_by, "modifie_par": campaign.modified_by, "valide_par": campaign.approved_by,
            "valide_le": campaign.approved_at.isoformat() if campaign.approved_at else None,
            "envoye_le": campaign.sent_at.isoformat() if campaign.sent_at else None,
            "destinataires": campaign.recipient_count, "resultat": campaign.result,
            "envois": {"total": len(deliveries), "envoyes": sum(1 for d in deliveries if d.status in ("SENT", "DELIVERED")), "livres": sum(1 for d in deliveries if d.status == "DELIVERED"), "echecs": sum(1 for d in deliveries if d.status == "FAILED")},
            "erreurs": [d.error for d in deliveries if d.error][:10],
        }
