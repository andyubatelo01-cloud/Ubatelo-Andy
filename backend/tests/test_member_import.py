"""Import de membres : répertoire iPhone (vCard), CSV, export de groupe WhatsApp."""
from __future__ import annotations

import io

from app.services import member_import as mi

from .conftest import login

VCARD = """BEGIN:VCARD
VERSION:3.0
N:Dupont;Marie;;;
FN:Marie Dupont
TEL;type=CELL;type=VOICE;type=pref:06 12 34 56 78
TEL;type=HOME:01 44 55 66 77
EMAIL;type=INTERNET;type=HOME:Marie.Dupont@example.org
TITLE:Responsable accueil
END:VCARD
BEGIN:VCARD
VERSION:3.0
N:;;;;
FN:Paul Martin
TEL;type=CELL:+33 6 98 76 54 32
END:VCARD
BEGIN:VCARD
VERSION:2.1
N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:Bouchard;Ren=C3=A9;;;
TEL;CELL:+41 79 123 45 67
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Sans Numero
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Doublon
TEL;type=CELL:0612345678
END:VCARD
"""

CSV_SEMICOLON = """Prénom;Nom;Téléphone;E-mail;Responsabilité
Marie;Dupont;06 12 34 56 78;marie@example.org;Chorale
Paul;Martin;;paul@example.org;
Luc;Bernard;12345;;
"""

WHATSAPP_ANDROID = """12/03/2026 18:04 - Les messages et les appels sont chiffrés de bout en bout.
12/03/2026 18:04 - Marie Dupont a créé le groupe « Jeunesse »
12/03/2026 18:05 - Marie Dupont a ajouté +33 6 98 76 54 32
12/03/2026 18:06 - Marie Dupont: Bienvenue à tous : on se retrouve dimanche !
12/03/2026 18:07 - +33 6 11 22 33 44: Merci Marie
12/03/2026 18:08 - LEROY Sophie: Super
12/03/2026 18:09 - Marie Dupont: <Médias omis>
"""

WHATSAPP_IPHONE = """[12/03/2026, 18:04:12] ‎Marie Dupont a ajouté ‎+33 6 98 76 54 32
[12/03/2026, 18:06:01] Marie Dupont: Bienvenue !
[12/03/2026, 18:07:45] ‎+33 6 11 22 33 44: Merci
"""


def test_parse_vcard_iphone():
    contacts = mi.parse_vcard(VCARD)
    assert [c.display_name for c in contacts] == ["Marie Dupont", "Paul Martin", "René Bouchard", "Sans Numero", "Doublon"]
    marie = contacts[0]
    assert marie.phone == "06 12 34 56 78"  # le mobile est préféré au fixe
    assert marie.email == "Marie.Dupont@example.org" and marie.responsibility == "Responsable accueil"
    assert contacts[1].first_name == "Paul" and contacts[1].last_name == "Martin"  # FN découpé quand N est vide


def test_parse_csv_with_french_headers():
    contacts = mi.parse_csv(CSV_SEMICOLON)
    assert len(contacts) == 3
    assert contacts[0].first_name == "Marie" and contacts[0].phone == "06 12 34 56 78" and contacts[0].responsibility == "Chorale"
    assert contacts[1].email == "paul@example.org"


def test_parse_csv_without_header_uses_positional_columns():
    contacts = mi.parse_csv("Marie,Dupont,0612345678,marie@example.org\nPaul,Martin,0698765432,\n")
    assert [c.display_name for c in contacts] == ["Marie Dupont", "Paul Martin"]


def test_parse_whatsapp_android_and_iphone():
    for text in (WHATSAPP_ANDROID, WHATSAPP_IPHONE):
        contacts = mi.parse_whatsapp(text)
        names = {c.display_name for c in contacts}
        phones = {mi.normalize_phone(c.phone) for c in contacts if c.phone}
        assert "Marie Dupont" in names
        assert phones >= {"+33698765432", "+33611223344"}
        assert not any("chiffrés" in c.display_name for c in contacts)
    android = mi.parse_whatsapp(WHATSAPP_ANDROID)
    sophie = next(c for c in android if c.last_name == "LEROY")
    assert sophie.first_name == "Sophie"  # convention « NOM Prénom »
    assert len([c for c in android if c.display_name == "Marie Dupont"]) == 1


