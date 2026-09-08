"""
DealScout - Data Quality & Integrity Validation Suite
Palier B / Palier H

Validates data expectations against Silver & Gold datasets:
- Non-null and unique primary keys (company_id)
- Positive revenue, debt, and valuations
- Bounded scores and sentiment ranges (-1.0 to 1.0, 0 to 100)
"""

from __future__ import annotations

import logging
from typing import Any
import pandas as pd

logger = logging.getLogger(__name__)


class DataQualityReport:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def add_check(self, check_name: str, passed: bool, details: str = "") -> None:
        self.checks.append({
            "check": check_name,
            "passed": passed,
            "details": details,
        })

    @property
    def is_successful(self) -> bool:
        return all(c["passed"] for c in self.checks)

    def summary(self) -> dict[str, Any]:
        total = len(self.checks)
        passed_count = sum(1 for c in self.checks if c["passed"])
        return {
            "total_checks": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "success": self.is_successful,
            "checks": self.checks,
        }


def validate_companies_silver(df: pd.DataFrame) -> DataQualityReport:
    report = DataQualityReport()

    # Check 1: company_id non null
    null_ids = df["company_id"].isnull().sum()
    report.add_check("company_id_not_null", null_ids == 0, f"Found {null_ids} null company_ids")

    # Check 2: company_id unique
    dup_ids = df["company_id"].duplicated().sum()
    report.add_check("company_id_unique", dup_ids == 0, f"Found {dup_ids} duplicate company_ids")

    # Check 3: employees positive
    invalid_emp = (df["employees"] <= 0).sum()
    report.add_check("employees_positive", invalid_emp == 0, f"Found {invalid_emp} non-positive employee records")

    # Check 4: scores between 0 and 100
    for score_col in ["innovation_score", "market_score", "international_presence"]:
        if score_col in df.columns:
            out_of_bounds = ((df[score_col] < 0.0) | (df[score_col] > 100.0)).sum()
            report.add_check(f"{score_col}_range_0_100", out_of_bounds == 0, f"{out_of_bounds} out of range [0, 100]")

    return report


def validate_financial_silver(df: pd.DataFrame) -> DataQualityReport:
    report = DataQualityReport()

    # Check 1: company_id non null
    null_ids = df["company_id"].isnull().sum()
    report.add_check("financial_company_id_not_null", null_ids == 0, f"Found {null_ids} null company_ids")

    # Check 2: company_id unique
    dup_ids = df["company_id"].duplicated().sum()
    report.add_check("financial_company_id_unique", dup_ids == 0, f"Found {dup_ids} duplicate financial records")

    # Check 3: revenue >= 0
    neg_rev = (df["revenue"] < 0).sum()
    report.add_check("revenue_non_negative", neg_rev == 0, f"Found {neg_rev} negative revenues")

    # Check 4: financial_health_score between 0 and 100
    if "financial_health_score" in df.columns:
        bad_health = ((df["financial_health_score"] < 0.0) | (df["financial_health_score"] > 100.0)).sum()
        report.add_check("financial_health_range_0_100", bad_health == 0, f"{bad_health} invalid health scores")

    return report


def validate_news_silver(df: pd.DataFrame) -> DataQualityReport:
    report = DataQualityReport()

    null_ids = df["company_id"].isnull().sum()
    report.add_check("news_company_id_not_null", null_ids == 0, f"Found {null_ids} null company_ids")

    # Sentiment between -1.0 and 1.0
    bad_sent = ((df["news_sentiment_score"] < -1.0) | (df["news_sentiment_score"] > 1.0)).sum()
    report.add_check("news_sentiment_range", bad_sent == 0, f"Found {bad_sent} out of range sentiments")

    # Mentions >= 1
    bad_mentions = (df["mentions_count"] < 1).sum()
    report.add_check("mentions_count_positive", bad_mentions == 0, f"{bad_mentions} records with <1 mentions")

    return report
