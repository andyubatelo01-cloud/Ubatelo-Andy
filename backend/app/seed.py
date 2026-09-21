"""Données de démonstration : `python -m app.seed`.

Crée une communauté fictive (membres, groupes, événements, présences,
automatisations) pour découvrir le Bureau du Pasteur. Toutes les personnes
sont inventées ; les numéros utilisent la plage réservée +33 6 00 00 xx xx.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import audit
from .db import SessionLocal, init_db
from .main import bootstrap
from .models import Automation, Channel, Event, Group, Member, MessageStyle, Priority, Task, utcnow
from .services import events as events_service
from .services.members import ensure_default_groups, get_group_by_name

FIRST = ["Jean", "Marie", "Paul", "Esther", "David", "Ruth", "Samuel", "Sarah", "Daniel", "Anne", "Joseph", "Déborah", "Élie", "Myriam", "Josué", "Lydie", "Timothée", "Rachel", "Nathan", "Priscille", "Marc", "Abigaïl", "Luc", "Naomi", "Pierre", "Élisabeth", "Jacques", "Hannah", "Michel", "Rebecca", "Emmanuel", "Grâce", "Thomas", "Judith", "Philippe", "Eunice", "Simon", "Tabitha", "Étienne", "Salomé"]
LAST = ["Dupont", "Martin", "Kouassi", "Nguyen", "Diallo", "Bernard", "Mbala", "Rodriguez", "Petit", "Traoré", "Lefebvre", "Okafor", "Moreau", "Silva", "Kamara", "Roux", "Ndiaye", "Garcia", "Fontaine", "Bâ"]


def _next_weekday(now: datetime, weekday: int, hour: int, minute: int = 0) -> datetime:
    delta = (weekday - now.weekday()) % 7 or 7
    return (now + timedelta(days=delta)).replace(hour=hour, minute=minute, second=0, microsecond=0)


def seed(db: Session, now: datetime | None = None) -> dict:
    now = now or utcnow()
    rng = random.Random(2026)
    ensure_default_groups(db)
    if db.scalar(select(Member)) is not None:
        return {"skipped": "des membres existent déjà"}

    groups = {g.slug: g for g in db.scalars(select(Group)).all()}
    membres, nouveaux, jeunesse, hommes, femmes, responsables, chorale, accueil, media, intercession, couples = (
        groups["membres"], groups["nouveaux-membres"], groups["jeunesse"], groups["hommes"], groups["femmes"],
        groups["responsables"], groups["chorale"], groups["accueil"], groups["media"], groups["intercession"], groups["couples"],
    )
    # Groupe dynamique de démonstration
    actifs = Group(name="Actifs 90 jours (SMS)", slug="actifs-90-jours-sms", description="Ont participé au moins une fois dans les 90 derniers jours et acceptent les SMS", dynamic_rule={"active_days": 90, "consent": "SMS"})
    db.add(actifs)

    members: list[Member] = []
    for i in range(40):
        first, last = FIRST[i], LAST[i % len(LAST)]
        m = Member(
            first_name=first, last_name=last, phone=f"+336000{i:04d}"[:12] if i != 7 else "0600",  # un numéro invalide volontaire
            email=f"{first.lower()}.{last.lower()}@exemple.org".replace("é", "e").replace("è", "e").replace("ï", "i").replace("â", "a").replace("ë", "e"),
            joined_at=now - timedelta(days=rng.randint(5, 900)), birthday=f"{rng.randint(1, 28):02d}-{rng.randint(1, 12):02d}",
            preferred_channel=rng.choice([Channel.SMS.value, Channel.WHATSAPP.value, Channel.SMS.value]),
            consent_sms=i % 9 != 0, consent_whatsapp=i % 3 != 0, consent_email=i % 2 == 0, consent_recorded_at=now - timedelta(days=rng.randint(1, 400)),
            is_new=False,
        )
        m.groups.append(membres)
        if i % 2 == 0:
            m.groups.append(femmes if i % 4 == 0 else hommes)
        else:
            m.groups.append(hommes if i % 4 == 1 else femmes)
        if i < 10:
            m.groups.append(jeunesse)
        if i in (0, 1, 2, 3, 4):
            m.groups.append(responsables)
            m.responsibility = ["Responsable accueil", "Responsable média", "Responsable intercession", "Chef de chorale", "Trésorier"][i]
        if 10 <= i < 18:
            m.groups.append(chorale)
        if i in (0, 20, 21):
            m.groups.append(accueil)
        if i in (1, 22):
            m.groups.append(media)
        if i in (2, 23, 24, 25):
            m.groups.append(intercession)
        if 26 <= i < 32:
            m.groups.append(couples)
        members.append(m)
        db.add(m)
    # Nouveaux membres (à intégrer)
    for i, (first, last) in enumerate([("Kevin", "Mendes"), ("Aïcha", "Sow"), ("Léa", "Carvalho")]):
        m = Member(first_name=first, last_name=last, phone=f"+3360009{i:03d}", email=f"{first.lower()}.{last.lower()}@exemple.org".replace("ï", "i").replace("é", "e"), joined_at=now - timedelta(days=rng.randint(2, 20)), consent_sms=True, consent_whatsapp=True, consent_recorded_at=now - timedelta(days=1), is_new=True)
        m.groups += [membres, nouveaux]
        members.append(m)
        db.add(m)
    # Une personne désinscrite
    members[15].unsubscribed = True
    members[15].consent_sms = members[15].consent_whatsapp = members[15].consent_email = False
    db.flush()

    # Événements : cultes passés et à venir, réunion responsables, veillée, retraite
    sunday_next = _next_weekday(now, 6, 10)
    events: list[Event] = []
    for k in range(1, 7):  # 6 cultes passés
        events.append(Event(name="Culte du dimanche", starts_at=sunday_next - timedelta(days=7 * k), location="Salle principale, 12 rue de la Paix", responsible="Pasteur", responsible_welcome="Jean Dupont", responsible_media="Marie Martin", responsible_intercession="Paul Kouassi", is_recurring_sunday=True, audience_group_id=membres.id))
    for k in range(0, 4):  # 4 cultes à venir
        events.append(Event(name="Culte du dimanche", starts_at=sunday_next + timedelta(days=7 * k), location="Salle principale, 12 rue de la Paix", responsible="Pasteur", responsible_welcome="Jean Dupont" if k != 1 else "", responsible_media="Marie Martin", responsible_intercession="Paul Kouassi", is_recurring_sunday=True, audience_group_id=membres.id))
    meeting = Event(name="Réunion des responsables", starts_at=_next_weekday(now, 2, 19, 30), location="Salle 2", responsible="Pasteur", audience_group_id=responsables.id, description="Point mensuel : programme, budget, accueil des nouveaux.")
    veillee = Event(name="Veillée de prière", starts_at=(now + timedelta(days=12)).replace(hour=20, minute=0, second=0, microsecond=0), location="Salle principale", speaker="Pasteur invité", responsible="Paul Kouassi", responsible_intercession="Paul Kouassi", audience_group_id=membres.id, registration_required=True, capacity=150, description="Soirée de prière et de louange.")
    retraite = Event(name="Retraite de prière", starts_at=(now + timedelta(days=35)).replace(hour=9, minute=0, second=0, microsecond=0), ends_at=(now + timedelta(days=37)).replace(hour=16, minute=0), location="", responsible="", audience_group_id=membres.id, registration_required=True, capacity=60, description="Week-end de retraite (informations à compléter).", deadlines=[{"label": "Clôture des inscriptions", "due_at": (now + timedelta(days=25)).isoformat()}])
    jeunesse_soiree = Event(name="Soirée jeunesse", starts_at=(now + timedelta(days=5)).replace(hour=19, minute=0, second=0, microsecond=0), location="Salle 2", responsible="Esther Nguyen", audience_group_id=jeunesse.id)
    events += [meeting, veillee, retraite, jeunesse_soiree]
    for e in events:
        db.add(e)
    db.flush()

    # Présences aux cultes passés (certains membres absents depuis longtemps)
    past = [e for e in events if e.starts_at < now]
    for i, m in enumerate(members[:40]):
        for e in past:
            if i in (30, 31, 32, 33):  # absents depuis 6 semaines
                continue
            if i in (34, 35) and e.starts_at > now - timedelta(days=28):  # absents depuis 4 semaines
                continue
            present = rng.random() < 0.75
            events_service.set_attendance(db, e, m, present=present, actor="SEED")
    # Inscriptions veillée : quelques confirmations
    for m in members[:20]:
        events_service.set_attendance(db, veillee, m, registered=True, confirmed=(m.id % 3 == 0), actor="SEED")

    # Automatisations (elles PRÉPARENT uniquement)
    db.add_all([
        Automation(name="Rappel du culte", kind="WEEKLY", weekday=6, hour=8, minute=30, group_id=membres.id, channel=Channel.SMS.value, style=MessageStyle.CHALEUREUX.value, campaign_name_template="Rappel du culte", message_template="Bonjour {PRENOM}, nous serons heureux de te retrouver ce matin pour le culte à {HEURE}. Que Dieu te bénisse 🙏"),
        Automation(name="Message du mois", kind="MONTHLY", day_of_month=1, hour=9, group_id=membres.id, channel=Channel.WHATSAPP.value, style=MessageStyle.PASTORAL.value, campaign_name_template="Message du mois"),
        Automation(name="Invitation 7 jours avant chaque événement", kind="BEFORE_EVENT", offset_hours=24 * 7, channel=Channel.SMS.value, style=MessageStyle.EVENEMENTIEL.value, campaign_name_template="Invitation {EVENEMENT}"),
        Automation(name="Rappel 24 h avant chaque événement", kind="BEFORE_EVENT", offset_hours=24, channel=Channel.SMS.value, style=MessageStyle.CHALEUREUX.value, campaign_name_template="Rappel {EVENEMENT}"),
    ])
    # Tâches du pasteur
    db.add_all([
        Task(title="Appeler le pasteur invité pour confirmer la veillée", priority=Priority.URGENT.value, due_at=now + timedelta(days=1)),
        Task(title="Préparer l'ordre du jour de la réunion des responsables", priority=Priority.A_TRAITER.value, due_at=meeting.starts_at - timedelta(days=1)),
        Task(title="Compléter le lieu de la retraite de prière", priority=Priority.A_TRAITER.value, due_at=now + timedelta(days=7)),
        Task(title="Prier pour la famille Mendes (demande enregistrée le " + now.strftime("%d/%m") + ")", priority=Priority.INFORMATION.value),
    ])
    audit.log(db, "SEED", "DEMO_DATA_CREATED", details={"members": len(members), "events": len(events)})
    audit.notify(db, Priority.A_TRAITER, "3 nouveaux membres doivent être intégrés", "Kevin Mendes, Aïcha Sow, Léa Carvalho", "/suivi")
    audit.notify(db, Priority.INFORMATION, "Données de démonstration chargées", f"{len(members)} membres, {len(events)} événements, 4 automatisations.")
    db.commit()
    return {"members": len(members), "events": len(events), "automations": 4}


def main() -> None:
    init_db()
    bootstrap()
    db = SessionLocal()
    try:
        print(seed(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
