"""AGENT 07 — DIRECTEUR IA : chef d'orchestre.

Reçoit une demande en langage naturel, la comprend, demande les informations
manquantes, mobilise les agents spécialisés, prépare les campagnes et les
présente au pasteur. Il attend ensuite la validation : il n'envoie jamais.

Compréhension en deux temps :
1. analyseur d'intentions déterministe (français, mots-clés, dates relatives) ;
2. si l'intention reste ambiguë et qu'un modèle est configuré, extraction
   structurée par le modèle (sans transmettre de données personnelles).
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from pydantic import BaseModel, Field
from sqlalchemy import select

from ..models import Channel, Event, Group, MessageStyle, Priority, utcnow
from ..services import campaign_engine
from ..services import events as events_service
from ..services import members as members_service
from ..services.personalization import format_date_fr, format_time_fr
from .analytics import AnalyticsAgent
from .base import CHARTER, Agent, AgentResult
from .berger import BergerAgent
from .communication import KIND_LABELS, CommunicationAgent
from .events_agent import EventsAgent
from .sarah import SarahAgent

DAYS_FR = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3, "vendredi": 4, "samedi": 5, "dimanche": 6}
NUMBERS_FR = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8, "dix": 10, "quinze": 15, "trente": 30}
STYLE_WORDS = {
    "chaleureux": MessageStyle.CHALEUREUX.value, "pastoral": MessageStyle.PASTORAL.value, "motivant": MessageStyle.MOTIVANT.value,
    "évangélisation": MessageStyle.EVANGELISATION.value, "evangelisation": MessageStyle.EVANGELISATION.value, "événementiel": MessageStyle.EVENEMENTIEL.value,
    "administratif": MessageStyle.ADMINISTRATIF.value, "urgent": MessageStyle.RAPPEL_URGENT.value,
}
CHANNEL_WORDS = {"whatsapp": Channel.WHATSAPP.value, "mail": Channel.EMAIL.value, "e-mail": Channel.EMAIL.value, "email": Channel.EMAIL.value, "courriel": Channel.EMAIL.value, "sms": Channel.SMS.value, "texto": Channel.SMS.value}


class ParsedIntent(BaseModel):
    """Schéma d'extraction structurée utilisé quand un modèle est configuré."""

    intent: str = Field(description="Une valeur parmi : plan_event, invitation, rappel, encouragement, unconfirmed, birthday, welcome, monthly, briefing, sunday, pending, upcoming_events, agenda, followup, task, unknown")
    event_hint: str = Field(default="", description="Mots désignant l'événement concerné, si présent")
    group_hint: str = Field(default="", description="Nom du groupe ciblé, si présent")
    weekday: str = Field(default="", description="Jour de la semaine mentionné (lundi…dimanche), sinon vide")
    channel: str = Field(default="", description="SMS, WHATSAPP, EMAIL ou vide")
    style: str = Field(default="", description="chaleureux, pastoral, motivant, evangelisation, evenementiel, administratif, rappel_urgent ou vide")
    horizon_days: int = Field(default=0, description="Nombre de jours d'horizon si la demande porte sur une période")
    task_title: str = Field(default="", description="Intitulé de la tâche si l'intention est task")


