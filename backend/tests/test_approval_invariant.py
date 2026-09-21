"""INVARIANT FONDAMENTAL : aucun message collectif ne part sans validation explicite du pasteur."""
from __future__ import annotations

from datetime import timedelta

import pytest

from app.models import CampaignStatus, Channel, Role, User, utcnow
from app.security import hash_password
from app.services import campaign_engine as engine
from app.services import scheduling
from app.services.members import get_group_by_name

from .conftest import console, member_sends


def _campaign(db, members, **kw):
    g = get_group_by_name(db, "Membres")
    params = dict(name="Invitation test", message="Bonjour {PRENOM}, rendez-vous dimanche.", channel=Channel.SMS.value, send_at=utcnow() + timedelta(hours=2), group_ids=[g.id])
    params.update(kw)
    return engine.create_campaign(db, **params)


def test_dispatch_refuses_draft(db, members):
    c = _campaign(db, members)
    with pytest.raises(engine.ApprovalRequired):
        engine.dispatch(db, c)
    assert console().sent == []


def test_dispatch_refuses_ready_for_review(db, members):
    c = _campaign(db, members)
    engine.submit_for_review(db, c, "SARAH")
    assert c.status == CampaignStatus.READY_FOR_REVIEW.value
    with pytest.raises(engine.ApprovalRequired):
        engine.dispatch(db, c)
    assert console().sent == []


def test_secretary_cannot_approve(db, members, secretary):
    c = _campaign(db, members)
    engine.submit_for_review(db, c, "SARAH")
    with pytest.raises(engine.ApprovalRequired):
        engine.approve(db, c, secretary)
    assert c.status == CampaignStatus.READY_FOR_REVIEW.value


def test_reader_cannot_approve(db, members):
    reader = User(email="l@test.org", name="Lecteur", password_hash=hash_password("x" * 8), role=Role.LECTEUR.value)
    db.add(reader)
    db.flush()
    c = _campaign(db, members)
    engine.submit_for_review(db, c, "SARAH")
    with pytest.raises(engine.ApprovalRequired):
        engine.approve(db, c, reader)


def test_pastor_approval_then_dispatch(db, members, pastor):
    c = _campaign(db, members, send_at=utcnow())
    engine.submit_for_review(db, c, "SARAH")
    engine.approve(db, c, pastor)
    assert c.status == CampaignStatus.APPROVED.value
    assert c.approved_by == pastor.name and c.approved_at is not None
    result = engine.dispatch(db, c, pastor.name)
    assert c.status == CampaignStatus.SENT.value
    assert result["sent"] == 5 and result["failed"] == 0
    assert len(console().sent) == 5
    assert all("Bonjour Prénom" in m.body for m in console().sent)


def test_silence_is_never_approval(db, members):
    """Une campagne non validée dont la date passe expire : elle n'est jamais envoyée."""
    c = _campaign(db, members, send_at=utcnow() - timedelta(hours=3))
    c.status = CampaignStatus.READY_FOR_REVIEW.value
    scheduling.tick(db)
    db.refresh(c)
    assert c.status == CampaignStatus.EXPIRED.value
    assert console().sent == []


def test_scheduler_sends_only_validated(db, members, pastor):
    validated = _campaign(db, members, name="Validée", send_at=utcnow() - timedelta(minutes=1))
    engine.submit_for_review(db, validated, "SARAH")
    engine.approve(db, validated, pastor)
    not_validated = _campaign(db, members, name="Non validée", send_at=utcnow() - timedelta(minutes=1))
    engine.submit_for_review(db, not_validated, "SARAH")
    out = scheduling.tick(db)
    assert out["sent"] == [validated.ref]
    assert validated.status == CampaignStatus.SENT.value
    assert not_validated.status == CampaignStatus.READY_FOR_REVIEW.value
    assert len(member_sends()) == 5
    # Le pasteur, lui, a bien reçu le lien de validation pour la campagne en attente
    assert any(m.metadata.get("kind") == "validation" and m.to == "+33600000099" for m in console().sent)


def test_modification_after_approval_revokes_it(db, members, pastor):
    c = _campaign(db, members, send_at=utcnow() + timedelta(days=1))
    engine.submit_for_review(db, c, "SARAH")
    engine.approve(db, c, pastor)
    assert c.status == CampaignStatus.SCHEDULED.value
    engine.update_campaign(db, c, "SARAH", message="Message modifié après validation {PRENOM}")
    assert c.status == CampaignStatus.DRAFT.value
    assert c.approved_by == "" and c.approved_at is None
    with pytest.raises(engine.ApprovalRequired):
        engine.dispatch(db, c)


def test_tampering_with_approved_content_blocks_send(db, members, pastor):
    """Défense en profondeur : même une modification directe en base est détectée par l'empreinte."""
    c = _campaign(db, members, send_at=utcnow())
    engine.submit_for_review(db, c, "SARAH")
    engine.approve(db, c, pastor)
    c.message = "Contenu altéré"  # contourne update_campaign
    with pytest.raises(engine.ApprovalRequired):
        engine.dispatch(db, c)
    assert console().sent == []


def test_double_validation_required_above_threshold(db, pastor):
    g = get_group_by_name(db, "Membres")
    from .conftest import make_member

    for i in range(1, 13):  # seuil de test : 10
        make_member(db, i, g)
    db.commit()
    c = _campaign(db, None, send_at=utcnow())
    engine.submit_for_review(db, c, "SARAH")
    assert c.requires_double_confirmation is True
    engine.approve(db, c, pastor)
    assert c.status == CampaignStatus.READY_FOR_REVIEW.value and c.pending_confirmation is True
    with pytest.raises(engine.ApprovalRequired):
        engine.dispatch(db, c)
    with pytest.raises(engine.CampaignError):
        engine.confirm(db, c, pastor, "oui")
    engine.confirm(db, c, pastor, "confirmer l'envoi")  # insensible à la casse, exact sinon
    assert c.status == CampaignStatus.APPROVED.value and c.confirmed_at is not None
    engine.dispatch(db, c, pastor.name)
    assert c.status == CampaignStatus.SENT.value and len(console().sent) == 12


def test_sensitive_campaign_always_requires_double_validation(db, members, pastor):
    c = _campaign(db, members, is_sensitive=True, send_at=utcnow())
    engine.submit_for_review(db, c, "SARAH")
    engine.approve(db, c, pastor)
    assert c.pending_confirmation is True


def test_automation_only_prepares(db, members, sunday):
    from app.models import Automation

    g = get_group_by_name(db, "Membres")
    now = utcnow()
    db.add(Automation(name="Rappel du culte", kind="WEEKLY", weekday=now.weekday(), hour=0, group_id=g.id, campaign_name_template="Rappel du culte", message_template="Bonjour {PRENOM}, culte à {HEURE}."))
    db.commit()
    out = scheduling.tick(db, now)
    assert len(out["prepared"]) == 1
    c = engine.get_by_ref(db, out["prepared"][0])
    assert c.status == CampaignStatus.READY_FOR_REVIEW.value
    assert out["sent"] == [] and member_sends() == []
    # Deuxième passage : pas de doublon
    out2 = scheduling.tick(db, now + timedelta(minutes=5))
    assert out2["prepared"] == []