def test_detect_format():
    assert mi.detect_format("contacts.vcf", "") == mi.FORMAT_VCARD
    assert mi.detect_format("export.txt", VCARD) == mi.FORMAT_VCARD
    assert mi.detect_format("membres.csv", "") == mi.FORMAT_CSV
    assert mi.detect_format("Discussion WhatsApp avec Jeunesse.txt", WHATSAPP_ANDROID) == mi.FORMAT_WHATSAPP
    assert mi.detect_format("x.txt", WHATSAPP_IPHONE) == mi.FORMAT_WHATSAPP


def test_prepare_flags_duplicates_and_invalid(db, members):
    # members[0] a le téléphone +336000000001 ; on importe un vCard le contenant
    text = "BEGIN:VCARD\nFN:Déjà Là\nTEL;type=CELL:+33 6 00 00 00 01\nEND:VCARD\n" + VCARD
    res = mi.prepare(db, "contacts.vcf", text.encode())
    by_name = {c.display_name: c for c in res.contacts}
    assert by_name["Déjà Là"].problem == "" and by_name["Déjà Là"].existing_id == members[0].id  # sera ajouté au groupe, pas recréé
    assert by_name["Marie Dupont"].problem == "" and by_name["Marie Dupont"].phone == "+33612345678" and by_name["Marie Dupont"].email == "marie.dupont@example.org"
    assert by_name["René Bouchard"].problem == "" and by_name["René Bouchard"].phone == "+41791234567"
    assert by_name["Sans Numero"].problem.startswith("ni téléphone ni e-mail")
    assert by_name["Doublon"].problem.startswith("en double dans le fichier")  # même numéro que Marie dans le fichier
    assert len(res.to_create) == 3 and len(res.existing) == 1


def test_api_import_two_steps(client, db):
    h = login(client, "sarah@test.org")
    groups = {g["nom"]: g["id"] for g in client.get("/api/groupes", headers=h).json()}
    files = {"file": ("contacts.vcf", io.BytesIO(VCARD.encode()), "text/vcard")}

    # 1. Aperçu : rien n'est créé
    r = client.post("/api/membres/import", files=files, data={"dry_run": "true"}, headers=h)
    assert r.status_code == 200, r.text
    p = r.json()
    assert p["format"] == "vcard" and p["total"] == 5 and p["importables"] == 3 and p["crees"] == 0
    assert client.get("/api/membres", headers=h).json() == []

    # 2. Confirmation dans le groupe Chorale
    files = {"file": ("contacts.vcf", io.BytesIO(VCARD.encode()), "text/vcard")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "false", "group_id": str(groups["Chorale"])}, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["crees"] == 3
    listed = client.get("/api/membres", headers=h).json()
    assert len(listed) == 3
    marie = next(m for m in listed if m.get("last_name") == "Dupont")
    assert marie["phone"] == "+33612345678" and marie["is_new"] is True
    assert set(marie["groups"]) == {"Membres", "Chorale"}
    # Aucun consentement n'est déduit d'un import
    assert not (marie["consent_sms"] or marie["consent_whatsapp"] or marie["consent_email"])

    # 3. Re-importer le même fichier ne recrée personne ; avec un groupe, les membres connus y sont ajoutés
    files = {"file": ("contacts.vcf", io.BytesIO(VCARD.encode()), "text/vcard")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "false", "group_id": str(groups["Jeunesse"])}, headers=h)
    p = r.json()
    assert p["crees"] == 0 and p["existants"] == 3 and p["ajoutes_au_groupe"] == 3 and p["ignores"] == 2
    assert len(client.get("/api/membres", headers=h).json()) == 3
    marie = next(m for m in client.get("/api/membres", headers=h).json() if m["last_name"] == "Dupont")
    assert set(marie["groups"]) == {"Membres", "Chorale", "Jeunesse"}

    # 4. Exclure des lignes avec skip (index dans l'aperçu)
    files = {"file": ("c.csv", io.BytesIO("Prénom;Nom;Téléphone\nA;Un;0611111111\nB;Deux;0622222222\n".encode()), "text/csv")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "false", "skip": "0"}, headers=h)
    assert r.json()["crees"] == 1
    assert [m["first_name"] for m in client.get("/api/membres?q=Deux", headers=h).json()] == ["B"]


