"""Registre des canaux : SMS, WhatsApp, e-mail (extensible : notifications push, appels…)."""
from __future__ import annotations

from ..config import get_settings
from ..models import Channel
from .base import ChannelGateway, OutboundMessage, SendResult
from .console import ConsoleGateway
from .smtp_email import SmtpGateway
from .twilio import TwilioGateway

__all__ = ["ChannelGateway", "OutboundMessage", "SendResult", "get_gateway", "reset_registry", "registry_status"]

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
