# Monitoring Stack

Services included (scaffolding):

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (credentials: admin / admin on first run)
- Node Exporter (host metrics)
- cAdvisor (container metrics)
- Placeholder app-metrics service (replace with your real metrics endpoint)

## Quick Start

```powershell
# From repo root
docker compose up -d prometheus grafana node-exporter cadvisor app-metrics

# Or bring everything up
docker compose up -d
```

## Data Source
Grafana auto-provisioned Prometheus datasource via `grafana-provisioning-datasources.yml`.

## Next Steps
- Replace `app-metrics` container with your application exposing /metrics.
- Add alerting rules file and mount into Prometheus.
- Add dashboards JSON exports under `monitoring/dashboards/` and provision them.
