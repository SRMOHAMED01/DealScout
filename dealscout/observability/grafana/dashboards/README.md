# Dashboards Grafana (Palier H)

Deux dashboards provisionnés et importables dans Grafana (Configuration → Data Sources → Prometheus, puis Create → Import) :

1. `dashboard_business.json` : entreprises analysées, cibles prioritaires, score M&A moyen, score par secteur, top opportunités.
2. `dashboard_technique.json` : latence API (p95), taux d'erreur, Kafka lag, DAG Airflow, durée des jobs Spark, requêtes API par endpoint.

Ces dashboards consomment les métriques exposées par `prometheus_fastapi_instrumentator` (endpoint `/metrics` du backend) et les exports Kafka / Airflow.
