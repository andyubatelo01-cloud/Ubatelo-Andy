"""Modèle de données du Bureau du Pasteur.

Principe de minimisation : les fiches membres ne contiennent que les informations
nécessaires à la communication et au suivi administratif. Aucun champ ne stocke
d'état spirituel, émotionnel ou médical.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ─────────────────────────────── Énumérations ───────────────────────────────


class Role(str, enum.Enum):
    PASTEUR = "PASTEUR"  # seul rôle autorisé à valider un envoi collectif
    SECRETAIRE = "SECRETAIRE"  # prépare, modifie, consulte
    LECTEUR = "LECTEUR"  # lecture seule


class Channel(str, enum.Enum):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    NOTIFICATION = "NOTIFICATION"


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    BLOCKED = "BLOCKED"  # anomalie détectée par les contrôles pré-envoi
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"  # date d'envoi dépassée sans validation : jamais envoyée


class MessageStyle(str, enum.Enum):
    CHALEUREUX = "chaleureux"
    PASTORAL = "pastoral"
    MOTIVANT = "motivant"
    EVANGELISATION = "evangelisation"
    EVENEMENTIEL = "evenementiel"
    ADMINISTRATIF = "administratif"
    RAPPEL_URGENT = "rappel_urgent"


class Priority(str, enum.Enum):
    URGENT = "URGENT"  # 🔴
    A_TRAITER = "A_TRAITER"  # 🟠
    A_VALIDER = "A_VALIDER"  # 🟡
    INFORMATION = "INFORMATION"  # 🟢


class TaskStatus(str, enum.Enum):
    OPEN = "OPEN"
    DONE = "DONE"


# ─────────────────────────────── Utilisateurs ───────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=Role.SECRETAIRE.value)
    phone: Mapped[str] = mapped_column(String(32), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ─────────────────────────────── Membres & groupes ───────────────────────────────

member_groups = Table(
    "member_groups",
    Base.metadata,
    Column("member_id", ForeignKey("members.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    # Groupe dynamique : règle JSON évaluée à la volée (ex : actifs 90 jours + consentement SMS)
    dynamic_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    members: Mapped[list[Member]] = relationship(secondary=member_groups, back_populates="groups")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str] = mapped_column(String(32), default="", index=True)
    email: Mapped[str] = mapped_column(String(255), default="", index=True)
    whatsapp: Mapped[str] = mapped_column(String(32), default="")  # vide = même numéro que phone
    responsibility: Mapped[str] = mapped_column(String(120), default="")
    joined_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    birthday: Mapped[str] = mapped_column(String(5), default="")  # "JJ-MM" uniquement (minimisation)
    preferred_channel: Mapped[str] = mapped_column(String(20), default=Channel.SMS.value)
    consent_sms: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_email: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_recorded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    unsubscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_new: Mapped[bool] = mapped_column(Boolean, default=True)  # nouveau membre à intégrer
    last_contact_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    admin_notes: Mapped[str] = mapped_column(Text, default="")  # notes administratives autorisées
    anonymized: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    groups: Mapped[list[Group]] = relationship(secondary=member_groups, back_populates="members")
    attendances: Mapped[list[Attendance]] = relationship(back_populates="member", cascade="all, delete-orphan")
    notes: Mapped[list[MemberNote]] = relationship(back_populates="member", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def contact_for(self, channel: str) -> str:
        if channel == Channel.SMS.value:
            return self.phone
        if channel == Channel.WHATSAPP.value:
            return self.whatsapp or self.phone
        if channel == Channel.EMAIL.value:
            return self.email
        return ""

    def has_consent(self, channel: str) -> bool:
        if self.unsubscribed:
            return False
        return {
            Channel.SMS.value: self.consent_sms,
            Channel.WHATSAPP.value: self.consent_whatsapp,
            Channel.EMAIL.value: self.consent_email,
        }.get(channel, False)


class MemberNote(Base):
    __tablename__ = "member_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    member: Mapped[Member] = relationship(back_populates="notes")


# ─────────────────────────────── Événements ───────────────────────────────


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    location: Mapped[str] = mapped_column(String(200), default="")
    speaker: Mapped[str] = mapped_column(String(160), default="")
    audience_group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_required: Mapped[bool] = mapped_column(Boolean, default=False)
    responsible: Mapped[str] = mapped_column(String(160), default="")
    responsible_media: Mapped[str] = mapped_column(String(160), default="")
    responsible_welcome: Mapped[str] = mapped_column(String(160), default="")
    responsible_intercession: Mapped[str] = mapped_column(String(160), default="")
    deadlines: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{label, due_at}]
    is_recurring_sunday: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    audience_group: Mapped[Group | None] = relationship()
    attendances: Mapped[list[Attendance]] = relationship(back_populates="event", cascade="all, delete-orphan")
    campaigns: Mapped[list[Campaign]] = relationship(back_populates="event")


class Attendance(Base):
    """Inscription et présence à un événement (données factuelles uniquement)."""

    __tablename__ = "attendances"
    __table_args__ = (UniqueConstraint("member_id", "event_id", name="uq_attendance"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    registered: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    present: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # None = non renseigné
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    member: Mapped[Member] = relationship(back_populates="attendances")
    event: Mapped[Event] = relationship(back_populates="attendances")


# ─────────────────────────────── Campagnes ───────────────────────────────


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    ref: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # CAM-2026-001
    name: Mapped[str] = mapped_column(String(200))
    objective: Mapped[str] = mapped_column(Text, default="")
    channel: Mapped[str] = mapped_column(String(20), default=Channel.SMS.value)
    style: Mapped[str] = mapped_column(String(30), default=MessageStyle.CHALEUREUX.value)
    message: Mapped[str] = mapped_column(Text, default="")
    subject: Mapped[str] = mapped_column(String(200), default="")  # e-mail uniquement
    status: Mapped[str] = mapped_column(String(30), default=CampaignStatus.DRAFT.value, index=True)
    send_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    group_ids: Mapped[list] = mapped_column(JSON, default=list)
    excluded_member_ids: Mapped[list] = mapped_column(JSON, default=list)
    explicit_member_ids: Mapped[list] = mapped_column(JSON, default=list)  # ciblage individuel
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    automation_id: Mapped[int | None] = mapped_column(ForeignKey("automations.id"), nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_double_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    pending_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    preflight_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recipient_count: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_eur: Mapped[float] = mapped_column(Float, default=0.0)
    content_hash: Mapped[str] = mapped_column(String(64), default="")  # empreinte validée
    approved_hash: Mapped[str] = mapped_column(String(64), default="")
    created_by: Mapped[str] = mapped_column(String(120), default="")
    modified_by: Mapped[str] = mapped_column(String(120), default="")
    approved_by: Mapped[str] = mapped_column(String(120), default="")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    event: Mapped[Event | None] = relationship(back_populates="campaigns")
    deliveries: Mapped[list[Delivery]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class Delivery(Base):
    """Un message individuel envoyé dans le cadre d'une campagne."""

    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"))
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[str] = mapped_column(String(20))
    recipient: Mapped[str] = mapped_column(String(255))
    rendered_message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING|SENT|FAILED|DELIVERED
    provider_id: Mapped[str] = mapped_column(String(120), default="")
    error: Mapped[str] = mapped_column(Text, default="")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="deliveries")


