"""AGENT 02 — COMMUNICATION : rédaction SMS / WhatsApp / e-mail / annonces / invitations.

Sept styles : chaleureux, pastoral, motivant, évangélisation, événementiel,
administratif, rappel urgent. Chaque message reste court, clair et naturel.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..models import Channel, Event, MessageStyle
from .base import CHARTER, Agent, AgentResult

# Gabarits hors-ligne : {PRENOM} {EVENEMENT} {DATE} {HEURE} {LIEU} sont résolus à l'envoi.
TEMPLATES: dict[str, dict[str, str]] = {
    "invitation": {
        MessageStyle.CHALEUREUX.value: "Bonjour {PRENOM}, nous serons heureux de te retrouver pour {EVENEMENT} {DATE} à {HEURE}, {LIEU}. Que Dieu te bénisse 🙏",
        MessageStyle.PASTORAL.value: "Bonjour {PRENOM}, tu es invité(e) à {EVENEMENT} {DATE} à {HEURE} ({LIEU}). Venons ensemble nous ressourcer dans la présence de Dieu. Fraternellement.",
        MessageStyle.MOTIVANT.value: "{PRENOM}, réserve ta place ! {EVENEMENT} c'est {DATE} à {HEURE}, {LIEU}. On compte sur toi 💪",
        MessageStyle.EVANGELISATION.value: "Bonjour {PRENOM}, vous êtes le/la bienvenu(e) à {EVENEMENT} {DATE} à {HEURE}, {LIEU}. Entrée libre, venez comme vous êtes !",
        MessageStyle.EVENEMENTIEL.value: "📅 {EVENEMENT} — {DATE} à {HEURE} — {LIEU}. {PRENOM}, tu es attendu(e) ! Réponds OUI pour confirmer ta présence.",
        MessageStyle.ADMINISTRATIF.value: "Bonjour {PRENOM}, information : {EVENEMENT} aura lieu {DATE} à {HEURE}, {LIEU}. Merci de confirmer votre participation.",
        MessageStyle.RAPPEL_URGENT.value: "⚠️ {PRENOM}, rappel : {EVENEMENT} {DATE} à {HEURE}, {LIEU}. Merci de confirmer rapidement.",
    },
    "rappel": {
        MessageStyle.CHALEUREUX.value: "Bonjour {PRENOM}, petit rappel : {EVENEMENT} {DATE} à {HEURE}, {LIEU}. Au plaisir de te voir 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, nous te rappelons {EVENEMENT} {DATE} à {HEURE}. Que le Seigneur te fortifie d'ici là.",
        MessageStyle.MOTIVANT.value: "{PRENOM}, c'est bientôt ! {EVENEMENT} {DATE} à {HEURE}. Prépare-toi, ça va être fort 🔥",
        MessageStyle.EVANGELISATION.value: "Bonjour {PRENOM}, nous vous attendons {DATE} à {HEURE} pour {EVENEMENT}, {LIEU}. Vous êtes le/la bienvenu(e).",
        MessageStyle.EVENEMENTIEL.value: "🔔 Rappel : {EVENEMENT} {DATE} à {HEURE}, {LIEU}. À très vite {PRENOM} !",
        MessageStyle.ADMINISTRATIF.value: "{PRENOM}, rappel : {EVENEMENT} le {DATE} à {HEURE}, {LIEU}. Merci de votre ponctualité.",
        MessageStyle.RAPPEL_URGENT.value: "⚠️ DERNIER RAPPEL {PRENOM} : {EVENEMENT} {DATE} à {HEURE}, {LIEU}.",
    },
    "motivation": {
        MessageStyle.CHALEUREUX.value: "{PRENOM}, plus que quelques jours avant {EVENEMENT} ! Nous prions pour que ce moment soit une bénédiction pour toi 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, « Là où deux ou trois sont assemblés en mon nom, je suis au milieu d'eux. » Rendez-vous {DATE} pour {EVENEMENT}.",
        MessageStyle.MOTIVANT.value: "J-3 {PRENOM} ! {EVENEMENT} approche. Invite quelqu'un, viens avec attente, Dieu a préparé quelque chose 🔥",
        MessageStyle.EVANGELISATION.value: "{PRENOM}, un rendez-vous d'espérance vous attend {DATE} : {EVENEMENT}. Venez avec vos proches.",
        MessageStyle.EVENEMENTIEL.value: "J-3 avant {EVENEMENT} 🎉 {DATE} à {HEURE}, {LIEU}. Prêt(e) {PRENOM} ?",
        MessageStyle.ADMINISTRATIF.value: "{PRENOM}, {EVENEMENT} approche ({DATE}). Merci de finaliser votre inscription.",
        MessageStyle.RAPPEL_URGENT.value: "{PRENOM}, J-3 : {EVENEMENT} {DATE}. Confirme ta présence dès aujourd'hui.",
    },
    "pratique": {
        MessageStyle.CHALEUREUX.value: "{PRENOM}, c'est dans quelques heures ! {EVENEMENT} à {HEURE}, {LIEU}. Ouverture des portes 30 min avant. À tout à l'heure 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, rendez-vous à {HEURE} ({LIEU}) pour {EVENEMENT}. Viens avec un cœur disposé.",
        MessageStyle.MOTIVANT.value: "H-3 {PRENOM} ! {EVENEMENT} à {HEURE}, {LIEU}. Sois à l'heure, on commence fort !",
        MessageStyle.EVANGELISATION.value: "Bonjour {PRENOM}, {EVENEMENT} commence à {HEURE}, {LIEU}. Accueil et parking sur place.",
        MessageStyle.EVENEMENTIEL.value: "📍 {LIEU} · ⏰ {HEURE} · {EVENEMENT}. Infos pratiques : arrivez 15 min en avance. À tout de suite {PRENOM} !",
        MessageStyle.ADMINISTRATIF.value: "{PRENOM}, informations pratiques : {EVENEMENT}, {HEURE}, {LIEU}. Accueil dès {HEURE}.",
        MessageStyle.RAPPEL_URGENT.value: "⚠️ {PRENOM}, {EVENEMENT} commence à {HEURE} ({LIEU}). Ne tarde pas !",
    },
    "remerciement": {
        MessageStyle.CHALEUREUX.value: "Merci {PRENOM} d'avoir été avec nous pour {EVENEMENT} ! Ta présence nous a réjouis. Que Dieu te garde 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, merci pour ta présence à {EVENEMENT}. Que ce que tu as reçu porte du fruit dans ta semaine.",
        MessageStyle.MOTIVANT.value: "Quel moment {PRENOM} ! Merci d'avoir été là pour {EVENEMENT}. Rendez-vous très vite 🔥",
        MessageStyle.EVANGELISATION.value: "Merci {PRENOM} d'être venu(e) à {EVENEMENT}. Vous êtes toujours le/la bienvenu(e) parmi nous.",
        MessageStyle.EVENEMENTIEL.value: "🎉 Merci {PRENOM} ! {EVENEMENT} était un succès grâce à toi. Photos et prochaines dates bientôt.",
        MessageStyle.ADMINISTRATIF.value: "Merci {PRENOM} pour votre participation à {EVENEMENT}. Les prochaines informations vous seront communiquées prochainement.",
        MessageStyle.RAPPEL_URGENT.value: "Merci {PRENOM} pour ta présence à {EVENEMENT}.",
    },
    "encouragement": {
        MessageStyle.CHALEUREUX.value: "Bonjour {PRENOM}, nous pensons à toi. Cela fait un moment que nous ne t'avons pas vu(e) et tu nous manques. Au plaisir de te retrouver bientôt 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, tu as une place parmi nous. Si tu souhaites échanger ou prier avec quelqu'un, réponds à ce message. Fraternellement, le pasteur.",
        MessageStyle.MOTIVANT.value: "{PRENOM}, la famille n'est pas complète sans toi ! On espère te revoir très bientôt 💪",
        MessageStyle.EVANGELISATION.value: "Bonjour {PRENOM}, notre porte reste grande ouverte. Nous serions heureux de vous revoir.",
        MessageStyle.EVENEMENTIEL.value: "{PRENOM}, de belles rencontres arrivent. Reviens nous voir, tu es attendu(e) !",
        MessageStyle.ADMINISTRATIF.value: "Bonjour {PRENOM}, nous n'avons pas eu de nouvelles récemment. N'hésitez pas à nous contacter.",
        MessageStyle.RAPPEL_URGENT.value: "{PRENOM}, nous aimerions avoir de tes nouvelles. Réponds-nous quand tu peux.",
    },
    "bienvenue": {
        MessageStyle.CHALEUREUX.value: "Bienvenue {PRENOM} ! Nous sommes heureux de t'accueillir dans la communauté. N'hésite pas à nous écrire pour toute question 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, sois le/la bienvenu(e) parmi nous. Nous prions pour que tu trouves ici une famille. Le pasteur.",
        MessageStyle.MOTIVANT.value: "Bienvenue à bord {PRENOM} ! Une belle aventure commence 🎉",
        MessageStyle.EVANGELISATION.value: "Bienvenue {PRENOM}. Merci de nous avoir rejoints, nous sommes là pour vous accompagner.",
        MessageStyle.EVENEMENTIEL.value: "Bienvenue {PRENOM} ! Prochaine occasion de se retrouver : {EVENEMENT} {DATE}.",
        MessageStyle.ADMINISTRATIF.value: "Bienvenue {PRENOM}. Votre fiche a été créée. Vous pouvez à tout moment modifier vos préférences de communication.",
        MessageStyle.RAPPEL_URGENT.value: "Bienvenue {PRENOM} !",
    },
    "anniversaire": {
        MessageStyle.CHALEUREUX.value: "Joyeux anniversaire {PRENOM} ! 🎂 Toute la communauté te souhaite une année remplie de la bonté de Dieu.",
        MessageStyle.PASTORAL.value: "{PRENOM}, en ce jour d'anniversaire, que le Seigneur te bénisse et te garde. Joyeux anniversaire !",
        MessageStyle.MOTIVANT.value: "Bon anniversaire {PRENOM} ! 🎉 Une nouvelle année pour briller !",
        MessageStyle.EVANGELISATION.value: "Joyeux anniversaire {PRENOM} ! Nous pensons à vous en ce jour spécial.",
        MessageStyle.EVENEMENTIEL.value: "🎂 Joyeux anniversaire {PRENOM} !",
        MessageStyle.ADMINISTRATIF.value: "Joyeux anniversaire {PRENOM}.",
        MessageStyle.RAPPEL_URGENT.value: "Joyeux anniversaire {PRENOM} !",
    },
    "mois": {
        MessageStyle.CHALEUREUX.value: "Bonjour {PRENOM}, bon début de mois ! Que ces prochaines semaines soient remplies de paix et de joie. Nous sommes là pour toi 🙏",
        MessageStyle.PASTORAL.value: "{PRENOM}, ce mois-ci, gardons les yeux fixés sur l'essentiel. « Cherchez premièrement le royaume de Dieu. » Bon mois à toi.",
        MessageStyle.MOTIVANT.value: "Nouveau mois, nouvelles grâces {PRENOM} ! Avançons ensemble 💪",
        MessageStyle.EVANGELISATION.value: "Bonjour {PRENOM}, bon mois à vous. Nos rencontres restent ouvertes à tous.",
        MessageStyle.EVENEMENTIEL.value: "Bon mois {PRENOM} ! Le programme des prochaines semaines arrive très vite.",
        MessageStyle.ADMINISTRATIF.value: "Bonjour {PRENOM}, voici les informations du mois. Merci de consulter le programme.",
        MessageStyle.RAPPEL_URGENT.value: "{PRENOM}, informations importantes pour ce mois : merci de lire attentivement.",
    },
    "annonce": {
        MessageStyle.CHALEUREUX.value: "Bonjour {PRENOM}, une information importante pour toi : {EVENEMENT} — {DATE} à {HEURE}, {LIEU}.",
        MessageStyle.PASTORAL.value: "{PRENOM}, nous avons le plaisir de t'annoncer {EVENEMENT}, {DATE} à {HEURE}. Que Dieu prépare nos cœurs.",
        MessageStyle.MOTIVANT.value: "Grande nouvelle {PRENOM} ! {EVENEMENT} arrive {DATE}. Note la date 🔥",
        MessageStyle.EVANGELISATION.value: "{PRENOM}, annonce : {EVENEMENT} le {DATE} à {HEURE}, {LIEU}. Ouvert à tous.",
        MessageStyle.EVENEMENTIEL.value: "📣 {PRENOM}, annonce — {EVENEMENT} · {DATE} · {HEURE} · {LIEU}",
        MessageStyle.ADMINISTRATIF.value: "{PRENOM}, annonce officielle : {EVENEMENT} se tiendra le {DATE} à {HEURE}, {LIEU}.",
        MessageStyle.RAPPEL_URGENT.value: "⚠️ {PRENOM}, annonce importante : {EVENEMENT} — {DATE} à {HEURE}, {LIEU}.",
    },
}

KIND_LABELS = {
    "invitation": "Invitation", "rappel": "Rappel", "motivation": "Message de motivation", "pratique": "Rappel pratique",
    "remerciement": "Message de remerciement", "encouragement": "Message d'encouragement", "bienvenue": "Message de bienvenue",
    "anniversaire": "Message d'anniversaire", "mois": "Message du mois", "annonce": "Annonce",
}


class DraftedMessage(BaseModel):
    message: str = Field(description="Le message final, avec les variables {PRENOM} {EVENEMENT} {DATE} {HEURE} {LIEU} si pertinent")
    subject: str = Field(default="", description="Objet, uniquement pour un e-mail")


class CommunicationAgent(Agent):
    name = "COMMUNICATION"
    icon = "📢"
    description = "Rédige SMS, WhatsApp, e-mails, annonces et invitations, dans le ton adapté au public."

    def draft(
        self,
        kind: str,
        style: str = MessageStyle.CHALEUREUX.value,
        channel: str = Channel.SMS.value,
        event: Event | None = None,
        audience_label: str = "les membres",
        instructions: str = "",
    ) -> AgentResult:
        kind = kind if kind in TEMPLATES else "annonce"
        style = style if style in TEMPLATES[kind] else MessageStyle.CHALEUREUX.value
        template = TEMPLATES[kind][style]
        # Sans événement, on retire les variables d'événement pour ne pas bloquer la campagne.
        if event is None:
            template = self._strip_event_vars(template)
        subject = f"{KIND_LABELS[kind]} — {event.name}" if event and channel == Channel.EMAIL.value else (KIND_LABELS[kind] if channel == Channel.EMAIL.value else "")
        message = template
        source = "gabarit"

        if self.llm.name != "template":
            drafted = self._draft_with_llm(kind, style, channel, event, audience_label, instructions, template)
            if drafted and drafted.message.strip():
                message, source = drafted.message.strip(), "ia"
                if drafted.subject and channel == Channel.EMAIL.value:
                    subject = drafted.subject
        result = AgentResult(
            agent=self.name,
            summary=f"{KIND_LABELS[kind]} rédigé(e) en style {style} pour {audience_label} ({channel}).",
            data={"message": message, "subject": subject, "style": style, "kind": kind, "channel": channel, "source": source},
        )
        self.trace(f"{kind}/{style}/{channel} {instructions}", "draft", result)
        return result

    def variants(self, kind: str, channel: str = Channel.SMS.value, event: Event | None = None) -> dict[str, str]:
        """Les 7 styles d'un même message, pour que le pasteur choisisse."""
        out = {}
        for style in TEMPLATES.get(kind, TEMPLATES["annonce"]):
            out[style] = self.draft(kind, style, channel, event).data["message"]
        return out

    @staticmethod
    def _strip_event_vars(template: str) -> str:
        cleaned = template
        for chunk in (" pour {EVENEMENT} {DATE} à {HEURE}, {LIEU}", " {EVENEMENT} {DATE} à {HEURE}, {LIEU}", " : {EVENEMENT} {DATE}", " {DATE} à {HEURE} ({LIEU})", "{EVENEMENT} — {DATE} à {HEURE}, {LIEU}"):
            cleaned = cleaned.replace(chunk, "")
        for var in ("{EVENEMENT}", "{DATE}", "{HEURE}", "{LIEU}"):
            cleaned = cleaned.replace(var, "")
        return " ".join(cleaned.split()).replace(" ,", ",").replace(" .", ".")

    def _draft_with_llm(self, kind, style, channel, event, audience_label, instructions, template) -> DraftedMessage | None:
        limit = "160 caractères maximum" if channel == Channel.SMS.value else ("300 caractères maximum" if channel == Channel.WHATSAPP.value else "un e-mail court de 4 à 8 lignes")
        event_desc = "Aucun événement précis." if event is None else f"Événement : {event.name}. Utilise les variables {{EVENEMENT}}, {{DATE}}, {{HEURE}}, {{LIEU}} au lieu d'écrire les valeurs."
        prompt = (
            f"Type de message : {KIND_LABELS[kind]}. Style : {style}. Canal : {channel} ({limit}). Public : {audience_label}.\n"
            f"{event_desc}\nCommence par une salutation avec {{PRENOM}}.\n"
            f"Exemple de ton attendu : « {template} »\n"
            + (f"Consignes du pasteur : {instructions}\n" if instructions else "")
            + "Réponds avec le message final uniquement."
        )
        try:
            return self.llm.generate_structured(CHARTER, prompt, DraftedMessage)
        except Exception as exc:  # noqa: BLE001 - le gabarit reste disponible
            import logging

            logging.getLogger("bureau.agents").warning("Rédaction IA indisponible (%s) : gabarit utilisé.", exc)
            return None
