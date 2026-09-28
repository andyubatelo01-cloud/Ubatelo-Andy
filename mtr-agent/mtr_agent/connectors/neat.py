"""Neat (Bar, Board, Pad) via l'API Neat Pulse.

Clé d'API Pulse et identifiant d'organisation. Variables : ``MTR_NEAT_TOKEN``,
``MTR_NEAT_ORG_ID`` ; ``MTR_NEAT_BASE_URL`` pour un autre point d'entrée.
Correspondance des champs à confirmer avec la documentation Pulse du tenant.
"""

from __future__ import annotations

from .base import RestInventoryConnector


class NeatConnector(RestInventoryConnector):
    vendor = "neat"
    required_settings = ("token", "org_id")
    default_base_url = "https://api.pulse.neat.no/v1"
    items_key = "endpoints"
    fields = {
        "device_id": "id", "name": "name", "room": "roomName", "model": "model",
        "firmware": "firmwareVersion", "online": "connected", "cpu": "cpuUsage", "memory": "memoryUsage",
    }
    peripherals_field = "peripherals"

    @property
    def devices_path(self) -> str:  # type: ignore[override]
        return f"/orgs/{self.setting('org_id')}/endpoints"
