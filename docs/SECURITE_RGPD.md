# Sécurité et protection des données

## Rôles

| Rôle | Peut |
|---|---|
| `PASTEUR` | tout, et **seul** à valider / confirmer un envoi, créer des comptes, gérer les automatisations, effacer un membre |
| `SECRETAIRE` | créer, importer (vCard, CSV, WhatsApp) et modifier membres, groupes, événements, campagnes ; consulter l'audit ; exporter les données d'un membre |
| `LECTEUR` | consulter |

Sessions : jeton HMAC-SHA256 signé avec `SECRET_KEY`, 12 h. Mots de passe : PBKDF2-HMAC-SHA256, 200 000 itérations, sel aléatoire.

## Consentement et désinscription

- Consentement **par canal** (SMS, WhatsApp, e-mail) avec date d'enregistrement.
- Exclusion automatique, avant chaque envoi, des personnes sans consentement pour le canal ou désinscrites.
- Réponse `STOP` / `ARRET` / `DESINSCRIRE` (webhook Twilio) : retrait immédiat du consentement du canal, journalisé. `START` réabonne.
- En-tête `List-Unsubscribe` sur les e-mails.
- WhatsApp : utilisation de la WhatsApp Business Platform (opt-in explicite), jamais d'automatisation d'un compte personnel.

## Minimisation

La fiche membre ne contient que : identité, coordonnées, groupe, responsabilité, date d'arrivée, anniversaire (jour et mois seulement), préférences et consentements, statut, participations factuelles, notes administratives autorisées. Aucun champ ne stocke d'état spirituel, émotionnel ou médical, et les agents ne l'infèrent jamais.

Un import de membres (répertoire, tableur, groupe WhatsApp) ne crée **jamais** de consentement : les fiches importées arrivent sans consentement et l'import est journalisé (`MEMBERS_IMPORTED`).

Les agents IA ne reçoivent **jamais** la liste des membres ni leurs coordonnées : seulement l'événement, le style, le canal, l'étiquette du public et la demande du pasteur. Les données ne servent à l'entraînement d'aucun modèle.

## Droits des personnes

| Droit | Mise en œuvre |
|---|---|
| Accès / portabilité | `GET /api/membres/{id}/export` (JSON complet, journalisé) |
| Rectification | `PATCH /api/membres/{id}` |
| Effacement | `DELETE /api/membres/{id}` (rôle PASTEUR) : anonymisation irréversible, notes supprimées, retrait des groupes, statistiques agrégées conservées |
| Opposition | désinscription par canal, `STOP` |

## Journalisation

`audit_log` enregistre qui (utilisateur, agent IA ou système), quoi, quand, sur quel objet : création, modification, contrôle, validation, confirmation, annulation, expiration, envoi, résultat, erreurs, consentements, exports, effacements, connexions et échecs de connexion, liens de validation émis. Consultable dans 🔐 Sécurité et par campagne dans l'aperçu.

## Envoi contrôlé

Voir `ARCHITECTURE.md` § Barrière de validation. Le principe : **personne ne peut envoyer un message collectif sans validation du pasteur, ni le pasteur sans avoir vu l'aperçu exact de ce qui partira.**

## Secrets et chiffrement

- Secrets uniquement en variables d'environnement (`.env` exclu de Git).
- Les identifiants Twilio / SMTP ne sont accessibles qu'aux modules `channels/` ; aucun agent IA n'y a accès.
- Jetons de validation mobile : aléatoires (256 bits), stockés hachés (SHA-256), usage unique, expiration.
- Transport : à déployer derrière TLS (reverse proxy) ; base de données chiffrée au repos (volume chiffré ou chiffrement PostgreSQL) ; hébergement européen recommandé.
- Piste d'évolution : chiffrement applicatif des coordonnées (téléphone, e-mail) avec une clé dédiée.

## Recommandations d'exploitation

1. Changer `ADMIN_PASSWORD` et `SECRET_KEY` avant la première mise en production.
2. Activer l'authentification multifacteur au niveau du reverse proxy ou du fournisseur d'identité.
3. Sauvegarder la base quotidiennement ; tester la restauration.
4. Définir une durée de conservation des journaux et des campagnes envoyées (par exemple 24 mois).
5. Tenir le registre des traitements et informer les membres (finalité, canaux, droit de retrait).
