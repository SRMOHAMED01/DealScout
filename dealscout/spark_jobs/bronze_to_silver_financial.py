"""
bronze_to_silver_financial.py — Nettoyage et enrichissement données financières (Palier B.1)

Pipeline:
1. Charge les métriques financières brutes depuis Bronze.
2. Typage strict (Double/Float, int).
3. Calcul des variables dérivées :
   - growth_yoy (croissance)
   - financial_health_score (formule pondérée normalisée 0-100 basée sur rentabilité et endettement)
4. Écriture Parquet vers Silver (silver/financial).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
import pandas as pd

from ingestion.config import config

logger = logging.getLogger(__name__)


def compute_financial_health_score(row: pd.Series) -> float:
    """
    Computes a 0-100 financial health score:
    - 50% Profitability component (margin scaled)
    - 50% Solvency / Debt component (cash to debt & debt-to-revenue ratio)
    """
    margin = float(row.get("profit_margin", 0.0))
    revenue = max(float(row.get("revenue", 1.0)), 1.0)
    debt = max(float(row.get("debt", 0.0)), 0.0)
    cash = max(float(row.get("cash", 0.0)), 0.0)

    # Margin sub-score: margin between -20% and +30% mapped to 0-100
    margin_score = min(100.0, max(0.0, (margin + 20.0) * 2.0))

    # Solvency sub-score: debt ratio
    debt_ratio = debt / revenue
    solvency_score = min(100.0, max(0.0, (1.0 - min(debt_ratio, 1.0)) * 80.0 + min(cash / max(debt, 1.0), 1.0) * 20.0))

    composite = (0.50 * margin_score) + (0.50 * solvency_score)
    return round(float(composite), 2)


def process_financial_silver(
    bronze_records: list[dict[str, Any]],
    output_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Processes raw financial records into clean, typed Silver Parquet.
    """
    if not bronze_records:
        return pd.DataFrame()

    rows = []
    for rec in bronze_records:
        payload = rec.get("payload", rec)
        rows.append(payload)

    df = pd.DataFrame(rows)

    if "company_id" not in df.columns:
        raise ValueError("Financial record missing mandatory 'company_id'")

    # Type enforcement
    numeric_cols = ["revenue", "revenue_growth", "profit_margin", "ebitda_margin", "debt", "cash", "market_cap", "funding_total"]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    if "funding_rounds" not in df.columns:
        df["funding_rounds"] = 0
    else:
        df["funding_rounds"] = pd.to_numeric(df["funding_rounds"], errors="coerce").fillna(0).astype(int)

    if "currency" not in df.columns:
        df["currency"] = "USD"
    else:
        df["currency"] = df["currency"].fillna("USD")

    # Derived metrics
    df["growth_yoy"] = df["revenue_growth"]
    df["financial_health_score"] = df.apply(compute_financial_health_score, axis=1)

    # Deduplicate on company_id, keeping the latest timestamp
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp", ascending=True)
    df = df.drop_duplicates(subset=["company_id"], keep="last")

    # Output to Parquet
    target_dir = output_dir or (config.local_bronze_dir.parent / "silver" / "financial")
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / "financial_silver.parquet"
    df.to_parquet(out_file, index=False, engine="pyarrow")
    logger.info("Saved Silver financial Parquet (%d records) to %s", len(df), out_file)

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bronze to Silver Financial Processor ready.")
