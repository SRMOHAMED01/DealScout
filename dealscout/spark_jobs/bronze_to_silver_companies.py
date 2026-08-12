"""
bronze_to_silver_companies.py — Nettoyage des entreprises (Palier B.1)

À IMPLÉMENTER :
1. spark.read.json("s3a://bronze/companies/...")
2. Dédoublonnage intelligent : une même entreprise peut apparaître comme
   "ABC", "ABC Inc", "ABC Inc." — normaliser le nom (lower, strip suffixes
   type Inc/Ltd/SARL) avant dropDuplicates()
3. Standardisation pays/secteur :
   mapping {"USA": "USA", "United States": "USA", "US": "USA", ...}
4. Écriture partitionnée en Parquet vers s3a://silver/companies/

if __name__ == "__main__":
    pass
"""
