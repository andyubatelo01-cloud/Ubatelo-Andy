# Le prix — Bureau du Pasteur

Trois sources, toutes vérifiables : ce que les acheteurs simulés ont dit (`founder/pricing-curve.md`, 20 réponses complètes), ce que les concurrents facturent (`founder/competitors.md`), ce que l'entreprise doit gagner (`founder/numbers.json`, outil du CFO).

## 1. Le prix recommandé, et pourquoi

**Abandon du prix unique de 39 € HT. Trois formules par taille d'église : 19 € HT, 29 € HT, 49 € HT par mois, tout compris, sans facturation SMS surprise.**

### Ce que les acheteurs ont dit (pitch v1, prix unique 39 € HT = 46,80 € TTC)

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

### Ce que les concurrents facturent (pour ~200 membres, par mois)

Offres en euros pour une église locale : **plus bas 29 €** (Ecclo ; Eliakim jusqu'à 50 utilisateurs), **médiane 50 €** (Church Manager, Enoria), **plus haut 59 €** (Eliakim Croissance). ChurchTools 54 €. En dollars : ChMeetings 25 $ (≤ 250 personnes), Text In Church 30 $ (1 250 SMS inclus). Gratuits : B1.church, Planning Center People, le groupe WhatsApp. Les expéditeurs SMS grossistes (smsmode, Octopush) sont à 9 €/mois + 0,045 € par SMS. Détail et liens : `founder/competitors.md`, section 2.

Lecture : le marché euro des logiciels d'église se situe entre 29 € et 59 €, mais ces outils vendent d'abord une base de membres avec dons et reçus fiscaux. Bureau du Pasteur vend la communication validée et le suivi ; il se compare, pour le pasteur, au groupe WhatsApp gratuit et à Ecclo à 29 €, pas à Eliakim à 59 €.

### Ce que l'entreprise doit gagner (outil du CFO, `numbers.json`)

| Prix moyen testé | Contribution par église-mois | Seuil de rentabilité (églises) | Marge au plan (60 églises) |
|---|---|---|---|
| 19 € (v1, coûts v1) | 9,76 € | 32 | 25 % |
| 25 € | 15,76 € | 20 | 43 % |
| 29 € | 19,76 € | 16 | 51 % |
| 39 € (hypothèse de départ) | 29,76 € | 11 | 63 % |
| **30 € (moyenne pondérée des trois formules, coûts v2 avec WhatsApp inclus)** | **17,71 €** | **18** | **42 %** |

À 30 € de prix moyen, le seuil de rentabilité est 18 églises abonnées et la marge au plan 42 % (`founder/cfo.md`). Le coût qui pèse est le forfait WhatsApp inclus (9,74 € en moyenne si le forfait est entièrement consommé) : c'est le prix de la promesse « un seul chiffre pour le conseil ». Sans lui, la facture variable revient et avec elle l'objection n° 6 du panel.

## 2. L'échelle

| Formule | Taille | HT / mois | TTC / mois | Inclus | Pourquoi monter d'un cran |
|---|---|---|---|---|---|
| **Petite assemblée** | jusqu'à 100 membres | **19 €** | 22,80 € | 100 messages WhatsApp, e-mail illimité, partage dans votre groupe WhatsApp, suivi des absents, rappels préparés | — |
| **Assemblée** | 101 à 200 membres | **29 €** | 34,80 € | 300 messages WhatsApp + tout ce qui précède | Plus de membres = plus de messages inclus ; même prix que l'entrée de gamme concurrente (Ecclo) |
| **Grande assemblée** | 201 à 300 membres | **49 €** | 58,80 € | 600 messages WhatsApp, plusieurs responsables (rôle secrétaire pour les bénévoles), double validation | Sous la médiane concurrente (50 à 59 €) avec une promesse qu'aucun concurrent ne fait |

SMS en option, au coût réel (0,08 € l'unité, arrondi au-dessus du tarif Twilio de 0,0798 $), sous un **plafond mensuel fixé par l'église** (0 € par défaut). Au-delà du forfait WhatsApp, rien ne part sans accord explicite : le chiffre annoncé au conseil est le chiffre payé.

Paiement annuel : deux mois offerts (soit 190 €, 290 €, 490 € HT par an). Les associations préfèrent une ligne budgétaire annuelle votée une fois.

Position de chaque formule dans la fourchette du panel : 22,80 € TTC est au niveau « commence à être cher » des petites assemblées (20 à 25 €), sous leur refus (30 à 40 €). 34,80 € TTC est au niveau « cher mais possible » des assemblées moyennes (25 à 30 €... à 40). 58,80 € TTC est dans la zone « cher mais possible » des grandes (45 à 60 €), sous leur refus (70 à 90 €). Aucune formule n'est au-dessus du seuil de refus de son segment ; aucune n'est en dessous du PMC.

## 3. L'offre d'ouverture

**Les 10 églises fondatrices** : moitié prix à vie (9,50 €, 14,50 €, 24,50 € HT) pour les dix premières églises, en échange d'un appel de retour mensuel de 20 minutes et, si elles le souhaitent, d'un témoignage nommé. Fermeture quand la dixième est installée, pas de date artificielle. Ce n'est pas une remise qui apprend à attendre les soldes : c'est le prix d'un travail (les retours) que personne d'autre ne fournira, et il ne reviendra pas.

Pas de « premier mois gratuit » : le panel v1 l'a ignoré (deux acheteurs sur vingt l'ont cité, dix-huit non) et il attire des essais sans intention. À la place, **satisfait ou remboursé 60 jours**, qui répond à la peur (« et si ça ne marche pas ») sans dévaloriser le prix.

## 4. Ce qu'il faut tester avec de vrais pasteurs

1. **19 € contre 25 € HT pour la Petite assemblée**, sur deux pages d'inscription identiques présentées en alternance aux pasteurs rencontrés dans les rassemblements d'unions (20 pasteurs chacune). Mesure : part qui demande le dossier pour le conseil, part qui s'inscrit sous 30 jours.
2. **49 € contre 39 € HT pour la Grande assemblée**, même méthode. Le panel laisse penser que 49 € passe ; le conseil (lentille Offres) demande si 79 € passerait : tester 49 € d'abord, 69 € si la Grande assemblée convertit au-dessus de 20 %.
3. **Paiement annuel avec deux mois offerts** proposé ou non à l'inscription : mesure la part qui choisit l'annuel (objectif : plus de la moitié, pour la trésorerie).

Critère de décision écrit avant le test : si moins de 3 pasteurs sur 20 s'inscrivent à 19 €, le problème n'est pas le prix mais la confiance (voir `founder/offer.md`) et c'est le programme des fondatrices qui doit passer en premier.

## 5. Les objections de prix, mot pour mot (panel v1)

1. « 46,80 € par mois, c'est presque 600 € par an sur un budget où chaque ligne est discutée au conseil. » (P003)
2. « Je ne vais pas aller devant le conseil défendre 47 € par mois, soit plus de 560 € par an, pour un outil qui fait ce que je fais déjà gratuitement. » (P004)
3. « Il faudrait un tarif petites églises autour de 15 € pour que le conseil dise oui. » (P006) ; « Un prix tout compris avec les SMS plafonnés et clairement annoncés, autour de 20 € par mois. » (P008)

Le marketing doit répondre aux trois : le coût annuel dit en clair (190 € HT par an pour une petite assemblée), ce que le conseil obtient en échange (le dossier RGPD, les absents retrouvés), et « un seul chiffre, jamais dépassé ».

## Règles

- Les réponses de prix viennent d'acheteurs simulés ; elles désignent ce qu'il faut tester, pas une preuve. Les tests du point 4 tranchent.
- Aucune formule n'est vendue sous son coût variable : la contribution la plus faible (Petite assemblée, forfait WhatsApp entièrement consommé) reste positive (19 € − 4,84 € = 14,16 € HT).
- Aucun faux prix barré : 39 € n'a jamais été facturé et n'apparaîtra nulle part comme « ancien prix ».
- TVA : prix HT, TVA 20 % en sus ; la plupart des églises la paient sans la récupérer, d'où les prix TTC affichés à côté. Un expert-comptable confirme le régime.

`founder/numbers.json` a été mis à jour avec le prix moyen pondéré de 30 € HT et les coûts des forfaits WhatsApp ; `/founder-cfo` est relancé dans `founder/cfo.md`.
