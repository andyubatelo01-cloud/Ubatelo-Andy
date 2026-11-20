# Le conseil d'administration — Bureau du Pasteur

Réuni le 2026-11-20 sur le brief `founder/board/brief.md`. Trois mémos : `founder/board/offers.md`, `founder/board/monopoly.md`, `founder/board/product.md`.

## 1. Le vote

**3 FUND IF, 0 FUND, 0 PASS. Score moyen : 5,3 / 10** (Offres 5, Monopole 5, Produit 6).

Personne ne passe, personne ne finance en l'état. Les trois lentilles disent la même chose avec des mots différents : le produit est réel et son cœur (« rien ne part sans le pasteur ») est bon ; ce qui manque, ce sont des acheteurs qui paient et un chemin pour les atteindre.

## 2. Les risques soulevés par plus d'un membre (en premier)

| Risque | Qui le soulève | En une phrase |
|---|---|---|
| **L'alternative est gratuite et déjà dans la poche du pasteur** (groupe WhatsApp + tableur + assistant IA grand public) ; la disposition à payer 39 € n'est prouvée par rien. | Offres (n° 1), Monopole (n° 2) | La douleur est une corvée, pas une hémorragie ; le budget logiciel de la cible est inconnu. |
| **L'effort d'entrée tue l'adoption** : import, dédoublonnage, consentements datés, compte Twilio, SMTP, clé API avant le premier message. | Offres (n° 3), Produit (n° 2) | Les cinq premières minutes se passent dans les coutures entre systèmes ; chaque couture est un abandon possible. |
| **Pas de distribution et pas de preuve sociale** : fondateur seul, budget quasi nul, aucun pasteur utilisateur. | Monopole (n° 1), Offres (n° 2) | « Bouche-à-oreille entre pasteurs » décrit un espoir, pas un canal ; un pasteur ne confie pas la voix de son église sans qu'un pair l'ait fait avant. |
| **Le produit dépend de canaux qu'il ne possède pas** (Twilio, Meta, SMTP) et le pasteur devrait aujourd'hui les configurer lui-même. | Produit (n° 3 et condition 3), Offres (n° 3) | Un gabarit WhatsApp refusé ou un e-mail en spam retombe sur le produit. |

Risques portés par un seul membre, à garder : la vitrine « sept agents » vend une boîte à outils et non une promesse (Produit n° 1) ; la position n'est pas défendue à dix ans face à un éditeur installé qui ajouterait un module IA en français (Monopole n° 3).

## 3. Les conditions, fusionnées, en liste à cocher

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

## 4. La version la plus forte de cette entreprise, vue par le conseil

Ce n'est pas tout à fait ce que le fondateur a présenté. Le fondateur vend un « bureau d'IA à sept agents » ; le conseil voit une entreprise plus étroite et plus solide : **le service clés en main qui envoie le rappel du culte et retrouve les absents, en français, avec le consentement de chaque membre, sans que le pasteur ait rien à configurer et sans qu'un seul message parte sans son pouce.** Le numéro d'envoi, WhatsApp et l'e-mail sont fournis et compris dans le prix ; l'IA est invisible ; le CRM des membres avec ses consentements est la mémoire de l'église et la raison de rester. La distribution ne se fait pas par de la publicité mais par une union d'églises ou un réseau de pasteurs qui recommande l'outil, après trois pilotes nommables. Le désaccord subsiste sur le prix : la lentille Offres pense qu'une offre assez forte justifie 79 € et plus ; la lentille Monopole craint que la cible ne paie pas 39 € ; seuls des pasteurs réels trancheront.

## Désaccords conservés

- **Sur le prix** : Offres pousse vers le haut (« à 79 €, seriez-vous encore le choix évident ? »), Monopole vers le bas (« rien ne prouve qu'un pasteur de 80 membres paie 39 € »).
- **Sur ce qui protège l'entreprise** : Monopole mise sur le CRM rempli et la recommandation institutionnelle ; Produit sur la qualité de l'expérience de bout en bout ; Offres sur la preuve sociale et la garantie.
- **Sur la richesse fonctionnelle** : Offres y voit « une pile déjà épaisse » (un atout) ; Produit y voit un produit qui « n'a pas encore dit non » (un risque).

---

*Vote : 3 « financer sous conditions », score moyen 5,3/10.* Étape suivante : `/founder-competitors` (C2, en cours) puis `/founder-consumer` (C1).
