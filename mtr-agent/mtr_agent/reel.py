"""Source réelle de l'exporteur : connecteurs configurés et sondes réseau.

Seuls les connecteurs dont les variables ``MTR_<VENDOR>_*`` obligatoires sont
définies sont interrogés. Les sondes visent les adresses listées dans
``MTR_SONDES`` sous la forme ``equipement=adresse,...`` (nom ou identifiant de
l'équipement tel que le remonte son connecteur).
"""

from __future__ import annotations

import logging
import os
from typing import Mapping

from .connectors import REGISTRY, BaseConnector
from .exporter.model import SourceMesures
from .mesures import Sondes, source_connecteurs
from .models import DeviceStatus
from .probes.http import probe_http
from .probes.network import tcp_probe

log = logging.getLogger(__name__)


def connecteurs_configures(env: Mapping[str, str] | None = None) -> list[BaseConnector]:
    env = os.environ if env is None else env
    connecteurs = [cls.from_env(env) for cls in REGISTRY.values()]
    actifs = [c for c in connecteurs if c.is_configured() and any(k.startswith(f"MTR_{c.vendor.upper()}_") for k in env)]
    log.info("Connecteurs actifs : %s", ", ".join(c.vendor for c in actifs) or "aucun")
    return actifs


def cibles_sondes(env: Mapping[str, str] | None = None) -> dict[str, str]:
    env = os.environ if env is None else env
    cibles = {}
    for paire in env.get("MTR_SONDES", "").split(","):
        nom, _, adresse = paire.partition("=")
        if nom.strip() and adresse.strip():
            cibles[nom.strip()] = adresse.strip()
    return cibles


def sondes_reseau(cibles: Mapping[str, str], port: int = 443) -> Sondes:
    def sonder(dev: DeviceStatus):
        adresse = cibles.get(dev.name) or cibles.get(dev.device_id)
        if not adresse:
            return None, None
        return probe_http(f"https://{adresse}/"), tcp_probe(adresse, port)

    return sonder


def source_reelle(env: Mapping[str, str] | None = None) -> SourceMesures:
    connecteurs = connecteurs_configures(env)
    if not connecteurs:
        raise ValueError("Aucun connecteur configuré : définissez les variables MTR_<CONSTRUCTEUR>_* d'au moins un équipement.")
    return source_connecteurs(connecteurs, sondes_reseau(cibles_sondes(env)))
