"""
serve.py — Point d'entrée utilisé par le backend (Palier E, F)

À IMPLÉMENTER :
def predict_acquisition(company_features: dict) -> dict:
    \"\"\"
    Retourne :
    {
        "acquisition_probability": float (0-100),
        "explanation": [...]  # sortie de explain.format_explanation()
    }
    \"\"\"
    pass

NOTE : le backend peut exposer à la fois le m_and_a_score (règles,
scoring_engine/) ET l'acquisition_probability (ML, ce fichier) — les
comparer est un bon argument de démonstration en entretien.
"""
