"""Modèle de données commun entre les connecteurs et l'exporteur.

Chaque connecteur (Teams Rooms, Cisco, Neat, Jabra, ...) produit des
``MesureEquipement`` ; l'exporteur les transforme en métriques Prometheus.
L'exporteur ne dépend d'aucun connecteur : il consomme une ``SourceMesures``,
c'est-à-dire tout appelable qui renvoie une liste de mesures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

# Valeurs admises pour ``MesureEquipement.sante``
ETATS_SANTE = ("ok", "avertissement", "critique", "inconnu")


@dataclass(frozen=True)
class MesureEquipement:
    """Dernier relevé d'un équipement (MTR ou périphérique) d'une salle.

    Les champs de mesure valent ``None`` quand le connecteur ne sait pas
    les fournir : la série correspondante n'est alors pas exposée.
    """

    salle: str
    equipement: str
    constructeur: str
    type_equipement: str  # "mtr", "camera", "ecran", "micro", "barre_video", ...

    # État remonté par le connecteur
    en_ligne: Optional[bool] = None  # l'équipement répond à sa plateforme / API
    sante: Optional[str] = None  # une valeur de ETATS_SANTE
    present: Optional[bool] = None  # périphérique détecté par la MTR / le système de salle

    # Métriques obligatoires du cahier de test des salles
    http_disponible: Optional[bool] = None
    http_temps_reponse_s: Optional[float] = None
    http_debit_octets_s: Optional[float] = None
    perte_paquets_ratio: Optional[float] = None  # 0.0 à 1.0
    latence_s: Optional[float] = None
    gigue_s: Optional[float] = None
    echecs_tcp_total: Optional[int] = None  # compteur cumulatif
    cpu_ratio: Optional[float] = None  # 0.0 à 1.0
    memoire_ratio: Optional[float] = None  # 0.0 à 1.0


SourceMesures = Callable[[], Iterable[MesureEquipement]]
