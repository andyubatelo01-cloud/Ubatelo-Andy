"""Classe de base des connecteurs.

Un connecteur lit l'état des équipements d'un constructeur ou d'un service, en
lecture seule, et le convertit en ``DeviceStatus``. Les seuls appels sortants sont
l'authentification et la lecture d'inventaire : aucune donnée de l'agent n'est
envoyée vers un tiers.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Iterable, Mapping

from ..config import mask, vendor_settings
from ..http_client import HttpClient, UrllibHttpClient
from ..models import CollectResult, DeviceStatus, Health


class ConnectorError(RuntimeError):
    pass


class BaseConnector(ABC):
    vendor: ClassVar[str]
    required_settings: ClassVar[tuple[str, ...]] = ()
    default_timeout: ClassVar[float] = 10.0

    def __init__(self, settings: Mapping[str, str], http: HttpClient | None = None) -> None:
        self.settings = dict(settings)
        self.http = http or UrllibHttpClient(self.settings.get("ca_file"))
        self.timeout = float(self.settings.get("timeout", self.default_timeout))

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None, http: HttpClient | None = None):
        return cls(vendor_settings(cls.vendor, env), http)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({mask(self.settings)})"

    # -- configuration -------------------------------------------------------
    def missing_settings(self) -> list[str]:
        return [k for k in self.required_settings if not self.settings.get(k)]

    def is_configured(self) -> bool:
        return not self.missing_settings()

    def setting(self, key: str, default: str | None = None) -> str:
        value = self.settings.get(key, default)
        if value is None:
            raise ConnectorError(f"{self.vendor}: réglage MTR_{self.vendor.upper()}_{key.upper()} manquant")
        return value

    def base_url(self, default: str | None = None) -> str:
        return self.setting("base_url", default).rstrip("/")

    # -- HTTP ----------------------------------------------------------------
    def auth_headers(self) -> dict[str, str]:
        return {}

    def request_json(self, method: str, url: str, *, headers: Mapping[str, str] | None = None,
                     params: Mapping[str, Any] | None = None, json: Any = None,
                     data: Mapping[str, str] | None = None, auth: bool = True) -> Any:
        hdrs = {"Accept": "application/json", **(self.auth_headers() if auth else {}), **(headers or {})}
        resp = self.http.request(method, url, headers=hdrs, params=params, json=json, data=data,
                                 timeout=self.timeout)
        if not resp.ok:
            # l'URL est journalisée, jamais les en-têtes (ils portent les jetons)
            raise ConnectorError(f"{self.vendor}: {method} {url} -> HTTP {resp.status}")
        try:
            return resp.json()
        except ValueError as exc:
            raise ConnectorError(f"{self.vendor}: réponse non JSON pour {url}") from exc

    def get_json(self, url: str, **kw: Any) -> Any:
        return self.request_json("GET", url, **kw)

    # -- collecte ------------------------------------------------------------
    @abstractmethod
    def fetch_devices(self) -> list[DeviceStatus]:
        ...

    def collect(self) -> CollectResult:
        result = CollectResult(self.vendor)
        missing = self.missing_settings()
        if missing:
            result.errors.append(f"réglages manquants : {', '.join(missing)}")
            return result
        start = time.perf_counter()
        try:
            result.devices = self.fetch_devices()
        except Exception as exc:  # une panne constructeur ne doit pas arrêter l'agent
            result.errors.append(str(exc))
        result.duration_seconds = time.perf_counter() - start
        return result


def dig(obj: Any, path: str, default: Any = None) -> Any:
    """Lit ``a.b.c`` dans un dictionnaire imbriqué."""
    for part in path.split("."):
        if not isinstance(obj, Mapping) or part not in obj:
            return default
        obj = obj[part]
    return obj


def to_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


class RestInventoryConnector(BaseConnector):
    """Connecteur générique pour une API REST qui liste des équipements en JSON.

    Les sous-classes déclarent le chemin d'inventaire et la correspondance des
    champs. Quand la documentation constructeur précise un champ différent, seule
    la table ``fields`` change.
    """

    devices_path: ClassVar[str] = "/devices"
    items_key: ClassVar[str | None] = None  # None : la réponse est directement une liste
    next_key: ClassVar[str | None] = None   # champ contenant l'URL de page suivante
    fields: ClassVar[dict[str, str]] = {
        "device_id": "id", "name": "name", "room": "room", "model": "model",
        "firmware": "firmware", "online": "online", "cpu": "cpu", "memory": "memory",
    }
    online_values: ClassVar[Iterable[Any]] = (True, "online", "connected", "ONLINE", "CONNECTED")
    health_field: ClassVar[str | None] = None
    health_map: ClassVar[dict[str, Health]] = {}
    peripherals_field: ClassVar[str | None] = None
    default_base_url: ClassVar[str | None] = None
    required_settings = ("base_url", "token")

    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.setting('token')}"}

    def list_items(self) -> list[Mapping[str, Any]]:
        url: str | None = self.base_url(self.default_base_url) + self.devices_path
        items: list[Mapping[str, Any]] = []
        for _ in range(100):  # garde-fou contre une pagination sans fin
            if not url:
                break
            payload = self.get_json(url)
            page = dig(payload, self.items_key) if self.items_key else payload
            if not isinstance(page, list):
                raise ConnectorError(f"{self.vendor}: format d'inventaire inattendu")
            items.extend(page)
            url = dig(payload, self.next_key) if self.next_key and isinstance(payload, Mapping) else None
        return items

    def parse_item(self, item: Mapping[str, Any]) -> DeviceStatus:
        f = self.fields
        online = dig(item, f["online"]) in tuple(self.online_values)
        health = Health.HEALTHY if online else Health.OFFLINE
        if self.health_field:
            raw = dig(item, self.health_field)
            health = self.health_map.get(str(raw), health)
        peripherals: dict[str, bool] = {}
        if self.peripherals_field:
            for p in dig(item, self.peripherals_field, []) or []:
                peripherals[str(p.get("name") or p.get("type"))] = dig(p, f["online"]) in tuple(self.online_values)
        return DeviceStatus(
            vendor=self.vendor,
            device_id=str(dig(item, f["device_id"])),
            name=str(dig(item, f["name"], "") or ""),
            room=dig(item, f["room"]),
            model=dig(item, f["model"]),
            firmware=dig(item, f["firmware"]),
            online=online,
            health=health,
            cpu_percent=to_float(dig(item, f["cpu"])),
            memory_percent=to_float(dig(item, f["memory"])),
            peripherals=peripherals,
        )

    def fetch_devices(self) -> list[DeviceStatus]:
        return [self.parse_item(i) for i in self.list_items()]
