"""Connecteur Twilio (SMS et WhatsApp Business Platform) via l'API REST officielle.

Le jeton d'authentification n'est jamais exposé à l'IA : seul ce module y accède.
"""
from __future__ import annotations

import httpx

from ..config import get_settings
from .base import ChannelGateway, OutboundMessage, SendResult

TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"


class TwilioGateway(ChannelGateway):
    name = "twilio"

    def __init__(self, channel: str):
        self.channel = channel
        s = get_settings()
        self.sid = s.twilio_account_sid
        self.token = s.twilio_auth_token
        self.sender = s.twilio_whatsapp_from if channel == "WHATSAPP" else s.twilio_sms_from
        self.status_callback = f"{s.base_url.rstrip('/')}/webhooks/twilio/status"

    def is_configured(self) -> bool:
        return bool(self.sid and self.token and self.sender)

    def _format_to(self, to: str) -> str:
        if self.channel == "WHATSAPP" and not to.startswith("whatsapp:"):
            return f"whatsapp:{to}"
        return to

    def send(self, message: OutboundMessage) -> SendResult:
        if not self.is_configured():
            return SendResult(ok=False, error="Twilio non configuré")
        data = {"From": self.sender, "To": self._format_to(message.to), "Body": message.body, "StatusCallback": self.status_callback}
        try:
            resp = httpx.post(TWILIO_API.format(sid=self.sid), data=data, auth=(self.sid, self.token), timeout=20)
        except httpx.HTTPError as exc:
            return SendResult(ok=False, error=f"Erreur réseau Twilio : {exc}")
        if resp.status_code >= 300:
            try:
                detail = resp.json().get("message", resp.text)
            except ValueError:
                detail = resp.text
            return SendResult(ok=False, error=f"Twilio {resp.status_code} : {detail}")
        return SendResult(ok=True, provider_id=resp.json().get("sid", ""))
