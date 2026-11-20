# La note du CFO — Bureau du Pasteur

Tous les chiffres ci-dessous viennent de `founder/numbers.json` (v2 : trois formules, prix moyen pondéré 30 € HT) passés dans `unit_economics.py`, ou d'une entrée nommée dans `founder/cfo-sources.md`. Les montants sont en euros HT ; l'outil écrit « $ », lire « € ». Ni conseil financier, ni fiscal, ni juridique : un expert-comptable doit vérifier la structure, les charges sociales et la TVA avant que de l'argent ne circule.

## La marge

- **Contribution par église-mois : 17,71 € sur 30 € (59 %).** Chaque église abonnée laisse 17,71 € après ses coûts propres. Le poste qui pèse est le forfait WhatsApp inclus (9,74 € si le forfait est consommé en entier) : c'est le prix de la promesse « un seul chiffre pour le conseil ». Si les églises consomment en moyenne 60 % du forfait, la contribution monte à 21,60 €.
- **Marge au plan (60 églises) : 42 %** après tous les coûts fixes. **Seuil de rentabilité : 18 églises abonnées** (coûts fixes 303 € par mois, sans rémunération du fondateur).

## La ligne à surveiller

**La montée en charge, puis la rémunération du fondateur.** Deux ce qui-si le prouvent :

| Scénario | Seuil (églises) | Marge au plan | Résultat an 1 |
|---|---|---|---|
| Base (fondateur non payé, 28 églises en mois 12) | 18 | 42 % | −922 € |
| Volume −20 % | 18 | 38 % | −1 464 € |
| Prix −10 % | 21 | 36 % | −1 381 € |
| Coûts unitaires +15 % | 20 | 36 % | −1 204 € |
| **Fondateur payé 1 500 €/mois** (`scratchpad/numbers-founder-paid.json`) | **102** | **−41 %** | **−18 922 €** |

Lecture : avec un fondateur non payé, l'affaire est à l'équilibre dès 18 églises et ne perd que 922 € en opérations l'année 1 à cause d'une montée en charge lente. **Avec un fondateur payé 1 500 € par mois, il faut 102 églises abonnées, au-dessus de la capacité d'un fondateur seul (100).** Autrement dit : telle qu'elle est chiffrée, c'est une activité d'appoint jusqu'à environ 100 églises, ou une entreprise à condition d'un prix moyen plus élevé (les Grandes assemblées à 49 € ou plus) ou d'un canal qui amène des églises par dizaines (une union).

## La montée en charge, et comment elle a été fixée

Le panel simulé donne 10 % d'achat (2 sur 20, les deux chez des pasteurs de plus de 150 membres), à lire comme un plafond. Avec un fondateur seul qui rencontre peut-être 30 pasteurs par mois dans les rassemblements d'unions, 10 % font 3 nouvelles églises par mois ; la ramp retenue (0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28 églises abonnées en fin de mois) suppose 2 à 3 nouvelles églises par mois et presque aucune résiliation. C'est optimiste sur la résiliation et prudent sur l'acquisition. Les 10 églises fondatrices à moitié prix font baisser le prix moyen réel des premiers mois d'environ 15 € par église : l'an 1 réel sera un peu pire que le tableau.

## Trésorerie

**Cash nécessaire avant que l'affaire ne se paie : 5 166 €** (3 790 € de démarrage, dont 1 500 € d'avis juridique RGPD, plus le creux des six premiers mois). Le démarrage n'est pas remboursé dans l'année 1. Le fondateur doit pouvoir vivre sans salaire de l'activité pendant l'année 1.

## Trois façons d'améliorer la marge (chiffrées avec l'outil)

1. **Vendre d'abord aux assemblées de 150 à 300 membres** (ce que le panel recommande de toute façon) : si le mix passe à 20 / 40 / 40 % au lieu de 40 / 35 / 25 %, le prix moyen passe de 30 € à 35,00 € HT et la contribution à environ 21 € ; le seuil tombe vers 15 églises.
2. **Facturer le forfait WhatsApp consommé, pas théorique** : à 60 % de consommation moyenne, la contribution passe de 17,71 € à 21,60 € (+22 %) ; seuil 14 églises. À surveiller chaque mois, c'est le compteur de messages.
3. **Paiement annuel (deux mois offerts)** : ne change pas la marge mais avance la trésorerie ; si la moitié des églises paient à l'année, le creux de trésorerie de 5 166 € se réduit d'environ un tiers.

