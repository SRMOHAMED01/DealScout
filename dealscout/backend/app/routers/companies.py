"""
companies.py — Routes entreprises (Palier F)
À IMPLÉMENTER :
  GET /companies                -> liste paginée depuis company_360
  GET /companies/{id}             -> fiche complète (company_360)
  GET /companies/{id}/score        -> score règles + ML + explication SHAP
     Retourne :
     {
       "m_and_a_score": 82.5,
       "acquisition_probability": 91,
       "ranking": 5,
       "explanation": [...]
     }
"""
