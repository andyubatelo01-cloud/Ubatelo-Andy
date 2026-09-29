"""Lenovo ThinkSmart (Core, Hub, One) via ThinkSmart Manager.

Variables : ``MTR_LENOVO_BASE_URL``, ``MTR_LENOVO_TOKEN``.
Correspondance des champs provisoire, à confirmer avec la documentation
ThinkSmart Manager du tenant.
"""

from __future__ import annotations

from ..models import Health
from .base import RestInventoryConnector


class LenovoConnector(RestInventoryConnector):
    vendor = "lenovo"
    devices_path = "/api/v1/devices"
    items_key = "data"
    next_key = "links.next"
    fields = {
        "device_id": "deviceId", "name": "deviceName", "room": "roomName", "model": "model",
        "firmware": "osVersion", "online": "status", "cpu": "cpuUsage", "memory": "memoryUsage",
    }
    online_values = ("Online", "online")
    health_field = "healthState"
    health_map = {"Good": Health.HEALTHY, "Warning": Health.DEGRADED, "Critical": Health.CRITICAL}
