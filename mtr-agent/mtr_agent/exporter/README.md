# Exporteur Prometheus pour Grafana

Expose sur `/metrics` les métriques obligatoires du cahier de test des salles,
par salle et par équipement (labels `salle`, `equipement`, `constructeur`, `type`).

| Métrique | Unité |
|---|---|
| `mtr_device_online` | 1 = en ligne selon le connecteur |
| `mtr_device_present` | 1 = périphérique détecté dans la salle |
| `mtr_device_health{etat="ok\|avertissement\|critique\|inconnu"}` | 1 pour l'état courant |
| `mtr_http_up` | 1 = joignable, 0 = injoignable |
| `mtr_http_response_seconds` | secondes |
| `mtr_http_throughput_bytes_per_second` | octets/s |
| `mtr_packet_loss_ratio` | 0 à 1 |
| `mtr_latency_seconds` | secondes |
| `mtr_jitter_seconds` | secondes |
| `mtr_tcp_connect_failures_total` | compteur |
| `mtr_cpu_usage_ratio` | 0 à 1 |
| `mtr_memory_usage_ratio` | 0 à 1 |

Plus `mtr_exporter_scrape_success`, `mtr_exporter_scrape_duration_seconds` et `mtr_exporter_devices`.

## Lancer en local avec des données simulées

```bash
cd mtr-agent
pip install -r requirements-exporter.txt
export MTR_EXPORTER_PASSWORD='un-mot-de-passe-long'   # dev uniquement
python -m mtr_agent.exporter --simulation
curl -u prometheus:"$MTR_EXPORTER_PASSWORD" http://127.0.0.1:9469/metrics
```

## Sécurité

- L'exporteur **refuse de démarrer** sans mot de passe. Aucun secret dans le code.
- En production, utiliser un hachage : `python -m mtr_agent.exporter hacher-mot-de-passe`,
  puis placer la valeur dans `MTR_EXPORTER_PASSWORD_HASH` (variable d'environnement ou coffre).
- Écoute sur `127.0.0.1` par défaut. Hors localhost, activer TLS avec
  `MTR_EXPORTER_TLS_CERT` et `MTR_EXPORTER_TLS_KEY` (sinon avertissement au démarrage).
- Après 5 échecs d'authentification en 5 minutes, l'IP est bloquée 15 minutes (HTTP 429).
- Seul `GET` est accepté ; `/healthz` répond `ok` sans aucune donnée.
- L'exporteur ne pousse rien : il ne répond qu'au Prometheus authentifié qui l'interroge.

## Brancher les connecteurs

L'exporteur consomme une `SourceMesures` : tout appelable qui renvoie des
`MesureEquipement` (voir `model.py`). Chaque connecteur n'a qu'à convertir son
état en `MesureEquipement` ; un champ laissé à `None` n'est simplement pas exposé.

## Grafana

- Tableau de bord : `mtr-agent/grafana/tableau-de-bord-mtr.json` (Grafana ≥ 10,
  menu Dashboards › Import, choisir la source Prometheus). Filtres par salle et équipement.
- Configuration Prometheus : `mtr-agent/grafana/prometheus.exemple.yml`.