# ─────────────────────────────── Automatisations ───────────────────────────────


class Automation(Base):
    """Une automatisation PRÉPARE une campagne. Elle n'envoie jamais sans validation."""

    __tablename__ = "automations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    kind: Mapped[str] = mapped_column(String(30))  # WEEKLY | MONTHLY | BEFORE_EVENT | AFTER_EVENT | DAILY
    # WEEKLY: weekday (0=lundi) + hour/minute ; MONTHLY: day_of_month ; BEFORE_EVENT: offset_hours
    weekday: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_of_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hour: Mapped[int] = mapped_column(Integer, default=8)
    minute: Mapped[int] = mapped_column(Integer, default=0)
    offset_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String(20), default=Channel.SMS.value)
    style: Mapped[str] = mapped_column(String(30), default=MessageStyle.CHALEUREUX.value)
    message_template: Mapped[str] = mapped_column(Text, default="")
    campaign_name_template: Mapped[str] = mapped_column(String(200), default="")
    requires_validation: Mapped[bool] = mapped_column(Boolean, default=True)  # toujours vrai pour un envoi collectif
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_run_key: Mapped[str] = mapped_column(String(80), default="")  # évite les doublons
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ─────────────────────────────── Tâches, notifications, audit ───────────────────────────────


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    details: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(String(20), default=Priority.A_TRAITER.value)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.OPEN.value)
    assigned_to: Mapped[str] = mapped_column(String(120), default="Pasteur")
    created_by: Mapped[str] = mapped_column(String(120), default="SARAH")
    related_campaign_ref: Mapped[str] = mapped_column(String(20), default="")
    related_member_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    done_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(String(20), default=Priority.INFORMATION.value)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(String(300), default="")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuditLog(Base):
    """Journal d'audit : qui a fait quoi, quand, sur quoi."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(120))  # utilisateur, agent IA ou "SYSTEME"
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(40), default="")
    entity_ref: Mapped[str] = mapped_column(String(80), default="")
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ApprovalToken(Base):
    """Jeton à usage unique pour la validation depuis le téléphone du pasteur."""

    __tablename__ = "approval_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    campaign_ref: Mapped[str] = mapped_column(String(20), index=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AgentRun(Base):
    """Trace de chaque intervention d'un agent IA (transparence)."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent: Mapped[str] = mapped_column(String(40))
    command: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(60), default="")
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    provider: Mapped[str] = mapped_column(String(30), default="template")
    actor: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
