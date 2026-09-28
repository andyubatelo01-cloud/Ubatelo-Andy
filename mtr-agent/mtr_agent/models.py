"""Modèles de données communs à tous les connecteurs et sondes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Health(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

    @property
    def code(self) -> int:
        """Valeur numérique (0 = sain, plus haut = pire)."""
        return {"healthy": 0, "degraded": 1, "critical": 2, "offline": 3, "unknown": -1}[self.value]


@dataclass
class DeviceStatus:
    vendor: str
    device_id: str
    name: str = ""
    room: str | None = None
    model: str | None = None
    online: bool = False
    health: Health = Health.UNKNOWN
    firmware: str | None = None
    cpu_percent: float | None = None
    memory_percent: float | None = None
    # nom du périphérique -> connecté ou non
    peripherals: dict[str, bool] = field(default_factory=dict)


@dataclass
class CollectResult:
    vendor: str
    devices: list[DeviceStatus] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def up(self) -> bool:
        return not self.errors
