"""Ochno (hubs de salle et boîtiers de connectique) via Ochno Cloud.

Variables : ``MTR_OCHNO_BASE_URL``, ``MTR_OCHNO_TOKEN``.
Correspondance des champs provisoire, à confirmer avec la documentation Ochno.
"""

from __future__ import annotations

from .base import RestInventoryConnector


class OchnoConnector(RestInventoryConnector):
    vendor = "ochno"
    devices_path = "/api/v1/devices"
    items_key = "devices"
    fields = {
        "device_id": "id", "name": "name", "room": "room.name", "model": "type",
        "firmware": "firmware", "online": "online", "cpu": "cpu", "memory": "memory",
    }
    peripherals_field = "ports"
