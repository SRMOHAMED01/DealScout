"""
companies_producer.py — Publishes company metadata events to Kafka (Palier A.2)
"""

from __future__ import annotations

import logging
from typing import Any

from ingestion.config import config
from ingestion.connectors.company_db_connector import generate_synthetic_companies
from ingestion.kafka.client import DealScoutProducer
from ingestion.models import CompanyProfile, EventEnvelope

logger = logging.getLogger(__name__)


def extract_company_profile(company_dict: dict[str, Any]) -> dict[str, Any]:
    """Extracts and validates company profile payload."""
    profile = CompanyProfile(
        company_id=company_dict["company_id"],
        name=company_dict["name"],
        sector=company_dict["sector"],
        country=company_dict["country"],
        city=company_dict["city"],
        founded_year=int(company_dict["founded_year"]),
        age_years=int(company_dict["age_years"]),
        employees=int(company_dict["employees"]),
        international_presence=float(company_dict.get("international_presence", 50.0)),
        innovation_score=float(company_dict.get("innovation_score", 50.0)),
        market_score=float(company_dict.get("market_score", 50.0)),
    )
    return profile.model_dump()


def publish_companies(
    companies: list[dict[str, Any]] | None = None,
    count: int = 50,
    producer: DealScoutProducer | None = None,
) -> list[EventEnvelope]:
    """
    Publishes company profile events to KAFKA_TOPIC_COMPANIES.
    """
    prod = producer or DealScoutProducer()
    topic = config.kafka_topic_companies

    if companies is None:
        companies = generate_synthetic_companies(n=count)

    published: list[EventEnvelope] = []

    for comp in companies[:count]:
        try:
            profile_data = extract_company_profile(comp)
            env = prod.send_event(
                topic=topic,
                key=profile_data["company_id"],
                payload=profile_data,
                event_type="company.created",
                source="company_generator",
            )
            published.append(env)
        except Exception as exc:
            logger.error("Skipping company event due to error: %s", exc)

    prod.flush()
    logger.info("Successfully produced %d company events to topic %s", len(published), topic)
    return published


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    publish_companies(count=10)
