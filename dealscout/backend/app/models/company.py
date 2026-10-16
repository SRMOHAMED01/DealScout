"""
company.py — Modèle SQLAlchemy mappant la table Gold company_360 (Palier F)
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "company_360"

    company_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String)
    employees = Column(Integer, default=0)
    founded_year = Column(Integer)
    age_years = Column(Integer)
    revenue = Column(Float, default=0.0)
    growth = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    ebitda_margin = Column(Float, default=0.0)
    debt = Column(Float, default=0.0)
    cash = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)
    funding = Column(Float, default=0.0)
    funding_rounds = Column(Integer, default=0)
    financial_health = Column(Float, default=50.0)
    international_presence = Column(Float, default=50.0)
    innovation_score = Column(Float, default=50.0)
    market_score = Column(Float, default=50.0)
    news_sentiment = Column(Float, default=0.0)
    mentions_count = Column(Integer, default=0)
    latest_headline = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
