"""Import de membres en masse depuis un fichier : répertoire iPhone (vCard), tableur (CSV)
ou discussion de groupe WhatsApp exportée (.txt).

Règles :
- aucun consentement n'est déduit d'un import : les membres arrivent sans consentement,
  celui-ci se coche ensuite sur la fiche (RGPD — consentement explicite) ;
- les doublons (même téléphone ou même e-mail, dans le fichier ou déjà en base) sont ignorés ;
- l'import se fait en deux temps : aperçu (dry_run) puis confirmation.
"""
from __future__ import annotations

import csv
import io
import quopri
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..models import Group, Member, utcnow
from .members import is_valid_email, is_valid_phone, normalize_phone, record_consent

FORMAT_VCARD = "vcard"
FORMAT_CSV = "csv"
FORMAT_WHATSAPP = "whatsapp"

# Colonnes reconnues dans un CSV (insensible à la casse et aux accents approximatifs)
CSV_ALIASES = {
    "first_name": {"prenom", "prénom", "first name", "firstname", "first_name", "given name", "given_name"},
    "last_name": {"nom", "nom de famille", "last name", "lastname", "last_name", "family name", "family_name", "surname"},
    "phone": {"telephone", "téléphone", "tel", "tél", "phone", "mobile", "portable", "numero", "numéro", "phone 1 - value", "gsm", "tel portable", "tel. portable", "telephone portable", "numero de telephone", "phone number", "mobile phone", "whatsapp"},
    "email": {"email", "e-mail", "mail", "courriel", "e-mail 1 - value", "adresse e-mail", "adresse email", "email address"},
    "responsibility": {"responsabilite", "responsabilité", "role", "rôle", "fonction"},
    "full_name": {"name", "nom complet", "full name", "fullname", "contact"},
    "joined_at": {"horodateur", "timestamp", "date", "date d'arrivee", "arrivee", "inscription"},
}
# Colonne de consentement (formulaire d'inscription) : reconnue par mots-clés dans l'en-tête
CONSENT_HEADER_KEYWORDS = ("consent", "acceptez-vous que vos donnees", "acceptez vous que vos donnees", "rgpd", "donnees personnelles")
YES_VALUES = {"oui", "yes", "true", "1", "x", "ok", "accepte", "j'accepte"}


@dataclass
class ImportedContact:
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    email: str = ""
    responsibility: str = ""
    source: str = ""  # information d'origine utile à l'aperçu (ex. numéro brut ou ligne CSV)
    problem: str = ""  # vide = importable
    existing_id: int | None = None  # membre déjà en base : il sera ajouté au groupe choisi, pas recréé
    consent: bool = False  # consentement explicite indiqué dans le fichier (colonne dédiée d'un formulaire)
    joined_at: datetime | None = None

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def as_dict(self) -> dict:
        return {
            "prenom": self.first_name,
            "nom": self.last_name,
            "telephone": self.phone,
            "email": self.email,
            "responsabilite": self.responsibility,
            "source": self.source,
            "probleme": self.problem,
            "importable": not self.problem,
            "existant": self.existing_id is not None,
            "action": "ignorer" if self.problem else ("ajouter_au_groupe" if self.existing_id else "creer"),
            "consentement": self.consent,
            "arrivee": self.joined_at.date().isoformat() if self.joined_at else None,
        }


@dataclass
class ImportResult:
    format: str
    contacts: list[ImportedContact] = field(default_factory=list)
    created_ids: list[int] = field(default_factory=list)
    added_to_group_ids: list[int] = field(default_factory=list)
    completed_ids: list[int] = field(default_factory=list)  # fiches existantes complétées (nom, e-mail, consentement)

    @property
    def importable(self) -> list[ImportedContact]:
        return [c for c in self.contacts if not c.problem]

    @property
    def to_create(self) -> list[ImportedContact]:
        return [c for c in self.importable if c.existing_id is None]

    @property
    def existing(self) -> list[ImportedContact]:
        return [c for c in self.importable if c.existing_id is not None]

    def as_dict(self) -> dict:
        return {
            "format": self.format,
            "total": len(self.contacts),
            "importables": len(self.importable),
            "nouveaux": len(self.to_create),
            "existants": len(self.existing),
            "ignores": len(self.contacts) - len(self.importable),
            "crees": len(self.created_ids),
            "ajoutes_au_groupe": len(self.added_to_group_ids),
            "completes": len(self.completed_ids),
            "avec_consentement": sum(1 for c in self.importable if c.consent),
            "contacts": [c.as_dict() for c in self.contacts],
        }


