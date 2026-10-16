# DealScout — M&A Intelligence Platform

Plateforme de détection et scoring automatique d'opportunités d'acquisition
et d'investissement. Architecture Data Lakehouse (Bronze/Silver/Gold) +
Scoring Engine (règles métier puis ML/SHAP) + Dashboard décisionnel React.

---

## 📊 État d'avancement par Palier

| Palier | Composant | Description | Statut |
|---|---|---|---|
| **A** | **Ingestion & Bronze** | Générateur d'entreprises réalistes, connecteurs (DB, Financial, News), Kafka producers standardisés avec enveloppe, consumer Bronze partitionné MinIO/Local | **Implemented** ✅ (100%) |
| **B** | **Silver (Spark / Parquet)** | Nettoyage, standardisation pays/secteurs, dédoublonnage, ratios financiers, sentiment agrégé, stockage Parquet PyArrow | **Implemented** ✅ (100%) |
| **C** | **Gold (dbt)** | Modèles SQL analytiques (`company_360`, `investment_targets`, `market_analysis`) + tests unitaires + profiles | **Implemented** ✅ (100%) |
| **D** | **Scoring Engine v1** | Formule de scoring M&A pondérée déterministe (0-100), ranking, recommandations et explications détaillées (forces / risques) | **Implemented** ✅ (100%) |
| **E** | **Machine Learning** | Modèle prédictif `XGBClassifier`, entraînement, évaluation (ROC-AUC), sauvegarde de modèle et explicabilité locale SHAP (`TreeExplainer`) | **Implemented** ✅ (100%) |
| **F** | **Backend FastAPI** | Endpoints REST (`/companies`, `/companies/{id}`, `/companies/{id}/score`, `/companies/{id}/ml-score`, `/search`, `/market-analysis`, `/health`, `/metrics`, `/auth/token`) + auth JWT + persistance Postgres | **Implemented** ✅ (100%) |
| **G** | **Frontend React** | Dashboard KPIs, Top opportunités, Recherche multi-critères, Profil entreprise 360, graphique décomposition score + explicabilité ML (SHAP), page de connexion, persistance token | **Implemented** ✅ (100%) |
| **H** | **Orchestration & DevOps** | DAG quotidien automatisé, validation Data Quality, `docker-compose.yml` multi-services (kafka-exporter, dbt), scraping Prometheus, dashboards Grafana provisionnés, recette OpenMetadata, CI/CD | **Implemented** ✅ (100%) |

---

## 🏗️ Structure du projet

- `ingestion/`          → Connecteurs sources (API/News/Synthetic), client Kafka résilient & Bronze writer
- `spark_jobs/`        → Jobs de nettoyage et transformation Bronze $\rightarrow$ Silver (Parquet)
- `data_quality/`     → Suites de validation de la qualité des données (Great Expectations style)
- `dbt_project/`       → Modèles dbt Silver $\rightarrow$ Gold (`company_360`, `investment_targets`, `market_analysis`)
- `scoring_engine/`    → Moteur de scoring M&A par règles métier pondérées et explications
- `ml/`                → Modèle prédictif XGBoost + explicabilité locale SHAP
- `backend/`           → API FastAPI (`/companies`, `/score`, `/search`, `/market-analysis`)
- `frontend/`          → Dashboard React Vite + Tailwind CSS + Recharts
- `orchestration/`     → DAGs Airflow (`dealscout_daily_pipeline.py`)
- `observability/`      → Configurations Prometheus & Dashboards Grafana
- `tests/`             → Suite complète de tests unitaires et d'intégration pytest

---

## 🚀 Démarrage & Tests

### 1. Exécuter la suite de tests automatisés

```bash
cd dealscout
python -m pytest -v
```

### 2. Lancer l'API FastAPI

```bash
cd dealscout
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Documentation Swagger accessible sur : `http://localhost:8000/docs`

### 3. Lancer le Frontend React

```bash
cd dealscout/frontend
npm install
npm run dev
```

### 4. Déploiement complet via Docker Compose

```bash
cd dealscout
cp .env.example .env
docker-compose up -d
```

---

## 💼 Positionnement dans la suite portfolio Fintech

```
LedgerLake   → Data Foundation (plateforme de données financières)
CreditPulse  → Credit Risk Decision Engine (scoring crédit)
DealScout    → Investment & M&A Intelligence Engine (scoring d'opportunités)
```
