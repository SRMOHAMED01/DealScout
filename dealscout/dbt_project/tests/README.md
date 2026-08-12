# Tests dbt (Palier C.1 / D)

À IMPLÉMENTER : tests génériques (schema.yml) sur chaque modèle Gold :
- not_null sur company_id, name
- accepted_values sur risk_level (["low", "medium", "high"])
- dbt_utils.accepted_range sur m_and_a_score (0 à 100)
