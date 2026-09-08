"""
bronze_to_silver_news.py — Agrégation et analyse des actualités (Palier B.1)

Pipeline:
1. Charge les articles bruts depuis Bronze.
2. Regroupe les articles par company_id.
3. Calcule un news_sentiment_score agrégé et un nombre de mentions.
4. Écriture Parquet vers Silver (silver/news).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
import pandas as pd

from ingestion.config import config

logger = logging.getLogger(__name__)


def process_news_silver(
    bronze_records: list[dict[str, Any]],
    output_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Groups raw news records by company_id, computes aggregated sentiment and media mentions.
    """
    if not bronze_records:
        return pd.DataFrame()

    rows = []
    for rec in bronze_records:
        payload = rec.get("payload", rec)
        rows.append(payload)

    df = pd.DataFrame(rows)

    if "company_id" not in df.columns:
        raise ValueError("News records missing 'company_id'")

    df["sentiment"] = pd.to_numeric(df.get("sentiment", 0.0), errors="coerce").fillna(0.0)

    # Aggregations per company
    aggregated = df.groupby("company_id").agg(
        news_sentiment_score=("sentiment", "mean"),
        news_sentiment_min=("sentiment", "min"),
        news_sentiment_max=("sentiment", "max"),
        mentions_count=("news_id", "count"),
        latest_headline=("title", "last"),
    ).reset_index()

    aggregated["news_sentiment_score"] = aggregated["news_sentiment_score"].round(3)

    # Output to Parquet
    target_dir = output_dir or (config.local_bronze_dir.parent / "silver" / "news")
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / "news_silver.parquet"
    aggregated.to_parquet(out_file, index=False, engine="pyarrow")
    logger.info("Saved Silver news Parquet (%d records) to %s", len(aggregated), out_file)

    return aggregated


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bronze to Silver News Processor ready.")
