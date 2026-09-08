"""
Unit tests for Daily Pipeline orchestration tasks (Palier H).
"""

from orchestration.dags.dealscout_daily_pipeline import (
    run_ingestion,
    run_bronze_storage,
    run_spark_silver,
    run_data_quality,
    run_scoring_gold,
    run_refresh_cache,
)
from ingestion.kafka.client import in_memory_bus


def test_full_pipeline_run():
    in_memory_bus.clear()

    # Step 1: Ingestion
    run_ingestion()

    # Step 2: Bronze
    run_bronze_storage()

    # Step 3: Spark Silver
    run_spark_silver()

    # Step 4: Data Quality
    run_data_quality()

    # Step 5: Scoring Gold
    run_scoring_gold()

    # Step 6: Refresh Cache
    run_refresh_cache()
