"""Interface commune des canaux de communication.

Un canal ne sait rien des campagnes ni de la validation : il reçoit un
`OutboundMessage` déjà autorisé par le moteur de campagnes et renvoie un résultat.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OutboundMessage:
    channel: str
    to: str
    body: str
    subject: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class SendResult:
    ok: bool
    provider_id: str = ""
    error: str = ""


class ChannelGateway:
    """Classe de base. `name` identifie le fournisseur (console, twilio, smtp...)."""

    name = "base"
    channel = ""

    def is_configured(self) -> bool:
        return True

    def send(self, message: OutboundMessage) -> SendResult:  # pragma: no cover - interface
        raise NotImplementedError


class ChannelError(RuntimeError):
    pass
