"""Microsoft Teams Rooms via Microsoft Graph (``/teamwork/devices``).

Application Entra ID en mode client credentials, permission
``TeamworkDevice.Read.All``. Variables : ``MTR_TEAMS_TENANT_ID``,
``MTR_TEAMS_CLIENT_ID``, ``MTR_TEAMS_CLIENT_SECRET``.
"""

from __future__ import annotations

import time
from typing import Any, Mapping

from ..models import DeviceStatus, Health
from .base import BaseConnector, ConnectorError, dig

GRAPH = "https://graph.microsoft.com/v1.0"
LOGIN = "https://login.microsoftonline.com"

GRAPH_HEALTH = {
    "healthy": Health.HEALTHY,
    "nonUrgent": Health.DEGRADED,
    "critical": Health.CRITICAL,
    "offline": Health.OFFLINE,
    "unknown": Health.UNKNOWN,
}


class GraphConnector(BaseConnector):
    required_settings = ("tenant_id", "client_id", "client_secret")
    _token: str | None = None
    _token_expiry: float = 0.0

    def graph_url(self) -> str:
        return self.settings.get("graph_url", GRAPH).rstrip("/")

    def access_token(self) -> str:
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        url = f"{self.settings.get('login_url', LOGIN).rstrip('/')}/{self.setting('tenant_id')}/oauth2/v2.0/token"
        payload = self.request_json("POST", url, auth=False, data={
            "grant_type": "client_credentials",
            "client_id": self.setting("client_id"),
            "client_secret": self.setting("client_secret"),
            "scope": "https://graph.microsoft.com/.default",
        })
        token = (payload or {}).get("access_token")
        if not token:
            raise ConnectorError(f"{self.vendor}: jeton Graph absent de la réponse")
        self._token = token
        self._token_expiry = time.time() + float(payload.get("expires_in", 3600))
        return token

    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token()}"}

    def graph_list(self, path: str) -> list[Mapping[str, Any]]:
        url: str | None = self.graph_url() + path
        items: list[Mapping[str, Any]] = []
        for _ in range(100):
            if not url:
                break
            payload = self.get_json(url)
            items.extend(payload.get("value", []))
            url = payload.get("@odata.nextLink")
        return items

    def list_graph_devices(self) -> list[Mapping[str, Any]]:
        return self.graph_list("/teamwork/devices")


def graph_device_status(vendor: str, item: Mapping[str, Any]) -> DeviceStatus:
    health = GRAPH_HEALTH.get(str(item.get("healthStatus")), Health.UNKNOWN)
    return DeviceStatus(
        vendor=vendor,
        device_id=str(item.get("id")),
        name=str(dig(item, "currentUser.displayName") or dig(item, "hardwareDetail.serialNumber") or ""),
        model=" ".join(x for x in (dig(item, "hardwareDetail.manufacturer"), dig(item, "hardwareDetail.model")) if x)
        or None,
        room=dig(item, "currentUser.displayName"),
        online=health not in (Health.OFFLINE, Health.UNKNOWN),
        health=health,
    )


class TeamsRoomsConnector(GraphConnector):
    vendor = "teams"

    def fetch_devices(self) -> list[DeviceStatus]:
        return [graph_device_status(self.vendor, d) for d in self.list_graph_devices()]
