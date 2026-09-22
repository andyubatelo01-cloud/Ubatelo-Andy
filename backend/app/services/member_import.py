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
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit
from ..models import Group, Member, utcnow
from .members import is_valid_email, is_valid_phone, normalize_phone

FORMAT_VCARD = "vcard"
FORMAT_CSV = "csv"
FORMAT_WHATSAPP = "whatsapp"

# Colonnes reconnues dans un CSV (insensible à la casse et aux accents approximatifs)
CSV_ALIASES = {
    "first_name": {"prenom", "prénom", "first name", "firstname", "first_name", "given name", "given_name"},
    "last_name": {"nom", "nom de famille", "last name", "lastname", "last_name", "family name", "family_name", "surname"},
    "phone": {"telephone", "téléphone", "tel", "tél", "phone", "mobile", "portable", "numero", "numéro", "phone 1 - value", "gsm"},
    "email": {"email", "e-mail", "mail", "courriel", "e-mail 1 - value", "adresse e-mail"},
    "responsibility": {"responsabilite", "responsabilité", "role", "rôle", "fonction"},
    "full_name": {"name", "nom complet", "full name", "fullname", "contact"},
}


@dataclass
class ImportedContact:
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    email: str = ""
    responsibility: str = ""
    source: str = ""  # information d'origine utile à l'aperçu (ex. numéro brut ou ligne CSV)
    problem: str = ""  # vide = importable

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
        }


@dataclass
class ImportResult:
    format: str
    contacts: list[ImportedContact] = field(default_factory=list)
    created_ids: list[int] = field(default_factory=list)

    @property
    def importable(self) -> list[ImportedContact]:
        return [c for c in self.contacts if not c.problem]

    def as_dict(self) -> dict:
        skipped = [c for c in self.contacts if c.problem]
        return {
            "format": self.format,
            "total": len(self.contacts),
            "importables": len(self.importable),
            "ignores": len(skipped),
            "crees": len(self.created_ids),
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
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " ").replace("-", " ")).replace("é", "e").replace("è", "e").replace("ô", "o")


