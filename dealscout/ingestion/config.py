"""
Centralized Configuration for Ingestion & Storage.
Reads from environment variables with robust defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)


@dataclass(frozen=True)
class IngestionConfig:
    # Kafka
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic_companies: str = os.getenv("KAFKA_TOPIC_COMPANIES", "companies-events")
    kafka_topic_financial: str = os.getenv("KAFKA_TOPIC_FINANCIAL", "financial-events")
    kafka_topic_news: str = os.getenv("KAFKA_TOPIC_NEWS", "news-events")
    kafka_consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "dealscout-bronze-group")

    # MinIO / S3
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ROOT_USER", "dealscout")
    minio_secret_key: str = os.getenv("MINIO_ROOT_PASSWORD", "changeme")
    minio_bucket_bronze: str = os.getenv("MINIO_BUCKET_BRONZE", "bronze")
    minio_bucket_silver: str = os.getenv("MINIO_BUCKET_SILVER", "silver")
    s3_use_ssl: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

    # Local storage fallback (for testing / offline mode)
    local_bronze_dir: Path = BASE_DIR / "data" / "bronze"
    local_samples_dir: Path = BASE_DIR / "data" / "samples"

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


config = IngestionConfig()
