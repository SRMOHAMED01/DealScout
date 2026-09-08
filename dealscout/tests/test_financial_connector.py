"""
Unit tests for Financial Connector (Palier A.1).
"""

from ingestion.connectors.financial_api_connector import (
    extract_financials_from_company,
    generate_synthetic_financials,
    fetch_financials,
)
from ingestion.generators.company_generator import generate_company


def test_extract_financials_from_company():
    company = generate_company(company_id=10)
    fin = extract_financials_from_company(company)

    assert fin["company_id"] == company["company_id"]
    assert fin["revenue"] == round(company["revenue"], 2)
    assert fin["profit_margin"] == round(company["profit_margin"], 2)
    assert fin["currency"] == "USD"
    assert "timestamp" in fin
    assert fin["debt"] >= 0
    assert fin["cash"] >= 0


def test_generate_synthetic_financials():
    fin = generate_synthetic_financials("CMP-TEST-99")
    assert fin["company_id"] == "CMP-TEST-99"
    assert fin["revenue"] > 0
    assert fin["market_cap"] > 0
    assert fin["currency"] == "USD"


def test_fetch_financials_fallback():
    fin = fetch_financials("CMP-UNKNOWN")
    assert fin["company_id"] == "CMP-UNKNOWN"
    assert fin["revenue"] > 0
