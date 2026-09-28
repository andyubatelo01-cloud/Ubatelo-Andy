"""Cisco Room/Board/Desk via l'API Webex (Control Hub).

Jeton d'intégration ou de bot avec le scope ``spark-admin:devices_read``.
Variables : ``MTR_CISCO_TOKEN`` (et ``MTR_CISCO_BASE_URL`` pour un autre point d'entrée).
"""

from __future__ import annotations

from ..models import DeviceStatus, Health
from .base import BaseConnector

WEBEX = "https://webexapis.com/v1"

STATUS = {
    "connected": Health.HEALTHY,
    "connected_with_issues": Health.DEGRADED,
    "disconnected": Health.OFFLINE,
    "offline_expired": Health.OFFLINE,
    "offline_deep_sleep": Health.OFFLINE,
}


class CiscoConnector(BaseConnector):
    vendor = "cisco"
    required_settings = ("token",)

    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.setting('token')}"}

    def fetch_devices(self) -> list[DeviceStatus]:
        base = self.base_url(WEBEX)
        rooms = {w["id"]: w.get("displayName") for w in self.get_json(f"{base}/workspaces", params={"max": 1000})
                 .get("items", [])}
        out = []
        for d in self.get_json(f"{base}/devices", params={"max": 1000}).get("items", []):
            health = STATUS.get(d.get("connectionStatus", ""), Health.UNKNOWN)
            if health == Health.HEALTHY and d.get("errorCodes"):
                health = Health.DEGRADED
            out.append(DeviceStatus(
                vendor=self.vendor,
                device_id=d["id"],
                name=d.get("displayName", ""),
                room=rooms.get(d.get("workspaceId")),
                model=d.get("product"),
                firmware=d.get("software"),
                online=health in (Health.HEALTHY, Health.DEGRADED),
                health=health,
            ))
        return out
