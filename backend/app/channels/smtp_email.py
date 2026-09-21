"""Connecteur e-mail SMTP (bibliothèque standard, STARTTLS)."""
from __future__ import annotations

import smtplib
import uuid
from email.message import EmailMessage

from ..config import get_settings
from .base import ChannelGateway, OutboundMessage, SendResult


class SmtpGateway(ChannelGateway):
    name = "smtp"
    channel = "EMAIL"

    def __init__(self, channel: str = "EMAIL"):
        self.channel = channel
        s = get_settings()
        self.host, self.port, self.user, self.password, self.sender = s.smtp_host, s.smtp_port, s.smtp_user, s.smtp_password, s.smtp_from

    def is_configured(self) -> bool:
        return bool(self.host and self.sender)

    def send(self, message: OutboundMessage) -> SendResult:
        if not self.is_configured():
            return SendResult(ok=False, error="SMTP non configuré")
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = self.sender, message.to, message.subject or "Message de votre communauté"
        msg["List-Unsubscribe"] = f"<mailto:{self.sender}?subject=STOP>"
        msg.set_content(message.body)
        try:
            with smtplib.SMTP(self.host, self.port, timeout=20) as server:
                server.starttls()
                if self.user:
                    server.login(self.user, self.password)
                server.send_message(msg)
        except (smtplib.SMTPException, OSError) as exc:
            return SendResult(ok=False, error=f"Erreur SMTP : {exc}")
        return SendResult(ok=True, provider_id=f"smtp-{uuid.uuid4().hex[:10]}")
