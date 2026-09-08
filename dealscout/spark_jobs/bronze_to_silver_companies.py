"""
bronze_to_silver_companies.py — Nettoyage des entreprises (Palier B.1)

Pipeline:
1. Charge les événements bruts Bronze (JSON) depuis MinIO ou stockage local.
2. Dédoublonnage intelligent : normalisation des noms (minuscules, suppression suffixes Inc/Ltd/SARL).
3. Standardisation pays et secteurs.
4. Écriture partitionnée en Parquet vers Silver (MinIO ou stockage local).
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any
import pandas as pd

from ingestion.config import config

logger = logging.getLogger(__name__)

# Standard mapping for country normalization
COUNTRY_MAPPING = {
    "usa": "United States",
    "us": "United States",
    "united states": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "great britain": "United Kingdom",
    "morocco": "Morocco",
    "maroc": "Morocco",
    "france": "France",
    "germany": "Germany",
    "deutschland": "Germany",
    "spain": "Spain",
    "canada": "Canada",
}

LEGAL_SUFFIXES_REGEX = re.compile(
    r"\b(inc\.?|incorporated|ltd\.?|limited|corp\.?|corporation|sarl|sa|llc|gmbh)\b",
    re.IGNORECASE,
)


def normalize_company_name(name: str) -> str:
    """Normalizes company name by removing punctuation and legal suffixes."""
    if not name:
        return ""
    cleaned = LEGAL_SUFFIXES_REGEX.sub("", name)
    cleaned = re.sub(r"[,.\-_]", " ", cleaned)
    return " ".join(cleaned.lower().split())


def standardize_country(country: str) -> str:
    """Standardizes country name to canonical form."""
    if not country:
        return "Unknown"
    normalized = country.strip().lower()
    return COUNTRY_MAPPING.get(normalized, country.strip().title())


def process_companies_silver(
    bronze_records: list[dict[str, Any]],
    output_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Cleans, deduplicates, and structures company records from Bronze to Silver.
    """
    if not bronze_records:
        return pd.DataFrame()

    # Extract payload if wrapped in event envelope
    rows = []
    for rec in bronze_records:
        payload = rec.get("payload", rec)
        rows.append(payload)

    df = pd.DataFrame(rows)

    # Required columns validation
    mandatory = ["company_id", "name", "sector", "country"]
    for col in mandatory:
        if col not in df.columns:
            raise ValueError(f"Missing mandatory column: {col}")

    # Deduplication and normalization
    df["normalized_name"] = df["name"].apply(normalize_company_name)
    df["country"] = df["country"].apply(standardize_country)
    df["sector"] = df["sector"].fillna("General").astype(str).str.strip().str.title()

    if "employees" not in df.columns:
        df["employees"] = 1
    else:
        df["employees"] = pd.to_numeric(df["employees"], errors="coerce").fillna(1).astype(int)

    for score_col in ["innovation_score", "market_score", "international_presence"]:
        if score_col not in df.columns:
            df[score_col] = 50.0
        else:
            df[score_col] = pd.to_numeric(df[score_col], errors="coerce").fillna(50.0)

    # Drop duplicates prioritizing unique company_id and normalized_name
    df = df.drop_duplicates(subset=["company_id"]).drop_duplicates(subset=["normalized_name"])

    # Output to Parquet
    target_dir = output_dir or (config.local_bronze_dir.parent / "silver" / "companies")
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / "companies_silver.parquet"
    df.to_parquet(out_file, index=False, engine="pyarrow")
    logger.info("Saved Silver companies Parquet (%d records) to %s", len(df), out_file)

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bronze to Silver Companies Processor ready.")
