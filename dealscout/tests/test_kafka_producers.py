"""
Unit tests for Kafka producers & abstraction (Palier A.2).
"""

from ingestion.config import config
from ingestion.kafka.client import DealScoutProducer, in_memory_bus
from ingestion.producers.companies_producer import publish_companies
from ingestion.producers.financial_producer import publish_financials
from ingestion.producers.news_producer import publish_news


def test_producer_event_envelope_and_memory_bus():
    in_memory_bus.clear()
    prod = DealScoutProducer(mock_mode=True)

    env = prod.send_event(
        topic="test-topic",
        key="CMP-123",
        payload={"sample_key": "sample_val"},
        event_type="test.event",
        source="unit_test",
    )

    assert env.event_type == "test.event"
    assert env.source == "unit_test"
    assert env.payload["sample_key"] == "sample_val"
    assert env.schema_version == "1.0"
    assert env.event_id is not None
    assert env.timestamp is not None

    messages = in_memory_bus.get_messages("test-topic")
    assert len(messages) == 1
    assert messages[0]["key"] == "CMP-123"
    assert messages[0]["value"]["payload"]["sample_key"] == "sample_val"


def test_companies_producer():
    in_memory_bus.clear()
    prod = DealScoutProducer(mock_mode=True)
    events = publish_companies(count=5, producer=prod)

    assert len(events) == 5
    messages = in_memory_bus.get_messages(config.kafka_topic_companies)
    assert len(messages) == 5
    assert messages[0]["value"]["event_type"] == "company.created"
    assert messages[0]["value"]["payload"]["company_id"].startswith("CMP-")


def test_financial_producer():
    in_memory_bus.clear()
    prod = DealScoutProducer(mock_mode=True)
    events = publish_financials(count=5, producer=prod)

    assert len(events) == 5
    messages = in_memory_bus.get_messages(config.kafka_topic_financial)
    assert len(messages) == 5
    assert messages[0]["value"]["event_type"] == "financial.updated"
    assert "revenue" in messages[0]["value"]["payload"]


def test_news_producer():
    in_memory_bus.clear()
    prod = DealScoutProducer(mock_mode=True)
    events = publish_news(count=3, articles_per_company=2, producer=prod)

    assert len(events) == 6
    messages = in_memory_bus.get_messages(config.kafka_topic_news)
    assert len(messages) == 6
    assert messages[0]["value"]["event_type"] == "news.published"
    assert "sentiment" in messages[0]["value"]["payload"]


def test_producer_dlq_routing():
    in_memory_bus.clear()
    prod = DealScoutProducer(mock_mode=True)
    prod.send_to_dlq(
        original_topic="test-topic",
        key="CMP-ERR",
        raw_payload={"broken": True},
        error_reason="Simulated validation failure",
    )

    dlq_msgs = in_memory_bus.get_messages("test-topic-dlq")
    assert len(dlq_msgs) == 1
    assert dlq_msgs[0]["key"] == "CMP-ERR"
    assert dlq_msgs[0]["value"]["error"] == "Simulated validation failure"
