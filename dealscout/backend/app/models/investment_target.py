"""
investment_target.py — Modèle SQLAlchemy mappant investment_targets (Palier F)
"""

from __future__ import annotations

from sqlalchemy import (
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


class InvestmentTarget(Base):
    __tablename__ = "investment_targets"

    company_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    country = Column(String, nullable=False)
    revenue = Column(Float, default=0.0)
    growth = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    financial_health = Column(Float, default=50.0)
    market_score = Column(Float, default=50.0)
    innovation_score = Column(Float, default=50.0)
    international_presence = Column(Float, default=50.0)
    news_sentiment = Column(Float, default=0.0)
    m_and_a_score = Column(Float, default=0.0)
    ranking = Column(Integer, default=0)
    risk_level = Column(String, default="Medium")
    recommendation = Column(String, default="Faible priorite")
    acquisition_probability = Column(Float, default=0.0)
    components_json = Column(Text, nullable=True)
    strengths_json = Column(Text, nullable=True)
    risks_json = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
