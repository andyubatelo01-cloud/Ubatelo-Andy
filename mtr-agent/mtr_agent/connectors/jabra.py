"""Jabra (PanaCast, Speak) via Jabra Plus / Device Management.

Variables : ``MTR_JABRA_BASE_URL``, ``MTR_JABRA_TOKEN`` et, si le portail passe
par une passerelle Azure API Management, ``MTR_JABRA_SUBSCRIPTION_KEY``.
Correspondance des champs provisoire, à confirmer avec la documentation Jabra.
"""

from __future__ import annotations

from .base import RestInventoryConnector


class JabraConnector(RestInventoryConnector):
    vendor = "jabra"
    devices_path = "/devices"
    items_key = "devices"
    next_key = "nextLink"
    fields = {
        "device_id": "id", "name": "name", "room": "roomName", "model": "productName",
        "firmware": "firmwareVersion", "online": "status", "cpu": "cpuUsage", "memory": "memoryUsage",
    }
    peripherals_field = "peripherals"

    def auth_headers(self) -> dict[str, str]:
        headers = super().auth_headers()
        if self.settings.get("subscription_key"):
            headers["Ocp-Apim-Subscription-Key"] = self.settings["subscription_key"]
        return headers
