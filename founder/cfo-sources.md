# Sources des chiffres du CFO — Bureau du Pasteur

Relevé le 2026-11-20. Trois niveaux de fiabilité : **[public]** prix publié par le fournisseur, lien donné ; **[estimation]** chiffre du CFO avec son raisonnement, à remplacer par un devis ; **[fondateur]** chiffre que seul le fondateur peut donner, à confirmer.

## Coûts variables (par église et par mois)

| Poste | Valeur retenue | Fiabilité | Source / raisonnement |
|---|---|---|---|
| SMS sortant vers un mobile français (Twilio) | 0,0798 $ ≈ **0,074 €** par segment | [public] | https://www.twilio.com/en-us/sms/pricing/fr (« Pricing current as of November 2026 », International Numbers et Alphanumeric Sender ID : 0,0798 $ sortant). Conversion 1 $ ≈ 0,92 € (hypothèse de taux, à ajuster). Le `.env.example` du projet retient 0,07 € : cohérent. **Refacturé au coût réel à l'église, donc neutre en marge** ; seul l'écart de change et les segments doubles (messages > 160 caractères, émojis en UCS-2 : 70 caractères) sont un risque. |
| Numéro Twilio (expéditeur) | à partir de 1,15 $/mois | [public] | même page, « Phone number pricing ». L'expéditeur alphanumérique (« EGLISE ») est gratuit mais n'accepte pas les réponses STOP : un numéro loué par église ou mutualisé est nécessaire pour les réponses. Retenu : 1 numéro mutualisé pour la plateforme + 0 par église au départ. |
| WhatsApp via Twilio | 0,005 $ par message (Twilio) + tarif Meta par modèle : France « utility » 0,0300 $, « marketing » 0,0859 $ | [public] | https://www.twilio.com/en-us/whatsapp/pricing ; grille Meta octobre 2026 citée par https://reflektlab.ai/blog/whatsapp-business-api-pricing/ et https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing (1 000 messages « service » gratuits par numéro et par mois). Une invitation au culte est un message « utility » ou « marketing » selon la classification Meta : **0,035 à 0,09 € par message**. Hypothèse produit : WhatsApp inclus dans l'abonnement, plafonné ; sinon refacturé comme le SMS. |
| E-mail (SMTP) | ≈ 0 € à ce volume | [estimation] | 300 membres × 4 envois/mois = 1 200 e-mails ; un envoi transactionnel (Brevo, Postmark, SES) coûte moins de 1 € pour ce volume. Retenu 0,50 €/église/mois. |
| IA (API Anthropic) | ≈ **1,00 €/église/mois** | [estimation] | Le `.env.example` cible `claude-opus-5` : 5 $ par million de jetons en entrée, 25 $ en sortie (grille Anthropic, novembre 2026). Hypothèse : 40 demandes au Directeur IA par mois, 3 000 jetons en entrée et 400 en sortie chacune = 120 k entrée + 16 k sortie ≈ 0,60 $ + 0,40 $ = 1,00 $. Avec `claude-sonnet-5-5` (2 $ / 10 $) ce poste tombe sous 0,40 €. L'IA ne reçoit jamais la liste des membres : pas de coût lié au volume de membres. |
| Frais de paiement (Stripe) | 1,5 % + 0,25 € par transaction (carte EEE) | [public] | https://stripe.com/fr/pricing. Sur un abonnement de 39 € : 0,835 €. Le prélèvement SEPA est moins cher (≈ 0,35 €). |
| Hébergement, part variable | ≈ 0,30 €/église/mois | [estimation] | Voir hébergement ci-dessous : un serveur à ~6 € tient largement 100 églises de cette taille (API FastAPI + PostgreSQL, trafic faible). Au-delà, un second serveur. Lissé : 0,30 €. |
| Support (temps du fondateur) | non compté en variable | [fondateur] | À chiffrer : 20 minutes de support par église et par mois est une hypothèse raisonnable au lancement, prise sur le temps du fondateur. |

## Coûts fixes mensuels

