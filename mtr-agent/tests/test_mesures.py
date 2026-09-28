"""Les connecteurs et sondes alimentent l'exporteur via MesureEquipement."""

from __future__ import annotations

import pytest
from prometheus_client import generate_latest

from mtr_agent.connectors.neat import NeatConnector
from mtr_agent.exporter import construire_registre
from mtr_agent.mesures import source_connecteurs, vers_mesure
from mtr_agent.models import DeviceStatus, Health
from mtr_agent.probes.http import HttpProbeResult
from mtr_agent.probes.network import NetworkProbeResult


def test_vers_mesure_convertit_unites():
    dev = DeviceStatus("jabra", "j1", name="Cam-Mirabeau", room="Salle Mirabeau", cpu_percent=25, memory_percent=50)
    http = HttpProbeResult("https://j1/", True, 200, 0.5, 1000)
    reseau = NetworkProbeResult("j1:443", 4, [10.0, 30.0, 20.0])
    m = vers_mesure(dev, http, reseau)
    assert (m.salle, m.equipement, m.constructeur, m.type_equipement) == ("Salle Mirabeau", "Cam-Mirabeau", "Jabra",
                                                                           "camera")
    assert m.http_disponible and m.http_temps_reponse_s == 0.5 and m.http_debit_octets_s == 2000
    assert m.perte_paquets_ratio == 0.25 and m.echecs_tcp_total == 1
    assert m.latence_s == pytest.approx(0.020) and m.gigue_s == pytest.approx(0.015)
    assert m.cpu_ratio == 0.25 and m.memoire_ratio == 0.5
    assert m.en_ligne is False and m.sante == "inconnu"


def test_sante_et_etat_en_ligne():
    assert vers_mesure(DeviceStatus("cisco", "c", online=True, health=Health.DEGRADED)).sante == "avertissement"
    hors_ligne = vers_mesure(DeviceStatus("cisco", "c", online=False, health=Health.OFFLINE))
    assert hors_ligne.en_ligne is False and hors_ligne.sante == "critique"


def test_source_connecteurs_expose_les_metriques_et_cumule_les_echecs_tcp(http):
    http.add("GET", "https://api.pulse.neat.no/v1/orgs/org1/endpoints", {"endpoints": [
        {"id": "n1", "name": "MTR-Rodin", "roomName": "Salle Rodin", "connected": True, "cpuUsage": 40,
         "peripherals": [{"name": "Neat Pad", "connected": True}, {"name": "Camera", "connected": False}]},
    ]})
    conn = NeatConnector({"token": "k", "org_id": "org1"}, http)
    source = source_connecteurs([conn], sondes=lambda dev: (None, NetworkProbeResult("n1", 5, [5.0] * 3)))

    assert source()[0].echecs_tcp_total == 2
    texte = generate_latest(construire_registre(source)).decode()

    labels = 'constructeur="Neat",equipement="MTR-Rodin",salle="Salle Rodin",type="mtr"'
    assert f"mtr_cpu_usage_ratio{{{labels}}} 0.4" in texte
    assert f"mtr_tcp_connect_failures_total{{{labels}}} 4.0" in texte
    assert f"mtr_device_online{{{labels}}} 1.0" in texte
    assert 'mtr_device_health{' in texte and 'etat="ok"' in texte
    cam = 'constructeur="Neat",equipement="MTR-Rodin / Camera",salle="Salle Rodin",type="camera"'
    assert f"mtr_device_present{{{cam}}} 0.0" in texte
    assert 'equipement="MTR-Rodin / Neat Pad",salle="Salle Rodin",type="tablette"} 1.0' in texte
