# Résumé — Bureau du Pasteur

**Verdict calculé par `compile.py` : Pas encore.** Deux vérifications sur quatre échouent : l'année 1 perd 1 080 € en exploitation (montée en charge trop lente pour un fondateur seul), et 2 pasteurs simulés sur 20 achètent (10 %, la barre est à 25 %). Les deux autres passent : chaque église-mois laisse 18,17 € avant coûts fixes (61 %) et le seuil de rentabilité, 18 églises, tient dans la capacité d'un fondateur seul (60).

## Ce qu'il faut changer, et quelle compétence le change

1. **Le segment, pas le produit.** Deux panels, deux fois 10 %, les deux acheteurs sont les mêmes : des pasteurs d'assemblées de plus de 150 membres qui utilisent déjà un assistant IA. Les églises de 50 à 100 membres ont acheté 0 % deux fois : le pasteur « voit les bancs ». La première cible est l'assemblée de 150 à 300 membres (`founder/marketing.md`). Un mix orienté vers elles porte le prix moyen de 30 à 35 € et le seuil de 18 à 15 églises (`founder/cfo.md`).
2. **La preuve par les pairs.** Après la version 2 de l'offre, l'objection n° 1 n'est plus le prix ni le RGPD mais « aucun pasteur que je connais ne l'utilise ». Seuls le programme des 10 églises fondatrices et un pilote avec une union la lèvent (`founder/launch.md`, condition C4 du conseil).
3. **Le pitch doit dire la vérité simplement** : retirer « dans vos mots » et « absents », montrer qui note les présences, faire partir la demande de consentement au nom du pasteur, offrir un essai présentable au conseil sans carte (`founder/offer.md`, re-test ; `founder/brand.md`).

## Ce que c'est, et pour qui

Bureau du Pasteur est un secrétariat de communication en ligne pour les églises évangéliques et protestantes francophones : il prépare le rappel du culte, les invitations et le suivi des personnes qu'on n'a pas vues depuis trois semaines, par WhatsApp, SMS et e-mail, et n'envoie rien sans la validation du pasteur d'un geste sur son téléphone. Il est vendu par abonnement, 19, 29 ou 49 € HT par mois selon la taille de l'assemblée, tout compris, au pasteur d'une assemblée de 150 à 300 membres en France qui ne connaît plus tous les visages.

## Les trois chiffres derrière le verdict

| | Valeur | Source |
|---|---|---|
| Contribution par église-mois | 18,17 € sur 30 € HT (61 %) | `founder/cfo.md` |
| Seuil de rentabilité | 18 églises abonnées (coûts fixes 322 €/mois, fondateur non payé) | `founder/cfo.md` |
| Année 1 | −1 080 € d'exploitation sur 4 590 € de revenus ; 28 églises en mois 12 | `founder/cfo.md` |

Avec un fondateur payé 1 500 € par mois, le seuil passe à 101 églises, au-dessus de la capacité de 60 : tel que chiffré, c'est une activité d'appoint ou une entreprise à condition d'un canal qui amène des églises par dizaines.

## Ce sur quoi le panel et le conseil sont d'accord, et où ils divergent

D'accord : l'alternative gratuite (groupe WhatsApp + bénévole) est le vrai concurrent ; la confiance (données, qui est derrière, aucun pair) bloque avant le prix ; l'effort d'entrée (import, consentements) tue l'adoption ; la distribution passe par une union, pas par de la publicité. Divergence : la lentille Offres pensait qu'une offre assez forte justifiait 79 € ; le panel a fixé le plafond de refus à 40 € pour les petites et moyennes assemblées, et seules les grandes tolèrent 49 à 59 €. Le conseil voyait le CRM comme le rempart ; le panel voit la liste des membres comme un risque à confier. Les deux ont raison : le CRM n'est un rempart qu'une fois la confiance acquise.

## Le plus grand risque, et ce qui est prévu

**La classification Meta des messages WhatsApp.** Si le rappel du culte est classé « marketing » (0,0859 $) au lieu de « utility » (0,030 $), le forfait inclus coûte 24,50 € au lieu de 9,74 € par église-mois, la contribution tombe à 3,41 € et le seuil à 95 églises : le modèle meurt. Prévu : trois gabarits réels soumis à Meta le 8 janvier 2027, verdict avant le 29 janvier ; si tout n'est pas « utility », forfait exprimé en euros et bascule SMS avant le 18 février, sinon retour à `/founder-pricing` et report (`founder/launch.md`, `founder/ops.md`). Second verrou : l'AIPD et le contrat de sous-traitance pour des données de conviction religieuse, à faire valider par un juriste avant la première église payante.

## Ce dont le fondateur a besoin pour démarrer

- **5 186 € de trésorerie** avant que l'affaire ne se paie (3 685 € de démarrage dont 1 500 € d'avis juridique, plus le creux des six premiers mois), et la capacité de vivre sans salaire de l'activité pendant l'année 1.
- **Le premier test réel** (`founder/launch.md`) : 20 pasteurs d'assemblées de 150 à 300 membres rencontrés du 11 janvier au 28 février 2027, dossier du conseil et prix en main ; succès si **au moins 5 sur 20 paient un premier trimestre fondateur avant le 28 février 2027**. Deux ou moins : « Pas encore », retour à l'offre ou au prix selon les refus.
- Un K-bis avant le 8 janvier 2027 (Twilio et Meta l'exigent), le dépôt INPI, et une union qui accepte un pilote de trois églises avant le 23 mars 2027.

## La chose à faire cette semaine

Déposer la création de la SASU au guichet unique de l'INPI (prévu le 2 décembre 2026) : tout le chemin critique (numéro français, vérification Meta, premier paiement) part du K-bis. En parallèle, rédiger les trois gabarits WhatsApp en style « utility » pour les soumettre dès que le compte Meta est vérifié.

---

Les acheteurs sont simulés et les chiffres sont des projections : de vrais pasteurs et de vrais devis les confirment. Ni conseil financier, ni juridique, ni fiscal.
