"""
rules_scoring.py — Calcul du score M&A par règles pondérées (Palier D)

FORMULE À IMPLÉMENTER :
  M&A Score = Growth * 0.30
            + Revenue * 0.20
            + Profitability * 0.20
            + Market_Opportunity * 0.15
            + Innovation * 0.10
            + International_Presence * 0.05

À IMPLÉMENTER :
1. normalize(series: pd.Series) -> pd.Series
   Normalise chaque composante entre 0 et 100 (min-max scaling) avant
   pondération — IMPORTANT car revenue et growth n'ont pas la même échelle
   brute (ex: revenue en millions vs growth en %)
2. compute_score(df: pd.DataFrame) -> pd.DataFrame
   Lit company_360 (Gold), calcule chaque composante normalisée, applique
   la formule, ajoute la colonne m_and_a_score
3. assign_ranking(df) -> trie par score décroissant, ajoute la colonne ranking
4. assign_recommendation(score: float) -> str
   score >= 85 -> "Cible prioritaire"
   score >= 60 -> "À surveiller"
   sinon        -> "Faible priorité"
5. write_to_gold(df) -> écrit dans la table investment_targets (Gold)

if __name__ == "__main__":
    pass
"""
