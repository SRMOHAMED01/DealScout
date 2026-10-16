# governance/ — OpenMetadata (Palier H)

## État : implémenté (recette + ligne de données)

La gouvernance OpenMetadata est désormais configurée :

- `metadata_config.yml` — déclaration des sources de données (Kafka, MinIO bronze, Parquet silver, Postgres Gold)
- `openmetadata_lineage.json` — lignée de bout en bout (source → Kafka → Bronze → Silver → Gold → API → UI)
- `openmetadata/ingestion_recipe.yaml` — recette d'ingestion OpenMetadata (MinIO, Postgres, Airflow, lignée)
- `openmetadata/README.md` — documentation d'utilisation

## Lignée de données (déjà définie)
`governance/openmetadata_lineage.json` décrit les arêtes :
  source.company_generator → Kafka topics → Bronze (MinIO) → Silver (Spark/Parquet)
  → Gold (dbt : company_360, investment_targets, market_analysis)
  → FastAPI endpoints → React Dashboard

## Utilisation
1. Déployer OpenMetadata.
2. Créer les services dans l'UI (MinIO, Postgres Gold, Airflow).
3. Exécuter l'ingestion :
   `openmetadata-ingest --config governance/openmetadata/ingestion_recipe.yaml`
