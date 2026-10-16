"""
config.py — Configuration centralisée (Palier F)

Settings lisant DATABASE_URL, SECRET_KEY, et les chemins vers les modèles ML
(ml/model_registry/).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Application
    app_name: str = "DealScout"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database (Postgres / Gold warehouse)
    database_url: str = "postgresql://dealscout:changeme@localhost:5432/dealscout_db"

    # Security / JWT
    secret_key: str = "changeme-generate-a-real-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # MinIO / S3
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "dealscout"
    minio_secret_key: str = "changeme"
    minio_bucket_bronze: str = "bronze"
    minio_bucket_silver: str = "silver"

    # ML model registry
    model_registry_dir: Path = BASE_DIR.parent / "ml" / "model_registry"
    model_filename: str = "acquisition_xgb.joblib"

    # Frontend
    api_base_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
