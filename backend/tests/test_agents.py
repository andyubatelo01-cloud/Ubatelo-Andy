from __future__ import annotations

from datetime import timedelta

from app.agents import BergerAgent, CommunicationAgent, DirecteurAgent, EventsAgent
from app.agents.communication import TEMPLATES
from app.models import CampaignStatus, Event, MessageStyle, utcnow
from app.services import campaign_engine as engine
from app.services import events as events_service
from app.services.briefing import daily_briefing, sunday_preparation
from app.services.members import get_group_by_name

from .conftest import console, make_member


def test_all_styles_exist_for_all_kinds(db):
    styles = {s.value for s in MessageStyle}
    for kind, variants in TEMPLATES.items():
        assert set(variants) == styles, kind
        for text in variants.values():
            assert "{PRENOM}" in text


def test_communication_draft_without_event_has_no_event_variables(db):
    res = CommunicationAgent(db).draft("encouragement", "pastoral", "SMS", None, "Marie")
    msg = res.data["message"]
    assert "{PRENOM}" in msg and "{EVENEMENT}" not in msg and "{DATE}" not in msg


def test_events_agent_generates_full_calendar(db, members):
    g = get_group_by_name(db, "Membres")
    ev = Event(name="Veillée de prière", starts_at=(utcnow() + timedelta(days=20)).replace(hour=20, minute=0, second=0, microsecond=0), location="Salle", responsible="Paul", audience_group_id=g.id)
    db.add(ev)
    db.commit()
    res = EventsAgent(db).plan_communications(ev)
    assert len(res.campaign_refs) == 6
    names = [engine.get_by_ref(db, r).name for r in res.campaign_refs]
    assert names[0].startswith("J-14 Invitation") and names[-1].startswith("Après événement Message de remerciement")
    for r in res.campaign_refs:
        c = engine.get_by_ref(db, r)
        assert c.status == CampaignStatus.READY_FOR_REVIEW.value
        assert c.recipient_count == 5
    assert console().sent == []
    # Relance : aucune campagne en double
    res2 = EventsAgent(db).plan_communications(ev)
    assert res2.campaign_refs == [] and len(res2.data["skipped"]) == 6


def test_events_agent_skips_past_steps(db, members):
    ev = Event(name="Culte", starts_at=utcnow() + timedelta(days=2), location="Salle", responsible="P", audience_group_id=get_group_by_name(db, "Membres").id)
    db.add(ev)
    db.commit()
    res = EventsAgent(db).plan_communications(ev)
    assert len(res.campaign_refs) == 3  # J-14, J-7 et J-3 sont passés


def test_directeur_pending_and_events(db, members, sunday):
    d = DirecteurAgent(db, "Pasteur")
    assert "Aucune campagne" in d.handle("Quelles campagnes attendent ma validation ?").summary
    r = d.handle("Quels sont les événements des deux prochaines semaines ?")
    assert r.data["intent"] == "upcoming_events" and "Culte du dimanche" in r.summary


def test_directeur_prepares_sunday_invitation(db, members, sunday):
    r = DirecteurAgent(db, "Pasteur").handle("Prépare une invitation pour dimanche.")
    assert r.data["intent"] == "invitation" and len(r.campaign_refs) == 1
    c = engine.get_by_ref(db, r.campaign_refs[0])
    assert c.status == CampaignStatus.READY_FOR_REVIEW.value and c.event_id == sunday.id
    assert c.send_at < sunday.starts_at
    assert "{HEURE}" in c.message
    assert "en attente de votre validation" in r.summary
    assert DirecteurAgent(db, "Pasteur").handle("Quelles campagnes attendent ma validation ?").campaign_refs == [c.ref]


def test_directeur_reminds_responsables_of_wednesday_meeting(db, members):
    resp = get_group_by_name(db, "Responsables")
    for m in members[:2]:
        m.groups.append(resp)
    now = utcnow()
    delta = (2 - now.weekday()) % 7 or 7
    ev = Event(name="Réunion des responsables", starts_at=(now + timedelta(days=delta)).replace(hour=19, minute=30, second=0, microsecond=0), location="Salle 2", responsible="Pasteur", audience_group_id=resp.id)
    db.add(ev)
    db.commit()
    r = DirecteurAgent(db, "Pasteur").handle("Rappelle aux responsables la réunion de mercredi", now)
    assert r.data["intent"] == "rappel" and r.campaign_refs
    c = engine.get_by_ref(db, r.campaign_refs[0])
    assert c.event_id == ev.id and c.group_ids == [resp.id] and c.recipient_count == 2


