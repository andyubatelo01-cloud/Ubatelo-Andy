"""Canal « console » : mode démonstration / recette.

Aucun message ne quitte le serveur ; chaque envoi est journalisé et conservé
en mémoire pour les tests.
"""
from __future__ import annotations

import logging
import uuid

from .base import ChannelGateway, OutboundMessage, SendResult

logger = logging.getLogger("bureau.channels.console")


class ConsoleGateway(ChannelGateway):
    name = "console"

    def __init__(self, channel: str):
        self.channel = channel
        self.sent: list[OutboundMessage] = []

    def send(self, message: OutboundMessage) -> SendResult:
        self.sent.append(message)
        logger.info("[%s→console] à %s : %s", message.channel, message.to, message.body[:120])
        return SendResult(ok=True, provider_id=f"console-{uuid.uuid4().hex[:10]}")
