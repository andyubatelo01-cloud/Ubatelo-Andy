import base64
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from prometheus_client import generate_latest

from mtr_agent.exporter import MesureEquipement, construire_registre, creer_serveur
from mtr_agent.exporter.securite import (
    ConfigurationInvalide,
    Identifiants,
    LimiteurTentatives,
    hacher_mot_de_passe,
    verifier_hachage,
)
from mtr_agent.exporter.simulation import SimulateurMesures

MDP = "motdepasse-de-test-123"
METRIQUES_OBLIGATOIRES = [
    "mtr_http_up",
    "mtr_http_response_seconds",
    "mtr_http_throughput_bytes_per_second",
    "mtr_packet_loss_ratio",
    "mtr_latency_seconds",
    "mtr_jitter_seconds",
    "mtr_tcp_connect_failures_total",
    "mtr_cpu_usage_ratio",
    "mtr_memory_usage_ratio",
]


def _auth(user="prometheus", mdp=MDP):
    return "Basic " + base64.b64encode(f"{user}:{mdp}".encode()).decode()


def test_toutes_les_metriques_obligatoires_sont_exposees():
    texte = generate_latest(construire_registre(SimulateurMesures(graine=1))).decode()
    for nom in METRIQUES_OBLIGATOIRES:
        assert f'{nom}{{constructeur="' in texte, nom
    assert 'salle="Salle Agathe"' in texte
    assert 'equipement="MTR-Agathe"' in texte


def test_valeur_absente_non_exposee():
    m = MesureEquipement("S", "E", "Neat", "mtr", http_disponible=True)
    texte = generate_latest(construire_registre(lambda: [m])).decode()
    assert 'mtr_http_up{constructeur="Neat",equipement="E",salle="S",type="mtr"} 1.0' in texte
    assert "mtr_cpu_usage_ratio{" not in texte


def test_source_en_panne_ne_casse_pas_metrics():
    def panne():
        raise RuntimeError("boom")

    texte = generate_latest(construire_registre(panne)).decode()
    assert "mtr_exporter_scrape_success 0.0" in texte


def test_hachage():
    h = hacher_mot_de_passe(MDP, iterations=1000)
    assert verifier_hachage(MDP, h)
    assert not verifier_hachage("autre", h)
    assert MDP not in h


def test_refus_sans_mot_de_passe():
    with pytest.raises(ConfigurationInvalide):
        Identifiants.depuis_environnement({})
    with pytest.raises(ConfigurationInvalide):
        Identifiants.depuis_environnement({"MTR_EXPORTER_PASSWORD": "court"})


def test_limiteur_bloque_apres_echecs():
    lim = LimiteurTentatives(max_echecs=3)
    for _ in range(3):
        lim.echec("1.2.3.4")
    assert lim.est_bloque("1.2.3.4")
    assert not lim.est_bloque("5.6.7.8")


@pytest.fixture
def serveur():
    ids = Identifiants("prometheus", hacher_mot_de_passe(MDP, iterations=1000))
    srv = creer_serveur(SimulateurMesures(graine=2), ids, hote="127.0.0.1", port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def _get(url, auth=None):
    req = urllib.request.Request(url, headers={"Authorization": auth} if auth else {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_metrics_exige_mot_de_passe(serveur):
    assert _get(serveur + "/metrics")[0] == 401
    assert _get(serveur + "/metrics", _auth(mdp="faux"))[0] == 401
    code, corps = _get(serveur + "/metrics", _auth())
    assert code == 200
    assert "mtr_latency_seconds" in corps


def test_blocage_force_brute(serveur):
    for _ in range(5):
        _get(serveur + "/metrics", _auth(mdp="faux"))
    # même le bon mot de passe est refusé pendant le blocage
    assert _get(serveur + "/metrics", _auth())[0] == 429


def test_healthz_sans_donnees(serveur):
    code, corps = _get(serveur + "/healthz")
    assert code == 200 and corps == "ok\n"


def test_tableau_de_bord_utilise_les_metriques_exposees():
    dash = json.loads((Path(__file__).parents[1] / "grafana" / "tableau-de-bord-mtr.json").read_text())
    exprs = " ".join(t["expr"] for p in dash["panels"] for t in p.get("targets", []))
    for nom in METRIQUES_OBLIGATOIRES:
        assert nom in exprs, nom