def test_api_import_whatsapp_and_errors(client):
    h = login(client)
    files = {"file": ("Discussion WhatsApp avec Jeunesse.txt", io.BytesIO(WHATSAPP_ANDROID.encode()), "text/plain")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "false"}, headers=h)
    assert r.status_code == 200, r.text
    p = r.json()
    assert p["format"] == "whatsapp"
    # Les participants nommés sans numéro sont signalés, les numéros cités sont importés avec un nom provisoire
    named = next(c for c in p["contacts"] if c["prenom"] == "Marie")
    assert named["probleme"].startswith("ni téléphone ni e-mail")
    assert p["crees"] == 2
    listed = client.get("/api/membres", headers=h).json()
    assert {m["phone"] for m in listed} == {"+33698765432", "+33611223344"}
    assert all(m["first_name"] == "Contact" for m in listed)

    # Lecteur : interdit
    from app.models import Role, User
    from app.security import hash_password
    from app import db as dbmod

    s = dbmod.SessionLocal()
    s.add(User(email="lecteur@test.org", name="Lecteur", password_hash=hash_password("motdepasse-test"), role=Role.LECTEUR.value))
    s.commit()
    s.close()
    hl = login(client, "lecteur@test.org")
    files = {"file": ("c.csv", io.BytesIO(CSV_SEMICOLON.encode()), "text/csv")}
    assert client.post("/api/membres/import", files=files, headers=hl).status_code == 403

    # Fichier vide / sans contact
    assert client.post("/api/membres/import", files={"file": ("v.csv", io.BytesIO(b""), "text/csv")}, headers=h).status_code == 400
    assert client.post("/api/membres/import", files={"file": ("n.txt", io.BytesIO(b"bonjour"), "text/plain")}, headers=h).status_code == 400


def test_whatsapp_group_flow_after_phone_book_import(client):
    """Cas réel : 1) import du répertoire (vCard), 2) import de l'export du groupe WhatsApp dans un groupe.
    Les participants nommés (contacts enregistrés) sont retrouvés par leur nom et ajoutés au groupe."""
    h = login(client)
    groups = {g["nom"]: g["id"] for g in client.get("/api/groupes", headers=h).json()}
    files = {"file": ("contacts.vcf", io.BytesIO(VCARD.encode()), "text/vcard")}
    assert client.post("/api/membres/import", files=files, data={"dry_run": "false"}, headers=h).json()["crees"] == 3

    files = {"file": ("Discussion WhatsApp avec Jeunesse.txt", io.BytesIO(WHATSAPP_ANDROID.encode()), "text/plain")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "true", "group_id": str(groups["Jeunesse"])}, headers=h)
    p = r.json()
    marie = next(c for c in p["contacts"] if c["prenom"] == "Marie")
    assert marie["existant"] is True and marie["action"] == "ajouter_au_groupe"
    paul_number = next(c for c in p["contacts"] if c["telephone"] == "+33698765432")
    assert paul_number["existant"] is True  # Paul Martin importé depuis la vCard, retrouvé par son numéro
    sophie = next(c for c in p["contacts"] if c["nom"] == "LEROY")
    assert sophie["importable"] is False  # nom inconnu et pas de numéro : impossible de la joindre

    files = {"file": ("Discussion WhatsApp avec Jeunesse.txt", io.BytesIO(WHATSAPP_ANDROID.encode()), "text/plain")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "false", "group_id": str(groups["Jeunesse"])}, headers=h)
    p = r.json()
    assert p["crees"] == 1 and p["ajoutes_au_groupe"] == 2  # +33611223344 créé ; Marie et Paul ajoutés à Jeunesse
    jeunesse = client.get(f"/api/groupes/{groups['Jeunesse']}", headers=h).json()
    assert {m["nom"] for m in jeunesse["membres"]} == {"Marie Dupont", "Paul Martin", "Contact +33611223344"}


FORM_CSV = """Horodateur,PRÉNOM,NOM,Adresse e-mail,ADRESSE,TEL. PORTABLE ,ACCEPTEZ-VOUS QUE VOS DONNÉES PERSONNELLES (NOM, ADRESSE, E-MAIL) SOIENT COLLECTÉES ET UTILISÉES PAR L'ÉGLISE ?
06/10/2024 12:37:14,Jovie,Bola,jovie@example.org,17 rue X,0769135977,Oui
13/10/2024 12:35:54,Mathys,Vanitou ,mathys@example.org,14 rue Y,665431013,Non
03/11/2024 18:56:28,Kethia,BUKA,couple@example.org,1 Allée Z,0612673131,Oui
03/11/2024 18:57:39,Aaron,Mofali Kolo,couple@example.org,1 Allée Z,+33 6 62 86 88 40,Oui
2026,,,,,,
19/10/2025 13:12:27,Ruth,,,Bobigny,33749636058,
"""

