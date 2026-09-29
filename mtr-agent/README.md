# mtr-agent

Agent en Python (connecteurs et sondes en bibliothèque standard) qui collecte l'état des salles
Microsoft Teams Rooms et de leurs périphériques, et l'expose au format Prometheus
pour Grafana.

## Structure

- `mtr_agent/models.py` : `DeviceStatus`, `CollectResult` (état brut remonté par les connecteurs).
- `mtr_agent/mesures.py` : conversion vers `MesureEquipement`, le modèle de l'exporteur (`mtr_agent/exporter/`).
- `mtr_agent/exporter/` : exporteur Prometheus protégé par mot de passe (voir son README).
- `mtr_agent/config.py` : réglages lus depuis l'environnement (`MTR_<VENDOR>_*`), jamais dans le code.
- `mtr_agent/probes/` : sondes HTTP (disponibilité, temps de réponse, débit) et réseau (perte, latence, gigue, échecs TCP).
- `mtr_agent/connectors/` : un connecteur par équipement ou service, tous dérivés de `base.py`.

## Connecteurs

| Connecteur | API | État de la correspondance |
|---|---|---|
| teams | Microsoft Graph `/teamwork/devices` | API documentée |
| teams_pro | Graph `/teamwork/devices/{id}/health` (le portail Pro n'a pas d'API publique) | API documentée |
| cisco | Webex `/v1/devices`, `/v1/workspaces` | API documentée |
| poly | Poly Lens GraphQL | requête à valider sur le tenant |
| grafana | `/api/health` | API documentée |
| sony | BRAVIA Pro REST (`getPowerStatus`, `getSystemInformation`) | API documentée |
| neat | Neat Pulse | champs à confirmer |
| jabra | Jabra Plus | champs à confirmer |
| lenovo | ThinkSmart Manager | champs à confirmer |
| ochno | Ochno Cloud | champs à confirmer |
| zebrix | Zebrix | champs à confirmer |
| sylphony | Sylphony | champs à confirmer |

Les connecteurs « champs à confirmer » héritent de `RestInventoryConnector` : seule
leur table `fields` (et le chemin d'inventaire) change quand la documentation
constructeur est disponible.

Tous les connecteurs sont en lecture seule : aucune donnée de l'agent n'est envoyée à un tiers.

## Tests

```bash
cd mtr-agent
python3 -m pip install pytest -r requirements-exporter.txt
python3 -m pytest
```

Les tests utilisent un faux client HTTP avec des réponses API simulées ; aucun appel réseau.
