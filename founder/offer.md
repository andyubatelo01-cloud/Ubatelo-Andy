# L'offre — Bureau du Pasteur

Méthode : la lentille Offres (`.claude/skills/founder-board/lenses.md`), résumé d'un cadre publié, appliqué par nous. Matière première : `founder/panel/results.md` (2 achètent, 18 passent), `founder/board.md` (conditions C1 à C10), `founder/numbers.json`, `founder/pricing-curve.md` (fourchette acceptable 5,20 € à 38,97 € ; 39 € est au-dessus).

## 1. Ce que les acheteurs ont dit, en une ligne

Le prix n'est pas la première raison de refus : **9 refus sur 18 sont « confiance »** (où vont les données de mes membres, qui est derrière, aucun pasteur que je connais ne l'utilise), **7 sont « habitude »** (WhatsApp et un bénévole font déjà le travail gratuitement). Le prix arrive derrière, mais il bloque quand même : 39 € HT (46,80 € TTC) est au-dessus du seuil « je n'achète pas » de 13 pasteurs sur 20, et les petites églises (0 % d'achat) ont un plafond de 30 à 40 € TTC. La facture SMS « au coût réel » est citée 5 fois : le pasteur veut **un seul chiffre à annoncer au conseil**.

## 2. La liste des problèmes (dans les mots des acheteurs)

### Avant d'acheter
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

### Pendant
11. L'import d'un groupe WhatsApp donne des « Contact » sans nom à corriger un par un. (P011)
12. Recueillir le consentement de 150 personnes. (P009)
13. Les membres âgés ne liront pas un SMS venu d'un logiciel plutôt que du pasteur. (P017)
14. « Le suivi des absents suppose que quelqu'un note les présences chaque dimanche ; personne ne le fait. » (P007)
15. Apprendre un outil de plus avec 35 heures de travail à côté. (P005, P016)
16. Créer un compte Twilio, un SMTP, une clé API (conseil, lentille Produit).

### Après
17. « Qui nous aide si ça ne marche pas un dimanche à 8 h ? » (P016, objection de départ de 3 cartes)
18. « Que deviennent les données si on arrête ? » (P002, P006, P007, P013)
19. « Le ton n'est pas le mien. » (P020)
20. « Les données servent-elles à entraîner une IA, sont-elles revendues ? » (P002, P013, P019)
21. « Le jour où je valide sans relire, la machine parle pour moi. » (P020)
22. Une facture qui varie d'un mois à l'autre. (P003, P018)

## 3. Les solutions, notées et triées

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

## 4. La pile

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

## 5. L'équation de valeur, avant et après (1 à 10)

| Élément | Avant (pitch v1) | Après (pitch v2) | Ce qui a bougé |
|---|---|---|---|
| Résultat rêvé | 6 | 7 | Le cœur est dit par le résultat (absents nommés, rappel dans mes mots) et non par les fonctions |
| Probabilité perçue d'y arriver | 3 | 6 | Dossier pour le conseil (S1), garanties (S10, S11), fondateur nommé (S13), églises fondatrices (S12) |
| Délai jusqu'au résultat | 5 | 7 | Installation en 30 minutes faite avec vous (S5) |
| Effort et sacrifice | 3 | 7 | Consentements recueillis par l'outil (S2), bénévole qui prépare (S6), un seul chiffre pour le conseil (S3), rien à configurer (S14) |

La probabilité perçue reste le point faible : seule une liste d'églises nommées la fera monter au-delà de 6. C'est le rôle du programme des fondatrices et de `/founder-launch`.

## 6. Ce qu'il faut construire avant de vendre l'offre

- S2 : demande de consentement par message et formulaire (petit développement sur le moteur de campagnes existant).
- S3 : forfaits par taille, compteur de messages, plafond par église (facturation Stripe).
- S4 : bouton « partager dans mon groupe WhatsApp » (texte prêt à coller).
- S7 : expéditeur au nom de l'église ; apprentissage du style sur trois anciens messages.
- S9 : présences en un geste.
- S1, S13 : deux documents à rédiger avec le juriste (voir `founder/cfo-sources.md`, poste « avis juridique »).

## 7. Le nouveau test

Le pitch v2 (`founder/pitch.md`, l'ancien est `founder/pitch-v1.md`) est présenté aux **mêmes 20 pasteurs** (graine 7) dans `founder/panel-v2/`. Résultat avant : 2 achètent, 18 passent (10 %). Résultat après : voir la section « Re-test » ci-dessous, ajoutée une fois le panel v2 compté.


## Re-test : pitch v2 devant les mêmes 20 pasteurs (`founder/panel-v2/results.md`)

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

## Règles respectées

Aucun témoignage, aucun avis, aucune rareté ou remise inventés. Les promesses (hébergement en France, DPA, remboursement, assistance du dimanche, installation en visio) sont livrables par un fondateur seul jusqu'à environ 50 églises ; au-delà, S5 et S8 doivent être réévaluées. Les règles françaises sur les garanties et la publicité s'appliquent ; ceci n'est pas un avis juridique.
