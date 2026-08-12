"""
news_connector.py — Connecteur actualités (Palier A.1)

À IMPLÉMENTER :
1. fetch_news(company_name: str) -> list[dict]
   Via NewsAPI (version gratuite, quota limité) ou un flux RSS
   (Google News RSS, gratuit et sans clé API)
   Retourne : title, date, company_mentioned, url
2. analyze_sentiment(article_text: str) -> "positive" | "negative" | "neutral"
   Utiliser une librairie légère (textblob) ou un modèle HuggingFace
   pré-entraîné pour l'analyse de sentiment
"""
