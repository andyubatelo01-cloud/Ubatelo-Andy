# Déploiement

## Variables d'environnement

Voir `.env.example`. Les plus importantes :

| Variable | Rôle |
|---|---|
| `SECRET_KEY` | signature des sessions — longue chaîne aléatoire |
| `DATABASE_URL` | `sqlite:///./data/bureau.db` ou `postgresql+psycopg://…` |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NAME`, `PASTOR_PHONE` | compte PASTEUR initial et téléphone recevant les liens de validation |
| `BASE_URL` | URL publique, utilisée dans les liens de validation mobile |
| `LLM_PROVIDER`, `ANTHROPIC_API_KEY`, `LLM_MODEL` | `template` (hors-ligne) ou `anthropic` |
| `SMS_PROVIDER`, `WHATSAPP_PROVIDER`, `EMAIL_PROVIDER` | `console` ou `twilio` / `smtp` |
| `TWILIO_*`, `SMTP_*` | identifiants des fournisseurs |
| `DOUBLE_CONFIRMATION_THRESHOLD` | seuil de double validation (défaut 100) |
| `APPROVAL_LINK_TTL_HOURS` | durée de vie d'un lien mobile (défaut 48) |
| `SCHEDULER_ENABLED`, `SCHEDULER_INTERVAL_SECONDS`, `DAILY_BRIEFING_HOUR` | planificateur |

## Docker Compose (recommandé)

```bash
cp .env.example .env      # éditez SECRET_KEY, ADMIN_PASSWORD, BASE_URL, fournisseurs
docker compose up --build -d
docker compose exec app python -m app.seed   # facultatif : données de démonstration
```

Le service `db` est un PostgreSQL 16 avec volume persistant ; `app` écoute sur le port 8000. Placez un reverse proxy TLS (Caddy, Nginx, Traefik) devant.

## Twilio

1. Créez un compte, achetez un numéro SMS, activez l'expéditeur WhatsApp Business.
2. Renseignez `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_FROM`, `TWILIO_WHATSAPP_FROM=whatsapp:+…`.
3. Dans la console Twilio, configurez les webhooks :
   - message entrant → `POST {BASE_URL}/webhooks/twilio/inbound` (STOP, START, OUI) ;
   - statut de message → `POST {BASE_URL}/webhooks/twilio/status` (renseigné automatiquement à l'envoi).
4. Passez `SMS_PROVIDER=twilio` et/ou `WHATSAPP_PROVIDER=twilio`.

Pour un autre fournisseur SMS, implémentez une `ChannelGateway` (voir `ARCHITECTURE.md`).

## E-mail

`EMAIL_PROVIDER=smtp` avec `SMTP_HOST`, `SMTP_PORT` (STARTTLS), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`.

Avec une adresse Gmail : `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER` = l'adresse Gmail, `SMTP_PASSWORD` = un **mot de passe d'application** (compte Google → Sécurité → validation en deux étapes → mots de passe des applications), `SMTP_FROM` = la même adresse.

## Vérifier un canal

Page **Paramètres → Canaux** : chaque canal indique le fournisseur demandé, le fournisseur effectif, les variables manquantes et un conseil. Le bouton **Envoyer un test** (rôle PASTEUR) envoie un message vers le numéro du pasteur (ou une adresse saisie) et affiche l'erreur exacte du fournisseur, traduite en conseil (compte Twilio d'essai, jeton refusé, mot de passe Gmail, etc.). `POST /api/parametres/test-envoi`.

## IA

`LLM_PROVIDER=anthropic` et `ANTHROPIC_API_KEY` ; modèle par défaut `claude-opus-5`. Sans clé, le système fonctionne intégralement avec les gabarits.

## Sans Docker

```bash
cd backend
pip install -e ".[postgres]"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Un seul worker : le planificateur est un fil interne. Pour plusieurs workers, mettez `SCHEDULER_ENABLED=false` et appelez `POST /api/planificateur/executer` toutes les minutes depuis un cron ou n8n avec un compte PASTEUR.

## Sauvegardes et supervision

- PostgreSQL : `pg_dump` quotidien du volume.
- `GET /api/sante` pour la supervision.
- Journaux applicatifs sur la sortie standard (uvicorn).
