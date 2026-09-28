"""Zebrix (affichage dynamique) : état des lecteurs d'écran.

Variables : ``MTR_ZEBRIX_BASE_URL``, ``MTR_ZEBRIX_TOKEN``.
Correspondance des champs provisoire, à confirmer avec la documentation Zebrix.
"""

from __future__ import annotations

from .base import RestInventoryConnector


class ZebrixConnector(RestInventoryConnector):
    vendor = "zebrix"
    devices_path = "/api/v1/players"
    items_key = "data"
    next_key = "next"
    fields = {
        "device_id": "id", "name": "name", "room": "location", "model": "hardware",
        "firmware": "version", "online": "status", "cpu": "cpu_usage", "memory": "memory_usage",
    }
    online_values = ("online", "playing")
