"""
financial_producer.py — Publie les événements financiers (Palier A.2)
À IMPLÉMENTER : pour chaque entreprise connue, appelle
financial_api_connector.py et publie sur KAFKA_TOPIC_FINANCIAL.
Format message :
  {"company_id": int, "revenue": float, "growth": float, "profit_margin": float}
"""
