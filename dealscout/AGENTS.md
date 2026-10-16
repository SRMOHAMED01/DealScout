# DealScout — Agent Instructions

## Commands

Run from the `dealscout/` directory.

### Tests
```bash
# Full suite
python -m pytest -v

# Specific palier
python -m pytest tests/test_palier_a_e2e.py tests/test_palier_b_silver.py -v
python -m pytest tests/test_scoring_engine.py tests/test_ml_pipeline.py -v
python -m pytest tests/test_backend_api.py -v
python -m pytest tests/test_daily_pipeline.py -v
python -m pytest tests/test_p0_syntax.py -v
```

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger: http://localhost:8000/docs

### ML
```bash
cd ml
pip install -r requirements.txt
python train.py          # trains + saves model to model_registry/acquisition_xgb.joblib
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev              # http://localhost:5173
npm run build            # production build
```

### Docker Compose (full platform)
```bash
cp .env.example .env
docker-compose up -d
```

### dbt (Gold layer)
```bash
cd dbt_project
cp profiles.yml ~/.dbt/profiles.yml   # or set DBT_PROFILES_DIR
dbt deps
dbt build --target dev
```

### Lint / Typecheck
```bash
pip install ruff sqlfluff
ruff check backend/ ingestion/ scoring_engine/ ml/ orchestration/ tests/
sqlfluff lint dbt_project/models/
cd frontend && npx eslint src --ext .js,.jsx
```

### Project structure
- `ingestion/` — Palier A: connectors, generators, Kafka producers, Bronze writer
- `spark_jobs/` — Palier B: Bronze → Silver (Parquet)
- `data_quality/` — Great Expectations-style validation
- `dbt_project/` — Palier C: Silver → Gold (company_360, investment_targets, market_analysis)
- `scoring_engine/` — Palier D: weighted M&A rules scoring (0-100)
- `ml/` — Palier E: XGBoost + SHAP acquisition probability
- `backend/` — Palier F: FastAPI REST API
- `frontend/` — Palier G: React dashboard
- `orchestration/` — Palier H: Airflow-style daily DAG
- `observability/` — Prometheus + Grafana
- `governance/` — OpenMetadata lineage config

## Notes
- `ml/model_registry/` must contain `acquisition_xgb.joblib` (run `python ml/train.py`).
- `tests/test_ml_pipeline.py` requires `shap`/`scipy`; blocked on this machine by an Application Control policy (DLL load). ML training itself works.
- Backend imports assume `backend/` on sys.path when run from `dealscout/` root (see `conftest.py`); Docker workdir is `/app` (backend dir).
