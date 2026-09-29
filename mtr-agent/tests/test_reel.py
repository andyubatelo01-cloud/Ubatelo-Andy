import pytest

from mtr_agent.exporter.__main__ import main
from mtr_agent.reel import cibles_sondes, connecteurs_configures, source_reelle


def test_seuls_les_connecteurs_configures_sont_actifs():
    env = {"MTR_SONY_HOSTS": "10.0.0.5", "MTR_SONY_PSK": "cle", "MTR_NEAT_TOKEN": "t"}  # Neat incomplet
    assert [c.vendor for c in connecteurs_configures(env)] == ["sony"]


def test_cibles_sondes():
    assert cibles_sondes({"MTR_SONDES": "Ecran=10.0.0.5, Bar = 10.0.0.6,invalide"}) == {
        "Ecran": "10.0.0.5", "Bar": "10.0.0.6"}


def test_source_reelle_refuse_sans_connecteur():
    with pytest.raises(ValueError):
        source_reelle({})


def test_exporteur_reel_refuse_sans_connecteur(monkeypatch):
    for k in list(__import__("os").environ):
        if k.startswith("MTR_"):
            monkeypatch.delenv(k)
    monkeypatch.setenv("MTR_EXPORTER_PASSWORD", "motdepasse-de-test-123")
    assert main([]) == 2
