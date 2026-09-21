"""Tests de l'API HTTP : rôles, cycle complet de validation, validation mobile, RGPD, webhooks."""
from __future__ import annotations

from datetime import timedelta

from app.models import CampaignStatus, utcnow
from app.services import campaign_engine as engine
from app.services.members import get_group_by_name

from .conftest import console, login, member_sends


def _iso(dt):
    return dt.replace(microsecond=0).isoformat()


def _create_members(client, h, n=3, consent=True):
    ids = []
    for i in range(1, n + 1):
        r = client.post("/api/membres", json={"first_name": f"P{i}", "last_name": f"N{i}", "phone": f"06 00 00 00 {i:02d}", "consent_sms": consent, "consent_whatsapp": True, "group_ids": [1]}, headers=h)
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


def test_login_and_roles(client):
    assert client.post("/api/auth/login", json={"email": "pasteur@test.org", "password": "faux"}).status_code == 401
    h = login(client)
    assert client.get("/api/auth/me", headers=h).json()["role"] == "PASTEUR"
    assert client.get("/api/dashboard").status_code == 401
    hs = login(client, "sarah@test.org")
    assert client.get("/api/auth/users", headers=hs).status_code == 403


def test_full_validation_cycle_via_api(client, monkeypatch):
    h, hs = login(client), login(client, "sarah@test.org")
    _create_members(client, h)
    r = client.post("/api/campagnes", json={"name": "Invitation", "message": "Bonjour {PRENOM}, bienvenue dimanche.", "channel": "SMS", "send_at": _iso(utcnow() + timedelta(minutes=30)), "group_ids": [1]}, headers=hs)
    assert r.status_code == 201, r.text
    p = r.json()
    ref = p["ref"]
    assert p["statut"] == "READY_FOR_REVIEW" and p["nombre_destinataires"] == 3
    assert client.get("/api/campagnes/a-valider", headers=hs).json()[0]["ref"] == ref
    # La secrétaire ne peut pas valider
    assert client.post(f"/api/campagnes/{ref}/valider", headers=hs).status_code == 403
    assert console().sent == []
    # Le pasteur valide → envoi immédiat (send_at dans 30 min < 1 min ? non : programmée)
    r = client.post(f"/api/campagnes/{ref}/valider", json={"content_hash": p.get("content_hash")}, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["preview"]["statut"] == "SCHEDULED"
    assert console().sent == []
    # Le planificateur envoie à l'heure : pas avant
    r = client.post("/api/planificateur/executer", headers=h)
    assert r.json()["sent"] == []
    # ... puis quand l'heure est venue (on avance l'horloge du planificateur)
    from app.services import scheduling

    real = scheduling.utcnow
    monkeypatch.setattr(scheduling, "utcnow", lambda: real() + timedelta(hours=1))
    r = client.post("/api/planificateur/executer", headers=h)
    assert r.json()["sent"] == [ref]
    assert len(member_sends()) == 3
    rep = client.get(f"/api/campagnes/{ref}/rapport", headers=h).json()
    assert rep["statut"] == "SENT" and rep["envois"]["envoyes"] == 3 and rep["valide_par"] == "Pasteur Test"
    audit = client.get("/api/audit", params={"entity_ref": ref}, headers=h).json()
    actions = [a["action"] for a in audit]
    assert "CAMPAIGN_CREATED" in actions and "CAMPAIGN_STATUS" in actions


def test_modify_cancel_and_blocked(client):
    h = login(client)
    _create_members(client, h)
    ref = client.post("/api/campagnes", json={"name": "X", "message": "Bonjour {PRENOM} {INCONNU}", "send_at": _iso(utcnow() + timedelta(hours=1)), "group_ids": [1]}, headers=h).json()["ref"]
    p = client.get(f"/api/campagnes/{ref}", headers=h).json()
    assert p["statut"] == "BLOCKED" and p["bloquee"]
    assert client.post(f"/api/campagnes/{ref}/valider", headers=h).status_code == 409
    p = client.patch(f"/api/campagnes/{ref}", json={"message": "Bonjour {PRENOM}"}, headers=h).json()
    assert p["statut"] == "READY_FOR_REVIEW"
    p = client.post(f"/api/campagnes/{ref}/annuler", json={"reason": "test"}, headers=h).json()
    assert p["statut"] == "CANCELLED"
    assert client.post(f"/api/campagnes/{ref}/valider", headers=h).status_code == 409


def test_double_validation_via_api(client):
    h = login(client)
    _create_members(client, h, n=11)  # seuil = 10
    ref = client.post("/api/campagnes", json={"name": "Grande", "message": "Bonjour {PRENOM}", "send_at": _iso(utcnow()), "group_ids": [1]}, headers=h).json()["ref"]
    r = client.post(f"/api/campagnes/{ref}/valider", headers=h).json()
    assert r["double_validation"] is True and "CONFIRMER L'ENVOI" in r["message"]
    assert client.post(f"/api/campagnes/{ref}/confirmer", json={"phrase": "OUI"}, headers=h).status_code == 409
    assert console().sent == []
    r = client.post(f"/api/campagnes/{ref}/confirmer", json={"phrase": "CONFIRMER L'ENVOI"}, headers=h)
    assert r.status_code == 200 and r.json()["preview"]["statut"] == "SENT"
    assert len(member_sends()) == 11


def test_mobile_validation_link(client):
    h = login(client)
    _create_members(client, h)
    ref = client.post("/api/campagnes", json={"name": "Mobile", "message": "Bonjour {PRENOM}", "send_at": _iso(utcnow()), "group_ids": [1]}, headers=h).json()["ref"]
    r = client.post(f"/api/campagnes/{ref}/envoyer-lien-validation", headers=h).json()
    link = r["link"]
    assert link.startswith("http://test/valider/")
    # Le pasteur a reçu le SMS de validation sur son téléphone (canal console)
    assert any("BUREAU DU PASTEUR" in m.body and m.to == "+33600000099" for m in console().sent)
    token = link.rsplit("/", 1)[1]
    sent_before = len(console().sent)
    assert client.get(f"/valider/{token}").status_code == 200
    assert client.get(f"/api/valider/{token}").json()["ref"] == ref
    # Mauvais mot de passe / mauvais rôle
    assert client.post(f"/api/valider/{token}", json={"action": "VALIDER", "email": "pasteur@test.org", "password": "faux"}).status_code == 401
    assert client.post(f"/api/valider/{token}", json={"action": "VALIDER", "email": "sarah@test.org", "password": "motdepasse-test"}).status_code == 401
    r = client.post(f"/api/valider/{token}", json={"action": "VALIDER", "email": "pasteur@test.org", "password": "motdepasse-test"})
    assert r.status_code == 200 and r.json()["preview"]["statut"] == "SENT"
    assert len(member_sends()) == 3
    # Jeton à usage unique
    assert client.get(f"/api/valider/{token}").status_code == 410


def test_mobile_link_invalid_after_modification(client):
    h = login(client)
    _create_members(client, h)
    ref = client.post("/api/campagnes", json={"name": "Mobile", "message": "Bonjour {PRENOM}", "send_at": _iso(utcnow() + timedelta(hours=1)), "group_ids": [1]}, headers=h).json()["ref"]
    token = client.post(f"/api/campagnes/{ref}/envoyer-lien-validation", headers=h).json()["link"].rsplit("/", 1)[1]
    client.patch(f"/api/campagnes/{ref}", json={"message": "Bonjour {PRENOM}, modifié"}, headers=h)
    assert client.get(f"/api/valider/{token}").status_code == 410


def test_rgpd_export_unsubscribe_delete(client):
    h = login(client)
    mid = _create_members(client, h, n=1)[0]
    exp = client.get(f"/api/membres/{mid}/export", headers=h)
    assert exp.status_code == 200 and exp.json()["membre"]["prenom"] == "P1"
    # STOP par webhook retire le consentement SMS
    r = client.post("/webhooks/twilio/inbound", data={"From": "+33600000001", "Body": "STOP"})
    assert r.status_code == 200 and "plus de messages" in r.text
    card = client.get(f"/api/membres/{mid}", headers=h).json()
    assert card["consentement"]["sms"] is False and card["consentement"]["whatsapp"] is True
    # START réabonne
    client.post("/webhooks/twilio/inbound", data={"From": "+33600000001", "Body": "START"})
    assert client.get(f"/api/membres/{mid}", headers=h).json()["consentement"]["sms"] is True
    # Effacement : réservé au pasteur, anonymisation
    hs = login(client, "sarah@test.org")
    assert client.delete(f"/api/membres/{mid}", headers=hs).status_code == 403
    assert client.delete(f"/api/membres/{mid}", headers=h).status_code == 204
    assert client.get(f"/api/membres/{mid}", headers=h).status_code == 404
    assert client.get("/api/membres", headers=h).json() == []


def test_agent_command_and_dashboard(client):
    h = login(client)
    _create_members(client, h)
    r = client.post("/api/agents/commande", json={"text": "Quelles campagnes attendent ma validation ?"}, headers=h)
    assert r.status_code == 200 and "Aucune" in r.json()["summary"]
    d = client.get("/api/dashboard", headers=h).json()
    assert d["membres"]["total"] == 3 and "communication" in d and "taches" in d
    assert client.get("/api/briefing", headers=h).json()["titre"].startswith("🌅")
    assert client.get("/api/agents", headers=h).json()["fournisseur_ia"] == "template"
    assert len(client.get("/api/agents", headers=h).json()["agents"]) == 8


def test_events_plan_and_attendance(client):
    h = login(client)
    ids = _create_members(client, h)
    ev = client.post("/api/evenements", json={"name": "Veillée de prière", "starts_at": _iso(utcnow() + timedelta(days=20)), "location": "Salle", "responsible": "Paul", "audience_group_id": 1, "registration_required": True, "capacity": 100}, headers=h).json()
    assert len(ev["communications"]) == 6
    r = client.post(f"/api/evenements/{ev['id']}/planifier", json={"channel": "WHATSAPP", "style": "motivant"}, headers=h).json()
    assert len(r["campaign_refs"]) == 6
    st = client.post(f"/api/evenements/{ev['id']}/presences", json={"member_id": ids[0], "registered": True, "confirmed": True}, headers=h).json()
    assert st["inscrits"] == 1 and st["confirmes"] == 1
    assert "COMPTE RENDU" in client.get(f"/api/evenements/{ev['id']}/compte-rendu", headers=h).json()["template"]


def test_dynamic_group(client):
    h = login(client)
    _create_members(client, h, n=2)
    client.post("/api/membres", json={"first_name": "Sans", "last_name": "Consent", "phone": "0600000099", "consent_sms": False, "group_ids": [1]}, headers=h)
    g = client.post("/api/groupes", json={"name": "SMS OK", "dynamic_rule": {"consent": "SMS"}}, headers=h).json()
    assert g["effectif"] == 2
    assert client.get("/api/membres", params={"group_id": g["id"]}, headers=h).json().__len__() == 2


def test_automation_endpoints(client):
    h = login(client)
    a = client.post("/api/automatisations", json={"name": "Rappel culte", "kind": "WEEKLY", "weekday": 6, "hour": 8, "minute": 30, "campaign_name_template": "Rappel du culte"}, headers=h).json()
    assert a["validation_requise"] is True and "dimanche" in a["description"]
    assert client.patch(f"/api/automatisations/{a['id']}", params={"is_active": False}, headers=h).json()["active"] is False
    assert client.get("/api/parametres", headers=h).json()["validation"]["phrase_confirmation"] == "CONFIRMER L'ENVOI"
