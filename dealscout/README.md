# DealScout - M&A Intelligence Platform

DealScout is an end-to-end data platform that helps investment teams identify and prioritize potential M&A targets. It ingests company, financial, and news data, transforms it through a Bronze ? Silver ? Gold data lakehouse pipeline, scores companies with both deterministic rules and an explainable ML model, and exposes insights through a FastAPI backend and a React dashboard.

## What it does

- **Ingests and standardizes data** – Pulls synthetic/structured company, financial, and news signals through Kafka, landing raw events in the Bronze layer for reproducible processing.
- **Cleans and enriches at scale** – Spark jobs normalize entities, deduplicate records, compute key financial ratios and aggregate news sentiment to create clean Silver datasets.
- **Builds an analytical layer** – dbt models shape curated Gold tables (company_360, investment_targets, market_analysis) that power analytics, scoring, and reporting.
- **Scores acquisition potential** – A transparent, rule-based M&A scoring engine (0-100) ranks targets with clear rationale (strengths/risks). An XGBoost classifier predicts acquisition probability and uses SHAP to explain why each prediction was made.
- **Exposes and visualizes insights** – FastAPI REST endpoints serve company data, scores, search, and market analysis. A React + Tailwind + Recharts dashboard lets users filter, rank, and drill into company 360° profiles with ML explainability visuals.

## Key Features

- **Hybrid intelligence** – Deterministic business rules for explainability + ML with local SHAP explanations for trust and auditability.
- **End-to-end pipeline** – From ingestion to scored outputs, the full flow is automated, testable, and orchestrated daily with Airflow-style scheduling.
- **Data quality built-in** – Great Expectations-style validations guard data quality at key stages.
- **Production-minded** – Includes Docker Compose setup, observability (Prometheus/Grafana), governance/lineage scaffolding (OpenMetadata), and CI workflow.
- **Search and discovery** – Multi-criteria search to quickly surface high-potential targets by sector, geography, growth, and more.

## Tech Stack

**Data and Pipelines:** Kafka, Apache Spark (PySpark), dbt, Parquet, MinIO/local storage  
**ML and Scoring:** scikit-learn/xgboost, SHAP  
**Backend:** FastAPI, SQLAlchemy, Pydantic, JWT auth, PostgreSQL  
**Frontend:** React, Vite, TypeScript, Tailwind CSS, Recharts  
**Infra/Platform:** Docker Compose, Airflow (DAGs), Prometheus, Grafana, Great Expectations, OpenMetadata  
**Testing:** pytest (unit, integration, E2E)

## Architecture (high level)

Sources (Companies/Financial/News) -> Kafka -> Bronze (raw) -> Spark (Silver, clean) -> dbt (Gold, curated) -> Scoring Engine (rules) + XGBoost + SHAP -> FastAPI -> React Dashboard

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Docker and Docker Compose (optional for full platform)

### Run Tests
`ash
cd dealscout
python -m pytest -v
`

### Run API
`ash
cd dealscout
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
`
Swagger: http://localhost:8000/docs

### Run Frontend
`ash
cd dealscout/frontend
npm install
npm run dev
`
App: http://localhost:5173

### Full Stack (Docker)
`ash
cd dealscout
cp .env.example .env
docker-compose up -d
`

## What this demonstrates

This project showcases practical full-stack data engineering: building a production-style lakehouse, enforcing data quality, blending rule-based + explainable ML for decision support, exposing clean APIs, and delivering an actionable UI. It's designed to be portfolio-ready and clearly communicates business value to both technical and non-technical audiences.

## Project Status

All 8 development paliers (A-H) are implemented and validated with passing tests. Core functionality is complete and demo-ready.

## Author

[Serrâar Mohamed](https://github.com/SRMOHAMED01)
