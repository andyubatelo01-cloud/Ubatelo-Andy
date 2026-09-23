# 🕊️ Bureau du Pasteur — Bureau d'IA de gestion et de communication pastorale

> **L'IA prépare · le pasteur valide · le système envoie.**
> Un secrétariat augmenté par l'IA, avec sept agents spécialisés, un moteur de campagnes à validation obligatoire, un CRM des membres, un calendrier de communication automatique et un centre de validation depuis le téléphone du pasteur.

Ce dépôt contient une **application complète et fonctionnelle**, pas une maquette :

| Bloc | Contenu |
|---|---|
| **Backend** (`backend/`) | API FastAPI + SQLAlchemy (SQLite en développement, PostgreSQL en production), moteur de campagnes, planificateur, connecteurs SMS / WhatsApp (Twilio) et e-mail (SMTP), webhooks STOP / accusés de livraison |
| **Agents IA** (`backend/app/agents/`) | DIRECTEUR IA, SARAH, COMMUNICATION, BERGER, MEMBRES, EVENTS, TABLEAU DE BORD — fonctionnent **hors-ligne** (gabarits français) ou avec **Claude** via le SDK Anthropic |
| **Frontend** (`frontend/`) | Tableau de bord responsive à 11 entrées, console du Directeur IA, aperçu de campagne avec 🟢 VALIDER / 🟡 MODIFIER / 🔴 ANNULER, page mobile `/valider/{jeton}` |
| **Tests** (`backend/tests/`) | 51 tests, dont la preuve de l'invariant fondamental : **aucun message collectif ne part sans validation explicite du pasteur** |
| **Docs** (`docs/`) | Architecture, agents, sécurité & RGPD, déploiement, guide des commandes |

---

## Démarrage en 3 minutes

Sur Mac ou Linux, une seule commande suffit :

```bash
git clone https://github.com/andyubatelo01-cloud/Ubatelo-Andy.git
cd Ubatelo-Andy
./demarrer.sh
```

À la main :

```bash
git clone https://github.com/andyubatelo01-cloud/Ubatelo-Andy.git
cd Ubatelo-Andy
cp .env.example .env                 # adaptez au moins ADMIN_PASSWORD et SECRET_KEY
cd backend
pip install -e ".[dev]"
python -m app.seed                   # communauté fictive : 43 membres, 14 événements, 4 automatisations
uvicorn app.main:app --reload
```

Ouvrez <http://localhost:8000> et connectez-vous avec `ADMIN_EMAIL` / `ADMIN_PASSWORD` (par défaut `pasteur@exemple.org` / `changez-moi`). La documentation interactive de l'API est sur `/api/docs`.

Avec Docker (PostgreSQL inclus) :

```bash
cp .env.example .env
docker compose up --build
```

Tant qu'aucun fournisseur n'est configuré, les canaux sont en **mode console** : aucun message ne quitte le serveur, tout est journalisé. Vous pouvez donc explorer le système sans risque.

---

## Ce que le pasteur peut dire au Directeur IA

| Commande | Ce qui se passe |
|---|---|
| « Prépare une invitation pour dimanche. » | Trouve le prochain culte, rédige l'invitation, contrôle les destinataires, crée `CAM-2026-001` en attente de validation |
| « Rappelle aux responsables la réunion de mercredi » | Cible le groupe Responsables et l'événement du mercredi, prépare le rappel |
| « Prépare la communication pour notre retraite de prière du mois prochain. » | Génère les six campagnes J-14, J-7, J-3, J-1, H-3, après-événement, et signale les informations manquantes (lieu, responsable…) |
| « Prépare une campagne pour les personnes qui n'ont pas encore confirmé leur présence » | Calcule dynamiquement les non-confirmés de l'événement à inscriptions |
| « Quels sont les événements des deux prochaines semaines ? » | Liste l'agenda |
| « Quelles campagnes attendent ma validation ? » | Liste les campagnes `READY_FOR_REVIEW` avec leur aperçu |
| « Qui dois-je recontacter ? » | Absences prolongées, nouveaux membres, anniversaires — **faits enregistrés uniquement** |
| « Briefing du jour » | 🌅 Briefing : aujourd'hui, communications à préparer, validations, suivi, priorités, à ne pas oublier |
| « Prépare la communication pour dimanche » | 📆 Dossier du dimanche : invitation, rappel du samedi, infos pratiques, responsables, suivi, après-culte |
| « Rappelle-moi d'appeler le pasteur invité » | SARAH note une tâche |

