"""Registre des canaux : SMS, WhatsApp, e-mail (extensible : notifications push, appels…)."""
from __future__ import annotations

from ..config import get_settings
from ..models import Channel
from .base import ChannelGateway, OutboundMessage, SendResult
from .console import ConsoleGateway
from .smtp_email import SmtpGateway
from .twilio import TwilioGateway

__all__ = ["ChannelGateway", "OutboundMessage", "SendResult", "get_gateway", "reset_registry", "registry_status", "channel_diagnostics", "explain_send_error"]

_registry: dict[str, ChannelGateway] = {}


def _build(channel: str) -> ChannelGateway:
    s = get_settings()
    provider = {
        Channel.SMS.value: s.sms_provider,
        Channel.WHATSAPP.value: s.whatsapp_provider,
        Channel.EMAIL.value: s.email_provider,
    }.get(channel, "console").lower()
    if provider == "twilio" and channel in (Channel.SMS.value, Channel.WHATSAPP.value):
        gw = TwilioGateway(channel)
        return gw if gw.is_configured() else ConsoleGateway(channel)
    if provider == "smtp" and channel == Channel.EMAIL.value:
        gw = SmtpGateway(channel)
        return gw if gw.is_configured() else ConsoleGateway(channel)
    return ConsoleGateway(channel)


def get_gateway(channel: str) -> ChannelGateway:
    if channel not in _registry:
        _registry[channel] = _build(channel)
    return _registry[channel]


def reset_registry() -> None:
    _registry.clear()


def registry_status() -> list[dict]:
    return [
        {"channel": ch.value, "provider": get_gateway(ch.value).name, "live": get_gateway(ch.value).name != "console"}
        for ch in (Channel.SMS, Channel.WHATSAPP, Channel.EMAIL)
    ]


def channel_diagnostics() -> list[dict]:
    """Pour chaque canal : fournisseur demandé dans la configuration, fournisseur effectif,
    variables manquantes (noms seulement, jamais les valeurs) et conseil."""
    s = get_settings()
    out = []
    for ch in (Channel.SMS, Channel.WHATSAPP, Channel.EMAIL):
        requested = {Channel.SMS: s.sms_provider, Channel.WHATSAPP: s.whatsapp_provider, Channel.EMAIL: s.email_provider}[ch].lower()
        gw = get_gateway(ch.value)
        missing: list[str] = []
        if requested == "twilio":
            missing = [n for n, v in (("TWILIO_ACCOUNT_SID", s.twilio_account_sid), ("TWILIO_AUTH_TOKEN", s.twilio_auth_token), ("TWILIO_WHATSAPP_FROM" if ch == Channel.WHATSAPP else "TWILIO_SMS_FROM", s.twilio_whatsapp_from if ch == Channel.WHATSAPP else s.twilio_sms_from)) if not v]
        elif requested == "smtp":
            missing = [n for n, v in (("SMTP_HOST", s.smtp_host), ("SMTP_FROM", s.smtp_from)) if not v]
        var = {Channel.SMS: "SMS_PROVIDER", Channel.WHATSAPP: "WHATSAPP_PROVIDER", Channel.EMAIL: "EMAIL_PROVIDER"}[ch]
        if requested == "console":
            advice = f"Mode démonstration : aucun message ne part. Pour envoyer réellement, mettez {var}={'smtp' if ch == Channel.EMAIL else 'twilio'} dans le fichier .env et renseignez les identifiants, puis redémarrez."
        elif missing:
            advice = f"{var}={requested} est demandé mais il manque {', '.join(missing)} dans le fichier .env : le canal reste en mode démonstration."
        else:
            advice = "Canal actif : les messages validés partent réellement."
        out.append({"channel": ch.value, "demande": requested, "provider": gw.name, "live": gw.name != "console", "manquants": missing, "conseil": advice})
    return out


TWILIO_HINTS = {
    "20003": "Identifiants Twilio refusés : vérifiez TWILIO_ACCOUNT_SID et TWILIO_AUTH_TOKEN (un jeton régénéré remplace l'ancien).",
    "21608": "Compte Twilio d'essai : ce numéro n'est pas vérifié. Ajoutez-le dans « Verified Caller IDs » de la console Twilio, ou passez le compte en payant.",
    "21211": "Numéro de destination invalide : format international attendu (+33…).",
    "21212": "Numéro d'expéditeur invalide : TWILIO_SMS_FROM doit être un numéro acheté chez Twilio (ou le numéro d'essai).",
    "21606": "Le numéro d'expéditeur n'appartient pas à ce compte Twilio ou ne peut pas envoyer de SMS.",
    "21614": "Ce numéro ne peut pas recevoir de SMS (fixe ?).",
    "21408": "Envoi vers ce pays non autorisé sur le compte Twilio : activez la région dans « Geo permissions ».",
    "21610": "Ce destinataire a répondu STOP à ce numéro : il doit répondre START pour recevoir à nouveau.",
    "63007": "Expéditeur WhatsApp non reconnu : TWILIO_WHATSAPP_FROM doit être whatsapp:+… d'un expéditeur activé.",
}


def explain_send_error(error: str) -> str:
    """Traduit une erreur brute de fournisseur en conseil actionnable."""
    if not error:
        return ""
    for code, hint in TWILIO_HINTS.items():
        if code in error:
            return hint
    low = error.lower()
    if "non configuré" in low:
        return "Le canal n'est pas configuré : complétez le fichier .env puis redémarrez."
    if "authentication" in low or "535" in error:
        return "Identifiants SMTP refusés. Avec Gmail, utilisez un « mot de passe d'application » (compte Google → Sécurité), pas le mot de passe habituel."
    if "name or service not known" in low or "nodename" in low or "getaddrinfo" in low:
        return "Serveur introuvable : vérifiez SMTP_HOST (Gmail : smtp.gmail.com) et la connexion internet."
    if "timed out" in low or "réseau" in low:
        return "Pas de réponse du fournisseur : vérifiez la connexion internet."
    return ""