| Poste | Valeur retenue | Fiabilité | Source / raisonnement |
|---|---|---|---|
| Serveur de production (UE) | **6,55 €** (Scaleway DEV1-S, 2 vCPU / 2 Go) ou 5,99 € (Hetzner CX) | [public] | https://www.scaleway.com/en/pricing/virtual-instances/ ; https://www.hetzner.com/cloud/. Hébergement en UE recommandé pour les données sensibles (RGPD). Retenu : 2 instances (prod + sauvegardes/pré-production) + stockage objet : **25 €**. |
| Nom de domaine, certificats | ≈ 1,50 €/mois | [estimation] | .fr ou .com ≈ 15 à 20 €/an ; TLS gratuit (Let's Encrypt via Caddy). |
| Outils (e-mail pro, statut, suivi d'erreurs, comptabilité) | **40 €** | [estimation] | Google Workspace Starter ≈ 7 €, suivi d'erreurs offre gratuite, logiciel de facturation/compta ≈ 20 à 30 €. |
| Assurance RC professionnelle | **25 €** | [estimation] | Les RC pro pour éditeur de logiciel démarrent autour de 25 à 40 €/mois en France ; devis à demander (Hiscox, AXA, Stello…). |
| Comptable (expert-comptable en ligne) | **60 €** | [estimation] | Offres micro-entreprise / SASU en ligne de 40 à 100 €/mois. À confirmer. |
| Numéro Twilio mutualisé | 1,15 € | [public] | Twilio, voir ci-dessus. |
| Rémunération du fondateur | **0 € au départ** (hypothèse explicite) | [fondateur] | Le modèle ci-dessous ne rémunère pas le fondateur la première année : c'est la principale faiblesse du compte d'exploitation et elle est dite telle quelle dans la note du CFO. Une variante avec 1 500 €/mois est donnée dans les scénarios. |
| Marketing récurrent | **150 €** | [estimation] | Déplacements vers des rassemblements de pasteurs, impression, quelques publications sponsorisées. Le fondateur a dit « très limité ». |

## Dépenses de démarrage (une fois)

| Poste | Valeur retenue | Fiabilité | Source / raisonnement |
|---|---|---|---|
| Création de la société (SASU/EURL) | 300 € | [estimation] | Frais de greffe + annonce légale ≈ 200 à 400 € ; capital libre. À confirmer avec le comptable. |
| Dépôt de marque INPI (France, 1 à 3 classes) | 190 € | [public] | Tarif INPI dépôt électronique : 190 € pour une classe, 40 € par classe supplémentaire (https://www.inpi.fr/). À vérifier à la date du dépôt. |
| Audit RGPD / mentions, CGV, DPA par un juriste | 1 500 € | [estimation] | Données de conviction religieuse (art. 9 RGPD) : un avis juridique est indispensable avant de vendre. Fourchette large (800 à 3 000 €). |
| Site vitrine, vidéo de démonstration, supports | 500 € | [estimation] | Fait par le fondateur ; coût = outils et éventuellement un micro/éclairage. |
| Lancement (événements, impression, publicités) | 1 000 € | [estimation] | Deux ou trois rassemblements de pasteurs + flyers + quelques annonces ciblées. |
| Réserve de trésorerie Twilio / IA | 300 € | [estimation] | Crédit prépayé initial. |

Le logiciel lui-même est déjà développé : son coût (le temps du fondateur) n'est pas compté dans le démarrage.

## Hypothèses de volume

- Unité = **une église abonnée pendant un mois** (church-month).
- Prix de l'hypothèse de départ : 39 € HT. La TVA (20 %) s'ajoute pour les églises non assujetties : prix TTC perçu par le pasteur 46,80 €.
- Capacité : pas de limite physique ; limite pratique = support par le fondateur seul, estimée à 150 églises avant d'embaucher. Retenue dans `capacity_per_day` convertie en « unités par jour » = 150 / 30 = 5.
- La montée en charge (ramp) est le chiffre le moins fiable : voir la note du CFO et le résultat du panel.

Ces chiffres ne sont ni un conseil financier, ni fiscal, ni juridique. Un expert-comptable doit vérifier la structure, les charges sociales et la TVA avant que de l'argent ne circule.