class DirecteurAgent(Agent):
    name = "DIRECTEUR IA"
    icon = "🤖"
    description = "Coordonne tous les agents : comprend la demande, prépare, présente, attend la validation."

    # ────────────────────────────── Point d'entrée ──────────────────────────────

    def handle(self, text: str, now: datetime | None = None) -> AgentResult:
        now = now or utcnow()
        text = (text or "").strip()
        if not text:
            return AgentResult(agent=self.name, summary="Dites-moi ce que vous souhaitez préparer : une invitation, un rappel, le briefing du jour, les campagnes à valider…")
        parsed = self._parse(text)
        if parsed.intent == "unknown" and self.llm.name != "template":
            try:
                llm_parsed = self.llm.generate_structured(CHARTER + " Tu classes la demande du pasteur dans une intention et tu extrais les indices utiles.", f"Demande : « {text} »", ParsedIntent)
                if llm_parsed:
                    parsed = llm_parsed
            except Exception:  # noqa: BLE001 - on retombe sur l'analyse déterministe
                pass
        handler = getattr(self, f"_do_{parsed.intent}", None) or self._do_unknown
        result = handler(text, parsed, now)
        result.data.setdefault("intent", parsed.intent)
        self.trace(text, parsed.intent, result)
        return result

    # ────────────────────────────── Analyse déterministe ──────────────────────────────

    def _parse(self, text: str) -> ParsedIntent:
        t = text.lower().replace("’", "'")
        p = ParsedIntent(intent="unknown")
        for word, value in CHANNEL_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", t):
                p.channel = value
                break
        for word, value in STYLE_WORDS.items():
            if word in t:
                p.style = value
                break
        for day in DAYS_FR:
            if re.search(rf"\b{day}\b", t):
                p.weekday = day
                break
        m = re.search(r"(\d+|un|une|deux|trois|quatre|cinq|six|sept|huit|dix|quinze|trente)\s+(prochain(?:e)?s?\s+)?(jour|semaine|mois)", t)
        if m:
            n = int(m.group(1)) if m.group(1).isdigit() else NUMBERS_FR[m.group(1)]
            p.horizon_days = n * {"jour": 1, "semaine": 7, "mois": 30}[m.group(3)]
        elif "prochaine semaine" in t or "semaine prochaine" in t:
            p.horizon_days = 7
        elif "mois prochain" in t or "prochain mois" in t:
            p.horizon_days = 45
        for g in self.db.scalars(select(Group)).all():
            if g.name.lower() in t or g.slug.replace("-", " ") in t:
                p.group_hint = g.name
                break

        if "briefing" in t or "résumé du jour" in t or "resume du jour" in t:
            p.intent = "briefing"
        elif ("valid" in t and ("attend" in t or "en attente" in t)) or "à valider" in t or "a valider" in t:
            p.intent = "pending"
        elif re.search(r"(quels?|liste|affiche|montre).*(événement|evenement|évènement)", t) or (("événement" in t or "evenement" in t) and ("prochain" in t or "semaine" in t or "à venir" in t)):
            p.intent = "upcoming_events"
        elif "agenda" in t or "planning" in t or "programme de la semaine" in t:
            p.intent = "agenda"
        elif "pas encore confirmé" in t or "pas confirmé" in t or "non confirmé" in t or "n'ont pas confirmé" in t:
            p.intent = "unconfirmed"
        elif "anniversaire" in t:
            p.intent = "birthday"
        elif "bienvenue" in t or ("nouveaux" in t and "membre" in t and ("message" in t or "accueil" in t or "intégr" in t)):
            p.intent = "welcome"
        elif "message du mois" in t or ("mois" in t and "message" in t):
            p.intent = "monthly"
        elif "absent" in t or "recontacter" in t or "encouragement" in t or "pas vu" in t or "suivi" in t:
            p.intent = "followup" if ("qui" in t or "liste" in t or "quelles" in t or "quels" in t) else "encouragement"
        elif "dimanche" in t and ("prépar" in t or "prepar" in t) and ("communication" in t or "dossier" in t or "culte" in t):
            p.intent = "sunday"
        elif "rappel" in t and not re.search(r"rappelle[- ]moi", t):
            p.intent = "rappel"
        elif re.search(r"rappelle[- ]moi|note (?:que|de)|tâche|tache|ajoute .* (?:à|a) faire|pense-bête", t):
            p.intent = "task"
            p.task_title = re.sub(r"^(rappelle[- ]moi (?:de |d')?|note (?:que |de )?|ajoute (?:une )?tâche ?:? ?)", "", text.strip(), flags=re.I).strip(" .")
        elif "invitation" in t or "invite" in t:
            p.intent = "invitation"
        elif ("communication" in t or "campagne" in t or "prépare" in t or "prepare" in t) and not p.group_hint:
            p.intent = "plan_event"
        elif "campagne" in t and p.group_hint:
            p.intent = "invitation"
        # indice d'événement : ce qui suit « pour » / « de » / « notre »
        m = re.search(r"(?:pour|de|d'|notre|la|le)\s+(?:notre\s+|la\s+|le\s+)?([a-zéèêàçùïôû'’\- ]{4,}?)(?:\s+(?:du|de|des)\s+(?:mois|semaine|dimanche|\d)|\s*$|\s*\?)", t)
        if m and p.intent in ("plan_event", "invitation", "rappel", "unconfirmed", "unknown"):
            hint = m.group(1).strip()
            for stop in ("les responsables", "les membres", "la jeunesse", "tous", "toute la communauté"):
                hint = hint.replace(stop, "").strip()
            p.event_hint = hint
        return p

    # ────────────────────────────── Aides ──────────────────────────────

    def _next_weekday(self, weekday: str, now: datetime) -> datetime:
        target = DAYS_FR[weekday]
        delta = (target - now.weekday()) % 7
        delta = 7 if delta == 0 and now.hour >= 12 else delta
        return (now + timedelta(days=delta)).replace(hour=10, minute=0, second=0, microsecond=0)

    def _find_event(self, parsed: ParsedIntent, text: str, now: datetime) -> Event | None:
        if parsed.weekday == "dimanche" and not parsed.event_hint:
            return events_service.next_sunday_service(self.db, now)
        if parsed.weekday:
            day = self._next_weekday(parsed.weekday, now).date()
            for ev in events_service.upcoming_events(self.db, 8, now):
                if ev.starts_at.date() == day and (not parsed.event_hint or any(w in ev.name.lower() for w in parsed.event_hint.split() if len(w) > 3)):
                    return ev
        if parsed.event_hint:
            ev = events_service.find_event(self.db, parsed.event_hint, now)
            if ev:
                return ev
        if parsed.horizon_days:
            evs = events_service.upcoming_events(self.db, parsed.horizon_days, now)
            if len(evs) == 1:
                return evs[0]
        return events_service.find_event(self.db, text, now)

    def _group(self, parsed: ParsedIntent, fallback: str = "Membres") -> Group | None:
        return members_service.get_group_by_name(self.db, parsed.group_hint or fallback) or members_service.get_group_by_name(self.db, fallback)

    def _default_send_at(self, event: Event | None, now: datetime, hours_before: int = 24) -> datetime:
        if event and event.starts_at - timedelta(hours=hours_before) > now + timedelta(minutes=30):
            return (event.starts_at - timedelta(hours=hours_before)).replace(minute=0, second=0, microsecond=0)
        return (now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)

    def _campaign_for(self, kind: str, parsed: ParsedIntent, event: Event | None, group: Group | None, now: datetime, send_at: datetime | None = None, name: str | None = None, explicit_member_ids: list[int] | None = None, audience_label: str | None = None) -> AgentResult:
        channel = parsed.channel or Channel.SMS.value
        style = parsed.style or MessageStyle.CHALEUREUX.value
        audience = audience_label or (group.name if group else "les membres")
        draft = CommunicationAgent(self.db, self.actor, self.llm).draft(kind, style, channel, event, audience)
        label = KIND_LABELS[kind]
        campaign = campaign_engine.create_campaign(
            self.db, name=name or (f"{label} — {event.name}" if event else f"{label} — {audience}"), message=draft.data["message"], channel=channel,
            send_at=send_at or self._default_send_at(event, now), group_ids=[group.id] if group and not explicit_member_ids else [],
            explicit_member_ids=explicit_member_ids or [], objective=f"{label} ({audience})", style=style, subject=draft.data["subject"],
            event_id=event.id if event else None, created_by=self.actor,
        )
        report = campaign_engine.submit_for_review(self.db, campaign, self.actor)
        preview = campaign_engine.preview(self.db, campaign)
        status_text = "bloquée par les contrôles" if report.blocked else f"prête — {campaign.recipient_count} destinataire(s) — en attente de votre validation"
        missing = events_service.missing_information(event) if event else []
        return AgentResult(agent=self.name, summary=f"{label} « {campaign.name} » {status_text}.", campaign_refs=[campaign.ref], missing_info=missing, data={"preview": preview, "blocked": report.blocked})

    # ────────────────────────────── Intentions ──────────────────────────────

    def _do_plan_event(self, text, parsed, now) -> AgentResult:
        event = self._find_event(parsed, text, now)
        if event is None:
            return AgentResult(agent=self.name, summary="Je n'ai pas trouvé cet événement dans l'agenda. Pouvez-vous me donner son nom exact, sa date, son heure et son lieu ? Je le créerai puis je préparerai toute la communication.", missing_info=["événement (nom, date, heure, lieu, public)"], data={"suggestion": "Créez l'événement dans 📅 Événements, puis redemandez-moi."})
        res = EventsAgent(self.db, self.actor, self.llm).plan_communications(event, parsed.channel or Channel.SMS.value, parsed.style or MessageStyle.CHALEUREUX.value, now=now)
        summary = res.summary
        if res.missing_info:
            summary += " Informations manquantes à compléter avant validation : " + ", ".join(res.missing_info) + "."
        return AgentResult(agent=self.name, summary=summary, campaign_refs=res.campaign_refs, missing_info=res.missing_info, data={"event": EventsAgent(self.db, self.actor).describe(event)})

    def _do_invitation(self, text, parsed, now) -> AgentResult:
        event = self._find_event(parsed, text, now)
        if event is None:
            return AgentResult(agent=self.name, summary="Pour quelle occasion souhaitez-vous inviter ? Je n'ai trouvé aucun événement correspondant. Indiquez-moi le nom, la date, l'heure et le lieu.", missing_info=["événement"])
        group = self._group(parsed, events_service.group_name(self.db, event.audience_group_id))
        return self._campaign_for("invitation", parsed, event, group, now, send_at=self._default_send_at(event, now, 72))

    def _do_rappel(self, text, parsed, now) -> AgentResult:
        event = self._find_event(parsed, text, now)
        group = self._group(parsed, events_service.group_name(self.db, event.audience_group_id) if event else "Membres")
        if event is None:
            return AgentResult(agent=self.name, summary="Quel événement dois-je rappeler ? Je n'en ai trouvé aucun correspondant" + (f" {parsed.weekday}" if parsed.weekday else "") + ". Précisez le nom ou créez-le dans l'agenda.", missing_info=["événement"])
        return self._campaign_for("rappel", parsed, event, group, now)

    def _do_unconfirmed(self, text, parsed, now) -> AgentResult:
        event = self._find_event(parsed, text, now)
        if event is None:
            candidates = [e for e in events_service.upcoming_events(self.db, 30, now) if e.registration_required]
            event = candidates[0] if len(candidates) == 1 else None
        if event is None:
            return AgentResult(agent=self.name, summary="Pour quel événement ? Précisez l'événement à inscriptions concerné.", missing_info=["événement"])
        base = members_service.members_of_event(self.db, event)
        targets = [m for m in base if not any(a.event_id == event.id and a.confirmed for a in m.attendances)]
        if not targets:
            return AgentResult(agent=self.name, summary=f"Tout le monde a confirmé pour « {event.name} ». Rien à préparer.")
        style = parsed.style or MessageStyle.EVENEMENTIEL.value
        parsed.style = style
        return self._campaign_for("rappel", parsed, event, None, now, name=f"Relance non confirmés — {event.name}", explicit_member_ids=[m.id for m in targets], audience_label="les personnes n'ayant pas confirmé")

    def _do_encouragement(self, text, parsed, now) -> AgentResult:
        return BergerAgent(self.db, self.actor, self.llm).prepare_followup_batch(30, parsed.style or MessageStyle.PASTORAL.value, parsed.channel or Channel.SMS.value)

    def _do_followup(self, text, parsed, now) -> AgentResult:
        res = BergerAgent(self.db, self.actor, self.llm).people_to_contact(30, now)
        return AgentResult(agent=self.name, summary=res.summary + " Dites « prépare un message d'encouragement » pour préparer la relance.", data=res.data)

    def _do_birthday(self, text, parsed, now) -> AgentResult:
        upcoming = members_service.upcoming_birthdays(self.db, 7)
        if not upcoming:
            return AgentResult(agent=self.name, summary="Aucun anniversaire enregistré dans les 7 prochains jours.")
        refs = []
        berger = BergerAgent(self.db, self.actor, self.llm)
        for m, in_days in upcoming:
            send_at = (now + timedelta(days=in_days)).replace(hour=9, minute=0, second=0, microsecond=0)
            refs += berger.prepare_individual_message(m, "anniversaire", parsed.style or MessageStyle.CHALEUREUX.value, parsed.channel, send_at).campaign_refs
        return AgentResult(agent=self.name, summary=f"{len(refs)} message(s) d'anniversaire préparé(s) — en attente de validation.", campaign_refs=refs)

    def _do_welcome(self, text, parsed, now) -> AgentResult:
        news = BergerAgent(self.db, self.actor, self.llm).new_members_to_integrate()
        if not news:
            return AgentResult(agent=self.name, summary="Aucun nouveau membre à intégrer pour le moment.")
        return self._campaign_for("bienvenue", parsed, None, None, now, name="Bienvenue aux nouveaux membres", explicit_member_ids=[m.id for m in news], audience_label="les nouveaux membres")

    def _do_monthly(self, text, parsed, now) -> AgentResult:
        first = (now.replace(day=1) + timedelta(days=32)).replace(day=1, hour=9, minute=0, second=0, microsecond=0) if now.day > 3 else now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(hours=2)
        parsed.style = parsed.style or MessageStyle.PASTORAL.value
        return self._campaign_for("mois", parsed, None, self._group(parsed), now, send_at=first, name=f"Message du mois — {format_date_fr(first)}")

    def _do_briefing(self, text, parsed, now) -> AgentResult:
        from ..services.briefing import daily_briefing

        b = daily_briefing(self.db, now, self.actor)
        return AgentResult(agent=self.name, summary=b["texte"], data={"briefing": b})

    def _do_sunday(self, text, parsed, now) -> AgentResult:
        from ..services.briefing import sunday_preparation

        dossier = sunday_preparation(self.db, now, self.actor, prepare_campaigns=True, channel=parsed.channel or Channel.SMS.value, style=parsed.style or MessageStyle.CHALEUREUX.value)
        if "erreur" in dossier:
            return AgentResult(agent=self.name, summary=dossier["erreur"], missing_info=["culte du dimanche"])
        return AgentResult(agent=self.name, summary=f"Dossier du dimanche préparé : {len(dossier['campagnes_creees'])} campagne(s) créée(s), en attente de validation.", campaign_refs=dossier["campagnes_creees"], data={"dossier": dossier})

    def _do_pending(self, text, parsed, now) -> AgentResult:
        pending = campaign_engine.pending_review(self.db)
        if not pending:
            return AgentResult(agent=self.name, summary="Aucune campagne n'attend votre validation. 🟢")
        lines = [f"• {c.ref} — {c.name} · {c.channel} · {c.recipient_count} dest. · envoi {format_date_fr(c.send_at)} {format_time_fr(c.send_at)}" + (" · ⚠️ double validation" if c.requires_double_confirmation else "") for c in pending]
        return AgentResult(agent=self.name, summary=f"🟡 {len(pending)} campagne(s) attendent votre validation :\n" + "\n".join(lines), campaign_refs=[c.ref for c in pending], data={"campaigns": [campaign_engine.preview(self.db, c) for c in pending]})

    def _do_upcoming_events(self, text, parsed, now) -> AgentResult:
        days = parsed.horizon_days or 14
        evs = events_service.upcoming_events(self.db, days, now)
        if not evs:
            return AgentResult(agent=self.name, summary=f"Aucun événement dans les {days} prochains jours.")
        lines = [f"• {format_date_fr(e.starts_at)} {format_time_fr(e.starts_at)} — {e.name}" + (f" ({e.location})" if e.location else "") for e in evs]
        return AgentResult(agent=self.name, summary=f"📅 {len(evs)} événement(s) dans les {days} prochains jours :\n" + "\n".join(lines), data={"events": [EventsAgent(self.db, self.actor).describe(e) for e in evs]})

    def _do_agenda(self, text, parsed, now) -> AgentResult:
        res = SarahAgent(self.db, self.actor, self.llm).agenda(parsed.horizon_days or 14, now)
        return AgentResult(agent=self.name, summary=res.summary + ("\n" + "\n".join(res.data["lines"]) if res.data["lines"] else ""), data=res.data)

    def _do_task(self, text, parsed, now) -> AgentResult:
        title = parsed.task_title or text
        due = self._next_weekday(parsed.weekday, now) if parsed.weekday else None
        task = SarahAgent(self.db, self.actor, self.llm).create_task(title, priority=Priority.A_TRAITER.value, due_at=due)
        return AgentResult(agent=self.name, summary=f"📋 Tâche notée : « {task.title} »" + (f" pour {format_date_fr(due)}" if due else "") + ".", task_ids=[task.id])

    def _do_unknown(self, text, parsed, now) -> AgentResult:
        return AgentResult(
            agent=self.name,
            summary="Je n'ai pas bien compris. Voici ce que je sais faire : « Prépare une invitation pour dimanche », « Rappelle aux responsables la réunion de mercredi », « Prépare la communication pour la retraite de prière », « Quelles campagnes attendent ma validation ? », « Quels sont les événements des deux prochaines semaines ? », « Briefing du jour », « Qui dois-je recontacter ? », « Rappelle-moi d'appeler Jean ».",
            missing_info=["reformulation de la demande"],
        )

    def dashboard(self, now: datetime | None = None) -> dict:
        return AnalyticsAgent(self.db, self.actor, self.llm).dashboard(now)


