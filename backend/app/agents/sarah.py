"""AGENT 01 — SARAH, secrétaire IA : tâches, agenda, rappels, comptes rendus, urgences."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select

from .. import audit
from ..models import Campaign, CampaignStatus, Event, Priority, Task, TaskStatus, utcnow
from ..services import events as events_service
from ..services.personalization import format_date_fr, format_time_fr
from .base import Agent, AgentResult


class SarahAgent(Agent):
    name = "SARAH"
    icon = "👔"
    description = "Secrétaire : tâches administratives, agenda, rappels, comptes rendus, centralisation des demandes."

    def create_task(self, title: str, details: str = "", priority: str = Priority.A_TRAITER.value, due_at: datetime | None = None, campaign_ref: str = "", member_id: int | None = None) -> Task:
        task = Task(title=title.strip(), details=details, priority=priority, due_at=due_at, created_by=self.actor, related_campaign_ref=campaign_ref, related_member_id=member_id)
        self.db.add(task)
        self.db.flush()
        audit.log(self.db, self.actor, "TASK_CREATED", "task", str(task.id), {"title": task.title, "priority": priority})
        if priority == Priority.URGENT.value:
            audit.notify(self.db, Priority.URGENT, f"Tâche urgente : {task.title}", details, "/taches")
        return task

    def complete_task(self, task: Task) -> Task:
        task.status = TaskStatus.DONE.value
        task.done_at = utcnow()
        audit.log(self.db, self.actor, "TASK_DONE", "task", str(task.id))
        return task

    def agenda(self, days: int = 14, now: datetime | None = None) -> AgentResult:
        now = now or utcnow()
        events = events_service.upcoming_events(self.db, days, now)
        tasks = self.db.scalars(select(Task).where(Task.status == TaskStatus.OPEN.value, Task.due_at.is_not(None), Task.due_at <= now + timedelta(days=days)).order_by(Task.due_at)).all()
        lines = [f"📅 {format_date_fr(e.starts_at)} {format_time_fr(e.starts_at)} — {e.name}" + (f" ({e.location})" if e.location else "") for e in events]
        lines += [f"📋 {format_date_fr(t.due_at)} — {t.title}" for t in tasks]
        result = AgentResult(
            agent=self.name,
            summary=f"{len(events)} événement(s) et {len(tasks)} tâche(s) dans les {days} prochains jours." if lines else f"Rien de programmé dans les {days} prochains jours.",
            data={"events": [self._event_dict(e) for e in events], "tasks": [self._task_dict(t) for t in tasks], "lines": lines},
        )
        self.trace(f"agenda {days}j", "agenda", result)
        return result

    def task_overview(self, now: datetime | None = None) -> dict:
        now = now or utcnow()
        open_tasks = self.db.scalars(select(Task).where(Task.status == TaskStatus.OPEN.value)).all()
        end_today = now.replace(hour=23, minute=59, second=59)
        end_week = now + timedelta(days=7)
        awaiting = self.db.scalar(select(func.count()).select_from(Campaign).where(Campaign.status == CampaignStatus.READY_FOR_REVIEW.value)) or 0
        return {
            "urgent": [self._task_dict(t) for t in open_tasks if t.priority == Priority.URGENT.value],
            "aujourdhui": [self._task_dict(t) for t in open_tasks if t.due_at and t.due_at <= end_today],
            "cette_semaine": [self._task_dict(t) for t in open_tasks if t.due_at and end_today < t.due_at <= end_week],
            "en_attente_de_validation": awaiting,
            "total_ouvertes": len(open_tasks),
        }

    def meeting_minutes_template(self, event: Event) -> str:
        """Trame de compte rendu, à compléter par le pasteur ou le secrétariat."""
        return (
            f"COMPTE RENDU — {event.name}\n"
            f"Date : {format_date_fr(event.starts_at)} à {format_time_fr(event.starts_at)}\n"
            f"Lieu : {event.location or 'à préciser'}\n"
            f"Responsable : {event.responsible or 'à préciser'}\n\n"
            "Présents : \nOrdre du jour : \n1. \n2. \n\nDécisions : \n- \n\nActions à suivre (qui / quoi / quand) : \n- \n\nProchaine réunion : "
        )

    def flag_urgent_items(self, now: datetime | None = None) -> list[str]:
        """Signale au pasteur les points urgents détectés dans les données."""
        now = now or utcnow()
        alerts = []
        for ev in events_service.upcoming_events(self.db, 7, now):
            missing = events_service.responsibles_missing(ev)
            if missing:
                alerts.append(f"{ev.name} ({format_date_fr(ev.starts_at)}) : responsable(s) manquant(s) — {', '.join(missing)}")
            if ev.registration_required and ev.capacity and events_service.event_stats(ev)["inscrits"] >= ev.capacity:
                alerts.append(f"{ev.name} : capacité atteinte ({ev.capacity}).")
        for c in self.db.scalars(select(Campaign).where(Campaign.status == CampaignStatus.READY_FOR_REVIEW.value, Campaign.send_at.is_not(None), Campaign.send_at <= now + timedelta(hours=24))).all():
            alerts.append(f"Campagne {c.ref} « {c.name} » doit partir avant 24h et attend votre validation.")
        return alerts

    @staticmethod
    def _event_dict(e: Event) -> dict:
        return {"id": e.id, "name": e.name, "starts_at": e.starts_at.isoformat(), "location": e.location, "responsible": e.responsible}

    @staticmethod
    def _task_dict(t: Task) -> dict:
        return {"id": t.id, "title": t.title, "priority": t.priority, "due_at": t.due_at.isoformat() if t.due_at else None, "status": t.status, "campaign_ref": t.related_campaign_ref}
