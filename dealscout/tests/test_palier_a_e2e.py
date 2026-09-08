"""
End-to-end test for Palier A (Ingestion & Bronze Storage).

Validates the full chain:
Company Generator -> Connectors -> Kafka Producers -> Kafka -> Bronze Consumer -> Raw Bronze Partitioned Storage.
"""

import json
from pathlib import Path

from ingestion.bronze_writer import BronzeStorageClient, BronzeWriter
from ingestion.config import config
from ingestion.connectors.company_db_connector import generate_synthetic_companies
from ingestion.kafka.client import DealScoutProducer, in_memory_bus
from ingestion.producers.companies_producer import publish_companies
from ingestion.producers.financial_producer import publish_financials
from ingestion.producers.news_producer import publish_news


def test_palier_a_end_to_end_pipeline(tmp_path: Path):
    in_memory_bus.clear()

    # Step 1: Generate dataset of companies
    raw_companies = generate_synthetic_companies(n=10, seed=100)
    assert len(raw_companies) == 10

    # Step 2: Initialize Kafka producer in mock mode
    producer = DealScoutProducer(mock_mode=True)

    # Step 3: Produce events across all 3 streams
    published_companies = publish_companies(raw_companies, count=10, producer=producer)
    published_financials = publish_financials(raw_companies, count=10, producer=producer)
    published_news = publish_news(raw_companies, count=10, articles_per_company=2, producer=producer)

    assert len(published_companies) == 10
    assert len(published_financials) == 10
    assert len(published_news) == 20

    # Verify messages in memory bus
    assert len(in_memory_bus.get_messages(config.kafka_topic_companies)) == 10
    assert len(in_memory_bus.get_messages(config.kafka_topic_financial)) == 10
    assert len(in_memory_bus.get_messages(config.kafka_topic_news)) == 20

    # Step 4: Run Bronze Consumer / Writer
    storage = BronzeStorageClient()
    storage.s3_client = None  # Route to local temp directory for deterministic verification
    storage.local_dir = tmp_path / "bronze"

    writer = BronzeWriter(storage=storage)
    written_batches = writer.run_batch_pipeline()

    # Step 5: Verify Bronze landing and partitioning
    assert config.kafka_topic_companies in written_batches
    assert config.kafka_topic_financial in written_batches
    assert config.kafka_topic_news in written_batches

    for topic, file_path_str in written_batches.items():
        file_path = Path(file_path_str)
        assert file_path.exists(), f"Raw batch file for {topic} does not exist"
        data = json.loads(file_path.read_text(encoding="utf-8"))
        assert len(data) > 0
        assert "event_id" in data[0]
        assert "payload" in data[0]
        assert "timestamp" in data[0]

        # Verify year=... month=... day=... partition folders exist
        assert any("year=" in part for part in file_path.parts)
        assert any("month=" in part for part in file_path.parts)
        assert any("day=" in part for part in file_path.parts)
