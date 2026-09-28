"""Collecteur Prometheus : convertit les mesures en métriques ``mtr_*``."""

from __future__ import annotations

import logging
import time
from typing import Iterator

from prometheus_client.core import (
    CounterMetricFamily,
    GaugeMetricFamily,
    Metric,
)
from prometheus_client.registry import Collector

from .model import MesureEquipement, SourceMesures

log = logging.getLogger(__name__)

LABELS = ["salle", "equipement", "constructeur", "type"]

# (attribut, nom de métrique, aide, type)
DEFINITIONS = [
    ("http_disponible", "mtr_http_up", "Disponibilité HTTP de l'équipement (1 = joignable).", "gauge"),
    ("http_temps_reponse_s", "mtr_http_response_seconds", "Temps de réponse HTTP en secondes.", "gauge"),
    ("http_debit_octets_s", "mtr_http_throughput_bytes_per_second", "Débit HTTP en octets par seconde.", "gauge"),
    ("perte_paquets_ratio", "mtr_packet_loss_ratio", "Perte de paquets (0 à 1).", "gauge"),
    ("latence_s", "mtr_latency_seconds", "Latence réseau aller-retour en secondes.", "gauge"),
    ("gigue_s", "mtr_jitter_seconds", "Gigue réseau en secondes.", "gauge"),
    ("echecs_tcp_total", "mtr_tcp_connect_failures", "Nombre cumulé d'échecs de connexion TCP.", "counter"),
    ("cpu_ratio", "mtr_cpu_usage_ratio", "Utilisation CPU (0 à 1).", "gauge"),
    ("memoire_ratio", "mtr_memory_usage_ratio", "Utilisation mémoire (0 à 1).", "gauge"),
]


def _labels(m: MesureEquipement) -> list[str]:
    return [m.salle, m.equipement, m.constructeur, m.type_equipement]


class CollecteurMTR(Collector):
    """Interroge la source à chaque scrape et expose les dernières valeurs."""

    def __init__(self, source: SourceMesures) -> None:
        self._source = source

    def collect(self) -> Iterator[Metric]:
        debut = time.monotonic()
        succes = 1.0
        try:
            mesures = list(self._source())
        except Exception:  # une source en panne ne doit pas faire tomber /metrics
            log.exception("Échec de lecture de la source de mesures")
            mesures = []
            succes = 0.0

        familles = {}
        for attr, nom, aide, genre in DEFINITIONS:
            cls = CounterMetricFamily if genre == "counter" else GaugeMetricFamily
            familles[attr] = cls(nom, aide, labels=LABELS)

        for m in mesures:
            for attr, _, _, _ in DEFINITIONS:
                valeur = getattr(m, attr)
                if valeur is None:
                    continue
                familles[attr].add_metric(_labels(m), float(valeur))

        yield from familles.values()

        yield GaugeMetricFamily(
            "mtr_exporter_scrape_success",
            "1 si la dernière lecture des équipements a réussi.",
            value=succes,
        )
        yield GaugeMetricFamily(
            "mtr_exporter_scrape_duration_seconds",
            "Durée de la lecture des équipements.",
            value=time.monotonic() - debut,
        )
        yield GaugeMetricFamily(
            "mtr_exporter_devices",
            "Nombre d'équipements remontés par la source.",
            value=len(mesures),
        )