def _map_headers(headers: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, h in enumerate(headers):
        nh = _norm_header(h)
        for field_name, aliases in CSV_ALIASES.items():
            if field_name in mapping:
                continue
            if nh in {_norm_header(a) for a in aliases}:
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
        contacts.append(ImportedContact(first_name=first, last_name=last, phone=cell(row, "phone"), email=cell(row, "email"), responsibility=cell(row, "responsibility"), source=" ; ".join(c for c in row if c.strip())[:80]))
    return contacts


# ── Export d'une discussion WhatsApp (.txt) ───────────────────────────────────

# Début de ligne d'un export WhatsApp (Android : « 12/03/2026 18:04 - … », iPhone : « [12/03/2026, 18:04:12] … »)
WHATSAPP_STAMP_RE = re.compile(r"^\[?\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?::\d{2})?\]?\s*(?:-\s*)?")
# « Auteur: message »
WHATSAPP_LINE_RE = re.compile(WHATSAPP_STAMP_RE.pattern + r"(?P<author>[^:\n]{1,80}?):\s", re.M)
# Numéros mentionnés en clair (auteurs non enregistrés, « X a ajouté +33 6 12 34 56 78 »)
PHONE_IN_TEXT_RE = re.compile(r"(?:\+|00)\d[\d\s().-]{7,20}\d")
SYSTEM_KEYWORDS = ("a ajouté", "added", "a rejoint", "joined", "a créé le groupe", "created group", "a retiré", "removed", "a quitté", "left")
INVISIBLE = "\u200e\u202a\u202c\u202d\u200b "


def parse_whatsapp(text: str) -> list[ImportedContact]:
    """Extrait les participants d'une discussion exportée : auteurs des messages (nom du contact tel
    qu'enregistré dans le téléphone qui a exporté, ou numéro brut) et numéros cités dans les messages système."""
    seen: dict[str, ImportedContact] = {}

    def add_phone(raw: str, source: str) -> None:
        seen.setdefault(normalize_phone(raw), ImportedContact(phone=raw.strip(), source=source))

    for line in text.splitlines():
        line = line.strip(INVISIBLE)
        stamp = WHATSAPP_STAMP_RE.match(line)
        if not stamp:
            continue
        body = line[stamp.end():].strip(INVISIBLE)
        m = WHATSAPP_LINE_RE.match(line)
        if m:
            author = m.group("author").strip(INVISIBLE)
            body = line[m.end():]
            if PHONE_IN_TEXT_RE.fullmatch(author):
                add_phone(author, "numéro non enregistré (WhatsApp)")
            else:
                first, last = split_name(author)
                seen.setdefault(author.lower(), ImportedContact(first_name=first, last_name=last, source="participant WhatsApp"))
        if any(k in body.lower() for k in SYSTEM_KEYWORDS):
            for ph in PHONE_IN_TEXT_RE.findall(body):
                add_phone(ph, "numéro cité dans le groupe WhatsApp")
    return list(seen.values())


# ── Validation, dédoublonnage, création ───────────────────────────────────────


def parse_contacts(fmt: str, text: str) -> list[ImportedContact]:
    if fmt == FORMAT_VCARD:
        return parse_vcard(text)
    if fmt == FORMAT_CSV:
        return parse_csv(text)
    return parse_whatsapp(text)


def prepare(db: Session, filename: str, data: bytes, fmt: str | None = None) -> ImportResult:
    """Analyse le fichier et signale, pour chaque contact, s'il est importable."""
    text = decode_upload(data)
    fmt = fmt or detect_format(filename, text)
    result = ImportResult(format=fmt, contacts=parse_contacts(fmt, text))

    existing_phones = {p for p in db.scalars(select(Member.phone).where(Member.phone != "")).all()}
    existing_emails = {e for e in db.scalars(select(Member.email).where(Member.email != "")).all()}
    seen_phones: set[str] = set()
    seen_emails: set[str] = set()

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
        if not c.phone and not c.email:
            c.problem = "ni téléphone ni e-mail"
            continue
        if not c.first_name and not c.last_name:
            # Numéro seul (WhatsApp non enregistré) : on garde un nom provisoire à corriger sur la fiche
            c.first_name, c.last_name = "Contact", c.phone or c.email
        if c.phone and (c.phone in existing_phones or c.phone in seen_phones):
            c.problem = "déjà présent (téléphone)"
            continue
        if c.email and (c.email in existing_emails or c.email in seen_emails):
            c.problem = "déjà présent (e-mail)"
            continue
        if c.phone:
            seen_phones.add(c.phone)
        if c.email:
            seen_emails.add(c.email)
    return result


def commit_import(db: Session, result: ImportResult, actor: str, group: Group | None = None, mark_new: bool = True) -> ImportResult:
    """Crée les membres importables. Aucun consentement n'est enregistré à l'import."""
    all_members = db.scalar(select(Group).where(Group.slug == "membres"))
    for c in result.importable:
        m = Member(first_name=c.first_name or "Contact", last_name=c.last_name, phone=c.phone, email=c.email, responsibility=c.responsibility, is_new=mark_new, joined_at=utcnow() if mark_new else None, admin_notes=f"Importé ({result.format}) — {c.source}" if c.source else f"Importé ({result.format})")
        if all_members is not None and not all_members.dynamic_rule:
            m.groups.append(all_members)
        if group is not None and not group.dynamic_rule and group is not all_members:
            m.groups.append(group)
        db.add(m)
        db.flush()
        result.created_ids.append(m.id)
    audit.log(db, actor, "MEMBERS_IMPORTED", "member", "bulk", {"format": result.format, "created": len(result.created_ids), "skipped": len(result.contacts) - len(result.importable), "group": group.slug if group else None})
    return result