WHATSAPP_IPHONE_GROUP = """[05/09/2024 19:18:19] CCAC COMMUNIQUÉS: \u200eLes messages et les appels sont chiffrés de bout en bout.
[05/09/2024 19:19:10] Espeguy: \u200eEspeguy a été ajouté·e
[09/09/2024 10:53:13] CCAC COMMUNIQUÉS: \u200e~\u202fCCAC a ajouté Deb. Ubatelo, Gaylor Manzola et 16 autres personnes
[09/09/2024 13:28:36] ~\u202fIrene: Amen
[09/09/2024 13:29:00] \u202a+33\u00a07\u00a078\u00a063\u00a006\u00a071\u202c: Merci
"""


def test_parse_form_csv_headers_consent_and_dates():
    contacts = mi.parse_csv(FORM_CSV)
    assert [c.display_name for c in contacts] == ["Jovie Bola", "Mathys Vanitou", "Kethia BUKA", "Aaron Mofali Kolo", "Ruth"]  # la ligne « 2026 » est ignorée
    jovie = contacts[0]
    assert jovie.phone == "0769135977" and jovie.email == "jovie@example.org" and jovie.consent is True
    assert jovie.joined_at is not None and jovie.joined_at.date().isoformat() == "2024-10-06"
    assert contacts[1].consent is False and contacts[4].consent is False


def test_phone_normalization_tolerates_form_inputs():
    assert mi.normalize_phone("665431013") == "+33665431013"  # sans le 0
    assert mi.normalize_phone("33749636058") == "+33749636058"  # indicatif sans +
    assert mi.normalize_phone("\u202a+33\u00a07\u00a078\u00a063\u00a006\u00a071\u202c") == "+33778630671"  # copie WhatsApp
    assert not mi.is_valid_phone(mi.normalize_phone("0=11762981172"))
    assert not mi.is_valid_phone(mi.normalize_phone("07"))


def test_whatsapp_iphone_group_export_names_and_pushnames():
    contacts = mi.parse_whatsapp(WHATSAPP_IPHONE_GROUP)
    names = {c.display_name for c in contacts}
    assert "CCAC COMMUNIQUÉS" not in names  # nom du groupe, pas une personne
    assert {"Espeguy", "Deb. Ubatelo", "Gaylor Manzola", "Irene"} <= names  # « ~ » retiré, personnes ajoutées listées
    assert not any("autres personnes" in n for n in names)
    assert {mi.normalize_phone(c.phone) for c in contacts if c.phone} == {"+33778630671"}


def test_shared_email_is_not_a_duplicate_when_phones_differ(db):
    res = mi.prepare(db, "form.csv", FORM_CSV.encode())
    by = {c.display_name: c for c in res.contacts}
    assert by["Kethia BUKA"].problem == "" and by["Aaron Mofali Kolo"].problem == ""  # couple avec la même adresse
    assert by["Mathys Vanitou"].phone == "+33665431013" and by["Ruth"].phone == "+33749636058"


def test_api_apply_consent_only_when_requested(client):
    h = login(client)
    files = {"file": ("form.csv", io.BytesIO(FORM_CSV.encode()), "text/csv")}
    p = client.post("/api/membres/import", files=files, data={"dry_run": "true"}, headers=h).json()
    assert p["avec_consentement"] == 3
    # Sans apply_consent : aucun consentement
    files = {"file": ("form.csv", io.BytesIO(FORM_CSV.encode()), "text/csv")}
    client.post("/api/membres/import", files=files, data={"dry_run": "false", "skip": "1,2,3,4"}, headers=h)
    jovie = client.get("/api/membres?q=Bola", headers=h).json()[0]
    assert not jovie["consent_sms"] and not jovie["consent_email"]
    # Avec apply_consent : seuls les « Oui » sont enregistrés, sur les canaux joignables, à la date du formulaire
    files = {"file": ("form.csv", io.BytesIO(FORM_CSV.encode()), "text/csv")}
    r = client.post("/api/membres/import", files=files, data={"dry_run": "false", "apply_consent": "true"}, headers=h).json()
    assert r["crees"] == 4
    mathys = client.get("/api/membres?q=Vanitou", headers=h).json()[0]
    assert not mathys["consent_sms"]
    aaron = client.get("/api/membres?q=Mofali", headers=h).json()[0]
    assert aaron["consent_sms"] and aaron["consent_whatsapp"] and aaron["consent_email"]
    card = client.get(f"/api/membres/{aaron['id']}", headers=h).json()
    assert card["consentement"]["enregistre_le"].startswith("2024-11-03") and "3 novembre" in card["date_arrivee"]
