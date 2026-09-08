"""
dealscout_daily_pipeline.py — DAG Airflow quotidien pour DealScout (Palier H)

Pipeline quotidien automatisé :
  02:00  extract_sources         -> Connecteurs (génération/extraction sources)
  03:00  kafka_ingestion         -> Producers (companies, financial, news)
  03:30  bronze_persistence      -> Bronze Writer (partitionnement date MinIO/S3)
  04:00  spark_silver_processing -> Jobs Silver (nettoyage, dédup, normalisation)
  04:30  data_quality_checks     -> Validation qualité Silver (clés, scores, bornes)
  05:00  gold_scoring_engine     -> Calcul score M&A pondéré & ranking
  06:00  refresh_dashboard_cache -> Invalidation et rafraîchissement cache API
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger("dealscout.orchestration")

# Standalone pipeline runners
def run_ingestion():
    from ingestion.connectors.company_db_connector import generate_synthetic_companies
    from ingestion.producers.companies_producer import publish_companies
    from ingestion.producers.financial_producer import publish_financials
    from ingestion.producers.news_producer import publish_news

    logger.info("Starting Daily Ingestion Phase...")
    comps = generate_synthetic_companies(n=50, seed=int(datetime.now().timestamp()))
    publish_companies(comps, count=50)
    publish_financials(comps, count=50)
    publish_news(comps, count=50, articles_per_company=2)
    logger.info("Daily Ingestion Phase Completed.")


def run_bronze_storage():
    from ingestion.bronze_writer import BronzeWriter
    logger.info("Writing Bronze Raw Batches...")
    writer = BronzeWriter()
    res = writer.run_batch_pipeline()
    logger.info("Bronze Batches Written: %s", res)


def run_spark_silver():
    from spark_jobs.bronze_to_silver_companies import process_companies_silver
    from spark_jobs.bronze_to_silver_financial import process_financial_silver
    from spark_jobs.bronze_to_silver_news import process_news_silver
    from ingestion.kafka.client import in_memory_bus
    from ingestion.config import config

    logger.info("Running Silver processing jobs...")
    comp_msgs = [m["value"] for m in in_memory_bus.get_messages(config.kafka_topic_companies)]
    fin_msgs = [m["value"] for m in in_memory_bus.get_messages(config.kafka_topic_financial)]
    news_msgs = [m["value"] for m in in_memory_bus.get_messages(config.kafka_topic_news)]

    df_comp = process_companies_silver(comp_msgs)
    df_fin = process_financial_silver(fin_msgs)
    df_news = process_news_silver(news_msgs)
    logger.info("Silver processed: %d companies, %d financials, %d news", len(df_comp), len(df_fin), len(df_news))


def run_data_quality():
    import pandas as pd
    from data_quality.validator import (
        validate_companies_silver,
        validate_financial_silver,
        validate_news_silver,
    )
    from ingestion.config import config

    silver_base = config.local_bronze_dir.parent / "silver"
    comp_path = silver_base / "companies" / "companies_silver.parquet"
    fin_path = silver_base / "financial" / "financial_silver.parquet"
    news_path = silver_base / "news" / "news_silver.parquet"

    if comp_path.exists():
        r1 = validate_companies_silver(pd.read_parquet(comp_path))
        assert r1.is_successful, f"Companies Silver DQ failed: {r1.summary()}"
    if fin_path.exists():
        r2 = validate_financial_silver(pd.read_parquet(fin_path))
        assert r2.is_successful, f"Financial Silver DQ failed: {r2.summary()}"
    if news_path.exists():
        r3 = validate_news_silver(pd.read_parquet(news_path))
        assert r3.is_successful, f"News Silver DQ failed: {r3.summary()}"
    logger.info("All Silver Data Quality checks PASSED.")


def run_scoring_gold():
    import pandas as pd
    from scoring_engine.rules_scoring import compute_scores, write_to_gold
    from ingestion.config import config

    silver_base = config.local_bronze_dir.parent / "silver"
    comp_path = silver_base / "companies" / "companies_silver.parquet"
    fin_path = silver_base / "financial" / "financial_silver.parquet"
    news_path = silver_base / "news" / "news_silver.parquet"

    if comp_path.exists() and fin_path.exists():
        c = pd.read_parquet(comp_path)
        f = pd.read_parquet(fin_path)
        n = pd.read_parquet(news_path) if news_path.exists() else pd.DataFrame(columns=["company_id", "news_sentiment_score"])

        # Join to build company_360
        merged = c.merge(f, on="company_id", how="left").merge(n, on="company_id", how="left")
        merged["growth"] = merged["revenue_growth"]
        merged["funding"] = merged["funding_total"]

        scored_targets = compute_scores(merged)
        write_to_gold(scored_targets)
        logger.info("Gold Investment Targets scored and written: %d targets", len(scored_targets))


def run_refresh_cache():
    from backend.app.services.scoring_service import service
    service.refresh_data()
    logger.info("API Service cache refreshed successfully.")


# Optional Airflow DAG definition if apache-airflow is installed
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    default_args = {
        "owner": "dealscout",
        "depends_on_past": False,
        "start_date": datetime(2026, 1, 1),
        "email_on_failure": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    }

    with DAG(
        "dealscout_daily_pipeline",
        default_args=default_args,
        description="DealScout End-to-End Daily M&A Lakehouse & Scoring Pipeline",
        schedule_interval="@daily",
        catchup=False,
    ) as dag:

        t_ingest = PythonOperator(task_id="extract_and_publish_sources", python_callable=run_ingestion)
        t_bronze = PythonOperator(task_id="persist_bronze_layer", python_callable=run_bronze_storage)
        t_silver = PythonOperator(task_id="spark_silver_processing", python_callable=run_spark_silver)
        t_dq = PythonOperator(task_id="silver_data_quality", python_callable=run_data_quality)
        t_gold = PythonOperator(task_id="gold_scoring_engine", python_callable=run_scoring_gold)
        t_refresh = PythonOperator(task_id="refresh_dashboard_cache", python_callable=run_refresh_cache)

        t_ingest >> t_bronze >> t_silver >> t_dq >> t_gold >> t_refresh

except ImportError:
    # Airflow not installed in local lightweight test env
    dag = None
