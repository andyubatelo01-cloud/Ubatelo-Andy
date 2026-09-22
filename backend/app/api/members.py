from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import audit
from ..agents import BergerAgent, MembresAgent
from ..db import get_db
from ..models import Group, Member, User, utcnow
from ..schemas import ConsentIn, GroupIn, MemberIn, MemberOut, MemberPatch, NoteIn
from ..services import member_import
from ..services import members as svc
from .deps import anyone, pastor_only, staff

router = APIRouter(prefix="/api", tags=["membres"])


def _out(m: Member) -> MemberOut:
    return MemberOut(id=m.id, first_name=m.first_name, last_name=m.last_name, phone=m.phone, email=m.email, responsibility=m.responsibility, is_active=m.is_active, is_new=m.is_new, unsubscribed=m.unsubscribed, consent_sms=m.consent_sms, consent_whatsapp=m.consent_whatsapp, consent_email=m.consent_email, preferred_channel=m.preferred_channel, groups=[g.name for g in m.groups])


@router.get("/membres", response_model=list[MemberOut])
def list_members(q: str = "", group_id: int | None = None, only_active: bool = True, db: Session = Depends(get_db), _: User = Depends(anyone)):
    stmt = select(Member).where(Member.anonymized.is_(False))
    if only_active:
        stmt = stmt.where(Member.is_active.is_(True))
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Member.first_name.ilike(like), Member.last_name.ilike(like), Member.phone.ilike(like), Member.email.ilike(like)))
    members = db.scalars(stmt.order_by(Member.last_name, Member.first_name)).all()
    if group_id:
        g = db.get(Group, group_id)
        ids = {m.id for m in svc.group_members(db, g)} if g else set()
        members = [m for m in members if m.id in ids]
    return [_out(m) for m in members]


@router.post("/membres", response_model=MemberOut, status_code=201)
def create_member(body: MemberIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    data = body.model_dump(exclude={"group_ids"})
    data["phone"] = svc.normalize_phone(data["phone"])
    data["whatsapp"] = svc.normalize_phone(data["whatsapp"])
    data["email"] = data["email"].strip().lower()
    if data["phone"] and not svc.is_valid_phone(data["phone"]):
        raise HTTPException(400, "Numéro invalide : utilisez le format international (+33612345678).")
    if data["email"] and not svc.is_valid_email(data["email"]):
        raise HTTPException(400, "Adresse e-mail invalide.")
    m = Member(**data)
    if any((body.consent_sms, body.consent_whatsapp, body.consent_email)):
        m.consent_recorded_at = utcnow()
    for gid in body.group_ids:
        g = db.get(Group, gid)
        if g and not g.dynamic_rule:
            m.groups.append(g)
    db.add(m)
    db.flush()
    audit.log(db, actor.name, "MEMBER_CREATED", "member", str(m.id))
    db.commit()
    return _out(m)


@router.post("/membres/import")
async def import_members(
    file: UploadFile = File(...),
    dry_run: bool = Form(default=True),
    group_id: int | None = Form(default=None),
    format: str | None = Form(default=None),
    skip: str = Form(default=""),
    db: Session = Depends(get_db),
    actor: User = Depends(staff),
):
    """Import en masse depuis le répertoire du téléphone (vCard .vcf), un tableur (CSV)
    ou une discussion de groupe WhatsApp exportée (.txt).

    Deux temps : ``dry_run=true`` renvoie l'aperçu (contacts importables / ignorés et pourquoi),
    ``dry_run=false`` crée les membres (``skip`` : index des lignes à écarter, séparés par des virgules).
    Un contact déjà membre n'est pas recréé : il est ajouté au groupe choisi.
    Aucun consentement n'est enregistré à l'import."""
    data = await file.read()
    if not data:
        raise HTTPException(400, "Fichier vide.")
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "Fichier trop volumineux (5 Mo maximum).")
    if format and format not in (member_import.FORMAT_VCARD, member_import.FORMAT_CSV, member_import.FORMAT_WHATSAPP):
        raise HTTPException(400, "Format inconnu : vcard, csv ou whatsapp.")
    result = member_import.prepare(db, file.filename or "", data, format or None)
    if not result.contacts:
        raise HTTPException(400, "Aucun contact reconnu dans ce fichier. Formats acceptés : vCard (.vcf), CSV, export de discussion WhatsApp (.txt).")
    group = db.get(Group, group_id) if group_id else None
    if group_id and group is None:
        raise HTTPException(404, "Groupe introuvable.")
    if group is not None and group.dynamic_rule:
        raise HTTPException(400, "Un groupe dynamique se calcule automatiquement : choisissez un groupe classique.")
    if dry_run:
        return result.as_dict()
    try:
        skipped = {int(x) for x in skip.split(",") if x.strip()}
    except ValueError:
        raise HTTPException(400, "Paramètre skip invalide.")
    member_import.commit_import(db, result, actor.name, group, skip=skipped)
    db.commit()
    return result.as_dict()


