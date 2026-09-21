from __future__ import annotations

from datetime import timedelta

import pytest

from app.models import CampaignStatus, Channel, utcnow
from app.services import campaign_engine as engine
from app.services import personalization
from app.services.members import get_group_by_name

from .conftest import make_member


def _campaign(db, **kw):
    g = get_group_by_name(db, "Membres")
    params = dict(name="Test", message="Bonjour {PRENOM}", channel=Channel.SMS.value, send_at=utcnow() + timedelta(hours=3), group_ids=[g.id])
    params.update(kw)
    return engine.create_campaign(db, **params)


def test_reference_format_and_sequence(db, members):
    a, b = _campaign(db), _campaign(db)
    year = utcnow().year
    assert a.ref == f"CAM-{year}-001" and b.ref == f"CAM-{year}-002"


def test_state_machine_cancellation_paths(db, members, pastor):
    c = _campaign(db)
    engine.cancel(db, c, "SARAH")
    assert c.status == CampaignStatus.CANCELLED.value
    with pytest.raises(engine.CampaignError):
        engine.cancel(db, c, "SARAH")
    c2 = _campaign(db, send_at=utcnow() + timedelta(days=2))
    engine.submit_for_review(db, c2, "SARAH")
    engine.approve(db, c2, pastor)
    assert c2.status == CampaignStatus.SCHEDULED.value
    engine.cancel(db, c2, pastor.name)
    assert c2.status == CampaignStatus.CANCELLED.value


def test_sent_campaign_is_immutable(db, members, pastor):
    c = _campaign(db, send_at=utcnow())
    engine.submit_for_review(db, c, "SARAH")
    engine.approve(db, c, pastor)
    engine.dispatch(db, c)
    with pytest.raises(engine.CampaignError):
        engine.update_campaign(db, c, "SARAH", message="x")
    with pytest.raises(engine.CampaignError):
        engine.cancel(db, c, "SARAH")


def test_preflight_blocks_empty_message(db, members):
    c = _campaign(db, message="")
    report = engine.submit_for_review(db, c, "SARAH")
    assert report.blocked and c.status == CampaignStatus.BLOCKED.value
    assert any(ch.code == "message" and not ch.ok for ch in report.checks)


def test_preflight_blocks_unknown_variable(db, members):
    c = _campaign(db, message="Bonjour {PRENOM}, {TRUC}")
    report = engine.submit_for_review(db, c, "SARAH")
    assert report.blocked
    assert any(ch.code == "variables_known" and "{TRUC}" in ch.detail for ch in report.checks)


def test_preflight_blocks_event_variables_without_event(db, members):
    c = _campaign(db, message="Rendez-vous à {HEURE} à {LIEU}")
    report = engine.submit_for_review(db, c, "SARAH")
    assert report.blocked
    assert any(ch.code == "variables_event" and not ch.ok for ch in report.checks)


def test_preflight_blocks_past_date(db, members):
    c = _campaign(db, send_at=utcnow() - timedelta(hours=1))
    report = engine.submit_for_review(db, c, "SARAH")
    assert report.blocked and any(ch.code == "date" and not ch.ok for ch in report.checks)


def test_preflight_blocks_missing_group(db, members):
    c = _campaign(db, group_ids=[9999])
    report = engine.submit_for_review(db, c, "SARAH")
    assert report.blocked and any(ch.code == "group" and not ch.ok for ch in report.checks)


def test_preflight_excludes_no_consent_duplicates_invalid_and_unsubscribed(db):
    g = get_group_by_name(db, "Membres")
    make_member(db, 1, g)
    make_member(db, 2, g, consent_sms=False)  # sans consentement
    make_member(db, 3, g, phone="+33600000001")  # doublon du membre 1
    make_member(db, 4, g, phone="0600")  # numéro invalide
    make_member(db, 5, g, unsubscribed=True)  # désinscrit
    make_member(db, 6, g, first_name="")  # variable {PRENOM} non résolvable
    db.commit()
    c = _campaign(db)
    report = engine.submit_for_review(db, c, "SARAH")
    assert not report.blocked
    assert len(report.recipients) == 1
    reasons = {e["reason"].split(" ")[0] for e in report.excluded}
    assert {"Pas", "Doublon", "Coordonnée", "Variable"} <= reasons
    assert c.recipient_count == 1
    assert c.estimated_cost_eur == pytest.approx(0.07)


def test_preflight_blocks_when_no_valid_recipient(db):
    g = get_group_by_name(db, "Membres")
    make_member(db, 1, g, consent_sms=False)
    db.commit()
    c = _campaign(db)
    report = engine.submit_for_review(db, c, "SARAH")
    assert report.blocked and any(ch.code == "recipients" and not ch.ok for ch in report.checks)


def test_email_requires_subject(db, members):
    c = _campaign(db, channel=Channel.EMAIL.value, subject="")
    assert engine.submit_for_review(db, c, "SARAH").blocked
    c2 = _campaign(db, channel=Channel.EMAIL.value, subject="Invitation")
    assert not engine.submit_for_review(db, c2, "SARAH").blocked


def test_preview_contains_required_fields(db, members, sunday):
    c = _campaign(db, event_id=sunday.id, message="Bonjour {PRENOM}, culte {DATE} à {HEURE}, {LIEU}.", objective="Inviter")
    engine.submit_for_review(db, c, "SARAH")
    p = engine.preview(db, c)
    for key in ("ref", "nom", "objectif", "date_envoi_texte", "canal", "nombre_destinataires", "groupes", "message", "variables", "exclus", "cout_estime_eur", "anomalies", "actions"):
        assert key in p
    assert p["nombre_destinataires"] == 5
    assert "{PRENOM}" in p["variables"] and "{HEURE}" in p["variables"]
    assert "Salle principale" in p["apercu_rendu"] and "{" not in p["apercu_rendu"]
    assert p["actions"]["valider"].startswith("🟢")


def test_personalization_render_and_helpers():
    ctx = {"PRENOM": "Jean", "NOM": "Dupont", "HEURE": "10h"}
    assert personalization.render("Bonjour {PRENOM} {NOM}, à {HEURE}", ctx) == "Bonjour Jean Dupont, à 10h"
    assert personalization.unknown_variables("{PRENOM} {FOO}") == ["FOO"]
    assert personalization.missing_variables("{PRENOM} {LIEU}", ctx) == ["LIEU"]
    from datetime import datetime

    assert personalization.format_date_fr(datetime(2026, 9, 27)) == "dimanche 27 septembre"
    assert personalization.format_time_fr(datetime(2026, 9, 27, 9, 30)) == "9h30"


def test_sms_segments():
    from app.services.preflight import sms_segments

    assert sms_segments("a" * 160) == 1
    assert sms_segments("a" * 161) == 2
    assert sms_segments("é" * 70) == 1
    assert sms_segments("é" * 71) == 2
