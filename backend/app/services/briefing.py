"""Mode « Briefing du pasteur » (section 15) et « Préparation du dimanche » (section 16)."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..agents.berger import BergerAgent
from ..agents.events_agent import EventsAgent
from ..agents.sarah import SarahAgent
from ..models import Campaign, CampaignStatus, Channel, Event, MessageStyle, Priority, Task, TaskStatus, utcnow
from . import events as events_service
from .personalization import format_date_fr, format_time_fr


def daily_briefing(db: Session, now: datetime | None = None, actor: str = "DIRECTEUR IA") -> dict:
    now = now or utcnow()
    start, end = now.replace(hour=0, minute=0, second=0, microsecond=0), now.replace(hour=23, minute=59, second=59)
    sarah = SarahAgent(db, actor)
    berger = BergerAgent(db, actor)

    today_events = db.scalars(select(Event).where(Event.starts_at >= start, Event.starts_at <= end).order_by(Event.starts_at)).all()
    week_events = events_service.upcoming_events(db, 7, now)
    to_prepare = []
    for ev in week_events + events_service.upcoming_events(db, 14, now)[len(week_events):]:
        planned = {c.name.split(" — ")[0] for c in events_service.campaigns_for_event(db, ev) if c.status not in (CampaignStatus.CANCELLED.value, CampaignStatus.EXPIRED.value)}
        for step in events_service.communication_calendar(ev, now):
            if step["future"] and step["send_at"] <= now + timedelta(days=2):
                from ..agents.communication import KIND_LABELS

                label = f"{step['label']} {KIND_LABELS[step['kind']]}"
                if label not in planned:
                    to_prepare.append(f"{label} pour « {ev.name} » (envoi prévu {format_date_fr(step['send_at'])})")
    pending = db.scalars(select(Campaign).where(Campaign.status == CampaignStatus.READY_FOR_REVIEW.value).order_by(Campaign.send_at)).all()
    blocked = db.scalars(select(Campaign).where(Campaign.status == CampaignStatus.BLOCKED.value)).all()
    follow = berger.people_to_contact(30, now).data["suggestions"]
    alerts = sarah.flag_urgent_items(now)
    reminders = db.scalars(select(Task).where(Task.status == TaskStatus.OPEN.value).order_by(Task.priority, Task.due_at)).all()
    priorities = []
    if pending:
        priorities.append(f"🟡 {len(pending)} campagne(s) attendent votre validation.")
    if blocked:
        priorities.append(f"🟠 {len(blocked)} campagne(s) bloquée(s) par les contrôles.")
    news = berger.new_members_to_integrate()
    if news:
        priorities.append(f"🟠 {len(news)} nouveau(x) membre(s) à intégrer.")
    priorities += [f"🔴 {a}" for a in alerts]
    if today_events:
        priorities.append(f"🟢 {len(today_events)} événement(s) aujourd'hui.")

    return {
        "titre": "🌅 BRIEFING DU JOUR",
        "date": now.isoformat(),
        "date_texte": format_date_fr(now),
        "aujourdhui": {"evenements": [{"id": e.id, "nom": e.name, "heure": format_time_fr(e.starts_at), "lieu": e.location, "responsable": e.responsible} for e in today_events]},
        "communications": {"campagnes_a_preparer": to_prepare},
        "validations": {"campagnes_en_attente": [{"ref": c.ref, "nom": c.name, "canal": c.channel, "destinataires": c.recipient_count, "envoi": c.send_at.isoformat() if c.send_at else None} for c in pending], "bloquees": [{"ref": c.ref, "nom": c.name} for c in blocked]},
        "suivi": {"personnes_a_recontacter": follow[:10], "total": len(follow)},
        "priorites": priorities,
        "cette_semaine": [{"id": e.id, "nom": e.name, "date": format_date_fr(e.starts_at), "heure": format_time_fr(e.starts_at)} for e in week_events],
        "a_ne_pas_oublier": [{"id": t.id, "titre": t.title, "priorite": t.priority, "echeance": format_date_fr(t.due_at) if t.due_at else None} for t in reminders[:10]],
        "texte": _briefing_text(now, today_events, to_prepare, pending, follow, priorities, reminders),
    }


def _briefing_text(now, today_events, to_prepare, pending, follow, priorities, reminders) -> str:
    lines = [f"🌅 Bonjour Pasteur, voici votre briefing du {format_date_fr(now)}.", "", "📅 Aujourd'hui"]
    lines += [f"  • {e.name} — {format_time_fr(e.starts_at)}" + (f" ({e.location})" if e.location else "") for e in today_events] or ["  • Aucun événement"]
    lines += ["", "📢 Communications à préparer"] + ([f"  • {t}" for t in to_prepare] or ["  • Rien à préparer dans les 48 h"])
    lines += ["", "⏳ Validations en attente"] + ([f"  • {c.ref} — {c.name} ({c.recipient_count} dest.)" for c in pending] or ["  • Aucune"])
    lines += ["", "👥 Suivi"] + ([f"  • {s['name']} — {s['fact']}" for s in follow[:5]] or ["  • Personne à recontacter"])
    lines += ["", "🔥 Priorités"] + ([f"  {p}" for p in priorities] or ["  • Journée calme"])
    lines += ["", "🙏 À ne pas oublier"] + ([f"  • {t.title}" for t in reminders[:5]] or ["  • Rien d'enregistré"])
    return "\n".join(lines)


def sunday_preparation(db: Session, now: datetime | None = None, actor: str = "DIRECTEUR IA", prepare_campaigns: bool = False, channel: str = Channel.SMS.value, style: str = MessageStyle.CHALEUREUX.value) -> dict:
    """Dossier DIMANCHE : communication, rappel, infos pratiques, responsables, suivi, après-culte."""
    now = now or utcnow()
    service = events_service.next_sunday_service(db, now)
    if service is None:
        return {"titre": "📆 PRÉPARATION DU DIMANCHE", "erreur": "Aucun culte du dimanche n'est enregistré dans les événements à venir.", "campagnes": []}
    refs: list[str] = []
    if prepare_campaigns:
        refs = EventsAgent(db, actor).plan_communications(service, channel, style, now=now).campaign_refs
    steps = events_service.communication_calendar(service, now)
    campaigns = [{"ref": c.ref, "nom": c.name, "statut": c.status, "envoi": c.send_at.isoformat() if c.send_at else None} for c in events_service.campaigns_for_event(db, service)]
    new_members = BergerAgent(db, actor).new_members_to_integrate()
    last_service = db.scalar(select(Event).where(Event.is_recurring_sunday.is_(True), Event.starts_at < now).order_by(Event.starts_at.desc()))
    newcomers = []
    if last_service:
        newcomers = [a.member.full_name for a in last_service.attendances if a.present and a.member.is_new]
    return {
        "titre": "📆 PRÉPARATION DU DIMANCHE",
        "culte": {"id": service.id, "nom": service.name, "date": format_date_fr(service.starts_at), "heure": format_time_fr(service.starts_at), "lieu": service.location, "intervenant": service.speaker},
        "1_communication": {"invitation": next((s for s in steps if s["kind"] == "invitation"), None) and "Invitation prévue " + format_date_fr(next(s for s in steps if s["kind"] == "invitation")["send_at"])},
        "2_rappel": "Rappel prévu samedi " + format_date_fr(next((s["send_at"] for s in steps if s["kind"] == "rappel"), service.starts_at - timedelta(days=1))),
        "3_informations_pratiques": {"horaires": format_time_fr(service.starts_at), "lieu": service.location or "à préciser"},
        "4_responsables": {"accueil": service.responsible_welcome or "⚠️ non désigné", "media": service.responsible_media or "⚠️ non désigné", "intercession": service.responsible_intercession or "⚠️ non désigné", "culte": service.responsible or "⚠️ non désigné"},
        "5_suivi": {"nouveaux_participants_dernier_culte": newcomers, "nouveaux_membres_a_integrer": [m.full_name for m in new_members]},
        "6_apres_culte": "Message de remerciement prévu " + format_date_fr(service.starts_at + timedelta(hours=6)),
        "campagnes": campaigns,
        "campagnes_creees": refs,
        "rappel": "Toutes les communications collectives restent en attente de validation du pasteur.",
    }


def notify_briefing(db: Session, now: datetime | None = None) -> None:
    from .. import audit

    b = daily_briefing(db, now)
    audit.notify(db, Priority.INFORMATION, f"Briefing du {b['date_texte']}", "\n".join(b["priorites"]) or "Journée calme.", "/dashboard")
