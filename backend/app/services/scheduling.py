"""Automatisations et planificateur (section 7).

Une automatisation PRÉPARE une campagne (DRAFT → contrôles → READY_FOR_REVIEW).
Le planificateur n'ENVOIE que les campagnes déjà validées par le pasteur.
Ainsi une automatisation qui tourne à 3 h du matin ne peut jamais envoyer
un SMS à toute la communauté sans accord explicite.
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..agents.communication import KIND_LABELS, CommunicationAgent
from ..config import get_settings
from ..models import Automation, Event, Priority, utcnow
from . import campaign_engine
from . import events as events_service
from .briefing import notify_briefing
from .notifications import notify_pastor_of_pending

logger = logging.getLogger("bureau.scheduler")


def _kind_from_template(name_template: str, message_template: str) -> str:
    text = f"{name_template} {message_template}".lower()
    for kind in ("invitation", "rappel", "motivation", "pratique", "remerciement", "encouragement", "bienvenue", "anniversaire", "mois", "annonce"):
        if kind in text:
            return kind
    return "annonce"


def _prepare(db: Session, auto: Automation, run_key: str, event: Event | None, send_at: datetime) -> str | None:
    if auto.last_run_key == run_key:
        return None  # déjà préparée pour cette occurrence
    now = utcnow()
    if event is not None and auto.kind in ("WEEKLY", "DAILY", "MONTHLY") and event.starts_at - timedelta(hours=1) > now + timedelta(minutes=30):
        send_at = (event.starts_at - timedelta(hours=1)).replace(second=0, microsecond=0)  # rappel une heure avant l'événement
    if send_at < now + timedelta(minutes=30):
        send_at = (now + timedelta(minutes=30)).replace(second=0, microsecond=0)  # laisse le temps de valider
    kind = _kind_from_template(auto.campaign_name_template, auto.message_template)
    audience = events_service.group_name(db, auto.group_id or (event.audience_group_id if event else None))
    message = auto.message_template
    if not message:
        message = CommunicationAgent(db, "AUTOMATISATION").draft(kind, auto.style, auto.channel, event, audience).data["message"]
    name = auto.campaign_name_template or f"{KIND_LABELS.get(kind, 'Message')} automatique"
    if event:
        name = name.replace("{EVENEMENT}", event.name)
    group_ids = [auto.group_id] if auto.group_id else ([event.audience_group_id] if event and event.audience_group_id else [])
    if not group_ids:
        from .members import get_group_by_name

        g = get_group_by_name(db, "Membres")
        group_ids = [g.id] if g else []
    campaign = campaign_engine.create_campaign(
        db, name=f"{name} — {send_at.strftime('%d/%m')}", message=message, channel=auto.channel, send_at=send_at, group_ids=group_ids,
        objective=f"Automatisation « {auto.name} »", style=auto.style, event_id=event.id if event else None, automation_id=auto.id, created_by="AUTOMATISATION",
    )
    campaign_engine.submit_for_review(db, campaign, "AUTOMATISATION")
    auto.last_run_at, auto.last_run_key = utcnow(), run_key
    audit.log(db, "AUTOMATISATION", "AUTOMATION_PREPARED", "automation", str(auto.id), {"campaign": campaign.ref, "requires_validation": True})
    return campaign.ref


def run_automations(db: Session, now: datetime | None = None) -> list[str]:
    """Évalue chaque automatisation active et prépare les campagnes dues. Retourne les références créées."""
    now = now or utcnow()
    created: list[str] = []
    for auto in db.scalars(select(Automation).where(Automation.is_active.is_(True))).all():
        try:
            if auto.kind == "WEEKLY" and auto.weekday is not None and now.weekday() == auto.weekday and now.hour >= auto.hour:
                send_at = now.replace(hour=auto.hour, minute=auto.minute, second=0, microsecond=0) + timedelta(hours=2)
                event = events_service.next_sunday_service(db, now) if "culte" in (auto.name + auto.campaign_name_template).lower() else None
                ref = _prepare(db, auto, now.strftime("%G-W%V"), event, send_at)
            elif auto.kind == "MONTHLY" and now.day == (auto.day_of_month or 1) and now.hour >= auto.hour:
                send_at = now.replace(hour=max(auto.hour, 9), minute=auto.minute, second=0, microsecond=0) + timedelta(hours=2)
                ref = _prepare(db, auto, now.strftime("%Y-%m"), None, send_at)
            elif auto.kind == "DAILY" and now.hour >= auto.hour:
                ref = _prepare(db, auto, now.strftime("%Y-%m-%d"), None, now.replace(hour=auto.hour, minute=auto.minute, second=0, microsecond=0) + timedelta(hours=2))
            elif auto.kind in ("BEFORE_EVENT", "AFTER_EVENT"):
                offset = timedelta(hours=auto.offset_hours or 24)
                ref = None
                for ev in events_service.upcoming_events(db, 30, now - (timedelta(days=2) if auto.kind == "AFTER_EVENT" else timedelta())):
                    send_at = ev.starts_at - offset if auto.kind == "BEFORE_EVENT" else ev.starts_at + offset
                    # On prépare 48 h avant l'heure d'envoi prévue, pour laisser le temps de valider.
                    if send_at - timedelta(hours=48) <= now <= send_at and auto.last_run_key != f"{auto.id}:{ev.id}":
                        r = _prepare(db, auto, f"{auto.id}:{ev.id}", ev, send_at)
                        if r:
                            created.append(r)
                continue
            else:
                ref = None
            if ref:
                created.append(ref)
        except Exception as exc:  # noqa: BLE001 - une automatisation défaillante n'arrête pas les autres
            logger.exception("Automatisation %s en erreur : %s", auto.name, exc)
            audit.notify(db, Priority.A_TRAITER, f"Automatisation « {auto.name} » en erreur", str(exc))
    return created


def tick(db: Session, now: datetime | None = None) -> dict:
    """Un cycle du planificateur. Ordre : préparer → expirer → envoyer ce qui est validé → notifier."""
    now = now or utcnow()
    prepared = run_automations(db, now)
    expired = campaign_engine.expire_stale(db, now)
    sent = campaign_engine.dispatch_due(db, now)
    notified = notify_pastor_of_pending(db)
    db.commit()
    return {"prepared": prepared, "expired": [c.ref for c in expired], "sent": [c.ref for c in sent], "notified": notified}


class SchedulerThread(threading.Thread):
    """Boucle d'arrière-plan simple (remplaçable par n8n, Celery ou un cron externe)."""

    def __init__(self, session_factory, interval: int | None = None):
        super().__init__(daemon=True, name="bureau-scheduler")
        self.session_factory = session_factory
        self.interval = interval or get_settings().scheduler_interval_seconds
        self._stop = threading.Event()
        self._last_briefing_day = ""

    def run(self) -> None:
        logger.info("Planificateur démarré (toutes les %s s).", self.interval)
        while not self._stop.is_set():
            db = self.session_factory()
            try:
                now = utcnow()
                tick(db, now)
                day = now.strftime("%Y-%m-%d")
                if now.hour >= get_settings().daily_briefing_hour and self._last_briefing_day != day:
                    notify_briefing(db, now)
                    db.commit()
                    self._last_briefing_day = day
            except Exception:  # noqa: BLE001
                logger.exception("Erreur dans le planificateur")
                db.rollback()
            finally:
                db.close()
            self._stop.wait(self.interval)

    def stop(self) -> None:
        self._stop.set()


def describe(auto: Automation) -> str:
    days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    if auto.kind == "WEEKLY":
        return f"Tous les {days[auto.weekday or 0]}s à {auto.hour}h{auto.minute:02d}, préparer « {auto.campaign_name_template or auto.name} »."
    if auto.kind == "MONTHLY":
        return f"Tous les {auto.day_of_month or 1} du mois à {auto.hour}h, préparer « {auto.campaign_name_template or auto.name} »."
    if auto.kind == "BEFORE_EVENT":
        return f"{auto.offset_hours or 24} h avant chaque événement, préparer « {auto.campaign_name_template or auto.name} »."
    if auto.kind == "AFTER_EVENT":
        return f"{auto.offset_hours or 24} h après chaque événement, préparer « {auto.campaign_name_template or auto.name} »."
    return f"Chaque jour à {auto.hour}h, préparer « {auto.campaign_name_template or auto.name} »."
