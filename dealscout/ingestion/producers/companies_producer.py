"""
companies_producer.py — Publie les événements entreprise (Palier A.2)
À IMPLÉMENTER : boucle qui appelle company_db_connector.py (génération ou
API réelle) et publie chaque nouvelle entreprise sur KAFKA_TOPIC_COMPANIES.
Format message :
  {"id": int, "name": str, "sector": str, "country": str, "employees": int}
"""
