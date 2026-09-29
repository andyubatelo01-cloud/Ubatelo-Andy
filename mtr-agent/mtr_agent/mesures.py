"""Passage des connecteurs et sondes au modèle de l'exporteur (``MesureEquipement``).

Les connecteurs remontent l'inventaire et l'état (CPU, mémoire) ; les sondes
mesurent le réseau et HTTP. ``vers_mesure`` combine les deux pour un équipement,
et ``source_connecteurs`` fournit la ``SourceMesures`` attendue par l'exporteur.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Callable, Iterable

from .connectors.base import BaseConnector
from .exporter.model import MesureEquipement, SourceMesures
from .models import DeviceStatus, Health
from .probes.http import HttpProbeResult
from .probes.network import NetworkProbeResult

CONSTRUCTEURS = {
    "teams": "Microsoft", "teams_pro": "Microsoft", "grafana": "Grafana", "cisco": "Cisco", "neat": "Neat",
    "jabra": "Jabra", "poly": "Poly/HP", "sony": "Sony", "lenovo": "Lenovo", "ochno": "Ochno",
    "zebrix": "Zebrix", "sylphony": "Sylphony",
}

TYPES = {
    "teams": "mtr", "teams_pro": "mtr", "cisco": "mtr", "neat": "mtr", "lenovo": "mtr",
    "poly": "barre_video", "jabra": "camera", "sony": "ecran", "zebrix": "affichage",
    "ochno": "tablette", "sylphony": "micro", "grafana": "service",
}

# Un équipement hors ligne rend la salle inutilisable : il compte comme critique.
SANTE = {
    Health.HEALTHY: "ok", Health.DEGRADED: "avertissement", Health.CRITICAL: "critique",
    Health.OFFLINE: "critique", Health.UNKNOWN: "inconnu",
}

# mot-clé dans le nom du périphérique -> type d'équipement de l'exporteur
TYPES_PERIPHERIQUES = (
    ("camera", "camera"), ("display", "ecran"), ("ecran", "ecran"), ("micro", "micro"),
    ("speaker", "haut_parleur"), ("pad", "tablette"), ("hdmi", "connectique"), ("usb", "connectique"),
)

# équipement -> (sonde HTTP, sonde réseau), l'une ou l'autre pouvant manquer
Sondes = Callable[[DeviceStatus], tuple[HttpProbeResult | None, NetworkProbeResult | None]]


def _ratio(pourcentage: float | None) -> float | None:
    return None if pourcentage is None else pourcentage / 100.0


def _ms_vers_s(valeur: float | None) -> float | None:
    return None if valeur is None else valeur / 1000.0


def vers_mesure(dev: DeviceStatus, http: HttpProbeResult | None = None,
                reseau: NetworkProbeResult | None = None) -> MesureEquipement:
    return MesureEquipement(
        salle=dev.room or "inconnue",
        equipement=dev.name or dev.device_id,
        constructeur=CONSTRUCTEURS.get(dev.vendor, dev.vendor),
        type_equipement=TYPES.get(dev.vendor, "autre"),
        en_ligne=dev.online,
        sante=SANTE[dev.health],
        http_disponible=http.available if http else None,
        http_temps_reponse_s=http.response_time_seconds if http and http.available else None,
        http_debit_octets_s=http.throughput_bytes_per_second if http else None,
        perte_paquets_ratio=reseau.loss_percent / 100.0 if reseau else None,
        latence_s=_ms_vers_s(reseau.latency_ms) if reseau else None,
        gigue_s=_ms_vers_s(reseau.jitter_ms) if reseau else None,
        # échecs de ce seul relevé ; source_connecteurs les cumule (compteur Prometheus)
        echecs_tcp_total=reseau.failures if reseau and reseau.method == "tcp" else None,
        cpu_ratio=_ratio(dev.cpu_percent),
        memoire_ratio=_ratio(dev.memory_percent),
    )


def _type_peripherique(nom: str) -> str:
    nom = nom.lower()
    return next((t for cle, t in TYPES_PERIPHERIQUES if cle in nom), "peripherique")


def mesures_peripheriques(dev: DeviceStatus) -> list[MesureEquipement]:
    """Une mesure par périphérique remonté par le connecteur (caméra, écran, ports...)."""
    parent = dev.name or dev.device_id
    return [
        MesureEquipement(
            salle=dev.room or "inconnue",
            equipement=f"{parent} / {nom}",
            constructeur=CONSTRUCTEURS.get(dev.vendor, dev.vendor),
            type_equipement=_type_peripherique(nom),
            present=present,
        )
        for nom, present in sorted(dev.peripherals.items())
    ]


def source_connecteurs(connecteurs: Iterable[BaseConnector], sondes: Sondes | None = None) -> SourceMesures:
    connecteurs = list(connecteurs)
    cumul_echecs: dict[tuple[str, str], int] = {}

    def lire() -> list[MesureEquipement]:
        mesures = []
        for conn in connecteurs:
            for dev in conn.collect().devices:
                http, reseau = sondes(dev) if sondes else (None, None)
                m = vers_mesure(dev, http, reseau)
                if m.echecs_tcp_total is not None:
                    cle = (dev.vendor, dev.device_id)
                    cumul_echecs[cle] = cumul_echecs.get(cle, 0) + m.echecs_tcp_total
                    m = replace(m, echecs_tcp_total=cumul_echecs[cle])
                mesures.append(m)
                mesures.extend(mesures_peripheriques(dev))
        return mesures

    return lire
