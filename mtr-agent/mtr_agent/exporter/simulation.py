"""Source de mesures simulées, pour tester l'exporteur et Grafana sans matériel."""

from __future__ import annotations

import random
import threading
from dataclasses import replace

from .model import MesureEquipement

# (salle, équipement, constructeur, type)
PARC_SIMULE = [
    ("Salle Agathe", "MTR-Agathe", "Lenovo", "mtr"),
    ("Salle Agathe", "Cam-Agathe", "Jabra", "camera"),
    ("Salle Agathe", "Ecran-Agathe", "Sony", "ecran"),
    ("Salle Agathe", "Affichage-Agathe", "Zebrix", "affichage"),
    ("Salle Monet", "MTR-Monet", "Cisco", "mtr"),
    ("Salle Monet", "Barre-Monet", "Poly/HP", "barre_video"),
    ("Salle Monet", "Reservation-Monet", "Ochno", "tablette"),
    ("Salle Rodin", "MTR-Rodin", "Neat", "mtr"),
    ("Salle Rodin", "Micro-Rodin", "Sylphony", "micro"),
]


class SimulateurMesures:
    """Génère des valeurs plausibles qui évoluent à chaque lecture.

    Environ 3 % des lectures simulent un équipement injoignable, pour que
    les alertes et le tableau de bord aient quelque chose à montrer.
    """

    def __init__(self, graine: int | None = None) -> None:
        self._rng = random.Random(graine)
        self._verrou = threading.Lock()
        self._etat = {
            eq: MesureEquipement(
                salle=salle, equipement=eq, constructeur=cons, type_equipement=typ,
                echecs_tcp_total=0,
            )
            for salle, eq, cons, typ in PARC_SIMULE
        }

    def __call__(self) -> list[MesureEquipement]:
        with self._verrou:
            for cle, m in self._etat.items():
                self._etat[cle] = self._suivant(m)
            return list(self._etat.values())

    def _suivant(self, m: MesureEquipement) -> MesureEquipement:
        r = self._rng
        joignable = r.random() > 0.03
        echecs = (m.echecs_tcp_total or 0) + (0 if joignable else r.randint(1, 3))
        if not joignable:
            return replace(
                m, http_disponible=False, http_temps_reponse_s=None,
                http_debit_octets_s=0.0, perte_paquets_ratio=1.0,
                latence_s=None, gigue_s=None, echecs_tcp_total=echecs,
                cpu_ratio=None, memoire_ratio=None,
            )
        est_mtr = m.type_equipement == "mtr"
        return replace(
            m,
            http_disponible=True,
            http_temps_reponse_s=round(r.uniform(0.04, 0.35), 4),
            http_debit_octets_s=round(r.uniform(2e5, 4e6) if est_mtr else r.uniform(2e4, 5e5)),
            perte_paquets_ratio=round(max(0.0, r.gauss(0.003, 0.004)), 4),
            latence_s=round(r.uniform(0.004, 0.060), 4),
            gigue_s=round(r.uniform(0.0005, 0.012), 4),
            echecs_tcp_total=echecs,
            cpu_ratio=round(r.uniform(0.15, 0.85) if est_mtr else r.uniform(0.05, 0.45), 3),
            memoire_ratio=round(r.uniform(0.35, 0.80), 3),
        )
