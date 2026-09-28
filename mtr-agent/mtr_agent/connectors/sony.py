"""Écrans Sony BRAVIA Professional via leur API REST locale (JSON-RPC).

Appels en lecture seule (``getPowerStatus``, ``getSystemInformation``) avec la
clé pré-partagée de l'écran. Variables : ``MTR_SONY_HOSTS`` (adresses séparées
par des virgules), ``MTR_SONY_PSK`` et ``MTR_SONY_SCHEME`` (``http`` par défaut,
les écrans n'exposant souvent pas HTTPS ; à réserver à un VLAN d'équipements).
"""

from __future__ import annotations

from typing import Any

from ..models import DeviceStatus, Health
from .base import BaseConnector, ConnectorError


class SonyConnector(BaseConnector):
    vendor = "sony"
    required_settings = ("hosts", "psk")
    default_timeout = 5.0

    def auth_headers(self) -> dict[str, str]:
        return {"X-Auth-PSK": self.setting("psk")}

    def rpc(self, host: str, service: str, method: str) -> Any:
        url = f"{self.settings.get('scheme', 'http')}://{host}/sony/{service}"
        payload = self.request_json("POST", url, json={"method": method, "id": 1, "params": [], "version": "1.0"})
        if "error" in payload:
            raise ConnectorError(f"sony: {host} {method} -> {payload['error']}")
        return payload["result"][0]

    def fetch_devices(self) -> list[DeviceStatus]:
        out = []
        for host in (h.strip() for h in self.setting("hosts").split(",")):
            if not host:
                continue
            dev = DeviceStatus(vendor=self.vendor, device_id=host, name=host)
            try:
                power = self.rpc(host, "system", "getPowerStatus").get("status")
                info = self.rpc(host, "system", "getSystemInformation")
            except ConnectorError:
                dev.health = Health.OFFLINE
            else:
                dev.online = True
                dev.model = info.get("model")
                dev.firmware = info.get("generation")
                dev.name = info.get("serial") or host
                # un écran en veille répond : il est joignable mais n'affiche rien
                dev.health = Health.HEALTHY if power == "active" else Health.DEGRADED
                dev.peripherals = {"display_on": power == "active"}
            out.append(dev)
        return out
