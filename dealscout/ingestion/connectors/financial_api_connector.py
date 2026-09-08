"""
DealScout - Financial API Connector
Palier A.1

Responsibility:
    Collect or generate financial data (revenue, EBITDA, debt, cash, valuation/market cap)
    for companies. Supports synthetic generation (local/offline) and fallback for API integrations.
"""

from __future__ import annotations

import logging
import os
import random
from typing import Any
import requests

from ingestion.config import config
from ingestion.models import FinancialMetrics, current_iso_timestamp

logger = logging.getLogger(__name__)


def extract_financials_from_company(company_data: dict[str, Any]) -> dict[str, Any]:
    """
    Extracts and standardizes financial metrics from a company record.
    """
    company_id = company_data.get("company_id", "CMP-UNKNOWN")
    revenue = float(company_data.get("revenue", 10_000_000.0))
    revenue_growth = float(company_data.get("revenue_growth", 15.0))
    profit_margin = float(company_data.get("profit_margin", 10.0))
    ebitda_margin = float(company_data.get("ebitda_margin", 15.0))
    debt = float(company_data.get("debt", 2_000_000.0))
    cash = float(company_data.get("cash", 3_000_000.0))
    market_cap = float(company_data.get("market_cap", revenue * 3.5))
    funding_total = float(company_data.get("funding_total", 5_000_000.0))
    funding_rounds = int(company_data.get("funding_rounds", 2))

    financials = FinancialMetrics(
        company_id=company_id,
        revenue=round(revenue, 2),
        revenue_growth=round(revenue_growth, 2),
        profit_margin=round(profit_margin, 2),
        ebitda_margin=round(ebitda_margin, 2),
        debt=round(debt, 2),
        cash=round(cash, 2),
        market_cap=round(market_cap, 2),
        funding_total=round(funding_total, 2),
        funding_rounds=funding_rounds,
        currency="USD",
        timestamp=current_iso_timestamp(),
    )
    return financials.model_dump()


def generate_synthetic_financials(
    company_id: str,
    base_revenue: float = 20_000_000.0,
) -> dict[str, Any]:
    """
    Generates realistic financial metrics on the fly for a given company ID.
    """
    revenue = max(100_000.0, random.gauss(base_revenue, base_revenue * 0.3))
    revenue_growth = random.uniform(-10.0, 60.0)
    profit_margin = random.uniform(-15.0, 30.0)
    ebitda_margin = profit_margin + random.uniform(2.0, 10.0)
    debt = max(0.0, revenue * random.uniform(0.05, 0.45))
    cash = max(50_000.0, revenue * random.uniform(0.10, 0.50))
    valuation_multiplier = random.uniform(2.0, 8.0) if revenue_growth > 20 else random.uniform(1.2, 3.5)
    market_cap = max(revenue, revenue * valuation_multiplier)
    funding_total = revenue * random.uniform(0.1, 0.8)
    funding_rounds = random.randint(1, 5)

    metrics = FinancialMetrics(
        company_id=company_id,
        revenue=round(revenue, 2),
        revenue_growth=round(revenue_growth, 2),
        profit_margin=round(profit_margin, 2),
        ebitda_margin=round(ebitda_margin, 2),
        debt=round(debt, 2),
        cash=round(cash, 2),
        market_cap=round(market_cap, 2),
        funding_total=round(funding_total, 2),
        funding_rounds=funding_rounds,
        currency="USD",
        timestamp=current_iso_timestamp(),
    )
    return metrics.model_dump()


def fetch_financials(
    company_identifier: str,
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    Fetches financial data from external API (Alpha Vantage / FMP) with fallback
    to synthetic data if no API key or network is available.
    """
    key = api_key or os.getenv("FINANCIAL_API_KEY")
    if key and key not in ("your_alpha_vantage_or_fmp_key", ""):
        try:
            logger.info("Calling external financial API for %s", company_identifier)
            # Simulated real API call or integration
            url = f"https://financialmodelingprep.com/api/v3/profile/{company_identifier}?apikey={key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return {
                    "company_id": company_identifier,
                    "revenue": float(data.get("revenue", 10_000_000.0)),
                    "revenue_growth": 15.0,
                    "profit_margin": 12.0,
                    "ebitda_margin": 18.0,
                    "debt": 1_000_000.0,
                    "cash": 2_000_000.0,
                    "market_cap": float(data.get("mktCap", 30_000_000.0)),
                    "funding_total": 5_000_000.0,
                    "funding_rounds": 2,
                    "currency": data.get("currency", "USD"),
                    "timestamp": current_iso_timestamp(),
                }
        except Exception as err:
            logger.warning("External API call failed, falling back to synthetic: %s", err)

    return generate_synthetic_financials(company_identifier)
