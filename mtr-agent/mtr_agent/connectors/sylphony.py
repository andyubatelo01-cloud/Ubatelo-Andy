"""Sylphony : équipements supervisés par la plateforme Sylphony.

Variables : ``MTR_SYLPHONY_BASE_URL``, ``MTR_SYLPHONY_TOKEN``.
Correspondance des champs provisoire, à confirmer avec la documentation Sylphony.
"""

from __future__ import annotations

from ..models import Health
from .base import RestInventoryConnector


class SylphonyConnector(RestInventoryConnector):
    vendor = "sylphony"
    devices_path = "/api/v1/devices"
    items_key = "items"
    fields = {
        "device_id": "id", "name": "label", "room": "room", "model": "model",
        "firmware": "firmware", "online": "state", "cpu": "metrics.cpu", "memory": "metrics.memory",
    }
    online_values = ("up", "online")
    health_field = "alarm"
    health_map = {"none": Health.HEALTHY, "minor": Health.DEGRADED, "major": Health.CRITICAL}
