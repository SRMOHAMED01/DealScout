# spark_jobs/ — Jobs Spark Bronze → Silver (Palier B)

Ordre de développement recommandé :
1. bronze_to_silver_companies.py (dédup et standardisation, base de tout le reste)
2. bronze_to_silver_financial.py
3. bronze_to_silver_news.py (le plus complexe, sentiment agrégé)