Sans clé API, l'analyse des demandes est déterministe (mots-clés français, dates relatives, groupes connus) et les messages viennent de gabarits en sept styles. Avec `LLM_PROVIDER=anthropic`, Claude reformule les messages et classe les demandes ambiguës, **sans jamais recevoir la liste des membres ni leurs coordonnées**.

---

## Importer les membres sans les retaper

Depuis la page **Membres → 📥 Importer**, trois fichiers sont acceptés, avec un aperçu avant toute création :

| Source | Comment obtenir le fichier |
|---|---|
| **Répertoire iPhone / Mac / iCloud** (vCard `.vcf`) | iPhone : Contacts → maintenir un contact → « Sélectionner » → tout cocher → « Partager ». Mac : Contacts → ⌘A → Fichier → Exporter → « Exporter la vCard… ». iCloud : icloud.com/contacts → ⌘A → roue crantée → « Exporter la vCard ». |
| **Tableur** (`.csv`, Excel / Numbers / Google Forms / Google Contacts) | Colonnes reconnues : Prénom, Nom, Téléphone (ou « Tel. portable »), E-mail, Responsabilité, Horodateur / Date d'arrivée, et une colonne de consentement (« Acceptez-vous que vos données… », « Consentement »). Les « Oui » de cette colonne peuvent être enregistrés comme consentement, à la date de la réponse, en cochant l'option dans l'aperçu. |
| **Groupe WhatsApp** (`.txt`) | Ouvrir le groupe → nom du groupe → « Exporter la discussion » → « Sans médias ». Les participants enregistrés dans le téléphone arrivent avec leur nom, les autres avec leur numéro (nom provisoire « Contact », à corriger sur la fiche). |

Les numéros sont normalisés au format international. Dans l'aperçu, chaque contact est coché par défaut : décochez ceux qui ne font pas partie de la communauté. Les nouveaux arrivent dans le groupe « Membres » plus le groupe choisi, marqués « nouveau ». Un contact **déjà membre** (même téléphone, même e-mail, ou même nom pour un participant WhatsApp sans numéro) n'est pas recréé : il est ajouté au groupe choisi. Pour un groupe WhatsApp, importez donc d'abord votre répertoire, puis l'export du groupe en choisissant le groupe cible. Pour nettoyer après un import, le pasteur coche des fiches dans la liste (ou toute la liste filtrée) et les supprime en lot : une fiche sans historique est supprimée définitivement, une fiche déjà contactée est anonymisée. **Aucun consentement n'est déduit d'un import** : il se coche ensuite sur chaque fiche, avec date, sauf option explicite pour les réponses « Oui » d'une colonne de consentement d'un formulaire.

## La règle absolue, et comment elle est garantie

```
IA → préparation → contrôles → APERÇU → validation du pasteur → envoi → rapport
```