# ── Détection du format ───────────────────────────────────────────────────────


def detect_format(filename: str, text: str) -> str:
    name = (filename or "").lower()
    head = text[:4000]
    if name.endswith(".vcf") or "BEGIN:VCARD" in head.upper():
        return FORMAT_VCARD
    if name.endswith(".csv") or name.endswith(".tsv"):
        return FORMAT_CSV
    if WHATSAPP_LINE_RE.search(head) or "whatsapp" in name:
        return FORMAT_WHATSAPP
    if "," in head or ";" in head or "\t" in head:
        return FORMAT_CSV
    return FORMAT_WHATSAPP


def decode_upload(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


# ── Nom prénom / nom ──────────────────────────────────────────────────────────


def split_name(full: str) -> tuple[str, str]:
    """« Marie Dupont » → (Marie, Dupont) ; « DUPONT Marie » → (Marie, DUPONT) ; « Marie » → (Marie, '')."""
    parts = [p for p in re.split(r"\s+", (full or "").strip()) if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    # Convention « NOM Prénom » quand le premier mot est entièrement en majuscules et pas le second
    if parts[0].isupper() and len(parts[0]) > 1 and not parts[1].isupper():
        return " ".join(parts[1:]), parts[0]
    return parts[0], " ".join(parts[1:])


# ── vCard (Contacts iPhone / Mac / Google) ────────────────────────────────────


def _unfold_vcard(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw.startswith((" ", "\t")) and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _vcard_value(params: str, value: str) -> str:
    if "QUOTED-PRINTABLE" in params.upper():
        try:
            value = quopri.decodestring(value.encode()).decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - valeur mal encodée
            pass
    return value.replace("\\,", ",").replace("\\;", ";").replace("\\n", " ").strip()


def parse_vcard(text: str) -> list[ImportedContact]:
    contacts: list[ImportedContact] = []
    current: dict | None = None
    for line in _unfold_vcard(text):
        upper = line.upper()
        if upper.startswith("BEGIN:VCARD"):
            current = {"phones": [], "emails": [], "n": None, "fn": "", "title": "", "org": ""}
            continue
        if upper.startswith("END:VCARD"):
            if current is not None:
                contacts.append(_vcard_to_contact(current))
            current = None
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parts = key.split(";")
        prop = parts[0].upper()
        if "." in prop:  # groupes « item1.TEL »
            prop = prop.split(".", 1)[1]
        params = ";".join(parts[1:])
        value = _vcard_value(params, value)
        if prop == "N":
            current["n"] = value.split(";")
        elif prop == "FN":
            current["fn"] = value
        elif prop == "TEL":
            current["phones"].append((params.upper(), value))
        elif prop == "EMAIL":
            current["emails"].append(value)
        elif prop == "TITLE":
            current["title"] = value
        elif prop == "ORG":
            current["org"] = value.split(";")[0]
    return contacts


def _vcard_to_contact(card: dict) -> ImportedContact:
    first = last = ""
    if card["n"]:
        n = card["n"] + [""] * 5
        last, first = n[0].strip(), n[1].strip()
    if not first and not last:
        first, last = split_name(card["fn"])
    # Numéro : on privilégie le mobile (SMS / WhatsApp)
    phones = card["phones"]
    chosen = next((v for p, v in phones if "CELL" in p or "MOBILE" in p or "IPHONE" in p), phones[0][1] if phones else "")
    email = card["emails"][0] if card["emails"] else ""
    return ImportedContact(first_name=first, last_name=last, phone=chosen, email=email, responsibility=card["title"], source=card["fn"] or chosen)


# ── CSV / TSV (Excel, Numbers, Google Contacts) ───────────────────────────────


def _norm_header(h: str) -> str:
    text = unicodedata.normalize("NFKD", (h or "")).encode("ascii", "ignore").decode().lower()
    text = text.replace("_", " ").replace("-", " ").replace(".", " ")
    return re.sub(r"\s+", " ", text).strip()


def _find_consent_column(headers: list[str]) -> int | None:
    for idx, h in enumerate(headers):
        nh = _norm_header(h)
        if any(k in nh for k in CONSENT_HEADER_KEYWORDS):
            return idx
    return None


def _parse_date(value: str) -> datetime | None:
    value = (value or "").strip()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _map_headers(headers: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, h in enumerate(headers):
        nh = _norm_header(h)
        for field_name, aliases in CSV_ALIASES.items():
            if field_name in mapping:
                continue
            if nh in {_norm_header(a) for a in aliases} or (field_name == "phone" and nh.startswith(("tel ", "telephone ", "numero de tel"))):
                mapping[field_name] = idx
                break
    return mapping


def parse_csv(text: str) -> list[ImportedContact]:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = [r for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]
    if not rows:
        return []
    mapping = _map_headers(rows[0])
    has_header = bool(mapping)
    consent_col = _find_consent_column(rows[0]) if has_header else None
    if not has_header:
        # Sans en-tête : Prénom ; Nom ; Téléphone ; E-mail
        mapping = {"first_name": 0, "last_name": 1, "phone": 2, "email": 3}
    body = rows[1:] if has_header else rows

    def cell(row: list[str], key: str) -> str:
        i = mapping.get(key)
        return row[i].strip() if i is not None and i < len(row) else ""

    contacts = []
    for row in body:
        first, last = cell(row, "first_name"), cell(row, "last_name")
        if not first and not last and "full_name" in mapping:
            first, last = split_name(cell(row, "full_name"))
        if not first and not last and not cell(row, "phone") and not cell(row, "email"):
            continue  # ligne de séparation (ex. « 2026 »)
        consent = consent_col is not None and consent_col < len(row) and row[consent_col].strip().lower() in YES_VALUES
        contacts.append(ImportedContact(first_name=first, last_name=last, phone=cell(row, "phone"), email=cell(row, "email"), responsibility=cell(row, "responsibility"), consent=consent, joined_at=_parse_date(cell(row, "joined_at")), source="formulaire" if consent_col is not None else " ; ".join(c for c in row if c.strip())[:80]))
    return contacts


# ── Export d'une discussion WhatsApp (.txt) ───────────────────────────────────

# Début de ligne d'un export WhatsApp (Android : « 12/03/2026 18:04 - … », iPhone : « [12/03/2026, 18:04:12] … »)
WHATSAPP_STAMP_RE = re.compile(r"^\[?\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?::\d{2})?\]?\s*(?:-\s*)?")
# « Auteur: message »
WHATSAPP_LINE_RE = re.compile(WHATSAPP_STAMP_RE.pattern + r"(?P<author>[^:\n]{1,80}?):\s", re.M)
# Numéros mentionnés en clair (auteurs non enregistrés, « X a ajouté +33 6 12 34 56 78 »)
PHONE_IN_TEXT_RE = re.compile(r"(?:\+|00)\d[\d\s().-]{7,20}\d")
SYSTEM_KEYWORDS = ("a ajouté", "added", "a rejoint", "joined", "a créé le groupe", "created group", "a retiré", "removed", "a quitté", "left")
INVISIBLE = "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u200b\u00a0 "
ADDED_NAMES_RE = re.compile(r"a ajouté (?P<names>.+)$")
NOT_A_PERSON = ("autres personnes", "vous", "you")


def _clean_author(author: str) -> str:
    author = "".join(ch for ch in author if ch not in INVISIBLE.strip(" ")).strip()
    return author.lstrip("~").strip()  # « ~ Pseudo » : participant non enregistré dans le téléphone


def parse_whatsapp(text: str) -> list[ImportedContact]:
    """Extrait les participants d'une discussion exportée : auteurs des messages (nom du contact tel
    qu'enregistré dans le téléphone qui a exporté, ou numéro brut), numéros cités et personnes ajoutées."""
    seen: dict[str, ImportedContact] = {}
    group_name = ""

    def add_phone(raw: str, source: str) -> None:
        seen.setdefault(normalize_phone(raw), ImportedContact(phone=raw.strip(INVISIBLE), source=source))

    def add_name(name: str, source: str) -> None:
        name = _clean_author(name)
        if not name or name == group_name or PHONE_IN_TEXT_RE.fullmatch(name) or any(k in name.lower() for k in NOT_A_PERSON):
            if PHONE_IN_TEXT_RE.fullmatch(name):
                add_phone(name, source)
            return
        first, last = split_name(name)
        seen.setdefault(name.lower(), ImportedContact(first_name=first, last_name=last, source=source))

    for line in text.splitlines():
        line = line.strip(INVISIBLE)
        stamp = WHATSAPP_STAMP_RE.match(line)
        if not stamp:
            continue
        body = line[stamp.end():].strip(INVISIBLE)
        m = WHATSAPP_LINE_RE.match(line)
        if m:
            author = _clean_author(m.group("author"))
            body = line[m.end():].strip(INVISIBLE)
            if "chiffrés de bout en bout" in body or "end-to-end encrypted" in body:
                group_name = author  # sur iPhone, les messages système portent le nom du groupe
                continue
            add_name(author, "participant WhatsApp")
        low = body.lower()
        if any(k in low for k in SYSTEM_KEYWORDS):
            for ph in PHONE_IN_TEXT_RE.findall(body):
                add_phone(ph, "numéro cité dans le groupe WhatsApp")
            added = ADDED_NAMES_RE.search(body)
            if added:
                for part in re.split(r",| et ", added.group("names")):
                    add_name(part, "ajouté au groupe WhatsApp")
    return [c for c in seen.values() if c.phone or c.display_name != group_name]


# ── Validation, dédoublonnage, création ───────────────────────────────────────


def parse_contacts(fmt: str, text: str) -> list[ImportedContact]:
    if fmt == FORMAT_VCARD:
        return parse_vcard(text)
    if fmt == FORMAT_CSV:
        return parse_csv(text)
    return parse_whatsapp(text)


def _name_key(first: str, last: str) -> str:
    text = unicodedata.normalize("NFKD", f"{first} {last}").encode("ascii", "ignore").decode().lower()
    return " ".join(sorted(w for w in re.split(r"[^a-z0-9]+", text) if w))


def prepare(db: Session, filename: str, data: bytes, fmt: str | None = None) -> ImportResult:
    """Analyse le fichier et signale, pour chaque contact, s'il est importable et s'il existe déjà."""
    text = decode_upload(data)
    fmt = fmt or detect_format(filename, text)
    result = ImportResult(format=fmt, contacts=parse_contacts(fmt, text))

    members = db.scalars(select(Member).where(Member.anonymized.is_(False))).all()
    by_phone = {m.phone: m.id for m in members if m.phone}
    by_email = {m.email: (m.id, m.phone) for m in members if m.email}
    by_name: dict[str, int | None] = {}
    for m in members:
        key = _name_key(m.first_name, m.last_name)
        by_name[key] = None if key in by_name else m.id  # homonymes : ambigu, on ne rapproche pas
    seen_phones: set[str] = set()
    seen_emails: set[str] = set()
    seen_existing: set[int] = set()

    for c in result.contacts:
        c.first_name, c.last_name = c.first_name.strip()[:80], c.last_name.strip()[:80]
        c.phone = normalize_phone(c.phone)
        c.email = c.email.strip().lower()
        c.responsibility = c.responsibility.strip()[:120]
        if c.phone and not is_valid_phone(c.phone):
            c.problem = f"numéro non reconnu ({c.phone}) : format international attendu (+33…)"
            continue
        if c.email and not is_valid_email(c.email):
            c.problem = f"e-mail invalide ({c.email})"
            continue
        existing = by_phone.get(c.phone) if c.phone else None
        if existing is None and c.email and c.email in by_email:
            member_id, member_phone = by_email[c.email]
            # Une adresse partagée (couple, famille) n'est pas un doublon si les deux ont un numéro différent
            if not c.phone or not member_phone:
                existing = member_id
        if existing is None and not c.phone and not c.email and (c.first_name or c.last_name):
            existing = by_name.get(_name_key(c.first_name, c.last_name))
        if existing is not None:
            if existing in seen_existing:
                c.problem = "en double dans le fichier"
                continue
            seen_existing.add(existing)
            c.existing_id = existing
            continue
        if not c.phone and not c.email:
            c.problem = "ni téléphone ni e-mail (et aucun membre de ce nom)"
            continue
        if not c.first_name and not c.last_name:
            # Numéro seul (WhatsApp non enregistré) : on garde un nom provisoire à corriger sur la fiche
            c.first_name, c.last_name = "Contact", c.phone or c.email
        if c.phone and c.phone in seen_phones:
            c.problem = "en double dans le fichier (téléphone)"
            continue
        if c.email and c.email in seen_emails and not c.phone:
            c.problem = "en double dans le fichier (e-mail)"
            continue
        if c.phone:
            seen_phones.add(c.phone)
        if c.email:
            seen_emails.add(c.email)
    return result


def commit_import(db: Session, result: ImportResult, actor: str, group: Group | None = None, mark_new: bool = True, skip: set[int] | None = None, apply_consent: bool = False) -> ImportResult:
    """Crée les membres importables (sauf les index exclus) et ajoute les membres déjà connus au groupe choisi.
    Aucun consentement n'est déduit : seul ``apply_consent`` enregistre, pour les contacts dont le fichier porte
    une réponse « Oui » dans une colonne de consentement, le consentement sur les canaux joignables."""
    skip = skip or set()
    all_members = db.scalar(select(Group).where(Group.slug == "membres"))
    for idx, c in enumerate(result.contacts):
        if c.problem or idx in skip:
            continue
        if c.existing_id is not None:
            m = db.get(Member, c.existing_id)
            if m is None:
                continue
            if group is not None and not group.dynamic_rule and m not in group.members:
                group.members.append(m)
                result.added_to_group_ids.append(m.id)
            # Compléter une fiche existante avec ce que le fichier apporte de plus
            completed = False
            if m.first_name == "Contact" and c.first_name and c.first_name != "Contact":
                m.first_name, m.last_name = c.first_name, c.last_name
                completed = True
            if not m.email and c.email:
                m.email = c.email
                completed = True
            if not m.phone and c.phone:
                m.phone = c.phone
                completed = True
            if apply_consent and c.consent and not (m.consent_sms or m.consent_whatsapp or m.consent_email):
                record_consent(db, m, sms=bool(m.phone), whatsapp=bool(m.phone), email=bool(m.email), actor=actor)
                if c.joined_at:
                    m.consent_recorded_at = c.joined_at
                completed = True
            if completed:
                result.completed_ids.append(m.id)
            continue
        m = Member(first_name=c.first_name or "Contact", last_name=c.last_name, phone=c.phone, email=c.email, responsibility=c.responsibility, is_new=mark_new, joined_at=c.joined_at or (utcnow() if mark_new else None), preferred_channel="EMAIL" if (c.email and not c.phone) else "SMS", admin_notes=f"Importé ({result.format}) — {c.source}" if c.source else f"Importé ({result.format})")
        if all_members is not None and not all_members.dynamic_rule:
            m.groups.append(all_members)
        if group is not None and not group.dynamic_rule and group is not all_members:
            m.groups.append(group)
        db.add(m)
        db.flush()
        result.created_ids.append(m.id)
        if apply_consent and c.consent:
            record_consent(db, m, sms=bool(c.phone), whatsapp=bool(c.phone), email=bool(c.email), actor=actor)
            if c.joined_at:
                m.consent_recorded_at = c.joined_at  # date de la réponse au formulaire
    audit.log(db, actor, "MEMBERS_IMPORTED", "member", "bulk", {"format": result.format, "created": len(result.created_ids), "added_to_group": len(result.added_to_group_ids), "completed": len(result.completed_ids), "skipped": len(result.contacts) - len(result.created_ids) - len(result.added_to_group_ids), "group": group.slug if group else None})
    return result
