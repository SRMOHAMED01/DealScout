# bronze/ — Convention de stockage brut (Palier A.3)

Structure attendue dans MinIO (bucket "bronze") :

    bronze/
      companies/year=2026/month=08/day=03/companies_<batch_id>.json
      financial/year=2026/month=08/day=03/financial_<batch_id>.json
      news/year=2026/month=08/day=03/news_<batch_id>.json
      funding/year=2026/month=08/day=03/funding_<batch_id>.json

RÈGLE D'OR : immutable, jamais modifié, historique complet — permet de
rejouer tout le pipeline en cas d'erreur de transformation en aval.
