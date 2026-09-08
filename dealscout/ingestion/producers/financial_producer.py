"""
financial_producer.py — Publishes financial events to Kafka (Palier A.2)
"""

from __future__ import annotations

import logging
from typing import Any

from ingestion.config import config
from ingestion.connectors.company_db_connector import generate_synthetic_companies
from ingestion.connectors.financial_api_connector import extract_financials_from_company
from ingestion.kafka.client import DealScoutProducer
from ingestion.models import EventEnvelope

logger = logging.getLogger(__name__)


def publish_financials(
    companies: list[dict[str, Any]] | None = None,
    count: int = 50,
    producer: DealScoutProducer | None = None,
) -> list[EventEnvelope]:
    """
    Publishes financial metrics events to KAFKA_TOPIC_FINANCIAL.
    """
    prod = producer or DealScoutProducer()
    topic = config.kafka_topic_financial

    if companies is None:
        companies = generate_synthetic_companies(n=count)

    published: list[EventEnvelope] = []

    for comp in companies[:count]:
        try:
            financials_data = extract_financials_from_company(comp)
            env = prod.send_event(
                topic=topic,
                key=financials_data["company_id"],
                payload=financials_data,
                event_type="financial.updated",
                source="financial_connector",
            )
            published.append(env)
        except Exception as exc:
            logger.error("Skipping financial event due to error: %s", exc)

    prod.flush()
    logger.info("Successfully produced %d financial events to topic %s", len(published), topic)
    return published


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    publish_financials(count=10)
