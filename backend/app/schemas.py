"""Schémas d'entrée/sortie de l'API (Pydantic)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    phone: str = ""

    model_config = {"from_attributes": True}


class UserIn(BaseModel):
    email: str
    name: str
    password: str = Field(min_length=8)
    role: str = "SECRETAIRE"
    phone: str = ""


class MemberIn(BaseModel):
    first_name: str
    last_name: str
    phone: str = ""
    email: str = ""
    whatsapp: str = ""
    responsibility: str = ""
    joined_at: datetime | None = None
    birthday: str = ""
    preferred_channel: str = "SMS"
    consent_sms: bool = False
    consent_whatsapp: bool = False
    consent_email: bool = False
    group_ids: list[int] = []
    admin_notes: str = ""
    is_new: bool = True


class MemberPatch(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    whatsapp: str | None = None
    responsibility: str | None = None
    joined_at: datetime | None = None
    birthday: str | None = None
    preferred_channel: str | None = None
    consent_sms: bool | None = None
    consent_whatsapp: bool | None = None
    consent_email: bool | None = None
    group_ids: list[int] | None = None
    admin_notes: str | None = None
    is_active: bool | None = None
    is_new: bool | None = None


class MemberOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    responsibility: str
    is_active: bool
    is_new: bool
    unsubscribed: bool
    consent_sms: bool
    consent_whatsapp: bool
    consent_email: bool
    preferred_channel: str
    groups: list[str]


class MemberIdsIn(BaseModel):
    member_ids: list[int] = Field(min_length=1, max_length=500)


class NoteIn(BaseModel):
    content: str = Field(min_length=1)


class GroupIn(BaseModel):
    name: str
    description: str = ""
    dynamic_rule: dict | None = None


class EventIn(BaseModel):
    name: str
    description: str = ""
    starts_at: datetime
    ends_at: datetime | None = None
    location: str = ""
    speaker: str = ""
    audience_group_id: int | None = None
    capacity: int | None = None
    registration_required: bool = False
    responsible: str = ""
    responsible_media: str = ""
    responsible_welcome: str = ""
    responsible_intercession: str = ""
    deadlines: list[dict] | None = None
    is_recurring_sunday: bool = False


class EventPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = None
    speaker: str | None = None
    audience_group_id: int | None = None
    capacity: int | None = None
    registration_required: bool | None = None
    responsible: str | None = None
    responsible_media: str | None = None
    responsible_welcome: str | None = None
    responsible_intercession: str | None = None
    deadlines: list[dict] | None = None
    is_recurring_sunday: bool | None = None


class AttendanceIn(BaseModel):
    member_id: int
    registered: bool | None = None
    confirmed: bool | None = None
    present: bool | None = None


class PlanIn(BaseModel):
    channel: str = "SMS"
    style: str = "chaleureux"
    steps: list[str] | None = None


class CampaignIn(BaseModel):
    name: str
    message: str
    channel: str = "SMS"
    send_at: datetime | None = None
    group_ids: list[int] = []
    explicit_member_ids: list[int] = []
    excluded_member_ids: list[int] = []
    objective: str = ""
    style: str = "chaleureux"
    subject: str = ""
    event_id: int | None = None
    is_sensitive: bool = False


class CampaignPatch(BaseModel):
    name: str | None = None
    message: str | None = None
    channel: str | None = None
    send_at: datetime | None = None
    group_ids: list[int] | None = None
    explicit_member_ids: list[int] | None = None
    excluded_member_ids: list[int] | None = None
    objective: str | None = None
    style: str | None = None
    subject: str | None = None
    event_id: int | None = None
    is_sensitive: bool | None = None


class ApproveIn(BaseModel):
    content_hash: str | None = None


class ConfirmIn(BaseModel):
    phrase: str


class CancelIn(BaseModel):
    reason: str = ""


class DraftIn(BaseModel):
    kind: str = "invitation"
    style: str = "chaleureux"
    channel: str = "SMS"
    event_id: int | None = None
    audience: str = "les membres"
    instructions: str = ""


class CommandIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class AutomationIn(BaseModel):
    name: str
    kind: str = Field(pattern="^(WEEKLY|MONTHLY|DAILY|BEFORE_EVENT|AFTER_EVENT)$")
    weekday: int | None = Field(default=None, ge=0, le=6)
    day_of_month: int | None = Field(default=None, ge=1, le=28)
    hour: int = Field(default=8, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    offset_hours: int | None = None
    group_id: int | None = None
    channel: str = "SMS"
    style: str = "chaleureux"
    message_template: str = ""
    campaign_name_template: str = ""
    is_active: bool = True


class TaskIn(BaseModel):
    title: str
    details: str = ""
    priority: str = "A_TRAITER"
    due_at: datetime | None = None


class ConsentIn(BaseModel):
    sms: bool | None = None
    whatsapp: bool | None = None
    email: bool | None = None
