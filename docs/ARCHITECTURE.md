# Architecture technique

## Vue d'ensemble

```
┌──────────────────────────── Navigateur / téléphone ─────────────────────────────┐
│  Dashboard SPA (frontend/)        Page mobile /valider/{jeton}                  │
└───────────────┬─────────────────────────────────┬───────────────────────────────┘
                │ HTTPS (JSON, Bearer)            │ HTTPS (jeton usage unique + mot de passe)
┌───────────────▼─────────────────────────────────▼───────────────────────────────┐
│                          API FastAPI  (backend/app/api)                         │
│  auth · membres · groupes · événements · campagnes · validation · bureau · webhooks │
├──────────────────────────────────────────────────────────────────────────────────┤
│                          Services (backend/app/services)                        │
│  campaign_engine ─ preflight ─ personalization ─ members ─ events ─ briefing    │
│  scheduling (automatisations + planificateur) ─ notifications (centre mobile)   │
├───────────────────────────────┬──────────────────────────────────────────────────┤
│   Agents IA (backend/app/agents)   │   Canaux (backend/app/channels)             │
│   Directeur, Sarah, Communication, │   console · Twilio SMS · Twilio WhatsApp ·  │
│   Berger, Membres, Events,         │   SMTP                                      │
│   Tableau de bord                  │   ↑ atteints UNIQUEMENT via                 │
│   LLM : Anthropic ou gabarits      │     campaign_engine.dispatch()              │
├───────────────────────────────┴──────────────────────────────────────────────────┤
│               SQLAlchemy 2 → SQLite (dev) / PostgreSQL (prod)                    │
│  users · members · groups · events · attendances · campaigns · deliveries ·      │
│  automations · tasks · notifications · audit_log · approval_tokens · agent_runs  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Cycle de vie d'une campagne

```
DRAFT ──contrôles──► READY_FOR_REVIEW ──validation PASTEUR──► APPROVED ──► SCHEDULED ──► SENDING ──► SENT
  │                      │      ▲                                  │            │                     └► FAILED
  │                      │      └── modification (retour DRAFT)    │            │
  ├──► BLOCKED ◄─────────┘  (anomalie bloquante)                   │            │
  ├──► CANCELLED  (DRAFT, READY_FOR_REVIEW, BLOCKED, APPROVED, SCHEDULED)
  └──► EXPIRED    (date d'envoi dépassée sans validation : jamais envoyée)
```

Extensions par rapport au cahier des charges, toutes dans le sens de la sécurité :

- `BLOCKED` : les contrôles ont détecté une anomalie bloquante ; la campagne ne peut pas être présentée à la validation.
- `EXPIRED` : matérialise la règle « une absence de réponse n'est jamais une validation ».
- `FAILED` : tous les envois ont échoué (fournisseur indisponible) ; réédition possible.

Identifiants : `CAM-AAAA-NNN`, séquence annuelle.

## Barrière de validation (défense en profondeur)

| Niveau | Mécanisme | Où |
|---|---|---|
| 1 | Rôle `PASTEUR` obligatoire pour `approve()` / `confirm()` | `campaign_engine._require_pastor` |
| 2 | Empreinte SHA-256 du contenu validé (`approved_hash`) comparée à l'empreinte courante avant l'envoi | `assert_sendable()` |
| 3 | Modification ⇒ retour `DRAFT`, effacement de la validation, invalidation des jetons | `update_campaign()` |
| 4 | Double validation par phrase exacte au-delà du seuil ou si sensible | `approve()` + `confirm()` |
| 5 | Jeton mobile à usage unique, lié à l'empreinte, expirant, + mot de passe | `issue_approval_token()` / `resolve_approval_token()` |
| 6 | Le planificateur ne traite que `APPROVED` / `SCHEDULED` et refuse (journalise) toute `ApprovalRequired` | `dispatch_due()` |
| 7 | Les connecteurs ne sont importés que par `campaign_engine` et `notifications` (message adressé au pasteur lui-même) | revue de code, tests |

## Contrôles pré-envoi (`preflight.py`)

`canal`, `groupe`, `message`, `objet` (e-mail), `longueur SMS`, `variables reconnues`, `variables d'événement`, `date`, `heure`, `envoi avant l'événement`, `destinataires valides`, `consentement`, `doublons`, `coordonnées`, `variables membres`. Chaque contrôle est `BLOCK`, `WARN` ou `INFO`. Le rapport est stocké sur la campagne et affiché dans l'aperçu ; le coût SMS est estimé à partir du nombre de segments (GSM-7 / UCS-2).

## Audiences

- **Groupes classiques** : appartenance explicite (`member_groups`).
- **Groupes dynamiques** : règle JSON évaluée à la volée : `active_days`, `absent_since_days`, `joined_within_days`, `consent`, `not_confirmed_event_id`.
- **Ciblage individuel** : `explicit_member_ids` (message d'encouragement, relance des non-confirmés).
- **Exclusions** : `excluded_member_ids`, plus exclusion automatique des désinscrits, des sans-consentement, des doublons et des coordonnées invalides.

## Planificateur

Un fil d'arrière-plan (`SchedulerThread`) exécute `tick()` toutes les `SCHEDULER_INTERVAL_SECONDS` :

1. `run_automations` — prépare les campagnes dues (hebdomadaire, mensuelle, quotidienne, avant/après événement, idempotent par clé d'occurrence) ;
2. `expire_stale` — expire les campagnes non validées dont la date est passée ;
3. `dispatch_due` — envoie les campagnes validées dont l'heure est venue ;
4. `notify_pastor_of_pending` — envoie un lien de validation pour chaque campagne prête sans lien actif ;
5. briefing quotidien à `DAILY_BRIEFING_HOUR`.

Le fil est remplaçable par un cron externe ou n8n en appelant `POST /api/planificateur/executer`.

## Intégration IA

`agents/llm.py` expose `LLMProvider` avec deux implémentations : `TemplateProvider` (hors-ligne, déterministe) et `AnthropicProvider` (SDK officiel, sorties structurées via `messages.parse`, pensée adaptative, effort `medium`). Les agents ne transmettent au modèle que l'événement, le style, le canal, l'étiquette du public et la demande du pasteur. Pour ajouter un fournisseur (OpenAI, modèle local…), implémentez `generate_text` / `generate_structured` et enregistrez-le dans `get_provider()`.

## Ajouter un agent, un canal, une automatisation

- **Agent** : sous-classe de `agents.base.Agent`, méthode métier renvoyant un `AgentResult`, entrée dans `AGENT_ROSTER`, intention dans `DirecteurAgent._parse` / `_do_<intent>`.
- **Canal** : sous-classe de `channels.base.ChannelGateway`, enregistrement dans `channels._build`, variable `XXX_PROVIDER`.
- **Automatisation** : nouveau `kind` dans `scheduling.run_automations`.

## API

Documentation OpenAPI générée : `/api/docs`. Principales routes :

| Domaine | Routes |
|---|---|
| Auth | `POST /api/auth/login`, `GET /api/auth/me`, `GET/POST/DELETE /api/auth/users` |
| Membres | `GET/POST /api/membres`, `GET/PATCH/DELETE /api/membres/{id}`, `/notes`, `/consentement`, `/desinscription`, `/export`, `/message` |
| Groupes | `GET/POST /api/groupes`, `GET/DELETE /api/groupes/{id}`, `POST/DELETE /api/groupes/{id}/membres/{mid}` |
| Suivi | `GET /api/suivi`, `POST /api/suivi/relance` |
| Événements | `GET/POST /api/evenements`, `GET/PATCH/DELETE /api/evenements/{id}`, `/planifier`, `/presences`, `/compte-rendu` |
| Campagnes | `GET/POST /api/campagnes`, `/a-valider`, `/statuts`, `/rediger`, `/variantes`, `GET/PATCH /api/campagnes/{ref}`, `/controler`, `/valider`, `/confirmer`, `/annuler`, `/rapport`, `/envoyer-lien-validation` |
| Validation mobile | `GET /valider/{jeton}`, `GET/POST /api/valider/{jeton}` |
| Bureau | `/api/dashboard`, `/api/briefing`, `/api/dimanche`, `/api/agents`, `POST /api/agents/commande`, `/api/taches`, `/api/notifications`, `/api/automatisations`, `/api/planificateur/executer`, `/api/audit`, `/api/parametres` |
| Webhooks | `POST /webhooks/twilio/inbound` (STOP / START / OUI), `POST /webhooks/twilio/status` |
