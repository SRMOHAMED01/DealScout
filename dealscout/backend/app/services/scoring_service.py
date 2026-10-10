"""
scoring_service.py â€” Data loading, search, and score aggregation service for FastAPI.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd

from ingestion.config import config
from ingestion.connectors.company_db_connector import generate_synthetic_companies
from scoring_engine.rules_scoring import compute_scores

logger = logging.getLogger(__name__)


class CompanyScoringService:
    """
    Central service caching and serving Company 360 data, M&A scores, and search filtering.
    """

    def __init__(self) -> None:
        self._df: pd.DataFrame = pd.DataFrame()
        self.refresh_data()

    def refresh_data(self) -> None:
        """Loads data from Gold storage or generates it on the fly if not yet persisted."""
        gold_path = Path("data") / "gold" / "investment_targets" / "investment_targets.parquet"

        if gold_path.exists():
            try:
                self._df = pd.read_parquet(gold_path)
                logger.info("Loaded %d records from Gold storage", len(self._df))
                return
            except Exception as e:
                logger.warning("Failed to load Gold parquet (%s), generating fallback", e)

        # Fallback: build Company 360 from generator + compute scores
        raw = generate_synthetic_companies(n=100, seed=42)
        base_df = pd.DataFrame(raw)
        base_df["growth"] = base_df["revenue_growth"]
        base_df["funding"] = base_df["funding_total"]
        base_df["financial_health"] = 65.0
        base_df["news_sentiment"] = 0.25
        base_df["mentions_count"] = 3
        base_df["latest_headline"] = "Strategic expansion announced"

        self._df = compute_scores(base_df)
        logger.info("Generated and scored %d fallback companies in memory", len(self._df))

    def get_all(self, limit: int = 50, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        total = len(self._df)
        subset = self._df.iloc[offset : offset + limit]
        return subset.to_dict(orient="records"), total

    def get_by_id(self, company_id: str) -> dict[str, Any] | None:
        matches = self._df[self._df["company_id"] == company_id]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def get_score_by_id(self, company_id: str) -> dict[str, Any] | None:
        rec = self.get_by_id(company_id)
        if not rec:
            return None

        exp = rec.get("explanation")
        if isinstance(exp, str):
            try:
                exp = json.loads(exp)
            except Exception:
                exp = {}
        elif not isinstance(exp, dict):
            exp = {}

        components = exp.get("components", {
            "growth": 0.0, "revenue": 0.0, "profitability": 0.0,
            "market": 0.0, "innovation": 0.0, "international": 0.0
        })

        return {
            "company_id": rec["company_id"],
            "name": rec["name"],
            "m_and_a_score": float(rec.get("m_and_a_score", 0.0)),
            "ranking": int(rec.get("ranking", 1)),
            "recommendation": str(rec.get("recommendation", "Ã€ surveiller")),
            "risk_level": str(rec.get("risk_level", "Medium")),
            "acquisition_probability": round(float(rec.get("m_and_a_score", 50.0)) * 0.95, 1),
            "components": components,
            "strengths": exp.get("strengths", []),
            "risks": exp.get("risks", []),
        }

    def search(
        self,
        sector: str | None = None,
        country: str | None = None,
        min_growth: float | None = None,
        min_revenue: float | None = None,
        min_score: float | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        filtered = self._df.copy()

        if sector:
            filtered = filtered[filtered["sector"].str.lower() == sector.lower()]
        if country:
            filtered = filtered[filtered["country"].str.lower() == country.lower()]
        if min_growth is not None:
            filtered = filtered[filtered["growth"] >= min_growth]
        if min_revenue is not None:
            filtered = filtered[filtered["revenue"] >= min_revenue]
        if min_score is not None:
            filtered = filtered[filtered["m_and_a_score"] >= min_score]

        filtered = filtered.sort_values(by="m_and_a_score", ascending=False)
        total = len(filtered)
        paged = filtered.iloc[offset : offset + limit]
        return paged.to_dict(orient="records"), total

    def market_analysis(self) -> list[dict[str, Any]]:
        if self._df.empty:
            return []

        grouped = self._df.groupby("sector").agg(
            number_of_companies=("company_id", "count"),
            average_growth=("growth", "mean"),
            average_financial_health=("financial_health", "mean"),
            investment_volume=("funding", "sum"),
            average_sentiment=("news_sentiment", "mean"),
        ).reset_index()

        grouped["average_growth"] = grouped["average_growth"].round(2)
        grouped["average_financial_health"] = grouped["average_financial_health"].round(2)
        grouped["investment_volume"] = grouped["investment_volume"].round(2)
        grouped["average_sentiment"] = grouped["average_sentiment"].round(3)

        return grouped.sort_values(by="average_growth", ascending=False).to_dict(orient="records")


service = CompanyScoringService()

