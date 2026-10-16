# Tests dbt (Palier C.1 / D)

Tests génériques (schema.yml) sur chaque modèle Gold :
- `company_360` : `unique` + `not_null` sur `company_id` ; `not_null` sur `name`, `sector`
- `investment_targets` : `unique` + `not_null` sur `company_id` ; `not_null` sur `m_and_a_score` ; `accepted_values` sur `risk_level` et `recommendation`
- `market_analysis` : `unique` + `not_null` sur `sector`

Tests unitaires SQL (`dbt_project/tests/`) :
- `unit_test_investment_targets_score_range.sql` : `m_and_a_score` compris entre 0 et 100
- `unit_test_investment_targets_risk_level.sql` : `risk_level` dans `['Low', 'Medium', 'High']`
- `unit_test_company_360_not_null.sql` : `company_id` et `name` non nuls
- `unit_test_market_analysis_sector.sql` : `sector` non nul et unique

Exécution :
```bash
cd dbt_project
dbt deps
dbt test
```