AGENT_ROSTER = [
    {"id": "directeur", "nom": "DIRECTEUR IA", "icone": "🤖", "role": "Chef d'orchestre : comprend la demande, coordonne, prépare, présente, attend la validation."},
    {"id": "sarah", "nom": "SARAH", "icone": "👔", "role": "Secrétaire : tâches, agenda, rappels, comptes rendus, urgences."},
    {"id": "communication", "nom": "COMMUNICATION", "icone": "📢", "role": "Rédaction SMS / WhatsApp / e-mail / annonces, 7 styles."},
    {"id": "berger", "nom": "BERGER", "icone": "❤️", "role": "Suivi : nouveaux, absences, anniversaires — faits enregistrés uniquement."},
    {"id": "membres", "nom": "MEMBRES", "icone": "👥", "role": "Fiches, groupes, consentements."},
    {"id": "events", "nom": "EVENTS", "icone": "📅", "role": "Événements et rétroplanning J-14 → après."},
    {"id": "analytics", "nom": "TABLEAU DE BORD", "icone": "📊", "role": "Statistiques et rapports."},
    {"id": "securite", "nom": "SÉCURITÉ / CONFORMITÉ", "icone": "🔐", "role": "Consentement, RGPD, rôles, journal d'audit (transversal, appliqué par le moteur)."},
]
