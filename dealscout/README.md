# DealScout — M&A Intelligence Platform

Plateforme de détection et scoring automatique d'opportunités d'acquisition
et d'investissement. Architecture Data Lakehouse (Bronze/Silver/Gold) +
Scoring Engine (règles métier puis ML/SHAP) + Dashboard décisionnel React.

## Structure du projet

- `ingestion/`          → Connecteurs sources (API/scraping/news) + producers Kafka
- `bronze/`               → Convention de stockage brut (MinIO/S3)
- `spark_jobs/`            → Jobs Spark Bronze → Silver
- `silver/`                 → Convention de stockage nettoyé (Parquet)
- `dbt_project/`             → Modèles dbt Silver → Gold (company_360, investment_targets...)
- `scoring_engine/`            → Scoring M&A v1 par règles métier pondérées
- `ml/`                          → Modèle prédictif XGBoost + explicabilité SHAP
- `backend/`                       → API FastAPI (companies, score, search)
- `frontend/`                        → Dashboard React (KPIs, classement, fiche entreprise)
- `orchestration/`                     → DAGs Airflow (pipeline quotidien)
- `data_quality/`                        → Suites Great Expectations
- `governance/`                            → Config OpenMetadata
- `observability/`                          → Prometheus + Grafana
- `docs/GUIDE_COMPLET.md`                     → Guide de construction détaillé, palier par palier

## Comment démarrer

Lis `docs/GUIDE_COMPLET.md` en premier — il explique l'ordre de construction
(Palier A à H) et pourquoi commencer par un scoring à règles avant le ML.

## Démarrage rapide (une fois le code écrit)

```bash
cp .env.example .env
docker-compose up
```

## Positionnement dans la suite portfolio

```
LedgerLake   → Data Foundation
CreditPulse  → Credit Risk Decision Engine
DealScout    → Investment & M&A Intelligence Engine   (ce projet)
```