À l'inverse, baisser le prix de 10 % coûte 6 points de marge et 3 églises de seuil : le prix n'est pas le levier.

## Les conditions du conseil qui touchent à l'argent

- **C3 (modèle de coûts par église)** : rempli, ci-dessus et dans `founder/cfo-sources.md`.
- **C1 (prix validé par des paiements)** : non rempli, c'est le test de `founder/launch.md`.
- **C8 (le produit fournit les canaux)** : chiffré (numéro mutualisé 1,15 €/mois, WhatsApp inclus) ; à confirmer par `founder/ops.md`.
- **C9 (garantie dont le coût est vérifié)** : provision de 0,50 € par église-mois dans les coûts variables.

---

# Unit economics: Bureau du Pasteur (abonnement SaaS pour églises locales, France)

Every number below comes from the input file. Nothing is looked up or guessed.

## One église-mois

| line | per église-mois |
| --- | ---: |
| Price | 30.00 |
| Frais de paiement Stripe 1,5 % + 0,25 € (moyenne des 3 formules) [public] | -0.71 |
| API IA, 20 à 40 demandes/mois selon la formule (sonnet pour les petites, opus pour les grandes) [estimation] | -0.62 |
| Messages WhatsApp inclus, forfait utilisé en entier : 100/300/600 à ~0,033 € (Meta utility France + Twilio) [public] | -9.74 |
| E-mails transactionnels [estimation] | -0.42 |
| Hébergement, part variable [estimation] | -0.30 |
| Provision garantie satisfait ou remboursé 60 jours (10 % des nouveaux, lissée) [estimation] | -0.50 |
| SMS : en option, refacturés au coût réel, 0 € de marge [public] | -0.00 |
| **Contribution** (what each église-mois leaves to pay the fixed costs) | **17.71** (59%) |

## The margin that matters

Fixed costs: 303 a month (Serveurs UE (prod + sauvegarde/préprod) et stockage [public] 25, Domaine et certificats [estimation] 2, Outils : e-mail pro, facturation/compta, suivi d'erreurs [estimation] 40, Assurance RC professionnelle [estimation] 25, Expert-comptable en ligne [estimation] 60, Numéro Twilio mutualisé [public] 1, Marketing récurrent (déplacements, impression, annonces) [estimation] 150, Rémunération du fondateur : 0 € la première année (hypothèse explicite) [fondateur] 0).

- **Break-even: 18 églises-mois a day.** Below that you lose money every month.
- **Profit margin at your plan** (60 a day): **42%** of every sale, after every cost.
- Capacity: 100 a day.

## Year 1, month by month

| month | églises-mois a day | revenue | profit | cumulative (after 3,790 startup) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | -303 | -4,093 |
| 2 | 2 | 60 | -267 | -4,360 |
| 3 | 4 | 120 | -232 | -4,592 |
| 4 | 6 | 180 | -196 | -4,788 |
| 5 | 8 | 240 | -161 | -4,949 |
| 6 | 10 | 300 | -126 | -5,075 |
| 7 | 13 | 390 | -72 | -5,147 |
| 8 | 16 | 480 | -19 | -5,166 |
| 9 | 19 | 570 | 34 | -5,132 |
| 10 | 22 | 660 | 87 | -5,046 |
| 11 | 25 | 750 | 140 | -4,905 |
| 12 | 28 | 840 | 193 | -4,712 |

- **Year 1 operating profit: -922** on 4,590 of revenue.
- After the 3,790 startup spend: -4,712.
- Startup money earned back: not within year 1.
- Cash you need before it pays for itself: **5,166**.

## What if

| scenario | margin at plan | break-even a day | year 1 profit |
| --- | ---: | ---: | ---: |
| Base plan | 42% | 18 | -922 |
| Price -10% | 36% | 21 | -1,381 |
| Volume -20% | 38% | 18 | -1,464 |
| Unit costs +15% | 36% | 20 | -1,204 |

## Red flags

- Year 1 loses money on operations (-922).
- The startup spend is not earned back within year 1.
