# scoring_engine/ — M&A Scoring Engine (Rules-based, Palier D)

First iteration of the M&A score using a weighted, explainable ruleset. Produces a demonstrable product before introducing ML (Palier E).

## Formula

`
M&A Score = Growth × 30% + Revenue × 20% + Profitability × 20%
          + Market Opportunity × 15% + Innovation × 10%
          + International Presence × 5%
`

Each component is normalized with min-max scaling (0-100) prior to weighting. If all values are equal, a neutral score of 50 is assigned per component.

## Implementation

| File | Purpose |
|---|---|
| ules_scoring.py | Core logic: normalization, weighted scoring, ranking, recommendations, risk classification, and human-readable explanations. |
| equirements.txt | Dependencies for the scoring module. |

## Key Functions

- 
ormalize_min_max(series) – Robust min-max scaling with guard against constant series.
- ssign_recommendation(score) – Maps score to recommendation: >= 85 ? "Cible prioritaire", >= 60 ? "À surveiller", else "Faible priorité".
- compute_scores(df_company_360) – Computes scores, ranks companies, assigns isk_level (Low/Medium/High), and builds explanation (strengths/risks + component breakdown).
- write_to_gold(df, output_path) – Persists results to data/gold/investment_targets/ as Parquet (flattens explanations to JSON for compatibility).

## Output

The engine produces an investment_targets dataset with fields such as company_id, 
ame, m_and_a_score, anking, ecommendation, isk_level, and explanation (strengths/risks + weighted contributions).

## Usage

`ash
# From dealscout/ root
python -c "
from scoring_engine import rules_scoring
import pandas as pd
# Load company_360 (Gold)
df = pd.read_parquet('data/gold/company_360/company_360.parquet')
scored = rules_scoring.compute_scores(df)
rules_scoring.write_to_gold(scored)
"
`

## Notes

- **Explainable by design** – Every score comes with concrete strengths/risks and a per-component breakdown.
- **Data-driven normalization** – Uses min-max over the input dataset, so relative ranking is dataset-dependent (by design for comparative analysis).
- **Bridges to ML** – Results feed into the dashboard and can be compared with XGBoost + SHAP predictions from ml/.
