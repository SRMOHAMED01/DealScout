"""
financial_api_connector.py — Connecteur données financières (Palier A.1)

À IMPLÉMENTER :
1. fetch_financials(company_ticker_or_name: str) -> dict
   Appelle une API financière (Alpha Vantage ou Financial Modeling Prep,
   versions gratuites) et retourne : revenue, market_cap, stock_price,
   growth, profit_margin, debt
2. Gérer le rate limiting des APIs gratuites (souvent 5-25 appels/minute)
   avec un simple time.sleep() entre les appels
3. Fallback : si l'API échoue ou pour du volume, générer des valeurs
   simulées réalistes via generate_synthetic_financials(company_name) —
   utile pour ne pas dépendre des quotas pendant le développement
"""
