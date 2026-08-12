"""
bronze_to_silver_financial.py — Nettoyage données financières (Palier B.1)

À IMPLÉMENTER :
1. Typage des montants (DoubleType), gestion multi-devises si applicable
2. Calcul de ratios dérivés :
   - growth_yoy (croissance année sur année)
   - profit_margin
3. Calcul de financial_health_score (règle simple : fonction pondérée de
   la marge et du niveau d'endettement, normalisée 0-100)
4. Écriture Parquet vers s3a://silver/financial/
"""
