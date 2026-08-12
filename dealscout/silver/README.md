# silver/ — Convention de stockage nettoyé (Palier B)

Structure attendue dans MinIO (bucket "silver"), format Parquet :

    silver/
      companies/year=2026/month=08/day=03/part-*.parquet
      financial/year=2026/month=08/day=03/part-*.parquet
      news/year=2026/month=08/day=03/part-*.parquet

Contenu : données dédupliquées, standardisées (pays, secteurs), enrichies
des variables dérivées (growth_score, market_score, innovation_score,
financial_health_score). Voir docs/GUIDE_COMPLET.md Palier B.
