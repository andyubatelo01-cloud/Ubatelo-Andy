"""Poly/HP via l'API GraphQL de Poly Lens (lecture seule).

Identifiants d'API Lens (client credentials). Variables : ``MTR_POLY_CLIENT_ID``,
``MTR_POLY_CLIENT_SECRET`` ; ``MTR_POLY_BASE_URL`` et ``MTR_POLY_TOKEN_URL`` si
le tenant utilise d'autres points d'entrée.
"""

from __future__ import annotations

from ..models import DeviceStatus, Health
from .base import BaseConnector, ConnectorError, dig

API = "https://api.silica-prod01.io.lens.poly.com/graphql"
TOKEN = "https://login.lens.poly.com/oauth/token"

QUERY = """
query Devices($next: String) {
  deviceSearch(params: {pageSize: 100, nextToken: $next}) {
    edges { node { id name connected hardwareModel softwareVersion room { name } } }
    pageInfo { nextToken hasNextPage }
  }
}
"""


class PolyConnector(BaseConnector):
    vendor = "poly"
    required_settings = ("client_id", "client_secret")
    _token: str | None = None

    def auth_headers(self) -> dict[str, str]:
        if not self._token:
            payload = self.request_json("POST", self.settings.get("token_url", TOKEN), auth=False, json={
                "client_id": self.setting("client_id"),
                "client_secret": self.setting("client_secret"),
                "grant_type": "client_credentials",
            })
            self._token = (payload or {}).get("access_token")
            if not self._token:
                raise ConnectorError("poly: jeton absent de la réponse")
        return {"Authorization": f"Bearer {self._token}"}

    def fetch_devices(self) -> list[DeviceStatus]:
        url = self.settings.get("base_url", API)
        out: list[DeviceStatus] = []
        next_token = None
        for _ in range(100):
            payload = self.request_json("POST", url, json={"query": QUERY, "variables": {"next": next_token}})
            if payload.get("errors"):
                raise ConnectorError(f"poly: {payload['errors'][0].get('message', 'erreur GraphQL')}")
            search = dig(payload, "data.deviceSearch") or {}
            for edge in search.get("edges", []):
                n = edge["node"]
                online = bool(n.get("connected"))
                out.append(DeviceStatus(
                    vendor=self.vendor, device_id=n["id"], name=n.get("name") or "",
                    room=dig(n, "room.name"), model=n.get("hardwareModel"), firmware=n.get("softwareVersion"),
                    online=online, health=Health.HEALTHY if online else Health.OFFLINE,
                ))
            next_token = dig(search, "pageInfo.nextToken")
            if not dig(search, "pageInfo.hasNextPage") or not next_token:
                break
        return out
