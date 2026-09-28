"""Teams Rooms Pro Management : santé détaillée des salles.

Le portail Pro Management n'a pas d'API publique ; les mêmes signaux (connexion
Teams/Exchange, caméras, écrans, micros, haut-parleurs, mises à jour) sont
exposés par Graph sur ``/teamwork/devices/{id}/health``. Même application Entra
ID que le connecteur Teams : ``MTR_TEAMS_PRO_TENANT_ID``, ``..._CLIENT_ID``,
``..._CLIENT_SECRET``.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..models import DeviceStatus, Health
from .base import dig
from .teams import GraphConnector, graph_device_status

PERIPHERALS = (
    "roomCameraHealth", "contentCameraHealth", "conferencingCameraHealth",
    "speakerHealth", "communicationSpeakerHealth", "microphoneHealth",
)


def _connected(block: Any) -> bool | None:
    status = dig(block, "connection.connectionStatus")
    return None if status is None else status == "connected"


def parse_health(health: Mapping[str, Any]) -> tuple[dict[str, bool], list[str]]:
    """Renvoie (périphériques connectés, liste des anomalies)."""
    peripherals: dict[str, bool] = {}
    issues: list[str] = []
    ph = health.get("peripheralsHealth") or {}
    for key in PERIPHERALS:
        block = ph.get(key)
        up = _connected(block)
        if up is None:
            continue
        peripherals[key.removesuffix("Health")] = up
        if not up and not block.get("isOptional", False):
            issues.append(key)
    for i, display in enumerate(ph.get("roomDisplayHealthCollection") or []):
        up = _connected(display)
        if up is not None:
            peripherals[f"roomDisplay{i + 1}"] = up
            if not up and not display.get("isOptional", False):
                issues.append(f"roomDisplay{i + 1}")
    for key in ("teamsConnection", "exchangeConnection"):
        if dig(health, f"loginStatus.{key}.connectionStatus") not in (None, "connected"):
            issues.append(key)
    for key in ("osSoftwareUpdateStatus", "teamsClientSoftwareUpdateStatus"):
        if dig(health, f"softwareUpdateHealth.{key}.softwareFreshness") == "updateAvailable":
            issues.append(key)
    return peripherals, issues


class TeamsRoomsProConnector(GraphConnector):
    vendor = "teams_pro"

    def fetch_devices(self) -> list[DeviceStatus]:
        out: list[DeviceStatus] = []
        for item in self.list_graph_devices():
            if item.get("deviceType") != "teamsRoom":
                continue
            dev = graph_device_status(self.vendor, item)
            health = self.get_json(f"{self.graph_url()}/teamwork/devices/{item['id']}/health")
            dev.peripherals, issues = parse_health(health or {})
            if dig(health, "connection.connectionStatus") == "disconnected":
                dev.online, dev.health = False, Health.OFFLINE
            elif issues and dev.health == Health.HEALTHY:
                dev.health = Health.DEGRADED
            out.append(dev)
        return out
