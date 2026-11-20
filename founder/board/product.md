# Lentille Produit
Score: 6/10 | Vote: FUND IF

## Ce qui est fort
- La lentille Produit cherche la seule chose que le produit doit faire brillamment. Elle existe : « rien ne part sans le pasteur ». Le moteur à états (brouillon → contrôles → aperçu → validation → envoi → rapport), le silence qui n'est jamais un oui, la phrase « CONFIRMER L'ENVOI » au-delà de 100 destinataires et l'empreinte SHA-256 du contenu validé forment un cœur cohérent.
- La validation depuis le téléphone (lien à usage unique, mot de passe, Valider / Modifier / Annuler) part du bon moment : le pasteur approuve un SMS en vingt secondes entre deux visites.
- Le suivi pastoral ne propose des recontacts qu'à partir de faits enregistrés, sans rien inventer : une retenue de bon goût.
- Livré, testé (51 tests dont la preuve de non-envoi), fonctionnel sans IA grâce aux gabarits.

## Ce qui pourrait le tuer (les 3 principaux, le plus dangereux d'abord)
1. **Sept agents, dix types de message, sept styles : le produit n'a pas encore dit non.** Un pasteur de 80 membres ne veut pas six agents et un tableau de bord ; il veut envoyer le rappel du culte et savoir qui manque depuis trois semaines. Si le pitch a besoin d'un paragraphe, le produit n'est pas clair. Sept agents en vitrine vendent une boîte à outils, pas une promesse.
2. **Les cinq premières minutes se passent dans les coutures.** Avant le premier message, le pasteur doit importer un répertoire iPhone ou un export WhatsApp, dédoublonner, comprendre les consentements datés, disposer d'un compte Twilio, d'un SMTP, peut-être d'une clé API. Chaque passage entre systèmes est un endroit où il abandonne avant le premier « Valider ».
3. **La promesse de maîtrise repose sur des canaux que le produit ne possède pas.** Lien de validation, SMS, WhatsApp, e-mail : tout passe par Twilio et SMTP. Numéro bloqué, gabarit WhatsApp refusé, e-mail en spam : la faute retombe sur le produit. Posséder l'expérience, c'est posséder aussi le rapport de livraison et le message d'erreur que lit le pasteur.

## Les questions que je poserais au fondateur
- En une phrase, pour un pasteur, que fait le produit ? Si elle contient « sept agents », recommencez.
- Racontez les cinq premières minutes d'un pasteur avec un iPhone et un groupe WhatsApp de 120 personnes. Combien de pasteurs réels ont atteint leur premier message livré sans vous au téléphone ? (question ouverte : /founder-consumer)
- Que coupez-vous en premier : le Directeur IA, les 7 styles, le rétroplanning J-14→H-3, les groupes dynamiques, l'anonymisation en lot, la version Docker ? Lesquels ont été demandés par un pasteur, lesquels par le développeur ?
- Qui fournit le numéro d'envoi et le compte Twilio ? Quel coût réel par église et par mois hors des 39 € ? (question ouverte : /founder-cfo)
- Que paient aujourd'hui les églises de 50 à 300 membres déjà équipées, et pour quoi ? (question ouverte : /founder-competitors)

## Si FUND IF : les conditions
1. Réduire la promesse à un geste : « le rappel du culte et le suivi des absents, validés depuis votre téléphone ». Les sept agents deviennent des fonctions internes, pas la vitrine.
2. Un parcours d'entrée en un seul import (export WhatsApp ou vCard) jusqu'au premier message validé, mesuré sur dix pasteurs réels sans assistance, temps et point d'abandon notés (/founder-consumer).
3. Le produit fournit le numéro et le canal : aucun compte Twilio, SMTP ou clé API à créer par le pasteur ; coûts chiffrés et intégrés au prix (/founder-cfo).
4. Une liste écrite de ce qui disparaît de l'interface à la prochaine version.
