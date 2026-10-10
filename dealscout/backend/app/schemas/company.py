"""
Pydantic schemas for DealScout FastAPI Backend.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class CompanyProfileSchema(BaseModel):
    company_id: str
    name: str
    sector: str
    country: str
    city: str
    employees: int
    founded_year: int
    age_years: int
    revenue: float
    growth: float
    profit_margin: float
    ebitda_margin: float
    debt: float
    cash: float
    market_cap: float
    funding: float
    funding_rounds: int
    financial_health: float
    international_presence: float
    innovation_score: float
    market_score: float
    news_sentiment: float = 0.0
    mentions_count: int = 0
    latest_headline: str | None = None


class ScoreComponentSchema(BaseModel):
    growth: float
    revenue: float
    profitability: float
    market: float
    innovation: float
    international: float


class CompanyScoreSchema(BaseModel):
    company_id: str
    name: str
    m_and_a_score: float
    ranking: int
    recommendation: str
    risk_level: str
    acquisition_probability: float | None = None
    components: ScoreComponentSchema
    strengths: list[str]
    risks: list[str]


class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[dict[str, Any]]


class MarketSectorSummary(BaseModel):
    sector: str
    number_of_companies: int
    average_growth: float
    average_financial_health: float
    investment_volume: float
    average_sentiment: float

