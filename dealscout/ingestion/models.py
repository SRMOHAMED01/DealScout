"""
Data models and Kafka event contracts for DealScout Ingestion.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field


def generate_event_id() -> str:
    """Generate a unique UUIDv4 string."""
    return str(uuid.uuid4())


def current_iso_timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class EventEnvelope(BaseModel):
    """
    Standard Kafka Event Envelope for all DealScout event streams.
    """
    event_id: str = Field(default_factory=generate_event_id)
    event_type: str
    schema_version: str = "1.0"
    source: str
    timestamp: str = Field(default_factory=current_iso_timestamp)
    payload: dict[str, Any]


class CompanyProfile(BaseModel):
    """
    Core metadata of an enterprise target.
    """
    company_id: str
    name: str
    sector: str
    country: str
    city: str
    founded_year: int
    age_years: int
    employees: int
    international_presence: float = Field(ge=0.0, le=100.0)
    innovation_score: float = Field(ge=0.0, le=100.0)
    market_score: float = Field(ge=0.0, le=100.0)


class FinancialMetrics(BaseModel):
    """
    Financial performance metrics for valuation and M&A scoring.
    """
    company_id: str
    revenue: float = Field(ge=0.0)
    revenue_growth: float
    profit_margin: float
    ebitda_margin: float
    debt: float = Field(ge=0.0)
    cash: float = Field(ge=0.0)
    market_cap: float = Field(ge=0.0)
    funding_total: float = Field(ge=0.0)
    funding_rounds: int = Field(ge=0)
    currency: str = "USD"
    timestamp: str = Field(default_factory=current_iso_timestamp)


class NewsArticle(BaseModel):
    """
    Market and media event for an enterprise with computed sentiment.
    """
    news_id: str = Field(default_factory=generate_event_id)
    company_id: str
    title: str
    description: str
    source: str
    url: str
    published_at: str = Field(default_factory=current_iso_timestamp)
    sentiment: float = Field(ge=-1.0, le=1.0)
