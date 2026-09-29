"""Grafana : disponibilité de l'instance qui affiche les tableaux de bord.

Lecture de ``/api/health`` (pas d'écriture dans Grafana). Variables :
``MTR_GRAFANA_BASE_URL`` et, si l'instance l'exige, ``MTR_GRAFANA_TOKEN``
(compte de service en lecture seule).
"""

from __future__ import annotations

from urllib.parse import urlparse

from ..models import DeviceStatus, Health
from .base import BaseConnector


class GrafanaConnector(BaseConnector):
    vendor = "grafana"
    required_settings = ("base_url",)

    def auth_headers(self) -> dict[str, str]:
        token = self.settings.get("token")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def fetch_devices(self) -> list[DeviceStatus]:
        base = self.base_url()
        payload = self.get_json(f"{base}/api/health") or {}
        db_ok = payload.get("database") == "ok"
        return [DeviceStatus(
            vendor=self.vendor,
            device_id=urlparse(base).netloc or base,
            name="Grafana",
            model="grafana",
            firmware=payload.get("version"),
            online=True,
            health=Health.HEALTHY if db_ok else Health.DEGRADED,
            peripherals={"database": db_ok},
        )]
