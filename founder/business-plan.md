# Bureau du Pasteur · Business plan

**Verdict: Not yet**

- ✓ Each église-mois earns $18.17 before fixed costs (61% contribution).
- ✗ Year 1 operating LOSS: $1,080.
- ✓ Break-even is 18 église-moiss a day against a capacity of 60.
- ✗ 2 of 20 simulated buyers buy (10%, the bar is 25%).

| key number | |
| --- | ---: |
| Price | $30.00 a église-mois |
| Profit margin at plan | 43% per église-mois |
| Break-even | 18 église-moiss a day |
| Year 1 operating profit | $-1,080 |
| Startup spend | $3,685 |
| Cash needed before it pays for itself | $5,186 |
| Startup money earned back | not in year 1 |
| Buyer panel | 2 buy · 18 pass |

## The idea

- What it is: un secrétariat d'IA pour les églises locales qui prépare toute la communication aux membres (SMS, WhatsApp, e-mail), le suivi pastoral et le calendrier des événements, et qui n'envoie jamais rien sans la validation explicite du pasteur depuis son téléphone.
- Who it is for: les pasteurs d'églises évangéliques et protestantes francophones indépendantes en France (en premier lieu l'Île-de-France), de 50 à 300 membres, qui gèrent eux-mêmes la communication avec un téléphone, WhatsApp et un tableur, sans secrétaire salariée.
- What it sells, at what price: un abonnement logiciel hébergé (SaaS). **Hypothèse de travail à tester : 39 € HT par mois et par église**, SMS facturés au coût réel en plus (≈ 0,07 € l'unité), WhatsApp et e-mail inclus. Aucun prix n'a encore été testé auprès de pasteurs ; c'est la question du panel et de la tarification.
- Where and how: en ligne, en français. L'application est déjà développée et fonctionnelle (API FastAPI, tableau de bord web responsive, page mobile de validation, connecteurs Twilio et SMTP, 51 tests, documentation RGPD). Le pasteur découvre le produit par le bouche-à-oreille entre pasteurs, les unions d'églises, les réseaux de pasteurs sur WhatsApp et Facebook, et une démonstration en ligne avec une communauté fictive de 43 membres. L'abonnement se prend en ligne ; une version auto-hébergée (Docker) existe pour les églises qui le souhaitent.
- Budget and constraints: fondateur seul (développeur), le logiciel est construit, pas d'équipe commerciale, budget marketing très limité (à confirmer par le fondateur). Contraintes fortes assumées : RGPD (données de conviction religieuse = données sensibles), consentement SMS/WhatsApp par membre, l'IA (Claude via SDK Anthropic) ne reçoit jamais la liste des membres ni leurs coordonnées, et le mode hors-ligne par gabarits fonctionne sans clé API. Les mots « jamais sans validation du pasteur » sont la règle fondatrice du produit.

Note de méthode : ce fichier a été rédigé à partir du dépôt du projet (README, docs, .env.example : fuseau Europe/Paris, numéros +33, coût SMS 0,07 €). Le prix, la zone géographique prioritaire et le budget sont des hypothèses du fondateur à confirmer, signalées comme telles dans tout le dossier.

## Summary

**Verdict calculé par `compile.py` : Pas encore.** Deux vérifications sur quatre échouent : l'année 1 perd 1 080 € en exploitation (montée en charge trop lente pour un fondateur seul), et 2 pasteurs simulés sur 20 achètent (10 %, la barre est à 25 %). Les deux autres passent : chaque église-mois laisse 18,17 € avant coûts fixes (61 %) et le seuil de rentabilité, 18 églises, tient dans la capacité d'un fondateur seul (60).

### Ce qu'il faut changer, et quelle compétence le change

1. **Le segment, pas le produit.** Deux panels, deux fois 10 %, les deux acheteurs sont les mêmes : des pasteurs d'assemblées de plus de 150 membres qui utilisent déjà un assistant IA. Les églises de 50 à 100 membres ont acheté 0 % deux fois : le pasteur « voit les bancs ». La première cible est l'assemblée de 150 à 300 membres (`founder/marketing.md`). Un mix orienté vers elles porte le prix moyen de 30 à 35 € et le seuil de 18 à 15 églises (`founder/cfo.md`).
2. **La preuve par les pairs.** Après la version 2 de l'offre, l'objection n° 1 n'est plus le prix ni le RGPD mais « aucun pasteur que je connais ne l'utilise ». Seuls le programme des 10 églises fondatrices et un pilote avec une union la lèvent (`founder/launch.md`, condition C4 du conseil).
3. **Le pitch doit dire la vérité simplement** : retirer « dans vos mots » et « absents », montrer qui note les présences, faire partir la demande de consentement au nom du pasteur, offrir un essai présentable au conseil sans carte (`founder/offer.md`, re-test ; `founder/brand.md`).

### Ce que c'est, et pour qui

Bureau du Pasteur est un secrétariat de communication en ligne pour les églises évangéliques et protestantes francophones : il prépare le rappel du culte, les invitations et le suivi des personnes qu'on n'a pas vues depuis trois semaines, par WhatsApp, SMS et e-mail, et n'envoie rien sans la validation du pasteur d'un geste sur son téléphone. Il est vendu par abonnement, 19, 29 ou 49 € HT par mois selon la taille de l'assemblée, tout compris, au pasteur d'une assemblée de 150 à 300 membres en France qui ne connaît plus tous les visages.

### Les trois chiffres derrière le verdict

| | Valeur | Source |
|---|---|---|
| Contribution par église-mois | 18,17 € sur 30 € HT (61 %) | `founder/cfo.md` |
| Seuil de rentabilité | 18 églises abonnées (coûts fixes 322 €/mois, fondateur non payé) | `founder/cfo.md` |
| Année 1 | −1 080 € d'exploitation sur 4 590 € de revenus ; 28 églises en mois 12 | `founder/cfo.md` |

Avec un fondateur payé 1 500 € par mois, le seuil passe à 101 églises, au-dessus de la capacité de 60 : tel que chiffré, c'est une activité d'appoint ou une entreprise à condition d'un canal qui amène des églises par dizaines.

### Ce sur quoi le panel et le conseil sont d'accord, et où ils divergent

D'accord : l'alternative gratuite (groupe WhatsApp + bénévole) est le vrai concurrent ; la confiance (données, qui est derrière, aucun pair) bloque avant le prix ; l'effort d'entrée (import, consentements) tue l'adoption ; la distribution passe par une union, pas par de la publicité. Divergence : la lentille Offres pensait qu'une offre assez forte justifiait 79 € ; le panel a fixé le plafond de refus à 40 € pour les petites et moyennes assemblées, et seules les grandes tolèrent 49 à 59 €. Le conseil voyait le CRM comme le rempart ; le panel voit la liste des membres comme un risque à confier. Les deux ont raison : le CRM n'est un rempart qu'une fois la confiance acquise.

### Le plus grand risque, et ce qui est prévu

**La classification Meta des messages WhatsApp.** Si le rappel du culte est classé « marketing » (0,0859 $) au lieu de « utility » (0,030 $), le forfait inclus coûte 24,50 € au lieu de 9,74 € par église-mois, la contribution tombe à 3,41 € et le seuil à 95 églises : le modèle meurt. Prévu : trois gabarits réels soumis à Meta le 8 janvier 2027, verdict avant le 29 janvier ; si tout n'est pas « utility », forfait exprimé en euros et bascule SMS avant le 18 février, sinon retour à `/founder-pricing` et report (`founder/launch.md`, `founder/ops.md`). Second verrou : l'AIPD et le contrat de sous-traitance pour des données de conviction religieuse, à faire valider par un juriste avant la première église payante.

### Ce dont le fondateur a besoin pour démarrer

- **5 186 € de trésorerie** avant que l'affaire ne se paie (3 685 € de démarrage dont 1 500 € d'avis juridique, plus le creux des six premiers mois), et la capacité de vivre sans salaire de l'activité pendant l'année 1.
- **Le premier test réel** (`founder/launch.md`) : 20 pasteurs d'assemblées de 150 à 300 membres rencontrés du 11 janvier au 28 février 2027, dossier du conseil et prix en main ; succès si **au moins 5 sur 20 paient un premier trimestre fondateur avant le 28 février 2027**. Deux ou moins : « Pas encore », retour à l'offre ou au prix selon les refus.
- Un K-bis avant le 8 janvier 2027 (Twilio et Meta l'exigent), le dépôt INPI, et une union qui accepte un pilote de trois églises avant le 23 mars 2027.

### La chose à faire cette semaine

Déposer la création de la SASU au guichet unique de l'INPI (prévu le 2 décembre 2026) : tout le chemin critique (numéro français, vérification Meta, premier paiement) part du K-bis. En parallèle, rédiger les trois gabarits WhatsApp en style « utility » pour les soumettre dès que le compte Meta est vérifié.

---

Les acheteurs sont simulés et les chiffres sont des projections : de vrais pasteurs et de vrais devis les confirment. Ni conseil financier, ni juridique, ni fiscal.

## What the board said

Réuni le 2026-11-20 sur le brief `founder/board/brief.md`. Trois mémos : `founder/board/offers.md`, `founder/board/monopoly.md`, `founder/board/product.md`.

### 1. Le vote

**3 FUND IF, 0 FUND, 0 PASS. Score moyen : 5,3 / 10** (Offres 5, Monopole 5, Produit 6).

Personne ne passe, personne ne finance en l'état. Les trois lentilles disent la même chose avec des mots différents : le produit est réel et son cœur (« rien ne part sans le pasteur ») est bon ; ce qui manque, ce sont des acheteurs qui paient et un chemin pour les atteindre.

### 2. Les risques soulevés par plus d'un membre (en premier)

| Risque | Qui le soulève | En une phrase |
|---|---|---|
| **L'alternative est gratuite et déjà dans la poche du pasteur** (groupe WhatsApp + tableur + assistant IA grand public) ; la disposition à payer 39 € n'est prouvée par rien. | Offres (n° 1), Monopole (n° 2) | La douleur est une corvée, pas une hémorragie ; le budget logiciel de la cible est inconnu. |
| **L'effort d'entrée tue l'adoption** : import, dédoublonnage, consentements datés, compte Twilio, SMTP, clé API avant le premier message. | Offres (n° 3), Produit (n° 2) | Les cinq premières minutes se passent dans les coutures entre systèmes ; chaque couture est un abandon possible. |
| **Pas de distribution et pas de preuve sociale** : fondateur seul, budget quasi nul, aucun pasteur utilisateur. | Monopole (n° 1), Offres (n° 2) | « Bouche-à-oreille entre pasteurs » décrit un espoir, pas un canal ; un pasteur ne confie pas la voix de son église sans qu'un pair l'ait fait avant. |
| **Le produit dépend de canaux qu'il ne possède pas** (Twilio, Meta, SMTP) et le pasteur devrait aujourd'hui les configurer lui-même. | Produit (n° 3 et condition 3), Offres (n° 3) | Un gabarit WhatsApp refusé ou un e-mail en spam retombe sur le produit. |

Risques portés par un seul membre, à garder : la vitrine « sept agents » vend une boîte à outils et non une promesse (Produit n° 1) ; la position n'est pas défendue à dix ans face à un éditeur installé qui ajouterait un module IA en français (Monopole n° 3).

### 3. Les conditions, fusionnées, en liste à cocher

Les conditions des trois mémos se recoupent. Fusionnées et attribuées à la compétence qui les teste :

- [ ] **C1. Prix et volonté de payer.** Dix conversations de prix avec des pasteurs de la cible (39 € / 79 € / 0 €, et *qui paie* : pasteur, conseil, union). Un test de prix réel avant tout investissement marketing. → `/founder-consumer`, `/founder-pricing` (simulation d'abord), puis des pasteurs réels (`/founder-launch`).
- [ ] **C2. Marché et concurrents chiffrés.** Nombre d'églises cibles (Île-de-France puis France) et qui vend déjà quoi à ces pasteurs, à quel prix. → `/founder-competitors`.
- [ ] **C3. Modèle de coûts par église** (hébergement, Twilio, API IA, paiement) et marge à 39 €. → `/founder-cfo`.
- [ ] **C4. Une distribution prouvée, pas décrite.** Au moins une union ou un réseau de pasteurs qui recommande officiellement l'outil, et dix églises payantes venues de ce canal, coût d'acquisition noté. → `/founder-marketing`, `/founder-launch`.
- [ ] **C5. Trois églises pilotes payantes en 90 jours**, onboarding fait *pour* elles, pour mesurer l'effort réel et obtenir la preuve sociale. → `/founder-launch`.
- [ ] **C6. Réduire la promesse à un geste** : « le rappel du culte et le suivi des absents, validés depuis votre téléphone ». Les sept agents deviennent des fonctions internes ; l'offre est renommée autour du résultat. Liste écrite de ce qui disparaît de l'interface. → `/founder-offer`, `/founder-brand`.
- [ ] **C7. Un parcours d'entrée en un seul import** (export WhatsApp ou vCard) jusqu'au premier message validé, mesuré sur dix pasteurs réels sans assistance, temps et point d'abandon notés. → `/founder-ops`, `/founder-launch`.
- [ ] **C8. Le produit fournit le numéro et les canaux** : aucun compte Twilio, SMTP ou clé API à créer par le pasteur ; coûts intégrés au prix. → `/founder-cfo`, `/founder-ops`.
- [ ] **C9. Une garantie écrite** sur un résultat mesurable, dont le coût est vérifié. → `/founder-offer`, `/founder-cfo`.
- [ ] **C10. Un avantage qui se renforce** : faire du CRM des membres et des consentements la pièce centrale, viser le statut d'outil recommandé par une union plutôt que d'ajouter des agents. → `/founder-marketing`, `/founder-plan`.

### 4. La version la plus forte de cette entreprise, vue par le conseil

Ce n'est pas tout à fait ce que le fondateur a présenté. Le fondateur vend un « bureau d'IA à sept agents » ; le conseil voit une entreprise plus étroite et plus solide : **le service clés en main qui envoie le rappel du culte et retrouve les absents, en français, avec le consentement de chaque membre, sans que le pasteur ait rien à configurer et sans qu'un seul message parte sans son pouce.** Le numéro d'envoi, WhatsApp et l'e-mail sont fournis et compris dans le prix ; l'IA est invisible ; le CRM des membres avec ses consentements est la mémoire de l'église et la raison de rester. La distribution ne se fait pas par de la publicité mais par une union d'églises ou un réseau de pasteurs qui recommande l'outil, après trois pilotes nommables. Le désaccord subsiste sur le prix : la lentille Offres pense qu'une offre assez forte justifie 79 € et plus ; la lentille Monopole craint que la cible ne paie pas 39 € ; seuls des pasteurs réels trancheront.

### Désaccords conservés

- **Sur le prix** : Offres pousse vers le haut (« à 79 €, seriez-vous encore le choix évident ? »), Monopole vers le bas (« rien ne prouve qu'un pasteur de 80 membres paie 39 € »).
- **Sur ce qui protège l'entreprise** : Monopole mise sur le CRM rempli et la recommandation institutionnelle ; Produit sur la qualité de l'expérience de bout en bout ; Offres sur la preuve sociale et la garantie.
- **Sur la richesse fonctionnelle** : Offres y voit « une pile déjà épaisse » (un atout) ; Produit y voit un produit qui « n'a pas encore dit non » (un risque).

---

*Vote : 3 « financer sous conditions », score moyen 5,3/10.* Étape suivante : `/founder-competitors` (C2, en cours) puis `/founder-consumer` (C1).

## The competition

Date de relevé : 20 novembre 2026. Sources publiques uniquement, lues page par page ; chaque fait est lié à sa source. Aucun chiffre n'a été inventé ; quand un prix n'est pas public, c'est écrit « non publié ». Fichier compagnon : `competitors.csv` (même dossier).

**Périmètre.** Produit étudié : secrétariat d'IA SaaS pour églises évangéliques et protestantes francophones de 50 à 300 membres (SMS, WhatsApp, e-mail, CRM membres, suivi pastoral, calendrier), validation obligatoire du pasteur avant tout envoi, hypothèse de prix 39 € HT/mois + SMS au coût réel (voir `idea.md`). L'« article comparable » retenu pour les prix est : *une église d'environ 200 membres, abonnement mensuel, communication + membres, hors frais d'installation*.

**Limites de ce relevé.** Dans cette session, plusieurs sites n'étaient pas joignables en direct (`logiciels.pro`, `appvizer.fr`, `lecnef.org`, `capterra.fr`) ; les pages ont donc été lues via un service de récupération tiers, et `business.whatsapp.com` n'a pas pu être lu du tout. Les avis utilisateurs lus sont ceux de Capterra (en anglais) et de l'App Store français : **aucun avis en français n'a été trouvé pour Eliakim, Church Manager, Ecclo, ChMeetings, ChurchTools ou ChurchDesk** (voir § 4).

---

### 1. Le tableau (du plus direct au moins direct)

Classement par proximité avec Bureau du Pasteur : vendu en français ET pensé pour une église locale d'abord ; puis en français mais international ; puis anglophone utilisé en Europe ; puis indirects ; puis substituts.

| # | Concurrent | Type | Lieu / canal | Prix de l'article comparable (~200 membres, mensuel) | Ce qu'il vend | Accroche (verbatim) | Note / avis |
|---|---|---|---|---|---|---|---|
| 1 | [Eliakim](https://eliakim.net/) | Direct | France (Bordeaux, 2014), serveurs en France | **29 €/mois** ≤50 utilisateurs ; **59 €/mois** ≤150 ; 99 €/mois ≤450 ; sans engagement, 60 j d'essai ; pas de SMS mentionné | Planning bénévoles, cultes, louange, suivi pastoral, annonces aux membres, groupes de discussion | « Le logiciel de référence pour votre église » | n/d |
| 2 | [Church Manager](https://churchmanager.fr/pricing) | Direct | France, FR/EN, hébergement France annoncé | **50 €/mois** (Genèse, ≤200 membres) ; 100 €/mois ≤600 ; −20 % en annuel ; Starter gratuit <50 membres annoncé en [FAQ](https://churchmanager.fr/) | Membres, départements, finances et reçus fiscaux, événements, planning, nouveaux venus, RDV pastoraux, « Outils IA » | « Gérez Votre Église avec Simplicité » | n/d |
| 3 | [Ecclo](https://eglise-numerique.fr/logiciel/ecclo) | Direct | France, web/PWA | **29 €/mois** (membres illimités) ; 67 €/mois avec planning des services (relevé Église Numérique) | Entraide/diaconie, annuaire, annonces modérées, suivi pastoral et visites, planning | « Gestion d'église communautaire » | n/d |
| 4 | [Enoria](https://association-enoria.org/) | Direct (catholique) | France, association, 624 paroisses adhérentes (2024) | **600 €/an** par paroisse soit 50 €/mois ([Le Pèlerin](https://www.lepelerin.com/religions-et-spiritualites/lactualite-de-leglise/enoria-le-service-numerique-qui-facilite-la-vie-des-paroisses-10388)) ; 120 à 500 €/an selon le [diocèse de Besançon](https://www.diocese-besancon.fr/diocese/enoria) | Carnet d'adresses, groupes, salles, **mails et SMS**, sacrements, dons, droits fins | « Une solution SaaS et une association au service de l'Église pour aider à la gestion paroissiale et diocésaine. » | 4,7 / 3 notes ([App Store MaParoisse](https://apps.apple.com/fr/app/maparoisse-by-enoria/id6757308852)) |
| 5 | [ChMeetings](https://www.chmeetings.com/pricing) | Direct | International, hébergé Azure États-Unis, [interface française](https://www.chmeetings.com/fr/) (26 langues) | Gratuit ≤50 ; 12 $/mois ≤100 ; **25 $/mois ≤250** ; SMS en sus | Membres, dons, événements, e-mails/SMS/push, comptabilité, appli, IA (rédaction, recherche, connexion ChatGPT/Claude en lecture seule) | « Simplifiez la gestion de votre église grâce à une plateforme tout-en-un facile à utiliser. » | 4,9 / 168 ([Capterra](https://www.capterra.com/p/184192/Chmeetings/reviews/)) |
| 6 | [ChurchTools](https://church.tools/de/preise/) | Direct | Allemagne, hébergement Allemagne ; site DE/EN ; FR signalé par [Église Numérique](https://eglise-numerique.fr/logiciel/eliakim), non annoncé par l'éditeur | 34 €/mois (100 pers.) ; **54 €/mois (200 pers.)** ; 89 €/mois (500) ; Finances +19 € | Personnes, groupes, calendriers, services, check-in, chat, appli, assistant d'écriture IA | « Für jede Gemeindegröße das richtige Paket » | 4,6 / 18 ([Capterra](https://www.capterra.com/p/158007/ChurchTools/reviews/)) |
| 7 | [B1.church](https://b1.church/fr/church-app/) | Direct | États-Unis (association 501(c)(3)), interface française | **Gratuit** | Appli au nom de l'église : annuaire, groupes, messagerie, push/e-mail (SMS en option), dons, check-in | « L'appli de votre église, gratuite » | n/d |
| 8 | [EgliseApp](https://egliseapp.net/) | Direct (francophone, hors France) | Togo, web | **5 000 FCFA TTC/mois** tous modules | Membres, cultes, finances, comptabilité, évangélisation, nouveaux venus, planning | « Toute la gestion de votre église, en un seul endroit » | n/d |
| 9 | [Elvanto](https://hackceleration.com/fr/labs/meilleur/logiciel-gestion-eglise) (Tithely) | Direct | Australie/US ; serveurs en Europe et FR « selon l'éditeur » (relevé Hack'celeration, non vérifié) | 19 $/mois ≤50 adultes ; **39 $/mois ≤100** ; + 149 $ de mise en route | Membres, planning des équipes, groupes, portail | « Des serveurs en Europe » (titre du classement) | n/d |
| 10 | [ChurchDesk](https://churchdesk.com/en/pricing/) | Direct (anglais) | Danemark/Allemagne/UK ; **pas de version française** (`/fr` → 404) | 55 £/mois HT (100 contacts, annuel) ; **99 £/mois (500 contacts)** ; **+ 655 £ de mise en route** | Calendrier, personnes (e-mail, SMS, newsletter), formulaires, site web, dons | « Find a plan that fits your needs » | 4,7 / 15 ([Capterra](https://www.capterra.com/p/135912/ChurchDesk/reviews/)) |
| 11 | [Text In Church](https://textinchurch.com/pricing) | Direct (anglais) | États-Unis, numéros US (10DLC) | **30 $/mois** (1 250 crédits SMS, e-mails illimités) ; 38 $ ; 50 $ | SMS de masse et 2 voies, e-mails, workflows de suivi des visiteurs, réponses IA | « Simple pricing for every church size » | 4,6 / 267 ([Capterra](https://www.capterra.com/p/142758/Text-In-Church/reviews/)) ; « 4.8 from nearly 5,000 App Store ratings » (éditeur) |
| 12 | [Planning Center](https://www.planningcenter.com/pricing) | Direct (anglais) | États-Unis | People **gratuit** illimité ; SMS 0,02 $/texte ; modules payants par palier | People, Services, Giving, Check-Ins, Groups, Calendar, appli Church Center | « Only pay for what your church needs » | 4,7 / 1 139 ([Capterra](https://www.capterra.com/p/76708/Planning-Center/reviews/)) |
| 13 | [Breeze ChMS](https://www.breezechms.com/pricing) (Tithely) | Direct (anglais) | États-Unis | **72 $/mois**, contacts illimités ; 250 SMS/mois inclus puis 10 $ les 500 ([Hack'celeration](https://hackceleration.com/fr/labs/meilleur/logiciel-gestion-eglise)) | Contacts illimités, dons, SMS, e-mails, événements, appli, check-in | « Choose one flat rate » | Tithe.ly 4,1 / 1 177 Trustpilot (via Hack'celeration) |
| 14 | [WhatsApp / WhatsApp Business](https://developers.facebook.com/docs/whatsapp/pricing/) | Indirect | Appli gratuite ; API Meta par message | Appli **gratuite** ; API : par message, par catégorie et par marché (la France est un marché distinct), 1 000 messages de service gratuits/mois ; grille EUR en CSV non lue | Messagerie, groupes, listes de diffusion ; API gabarits | « Meta charges on a per-message basis » | n/d |
| 15 | [Brevo](https://www.brevo.com/fr/tarifs/) (ex-Sendinblue) | Indirect | France (Paris) | Gratuit (300 e-mails/j) ; **Starter 9 $US/mois** (5 000 e-mails, 500 contacts) ; SMS en crédits ; WhatsApp seulement en Pro à 499 $US | E-mail, SMS, CRM, formulaires, IA rédaction, MCP ChatGPT/Claude | « Gratuit pour toujours, pas de carte bleue requise » | « Plus de 3 300 avis » Capterra (éditeur) |
| 16 | [smsmode](https://www.smsmode.com/tarifs-sms/) | Indirect | France (Marseille), opérateur | Pack 1 000 SMS **0,0610 € HT/SMS** (61 €) ; Basique **9 € HT/mois + 0,0445 €/SMS** ; WhatsApp 0,0069 €/msg (plan 69 €) | SMS, TTS, RCS, WhatsApp Business, API | « Des tarifs adaptés à votre entreprise » | n/d |
| 17 | [Octopush](https://www.octopush.com/tarifs-sms/) | Indirect | France | Pack 1 000 SMS **0,061 €/SMS** (61 €) ; Basique **9 €/mois + 0,045 €/SMS** | SMS, API, formulaires, inbox, e-mail | « Des tarifs simples et transparents » | 4,3 / 93 (Avis Vérifiés) ; 4,8–4,9 ailleurs selon l'éditeur |
| 18 | [Tableur + téléphone](https://eglise-numerique.fr/guides/excel-gerer-membres-eglise) | Indirect | Partout | **Gratuit** / déjà payé | Liste de membres, colonnes libres ; ni droits fins, ni historique, ni envoi | « Excel ou Google Sheets semblent parfaitement suffisants. » | n/d |
| 19 | [Groupe WhatsApp du pasteur](https://regardsprotestants.com/actualites/vie-des-eglises/faire-eglise-ensemble-via-whatsapp/) | Substitut | Téléphone du pasteur (EPUdF Pays niortais, ~50 paroissiens) | Gratuit | Prières, méditations, prédications, nouvelles ; 3 modérateurs bénévoles | « Faire "église ensemble" via WhatsApp » | n/d |
| 20 | [Annonces en chaire + courrier + appels](https://regardsprotestants.com/actualites/vie-des-eglises/faire-eglise-ensemble-via-whatsapp/) | Substitut | Culte, boîte aux lettres, téléphone | Temps + timbres | Lettre « Cofino-nouvelles » pour « ceux qui n'ont ni de téléphone, ni adresse mail » | — | n/d |
| 21 | [Secrétaire / assistant(e) pastoral(e) bénévole](https://association-enoria.org/) | Substitut | Bénévole ou temps partiel (formation [CD Assist'](https://eliakim.net/) citée par Eliakim) | Non publié | Fichier, envois à la main, inscriptions, agenda | « Avant je devais envoyer à la main 60 SMS pour les temps forts du caté » | n/d |

**Écartés après vérification.** [Hozana](https://hozana.org/) est une « application de prière catholique » (communautés de prière), pas un logiciel de gestion d'église. [Kelio](https://www.kelio.com/fr) est un « logiciel RH : gestion des temps, paie et accès » (Bodet), sans rapport. « Eglise.app » et « church-app.fr » n'ont renvoyé aucune page éditeur ; le seul « EgliseApp » trouvé est togolais (ligne 8). [Sunergo](https://www.sunergo.net/) se présente comme « Church Management Software for Canadian Organizations », en anglais. Flocknote, Clearstream, Subsplash, PastorsLine n'annoncent ni français ni présence en France sur les fiches Capterra France consultées en recherche (PastorsLine : « Pays disponibles : États-Unis ») et n'ont pas été approfondis.

---

### 2. Fourchette de prix (article comparable : ~200 membres, mensuel, hors installation)

**Offres facturées en euros, pensées pour une église locale (5 prix publics) :**

| Concurrent | Prix retenu | Source |
|---|---|---|
| Ecclo | 29 €/mois (Essentiel, membres illimités) | [Église Numérique](https://eglise-numerique.fr/logiciel/ecclo) |
| Church Manager | 50 €/mois (Genèse, ≤200 membres) | [churchmanager.fr/pricing](https://churchmanager.fr/pricing) |
| Enoria | 50 €/mois (600 €/an) | [Le Pèlerin](https://www.lepelerin.com/religions-et-spiritualites/lactualite-de-leglise/enoria-le-service-numerique-qui-facilite-la-vie-des-paroisses-10388) |
| ChurchTools | 54 €/mois (S, 200 personnes) | [church.tools/de/preise](https://church.tools/de/preise/) |
| Eliakim | 59 €/mois (Croissance, ≤150 utilisateurs) — 29 € si ≤50 | [eliakim.net](https://eliakim.net/) |

- **Plus bas : 29 €** (Ecclo ; Eliakim pour ≤50 utilisateurs).
- **Médiane : 50 €** (Church Manager / Enoria).
- **Plus haut : 59 €** (Eliakim Croissance). ChurchDesk, hors euros, est bien au-dessus : 99 £/mois pour 500 contacts + 655 £ d'installation.
- Le **39 € HT** de l'hypothèse se place **sous la médiane euro**, au-dessus des entrées de gamme à 29 €, et nettement au-dessus de ChMeetings (25 $/mois pour 250 personnes) et des gratuits (B1.church ; Planning Center People).

**Offres en dollars ou livres (pour mémoire) :** ChMeetings 25 $ (≤250) ; Text In Church 30 $ (1 250 SMS inclus) ; Elvanto 39 $ (≤100 adultes) + 149 $ ; Breeze 72 $ ; ChurchDesk 99 £ + 655 £. **Indirects :** 9 €/mois d'abonnement SMS (smsmode, Octopush) + ~0,045 €/SMS ; Brevo Starter 9 $US ; WhatsApp appli gratuite.

**Coût SMS de référence (France, petits volumes) :** 0,061 €/SMS en pack de 1 000 chez [smsmode](https://www.smsmode.com/tarifs-sms/) et [Octopush](https://www.octopush.com/tarifs-sms/) ; 0,0445–0,045 €/SMS avec abonnement à 9 €/mois. L'hypothèse « ≈ 0,07 € l'unité » de `idea.md` est donc cohérente, légèrement au-dessus du marché des opérateurs grossistes.

---

### 3. Carte de positionnement (texte)

**Axe 1 — Prix mensuel pour ~200 membres** (gratuit → > 60 €).
**Axe 2 — Qui tient le volant de la communication ?** De « l'outil envoie / le membre publie » (automatisations, groupes ouverts) à « le pasteur reste maître de chaque envoi ».

```
                       LE PASTEUR GARDE LA MAIN SUR CHAQUE ENVOI
                                      ▲
   Secrétaire bénévole (coût caché) ● │        ● Bureau du Pasteur (39 € HT, cible)
   Annonces en chaire / courrier    ● │
                                      │   ● Ecclo 29 € (annonces « modérées par les responsables »)
                                      │
 GRATUIT ─────────────────────────────┼────────────────────────────────────── > 60 €/mois
   Tableur + téléphone ●              │  ● Eliakim 29–59 €     ● ChurchTools 54 €
   B1.church ●                        │  ● Church Manager 50 €  ● Enoria 50 €
   Planning Center People ●           │  ● ChMeetings 25 $      ● Breeze 72 $
   Groupe WhatsApp du pasteur ●       │  ● Text In Church 30 $ (workflows automatisés)
     (chacun publie, 3 modérateurs)   │  ● smsmode / Octopush 9 € + SMS (envoi « en 1 clic »)
                                      │  ● Brevo 9 $ (automation, IA de rédaction)
                                      ▼
                     L'OUTIL ENVOIE SEUL / LES MEMBRES PUBLIENT
```

Lecture :
- **Coin haut-gauche (gratuit, pasteur aux commandes)** : les substituts. Le groupe WhatsApp niortais montre la limite : « nous avons aussi reçu quelques messages qui n'allaient pas dans le sens du projet. Pour éviter que cela ne se reproduise, trois modérateurs surveillent dorénavant les publications » ([Regards protestants](https://regardsprotestants.com/actualites/vie-des-eglises/faire-eglise-ensemble-via-whatsapp/)).
- **Centre-droit (30–60 €, logiciels d'église)** : tous vendent une *base de membres* d'abord ; la communication est un module. Aucun ne met en avant une étape de validation humaine avant envoi : Text In Church vend des « Automated Workflows » ([pricing](https://textinchurch.com/pricing)), ChMeetings des « Automations » et un « Assistant de rédaction IA » ([chmeetings.com/fr](https://www.chmeetings.com/fr/)), Enoria l'envoi de SMS « En un clic, c'est fait ! » ([association-enoria.org](https://association-enoria.org/)).
- **Bas (gratuit à 9 €, génériques)** : Brevo, smsmode, Octopush, tableur. Puissants, mais rien n'est « pensé pour une église » : pas de suivi pastoral, pas de consentement par membre pour une donnée de conviction religieuse.
- **Deuxième axe utile : « construit pour les églises » vs « générique »** — les 13 directs sont construits pour les églises ; parmi eux, seuls Eliakim, Church Manager, Ecclo (France) et Enoria (catholique) sont *faits en France*, et seuls Eliakim et Church Manager annoncent l'hébergement en France ([eliakim.net](https://eliakim.net/) : « serveurs physiques en France » ; [churchmanager.fr/pays/france](https://churchmanager.fr/pays/france) : « Hébergement en France »). ChMeetings héberge « sur Microsoft Azure aux États-Unis » ([chmeetings.com/fr](https://www.chmeetings.com/fr/)).

---

### 4. Plaintes récurrentes (avis 1–3 étoiles d'abord, puis « j'aime mais… » à 4 étoiles)

Avis lus : Capterra (anglais), pages « reviews » de chaque produit, 15 à 25 avis par produit (page « most helpful » ; le tri « lowest rated » n'a pas été appliqué par le site). **Aucun avis en français trouvé** pour ces produits ; le seul avis francophone lu est celui de l'App Store sur MaParoisse by Enoria (1 avis, 4,7 sur 3 notes). Un thème est noté « mince » sous 3 avis.

#### Text In Church — 4,6 / 267 avis ([Capterra](https://www.capterra.com/p/142758/Text-In-Church/reviews/))
1. **Prix jugé trop élevé pour une petite église — 3 avis.** « their pricing was extremely high compared to the competition » (Andrea S., pasteure, 2/5, janv. 2025) ; « The cost is not feasible for all churches. » (Kyle S., lead pastor, 4/5, janv. 2025) ; « Also it is a little more expensive. » (Nathaniel O., mars 2025).
2. **Courbe d'apprentissage — 3 avis.** « There was a steep learning curve » (Daniel B., juin 2026) ; « There was a bit of a learning curve » (Admin T., avr. 2025) ; « I feel like I still have a lot to learn » (Paula R., 4/5, août 2026).
3. **Envois programmés peu fiables — 2 avis (mince).** « Often we would schedule them and they'd either not go or be sent at the wrong time (was not operator error) » (Andrea S., 2/5) ; demande de « setting specific dates for txts to go out » (Rob H., 2021).
4. **Expéditeur anonyme pris pour du spam — 1 avis (mince).** « We would love to be able to add our name or church name as the number so people don't think it's a spam call or text » (Brooke K., avr. 2026).
5. **Appli mobile lente / limitée — 2 avis (mince, 2019).** « the "app" for mobile use is rather clunky and slow » (Faith B.).

#### ChMeetings — 4,9 / 168 avis ([Capterra](https://www.capterra.com/p/184192/Chmeetings/reviews/))
1. **Prise en main / navigation peu intuitive — 5 avis.** « often I have to demonstrate to church members how to use it because it's not very intuitive » (3/5, « Needs to be more User Friendly », mai 2023) ; « Getting started, there is quite a learning curve. Even following the given guides, it feels time-consuming and difficult. » (mars 2026) ; « A little learning curve e.g. with check-ins » (janv. 2025).
2. **Outil e-mail / messages limité — 5 avis.** « I don't love their email platform. It seems laggy. I don't love that they up-sale me every time I log in. » (avr. 2026) ; « limited file upload for push notifications » (sept. 2026) ; « Some of the design features (fonts/graphics) are limited » (avr. 2026) ; impossible d'« attach a pdf file » (juil. 2026) ; e-mails aux visiteurs non membres impossibles (avr. 2026).
3. **Prix et hausse des crédits — 3 avis.** « The main con is the price. » (nov. 2025) ; « 1000 text/emails went up from 10 dollars to 15 dollars » (janv. 2026).
4. **Confidentialité des modèles partagés — 1 avis (mince).** « anyone can use anyone's template to email someone, and this can be problematic for privacy reasons » (avr. 2026).

#### Planning Center — 4,7 / 1 139 avis ([Capterra](https://www.capterra.com/p/76708/Planning-Center/reviews/))
Échantillon lu : 11 avis « most helpful », donc moins représentatif.
1. **Complexité, « trop de choix » — 3 avis.** « this can also be a little overwhelming for a first time user in regards to choice fatigue » (janv. 2026) ; « some features can take a little time to figure out » (oct. 2026) ; une église partie car l'outil « ne lui paraissait "pas du tout intuitif" » ([Hack'celeration](https://hackceleration.com/fr/labs/meilleur/logiciel-gestion-eglise)).
2. **Doublons et profils créés automatiquement — 2 avis (mince).** « It is difficult to keep the people database under control due to the automatic creation of profiles anytime anyone downloads the app, fills out a form… » (août 2025) ; « We've had several duplicates » (sept. 2025).
3. **Annuaire en opt-in trop technique pour certains membres — 1 avis (mince).** « for some users it's proven too technically difficult » (4/5, févr. 2026).
4. **Anglais uniquement** : « l'éditeur n'annonce aucune autre langue que l'anglais » ([Hack'celeration](https://hackceleration.com/fr/labs/meilleur/logiciel-gestion-eglise)).

#### ChurchTools — 4,6 / 18 avis ([Capterra](https://www.capterra.com/p/158007/ChurchTools/reviews/))
1. **Concepts et gestion des droits complexes au départ — 5 avis.** « The way to give rights can be complex » (déc. 2018) ; « You need to understand the concepts of groups, teams, the structures etc. … This can be frustrating at the beginning » (2016) ; « It's difficult at first » (2018) ; « Little bit tricky to admin sometimes » (2017).
2. **Import des données difficile — 2 avis (mince).** « To first import your data is sometimes difficult » ; « The import is not always that easy » (2016).
3. Avis anciens (2015–2021) : l'absence d'appli mobile citée deux fois en 2017 n'est plus d'actualité (appli annoncée sur [church.tools/de/preise](https://church.tools/de/preise/)).

#### ChurchDesk — 4,7 / 15 avis ([Capterra](https://www.capterra.com/p/135912/ChurchDesk/reviews/))
1. **Courbe d'apprentissage — 3 avis.** « Because the software is so comprehensive it takes a while to get used to using the features » (2017) ; « a steep learning curve » (2017) ; « I am not an intuitive user of such packages and therefore value guidance at every step. This can be frustrating. » (2018).
2. **Trop complet / trop cher pour une petite paroisse — 1 avis (mince).** « felt it did too much for us to justify the cost » (2015).
3. **Changements fréquents de l'interface — 2 avis (mince).** « The frequent system changes » (2017).
4. **Confidentialité des contacts — 1 avis (mince).** « You can't hide contacts from other registered members » (2017).

#### Enoria — App Store 4,7 / 3 notes ([MaParoisse by Enoria](https://apps.apple.com/fr/app/maparoisse-by-enoria/id6757308852))
Un seul avis, en français : « Très bien pour une v1 … On attend un peu plus d'interactivité » (mince). Aucun avis public trouvé sur l'application de gestion elle-même.

**Thèmes transversaux (4 produits sur 5) :** prise en main jugée longue pour des bénévoles ; prix ou hausses mal vécus par les petites églises ; module de communication perçu comme secondaire (e-mails « laggy », pièces jointes, expéditeur anonyme, envois programmés ratés).

---

### 5. L'écart : ce que personne ne fait bien

Évidence par évidence, en partant de ce que Bureau du Pasteur revendique (`idea.md`).

1. **« Jamais sans validation du pasteur » : aucun concurrent ne vend cela.** Les pages tarifaires lues vendent l'inverse : « Automated Workflows » et « Keyword Auto-Responder » ([Text In Church](https://textinchurch.com/pricing)), « Automations » ([ChMeetings](https://www.chmeetings.com/pricing)), « Workflows » ([ChurchDesk](https://churchdesk.com/en/pricing/)), SMS « En un clic, c'est fait ! » ([Enoria](https://association-enoria.org/)). Le seul écho d'un contrôle humain est la validation des *bénévoles* et des *annonces des membres* chez Ecclo (« annonces … modérées par les responsables », [Église Numérique](https://eglise-numerique.fr/logiciel/ecclo)), pas une validation des envois sortants du pasteur. Un avis Text In Church illustre le risque : des SMS « sent at the wrong time (was not operator error) » ([Capterra](https://www.capterra.com/p/142758/Text-In-Church/reviews/)). **Écart réel.**

2. **IA de rédaction sans transmettre la liste des membres : l'inverse du marché.** ChMeetings connecte « ChatGPT, Claude, Gemini ou Grok » aux données de la paroisse « avec un accès en lecture seule » ([chmeetings.com/fr](https://www.chmeetings.com/fr/)) ; Brevo propose un « MCP pour ChatGPT et Claude » pour « gérer vos campagnes et vos contacts » ([brevo.com/fr/tarifs](https://www.brevo.com/fr/tarifs/)) ; ChurchTools inclut un « KI-Schreibassistent » ([church.tools/de/preise](https://church.tools/de/preise/)) ; Text In Church promet seulement que « The AI tools we use are not allowed to train on your data » ([pricing](https://textinchurch.com/pricing)). Personne n'affirme « l'IA ne reçoit jamais la liste des membres ». **Écart réel, mais à prouver techniquement et à expliquer simplement.** Attention : l'IA de rédaction en elle-même n'est plus un différenciateur (ChMeetings, ChurchTools, Brevo l'ont).

3. **WhatsApp comme canal d'église : absent des logiciels d'église.** Aucun des 13 directs ne liste WhatsApp comme canal d'envoi (ChMeetings parle vaguement de « se connecter à des applications de messagerie »). WhatsApp n'existe que chez les génériques : smsmode à 0,0069 €/msg sur plan 69 €/mois ([tarifs](https://www.smsmode.com/tarifs-sms/)), Brevo réservé au plan Pro à 499 $US/mois ([tarifs](https://www.brevo.com/fr/tarifs/)). Or le terrain montre l'usage : une cinquantaine de paroissiens niortais sur un groupe WhatsApp ([Regards protestants](https://regardsprotestants.com/actualites/vie-des-eglises/faire-eglise-ensemble-via-whatsapp/)). **Écart réel**, sous réserve du coût et des règles de la WhatsApp Business Platform (facturation par message, [Meta](https://developers.facebook.com/docs/whatsapp/pricing/)).

4. **Français + hébergement en France + RGPD « données sensibles » : écart partiel seulement.** Eliakim (« serveurs physiques en France », « respect strict du RGPD », [eliakim.net](https://eliakim.net/)) et Church Manager (« Hébergement en France », « Gestion des consentements », [churchmanager.fr/pays/france](https://churchmanager.fr/pays/france)) occupent déjà ce terrain. En revanche, **aucun n'évoque explicitement l'article 9 du RGPD (conviction religieuse = donnée sensible) ni le consentement SMS/WhatsApp par membre** ; Hack'celeration rappelle que « Le RGPD classe l'appartenance religieuse parmi les données sensibles (article 9). Ton fichier de membres en est une. » et que ChMeetings « héberge ses services sur Microsoft Azure aux États-Unis » ([Hack'celeration](https://hackceleration.com/fr/labs/meilleur/logiciel-gestion-eglise)). **Écart de discours plus que de fonctionnalité** : le dire clairement, documents à l'appui, reste rare.

5. **SMS inclus dans un outil d'église francophone : quasi inexistant.** Eliakim ne mentionne pas le SMS ; Church Manager parle de « communication multicanale » sans prix SMS ; ChMeetings facture les SMS en sus ; seul Enoria (catholique) inclut l'envoi de SMS et de mails « en un clic ». Les pasteurs font encore « à la main 60 SMS » ([témoignage Enoria](https://association-enoria.org/)). **Écart réel côté évangélique/protestant**, avec un prix de marché connu (0,045–0,061 €/SMS, [smsmode](https://www.smsmode.com/tarifs-sms/), [Octopush](https://www.octopush.com/tarifs-sms/)).

6. **Où il n'y a pas d'écart.** Sur le *prix*, 39 € HT n'est pas un avantage : Ecclo et Eliakim démarrent à 29 €, ChMeetings à 12–25 $, B1.church est gratuit. Sur la *base de membres*, la *gestion des bénévoles*, les *dons et reçus fiscaux*, les concurrents français sont plus complets (Church Manager : « reçus Cerfa conformes » ; Eliakim : louange, plannings). Bureau du Pasteur ne gagnera pas comme « gestion d'église » généraliste ; il gagne comme **secrétariat de communication contrôlé**.

**En une phrase :** personne ne vend aujourd'hui, en français, un outil qui *prépare* SMS + WhatsApp + e-mail et suivi pastoral avec une IA qui ne voit pas le fichier des membres, et qui *n'envoie rien* sans l'accord du pasteur depuis son téléphone ; les concurrents vendent soit une base de membres (Eliakim, Church Manager, ChMeetings), soit un canal d'envoi automatisé (Text In Church, smsmode, Brevo).

---

### 6. La menace : qui peut copier le plus vite, et comment

1. **ChMeetings** (le plus rapide). Déjà en français, 26 langues, gratuit ≤50 personnes puis 12–25 $/mois, « Assistant de rédaction IA » et connecteurs ChatGPT/Claude en place, SMS via Twilio, « migration gratuite des données » ([chmeetings.com/fr](https://www.chmeetings.com/fr/), [pricing](https://www.chmeetings.com/pricing)). Il lui suffit d'ajouter un bouton « soumettre à validation » et un canal WhatsApp pour neutraliser le discours. Faiblesses à exploiter : hébergement aux États-Unis, interface jugée « not very intuitive » par des bénévoles, upsell à chaque connexion ([Capterra](https://www.capterra.com/p/184192/Chmeetings/reviews/)).

2. **Eliakim** (le plus crédible en France). « Plus de 10 ans », 2 092 comptes d'églises revendiqués, 13 124 utilisateurs, « serveurs propriétaires en France », suivi pastoral et « Communication Directe » déjà présents, partenariats (ThéoAsso, Ekklesi, CD Assist') ([eliakim.net](https://eliakim.net/)). Ajouter un assistant de rédaction et un envoi SMS/WhatsApp validé est un chantier de quelques mois ; sa V2 est en cours ([Église Numérique](https://eglise-numerique.fr/logiciel/eliakim)). C'est aussi le partenaire ou l'acquéreur le plus naturel.

3. **Church Manager** (ambition affichée). « 500+ Églises gérées », « intégration future de l'intelligence artificielle », « Outils IA » déjà au catalogue, hébergement France, reçus fiscaux ([churchmanager.fr](https://churchmanager.fr/), [pricing](https://churchmanager.fr/pricing)). Incohérences visibles (FAQ : « les détails sur nos différentes formules d'abonnement seront dévoilés très bientôt » alors que la page tarifs est publiée ; « n°1 en France » auto-proclamé) : exécution à surveiller plutôt que menace immédiate.

4. **Brevo** (le générique français). E-mail + SMS + WhatsApp + IA + MCP, 600 000 clients, « plateforme marketing 100 % française » ([tarifs](https://www.brevo.com/fr/tarifs/)). Ne fera jamais de « suivi pastoral », mais un pasteur à l'aise avec le numérique peut s'en servir à 9 $/mois ; c'est le concurrent du **prix**.

5. **Text In Church / Tithely** : pas de français, numéros américains ; menace faible en France tant qu'ils n'ouvrent pas l'Europe (Text In Church n'a qu'une page « Australia pricing » en plus des États-Unis, [pricing](https://textinchurch.com/pricing)).

Défense raisonnable : faire de « jamais sans validation » et « l'IA ne voit pas vos membres » une **promesse écrite et vérifiable** (documentation RGPD, démonstration), prendre position sur WhatsApp avant les autres, et viser la distribution par les unions d'églises et réseaux de pasteurs plutôt que par les comparateurs, où ChMeetings est déjà « le meilleur choix en français » ([Hack'celeration](https://hackceleration.com/fr/labs/meilleur/logiciel-gestion-eglise)).

---

### Taille du marché (sources)

| Chiffre | Source | Statut |
|---|---|---|
| **745 000** protestants évangéliques pratiquants réguliers ; **« au moins 2 700 lieux de culte évangélique en France »** ; 45 unions ou dénominations dont 33 membres du CNEF ; « 1 Église protestante évangélique pour 25 000 habitants », objectif 1 pour 10 000 | [CNEF, Livret cartographique et statistique 2023](https://jesuspeople.com/wp-content/uploads/2023/05/CNEF_2023_Livret-cartographique-et-statistique.pdf) (copie hébergée par un tiers) | Vérifié (lu dans le PDF) |
| « quelque 2 700 églises et 745 000 pratiquants » ; « estimation basse » ; en 2017 : 2 521 églises et 650 000 pratiquants ; le CNEF « affirme représenter plus de 70 % des protestants évangéliques » | [Réforme / AFP, 7 juin 2022](https://www.reforme.net/societe/le-cnef-revendique-2-700-eglises-et-745-000-pratiquants-en-france/) | Vérifié |
| **1 370 000 Français protestants, soit 2 % de la population** ; FPF : 26 unions d'Églises, 7 Églises associées, 12 communautés, « près de 500 communautés, œuvres et mouvements » | [Présentation FPF (PDF, 2025)](https://www.protestants.org/wp-content/uploads/2025/07/Presentation-FPF.pdf) | Vérifié |
| EPUdF : « plus de 480 paroisses ou Églises locales », « 1 100 lieux de culte » | [Brochure EPUdF](https://acteurs.epudf.org/wp-content/uploads/sites/2/2023/05/epudf_brochure_francaise-999998.pdf) | **Non vérifié** (extrait de résultat de recherche, PDF non lu) |
| « 2 530 églises évangéliques et 745 000 pratiquants » (2025) | [Wikipédia FR, CNEF](https://fr.wikipedia.org/wiki/Conseil_national_des_%C3%A9vang%C3%A9liques_de_France) | **Non vérifié**, diffère du chiffre CNEF 2023 |
| « environ 750 000 fidèles », « le nombre de communautés double environ tous les quinze ans » | RCF, sept. 2025 (page non lisible : « JavaScript is required ») | **Non vérifié** |
| « La France compte plus de 45 000 lieux de culte chrétiens » ; « plus de 40 000 paroisses » catholiques | [Church Manager, page France](https://churchmanager.fr/pays/france) | **Non vérifié**, affirmation commerciale |

Ordre de grandeur utile pour `idea.md` : **≈ 2 700 lieux de culte évangéliques** (CNEF 2023) + les paroisses luthéro-réformées (EPUdF ≈ 480, non vérifié) forment le marché adressable brut ; la cible « 50 à 300 membres, sans secrétaire salariée » en est un sous-ensemble que aucune source publique ne chiffre directement. À 39 € HT/mois, 1 % des lieux de culte évangéliques (27 églises) représenterait ≈ 12 600 € HT/an de revenu récurrent.

---

### Méthode et traçabilité

- Recherches en français et en anglais (« logiciel gestion église », « application église communication membres », noms connus) ; pages éditeurs lues : Eliakim, Church Manager, ChMeetings (EN et FR), ChurchTools (EUR et USD), Enoria, ChurchDesk, Text In Church, Planning Center, Breeze, B1.church, EgliseApp, Brevo, smsmode, Octopush, Meta (WhatsApp pricing) ; fiches tierces : Église Numérique (Eliakim, Ecclo), Hack'celeration (classement 2026), Capterra (5 pages d'avis), App Store FR, Le Pèlerin, Réforme, Regards protestants, CNEF 2023, FPF 2025.
- Prix relevés dans la devise affichée, sans conversion sauf mention. Les prix Ecclo et Elvanto proviennent de fiches tierces (non vérifiés sur le site éditeur).
- Non joignables dans cette session : `logiciels.pro`, `appvizer.fr`, `lecnef.org`, `capterra.fr` (lus via récupération tierce ou remplacés par capterra.com), `business.whatsapp.com` (non pris en charge), `churchdesk.com/fr` (404).

## The buyer panel

**2 buy · 18 pass** (10% buy) out of 20 simulated buyers. Seed 7, so the same cards can be dealt again.

These are simulated buyers, not customers. Use this to find objections and weak spots, then confirm the big ones with real people before you spend.

### By segment

| group | buyers | buy rate |
| --- | ---: | ---: |
| Pasteur d'une église de 200 à 300 membres avec un conseil et des responsables bénévoles (budget annuel ≈ 150 000 à 300 000 €) | 5 | 20%  (thin) |
| Pasteur à plein temps d'une église de 100 à 200 membres (budget annuel ≈ 60 000 à 150 000 €, un seul salarié : lui) | 7 | 14%  (thin) |
| Pasteur bi-vocationnel d'une église de 50 à 100 membres (budget annuel de l'église ≈ 30 000 à 60 000 €, pas de salarié) | 8 | 0% |

### By buying behaviour

| group | buyers | buy rate |
| --- | ---: | ---: |
| Curieux de l'IA | 2 | 100%  (thin) |
| Prudent avec l'argent de l'église | 4 | 0%  (thin) |
| Méfiant de l'IA | 3 | 0%  (thin) |
| Délègue à un bénévole | 3 | 0%  (thin) |
| Tout sur WhatsApp | 5 | 0%  (thin) |
| Suit les recommandations de pairs | 3 | 0%  (thin) |

### By income

| group | buyers | buy rate |
| --- | ---: | ---: |
| $29,000 to $35,000 | 8 | 25% |
| $35,000 and up | 7 | 0%  (thin) |
| under $29,000 | 5 | 0%  (thin) |

### Why they pass

| reason | buyers | in their words |
| --- | ---: | --- |
| trust | 9 | "Je regarderais la démo et peut-être le mois gratuit, mais je ne mettrais pas 46,80 € par mois de l'argent de l'église dans un outil où je dois importer tous mes membres depuis WhatsApp sans savoir où sont hébergées les données ni qui en est responsable. Aujourd'hui le groupe WhatsApp et mon tableur font le travail gratuitement, et le conseil me demandera pourquoi payer 560 € par an pour ça." (P001) · "Le suivi des absents me parle, parce que j'ai perdu trois familles sans m'en rendre compte, mais je ne vais pas mettre les noms, numéros et absences de mes membres dans un outil en ligne que je ne connais pas, sur la foi d'une page. Pour l'instant on garde le groupe WhatsApp et notre bénévole." (P002) |
| habit | 7 | "On a déjà un groupe WhatsApp et un jeune de l'église qui fait les affiches et les envois : ça marche, ça ne coûte rien, et je n'ai pas envie de toucher à un outil de plus. 46,80 € par mois, c'est presque 600 € par an sur un budget où chaque ligne est discutée au conseil." (P003) · "Je fais déjà tout ça avec le groupe WhatsApp et mon tableur, ça marche et ça ne coûte rien. Je ne vais pas aller devant le conseil défendre 47 € par mois, soit plus de 560 € par an, pour un outil qui fait ce que je fais déjà gratuitement, même si je reconnais que le suivi des absents et les anniversaires me passent souvent à travers." (P004) |
| need | 1 | "Nous sommes 70 à peu près, tout le monde est dans le groupe WhatsApp, et le rappel du culte je l'écris en trois minutes le samedi soir. Payer 46,80 € chaque mois sur l'argent de l'église pour qu'une machine prépare ce que j'écris déjà moi-même, le conseil ne comprendrait pas et moi non plus." (P016) |
| price | 1 | "46,80 € par mois, ça fait plus de 560 € par an pris sur un budget d'église qui tient déjà à peine, pour faire ce que je fais déjà gratuitement avec mon groupe WhatsApp et mes pouces. Je testerais peut-être le mois gratuit par curiosité, mais je ne vois pas le conseil voter cette dépense." (P017) |

### Why they buy

| reason | buyers | in their words |
| --- | ---: | --- |
| convenience | 2 | "Je rédige déjà mes annonces avec une IA, donc ce qui m'intéresse ici ce n'est pas la rédaction, c'est l'import de mes 140 contacts en vrac, les rappels préparés d'avance et le fait que rien ne parte sans que j'appuie sur valider. Premier mois gratuit, sans engagement, 39 € HT sur un budget d'église de 150 000 € : je l'essaie sur la démo puis sur ma vraie liste, et si le conseil ne hurle pas, je garde." (P007) · "Je passe déjà mes samedis soirs à rédiger le rappel du culte avec un assistant IA et à relancer les absents un par un sur WhatsApp ; un outil qui prépare tout ça et ne l'envoie qu'après mon OK depuis le téléphone, avec le premier mois gratuit et sans engagement, je l'essaie. Mais 39 € HT par mois sur le budget de l'église, je ne le garderai que si la gestion des consentements est vraiment sérieuse et si les membres ne trouvent pas ça impersonnel." (P015) |

### What would flip a no

- Un document RGPD clair que je puisse poser sur la table du conseil (hébergement en France ou en UE, contrat de sous-traitance, consentement recueilli par l'outil auprès de chaque membre), avec le témoignage d'une autre église française qui l'utilise déjà.
- Un pasteur que je connais qui l'utilise depuis six mois et me le recommande, plus un engagement écrit et clair : données hébergées en France ou en Europe, jamais revendues ni utilisées pour entraîner une IA, et exportables/supprimables en un clic si on arrête.
- Que mon bénévole essaie le mois gratuit lui-même, me dise que ça lui fait gagner du temps, et qu'on ait un plafond SMS fixe (ou un forfait tout compris) pour que je puisse annoncer un chiffre au conseil.
- Qu'un pasteur d'une église que je connais, de même taille, me dise qu'il l'utilise depuis un an, que son conseil l'a validé et que ça lui fait gagner plusieurs heures par semaine.
- Que la bénévole qui gère la communication arrête, ou qu'un pasteur d'une église que je connais m'en parle lui-même et me montre que ça lui fait vraiment gagner du temps chaque semaine.
- Un engagement écrit, noir sur blanc, d'hébergement en France avec conformité RGPD et suppression des données à la résiliation, que je puisse mettre sur la table du conseil ; et même là, 46,80 € par mois pour une église de notre taille, il faudrait un tarif petites églises autour de 15 € pour que le conseil dise oui.
- Un prix tout compris avec les SMS plafonnés et clairement annoncés, autour de 20 € par mois, et que mon bénévole puisse tout piloter à ma place avec juste un oui de ma part. Le suivi des absents, par contre, j'en aurais eu besoin avant de perdre trois familles.
- Une garantie RGPD claire (hébergement en France ou UE, modèle de consentement à faire signer aux membres, contrat de sous-traitance) et le témoignage d'une autre église évangélique française de ma taille qui l'utilise déjà.
- Qu'un pasteur de mon union ou de mon réseau l'utilise depuis quelques mois et me dise de lui-même que ça lui fait gagner du temps et que ses membres suivent mieux.
- Qu'un pasteur que je connais, d'une église de notre taille, me montre sur son propre téléphone qu'il l'utilise depuis six mois et que ses membres ont bien reçu les messages, le jour où mon bénévole arrête.
- Qu'un pasteur de mon union que je connais l'utilise depuis quelques mois et me dise que ça lui a vraiment permis de repérer les absents avant qu'il ne soit trop tard.
- Une garantie claire et écrite : données hébergées en France ou en Europe, conformité RGPD avec un contrat que je peux montrer au conseil, suppression et export possibles à tout moment, et un autre pasteur que je connais qui l'utilise déjà et me dit que ses membres n'ont rien vu d'étrange.

Buyers say they would buy **1.0 times** in the first month on average.

20 buyers gave all four price answers. Run founder-pricing's van_westendorp.py on the answers folder.

## Pricing

Trois sources, toutes vérifiables : ce que les acheteurs simulés ont dit (`founder/pricing-curve.md`, 20 réponses complètes), ce que les concurrents facturent (`founder/competitors.md`), ce que l'entreprise doit gagner (`founder/numbers.json`, outil du CFO).

### 1. Le prix recommandé, et pourquoi

**Abandon du prix unique de 39 € HT. Trois formules par taille d'église : 19 € HT, 29 € HT, 49 € HT par mois, tout compris, sans facturation SMS surprise.**

#### Ce que les acheteurs ont dit (pitch v1, prix unique 39 € HT = 46,80 € TTC)

| Point | Prix | Sens |
|---|---|---|
| PMC | 5,20 € | en dessous, trop bon marché pour être sérieux |
| OPP | 5,20 € | moindre résistance |
| IPP | 15,10 € | autant disent « bonne affaire » que « cher » |
| PME | 38,97 € | au-dessus, trop de refus |

Fourchette acceptable : **5,20 € à 38,97 €**. Médianes : trop bon marché 5 €, bonne affaire 12 €, commence à être cher 25 €, trop cher 40 €. **Le prix de 39 € est au-dessus de la fourchette.** Treize pasteurs sur vingt ont un seuil de refus inférieur ou égal à 40 €.

La fourchette cache deux populations, lisibles dans les réponses individuelles (`founder/panel/answers/`) :

| Segment | « commence à être cher » | « je n'achète pas » |
|---|---|---|
| Petites assemblées, 50 à 100 membres (8 pasteurs, 0 % d'achat) | 20 à 25 € | 30 à 40 € |
| Assemblées, 100 à 200 membres (7 pasteurs) | 25 à 30 € | 40 à 45 € |
| Grandes assemblées, 200 à 300 membres (5 pasteurs) | 45 à 60 € | 70 à 90 € |

Les pasteurs raisonnent en TTC (une association cultuelle ne récupère pas la TVA) et en coût annuel (« 560 € par an devant le conseil »). Un prix unique ne peut pas servir les trois : 39 € est trop cher pour les petites et laisse de l'argent sur la table chez les grandes.

#### Ce que les concurrents facturent (pour ~200 membres, par mois)

Offres en euros pour une église locale : **plus bas 29 €** (Ecclo ; Eliakim jusqu'à 50 utilisateurs), **médiane 50 €** (Church Manager, Enoria), **plus haut 59 €** (Eliakim Croissance). ChurchTools 54 €. En dollars : ChMeetings 25 $ (≤ 250 personnes), Text In Church 30 $ (1 250 SMS inclus). Gratuits : B1.church, Planning Center People, le groupe WhatsApp. Les expéditeurs SMS grossistes (smsmode, Octopush) sont à 9 €/mois + 0,045 € par SMS. Détail et liens : `founder/competitors.md`, section 2.

Lecture : le marché euro des logiciels d'église se situe entre 29 € et 59 €, mais ces outils vendent d'abord une base de membres avec dons et reçus fiscaux. Bureau du Pasteur vend la communication validée et le suivi ; il se compare, pour le pasteur, au groupe WhatsApp gratuit et à Ecclo à 29 €, pas à Eliakim à 59 €.

#### Ce que l'entreprise doit gagner (outil du CFO, `numbers.json`)

| Prix moyen testé | Contribution par église-mois | Seuil de rentabilité (églises) | Marge au plan (60 églises) |
|---|---|---|---|
| 19 € (v1, coûts v1) | 9,76 € | 32 | 25 % |
| 25 € | 15,76 € | 20 | 43 % |
| 29 € | 19,76 € | 16 | 51 % |
| 39 € (hypothèse de départ) | 29,76 € | 11 | 63 % |
| **30 € (moyenne pondérée des trois formules, coûts v2 avec WhatsApp inclus)** | **17,71 €** | **18** | **42 %** |

À 30 € de prix moyen, le seuil de rentabilité est 18 églises abonnées et la marge au plan 42 % (`founder/cfo.md`). Le coût qui pèse est le forfait WhatsApp inclus (9,74 € en moyenne si le forfait est entièrement consommé) : c'est le prix de la promesse « un seul chiffre pour le conseil ». Sans lui, la facture variable revient et avec elle l'objection n° 6 du panel.

### 2. L'échelle

| Formule | Taille | HT / mois | TTC / mois | Inclus | Pourquoi monter d'un cran |
|---|---|---|---|---|---|
| **Petite assemblée** | jusqu'à 100 membres | **19 €** | 22,80 € | 100 messages WhatsApp, e-mail illimité, partage dans votre groupe WhatsApp, suivi des absents, rappels préparés | — |
| **Assemblée** | 101 à 200 membres | **29 €** | 34,80 € | 300 messages WhatsApp + tout ce qui précède | Plus de membres = plus de messages inclus ; même prix que l'entrée de gamme concurrente (Ecclo) |
| **Grande assemblée** | 201 à 300 membres | **49 €** | 58,80 € | 600 messages WhatsApp, plusieurs responsables (rôle secrétaire pour les bénévoles), double validation | Sous la médiane concurrente (50 à 59 €) avec une promesse qu'aucun concurrent ne fait |

SMS en option, au coût réel (0,08 € l'unité, arrondi au-dessus du tarif Twilio de 0,0798 $), sous un **plafond mensuel fixé par l'église** (0 € par défaut). Au-delà du forfait WhatsApp, rien ne part sans accord explicite : le chiffre annoncé au conseil est le chiffre payé.

Paiement annuel : deux mois offerts (soit 190 €, 290 €, 490 € HT par an). Les associations préfèrent une ligne budgétaire annuelle votée une fois.

Position de chaque formule dans la fourchette du panel : 22,80 € TTC est au niveau « commence à être cher » des petites assemblées (20 à 25 €), sous leur refus (30 à 40 €). 34,80 € TTC est au niveau « cher mais possible » des assemblées moyennes (25 à 30 €... à 40). 58,80 € TTC est dans la zone « cher mais possible » des grandes (45 à 60 €), sous leur refus (70 à 90 €). Aucune formule n'est au-dessus du seuil de refus de son segment ; aucune n'est en dessous du PMC.

### 3. L'offre d'ouverture

**Les 10 églises fondatrices** : moitié prix à vie (9,50 €, 14,50 €, 24,50 € HT) pour les dix premières églises, en échange d'un appel de retour mensuel de 20 minutes et, si elles le souhaitent, d'un témoignage nommé. Fermeture quand la dixième est installée, pas de date artificielle. Ce n'est pas une remise qui apprend à attendre les soldes : c'est le prix d'un travail (les retours) que personne d'autre ne fournira, et il ne reviendra pas.

Pas de « premier mois gratuit » : le panel v1 l'a ignoré (deux acheteurs sur vingt l'ont cité, dix-huit non) et il attire des essais sans intention. À la place, **satisfait ou remboursé 60 jours**, qui répond à la peur (« et si ça ne marche pas ») sans dévaloriser le prix.

### 4. Ce qu'il faut tester avec de vrais pasteurs

1. **19 € contre 25 € HT pour la Petite assemblée**, sur deux pages d'inscription identiques présentées en alternance aux pasteurs rencontrés dans les rassemblements d'unions (20 pasteurs chacune). Mesure : part qui demande le dossier pour le conseil, part qui s'inscrit sous 30 jours.
2. **49 € contre 39 € HT pour la Grande assemblée**, même méthode. Le panel laisse penser que 49 € passe ; le conseil (lentille Offres) demande si 79 € passerait : tester 49 € d'abord, 69 € si la Grande assemblée convertit au-dessus de 20 %.
3. **Paiement annuel avec deux mois offerts** proposé ou non à l'inscription : mesure la part qui choisit l'annuel (objectif : plus de la moitié, pour la trésorerie).

Critère de décision écrit avant le test : si moins de 3 pasteurs sur 20 s'inscrivent à 19 €, le problème n'est pas le prix mais la confiance (voir `founder/offer.md`) et c'est le programme des fondatrices qui doit passer en premier.

### 5. Les objections de prix, mot pour mot (panel v1)

1. « 46,80 € par mois, c'est presque 600 € par an sur un budget où chaque ligne est discutée au conseil. » (P003)
2. « Je ne vais pas aller devant le conseil défendre 47 € par mois, soit plus de 560 € par an, pour un outil qui fait ce que je fais déjà gratuitement. » (P004)
3. « Il faudrait un tarif petites églises autour de 15 € pour que le conseil dise oui. » (P006) ; « Un prix tout compris avec les SMS plafonnés et clairement annoncés, autour de 20 € par mois. » (P008)

Le marketing doit répondre aux trois : le coût annuel dit en clair (190 € HT par an pour une petite assemblée), ce que le conseil obtient en échange (le dossier RGPD, les absents retrouvés), et « un seul chiffre, jamais dépassé ».

### Règles

- Les réponses de prix viennent d'acheteurs simulés ; elles désignent ce qu'il faut tester, pas une preuve. Les tests du point 4 tranchent.
- Aucune formule n'est vendue sous son coût variable : la contribution la plus faible (Petite assemblée, forfait WhatsApp entièrement consommé) reste positive (19 € − 4,84 € = 14,16 € HT).
- Aucun faux prix barré : 39 € n'a jamais été facturé et n'apparaîtra nulle part comme « ancien prix ».
- TVA : prix HT, TVA 20 % en sus ; la plupart des églises la paient sans la récupérer, d'où les prix TTC affichés à côté. Un expert-comptable confirme le régime.

`founder/numbers.json` a été mis à jour avec le prix moyen pondéré de 30 € HT et les coûts des forfaits WhatsApp ; `/founder-cfo` est relancé dans `founder/cfo.md`.

## The offer

Méthode : la lentille Offres (`.claude/skills/founder-board/lenses.md`), résumé d'un cadre publié, appliqué par nous. Matière première : `founder/panel/results.md` (2 achètent, 18 passent), `founder/board.md` (conditions C1 à C10), `founder/numbers.json`, `founder/pricing-curve.md` (fourchette acceptable 5,20 € à 38,97 € ; 39 € est au-dessus).

### 1. Ce que les acheteurs ont dit, en une ligne

Le prix n'est pas la première raison de refus : **9 refus sur 18 sont « confiance »** (où vont les données de mes membres, qui est derrière, aucun pasteur que je connais ne l'utilise), **7 sont « habitude »** (WhatsApp et un bénévole font déjà le travail gratuitement). Le prix arrive derrière, mais il bloque quand même : 39 € HT (46,80 € TTC) est au-dessus du seuil « je n'achète pas » de 13 pasteurs sur 20, et les petites églises (0 % d'achat) ont un plafond de 30 à 40 € TTC. La facture SMS « au coût réel » est citée 5 fois : le pasteur veut **un seul chiffre à annoncer au conseil**.

### 2. La liste des problèmes (dans les mots des acheteurs)

#### Avant d'acheter
1. « Où sont hébergées les données de mes membres, qui y a accès ? » (P001, P002, P006, P009, P013, P014, P019)
2. « La moitié de mes membres n'ont jamais signé de consentement ; le risque RGPD retombe sur moi. » (P001, P009, P015)
3. « Aucun pasteur de mon union ne l'utilise. » (P010, P012, P014, P016, P020)
4. « Qui est derrière ce produit ? Existera-t-il encore l'an prochain ? » (P004, P011, P016)
5. « 560 € par an à défendre devant le conseil alors que WhatsApp est gratuit. » (P003, P004, P005, P010, P017)
6. « Les SMS au coût réel : je ne peux pas annoncer un chiffre au conseil. » (P003, P008, P012, P018)
7. « Trop cher pour une église de notre taille ; il faudrait un tarif petites églises. » (P006, P008, P019, P017)
8. « Une machine écrit à mes membres à ma place ; c'est impersonnel. » (P013, P019, P020, P015)
9. « Pas le temps d'importer et de nettoyer 140 contacts à moitié sans nom. » (P005, P011, P016)
10. « C'est mon bénévole qui fait la communication ; moi je ne touche pas aux outils, et là tout repasse par mon téléphone. » (P008, P018, P005)

#### Pendant
11. L'import d'un groupe WhatsApp donne des « Contact » sans nom à corriger un par un. (P011)
12. Recueillir le consentement de 150 personnes. (P009)
13. Les membres âgés ne liront pas un SMS venu d'un logiciel plutôt que du pasteur. (P017)
14. « Le suivi des absents suppose que quelqu'un note les présences chaque dimanche ; personne ne le fait. » (P007)
15. Apprendre un outil de plus avec 35 heures de travail à côté. (P005, P016)
16. Créer un compte Twilio, un SMTP, une clé API (conseil, lentille Produit).

#### Après
17. « Qui nous aide si ça ne marche pas un dimanche à 8 h ? » (P016, objection de départ de 3 cartes)
18. « Que deviennent les données si on arrête ? » (P002, P006, P007, P013)
19. « Le ton n'est pas le mien. » (P020)
20. « Les données servent-elles à entraîner une IA, sont-elles revendues ? » (P002, P013, P019)
21. « Le jour où je valide sans relire, la machine parle pour moi. » (P020)
22. Une facture qui varie d'un mois à l'autre. (P003, P018)

### 3. Les solutions, notées et triées

Valeur pour l'acheteur (1-5) et coût de livraison (1-5, d'après `founder/numbers.json` et le temps du fondateur).

| # | Solution | Répond à | Valeur | Coût | Gardée ? |
|---|---|---|---|---|---|
| S1 | **Le dossier pour le conseil** : 2 pages à imprimer. Hébergement en France (Scaleway, Paris), contrat de sous-traitance RGPD (DPA) signé, aucune donnée utilisée pour entraîner une IA ni revendue, export et suppression en un clic, l'IA ne voit jamais la liste des membres. | 1, 4, 18, 20 | 5 | 1 | Oui |
| S2 | **Consentements recueillis par l'outil** : message « Répondez OUI pour recevoir les nouvelles de l'église », formulaire en ligne et modèle papier ; consentement daté sur la fiche. Rien n'est envoyé aux non-consentants. | 2, 12 | 5 | 2 (petit développement) | Oui |
| S3 | **Prix tout compris par taille d'église**, un seul chiffre, messages WhatsApp inclus, e-mail illimité ; au-delà du forfait, rien ne part sans accord (plafond fixé par l'église, 0 € par défaut). SMS en option au coût réel sous le même plafond. | 5, 6, 7, 22 | 5 | 2 (facturation) | Oui |
| S4 | **Partage dans votre groupe WhatsApp** : l'outil prépare le message, le pasteur le partage dans son groupe existant, gratuit. Zéro coût d'API, ton préservé. | 5, 8, 13 | 4 | 1 | Oui |
| S5 | **Installation faite avec vous** : 30 minutes en visio, le fondateur importe le répertoire, nettoie les doublons, lance la demande de consentement. | 9, 11, 15 | 5 | 3 (temps du fondateur) | Oui, pour les 50 premières églises |
| S6 | **Le bénévole prépare, le pasteur valide d'un geste** : rôle secrétaire (existe déjà), le pasteur ne reçoit qu'un SMS Valider / Modifier / Annuler. | 10, 15 | 4 | 1 | Oui (à expliquer) |
| S7 | **Dans vos mots** : l'IA apprend le style du pasteur sur trois de ses anciens messages ; l'expéditeur affiché est le nom de l'église ou du pasteur ; tout est modifiable avant validation. | 8, 13, 19, 21 | 4 | 2 | Oui |
| S8 | **Assistance du dimanche matin** : un numéro WhatsApp/téléphone répondu de 7 h à 13 h le dimanche. | 17 | 4 | 3 (temps du fondateur) | Oui |
| S9 | **Présences en 10 secondes** : le dimanche, une liste à cocher sur le téléphone, ou « qui manquait ? » par groupe ; l'alerte d'absence prolongée en découle. | 14 | 3 | 2 | Oui |
| S10 | **Garantie « rien ne part sans vous »** : si un message collectif part sans validation du pasteur, un an d'abonnement offert. Adossée aux tests `test_approval_invariant.py`. | 8, 21 | 5 | 1 | Oui |
| S11 | **Satisfait ou remboursé 60 jours**, sans question. | 5, 7 | 4 | 1 (voir coût ci-dessous) | Oui |
| S12 | **Programme des 10 églises fondatrices** : moitié prix à vie contre un appel mensuel de retour et, si elles le souhaitent, un témoignage nommé. Fabrique la preuve par les pairs qui manque. | 3, 4 | 4 | 2 (remise) | Oui, lancement seulement |
| S13 | Page « Qui est derrière » : nom, visage, église d'attache et parcours du fondateur. | 4 | 3 | 1 | Oui |
| S14 | Fournir le numéro d'envoi et les canaux : aucun compte Twilio, SMTP ou clé API à créer par le pasteur. | 16 | 4 | 2 | Oui (déjà exigé par le conseil, C8) |
| S15 | Application mobile native | 15 | 3 | 5 | **Non** : la page mobile de validation suffit au lancement |
| S16 | Plus d'agents, plus de styles | — | 1 | 3 | **Non** : le conseil demande de retirer, pas d'ajouter (C6) |

### 4. La pile

**Le nom de l'offre : « Formule Église sereine »** (l'abonnement) et **« Les 10 églises fondatrices »** (l'offre de lancement).

**Le cœur, décrit par le résultat** : chaque dimanche, vos membres ont reçu le rappel dans vos mots, les absents de plus de trois semaines ont un nom sur votre téléphone, et rien n'est parti sans votre pouce.

**Les bonus (chacun tue une objection)**
- Le dossier pour le conseil (S1) : tue « où sont mes données / qui est derrière ».
- L'installation faite avec vous en 30 minutes et le consentement recueilli par l'outil (S5 + S2) : tue « je n'ai pas le temps / mes membres n'ont pas consenti ».
- L'assistance du dimanche matin (S8) : tue « qui m'aide à 8 h ».

**La garantie** : satisfait ou remboursé 60 jours (S11), et un an offert si un seul message collectif part sans validation (S10).

Coût de la garantie, chiffré avec l'outil du CFO : à un taux de remboursement réaliste de 10 % des nouveaux abonnés sur les deux premiers mois, le coût est de 2 mois × prix moyen 30 € × 10 % = **6 € par nouvelle église**, soit moins d'un mois de contribution (18,20 € en moyenne, voir `founder/cfo.md`). La garantie S10 ne coûte que si l'invariant du code est violé ; sa probabilité est celle d'un bug sur le chemin le plus testé du produit.

**Urgence et rareté, vraies** : le programme des 10 églises fondatrices est limité à dix parce que le fondateur fait lui-même chaque installation et chaque appel mensuel ; il ferme quand la dixième église est installée. Pas de compte à rebours.

**Le prix** (détail et raisons dans `founder/pricing.md`) :

| Formule | Taille | Prix HT / mois | TTC | Inclus |
|---|---|---|---|---|
| Petite assemblée | jusqu'à 100 membres | 19 € | 22,80 € | 100 messages WhatsApp, e-mail illimité, partage groupe WhatsApp |
| Assemblée | 101 à 200 membres | 29 € | 34,80 € | 300 messages WhatsApp, idem |
| Grande assemblée | 201 à 300 membres | 49 € | 58,80 € | 600 messages WhatsApp, idem |

SMS en option, au coût réel (0,08 € l'unité), sous un plafond mensuel que l'église fixe. Au-delà du forfait, rien ne part sans accord.

### 5. L'équation de valeur, avant et après (1 à 10)

| Élément | Avant (pitch v1) | Après (pitch v2) | Ce qui a bougé |
|---|---|---|---|
| Résultat rêvé | 6 | 7 | Le cœur est dit par le résultat (absents nommés, rappel dans mes mots) et non par les fonctions |
| Probabilité perçue d'y arriver | 3 | 6 | Dossier pour le conseil (S1), garanties (S10, S11), fondateur nommé (S13), églises fondatrices (S12) |
| Délai jusqu'au résultat | 5 | 7 | Installation en 30 minutes faite avec vous (S5) |
| Effort et sacrifice | 3 | 7 | Consentements recueillis par l'outil (S2), bénévole qui prépare (S6), un seul chiffre pour le conseil (S3), rien à configurer (S14) |

La probabilité perçue reste le point faible : seule une liste d'églises nommées la fera monter au-delà de 6. C'est le rôle du programme des fondatrices et de `/founder-launch`.

### 6. Ce qu'il faut construire avant de vendre l'offre

- S2 : demande de consentement par message et formulaire (petit développement sur le moteur de campagnes existant).
- S3 : forfaits par taille, compteur de messages, plafond par église (facturation Stripe).
- S4 : bouton « partager dans mon groupe WhatsApp » (texte prêt à coller).
- S7 : expéditeur au nom de l'église ; apprentissage du style sur trois anciens messages.
- S9 : présences en un geste.
- S1, S13 : deux documents à rédiger avec le juriste (voir `founder/cfo-sources.md`, poste « avis juridique »).

### 7. Le nouveau test

Le pitch v2 (`founder/pitch.md`, l'ancien est `founder/pitch-v1.md`) est présenté aux **mêmes 20 pasteurs** (graine 7) dans `founder/panel-v2/`. Résultat avant : 2 achètent, 18 passent (10 %). Résultat après : voir la section « Re-test » ci-dessous, ajoutée une fois le panel v2 compté.


### Re-test : pitch v2 devant les mêmes 20 pasteurs (`founder/panel-v2/results.md`)

**Avant : 2 achètent, 18 passent (10 %). Après : 2 achètent, 18 passent (10 %).** Les deux acheteurs sont les mêmes (P007 et P015, les deux pasteurs « curieux de l'IA » d'églises de plus de 150 membres). **Le taux d'achat n'a pas bougé. Il faut le dire tel quel : le problème n'est pas d'abord l'offre, c'est le segment.**

Ce qui a bougé sous la surface :

| Raison du refus | v1 | v2 | Lecture |
|---|---|---|---|
| Confiance (données, qui est derrière) | 9 | 6 | Le dossier pour le conseil et l'hébergement en France ont été lus et crus « sur le papier » ; il reste « je ne connais pas l'entreprise » et « aucun pasteur que je connais ne l'utilise », que seule une liste d'églises nommées lève. |
| Habitude (WhatsApp gratuit + bénévole) | 7 | 7 | Inchangé. Le groupe WhatsApp gratuit est le vrai concurrent. |
| Besoin (« je connais mes 70 membres de vue ») | 1 | 5 | **Nouveau.** En nommant le résultat (« les absents de plus de trois semaines ont un nom »), l'offre a révélé que les petites assemblées n'ont pas ce problème : le pasteur voit les bancs. |
| Prix | 1 | 1 | Le prix a cessé d'être l'objection principale ; les formules sont dans la fourchette (PME 40,01 € sur v2). |

Objections nouvelles, à prendre au sérieux :
1. **« Qui pointe les présences chaque dimanche ? »** (P002, P003, P008, P015) : la promesse des absents suppose une saisie que personne ne fait. La solution S9 (présences en un geste) doit être montrée, pas sous-entendue, et le mot « absents » doit être remplacé par ce que l'outil fait vraiment : « les personnes qu'on n'a pas vues ».
2. **« La demande de consentement envoyée par l'outil, c'est une machine qui écrit à mes membres avant moi »** (P007, P002, P016, P001) : la demande de consentement doit partir du numéro ou du nom du pasteur, dans ses mots, et pouvoir être faite en chaire + papier pour les aînés.
3. **« Dans vos mots » a sonné faux** (P013, P019, P020) : si une IA rédige, le pasteur l'entend. Le pitch doit dire la vérité simplement : « vous écrivez ou vous relisez ; l'outil n'invente rien et n'envoie rien ».
4. **« Deux mois pour le conseil, sans carte bancaire »** (P001, P009, P020) : la décision est collective ; l'essai doit pouvoir être présenté au conseil avant tout paiement.

Conséquences pour la suite du dossier :
- **Segment** : la première cible n'est pas l'église de 50 à 100 membres (0 % d'achat deux fois, 8 cartes sur 20) mais le pasteur d'une assemblée de **150 à 300 membres**, déjà utilisateur d'un assistant IA, qui ne connaît plus tous les visages. `/founder-marketing` doit partir de là.
- **Pitch v3 (à tester avec de vrais pasteurs)** : retirer « dans vos mots », expliquer la présence en un geste, consentement au nom du pasteur, « essai de deux mois présentable au conseil, sans carte ». Non testé ici : le panel simulé a donné ce qu'il pouvait, le reste se mesure avec dix pasteurs réels (`founder/launch.md`).
- **Prix** : les formules tiennent (aucune objection de prix nouvelle hors P004 sur la Grande assemblée à 49 €). Le test 49 € contre 39 € de `founder/pricing.md` reste nécessaire.

Rappel : acheteurs simulés, taux d'achat à lire comme un plafond, aucune de ces phrases n'est un témoignage.

### Règles respectées

Aucun témoignage, aucun avis, aucune rareté ou remise inventés. Les promesses (hébergement en France, DPA, remboursement, assistance du dimanche, installation en visio) sont livrables par un fondateur seul jusqu'à environ 50 églises ; au-delà, S5 et S8 doivent être réévaluées. Les règles françaises sur les garanties et la publicité s'appliquent ; ceci n'est pas un avis juridique.

## The numbers

Tous les chiffres viennent de `founder/numbers.json` (v3 : trois formules, prix moyen pondéré 30 € HT, coûts corrigés par `founder/ops.md`) passés dans `unit_economics.py`, ou d'une entrée nommée dans `founder/cfo-sources.md`. Montants en euros HT ; l'outil écrit « $ », lire « € ». Ni conseil financier, ni fiscal, ni juridique : un expert-comptable doit vérifier la structure, les charges sociales et la TVA avant que de l'argent ne circule.

### La marge

- **Contribution par église-mois : 18,17 € sur 30 € (61 %).** Le poste qui pèse est le forfait WhatsApp inclus (9,74 € si le forfait est consommé en entier, catégorie Meta « utility ») : c'est le prix de la promesse « un seul chiffre pour le conseil ».
- **Marge au plan (60 églises) : 43 %** après tous les coûts fixes (322 € par mois, dont 99 € d'expert-comptable et 150 € de marketing, sans rémunération du fondateur). **Seuil de rentabilité : 18 églises abonnées.**

### La ligne à surveiller

**La classification Meta des messages WhatsApp, puis la rémunération du fondateur.** Deux « et si » le prouvent (fichiers de scénario dans le scratchpad de la session, chiffres reproduits ici) :

| Scénario | Contribution | Seuil (églises) | Marge au plan | Résultat an 1 |
|---|---|---|---|---|
| Base (WhatsApp « utility », fondateur non payé) | 18,17 € | 18 | 43 % | −1 080 € |
| Prix −10 % | — | 22 | 36 % | −1 539 € |
| Volume −20 % | — | 18 | 38 % | −1 636 € |
| Coûts unitaires +15 % | — | 20 | 37 % | −1 351 € |
| **WhatsApp classé « marketing » par Meta** (forfait 24,50 € au lieu de 9,74 €) | **3,41 €** | **95, au-dessus de la capacité de 60** | **−7 %** | −3 338 € |
| **Fondateur payé 1 500 €/mois** | 18,17 € | **101, au-dessus de la capacité de 60** | **−41 %** | −19 080 € |

Lecture :
1. **Si Meta classe le rappel du culte en « marketing » (0,0859 $ au lieu de 0,030 $ par message), le modèle meurt** : la contribution tombe à 3,41 € et le seuil à 95 églises, hors de portée d'un fondateur seul. `founder/ops.md` donne la parade : rédiger les gabarits en « utility », tester la classification sur trois gabarits réels avant de vendre, et exprimer le forfait inclus en euros plutôt qu'en messages. C'est la première chose à vérifier, avant tout le reste.
2. **Avec un fondateur payé 1 500 € par mois, il faut 101 églises, au-dessus du plafond de 60 églises** que les promesses de l'offre (installation en visio, assistance du dimanche) permettent à une seule personne de tenir (`founder/ops.md`). Telle qu'elle est chiffrée, c'est une activité d'appoint jusqu'à 60 églises, ou une entreprise à condition d'un prix moyen plus élevé (Grandes assemblées à 49 € ou plus) ou d'un canal qui amène des églises par dizaines (une union) et d'une personne de support.

### La montée en charge, et comment elle a été fixée

Le panel simulé donne 10 % d'achat (2 sur 20, deux fois, les deux chez des pasteurs de plus de 150 membres), à lire comme un plafond. Un fondateur seul qui rencontre 30 pasteurs par mois dans les rassemblements d'unions en convertit au mieux 3 ; la ramp retenue (0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28 églises abonnées en fin de mois) suppose 2 à 3 nouvelles églises par mois et presque aucune résiliation : prudente sur l'acquisition, optimiste sur la résiliation. Les 10 églises fondatrices à moitié prix baissent le prix moyen réel des premiers mois d'environ 15 € par église : l'an 1 réel sera un peu pire que le tableau.

### Trésorerie

**Cash nécessaire avant que l'affaire ne se paie : 5 186 €** (3 685 € de démarrage, dont 1 500 € d'avis juridique RGPD et d'AIPD, plus le creux des six premiers mois). Le démarrage n'est pas remboursé dans l'année 1. Le fondateur doit pouvoir vivre sans salaire de l'activité pendant l'année 1.

### Trois façons d'améliorer la marge (chiffrées avec l'outil)

1. **Vendre d'abord aux assemblées de 150 à 300 membres** (le panel et le marketing le recommandent) : un mix 20 / 40 / 40 % au lieu de 40 / 35 / 25 % porte le prix moyen de 30 € à 35 € HT et la contribution à environ 21,50 € ; le seuil passe de 18 à 15 églises.
2. **Facturer le forfait WhatsApp consommé, pas théorique** : à 60 % de consommation moyenne, la contribution passe de 18,17 € à 22,07 € (+21 %) ; seuil 15 églises. Le compteur de messages est le chiffre à regarder chaque mois.
3. **Paiement annuel (deux mois offerts)** : ne change pas la marge mais avance la trésorerie ; si la moitié des églises paient à l'année, le creux de 5 186 € se réduit d'environ un tiers.

À l'inverse, baisser le prix de 10 % coûte 7 points de marge et 4 églises de seuil : le prix n'est pas le levier.

### Ce que `founder/ops.md` a corrigé dans les chiffres

Prélèvement SEPA au lieu de la carte (0,56 € au lieu de 0,71 €), expert-comptable SASU avec liasse 99 € au lieu de 60 €, outils 20 € au lieu de 40 €, e-mail 0,11 € au lieu de 0,42 €, création de société 195 € au lieu de 300 €, capacité 60 églises au lieu de 100 (goulot de l'assistance du dimanche). Hébergement : Hetzner exclu tant que l'offre promet « hébergé en France » (Scaleway Paris ou OVHcloud). Recommandation reprise : passer le modèle d'IA de `claude-opus-5` à `claude-opus-5-5` (4 $ / 20 $ par million de jetons au lieu de 5 $ / 25 $).

### Les conditions du conseil qui touchent à l'argent

- **C3 (modèle de coûts par église)** : rempli, ci-dessus et dans `founder/cfo-sources.md`.
- **C1 (prix validé par des paiements)** : non rempli, c'est le test de `founder/launch.md`.
- **C8 (le produit fournit les canaux)** : chiffré (numéro mutualisé 1,15 €/mois, WhatsApp inclus) ; les verrous (K-bis pour Twilio et Meta) sont dans `founder/ops.md`.
- **C9 (garantie dont le coût est vérifié)** : provision de 0,50 € par église-mois dans les coûts variables.

---

## Unit economics: Bureau du Pasteur (abonnement SaaS pour églises locales, France)

Every number below comes from the input file. Nothing is looked up or guessed.

### One église-mois

| line | per église-mois |
| --- | ---: |
| Price | 30.00 |
| Frais de paiement : prélèvement SEPA Stripe 0,35 € + Billing 0,7 % [public] | -0.56 |
| API IA, 20 à 40 demandes/mois selon la formule (sonnet pour les petites, opus pour les grandes) [estimation] | -0.62 |
| Messages WhatsApp inclus, forfait utilisé en entier : 100/300/600 à ~0,033 € (Meta utility France + Twilio) [public] | -9.74 |
| E-mails transactionnels [estimation] | -0.11 |
| Hébergement, part variable [estimation] | -0.30 |
| Provision garantie satisfait ou remboursé 60 jours (10 % des nouveaux, lissée) [estimation] | -0.50 |
| SMS : en option, refacturés au coût réel, 0 € de marge [public] | -0.00 |
| **Contribution** (what each église-mois leaves to pay the fixed costs) | **18.17** (61%) |

### The margin that matters

Fixed costs: 322 a month (Serveurs UE (prod + sauvegarde/préprod) et stockage [public] 25, Domaine et certificats [estimation] 2, Outils : e-mail pro, facturation/compta, suivi d'erreurs [estimation] 20, Assurance RC professionnelle [estimation] 25, Expert-comptable en ligne, SASU avec liasse (Indy Sérénité 99 € HT) [public] 99, Numéro Twilio mutualisé [public] 1, Marketing récurrent (déplacements, impression, annonces) [estimation] 150, Rémunération du fondateur : 0 € la première année (hypothèse explicite) [fondateur] 0).

- **Break-even: 18 églises-mois a day.** Below that you lose money every month.
- **Profit margin at your plan** (60 a day): **43%** of every sale, after every cost.
- Capacity: 60 a day.

### Year 1, month by month

| month | églises-mois a day | revenue | profit | cumulative (after 3,685 startup) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | -322 | -4,007 |
| 2 | 2 | 60 | -285 | -4,292 |
| 3 | 4 | 120 | -249 | -4,541 |
| 4 | 6 | 180 | -213 | -4,754 |
| 5 | 8 | 240 | -176 | -4,930 |
| 6 | 10 | 300 | -140 | -5,070 |
| 7 | 13 | 390 | -85 | -5,155 |
| 8 | 16 | 480 | -31 | -5,186 |
| 9 | 19 | 570 | 24 | -5,163 |
| 10 | 22 | 660 | 78 | -5,084 |
| 11 | 25 | 750 | 133 | -4,952 |
| 12 | 28 | 840 | 187 | -4,765 |

- **Year 1 operating profit: -1,080** on 4,590 of revenue.
- After the 3,685 startup spend: -4,765.
- Startup money earned back: not within year 1.
- Cash you need before it pays for itself: **5,186**.

### What if

| scenario | margin at plan | break-even a day | year 1 profit |
| --- | ---: | ---: | ---: |
| Base plan | 43% | 18 | -1,080 |
| Price -10% | 36% | 22 | -1,539 |
| Volume -20% | 38% | 18 | -1,636 |
| Unit costs +15% | 37% | 20 | -1,351 |

### Red flags

- Year 1 loses money on operations (-1,080).
- The startup spend is not earned back within year 1.

## Marketing

Méthode : `.claude/skills/founder-marketing/SKILL.md`. Sources : `founder/panel/results.md` et `founder/panel-v2/results.md` (2 achètent / 18 passent, deux fois, les mêmes acheteurs), `founder/offer.md` (« Re-test »), `founder/competitors.md` (§ 3, § 5, marché), `founder/pricing.md`, `founder/cfo.md` (contribution 17,71 € par église-mois), `founder/board.md` (C4, C6, C10). Acheteurs simulés : hypothèses à vérifier avec dix pasteurs réels, jamais une preuve. Pas un avis juridique.

### 1. Ce que l'évidence dit

**Qui achète.** Deux pasteurs sur vingt, les mêmes sur les deux pitchs : **P007** (assemblée de 200 à 300 membres, « 140 contacts en vrac », rédige déjà avec une IA) et **P015** (pasteur à plein temps, 100 à 200 membres, « ma première peur, c'est le RGPD »). Profil commun : **« curieux de l'IA »** (2 sur 2 ; les cinq autres comportements : 0 sur 18), **plus de 150 membres, à plein temps, un conseil qui vote**. Les églises de 50 à 100 membres : 0 % deux fois sur 8 cartes ; le v2 a dit pourquoi : « avec 70 membres je sais qui manque rien qu'en regardant les bancs » (P005, P006). Le besoin naît quand le pasteur ne connaît plus tous les visages (flip P015 : « que l'église dépasse 150 membres et que je commence à perdre des gens de vue »).

**Objections après le v2, dans l'ordre à traiter.**

| # | Objection (paraphrase) | Qui | Réponse marketing |
|---|---|---|---|
| 1 | Personne que je connais ne l'utilise ; qui est derrière ? | P002, P009, 5 flips « un pasteur de mon union » | Fondateur nommé, visage, église d'attache ; 10 églises fondatrices nommables ; distribution par une union (C4) |
| 2 | WhatsApp est gratuit et fait déjà le rappel | P001, P003, P006 (7 refus « habitude ») | Ne pas vendre le rappel : vendre « les personnes qu'on n'a pas vues », ce que WhatsApp ne fait pas |
| 3 | Qui pointe les présences chaque dimanche ? | P002, P003, P008, P015 | Montrer « présences en dix secondes » (S9), jamais le sous-entendre |
| 4 | La demande de consentement doit venir de moi, pas d'un logiciel | P007, P002, P016, P001 | Elle part au nom du pasteur, dans ses mots, ou en chaire + papier |
| 5 | « Dans vos mots » sonne faux | P013, P019, P020 | Retirer la formule ; dire « vous écrivez ou vous relisez ; l'outil n'invente rien et n'envoie rien » |
| 6 | Deux mois d'essai présentables au conseil, sans carte | P001, P009, P020 | « Essai de 60 jours sans carte, dossier de deux pages joint » (couvert par la garantie S11) |

Le prix n'est plus l'objection principale (1 refus sur 18 au v2) : il ne sera pas le message.

### 2. Positionnement

| | Ligne | Évidence | Verdict |
|---|---|---|---|
| **A (recommandée)** | Pour le pasteur d'une assemblée de 150 à 300 membres, qui rédige déjà ses annonces avec un assistant IA et ne connaît plus tous les visages, Bureau du Pasteur est le secrétariat de communication contrôlé qui prépare le rappel du culte et met un nom sur les personnes qu'on n'a pas vues depuis trois semaines, sans rien envoyer sans son geste, contrairement au groupe WhatsApp gratuit qui envoie tout et ne remarque personne. | P007 et P015 (les deux acheteurs : IA déjà en main, > 150 membres) ; 7 refus « habitude » désignent WhatsApp comme l'alternative réelle ; refus « besoin » des petites assemblées (P005, P006) exclus par le segment | Oui : le segment le plus étroit qui achète, face à l'alternative que le panel cite |
| B | Pour le pasteur qui doit défendre chaque euro et chaque donnée devant son conseil, Bureau du Pasteur est l'outil d'église qui arrive avec le dossier RGPD de deux pages, un seul chiffre par mois et rien d'envoyé sans validation, contrairement aux logiciels de gestion d'église qui vendent une base de membres et automatisent les envois. | P015 (achat « confiance ») ; refus confiance 9 → 6 entre v1 et v2 ; écart § 5 de `competitors.md` | Second message (le dossier) ; parle au conseil, et « prudent avec l'argent » a acheté 0 sur 4 |
| C | Pour le pasteur dont un bénévole prépare la communication, Bureau du Pasteur est l'outil où le bénévole prépare et le pasteur valide d'un geste, contrairement à l'assistant IA grand public qui rédige mais ne sait ni qui est membre ni qui manque. | P007 (v2 : « si un bénévole prépare et que je ne fais que valider ») | Argument, pas cible : « délègue à un bénévole » a acheté 0 sur 3 |

Règle d'écriture : les concurrents ne sont nommés que dans ce dossier, jamais dans les messages (publicité comparative : objective et vérifiable seulement ; on évite). Les mots « absents » et « dans vos mots » disparaissent ; on dit « les personnes qu'on n'a pas vues » et « vous relisez, rien ne part sans vous ».

### 3. Canaux

Tous les canaux ci-dessous existent (vérifiés par recherche le 2026-11-20, liens) ; **aucune taille d'audience n'est avancée**, aucune n'a été mesurée.

| Canal | Pourquoi il colle à l'acheteur | Coût | Comment on sait que ça marche |
|---|---|---|---|
| **1. Rassemblements de pasteurs et unions** : comités départementaux et pastorales du [CNEF](https://www.lecnef.org/page/445853-reseau-departemental), congrès d'unions membres (ex. [FEEBF](https://feebf.com/presentation/), > 110 Églises ; rendez-vous national des [ADD](https://fr.wikipedia.org/wiki/Assembl%C3%A9es_de_Dieu_de_France), dates 2027 à confirmer) | Le pasteur achète sur recommandation d'un pair de son union (12 flips sur 12 au v2) ; il voit le visage du fondateur (objection 1) ; démo sur téléphone en deux minutes | Déplacements + impression : 600 € ; table souvent gratuite pour un membre | Pasteurs de la cible rencontrés, dossiers remis, installations sous 30 jours (objectif : 1 pour 8 conversations) |
| **2. Contact direct des responsables d'unions** (secrétaires généraux, responsables de pastorale) + **groupes WhatsApp de pasteurs** (réseaux existants, entrés par un pasteur membre, jamais par scraping) | C4 et C10 : l'endossement d'une union est la distribution et le fossé ; les groupes WhatsApp sont là où le pasteur lit déjà | 0 € en cash, 2 h par jour de fondateur ; prospection B2B conforme (voir règles § 4) | Rendez-vous obtenus / e-mails envoyés (seuil : 1 sur 10) ; une union qui accepte un pilote de 3 églises |
| **3. Programme des 10 églises fondatrices + parrainage** (`pricing.md` § 3 : moitié prix à vie, appel mensuel, ferme à la dixième installée) | La seule preuve qui lève l'objection 1 : des églises nommées, de même taille, qu'on peut appeler | Remise, pas de cash ; contribution d'une fondatrice ≈ 2,71 €/mois (15 € − 12,29 € de coûts variables) : un investissement en preuve, pas un canal rentable | Fondatrices installées ; part des installations amenées par une fondatrice (objectif : 1 sur 3 après le mois 2) |
| 4. Fiche dans l'annuaire [Église Numérique](https://eglise-numerique.fr/logiciels) | Là où un pasteur qui cherche compare déjà Eliakim et Ecclo | Gratuit a priori (à vérifier) ; 1 h | Visites de la page d'inscription depuis la fiche |
| 5. Médias chrétiens : [Regards protestants](https://regardsprotestants.com/), [Christianisme Aujourd'hui](https://www.christianismeaujourdhui.info/), [Info Chrétienne](https://www.infochretienne.com/), [Réforme](https://www.reforme.net/), [RCF](https://www.rcf.fr/), [Phare FM](https://pharefm.com/) | Crédibilité (objection 1) ; audience surtout de membres | Relations presse gratuites (« IA et secret pastoral ») ; aucun achat d'espace | Une parution reprise dans un groupe de pasteurs |
| 6. Partenariats non concurrents (dons, comptabilité d'église) ; instituts ([IBN](https://www.ibnogent.org/), [FLTE](https://flte.fr/)) | Même acheteur ; pasteurs de demain | 0 € | Plus tard : après 10 églises, horizon > 1 an |
| 7. Google « logiciel église » | Volume faible, comparateurs en place (ChMeetings y est « le meilleur choix en français ») | Payant : non ; une page SEO « qui n'est pas venu depuis trois dimanches » : gratuite | Inscriptions venues de la recherche |
| 8. Publicité sociale payante | Achat de confiance, collectif, non impulsif ; 1 000 € ne forment pas une audience | — | **Non** |

**On démarre avec 1, 2 et 3.** On fait 4 et la page SEO (une heure chacune), on tente la presse (5) sans y compter. **On ne fait pas** la publicité payante : trop chère pour 17,71 € de contribution et contraire à la façon dont ce pasteur achète (par un pair, devant un conseil) ; ni la radio (audience de membres) ; ni les instituts (trop tôt).

### 4. La campagne de 30 jours

Lancement : **dimanche 7 mars 2027**. Avant : préparer la preuve. Après : convertir les conversations en installations. Chaque message répond à une objection du § 1.

| Date | Jour | Canal | Ce qui part |
|---|---|---|---|
| 21/02 | dim. L−14 | Site | Page « Qui est derrière » (S13), page d'inscription, essai 60 jours sans carte. Rien de public. |
| 22/02 | lun. | E-mail | 5 responsables d'unions : objet H4, 20 minutes demandées, dossier RGPD joint. |
| 23/02 | mar. | WhatsApp | Groupes où le fondateur est déjà membre : H1 (qui je suis, ce que je cherche). Pas de lien avant l'accord de l'admin. |
| 24/02 | mer. | Vidéo | Tournage 45 s vertical : présences en dix secondes (objection 3). |
| 25/02 | jeu. | E-mail | Relance personnalisée des unions sans réponse (1 seule relance). |
| 26/02 | ven. | Site / annuaire | Fiche Église Numérique soumise ; page SEO « Qui n'est pas venu depuis trois dimanches ? ». |
| 27/02 | sam. | Visio | 3 démos à des pasteurs « curieux de l'IA » repérés dans les groupes. |
| 28/02 | dim. | Terrain | Culte dans une église de 150 à 300 membres du réseau : observer, pas vendre. |
| 01/03 | lun. | WhatsApp | Coulisses 1 : capture du flux de validation (Valider / Modifier / Annuler) ; objection 5. |
| 02/03 | mar. | E-mail | Pasteurs rencontrés le 27 : dossier + H8. |
| 03/03 | mer. | Impression | Flyer une page (H2 recto, H9 verso), 200 ex. |
| 04/03 | jeu. | WhatsApp | Coulisses 2 : « L'IA ne voit jamais la liste des membres », schéma d'une phrase. |
| 05/03 | ven. | Presse | Pitch à Regards protestants et Christianisme Aujourd'hui : « Une IA au secrétariat, jamais à la place du pasteur ». |
| 06/03 | sam. | Visio | Première installation fondatrice (30 min, S5). |
| **07/03** | **dim. L** | **WhatsApp + site** | Lancement : H10 (fondatrices) + lien d'inscription. Vidéo H3 publiée. Compteur « x/10 installées » réel. |
| 08/03 | lun. | E-mail | Toutes les conversations ouvertes : « ouvert aujourd'hui, 60 jours sans carte, dossier joint ». |
| 09/03 | mar. | WhatsApp | H5 (consentement au nom du pasteur). |
| 10/03 | mer. | Terrain | Pastorale ou comité CNEF départemental (date à caler) : flyers, démos sur téléphone. |
| 11/03 | jeu. | Vidéo | H7 (140 contacts, 30 minutes). |
| 12/03 | ven. | Visio | 2e et 3e installations fondatrices. |
| 13/03 | sam. | WhatsApp | Coulisses 3 : histoire du fondateur (sans témoignage client). |
| 14/03 | dim. | Terrain | Dimanche chez une fondatrice : premier relevé de présences réel ; on note le temps, on ne filme personne. |
| 15/03 | lun. | E-mail | Unions : compte rendu de la semaine (chiffres réels, même petits) + pilote de 3 églises proposé. |
| 16/03 | mar. | WhatsApp | H6 (« vous relisez, rien ne part sans vous »). |
| 17/03 | mer. | Site | Page « Dossier pour le conseil » téléchargeable sans formulaire (zéro friction, objection 6). |
| 18/03 | jeu. | Visio | Installations 4-5. Appel de retour mensuel des premières fondatrices (20 min). |
| 19/03 | ven. | WhatsApp | Coulisses 4 : le dossier RGPD, pourquoi deux pages et pas vingt. |
| 20/03 | sam. | Terrain | Congrès ou rassemblement d'union (date à caler) : stand, flyers H2/H9. |
| 21/03 | dim. | — | Repos. Rien ne part. |
| 22/03 | lun. | E-mail | Relance douce des pasteurs avec dossier mais sans installation : « une question qui bloque ? » |
| 23/03 | mar. L+16 | Interne | Bilan : les trois chiffres du § 5 ; décision continuer / changer. |

**Les dix accroches** (chacune dans son format, chacune contre une objection du § 1 ou pour une raison d'achat ; jamais attribuées à un pasteur ou une église) :

| # | Format | Accroche | Répond à |
|---|---|---|---|
| H1 | Première ligne WhatsApp, groupe de pasteurs | « Je suis [prénom], je développe un outil pour les pasteurs depuis [église d'attache]. Je cherche dix églises de 150 à 300 membres pour le mettre à l'épreuve, et je viens avec mon nom, pas avec une pub. » | 1 (qui est derrière) |
| H2 | Titre de flyer | « Personne ne pointe à la porte. Dix secondes le dimanche, et les personnes qu'on n'a pas vues depuis trois semaines ont un nom sur votre téléphone. » | 3 |
| H3 | 3 premières secondes, vidéo verticale | « Votre groupe WhatsApp est gratuit. Il ne vous dit pas qui n'est pas venu depuis trois dimanches. » | 2 |
| H4 | Objet d'e-mail, responsable d'union | « Un outil qui n'envoie rien sans vos pasteurs : 20 minutes pour votre avis, pas pour une vente » | 1, C4 |
| H5 | WhatsApp | « La demande de consentement part de votre nom, avec vos phrases, ou en chaire avec un papier pour les aînés. Jamais d'un logiciel. » | 4 |
| H6 | Flyer / WhatsApp | « Vous écrivez ou vous relisez. L'outil n'invente rien et n'envoie rien. » | 5 |
| H7 | 3 premières secondes, vidéo | « 140 contacts, la moitié sans nom de famille. Trente minutes en visio avec moi, et c'est propre. » | Raison d'achat P007 |
| H8 | Objet d'e-mail, pasteur | « Deux mois pour le conseil, sans carte bancaire : le dossier de deux pages est joint » | 6 |
| H9 | Verso du flyer | « 29 € HT par mois jusqu'à 200 membres (34,80 € TTC), 49 € HT jusqu'à 300 (58,80 € TTC). Un seul chiffre pour le conseil, jamais dépassé. » | Objection prix résiduelle, « un seul chiffre » |
| H10 | WhatsApp, jour du lancement | « Dix églises fondatrices : moitié prix à vie contre vingt minutes de retour par mois. Ça ferme quand la dixième est installée, pas à une date. » | 1 (preuve par les pairs), offre de lancement |

**L'offre de lancement** : les 10 églises fondatrices (`pricing.md` § 3), 9,50 / 14,50 / 24,50 € HT à vie, appel mensuel de 20 minutes, témoignage nommé seulement si l'église le veut, après usage. Fermeture à la dixième installation ; le compteur affiché est le vrai. Pas de « premier mois gratuit » : l'essai de 60 jours sans carte est la garantie satisfait ou remboursé, présentée comme essai.

**Quand il n'y a rien de neuf** (au plus un message tous les deux jours) : le flux de validation en capture, le schéma « l'IA ne voit pas vos membres », le dossier RGPD page par page, l'histoire du fondateur, une question aux pasteurs (« comment relevez-vous les présences ? »), le compteur réel. Jamais : avis, nombres d'abonnés, « vu dans », avant/après.

**Règles** : prospection B2B (adresses de fonction, intérêt légitime, désinscription dans chaque e-mail, registre, une seule relance) ; accord de l'administrateur avant tout lien dans un groupe WhatsApp ; les citations du panel servent à écrire, jamais à témoigner ; prix HT et TTC ; aucun superlatif non vérifiable ; tout partenariat payé est écrit « partenariat ». Pas un avis juridique.

### 5. Budget et chiffres

**Répartition** (1 000 € de lancement + 150 €/mois de récurrent, soit ≈ 1 300 € sur la fenêtre de 30 jours) :

| Poste | Canal | Montant |
|---|---|---|
| Déplacements vers 2 à 3 rassemblements (train, repas) | 1 | 450 € |
| Impression (200 flyers, 1 kakémono) | 1 | 150 € |
| Vidéo : micro-cravate, lumière, montage maison | 2, 3 | 120 € |
| Nom de domaine secondaire, hébergement vidéo, e-mailing conforme | 2 | 80 € |
| Réserve pour une invitation d'union imprévue | 1, 2 | 200 € |
| Récurrent 150 €/mois : déplacements du mois suivant, réimpression | 1 | 300 € |
| Publicité payante | — | 0 € |

**Le plus qu'on peut payer pour gagner une église.** Contribution CFO : **17,71 € par église-mois** (prix moyen 30 € HT). Le panel dit 1 achat par mois (abonnement) : la valeur dépend de la durée de vie, **inconnue** ; hypothèse posée : 18 mois.

| Durée de vie supposée | Contribution cumulée | Marge de sécurité 50 % (résiliation inconnue, panel simulé, trésorerie de 5 166 € à protéger) | Plafond |
|---|---|---|---|
| **18 mois (hypothèse)** | 17,71 × 18 = **318,78 €** | − 159,39 € | **≈ 160 € par église** |
| 12 mois (sensibilité) | 17,71 × 12 = 212,52 € | − 106,26 € | ≈ 106 € par église |

Lecture : **jamais plus de 160 € par église installée ; cible 106 €** (six mois de contribution : l'argent doit être revenu avant, tant que la trésorerie est celle du CFO). Avec 1 300 € sur 30 jours, il faut 8 installations pour tenir le plafond, 12 pour la cible. Les fondatrices à moitié prix rapportent ≈ 2,71 €/mois : leur coût est celui de la preuve, imputé au lancement, pas à l'acquisition.

**Trois chiffres, chaque lundi** :

| Chiffre | Objectif hebdo | « Changer quelque chose » si |
|---|---|---|
| Conversations de 15 min avec des pasteurs de la cible (150-300 membres, IA en main) | 8 | < 4 deux semaines de suite : le canal n'atteint pas le segment ; changer de canal |
| Dossiers remis → installations prises | 1 pour 4 | < 1 pour 8 sur deux semaines : le pitch ne lève pas l'objection 1 ou 3 ; réécouter cinq refus avant de toucher au prix |
| Coût cash par église installée | ≤ 106 € | > 160 € au 23/03 : arrêter les déplacements, garder 2 et 3 |

Et un quatrième, décisif (C4) : **une union qui accepte un pilote de trois églises avant le 23 mars**. Zéro sur cinq unions contactées deux fois : la distribution n'existe pas encore, et `/founder-launch` commence par là.

Suite : `/founder-brand` (nom de l'offre, ton, visuels des dix accroches), puis `/founder-launch` (les dix pasteurs réels, le test 49 € / 39 €).

## Brand

Méthode : `.claude/skills/founder-brand/SKILL.md`. Sources : `founder/idea.md`, `founder/marketing.md` (positionnement A), `founder/competitors.md`, `founder/panel/results.md`, `founder/panel-v2/results.md`, `founder/pitch.md`, `frontend/styles.css` (thème « Cabinet »). Recherches publiques seulement, faites le 20 novembre 2026 ; pas un avis juridique.

### 1. Le brief

**Positionnement (A).** Pour le pasteur d'une assemblée de 150 à 300 membres qui rédige déjà ses annonces avec un assistant IA et ne connaît plus tous les visages, Bureau du Pasteur est le secrétariat de communication contrôlé : il prépare le rappel du culte et met un nom sur les personnes qu'on n'a pas vues depuis trois semaines, sans rien envoyer sans son geste. L'alternative réelle n'est pas un logiciel d'église, c'est le groupe WhatsApp gratuit qui envoie tout et ne remarque personne. La marque doit donc dire *contrôle* avant *intelligence*, et rester discrète : ce que les membres voient, c'est le nom de leur église, jamais le nôtre.

**Ce que les acheteurs ont payé.** Deux pasteurs sur vingt, deux fois les mêmes (P007, P015) : « rien ne parte sans que j'appuie sur valider », « un bénévole prépare et je ne fais que valider d'un geste », « hébergement en France, consentement demandé à chaque membre, un dossier de deux pages pour le conseil ». Deux formules ont sonné faux et disparaissent : « dans vos mots » (P013, P019, P020 : une machine n'écrit pas dans les mots du pasteur) et « absents » (un pointage ; on dit « les personnes qu'on n'a pas vues »). Le prix n'est plus l'objection ; « qui est derrière » l'est : la marque porte un nom de fondateur et un visage.

### 2. Dix noms

| # | Nom | Style | Ce qu'il dit | À l'oral | Icône 32 px / flyer | Risque |
|---|---|---|---|---|---|---|
| 1 | **Bureau du Pasteur** | Descriptif (nom actuel) | Le pasteur est au bureau, c'est lui qui signe ; « pasteur » est le mot protestant et évangélique (un catholique dit curé) | Trois mots nets, se répètent sans faute au téléphone | Trop long pour une icône (il faut un monogramme) ; parfait sur un flyer et un dossier | Descriptif, donc marque faible à l'INPI ; 17 caractères, ne tient pas en expéditeur SMS |
| 2 | Le Cabinet | Descriptif (nom du thème CSS) | Un lieu fermé où l'on travaille avec discrétion | Sec, notarial ; évoque le médecin et le ministre | Bon monogramme « C » ; froid sur un flyer | Générique, impossible à protéger seul ; aucun lien à l'église |
| 3 | **Paraphe** | Évocateur (le geste) | Rien ne part sans vos initiales : le geste de validation nommé | « pa-raf », ferme ; parfois entendu « paragraphe » | Excellent à 32 px (un trait de plume) ; 7 caractères, tient en SMS | Mot administratif à expliquer une fois ; **paraphe.fr et .com pris** ; des marques « Paraphe » existent probablement en 9/42 |
| 4 | **Veilleur** | Évocateur (Ésaïe 62, Ézéchiel 33) | Celui qui remarque qui manque ; lexique protestant sans symbole | Doux, se retient | Belle lettre « V » ; 8 caractères | Peut se lire **surveillance des membres**, l'inverse de l'argument RGPD ; **veilleur.fr et .com pris** |
| 5 | Relève | Évocateur (relever les présences, relever celui qui tombe) | Le dimanche on relève, et on relève les personnes | Court, chantant ; accent gênant en URL | Bon ; l'accent disparaît en icône | Très usité (associations, RH) ; sens triple, donc flou |
| 6 | Pupitre | Évocateur | La table où le pasteur écrit son mot | Un peu scolaire | Forme simple | Pupitre = chaire dans certains temples : trop « culte », pas assez « communication » |
| 7 | Pastel | Inventé (PASteur + TÉLéphone) | Léger, moderne | Agréable, mais on entend la couleur | Icône douce, trop douce pour « contrôle » | Marques « Pastel » nombreuses ; ne dit ni église ni validation |
| 8 | Vigie | Évocateur court | Celui qui veille d'en haut | Vif | 5 lettres, idéal en icône et en SMS | Même risque que Veilleur ; marques « Vigie » nombreuses dans la sécurité |
| 9 | Charenton | Lieu (le temple de Charenton, Paris protestant du XVIIe) | Héritage huguenot d'Île-de-France | « Bon pour Charenton » veut dire « fou » | Lettrage historique crédible | Connotation asilaire ; nom de commune ; inconnu des évangéliques |
| 10 | Ubatelo | Nom du fondateur | « Je viens avec mon nom » (objection 1) ; très distinctif | Quatre syllabes régulières | Monogramme « U » net ; 7 caractères | Ne dit rien du produit ; lie l'entreprise à une personne ; à ne porter que si le fondateur l'assume publiquement |

Écartés sans tableau : tout nom à racine « Ecclé/Ekklo/Église-App » (confusion avec Ecclo et EgliseApp), toute racine « Church » (sept concurrents), « Visa » (marque notoire), « Sceau » (homophone de seau).

#### Short-list

1. **Bureau du Pasteur** : le seul des dix qu'un pasteur comprend sans explication, protestant par le mot même, entendu par quarante acheteurs simulés sans qu'un seul le relève. Forme courte pour l'icône et le SMS : **« le Bureau »** (expéditeur `LeBureau`, 8 caractères).
2. **Paraphe** : nomme exactement la promesse, protégeable, superbe à 32 px ; mais les deux domaines sont pris et le mot demande une phrase d'explication sur un stand.
3. **Veilleur** : le plus beau à l'oreille pour cette audience, mais il contredit « ce n'est pas un pointage » ; à garder comme nom d'une fonction, pas de la marque.

**Recommandation : garder Bureau du Pasteur**, avec Paraphe en réserve si la recherche INPI révèle une marque antérieure gênante. **Risque principal** : un nom descriptif est faiblement distinctif ; l'INPI peut refuser le mot seul, et un concurrent peut l'employer dans une phrase sans contrefaire. Parade : déposer une **marque semi-figurative** (nom + monogramme) et faire porter la distinctivité par le dessin et par la constance d'usage.

#### Les vérifications que le fondateur doit faire lui-même

- **INPI** : <https://data.inpi.fr/> (recherche « marques », à l'identique puis par similarité phonétique). Classes de Nice : **9** (logiciels), **38** (télécommunications : SMS, messagerie), **42** (SaaS, hébergement), **45** (services religieux et sociaux, où une union ou un éditeur religieux aurait pu déposer). Vérifier aussi les dénominations sociales (même site, onglet « entreprises »).
- **EUIPO** si l'offre passe en Belgique : <https://euipo.europa.eu/eSearch/>, mêmes classes. Inutile pour démarrer en France.
- **Domaines**, vérifiés par requête RDAP aux registres le 20 novembre 2026 : `bureaudupasteur.fr` et `lebureaudupasteur.fr` : **aucun enregistrement trouvé** ([rdap.nic.fr](https://rdap.nic.fr/domain/bureaudupasteur.fr)) ; `bureaudupasteur.com` : **aucun enregistrement trouvé** ([rdap.verisign.com](https://rdap.verisign.com/com/v1/domain/bureaudupasteur.com)) ; `paraphe.fr` (2009) et `paraphe.com` (1999) : **pris** ; `veilleur.fr` (2016) et `veilleur.com` (2015, parqué) : **pris**. « Non trouvé » veut dire libre à l'instant de la requête, pas réservé : enregistrer .fr et .com le jour de la décision.
- **Pseudos** Instagram, Facebook, YouTube, X : **non vérifiés** ; viser `bureaudupasteur` partout, repli `lebureaudupasteur`.
- **Confusion avec les concurrents** (`competitors.md`) : Eliakim, Church Manager, Ecclo, Enoria, ChMeetings, ChurchTools, B1.church, Text In Church, Planning Center, Breeze, ChurchDesk. Aucun des trois noms ne partage une racine, une sonorité ou une initiale dominante avec l'un d'eux. Leurs logos et couleurs **n'ont pas été relevés** dans `competitors.md` : avant de figer le logo, ouvrir les onze sites et poser les captures à côté des pistes ; si une forme ou une couleur dominante coïncide, changer la nôtre.

Seules des recherches publiques ont été faites ici. Un conseil en propriété industrielle confirme la disponibilité ; rien n'est protégé tant que le fondateur n'a pas déposé.

### 3. Voix et promesse

**La promesse (une ligne) :** « Rien ne part sans vous. »

**Trois signatures :**
1. « Préparé d'avance, jamais envoyé sans vous. »
2. « Le secrétariat qui attend votre geste. »
3. « Le rappel est prêt ; les personnes qu'on n'a pas vues ont un nom. »

**La voix en trois adjectifs :**

| Adjectif | On fait | On ne fait pas |
|---|---|---|
| **Sobre** | Une phrase, un fait, un chiffre réel (« 7 églises sur 10 installées ») ; le nom de l'église plus gros que le nôtre | Pas de superlatif, pas d'« IA révolutionnaire », pas d'émoji dans les messages aux pasteurs, pas de « sereine » ni d'adjectif qui promet un sentiment |
| **Franc** | Dire ce que l'outil ne fait pas (« il ne sait pas qui est venu si personne ne le note ») ; nommer le fondateur et son église d'attache | Pas de « dans vos mots », pas de témoignage prêté, pas de concurrent nommé dans un message |
| **Attentif** | Parler des personnes, jamais des « absents » ; vouvoyer ; écrire comme on parle à un pasteur après le culte, pas comme à un « utilisateur » | Pas de vocabulaire de pointage (« taux de présence », « relance »), pas de jargon logiciel (« workflow », « campagne ») face au pasteur |

**Avant / après** (première ligne de `founder/pitch.md`) :

> *Avant* : « Bureau du Pasteur, la Formule Église sereine : chaque dimanche, vos membres reçoivent le rappel du culte dans vos mots, les absents de plus de trois semaines ont un nom sur votre téléphone, et rien ne part sans votre validation d'un geste. Un bénévole peut tout préparer ; vous ne faites que valider. »

> *Après* : « Bureau du Pasteur prépare le rappel du culte ; vous l'écrivez ou vous le relisez, puis vous validez d'un geste sur votre téléphone. L'outil n'invente rien et n'envoie rien. Le dimanche soir, les personnes qu'on n'a pas vues depuis trois semaines ont un nom. Un bénévole peut préparer ; le dernier geste reste le vôtre. »

### 4. Le look

#### Couleurs

Le thème « Cabinet » actuel (violet profond `#2D1B4E`, or `#C9A227`, ivoire, empattements) a la bonne idée, le bureau d'un homme de lettres, et deux défauts. Le **violet** est la couleur liturgique de l'Avent et du Carême, et celle des évêques : un évangélique y lit « catholique » ou « mystique » (le commit git disait d'ailleurs « bleu nuit »). L'**or** `#C9A227` sur ivoire ne fait que **2,21:1**, illisible en texte. On garde l'esprit (encre, papier, un métal) et on corrige les valeurs.

| Couleur | Hex | Rôle | Contraste (WCAG) |
|---|---|---|---|
| **Encre** | `#1F2A44` | Titres, bouton principal, barre latérale, monogramme | Papier sur Encre **12,77:1** ; Encre sur blanc **14,26:1** (AAA) |
| **Papier** | `#F6F2EA` | Fond des pages, du dossier, du flyer | Encre sur Papier **12,77:1** (AAA) |
| **Laiton** | `#7A5C0E` | L'accent unique : le filet sous le titre, le trait du geste dans le logo, un mot souligné | Laiton sur Papier **5,59:1**, Laiton sur blanc **6,24:1** (AA texte normal) ; variante claire `#E6C766` **seulement sur Encre** (8,64:1), jamais sur fond clair |

Le vert de « Valider » reste une couleur fonctionnelle de l'interface (`--ok`), pas une couleur de marque, et on reste loin du vert WhatsApp.

#### Typographie

- **Titres : EB Garamond** (SIL OFL 1.1) : <https://fonts.google.com/specimen/EB+Garamond>. Garamond grave ses caractères à Paris dans les années 1530, le siècle des premières Bibles françaises : un héritage sans symbole religieux. Il remplace Cormorant Garamond, trop fin et trop petit d'œil sur un téléphone.
- **Texte : Inter** (SIL OFL 1.1), déjà dans `styles.css` : <https://fonts.google.com/specimen/Inter>. Chiffres clairs pour les prix et le compteur « x/10 ».
- Héberger les fichiers de polices sur notre serveur, pas via le CDN Google (l'adresse IP du visiteur ne doit pas partir aux États-Unis ; cohérent avec « données en France »).

#### Brief du logo

- **Doit dire** : le contrôle (c'est le pasteur qui signe), un geste de la main (un trait de plume, un paraphe), la discrétion (le logo recule derrière le nom de l'église).
- **Piste** : un monogramme « B » en EB Garamond dont le dernier trait s'achève en paraphe, couleur Encre, le trait en Laiton. Une seule forme, un seul trait, pas de dégradé.
- **Doit marcher** : en-tête de la page `/valider/{jeton}` à 24 px ; icône d'application 32 px (le monogramme seul, sur Encre) ; flyer A5 (monogramme + « Bureau du Pasteur » en Garamond) ; expéditeur SMS de 11 caractères : `LeBureau` pour les SMS au pasteur ; les SMS aux membres partent **au nom de l'église**, jamais au nôtre.
- **À éviter** : la croix (lue catholique par les uns, générique par les autres, clivante entre dénominations) ; la colombe (le 🕊️ du README disparaît : Pentecôte pour certains, application de prière pour d'autres) ; le poisson, la Bible ouverte, la silhouette d'église à clocher (image de paroisse) ; toute étincelle ou robot « IA » (l'IA est invisible, décision C6) ; le violet, pour la raison dite ; toute forme proche des onze concurrents.
- Pas d'outil d'image dans cette session : les pistes ci-dessus sont des **concepts**, pas un logo fini.

#### Les cinq premiers points de contact

1. **Titre de la page d'accueil** : « Le rappel du culte est prêt. Les personnes qu'on n'a pas vues ont un nom. Rien ne part sans vous. » Sous-titre : « Pour les pasteurs d'assemblées de 150 à 300 membres. Vous écrivez ou vous relisez ; l'outil n'invente rien et n'envoie rien. Données hébergées en France. Essai de 60 jours sans carte, dossier de deux pages pour le conseil. » Bouton : « Voir la démo (43 membres fictifs) ».
2. **Couverture du dossier de deux pages pour le conseil** : Papier, Encre, un filet Laiton. Titre : « Dossier pour le conseil de [nom de l'église] ». Sous-titre : « Ce que l'outil fait, ce qu'il ne fait jamais, où sont les données, ce que ça coûte. » Nom de l'église plus gros que le nôtre ; en pied : « Hébergé en France · Rien n'est envoyé sans validation du pasteur · Export et suppression en un clic », nom du fondateur, téléphone.
3. **SMS de validation reçu par le pasteur** (expéditeur `LeBureau`) : « Le rappel de dimanche est préparé : 212 destinataires, 0 sans consentement. Relire et valider : bureaudupasteur.fr/valider/[jeton] . Rien ne part sans vous. » (un seul segment ; éviter ê, ô, î, ç minuscule et le tiret long, qui font basculer le SMS en Unicode et le coupent en trois).
4. **Premier message dans un groupe WhatsApp de pasteurs** : « Bonjour à tous, je suis [prénom], membre de [église], développeur. Je construis un outil pour les pasteurs d'assemblées de 150 à 300 membres : il prépare le rappel du culte et met un nom sur les personnes qu'on n'a pas vues depuis trois dimanches ; rien ne part sans le pasteur. Je cherche dix églises pour le mettre à l'épreuve, pas des clients. Si l'administrateur est d'accord, je mettrai un lien ; sinon écrivez-moi en privé. »
5. **Réponse à la première plainte** (un rappel remis en retard un dimanche) : « Pasteur, vous avez raison. Le rappel que vous avez validé à 8 h 12 a été remis à 31 membres sur 212 à 10 h 40, après le début du culte. La cause : [fait vérifié ; si on ne sait pas encore : « je ne la connais pas encore, je vous rappelle à 14 h »]. Ce que j'ai fait ce matin : [action]. Ce que je change cette semaine : [action datée]. Le mois en cours ne vous sera pas facturé. Je vous appelle demain à l'heure qui vous convient. » Jamais d'excuse générale, jamais de cause inventée, jamais de « incident technique ».

Suite : `/founder-ops` et `/founder-launch`.

## Operations

Méthode : `.claude/skills/founder-ops/SKILL.md`, adaptée à un abonnement logiciel tenu par un fondateur seul. Matière : `founder/offer.md` (hébergement en France, DPA signé, consentement par l'outil, installation en visio 30 min, assistance dimanche 7 h-13 h, remboursé 60 jours, WhatsApp inclus, SMS au coût réel sous plafond), `founder/numbers.json`, `founder/cfo-sources.md`, `docs/DEPLOIEMENT.md`, `docs/SECURITE_RGPD.md`. Prix relevés le 2026-11-20 sur les pages publiques liées ; « devis » quand seul un devis dira. Ceci n'est pas un avis juridique, fiscal ou comptable.

### 1. Le cycle de la semaine

👁 = l'église le voit.

| Quand | Ce que fait le fondateur |
|---|---|
| **Chaque jour, 8 h (15 min)** | `GET /api/sante`, erreurs Sentry, messages en attente/échoués, webhooks Twilio (statuts, STOP/START/OUI) reçus, `pg_dump` de la nuit présent. Boîte de support (e-mail + WhatsApp Business) : réponse sous 24 h 👁. |
| **Lundi** | Revue délivrabilité et coûts (SOP d). Relances d'impayés SEPA. |
| **Mardi à jeudi** | Installations en visio (SOP a), 30 min + 15 min de préparation/suivi 👁. Corrections produit ; déploiements le jeudi, jamais le week-end. |
| **Vendredi** | Avant le week-end : rappels planifiés, solde Twilio/API, certificats TLS, disque. Message aux nouvelles églises : « votre premier rappel part samedi à 18 h » 👁. |
| **Samedi** | Pic d'envoi des rappels du culte. Téléphone à portée ; pas de déploiement. |
| **Dimanche 7 h-13 h** | Assistance téléphone/WhatsApp (SOP b) 👁. Rien d'autre. 13 h : note d'incidents. |
| **En continu (automatisé)** | STOP/ARRET/DESINSCRIRE → retrait du consentement du canal, journalisé ; OUI → consentement daté ; `List-Unsubscribe` ; liens de validation valables 48 h. Le fondateur vérifie seulement que ça a tourné. |
| **1er du mois** | Clôture (SOP e) : versements Stripe, factures 👁, test de restauration, journal RGPD, registre. |

### 2. Fournisseurs

**L'offre promet « hébergement en France »** : Scaleway (Paris) et OVHcloud (Gravelines, Strasbourg, Roubaix) la tiennent ; Hetzner (Falkenstein, Nuremberg, Helsinki) est en UE mais **pas en France**.

| Poste | Fournisseur | Prix public (HT) | Note |
|---|---|---|---|
| Serveur de production | [Scaleway DEV1-S](https://www.scaleway.com/en/pricing/virtual-instances/) (2 vCPU/2 Go, Paris) | 6,55 €/mois | Retenu. PLAY2-PICO 10,42 € si besoin. |
| | [OVHcloud VPS-1](https://www.ovhcloud.com/fr/vps/) (2 vCore/4 Go) | « à partir de » 3,81 €/mois | Prix de première période ; [datacentres France](https://www.ovhcloud.com/en/about-us/global-infrastructure/regions/). |
| | [Hetzner](https://www.hetzner.com/cloud/) | dès 4,99 €/mois | Allemagne/Finlande : **hors promesse France**. |
| PostgreSQL | Auto-hébergé (conteneur `db`) | 0 € | Retenu au départ ; `pg_dump` quotidien. |
| | [Scaleway Managed DB DB-DEV-S](https://www.scaleway.com/en/pricing/managed-databases/) | 0,0156 €/h ≈ 11,40 €/mois + 0,0993 €/Go + sauvegardes 0,03 €/Go | Vers 30-40 églises : sauvegardes et chiffrement gérés. |
| Sauvegardes hors serveur | [Scaleway Object Storage](https://www.scaleway.com/en/pricing/storage/) (Paris) | 0,00803 €/Go/mois, 75 Go de sortie gratuits | Centimes/mois pour des dumps chiffrés. |
| SMS | [Twilio](https://www.twilio.com/en-us/sms/pricing/fr) | 0,0798 $/segment, 0,0075 $ entrant, numéro dès 1,15 $/mois ; expéditeur alphanumérique gratuit mais sans réponse STOP | « As of November 2026 ». Numéro français : [K-bis et adresse exigés](https://www.twilio.com/en-us/guidelines/fr/regulatory). |
| | [smsmode](https://www.smsmode.com/tarifs-sms/) (Marseille) | 0,061 €/SMS (pack 1 000) ; abonnement 9 €/mois → 0,0445 €/SMS | Numéro de réponse : devis. Exige une `ChannelGateway`. |
| | [Octopush](https://www.octopush.com/), [Spot-Hit](https://www.spot-hit.fr/) | devis | Grilles non publiques au relevé. |
| WhatsApp (BSP) | [Twilio](https://www.twilio.com/en-us/whatsapp/pricing) | 0,005 $/message + tarif Meta | « As of September 2026 ». Retenu. |
| | [360dialog](https://www.360dialog.com/pricing) | 49 €/numéro/mois, Meta sans marge | Rentable > ~9 000 messages/mois ; secours si Twilio bloque. |
| Tarif Meta WhatsApp | [Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) | **par message livré**, par catégorie et pays ; France : utility ≈ 0,030 $, marketing ≈ 0,0859 $ (grille citée dans `cfo-sources.md`) ; 1 000 « service » gratuits/mois | **Meta décide la catégorie** du gabarit : voir « Écarts ». |
| E-mail transactionnel | [Brevo](https://www.brevo.com/fr/pricing/) (France) | gratuit 300/jour ; Starter dès ~7 €/mois | Retenu au lancement. |
| | [Amazon SES](https://aws.amazon.com/ses/pricing/) (Paris) | 0,10 $/1 000 e-mails | Le moins cher à l'échelle. |
| | [Postmark](https://postmarkapp.com/pricing) | gratuit 100/mois ; 15 $/mois pour 10 000 | Hébergé aux États-Unis (point DPA). |
| Encaissement (SEPA) | [Stripe](https://stripe.com/fr/pricing) | SEPA 0,35 € ; carte UE 1,5 % + 0,25 € ; Billing 0,7 % | Retenu. |
| | [GoCardless](https://gocardless.com/fr-fr/tarifs/) | 1 % + 0,20 €, plafonné à 2 € | 0,50 € sur 30 €. |
| | [Mollie](https://www.mollie.com/fr/pricing) | SEPA 0,35 € ; CB 1,2 % + 0,25 € | 0 €/mois. |
| IA | [Anthropic API](https://platform.claude.com/docs/en/about-claude/pricing) | Opus 5 : 5 $/25 $ par M jetons ; **Opus 5.5 : 4 $/20 $** ; Sonnet 5.5 : 2 $/10 $ ; Haiku 5.5 : 0,10 $/0,50 $ | `.env.example` cible `claude-opus-5` : passer à `claude-opus-5-5`. |
| Erreurs, disponibilité, page d'état | [Sentry](https://sentry.io/pricing/) | gratuit (5 000 erreurs/mois) ; Team 26 $/mois | |
| | [Better Stack](https://betterstack.com/pricing) | gratuit : 10 moniteurs, 1 page d'état ; dès 25 $/mois | Page d'état publique 👁. |
| | [Uptime Kuma](https://github.com/louislam/uptime-kuma) | gratuit (auto-hébergé) | Sur la seconde instance. |
| Juridique | [CNIL, clauses de sous-traitance](https://www.cnil.fr/fr/sous-traitance-exemple-de-clauses) ; [clauses types UE 2021](https://www.cnil.fr/fr/clauses-contractuelles-types-entre-responsable-de-traitement-et-sous-traitant) ; [guide du sous-traitant](https://www.cnil.fr/sites/default/files/atoms/files/rgpd-guide_sous-traitant-cnil.pdf) | gratuit ; relecture juriste : devis (1 500 € estimés) | Base du DPA promis. |

#### Écarts avec numbers.json (pour le CFO, fichier non modifié)

1. **WhatsApp inclus (9,74 €/église-mois)** suppose 0,033 €/message, donc la catégorie « utility ». Si Meta classe le rappel du culte en « marketing » (0,0859 $ + 0,005 $ ≈ 0,083 €), le forfait pondéré (295 messages) coûte **≈ 24,50 €** : la marge sur un prix moyen de 30 € disparaît. Avant de vendre : rédiger les gabarits en « utility » (rappel d'un événement auquel la personne est inscrite), tester la classification Meta sur 3 gabarits réels, prévoir un plafond d'inclusion en euros plutôt qu'en messages. [Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)
2. **Frais de paiement (0,71 €)** : en SEPA, Stripe facture 0,35 € + **Stripe Billing 0,7 %** (0,21 € sur 30 €) ≈ 0,56 € ; GoCardless ≈ 0,50 €. Faible, à la baisse. [Stripe](https://stripe.com/fr/pricing)
3. **Expert-comptable (60 €)** : SASU avec liasse par l'expert-comptable : Indy « Sérénité » **99 € HT/mois** ; « Autonomie » (sans expert) 49 € ; micro-entreprise 0 à 12 €. [Indy](https://www.indy.fr/tarifs/)
4. **E-mail (0,42 €/église)** : à 60 églises (≈ 72 000 e-mails/mois) SES ≈ 7 $/mois, soit 0,11 €/église. À la baisse.
5. **Création de société (300 €)** : obligatoire 2026 ≈ 142 € HT d'annonce légale + 53,16 € de greffe ≈ **195 €** ([service-public](https://entreprendre.service-public.gouv.fr/vosdroits/F37688)). À la baisse.
6. **IA (0,62 €)** et **hébergement (25 €)** : cohérents (Opus 5.5 à 4 $/20 $ ; 2 × DEV1-S = 13,10 €, ≈ 26-30 € avec PostgreSQL managé).

### 3. Les personnes

Fondateur seul. Par église : **installation 0,75 h une fois** (30 min d'appel + 15 min de préparation/suivi) et **support 0,33 h/mois** (hypothèse `cfo-sources.md`, à mesurer sur les trois pilotes). Temps fixe, indépendant du nombre d'églises : dimanche 6 h × 4,3 = 26 h/mois, revue hebdo 6,5 h, clôture 4 h, surveillance quotidienne 7,5 h → **44 h/mois avant la première église**.

| | Premier mois (3 pilotes) | À 60 églises (+3 nouvelles/mois) |
|---|---|---|
| Fixe | 44 h | 44 h |
| Installations | 2,25 h | 2,25 h |
| Support | 1 h | 20 h |
| **Total exploitation** | **≈ 47 h/mois (11 h/sem.)** | **≈ 66 h/mois (15 h/sem.)** |
| Reste pour développer et vendre (base 170 h) | 123 h | 104 h |

**Plafond du fondateur seul** : l'exploitation dépasse 80 h/mois (un mi-temps) vers ≈ 100 églises, mais le dimanche est le goulot : à 60 églises, 60 rappels partent le samedi soir et les incidents tombent sur les mêmes six heures pour une seule personne ; `offer.md` fixe déjà la réévaluation de S5 et S8 à 50. **Retenu : 60 églises** (= `plan_per_day`) sous les promesses actuelles ; au-delà, une personne de support à temps partiel (10 h/semaine : dimanche en alternance + installations).

**Paie, à chiffrer par le comptable** : SMIC horaire brut 12,31 € au 1er juin 2026 ([service-public](https://www.service-public.gouv.fr/particuliers/vosdroits/F2300)) ; coût employeur complet via le [simulateur URSSAF](https://mon-entreprise.urssaf.fr/simulateurs/salaire-brut-net). Le travail du dimanche a ses règles (repos, majorations) : à vérifier avant d'embaucher. Alternative : prestataire indépendant à l'heure.

### 4. Routines (SOP)

#### a. Installation en visio (30 min) 👁

1. Avant : compte église créé, forfait et plafond SMS (0 € par défaut), expéditeur = nom de l'église, lien Cal.com avec la liste « à préparer » (export WhatsApp, vCard ou tableur).
2. 0-5 min : page de validation mobile sur le téléphone du pasteur ; redire « rien ne part sans vous ».
3. 5-12 min : import (vCard/CSV/export WhatsApp). L'import ne crée **jamais** de consentement ; le dire.
4. 12-18 min : doublons et « Contact » sans nom ; le pasteur nomme ceux qu'il reconnaît, le reste est « à compléter », jamais contacté.
5. 18-24 min : campagne de consentement (« Répondez OUI pour recevoir les nouvelles de l'église ») + formulaire en ligne + modèle papier.
6. 24-29 min : premier rappel du culte dans les mots du pasteur (3 anciens messages collés) ; il valide depuis son téléphone ; vérifier qu'il ne part qu'aux consentants.
7. 29-30 min : jour/heure d'envoi hebdo, numéro du dimanche, page d'état. Après : DPA envoyé à signer, note dans la fiche, rappel à J+7.

#### b. Incident du dimanche matin

1. Accuser réception en moins de 10 min ; ouvrir une ligne au journal d'incidents.
2. Trier : (i) non livré à quelques personnes → statut Twilio (`undelivered`, code), consentement retiré, numéro invalide ; renvoyer au pasteur la liste des non-joints. (ii) Erreur Twilio/Meta pour tous (gabarit refusé, numéro suspendu, solde) → basculer : WhatsApp → SMS si plafond, sinon e-mail + « partager dans mon groupe WhatsApp ». (iii) Serveur injoignable → page d'état, redémarrage `docker compose`, restauration sur la seconde instance si > 30 min.
3. Jamais de correctif de code le dimanche : contournement, correction le jeudi.
4. 13 h : message de clôture à chaque église touchée (cause, heure, ce qui change). Lundi : registre des incidents ; si des données ont pu fuir, SOP c, point 5.

#### c. Réclamation, demande RGPD, réponse STOP

1. STOP/ARRET/DESINSCRIRE : automatique et immédiat ; vérifier l'entrée d'audit ; aucune relance.
2. Demande d'un membre à l'église (responsable de traitement ; Bureau du Pasteur est sous-traitant) : le pasteur agit dans l'outil : accès/portabilité `GET /api/membres/{id}/export`, rectification `PATCH`, effacement `DELETE` (anonymisation). Le fondateur n'agit que sur instruction écrite ; délai un mois.
3. Demande reçue par le fondateur : accuser réception, rediriger vers l'église, consigner.
4. Réclamation sur le service : réponse sous 24 h ; garantie 60 jours sans question ; export remis, suppression à J+30 confirmée par écrit.
5. Violation de données : prévenir l'église sans délai indu ; elle notifie la CNIL sous 72 h si risque ; modèle de notification prêt à l'avance.

#### d. Revue hebdomadaire délivrabilité et coûts (lundi, 1 h 30)

1. Gabarits WhatsApp : statut (approuvé/en attente/refusé/en pause) et **catégorie** attribuée par Meta ; tout gabarit requalifié « marketing » est réécrit.
2. Qualité du numéro WhatsApp (vert/jaune/rouge) et limite de messagerie.
3. SMS : coût par église vs plafond ; alerte à 80 % ; segments doubles (émojis → UCS-2, 70 caractères).
4. Messages échoués par code d'erreur ; numéros invalides marqués ; e-mails : rebonds et plaintes.
5. Taux de STOP par église ; > 2 % → appeler le pasteur (ton, fréquence).
6. Solde Twilio, dépense IA, facture Scaleway ; noter les écarts avec `numbers.json`.

#### e. Clôture mensuelle (1er du mois, 4 h)

1. Stripe : versements rapprochés, échecs SEPA relancés, factures émises (mentions, TVA).
2. Pièces fournisseurs déposées en comptabilité (Twilio, Scaleway, Anthropic, Brevo).
3. Restauration d'une sauvegarde en préproduction ; compter les lignes ; noter la durée.
4. Mises à jour : dépendances Python, images Docker, PostgreSQL mineur ; les 51 tests verts avant déploiement.
5. Journal RGPD (demandes, délais) ; registre mis à jour si un sous-traitant change.
6. Métriques : églises actives, résiliations, remboursements, coût réel par église-mois.

### 5. Les outils (pile minimale)

| Besoin | Outil | Prix |
|---|---|---|
| Facturation, abonnements, SEPA | [Stripe Billing](https://stripe.com/fr/pricing) | 0,35 €/prélèvement + 0,7 % |
| Boîte de support | Google Workspace Business Starter ([tarifs](https://workspace.google.com/pricing)) + [application WhatsApp Business](https://business.whatsapp.com/products/business-app) | ≈ 7 $/utilisateur/mois (annuel) ; application gratuite |
| Page d'état et disponibilité | [Better Stack](https://betterstack.com/pricing) | gratuit (1 page d'état, 10 moniteurs) |
| Erreurs | [Sentry Developer](https://sentry.io/pricing/) | gratuit |
| Comptabilité, facturation électronique | [Indy](https://www.indy.fr/tarifs/) (ou [Pennylane](https://www.pennylane.com/fr/tarifs/) dès 7 €/mois) | 0 € ; 49 € Autonomie ; 99 € avec expert-comptable |
| Prise de rendez-vous d'installation | [Cal.com](https://cal.com/pricing) | gratuit (1 utilisateur) |
| Mots de passe et secrets | [Bitwarden](https://bitwarden.com/pricing/) | gratuit ; Premium 19,80 $/an |
| Support partagé (quand une 2e personne arrive) | [Crisp](https://crisp.chat/fr/pricing/) | offre gratuite, puis payant |

Total au lancement : **≈ 10 à 20 €/mois** (40 € dans `numbers.json` : prudent).

### 6. Licences, enregistrements, obligations, assurance

Les règles diffèrent selon le statut et changent chaque année ; chaque ligne est à confirmer avec l'autorité ou un professionnel.

| Sujet | À faire | Où confirmer |
|---|---|---|
| Immatriculation | Micro-entreprise (simple, plafonds, TVA non récupérable) ou SASU (recommandée : contrats B2B, DPA, assurance, embauche). Guichet unique ; coût obligatoire SASU ≈ 195 €. | [procedures.inpi.fr](https://procedures.inpi.fr/) ; [coût des formalités](https://entreprendre.service-public.gouv.fr/vosdroits/F37688) ; [cotisations micro](https://entreprendre.service-public.gouv.fr/vosdroits/F36232) |
| TVA | Franchise en base 2026 : 37 500 € (majoré 41 250 €) pour les services ; en dessous, « TVA non applicable, art. 293 B » et les prix de l'offre se lisent HT = TTC. Au-delà, 20 %. | [service-public](https://entreprendre.service-public.gouv.fr/vosdroits/F21746) |
| Marque | 1 classe : 190 €, + 40 €/classe. | [INPI](https://www.inpi.fr/) |
| RGPD, art. 9 | L'appartenance à une église révèle une conviction religieuse : donnée sensible. Base côté église : art. 9-2-d (organisme sans but lucratif à finalité religieuse, membres et contacts réguliers) ; l'éditeur est sous-traitant. Minimisation documentée dans `docs/SECURITE_RGPD.md`. | [CNIL, données sensibles](https://www.cnil.fr/fr/definition/donnee-sensible) |
| Registre des traitements | Obligatoire même < 250 salariés dès qu'il y a des données sensibles ; registre « sous-traitant » + modèle fourni aux églises. | [CNIL, registre](https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement) |
| AIPD | La liste CNIL des **exemptions** couvre la gestion des membres d'une association « dès lors que les données ne sont pas sensibles » : ici elles le sont, avec envoi à grande échelle et IA. **AIPD très probablement requise**, à faire une fois (modèle pour toutes les églises) avant le lancement. | [CNIL, listes AIPD](https://www.cnil.fr/fr/listes-des-traitements-pour-lesquels-une-aipd-est-requise-ou-non) |
| DPA (art. 28) | Signé avec chaque église : objet, durée, sous-traitants ultérieurs (Scaleway, Twilio/Meta, Anthropic, Brevo, Stripe), transferts hors UE (clauses types + mesures), suppression en fin de contrat. | [CNIL, clauses](https://www.cnil.fr/fr/sous-traitance-exemple-de-clauses) ; [CCT 2021](https://www.cnil.fr/fr/clauses-contractuelles-types-entre-responsable-de-traitement-et-sous-traitant) |
| Mentions légales, CGV B2B, confidentialité | Éditeur, hébergeur (Scaleway, Paris), SIREN, TVA ; CGV : durée, résiliation, garantie 60 jours, plafond de responsabilité. | juriste (devis) |
| RC professionnelle (+ cyber) | Défaillance du service, fuite de données, litige. Hiscox « dès 175 €/an » (indépendant) ; éditeur SaaS : devis. | [Hiscox](https://www.hiscox.fr/), [Stello](https://www.stello.fr/) |
| WhatsApp Business Platform | Vérification de l'entreprise Meta (K-bis, adresse, site), puis nom affiché ; gabarits soumis et classés par Meta ; opt-in explicite. | [Meta, vérification](https://www.facebook.com/business/help/2058515294227817) |
| Numéro SMS français | Twilio exige K-bis + justificatif d'adresse ; l'expéditeur alphanumérique ne reçoit pas les STOP. | [Twilio, France](https://www.twilio.com/en-us/guidelines/fr/regulatory) |
| Règles SMS France | Consentement préalable (L34-5 CPCE) ; STOP gratuit dans chaque message (« STOP au 36111 » si expéditeur alphanumérique, selon l'agrégateur) ; charte af2m 2026 : promotionnels 8 h-21 h 30, dimanche toléré non recommandé ; les messages fonctionnels (rappel d'un événement auquel on est inscrit) ne sont pas concernés : rédiger les rappels comme tels. | [CNIL](https://www.cnil.fr/fr/la-prospection-commerciale-par-courrier-electronique-sms-mms-et-automate-dappel) ; [af2m 2026](https://af2m.org/charte-business-messaging-2026-laf2m-renforce-les-regles-du-jeu/) ; [ARCEP](https://www.arcep.fr/demarches-et-services/utilisateurs/sms-appels-et-courriers-electroniques-indesirables-et-ou-frauduleux.html) |

### 7. Registre des risques

| # | Risque | Prob. | Impact | Plan |
|---|---|---|---|---|
| 1 | Numéro Twilio bloqué ou filtré par les opérateurs (volume soudain, contenu signalé) | moyenne | fort : aucun SMS un samedi | Numéro acheté 30 jours avant, montée progressive, K-bis à jour ; smsmode prêt en secours (`ChannelGateway`) ; bascule e-mail + partage WhatsApp. |
| 2 | Gabarit WhatsApp refusé ou requalifié « marketing » | forte | fort : coût ×2,5 ou envoi impossible | 3 gabarits approuvés d'avance ; revue hebdo des catégories ; plafond en euros ; SMS de repli sous plafond. |
| 3 | E-mails en spam | moyenne | moyen | SPF/DKIM/DMARC, domaine d'envoi dédié, `List-Unsubscribe`, rebonds nettoyés ; Postmark en secours. |
| 4 | Serveur indisponible le dimanche | faible | fort | Seconde instance, restauration testée chaque mois (RTO < 1 h) ; page d'état ; rappels envoyés le samedi, un incident du dimanche ne touche que l'assistance. |
| 5 | Fondateur malade ou indisponible | moyenne | fort | Envois automatisés et validés par le pasteur : le service tourne sans lui. Absence annoncée sur la ligne du dimanche ; un pair de confiance avec accès d'urgence (Bitwarden, procédure écrite) ; temps partiel au-delà de 60 églises. |
| 6 | Violation de données d'une église | faible | très fort (art. 9, CNIL, confiance) | Chiffrement au repos, MFA, secrets hors Git ; sauvegardes chiffrées ; procédure 72 h ; assurance cyber. |
| 7 | Plainte CNIL (non-consentant contacté, STOP ignoré) | faible | fort | Consentement par canal daté, exclusion et STOP automatiques, audit complet ; AIPD et DPA avant la vente. |
| 8 | Litige ou rejet SEPA | moyenne | faible | Garantie 60 jours avant tout litige ; mandat SEPA clair ; relance J+3, suspension douce J+30 sans effacer. |
| 9 | Hausse de tarif Meta ou Twilio | forte (annuelle) | moyen | Clause d'indexation des canaux dans les CGV, plafond en euros, 360dialog/smsmode comparés chaque trimestre ; e-mail et partage WhatsApp gratuits en plancher. |
| 10 | Panne du fournisseur d'IA ou retrait d'un modèle | moyenne | faible | Mode gabarits hors-ligne déjà fonctionnel ; `LLM_MODEL` configurable ; aucune donnée membre envoyée à l'IA. |

**Prochaine étape** : `/founder-launch`, trois pilotes payants pour mesurer le temps réel d'installation et de support et confirmer la classification Meta des gabarits.

## Launch plan

Méthode : `.claude/skills/founder-launch/SKILL.md`. Rédigé le 2026-11-20. Lancement public : **dimanche 7 mars 2027** (`founder/marketing.md`). Chiffres repris sans modification de `pricing.md`, `numbers.json`, `cfo.md`, `ops.md`, `marketing.md`, `brand.md`. Aucun pasteur, aucune union, aucune église n'est nommée : rien n'est acquis. Pas un avis juridique ni comptable.

Rôles : **F** = le fondateur (seul, développeur) · **J** = le juriste (RGPD art. 9, AIPD, DPA, CGV ; 1 500 € estimés) · **EC** = l'expert-comptable (99 € HT/mois) · **EA** = l'église amie (une assemblée du réseau du fondateur, 5 bénévoles volontaires, non cliente : le banc d'essai).

### 1. Tester avant de dépenser

C'est un abonnement : le test est **le programme des 10 églises fondatrices, payé d'avance** (`pricing.md` § 3 : moitié prix à vie, 14,50 € HT pour une Assemblée de 101 à 200 membres, 24,50 € HT pour une Grande assemblée de 201 à 300, contre un appel de retour mensuel de 20 minutes). Le démarrage (3 685 € : société, marque, juriste, site) part avant le test ; **le récurrent (déplacements, impression, serveurs à l'échelle) n'est engagé qu'après**.

| | |
|---|---|
| Qui | **20 pasteurs réels** d'assemblées de **150 à 300 membres** (`marketing.md` § 2), rencontrés dans des rassemblements d'unions ou présentés par un pair |
| Quand | Conversations du **lundi 11 janvier au dimanche 28 février 2027** |
| Quoi | 15 à 30 min : le dossier pour le conseil (S1), la démo sur téléphone (43 membres fictifs), le prix public (29 € / 49 € HT, TTC à côté), l'offre fondatrice |
| L'engagement | **Payer le premier trimestre fondateur** (43,50 € ou 73,50 € HT) par mandat SEPA Stripe, ou signer le mandat avec prélèvement à l'activation, **avant que le logiciel ne soit allumé**. La garantie 60 jours reste : l'argent est réel mais récupérable, c'est ce qui rend le test honnête |
| À consigner (C1) | taille, « curieux de l'IA » ou non, **qui paie** (pasteur, conseil, union), objection de départ, dossier remis, mandat signé |

Aucune activation avant l'AIPD et le DPA validés par J (29/01, § 2) : on peut encaisser un engagement, pas traiter les données d'une église.

**Ligne de succès, écrite avant de commencer : au moins 5 églises sur 20 paient un premier trimestre fondateur (ou signent un mandat SEPA) d'ici le 2027-02-28.**

Comparaison avec le panel (`panel-v2/results.md`) : 2 sur 20 (10 %) sur la cible large ; sur le segment 150-300 membres, 2 sur 12 (échantillons minces). Le 10 % est un plafond ; la ligne (25 %) est au-dessus parce que le test se fait en face à face, avec le dossier, sur le seul segment qui a acheté deux fois. Si des pasteurs réels font moins bien que des cartes simulées, c'est l'information.

| Au 28/02 | Lecture | Décision |
|---|---|---|
| **≥ 5 / 20** | Au-dessus du panel ; la ramp (2 à 3 nouvelles églises par mois) est crédible | Lancement le 07/03 ; budget marketing de `marketing.md` § 5 engagé |
| **3-4 / 20** | Panel confirmé (10 à 20 %) | Lancement maintenu, un seul rassemblement payé ; le seuil de **18 églises** recule après le mois 9 et le creux dépasse les **5 186 €** du CFO : le fondateur le sait avant de dépenser |
| **≤ 2 / 20** | Le segment réel achète moins que le simulé | **« Pas encore »**, lancement reporté. Refus « confiance » ou « besoin » (les deux premières causes du panel v2) → `/founder-offer` (pitch v3). Refus « prix » (1 sur 18 au panel) → `/founder-pricing`. Critère de `pricing.md` § 4 : moins de 3 sur 20, le problème n'est pas le prix |

Les nombres qui tranchent : la ramp suppose **10 % sur ≈ 30 conversations par mois** (`cfo.md`) ; seuil **18** ; trésorerie **5 186 €** ; une fondatrice rapporte ≈ 2,71 €/mois (`marketing.md`) : de la preuve, pas du revenu. Les tests de prix de `pricing.md` § 4 (49 € contre 39 € HT ; annuel avec deux mois offerts) se font **à partir du 07/03 sur deux pages d'inscription alternées**, pas pendant le test fondateur, dont les prix sont fixes.

#### Les trois pré-tests techniques

| | Test | Pourquoi | Quand | Succès |
|---|---|---|---|---|
| **(a)** | **Classification Meta de trois gabarits réels** (rappel du culte, demande de consentement, changement d'horaire) soumis via Twilio | « Marketing » (0,0859 $ au lieu de 0,030 $) ramène la contribution de 18,17 € à **3,41 €** et le seuil à **95 églises**, au-dessus de la capacité de 60 (`cfo.md`) | Soumission 08/01 ; verdict et réécritures jusqu'au **29/01** | Trois gabarits **« utility »** ; sinon forfait inclus en euros, repli SMS sous plafond, `/founder-pricing` avant le 05/02 |
| **(b)** | **Bout en bout sur l'EA** : import (vCard ou export WhatsApp) → consentement → validation depuis le téléphone → rappel du samedi 18 h à 5 bénévoles → présences en un geste le dimanche | C7 : temps réel et point d'abandon ; rien aux non-consentants (`test_approval_invariant.py`) | Samedis **06/02, 13/02, 20/02** | Installation ≤ 45 min (0,75 h de `ops.md`), 5 livrés sur 5, 0 sans consentement, 0 sans validation |
| **(c)** | **AIPD et DPA relus par J**, avec le registre sous-traitant et les CGV | Art. 9 ; `ops.md` : AIPD très probablement requise, avant la première église payante | Brouillons F 11/12 et 18/12 ; retour J 08/01 ; **final 29/01** | J écrit « prêt à signer » ; DPA signé par chaque église avant son import |

### 2. Le compte à rebours (23/11/2026 → 07/03/2027)

**★ = chemin critique.** Trois chaînes : **K-bis → Twilio et Meta** (les deux exigent l'extrait) ; **AIPD + DPA → première église payante** ; **classification Meta → prix**. Les dates sont des échéances, pas des promesses des administrations ; la marge est indiquée.

| Semaine | Légal et argent | Conformité | Build et canaux | Marque et marketing |
|---|---|---|---|---|
| **S1 · 23-29/11** | ★ F : statuts SASU, compte pro en ligne, dépôt du capital, annonce légale (≈ 142 €) — 27/11. EC : rendez-vous 27/11, régime TVA (franchise en base 37 500 € : HT = TTC pour l'église, ou option 20 %). F : devis J, devis RC pro + cyber | F : registre des traitements (sous-traitant) v1 — 04/12 | F : `LLM_MODEL` → `claude-opus-5-5` ; S3 forfaits, compteur, plafond (début) | F : bureaudupasteur.fr et .com — 23/11 ; recherche INPI classes 9, 38, 42, 45 — 27/11 ; captures des logos des 11 concurrents |
| **S2 · 30/11-06/12** | ★ F : dépôt au guichet unique INPI — **02/12** (greffe 53,16 €). J engagé 30/11 | F → J : brief dossier du conseil (S1), « Qui est derrière » (S13), CGV, mentions — 04/12 | F : S2 demande de consentement (« Répondez OUI », formulaire, papier) | F : dossier du conseil v1 (Papier, Encre, filet Laiton) — 04/12 |
| **S3 · 07-13/12** | ★ K-bis attendu (cible 11/12) ; RC pro signée à réception | F : AIPD brouillon → J — 11/12 | F : S4 bouton « partager dans mon groupe WhatsApp » ; S7 expéditeur au nom de l'église | F : concept du monogramme « B » EB Garamond au paraphe — 11/12 ; polices auto-hébergées |
| **S4 · 14-20/12** | ★ **K-bis au plus tard le 18/12.** Le jour même : **Twilio regulatory bundle** et **Meta Business verification** ; Stripe compte + SEPA + Billing ; dépôt INPI marque semi-figurative (190 € + 40 €/classe) — 18/12 | F : DPA brouillon → J — 18/12 | F : S9 présences en un geste ; Scaleway Paris prod DEV1-S + seconde instance — 18/12 | F : expéditeur SMS `LeBureau` réservé |
| **S5 · 21-27/12** | Noël, pas d'échéance | — | F : `pg_dump` chiffrés vers Object Storage Paris ; page d'état Better Stack ; Sentry — 23/12 | — |
| **S6 · 28/12-03/01** | Marge K-bis (limite **08/01**) | F : modèle de notification de violation 72 h | F : SPF/DKIM/DMARC Brevo ; 51 tests + tests S2/S3/S9 verts ; restauration testée | F : page d'accueil v1 (point de contact 1 de `brand.md`) |
| **S7 · 04-10/01** | ★ Bundle approuvé → **numéro français acheté** — 08/01 (limite **05/02 = L−30**, `ops.md` risque 1). Meta vérifié → expéditeur WhatsApp, nom affiché | ★ J : retours AIPD, DPA, CGV — 08/01 | ★ **3 gabarits soumis à Meta — 08/01** ; `ChannelGateway` smsmode en secours | F : liste des 20 pasteurs (unions, pairs) ; dates des rassemblements calées ; page « Qui est derrière » |
| **S8 · 11-17/01** | F : mandat SEPA de test interne | F : DPA v2, registre v2 | ★ Verdict Meta (cible 15/01) ; réécriture si « marketing » | **Test réel : conversations 1-5** ; flyer A5 brouillon (H2 / H9) |
| **S9 · 18-24/01** | EC : première déclaration, facturation électronique | ★ J : CGV et mentions finales — 22/01 | Seconde soumission si besoin ; compteur testé contre 300/600 | Conversations 6-10 |
| **S10 · 25-31/01** | — | ★ **J : AIPD + DPA « prêts à signer » — 29/01** → première église payante autorisée | ★ **Porte Meta fermée le 29/01** : « utility » ou décision prix/forfait avant le 05/02 | Conversations 11-15 ; EA : répertoire exporté — 29/01 |
| **S11 · 01-07/02** | Premiers trimestres fondateurs encaissés dès le 01/02 | DPA signé avec l'EA avant import | ★ **Pré-test (b) n° 1** : livraison **samedi 06/02 18 h**, présences dimanche 07/02 ; **première ligne du dimanche 7 h-13 h** | Conversations 16-20 ; 200 flyers + kakémono commandés (150 €) |
| **S12 · 08-14/02** | EC : point TVA, factures Stripe | SOP c relue avec J | Pré-test (b) n° 2 — 13/02 ; corrections déployées le **jeudi 11/02** | Vidéo 45 s « présences en dix secondes » ; pair de confiance avec accès d'urgence (Bitwarden) — 12/02 |
| **S13 · 15-21/02** | — | DPA signé avec chaque fondatrice avant son import | Pré-test (b) n° 3 — 20/02 ; **gel des fonctions le 18/02** | **Ouverture douce** : installations fondatrices 1 et 2 (mardi-jeudi, SOP a) ; **21/02 L−14 : calendrier `marketing.md` § 4** |
| **S14 · 22-28/02** | — | — | Rappels réels des fondatrices samedi 27/02 18 h | Calendrier 22-28/02 tel qu'écrit ; installation fondatrice 3 ; **28/02 : clôture du test, comptage** |
| **S15 · 01-07/03** | **Lundi 01/03 : décision** go / go réduit / pas encore | — | Dernier déploiement **jeudi 04/03** ; vendredi : solde Twilio et API, TLS, disque, « votre rappel part samedi 18 h » | Calendrier 01-06/03 ; 06/03 installation fondatrice (créneau de `marketing.md`) ; rappels 06/03 18 h ; **dimanche 07/03 : lancement** |

Écart assumé avec `marketing.md` : il place la « première installation fondatrice » le 06/03 ; le test exige des églises payées avant le lancement, donc les fondatrices du test sont installées du 16/02 au 06/03 et **le compteur « x/10 installées » du 07/03 est réel**.

**Règles de glissement.** K-bis après le 08/01 : Twilio et Meta reculent d'autant, le numéro perd ses 30 jours, le lancement recule d'un dimanche par semaine de retard. Gabarits non « utility » au 29/01 : lancement maintenu seulement si le forfait en euros et le repli SMS sont livrés le 18/02. AIPD/DPA non finalisés le 12/02 : aucune activation avant le 28/02, le test ne se clôt pas, le lancement recule. Pré-test (b) raté trois fois : pas de lancement public.

**Équipe** : aucune embauche. F tient seul la ligne du dimanche 7 h-13 h dès le 07/02 (26 h/mois, `ops.md`) ; plafond **60 églises**, au-delà un temps partiel de support (10 h/semaine).

### 3. Le jour du lancement : dimanche 7 mars 2027

F chez lui, téléphone, page d'état ouverte, **pas de déplacement** : la ligne du dimanche passe avant la communication. Les rappels des églises installées sont partis **samedi 06/03 à 18 h** ; le dimanche porte l'assistance et la publication.

| Heure | Quoi |
|---|---|
| 6 h 00 | `GET /api/sante`, Sentry, `pg_dump` de la nuit, webhooks Twilio (statuts, STOP/OUI), qualité du numéro WhatsApp, solde Twilio et API, certificats ; par église installée : livrés / non livrés du samedi, liste des non-joints prête |
| 6 h 30 | Journal d'incidents ouvert ; replis vérifiés (SMS sous plafond, e-mail, bouton « partager », smsmode) ; page d'inscription testée avec un mandat interne ; compteur « x/10 » vérifié à la main |
| 7 h 00 | **Ouverture de la ligne** (WhatsApp Business + téléphone, SOP b) ; un message sobre à chaque pasteur installé : « Ligne ouverte jusqu'à 13 h. » |
| 8 h-12 h | Cultes. Accusé de réception en moins de 10 min ; rien d'autre : ni publication, ni code |
| 12 h-13 h | Les pasteurs relèvent les présences en un geste ; F vérifie que les saisies arrivent |
| 13 h 00 | Fermeture ; note d'incidents ; message de clôture à chaque église touchée (cause, heure, ce qui change : point de contact 5 de `brand.md`) |
| 13 h 30 | **Go / no-go** : aucun incident ouvert, page d'état verte, compteur exact. Sinon la publication glisse au **lundi 08/03 soir** : on ne lance pas « Rien ne part sans vous » pendant une panne |
| 14 h 00 | **Lancement** (`marketing.md`, 07/03) : groupes WhatsApp de pasteurs (accord des administrateurs obtenu avant) : **H10** « Dix églises fondatrices : moitié prix à vie contre vingt minutes de retour par mois. Ça ferme quand la dixième est installée, pas à une date. » + lien d'inscription ; page d'inscription publique (variantes 49 € / 39 € alternées) ; **vidéo H3** publiée ; compteur réel |
| 14 h-16 h | Réponses en privé ; chaque conversation consignée (taille, IA en main, qui paie) ; aucune relance dans les groupes |
| 19 h-21 h | Vérifier que la liste « personnes qu'on n'a pas vues depuis trois semaines » est arrivée aux pasteurs ; répondre ; chiffres du jour ; préparer l'e-mail du lundi 08/03 (« ouvert aujourd'hui, 60 jours sans carte, dossier joint ») et la revue délivrabilité-coûts (SOP d) |

**Si ça casse** (`ops.md`, registre et SOP b) :

| Panne | Geste du dimanche | Jamais |
|---|---|---|
| Quelques membres non livrés | Statut Twilio (`undelivered`, code), consentement retiré, numéro invalide ; liste renvoyée au pasteur | Renvoyer en masse |
| Gabarit refusé ou requalifié, numéro suspendu, solde | WhatsApp → SMS si le plafond de l'église le permet, sinon e-mail + partage dans le groupe ; gabarit réécrit lundi | Corriger du code le dimanche |
| Numéro Twilio bloqué ou filtré | smsmode via `ChannelGateway` ; e-mail + partage en plancher | Acheter un numéro dans l'urgence |
| Serveur injoignable | Page d'état, `docker compose` redémarré ; seconde instance si > 30 min (RTO < 1 h) | Déployer |
| Un message parti sans validation | Garantie S10 (un an offert), église prévenue, audit extrait, publication du jour annulée | Minimiser |
| Donnée exposée | SOP c point 5 : église prévenue sans délai, notification CNIL 72 h, assurance cyber | Attendre lundi |

### 4. Les trente premiers jours (07/03 → 06/04)

Chaque lundi, les mêmes chiffres :

| Chiffre | Cible | « Changer quelque chose » si |
|---|---|---|
| Églises payantes (fondatrices comprises) vs **seuil 18** et ramp `numbers.json` (fin de mois : 0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28 ; 19 au mois 9 = novembre 2027) | ≥ 5 le 07/03 ; **≥ 7 le 06/04** | < 5 le 06/04 : « Pas encore » (ci-dessous) |
| Compteur WhatsApp par église vs forfait (300 / 600) ; catégorie Meta de chaque gabarit (SOP d) | Consommation ≈ 60 % (contribution 22,07 €, `cfo.md`) ; 100 % « utility » | Une église > 80 % : alerte, plafond discuté ; un gabarit « marketing » : réécrit la semaine même ; variable réel > 11,83 €/église-mois : forfait en euros |
| Conversations de 15 min, pasteurs 150-300, IA en main (`marketing.md` § 5) | **8 / semaine** | < 4 deux semaines de suite : changer de canal |
| Dossiers remis → installations | **1 pour 4** | < 1 pour 8 sur deux semaines : réécouter cinq refus avant de toucher au prix |
| Coût cash par église installée | **≤ 106 €** | > 160 € au 23/03 : arrêter les déplacements, garder les canaux 2 et 3 |
| Incidents du dimanche (types ii, iii) ; délai d'accusé | 0 ; < 10 min | Un incident deux dimanches de suite : gel des installations jusqu'à la cause |
| Temps d'installation et de support (`ops.md` § 3) ; STOP ; remboursements | 0,75 h et 0,33 h/mois ; < 2 % ; ≤ 10 % des nouvelles | > 1,5 h sur trois églises : C7 non tenu ; STOP > 2 % : appeler le pasteur ; remboursements > 10 % : `/founder-offer` |

**J+7, lundi 15 mars** (le compte rendu aux unions de `marketing.md`). Deux samedis de rappels, un dimanche de présences réelles (14/03). Combien d'églises ont relevé les présences sans qu'on le leur demande ? Combien de membres ont répondu OUI, en quel délai ? Les trois gabarits sont-ils toujours « utility » ? Les 8 conversations ont-elles eu lieu, avec le bon segment ? Un seul message parti sans validation ? (attendu : non, sinon tout s'arrête).

**J+14, mardi 23 mars** (le bilan L+16 de `marketing.md`). Les trois chiffres marketing dans la cible ? Coût par église ≤ 160 € ? **C4 : une union a-t-elle accepté le pilote de trois églises ?** Cinq unions contactées deux fois sans réponse : la distribution n'existe pas encore, et c'est par là qu'on recommence. Fondatrices installées sur 10 ? Taux réel conversation → mandat, face aux 10 % du panel et aux 25 % de la ligne ? Décision : continuer / changer de canal / changer de pitch.

**J+30, mardi 6 avril.** Églises payantes vs 7 attendues et 18 à atteindre ; contribution réelle par église-mois vs 18,17 € ; remboursements ; temps mesurés vs 0,75 h et 0,33 h ; heures réelles du dimanche ; une église accepte-t-elle un témoignage nommé ? Le 49 € a-t-il converti autant que le 39 € ? Plus de la moitié en annuel ?

**Critère « Pas encore » du J+30 : le 06/04, moins de 5 églises payantes au total (fondatrices du test comprises), ou aucune union n'ayant accepté le pilote de trois églises après deux contacts auprès de cinq unions.** Alors : les églises installées restent servies (ligne du dimanche, appels mensuels) ; les déplacements s'arrêtent ; retour à `/founder-offer` si les refus consignés sont « confiance » ou « besoin », à `/founder-pricing` s'ils sont « prix », à `/founder-marketing` canal 2 si c'est l'accès aux unions ; nouvelle date fixée seulement quand une union a dit oui. Si les deux conditions tiennent : `/founder-plan` compile le dossier avec les chiffres réels.

_The panel is simulated buyers and the numbers are projections from your inputs. Confirm demand with real customers and costs with real quotes before you spend. Not financial, legal or tax advice._
