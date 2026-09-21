"""Tableau de bord, agents, briefing, tâches, notifications, automatisations, audit, paramètres."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..agents import AGENT_ROSTER, AnalyticsAgent, DirecteurAgent, SarahAgent
from ..agents.llm import get_provider
from ..channels import registry_status
from ..config import get_settings
from ..db import get_db
from ..models import AgentRun, AuditLog, Automation, Notification, Task, TaskStatus, User
from ..schemas import AutomationIn, CommandIn, TaskIn
from ..services import scheduling
from ..services.briefing import daily_briefing, sunday_preparation
from .deps import anyone, pastor_only, staff

router = APIRouter(prefix="/api", tags=["bureau"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(anyone)):
    return AnalyticsAgent(db).dashboard()


@router.get("/briefing")
def briefing(db: Session = Depends(get_db), actor: User = Depends(anyone)):
    out = daily_briefing(db, actor=actor.name)
    db.commit()
    return out


@router.get("/dimanche")
def sunday(db: Session = Depends(get_db), actor: User = Depends(anyone)):
    return sunday_preparation(db, actor=actor.name)


@router.post("/dimanche/preparer")
def sunday_prepare(channel: str = "SMS", style: str = "chaleureux", db: Session = Depends(get_db), actor: User = Depends(staff)):
    out = sunday_preparation(db, actor=actor.name, prepare_campaigns=True, channel=channel, style=style)
    db.commit()
    return out


# ── Agents ────────────────────────────────────────────────────────────────────


@router.get("/agents")
def agents(db: Session = Depends(get_db), _: User = Depends(anyone)):
    runs = db.scalars(select(AgentRun).order_by(AgentRun.created_at.desc()).limit(30)).all()
    return {"agents": AGENT_ROSTER, "fournisseur_ia": get_provider().name, "modele": get_settings().llm_model if get_provider().name != "template" else "gabarits hors-ligne", "dernieres_actions": [{"agent": r.agent, "commande": r.command[:160], "intention": r.intent, "resume": (r.result or {}).get("summary", "")[:300], "date": r.created_at.isoformat()} for r in runs]}


@router.post("/agents/commande")
def command(body: CommandIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """Commande en langage naturel adressée au DIRECTEUR IA."""
    result = DirecteurAgent(db, actor.name).handle(body.text)
    db.commit()
    return result.as_dict()


# ── Tâches ────────────────────────────────────────────────────────────────────


@router.get("/taches")
def tasks(include_done: bool = False, db: Session = Depends(get_db), _: User = Depends(anyone)):
    stmt = select(Task).order_by(Task.status, Task.due_at.is_(None), Task.due_at)
    if not include_done:
        stmt = stmt.where(Task.status == TaskStatus.OPEN.value)
    return {"taches": [SarahAgent._task_dict(t) | {"details": t.details, "created_by": t.created_by} for t in db.scalars(stmt).all()], "synthese": SarahAgent(db).task_overview()}


@router.post("/taches", status_code=201)
def create_task(body: TaskIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    t = SarahAgent(db, actor.name).create_task(body.title, body.details, body.priority, body.due_at)
    db.commit()
    return SarahAgent._task_dict(t)


@router.post("/taches/{task_id}/terminer")
def complete_task(task_id: int, db: Session = Depends(get_db), actor: User = Depends(staff)):
    t = db.get(Task, task_id)
    if t is None:
        raise HTTPException(404)
    SarahAgent(db, actor.name).complete_task(t)
    db.commit()
    return SarahAgent._task_dict(t)


# ── Notifications ─────────────────────────────────────────────────────────────


@router.get("/notifications")
def notifications(unread_only: bool = False, db: Session = Depends(get_db), _: User = Depends(anyone)):
    stmt = select(Notification).order_by(Notification.created_at.desc()).limit(100)
    if unread_only:
        stmt = stmt.where(Notification.read.is_(False))
    notes = db.scalars(stmt).all()
    return {"non_lues": sum(1 for n in notes if not n.read), "notifications": [{"id": n.id, "niveau": n.level, "icone": audit.LEVEL_ICON.get(n.level, ""), "titre": n.title, "corps": n.body, "lien": n.link, "lue": n.read, "date": n.created_at.isoformat()} for n in notes]}


@router.post("/notifications/lire")
def mark_read(ids: list[int] | None = None, db: Session = Depends(get_db), _: User = Depends(anyone)):
    stmt = select(Notification).where(Notification.read.is_(False))
    if ids:
        stmt = stmt.where(Notification.id.in_(ids))
    for n in db.scalars(stmt).all():
        n.read = True
    db.commit()
    return {"ok": True}


# ── Automatisations ───────────────────────────────────────────────────────────


@router.get("/automatisations")
def automations(db: Session = Depends(get_db), _: User = Depends(anyone)):
    return [_auto_dict(a) for a in db.scalars(select(Automation).order_by(Automation.id)).all()]


@router.post("/automatisations", status_code=201)
def create_automation(body: AutomationIn, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    a = Automation(**body.model_dump(), requires_validation=True)
    db.add(a)
    db.flush()
    audit.log(db, actor.name, "AUTOMATION_CREATED", "automation", str(a.id), {"kind": a.kind, "name": a.name})
    db.commit()
    return _auto_dict(a)


@router.patch("/automatisations/{auto_id}")
def toggle_automation(auto_id: int, is_active: bool, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    a = db.get(Automation, auto_id)
    if a is None:
        raise HTTPException(404)
    a.is_active = is_active
    audit.log(db, actor.name, "AUTOMATION_TOGGLED", "automation", str(a.id), {"is_active": is_active})
    db.commit()
    return _auto_dict(a)


@router.delete("/automatisations/{auto_id}", status_code=204)
def delete_automation(auto_id: int, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    a = db.get(Automation, auto_id)
    if a is None:
        raise HTTPException(404)
    db.delete(a)
    audit.log(db, actor.name, "AUTOMATION_DELETED", "automation", str(auto_id))
    db.commit()


@router.post("/planificateur/executer")
def run_scheduler_now(db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    """Exécute un cycle du planificateur à la demande (préparer → expirer → envoyer le validé)."""
    out = scheduling.tick(db)
    audit.log(db, actor.name, "SCHEDULER_MANUAL_TICK", details=out)
    db.commit()
    return out


def _auto_dict(a: Automation) -> dict:
    return {"id": a.id, "nom": a.name, "type": a.kind, "description": scheduling.describe(a), "weekday": a.weekday, "day_of_month": a.day_of_month, "hour": a.hour, "minute": a.minute, "offset_hours": a.offset_hours, "group_id": a.group_id, "canal": a.channel, "style": a.style, "message_template": a.message_template, "campaign_name_template": a.campaign_name_template, "validation_requise": True, "active": a.is_active, "derniere_execution": a.last_run_at.isoformat() if a.last_run_at else None}


# ── Audit & paramètres ────────────────────────────────────────────────────────


@router.get("/audit")
def audit_log(limit: int = 200, entity_ref: str | None = None, db: Session = Depends(get_db), _: User = Depends(staff)):
    stmt = select(AuditLog).order_by(AuditLog.at.desc()).limit(min(limit, 1000))
    if entity_ref:
        stmt = stmt.where(AuditLog.entity_ref == entity_ref)
    return [{"id": e.id, "date": e.at.isoformat(), "acteur": e.actor, "action": e.action, "type": e.entity_type, "ref": e.entity_ref, "details": e.details} for e in db.scalars(stmt).all()]


@router.get("/parametres")
def settings(db: Session = Depends(get_db), _: User = Depends(anyone)):
    s = get_settings()
    return {
        "application": s.app_name, "environnement": s.app_env, "fuseau": s.timezone, "url": s.base_url,
        "ia": {"fournisseur": get_provider().name, "modele": s.llm_model if get_provider().name != "template" else None},
        "canaux": registry_status(),
        "validation": {"seuil_double_validation": s.double_confirmation_threshold, "duree_lien_heures": s.approval_link_ttl_hours, "phrase_confirmation": "CONFIRMER L'ENVOI"},
        "planificateur": {"actif": s.scheduler_enabled, "intervalle_s": s.scheduler_interval_seconds, "heure_briefing": s.daily_briefing_hour},
        "cout_sms_eur": s.sms_unit_cost_eur,
        "rgpd": {"consentement_par_canal": True, "desinscription_stop": True, "export": True, "effacement": True, "journal_audit": True, "roles": ["PASTEUR", "SECRETAIRE", "LECTEUR"], "entrainement_ia_sur_donnees_membres": False},
    }
