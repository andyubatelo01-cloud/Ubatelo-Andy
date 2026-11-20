# Brief pour le conseil d'administration — Bureau du Pasteur

Vous lisez ce brief sans accès à aucune autre conversation. Tout ce que vous devez savoir est ici. Écrivez votre mémo en français.

## L'idée (fichier founder/idea.md)

- What it is: un secrétariat d'IA pour les églises locales qui prépare toute la communication aux membres (SMS, WhatsApp, e-mail), le suivi pastoral et le calendrier des événements, et qui n'envoie jamais rien sans la validation explicite du pasteur depuis son téléphone.
- Who it is for: les pasteurs d'églises évangéliques et protestantes francophones indépendantes en France (en premier lieu l'Île-de-France), de 50 à 300 membres, qui gèrent eux-mêmes la communication avec un téléphone, WhatsApp et un tableur, sans secrétaire salariée.
- What it sells, at what price: un abonnement logiciel hébergé (SaaS). Hypothèse de travail à tester : 39 € HT par mois et par église, SMS facturés au coût réel en plus (≈ 0,07 € l'unité), WhatsApp et e-mail inclus. Aucun prix n'a encore été testé auprès de pasteurs.
- Where and how: en ligne, en français. L'application est déjà développée et fonctionnelle. Découverte par le bouche-à-oreille entre pasteurs, les unions d'églises, les réseaux de pasteurs sur WhatsApp et Facebook, et une démonstration en ligne. Abonnement en ligne ; version auto-hébergée (Docker) possible.
- Budget and constraints: fondateur seul (développeur), logiciel construit, pas d'équipe commerciale, budget marketing très limité. RGPD : les données d'appartenance religieuse sont des données sensibles ; consentement SMS/WhatsApp par membre ; l'IA ne reçoit jamais la liste des membres ni leurs coordonnées ; un mode hors-ligne par gabarits fonctionne sans clé API.

## Ce que le produit fait concrètement (d'après la documentation du dépôt)

- Sept « agents » : un Directeur IA qui comprend une demande en français (« Prépare une invitation pour dimanche », « Qui dois-je recontacter ? », « Briefing du jour »), une secrétaire (tâches, agenda), un rédacteur (10 types de message × 7 styles : chaleureux, pastoral, motivant, évangélisation, événementiel, administratif, rappel urgent), un agent de suivi pastoral qui propose des personnes à recontacter uniquement à partir de faits enregistrés (absence prolongée, nouveau membre, anniversaire), un agent membres, un agent événements (rétroplanning J-14, J-7, J-3, J-1, H-3, après-événement), un tableau de bord.
- Un CRM des membres : fiches, groupes (dont groupes dynamiques), consentements datés, import depuis le répertoire iPhone (vCard), un tableur CSV ou l'export d'un groupe WhatsApp, dédoublonnage, suppression ou anonymisation en lot.
- Un moteur de campagnes à états : brouillon → contrôles (destinataires valides, consentement, doublons, variables, date) → aperçu → validation du pasteur → envoi → rapport de livraison. Le silence n'est jamais une validation (la campagne expire). Au-delà de 100 destinataires ou pour un message sensible, double validation par la phrase exacte « CONFIRMER L'ENVOI ». Une empreinte SHA-256 du contenu validé est vérifiée avant l'envoi.
- Validation depuis le téléphone du pasteur : SMS avec lien à usage unique, expiration, mot de passe, boutons Valider / Modifier / Annuler.
- Canaux : SMS et WhatsApp via Twilio, e-mail via SMTP ; gestion des STOP et des accusés de livraison.
- Automatisations : rappel du culte le dimanche matin, message du mois, invitation 7 jours avant chaque événement, rappel 24 h avant. Les automatisations préparent, elles n'envoient pas.
- Technique : FastAPI + SQLAlchemy, SQLite ou PostgreSQL, Docker, 51 tests dont la preuve que rien ne part sans validation.

## Ce qui n'est pas encore connu

- Le nombre d'églises cibles en France et leur budget logiciel (aucun chiffre vérifié).
- Les concurrents et leurs prix (à cartographier par /founder-competitors).
- Le coût d'acquisition d'un client et le canal qui marche (à tester).
- Si des pasteurs paieraient 39 € par mois (à tester par /founder-consumer et /founder-pricing).
- Les coûts d'exploitation réels (hébergement, Twilio, API IA) : à chiffrer par /founder-cfo.

Ne faites aucune supposition sur ces points sans la signaler comme une question ouverte.
