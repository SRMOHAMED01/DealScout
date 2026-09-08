"""
Unit tests for Bronze Writer & storage partitioning (Palier A.3).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from ingestion.bronze_writer import BronzeStorageClient, BronzeWriter
from ingestion.kafka.client import in_memory_bus


def test_bronze_storage_partition_path_and_persistence(tmp_path: Path):
    storage = BronzeStorageClient()
    storage.s3_client = None  # Force local filesystem fallback
    storage.local_dir = tmp_path / "bronze"

    sample_records = [
        {"event_id": "ev-1", "payload": {"company_id": "CMP-1", "name": "Alpha"}},
        {"event_id": "ev-2", "payload": {"company_id": "CMP-2", "name": "Beta"}},
    ]
    custom_dt = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    out_path = storage.write_raw_batch("companies", sample_records, dt=custom_dt)

    assert out_path != ""
    written_file = Path(out_path)
    assert written_file.exists()

    # Check path follows year=YYYY/month=MM/day=DD
    parts = written_file.parts
    assert "year=2026" in parts
    assert "month=09" in parts
    assert "day=08" in parts

    # Check content integrity
    content = json.loads(written_file.read_text(encoding="utf-8"))
    assert len(content) == 2
    assert content[0]["payload"]["name"] == "Alpha"


def test_bronze_writer_empty_records():
    storage = BronzeStorageClient()
    res = storage.write_raw_batch("empty_dataset", [])
    assert res == ""


def test_bronze_writer_process_topic(tmp_path: Path):
    in_memory_bus.clear()
    in_memory_bus.publish("companies-events", "CMP-1", {"company_id": "CMP-1", "val": 100})

    storage = BronzeStorageClient()
    storage.s3_client = None
    storage.local_dir = tmp_path / "bronze"

    writer = BronzeWriter(storage=storage)
    path = writer.process_in_memory_topic("companies-events")

    assert path != ""
    assert Path(path).exists()
