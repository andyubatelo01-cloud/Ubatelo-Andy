# La note du CFO — Bureau du Pasteur

Tous les chiffres viennent de `founder/numbers.json` (v3 : trois formules, prix moyen pondéré 30 € HT, coûts corrigés par `founder/ops.md`) passés dans `unit_economics.py`, ou d'une entrée nommée dans `founder/cfo-sources.md`. Montants en euros HT ; l'outil écrit « $ », lire « € ». Ni conseil financier, ni fiscal, ni juridique : un expert-comptable doit vérifier la structure, les charges sociales et la TVA avant que de l'argent ne circule.

## La marge

- **Contribution par église-mois : 18,17 € sur 30 € (61 %).** Le poste qui pèse est le forfait WhatsApp inclus (9,74 € si le forfait est consommé en entier, catégorie Meta « utility ») : c'est le prix de la promesse « un seul chiffre pour le conseil ».
- **Marge au plan (60 églises) : 43 %** après tous les coûts fixes (322 € par mois, dont 99 € d'expert-comptable et 150 € de marketing, sans rémunération du fondateur). **Seuil de rentabilité : 18 églises abonnées.**

## La ligne à surveiller

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

## La montée en charge, et comment elle a été fixée

Le panel simulé donne 10 % d'achat (2 sur 20, deux fois, les deux chez des pasteurs de plus de 150 membres), à lire comme un plafond. Un fondateur seul qui rencontre 30 pasteurs par mois dans les rassemblements d'unions en convertit au mieux 3 ; la ramp retenue (0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28 églises abonnées en fin de mois) suppose 2 à 3 nouvelles églises par mois et presque aucune résiliation : prudente sur l'acquisition, optimiste sur la résiliation. Les 10 églises fondatrices à moitié prix baissent le prix moyen réel des premiers mois d'environ 15 € par église : l'an 1 réel sera un peu pire que le tableau.

## Trésorerie

**Cash nécessaire avant que l'affaire ne se paie : 5 186 €** (3 685 € de démarrage, dont 1 500 € d'avis juridique RGPD et d'AIPD, plus le creux des six premiers mois). Le démarrage n'est pas remboursé dans l'année 1. Le fondateur doit pouvoir vivre sans salaire de l'activité pendant l'année 1.

## Trois façons d'améliorer la marge (chiffrées avec l'outil)

1. **Vendre d'abord aux assemblées de 150 à 300 membres** (le panel et le marketing le recommandent) : un mix 20 / 40 / 40 % au lieu de 40 / 35 / 25 % porte le prix moyen de 30 € à 35 € HT et la contribution à environ 21,50 € ; le seuil passe de 18 à 15 églises.
2. **Facturer le forfait WhatsApp consommé, pas théorique** : à 60 % de consommation moyenne, la contribution passe de 18,17 € à 22,07 € (+21 %) ; seuil 15 églises. Le compteur de messages est le chiffre à regarder chaque mois.
3. **Paiement annuel (deux mois offerts)** : ne change pas la marge mais avance la trésorerie ; si la moitié des églises paient à l'année, le creux de 5 186 € se réduit d'environ un tiers.

À l'inverse, baisser le prix de 10 % coûte 7 points de marge et 4 églises de seuil : le prix n'est pas le levier.

## Ce que `founder/ops.md` a corrigé dans les chiffres

Prélèvement SEPA au lieu de la carte (0,56 € au lieu de 0,71 €), expert-comptable SASU avec liasse 99 € au lieu de 60 €, outils 20 € au lieu de 40 €, e-mail 0,11 € au lieu de 0,42 €, création de société 195 € au lieu de 300 €, capacité 60 églises au lieu de 100 (goulot de l'assistance du dimanche). Hébergement : Hetzner exclu tant que l'offre promet « hébergé en France » (Scaleway Paris ou OVHcloud). Recommandation reprise : passer le modèle d'IA de `claude-opus-5` à `claude-opus-5-5` (4 $ / 20 $ par million de jetons au lieu de 5 $ / 25 $).

## Les conditions du conseil qui touchent à l'argent

- **C3 (modèle de coûts par église)** : rempli, ci-dessus et dans `founder/cfo-sources.md`.
- **C1 (prix validé par des paiements)** : non rempli, c'est le test de `founder/launch.md`.
- **C8 (le produit fournit les canaux)** : chiffré (numéro mutualisé 1,15 €/mois, WhatsApp inclus) ; les verrous (K-bis pour Twilio et Meta) sont dans `founder/ops.md`.
- **C9 (garantie dont le coût est vérifié)** : provision de 0,50 € par église-mois dans les coûts variables.

---

# Unit economics: Bureau du Pasteur (abonnement SaaS pour églises locales, France)

Every number below comes from the input file. Nothing is looked up or guessed.

## One église-mois

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

## The margin that matters

Fixed costs: 322 a month (Serveurs UE (prod + sauvegarde/préprod) et stockage [public] 25, Domaine et certificats [estimation] 2, Outils : e-mail pro, facturation/compta, suivi d'erreurs [estimation] 20, Assurance RC professionnelle [estimation] 25, Expert-comptable en ligne, SASU avec liasse (Indy Sérénité 99 € HT) [public] 99, Numéro Twilio mutualisé [public] 1, Marketing récurrent (déplacements, impression, annonces) [estimation] 150, Rémunération du fondateur : 0 € la première année (hypothèse explicite) [fondateur] 0).

- **Break-even: 18 églises-mois a day.** Below that you lose money every month.
- **Profit margin at your plan** (60 a day): **43%** of every sale, after every cost.
- Capacity: 60 a day.

## Year 1, month by month

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

## What if

| scenario | margin at plan | break-even a day | year 1 profit |
| --- | ---: | ---: | ---: |
| Base plan | 43% | 18 | -1,080 |
| Price -10% | 36% | 22 | -1,539 |
| Volume -20% | 38% | 18 | -1,636 |
| Unit costs +15% | 37% | 20 | -1,351 |

## Red flags

- Year 1 loses money on operations (-1,080).
- The startup spend is not earned back within year 1.