1. **Seul le rôle `PASTEUR` peut valider.** La secrétaire prépare et modifie ; le lecteur consulte.
2. **Le silence n'est jamais une validation.** Une campagne non validée dont la date d'envoi passe devient `EXPIRED` : elle n'est jamais envoyée.
3. **Une campagne validée est envoyée telle quelle.** L'empreinte SHA-256 du contenu validé (message, canal, cibles, date) est vérifiée juste avant l'envoi ; toute modification ramène la campagne en brouillon et invalide les liens de validation.
4. **Double validation** au-delà de `DOUBLE_CONFIRMATION_THRESHOLD` destinataires ou pour une campagne sensible : le pasteur doit répondre exactement **« CONFIRMER L'ENVOI »**.
5. **Les automatisations préparent, elles n'envoient pas.** Le planificateur n'expédie que les campagnes `APPROVED`/`SCHEDULED` portant la signature du pasteur.
6. **Contrôles pré-envoi bloquants** : destinataires valides, consentement, doublons, numéros, variables, groupe, date, heure, message. Une anomalie bloque et explique.
7. **Barrière unique dans le code** : `campaign_engine.assert_sendable()` est le seul chemin vers un connecteur. Les tests `test_approval_invariant.py` tentent chaque contournement (brouillon, secrétaire, altération directe en base, planificateur, automatisation) et vérifient qu'aucun message ne part.

### Validation depuis le téléphone

Quand une campagne est prête, le pasteur reçoit un SMS (ou une notification) :

```
🔔 BUREAU DU PASTEUR
Campagne prête : Invitation — Culte du dimanche
👥 36 destinataires · 📱 SMS
🗓️ jeudi 24 septembre — 10:00
Message : « Bonjour {PRENOM}, nous serons heureux… »
🟢 Valider / ✏️ Modifier / 🔴 Annuler : https://…/valider/<jeton>
```

Le lien est **à usage unique**, lié au contenu exact, expire après `APPROVAL_LINK_TTL_HOURS`, et exige en plus le mot de passe du pasteur. Le téléphone est la console de commandement, jamais le serveur d'envoi.

---

## Organigramme du Bureau d'IA

```
                👤 PASTEUR — décide, valide
                        │
                 🤖 DIRECTEUR IA — comprend, coordonne, présente
        ┌───────────────┼───────────────┐
   👔 SARAH       📢 COMMUNICATION    ❤️ BERGER
   agenda, tâches   7 styles de message  suivi factuel
        └───────────────┼───────────────┘
                   👥 MEMBRES — fiches, groupes, consentements
                   📅 EVENTS — rétroplanning J-14 → après
                   📨 CAMPAGNES — machine à états, contrôles
                   🔐 VALIDATION PASTEUR — rôle, empreinte, double validation
                   📱 ENVOI — SMS / WhatsApp / e-mail
                   📊 RAPPORT — livraisons, audit, tableau de bord
```

---

## Structure du dépôt

```
backend/app/
  main.py            point d'entrée FastAPI, amorçage, planificateur
  config.py          variables d'environnement
  models.py          schéma de données (membres, groupes, événements, campagnes, audit…)
  security.py        mots de passe, sessions, jetons de validation, empreintes
  services/
    campaign_engine.py   machine à états, validation, envoi contrôlé   ← cœur du système
    preflight.py         contrôles pré-envoi et estimation de coût
    personalization.py   {PRENOM} {NOM} {DATE} {HEURE} {LIEU} {EVENEMENT}
    members.py           audiences, groupes dynamiques, consentement, RGPD
    events.py            calendrier de communication
    scheduling.py        automatisations et planificateur
    briefing.py          briefing du jour, préparation du dimanche
    notifications.py     centre de validation mobile
  agents/            les sept agents + fournisseurs IA (Anthropic / gabarits)
  channels/          console, Twilio (SMS, WhatsApp), SMTP
  api/               routes REST
  seed.py            données de démonstration
backend/tests/       51 tests pytest
frontend/            index.html, app.js, styles.css, valider.html
docs/                ARCHITECTURE.md, AGENTS.md, SECURITE_RGPD.md, DEPLOIEMENT.md
```

## Tests

```bash
cd backend && python -m pytest -q
```

## Feuille de route

Le système est livré complet pour la phase 1 à 4 du cahier des charges (MVP, communication, intelligence, bureau complet). Pistes ultérieures : notifications push natives, appels automatisés, connecteur Google Calendar, chiffrement applicatif des coordonnées, interface multilingue.

## Licence

Projet privé de la communauté. Les personnes des données de démonstration sont fictives.
