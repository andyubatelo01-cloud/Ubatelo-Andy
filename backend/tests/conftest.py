"""Fixtures : base SQLite en mémoire, canaux console, utilisateurs de chaque rôle."""
from __future__ import annotations

import os
from datetime import timedelta

os.environ.update({
    "DATABASE_URL": "sqlite://",
    "SCHEDULER_ENABLED": "false",
    "LLM_PROVIDER": "template",
    "SMS_PROVIDER": "console",
    "WHATSAPP_PROVIDER": "console",
    "EMAIL_PROVIDER": "console",
    "SECRET_KEY": "test-secret",
    "ADMIN_EMAIL": "pasteur@test.org",
    "ADMIN_PASSWORD": "motdepasse-test",
    "PASTOR_PHONE": "+33600000099",
    "DOUBLE_CONFIRMATION_THRESHOLD": "10",
    "BASE_URL": "http://test",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event as sa_event  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import db as dbmod  # noqa: E402
from app.channels import get_gateway, reset_registry  # noqa: E402
from app.db import Base  # noqa: E402
from app.models import Channel, Event, Group, Member, Role, User, utcnow  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.services.members import ensure_default_groups, get_group_by_name  # noqa: E402

# Une seule connexion partagée pour SQLite en mémoire
from sqlalchemy import create_engine  # noqa: E402

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool, future=True)


@sa_event.listens_for(engine, "connect")
def _fk(conn, _):
    conn.execute("PRAGMA foreign_keys=ON")


dbmod.engine = engine
dbmod.SessionLocal.configure(bind=engine)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    reset_registry()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    session = dbmod.SessionLocal()
    ensure_default_groups(session)
    session.commit()
    yield session
    session.close()


@pytest.fixture
def pastor(db) -> User:
    u = User(email="pasteur@test.org", name="Pasteur Test", password_hash=hash_password("motdepasse-test"), role=Role.PASTEUR.value, phone="+33600000099")
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def secretary(db) -> User:
    u = User(email="sarah@test.org", name="Sarah", password_hash=hash_password("motdepasse-test"), role=Role.SECRETAIRE.value)
    db.add(u)
    db.commit()
    return u


def make_member(db, i: int, group: Group | None = None, **kw) -> Member:
    data = dict(first_name=f"Prénom{i}", last_name=f"Nom{i}", phone=f"+3360000{i:04d}", email=f"m{i}@test.org", consent_sms=True, consent_whatsapp=True, consent_email=True, is_new=False, joined_at=utcnow() - timedelta(days=200))
    data.update(kw)
    m = Member(**data)
    if group is not None:
        m.groups.append(group)
    db.add(m)
    db.flush()
    return m


@pytest.fixture
def members(db) -> list[Member]:
    g = get_group_by_name(db, "Membres")
    out = [make_member(db, i, g) for i in range(1, 6)]
    db.commit()
    return out


@pytest.fixture
def sunday(db) -> Event:
    e = Event(name="Culte du dimanche", starts_at=(utcnow() + timedelta(days=5)).replace(hour=10, minute=0, second=0, microsecond=0), location="Salle principale", responsible="Pasteur", is_recurring_sunday=True, audience_group_id=get_group_by_name(db, "Membres").id)
    db.add(e)
    db.commit()
    return e


@pytest.fixture
def client(pastor, secretary):
    from app.main import app

    with TestClient(app) as c:
        yield c


def login(client, email="pasteur@test.org", password="motdepasse-test") -> dict:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


def console(channel: str = Channel.SMS.value):
    return get_gateway(channel)


def member_sends(channel: str = Channel.SMS.value):
    """Messages partis vers des membres (hors liens de validation adressés au pasteur)."""
    return [m for m in get_gateway(channel).sent if m.metadata.get("kind") != "validation"]
