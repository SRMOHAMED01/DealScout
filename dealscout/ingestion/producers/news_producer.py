"""
news_producer.py — Publishes market and company news events to Kafka (Palier A.2)
"""

from __future__ import annotations

import logging
from typing import Any

from ingestion.config import config
from ingestion.connectors.company_db_connector import generate_synthetic_companies
from ingestion.connectors.news_connector import generate_synthetic_news
from ingestion.kafka.client import DealScoutProducer
from ingestion.models import EventEnvelope

logger = logging.getLogger(__name__)


def publish_news(
    companies: list[dict[str, Any]] | None = None,
    count: int = 30,
    articles_per_company: int = 2,
    producer: DealScoutProducer | None = None,
) -> list[EventEnvelope]:
    """
    Publishes news article events to KAFKA_TOPIC_NEWS.
    """
    prod = producer or DealScoutProducer()
    topic = config.kafka_topic_news

    if companies is None:
        companies = generate_synthetic_companies(n=count)

    published: list[EventEnvelope] = []

    for comp in companies[:count]:
        try:
            articles = generate_synthetic_news(
                company_id=comp["company_id"],
                company_name=comp["name"],
                count=articles_per_company,
            )
            for article in articles:
                env = prod.send_event(
                    topic=topic,
                    key=article["company_id"],
                    payload=article,
                    event_type="news.published",
                    source="news_connector",
                )
                published.append(env)
        except Exception as exc:
            logger.error("Skipping news events for company %s due to: %s", comp.get("company_id"), exc)

    prod.flush()
    logger.info("Successfully produced %d news events to topic %s", len(published), topic)
    return published


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    publish_news(count=5)
