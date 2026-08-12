"""
bronze_writer.py — Consumer Kafka qui écrit brut dans Bronze (Palier A.3)

RÈGLE D'OR : jamais de transformation ici, données écrites telles quelles.

À IMPLÉMENTER :
1. Consumer confluent_kafka.Consumer abonné aux 3 topics
   (companies-events, financial-events, news-events)
2. Écriture par batch dans MinIO au chemin :
     bronze/<topic>/year=YYYY/month=MM/day=DD/<batch_id>.json
3. Voir bronze/README.md pour la convention complète de partitionnement.

if __name__ == "__main__":
    pass
"""
