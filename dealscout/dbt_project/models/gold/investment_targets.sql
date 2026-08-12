-- investment_targets.sql — Table principale de classement (Palier C.1 / D)
-- À IMPLÉMENTER : alimentée par le Scoring Engine (scoring_engine/).
-- Cette table peut être écrite directement par le script Python de scoring
-- plutôt que par dbt seul (dbt prépare les inputs, le scoring calcule
-- le score final et écrit ici).
--
-- Colonnes attendues :
--   company, m_and_a_score, ranking, recommendation, risk_level

select
    company_id,
    1 as placeholder -- TODO: sera remplacé/complété par scoring_engine
from {{ ref('company_360') }}
