from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..agents import EventsAgent, SarahAgent
from ..db import get_db
from ..models import Event, Member, User, utcnow
from ..schemas import AttendanceIn, EventIn, EventPatch, PlanIn
from ..services import events as svc
from .deps import anyone, staff

router = APIRouter(prefix="/api/evenements", tags=["evenements"])


@router.get("")
def list_events(days: int = 60, include_past: bool = False, db: Session = Depends(get_db), _: User = Depends(anyone)):
    agent = EventsAgent(db)
    if include_past:
        events = db.scalars(select(Event).order_by(Event.starts_at.desc()).limit(200)).all()
    else:
        events = svc.upcoming_events(db, days)
    return [agent.describe(e) for e in events]


@router.post("", status_code=201)
def create_event(body: EventIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    e = svc.create_event(db, actor.name, **body.model_dump())
    db.commit()
    return EventsAgent(db).describe(e)


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db), _: User = Depends(anyone)):
    e = db.get(Event, event_id)
    if e is None:
        raise HTTPException(404, "Événement introuvable.")
    return EventsAgent(db).describe(e)


@router.patch("/{event_id}")
def update_event(event_id: int, body: EventPatch, db: Session = Depends(get_db), actor: User = Depends(staff)):
    e = db.get(Event, event_id)
    if e is None:
        raise HTTPException(404)
    changes = body.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(e, k, v)
    audit.log(db, actor.name, "EVENT_UPDATED", "event", str(e.id), {"fields": sorted(changes)})
    db.commit()
    return EventsAgent(db).describe(e)


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db), actor: User = Depends(staff)):
    e = db.get(Event, event_id)
    if e is None:
        raise HTTPException(404)
    linked = svc.campaigns_for_event(db, e)
    if any(c.status in ("SCHEDULED", "SENDING") for c in linked):
        raise HTTPException(400, "Des campagnes programmées dépendent de cet événement : annulez-les d'abord.")
    for c in linked:
        c.event_id = None
    db.delete(e)
    audit.log(db, actor.name, "EVENT_DELETED", "event", str(event_id))
    db.commit()


@router.post("/{event_id}/planifier")
def plan(event_id: int, body: PlanIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """Génère le calendrier de communication (J-14 → après) en campagnes à valider."""
    e = db.get(Event, event_id)
    if e is None:
        raise HTTPException(404)
    res = EventsAgent(db, actor.name).plan_communications(e, body.channel, body.style, body.steps)
    db.commit()
    return res.as_dict()


@router.post("/{event_id}/presences")
def attendance(event_id: int, body: AttendanceIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    e, m = db.get(Event, event_id), db.get(Member, body.member_id)
    if e is None or m is None:
        raise HTTPException(404)
    svc.set_attendance(db, e, m, registered=body.registered, confirmed=body.confirmed, present=body.present, actor=actor.name)
    db.commit()
    return svc.event_stats(e)


@router.get("/{event_id}/compte-rendu")
def minutes_template(event_id: int, db: Session = Depends(get_db), actor: User = Depends(anyone)):
    e = db.get(Event, event_id)
    if e is None:
        raise HTTPException(404)
    return {"template": SarahAgent(db, actor.name).meeting_minutes_template(e), "generated_at": utcnow().isoformat()}