@router.get("/membres/{member_id}")
def member_card(member_id: int, db: Session = Depends(get_db), _: User = Depends(anyone)):
    m = db.get(Member, member_id)
    if m is None or m.anonymized:
        raise HTTPException(404, "Membre introuvable.")
    return MembresAgent(db).card(m)


@router.patch("/membres/{member_id}", response_model=MemberOut)
def update_member(member_id: int, body: MemberPatch, db: Session = Depends(get_db), actor: User = Depends(staff)):
    m = db.get(Member, member_id)
    if m is None or m.anonymized:
        raise HTTPException(404, "Membre introuvable.")
    changes = body.model_dump(exclude_unset=True)
    consent = {k: changes.pop(k) for k in ("consent_sms", "consent_whatsapp", "consent_email") if k in changes}
    group_ids = changes.pop("group_ids", None)
    if "phone" in changes and changes["phone"] is not None:
        changes["phone"] = svc.normalize_phone(changes["phone"])
        if changes["phone"] and not svc.is_valid_phone(changes["phone"]):
            raise HTTPException(400, "Numéro invalide : utilisez le format international.")
    for k, v in changes.items():
        if v is not None:
            setattr(m, k, v)
    if consent:
        svc.record_consent(db, m, sms=consent.get("consent_sms"), whatsapp=consent.get("consent_whatsapp"), email=consent.get("consent_email"), actor=actor.name)
    if group_ids is not None:
        m.groups = [g for g in (db.get(Group, gid) for gid in group_ids) if g and not g.dynamic_rule]
    audit.log(db, actor.name, "MEMBER_UPDATED", "member", str(m.id), {"fields": sorted(changes)})
    db.commit()
    return _out(m)


