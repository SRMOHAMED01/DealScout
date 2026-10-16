# OpenMetadata — Connecteur DealScout (Palier H / Gouvernance)

Ce dossier contient la recette d'ingestion OpenMetadata pour DealScout.

## Contenu
- `ingestion_recipe.yaml` : recette qui connecte OpenMetadata à :
  - MinIO (buckets bronze & silver — stockage Data Lakehouse)
  - PostgreSQL (entrepôt Gold : company_360, investment_targets, market_analysis)
  - Airflow (DAG dealscout_daily_pipeline — orchestration)
  - Lignée de bout en bout (`governance/openmetadata_lineage.json`)

## Lignée de données (déjà définie)
Le fichier `governance/openmetadata_lineage.json` décrit déjà les arêtes de
lignée complètes :
  source.company_generator → Kafka topics → Bronze (MinIO) → Silver (Spark/Parquet)
  → Gold (dbt : company_360, investment_targets, market_analysis)
  → FastAPI endpoints → React Dashboard

## Utilisation
1. Déployer OpenMetadata (docker-compose dédié ou binaire).
2. Créer les services dans l'UI OpenMetadata (MinIO, Postgres, Airflow).
3. Exécuter l'ingestion :
   `openmetadata-ingest --config governance/openmetadata/ingestion_recipe.yaml`

## Prérequis
- OpenMetadata serveur accessible
- Connecteurs S3, Postgres, Airflow installés côté OpenMetadata
