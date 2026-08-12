"""
dealscout_daily_pipeline.py — DAG Airflow quotidien (Palier H)

À IMPLÉMENTER : DAG avec planning explicite (schedule_interval='@daily'),
tâches dans l'ordre :

  02:00  extract_sources           -> connecteurs (ingestion/connectors/)
  03:00  kafka_ingestion             -> producers (ingestion/producers/)
  03:30  quality_check_bronze          -> Great Expectations
  04:00  spark_processing                -> spark_jobs/ (companies, financial, news)
  04:30  quality_check_silver               -> Great Expectations
  05:00  dbt_transformation                   -> dbt run (dbt_project/)
  06:00  calculate_scores                       -> scoring_engine/rules_scoring.py
                                                    + ml/serve.py si modèle entraîné
  06:30  quality_check_gold                        -> validation finale scores (0-100)
  07:00  refresh_dashboard                            -> invalidation cache / notification

Utiliser des BashOperator/PythonOperator selon les tâches, avec des
dépendances explicites (>>) respectant cet ordre.
"""
