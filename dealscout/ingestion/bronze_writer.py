"""
DealScout - Bronze Writer (Palier A.3)
Consumes events from Kafka topics and writes raw partitioned JSON batches
to MinIO (or local storage fallback).

Partitioning convention:
  bronze/<dataset>/year=YYYY/month=MM/day=DD/batch_<uuid>.json
"""

from __future__ import annotations

import io
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ingestion.config import config
from ingestion.kafka.client import KAFKA_AVAILABLE, in_memory_bus

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.client import Config as BotoConfig
    BOTO_AVAILABLE = True
except ImportError:
    BOTO_AVAILABLE = False


TOPIC_TO_DATASET = {
    config.kafka_topic_companies: "companies",
    config.kafka_topic_financial: "financial",
    config.kafka_topic_news: "news",
}


class BronzeStorageClient:
    """
    Handles writes to MinIO / S3 with automatic fallback to local filesystem.
    """

    def __init__(self) -> None:
        self.s3_client: Any = None
        self.bucket = config.minio_bucket_bronze
        self.local_dir = config.local_bronze_dir

        if BOTO_AVAILABLE and config.minio_endpoint:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=config.minio_endpoint,
                    aws_access_key_id=config.minio_access_key,
                    aws_secret_access_key=config.minio_secret_key,
                    config=BotoConfig(signature_version="s3v4", connect_timeout=1, read_timeout=2),
                    verify=config.s3_use_ssl,
                )
                # Check / create bucket
                self._ensure_bucket_exists()
            except Exception as exc:
                logger.warning("MinIO unavailable (%s), falling back to local Bronze storage", exc)
                self.s3_client = None

    def _ensure_bucket_exists(self) -> None:
        if not self.s3_client:
            return
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket)
                logger.info("Created MinIO bucket '%s'", self.bucket)
            except Exception as create_err:
                logger.warning("Could not auto-create MinIO bucket: %s", create_err)

    def write_raw_batch(
        self,
        dataset: str,
        records: list[dict[str, Any]],
        dt: datetime | None = None,
    ) -> str:
        """
        Writes a list of raw event dictionaries to partitioned storage.
        Returns the object key or relative file path.
        """
        if not records:
            return ""

        date_val = dt or datetime.now(timezone.utc)
        year_str = f"{date_val.year:04d}"
        month_str = f"{date_val.month:02d}"
        day_str = f"{date_val.day:02d}"
        batch_id = uuid.uuid4().hex[:12]

        relative_key = (
            f"{dataset}/year={year_str}/month={month_str}/day={day_str}/batch_{batch_id}.json"
        )
        content_bytes = json.dumps(records, indent=2, ensure_ascii=False).encode("utf-8")

        if self.s3_client:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=relative_key,
                    Body=content_bytes,
                    ContentType="application/json",
                )
                logger.info("Persisted %d raw events to s3a://%s/%s", len(records), self.bucket, relative_key)
                return f"s3a://{self.bucket}/{relative_key}"
            except Exception as s3_err:
                logger.warning("S3 write failed (%s), writing locally instead", s3_err)

        # Local storage fallback
        dest_path = self.local_dir / Path(relative_key)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(content_bytes)
        logger.info("Persisted %d raw events to local file %s", len(records), dest_path)
        return str(dest_path)


class BronzeWriter:
    """
    Coordinates consuming from Kafka and persisting raw batches into Bronze storage.
    """

    def __init__(self, storage: BronzeStorageClient | None = None) -> None:
        self.storage = storage or BronzeStorageClient()

    def process_in_memory_topic(self, topic: str, max_records: int | None = None) -> str:
        """
        Flushes events from the in-memory bus directly to Bronze. Useful for testing and offline runs.
        """
        dataset = TOPIC_TO_DATASET.get(topic, topic)
        messages = in_memory_bus.get_messages(topic)
        if not messages:
            return ""

        to_process = messages[:max_records] if max_records else messages
        records = [m["value"] for m in to_process]
        path = self.storage.write_raw_batch(dataset, records)
        return path

    def run_batch_pipeline(self) -> dict[str, str]:
        """
        Ingests all queued topics into their respective Bronze partitions.
        """
        results = {}
        for topic in [
            config.kafka_topic_companies,
            config.kafka_topic_financial,
            config.kafka_topic_news,
        ]:
            path = self.process_in_memory_topic(topic)
            if path:
                results[topic] = path
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    writer = BronzeWriter()
    res = writer.run_batch_pipeline()
    print("Bronze batch pipeline completed:", res)
