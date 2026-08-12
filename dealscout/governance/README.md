# governance/ — OpenMetadata (Palier H)

À IMPLÉMENTER : mêmes principes que LedgerLake.
1. Connecter OpenMetadata à MinIO, PostgreSQL (Gold) et Airflow
2. Documenter investment_targets : owner ("M&A / Investment Team"),
   source (Crunchbase/API -> Kafka -> Bronze -> Spark -> Silver -> dbt),
   tags de sensibilité si données financières confidentielles

Objectif : retrouver dans l'UI OpenMetadata la lignée complète de
investment_targets, visible graphiquement (data lineage).
