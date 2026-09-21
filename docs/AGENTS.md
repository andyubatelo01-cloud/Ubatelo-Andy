# Les agents du Bureau d'IA

Tous les agents partagent une charte (`agents/base.py`) : assister le pasteur, préparer sans envoyer, ne jamais prétendre connaître l'état spirituel, émotionnel ou médical d'une personne, travailler uniquement à partir d'informations explicitement enregistrées, écrire en français clair et court, demander ce qui manque plutôt qu'inventer.

Chaque intervention est tracée dans `agent_runs` (agent, commande, intention, résumé, fournisseur IA) et visible dans 🤖 Agents IA.

## 🤖 DIRECTEUR IA (`directeur.py`)

Chef d'orchestre. Reçoit une demande en langage naturel et :

1. l'analyse (mots-clés français, jours de la semaine, horizons « deux prochaines semaines », styles, canaux, groupes connus, indice d'événement) ;
2. si l'intention reste inconnue et qu'un modèle est configuré, demande une extraction structurée (`ParsedIntent`) ;
3. mobilise les agents : recherche l'événement, identifie le public, rédige, crée la campagne, lance les contrôles ;
4. présente l'aperçu et **attend la validation**.

Intentions : `plan_event`, `invitation`, `rappel`, `unconfirmed`, `encouragement`, `followup`, `birthday`, `welcome`, `monthly`, `briefing`, `sunday`, `pending`, `upcoming_events`, `agenda`, `task`, `unknown` (réponse d'aide).

## 👔 SARAH (`sarah.py`) — secrétaire

Tâches (priorités 🔴 🟠 🟡 🟢), agenda, trame de compte rendu, synthèse « urgent / aujourd'hui / cette semaine / en attente de validation », détection des urgences (responsables manquants, capacité atteinte, campagne à valider sous 24 h).

## 📢 COMMUNICATION (`communication.py`)

Dix types de message (invitation, rappel, motivation, rappel pratique, remerciement, encouragement, bienvenue, anniversaire, message du mois, annonce) × sept styles (chaleureux, pastoral, motivant, évangélisation, événementiel, administratif, rappel urgent). Les gabarits utilisent `{PRENOM}`, `{EVENEMENT}`, `{DATE}`, `{HEURE}`, `{LIEU}` ; sans événement, les variables d'événement sont retirées pour ne pas bloquer la campagne. Avec Claude, le gabarit sert d'exemple de ton et le modèle propose une rédaction, contrainte par la longueur du canal.

## ❤️ BERGER (`berger.py`) — suivi pastoral

Propose au pasteur les personnes à contacter, avec le **fait** qui motive la proposition : « dernière présence enregistrée : dimanche 16 août », « arrivé(e) il y a 12 jours », « anniversaire dans 3 jours ». Prépare des messages individuels (1 destinataire) ou une relance groupée des absents ; les deux passent par le moteur de campagnes et attendent la validation.

## 👥 MEMBRES (`membres_agent.py`)

Fiche CRM (section 10 du cahier des charges) avec les cinq actions, résumé de groupe, groupes dynamiques.

## 📅 EVENTS (`events_agent.py`)

Pour chaque événement : description complète, informations manquantes, statistiques d'inscription et de présence, calendrier de communication et génération des campagnes :

| Étape | Message | Envoi |
|---|---|---|
| J-14 | Invitation | 9 h |
| J-7 | Rappel | 9 h |
| J-3 | Message de motivation | 9 h |
| J-1 | Dernier rappel | 9 h |
| H-3 | Rappel pratique | 3 h avant |
| Après | Remerciement | +20 h |

Culte du dimanche : J-4 (mercredi) invitation, J-1 (samedi) rappel, H-3 infos pratiques, après-culte remerciement. Les étapes déjà passées ou déjà préparées sont ignorées (aucun doublon).

## 📊 TABLEAU DE BORD (`analytics.py`)

Membres (total, actifs, nouveaux, à recontacter, groupes, consentements), communication (préparées, à valider, bloquées, validées, programmées, envoyées, annulées, expirées, messages du mois, taux de participation sur 90 jours lorsque des présences sont enregistrées), événements, tâches du pasteur, rapport détaillé par campagne.

## 🔐 SÉCURITÉ / CONFORMITÉ

Agent transversal : il n'a pas de classe propre, ses règles sont appliquées par le moteur (`campaign_engine`, `preflight`, `members`, `security`, `audit`). Voir `SECURITE_RGPD.md`.