def test_directeur_unconfirmed(db, members):
    g = get_group_by_name(db, "Membres")
    ev = Event(name="Veillée de prière", starts_at=utcnow() + timedelta(days=6), location="Salle", responsible="P", registration_required=True, audience_group_id=g.id)
    db.add(ev)
    db.flush()
    events_service.set_attendance(db, ev, members[0], registered=True, confirmed=True)
    db.commit()
    r = DirecteurAgent(db, "Pasteur").handle("Prépare une campagne pour les personnes qui n'ont pas encore confirmé leur présence.")
    assert r.data["intent"] == "unconfirmed" and r.campaign_refs
    c = engine.get_by_ref(db, r.campaign_refs[0])
    assert c.recipient_count == 4 and members[0].id not in c.explicit_member_ids


def test_directeur_asks_when_event_unknown(db, members):
    r = DirecteurAgent(db, "Pasteur").handle("Prépare la communication pour notre retraite de prière du mois prochain.")
    assert r.data["intent"] == "plan_event" and r.missing_info and r.campaign_refs == []


def test_directeur_plans_known_event(db, members):
    ev = Event(name="Retraite de prière", starts_at=utcnow() + timedelta(days=30), location="", responsible="", audience_group_id=get_group_by_name(db, "Membres").id)
    db.add(ev)
    db.commit()
    r = DirecteurAgent(db, "Pasteur").handle("Prépare la communication pour notre retraite de prière du mois prochain.")
    assert len(r.campaign_refs) == 6
    assert "lieu" in r.missing_info and "Informations manquantes" in r.summary


def test_directeur_task_and_briefing(db, members, sunday):
    d = DirecteurAgent(db, "Pasteur")
    r = d.handle("Rappelle-moi d'appeler le pasteur invité")
    assert r.data["intent"] == "task" and r.task_ids
    b = d.handle("Briefing du jour")
    assert "BRIEFING" in b.summary.upper() or "Bonjour Pasteur" in b.summary


def test_berger_uses_recorded_facts_only(db, members):
    g = get_group_by_name(db, "Membres")
    past = Event(name="Culte", starts_at=utcnow() - timedelta(days=45), audience_group_id=g.id)
    recent = Event(name="Culte", starts_at=utcnow() - timedelta(days=3), audience_group_id=g.id)
    db.add_all([past, recent])
    db.flush()
    for m in members[:3]:
        events_service.set_attendance(db, recent, m, present=True)
    for m in members[3:]:
        events_service.set_attendance(db, past, m, present=True)
    make_member(db, 99, g, is_new=True, joined_at=utcnow() - timedelta(days=4))
    db.commit()
    res = BergerAgent(db).people_to_contact(30)
    reasons = {(s["name"], s["reason"]) for s in res.data["suggestions"]}
    assert ("Prénom4 Nom4", "absence") in reasons and ("Prénom5 Nom5", "absence") in reasons
    assert ("Prénom99 Nom99", "nouveau") in reasons
    assert not any(s["name"] == "Prénom1 Nom1" for s in res.data["suggestions"])
    for s in res.data["suggestions"]:
        assert "Dernière présence" in s["fact"] or "Arrivé" in s["fact"] or "Anniversaire" in s["fact"]


def test_berger_batch_and_individual_need_validation(db, members):
    g = get_group_by_name(db, "Membres")
    past = Event(name="Culte", starts_at=utcnow() - timedelta(days=60), audience_group_id=g.id)
    db.add(past)
    db.flush()
    for m in members:
        events_service.set_attendance(db, past, m, present=True)
    db.commit()
    res = BergerAgent(db).prepare_followup_batch(30)
    c = engine.get_by_ref(db, res.campaign_refs[0])
    assert c.status == CampaignStatus.READY_FOR_REVIEW.value and c.recipient_count == 5
    single = BergerAgent(db).prepare_individual_message(members[0], "anniversaire")
    c1 = engine.get_by_ref(db, single.campaign_refs[0])
    assert c1.recipient_count == 1 and c1.status == CampaignStatus.READY_FOR_REVIEW.value
    assert console().sent == []


def test_briefing_and_sunday(db, members, sunday):
    b = daily_briefing(db)
    assert b["titre"].startswith("🌅") and "priorites" in b and "Bonjour Pasteur" in b["texte"]
    s = sunday_preparation(db, prepare_campaigns=True)
    assert s["culte"]["nom"] == "Culte du dimanche"
    assert len(s["campagnes_creees"]) >= 3
    assert "⚠️" in s["4_responsables"]["accueil"]
    for ref in s["campagnes_creees"]:
        assert engine.get_by_ref(db, ref).status == CampaignStatus.READY_FOR_REVIEW.value
