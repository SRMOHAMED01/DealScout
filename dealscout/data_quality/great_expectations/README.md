# data_quality/great_expectations/ — Validation qualité (Palier H)

À IMPLÉMENTER : suites de validation aux frontières du pipeline.

## Suite "bronze_to_silver"
- expect_column_values_to_not_be_null : company name, company_id
- expect_column_values_to_be_between : revenue (min=0), employees (min=0)

## Suite "silver_to_gold"
- expect_column_values_to_be_unique : company_id
- expect_column_values_to_be_between : m_and_a_score (min=0, max=100)
- expect_column_values_to_be_in_set : risk_level (["low","medium","high"])

Appelées par les tâches quality_check_* du DAG Airflow.