@router.post("/membres/{member_id}/notes", status_code=201)
def add_note(member_id: int, body: NoteIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    m = db.get(Member, member_id)
    if m is None:
        raise HTTPException(404)
    note = svc.add_note(db, m, body.content, actor.id, actor.name)
    db.commit()
    return {"id": note.id, "created_at": note.created_at.isoformat()}


@router.post("/membres/{member_id}/consentement", response_model=MemberOut)
def consent(member_id: int, body: ConsentIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    m = db.get(Member, member_id)
    if m is None:
        raise HTTPException(404)
    svc.record_consent(db, m, body.sms, body.whatsapp, body.email, actor.name)
    db.commit()
    return _out(m)


@router.post("/membres/{member_id}/desinscription", response_model=MemberOut)
def unsubscribe(member_id: int, channel: str = "ALL", db: Session = Depends(get_db), actor: User = Depends(staff)):
    m = db.get(Member, member_id)
    if m is None:
        raise HTTPException(404)
    svc.unsubscribe(db, m, channel, source=f"demande traitée par {actor.name}")
    db.commit()
    return _out(m)


@router.get("/membres/{member_id}/export")
def export_member(member_id: int, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """RGPD — droit d'accès et portabilité."""
    m = db.get(Member, member_id)
    if m is None:
        raise HTTPException(404)
    audit.log(db, actor.name, "MEMBER_EXPORTED", "member", str(m.id))
    db.commit()
    return JSONResponse(svc.export_member_data(db, m), headers={"Content-Disposition": f'attachment; filename="membre-{m.id}.json"'})


@router.delete("/membres/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    """RGPD — droit à l'effacement (anonymisation irréversible, statistiques agrégées conservées)."""
    m = db.get(Member, member_id)
    if m is None:
        raise HTTPException(404)
    svc.anonymize_member(db, m, actor.name)
    db.commit()


@router.post("/membres/{member_id}/message")
def prepare_message(member_id: int, kind: str = "encouragement", style: str = "pastoral", channel: str | None = None, db: Session = Depends(get_db), actor: User = Depends(staff)):
    """Action « Envoyer message » de la fiche : prépare une campagne individuelle à valider."""
    m = db.get(Member, member_id)
    if m is None:
        raise HTTPException(404)
    res = BergerAgent(db, actor.name).prepare_individual_message(m, kind, style, channel)
    db.commit()
    return res.as_dict()


# ── Groupes ───────────────────────────────────────────────────────────────────


@router.get("/groupes")
def list_groups(db: Session = Depends(get_db), _: User = Depends(anyone)):
    agent = MembresAgent(db)
    return [agent.group_summary(g) | {"membres": None} for g in db.scalars(select(Group).order_by(Group.is_system.desc(), Group.name)).all()]


@router.get("/groupes/{group_id}")
def group_detail(group_id: int, db: Session = Depends(get_db), _: User = Depends(anyone)):
    g = db.get(Group, group_id)
    if g is None:
        raise HTTPException(404)
    return MembresAgent(db).group_summary(g)


@router.post("/groupes", status_code=201)
def create_group(body: GroupIn, db: Session = Depends(get_db), actor: User = Depends(staff)):
    if svc.get_group_by_name(db, body.name):
        raise HTTPException(409, "Ce groupe existe déjà.")
    g = svc.create_group(db, body.name, body.description, body.dynamic_rule, actor.name)
    db.commit()
    return MembresAgent(db).group_summary(g)


@router.post("/groupes/{group_id}/membres/{member_id}", status_code=204)
def add_to_group(group_id: int, member_id: int, db: Session = Depends(get_db), actor: User = Depends(staff)):
    g, m = db.get(Group, group_id), db.get(Member, member_id)
    if g is None or m is None:
        raise HTTPException(404)
    if g.dynamic_rule:
        raise HTTPException(400, "Un groupe dynamique se calcule automatiquement.")
    if m not in g.members:
        g.members.append(m)
        audit.log(db, actor.name, "MEMBER_ADDED_TO_GROUP", "member", str(m.id), {"group": g.slug})
    db.commit()


@router.delete("/groupes/{group_id}/membres/{member_id}", status_code=204)
def remove_from_group(group_id: int, member_id: int, db: Session = Depends(get_db), actor: User = Depends(staff)):
    g, m = db.get(Group, group_id), db.get(Member, member_id)
    if g is None or m is None:
        raise HTTPException(404)
    if m in g.members:
        g.members.remove(m)
        audit.log(db, actor.name, "MEMBER_REMOVED_FROM_GROUP", "member", str(m.id), {"group": g.slug})
    db.commit()


@router.delete("/groupes/{group_id}", status_code=204)
def delete_group(group_id: int, db: Session = Depends(get_db), actor: User = Depends(pastor_only)):
    g = db.get(Group, group_id)
    if g is None:
        raise HTTPException(404)
    if g.is_system:
        raise HTTPException(400, "Les groupes système ne peuvent pas être supprimés.")
    db.delete(g)
    audit.log(db, actor.name, "GROUP_DELETED", "group", g.slug)
    db.commit()


# ── Suivi ─────────────────────────────────────────────────────────────────────


@router.get("/suivi")
def followup(absence_days: int = Query(default=30, ge=7, le=365), db: Session = Depends(get_db), actor: User = Depends(anyone)):
    berger = BergerAgent(db, actor.name)
    res = berger.people_to_contact(absence_days)
    db.commit()
    return res.as_dict() | {"nouveaux": [{"id": m.id, "nom": m.full_name, "arrive_le": m.joined_at.isoformat() if m.joined_at else None} for m in berger.new_members_to_integrate()]}


@router.post("/suivi/relance")
def followup_batch(absence_days: int = 30, style: str = "pastoral", channel: str = "SMS", db: Session = Depends(get_db), actor: User = Depends(staff)):
    res = BergerAgent(db, actor.name).prepare_followup_batch(absence_days, style, channel)
    db.commit()
    return res.as_dict()
