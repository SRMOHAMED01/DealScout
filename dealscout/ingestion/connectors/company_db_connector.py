"""
company_db_connector.py — Connecteur métadonnées entreprise (Palier A.1)

À IMPLÉMENTER :
1. fetch_company_metadata(company_name: str) -> dict
   Retourne : sector, country, employees, funding, investors
   (via OpenCorporates API si accessible, sinon données simulées)
2. generate_synthetic_companies(n: int) -> list[dict]
   Génère n entreprises fictives réalistes avec `faker` :
   secteurs variés (FinTech, SaaS, HealthTech, E-commerce...),
   pays variés, effectifs, levées de fonds cohérentes avec le secteur
   et l'âge de l'entreprise (une startup de 2 ans ne lève pas 500M).

RECOMMANDATION : pour ce projet, génère un dataset de 500-1000 entreprises
simulées comme source principale — plus fiable et plus rapide à développer
que de dépendre d'APIs externes à quota limité.
"""
