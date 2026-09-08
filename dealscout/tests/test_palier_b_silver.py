"""
Unit tests for Palier B (Spark / Silver Layer) and Data Quality Validation.
"""

from pathlib import Path
import pandas as pd

from spark_jobs.bronze_to_silver_companies import (
    normalize_company_name,
    standardize_country,
    process_companies_silver,
)
from spark_jobs.bronze_to_silver_financial import (
    compute_financial_health_score,
    process_financial_silver,
)
from spark_jobs.bronze_to_silver_news import process_news_silver
from data_quality.validator import (
    validate_companies_silver,
    validate_financial_silver,
    validate_news_silver,
)


def test_company_normalization_and_country():
    assert normalize_company_name("Acme, Inc.") == "acme"
    assert normalize_company_name("Global Tech Ltd.") == "global tech"
    assert standardize_country("USA") == "United States"
    assert standardize_country("maroc") == "Morocco"
    assert standardize_country("UK") == "United Kingdom"


def test_process_companies_silver(tmp_path: Path):
    raw_bronze = [
        {"payload": {"company_id": "CMP-1", "name": "Alpha Corp", "sector": "SaaS", "country": "US", "employees": 50}},
        {"payload": {"company_id": "CMP-1", "name": "Alpha Corp", "sector": "SaaS", "country": "USA", "employees": 50}},  # Duplicate ID
        {"payload": {"company_id": "CMP-2", "name": "Beta LLC", "sector": "FinTech", "country": "France", "employees": 120}},
    ]
    df = process_companies_silver(raw_bronze, output_dir=tmp_path / "companies")
    assert len(df) == 2
    assert "CMP-1" in df["company_id"].values
    assert "CMP-2" in df["company_id"].values
    assert df[df["company_id"] == "CMP-1"]["country"].values[0] == "United States"

    # Validate data quality
    report = validate_companies_silver(df)
    assert report.is_successful is True


def test_process_financial_silver(tmp_path: Path):
    raw_bronze = [
        {"payload": {"company_id": "CMP-1", "revenue": 10_000_000, "profit_margin": 15.0, "debt": 2_000_000, "cash": 3_000_000, "revenue_growth": 25.0}},
        {"payload": {"company_id": "CMP-2", "revenue": 5_000_000, "profit_margin": -5.0, "debt": 4_000_000, "cash": 500_000, "revenue_growth": 10.0}},
    ]
    df = process_financial_silver(raw_bronze, output_dir=tmp_path / "financial")
    assert len(df) == 2
    assert "financial_health_score" in df.columns
    assert 0 <= df["financial_health_score"].iloc[0] <= 100

    report = validate_financial_silver(df)
    assert report.is_successful is True


def test_process_news_silver(tmp_path: Path):
    raw_bronze = [
        {"payload": {"news_id": "N-1", "company_id": "CMP-1", "title": "Good Q1", "sentiment": 0.6}},
        {"payload": {"news_id": "N-2", "company_id": "CMP-1", "title": "Great Q2", "sentiment": 0.8}},
        {"payload": {"news_id": "N-3", "company_id": "CMP-2", "title": "Struggles", "sentiment": -0.4}},
    ]
    df = process_news_silver(raw_bronze, output_dir=tmp_path / "news")
    assert len(df) == 2
    cmp1 = df[df["company_id"] == "CMP-1"].iloc[0]
    assert cmp1["mentions_count"] == 2
    assert cmp1["news_sentiment_score"] == 0.7

    report = validate_news_silver(df)
    assert report.is_successful is True
