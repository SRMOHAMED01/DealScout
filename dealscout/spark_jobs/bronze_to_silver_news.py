"""
bronze_to_silver_news.py — Agrégation des actualités (Palier B.1)

À IMPLÉMENTER :
1. Grouper les articles par company_id
2. Calculer un news_sentiment_score agrégé (moyenne pondérée par
   récence : les articles récents comptent plus)
3. Compter le nombre de mentions récentes (signal d'intérêt médiatique)
4. Écriture Parquet vers s3a://silver/news/
"""
