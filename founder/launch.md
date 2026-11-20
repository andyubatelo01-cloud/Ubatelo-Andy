# Le lancement — Bureau du Pasteur

Méthode : `.claude/skills/founder-launch/SKILL.md`. Rédigé le 2026-11-20. Lancement public : **dimanche 7 mars 2027** (`founder/marketing.md`). Chiffres repris sans modification de `pricing.md`, `numbers.json`, `cfo.md`, `ops.md`, `marketing.md`, `brand.md`. Aucun pasteur, aucune union, aucune église n'est nommée : rien n'est acquis. Pas un avis juridique ni comptable.

Rôles : **F** = le fondateur (seul, développeur) · **J** = le juriste (RGPD art. 9, AIPD, DPA, CGV ; 1 500 € estimés) · **EC** = l'expert-comptable (99 € HT/mois) · **EA** = l'église amie (une assemblée du réseau du fondateur, 5 bénévoles volontaires, non cliente : le banc d'essai).

## 1. Tester avant de dépenser

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

### Les trois pré-tests techniques

| | Test | Pourquoi | Quand | Succès |
|---|---|---|---|---|
| **(a)** | **Classification Meta de trois gabarits réels** (rappel du culte, demande de consentement, changement d'horaire) soumis via Twilio | « Marketing » (0,0859 $ au lieu de 0,030 $) ramène la contribution de 18,17 € à **3,41 €** et le seuil à **95 églises**, au-dessus de la capacité de 60 (`cfo.md`) | Soumission 08/01 ; verdict et réécritures jusqu'au **29/01** | Trois gabarits **« utility »** ; sinon forfait inclus en euros, repli SMS sous plafond, `/founder-pricing` avant le 05/02 |
| **(b)** | **Bout en bout sur l'EA** : import (vCard ou export WhatsApp) → consentement → validation depuis le téléphone → rappel du samedi 18 h à 5 bénévoles → présences en un geste le dimanche | C7 : temps réel et point d'abandon ; rien aux non-consentants (`test_approval_invariant.py`) | Samedis **06/02, 13/02, 20/02** | Installation ≤ 45 min (0,75 h de `ops.md`), 5 livrés sur 5, 0 sans consentement, 0 sans validation |
| **(c)** | **AIPD et DPA relus par J**, avec le registre sous-traitant et les CGV | Art. 9 ; `ops.md` : AIPD très probablement requise, avant la première église payante | Brouillons F 11/12 et 18/12 ; retour J 08/01 ; **final 29/01** | J écrit « prêt à signer » ; DPA signé par chaque église avant son import |

## 2. Le compte à rebours (23/11/2026 → 07/03/2027)

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

## 3. Le jour du lancement : dimanche 7 mars 2027

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

## 4. Les trente premiers jours (07/03 → 06/04)

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
