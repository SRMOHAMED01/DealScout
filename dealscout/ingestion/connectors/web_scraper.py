"""
web_scraper.py — Scraping de sites d'entreprises (Palier A.1, à faire en dernier)

À IMPLÉMENTER :
1. scrape_company_website(url: str) -> dict
   Utiliser BeautifulSoup pour une extraction simple (texte statique),
   ou Playwright si le site est en JavaScript (rendu dynamique)
   Retourne : products (mots-clés extraits), technologies détectées,
   mentions de "careers"/"partners"
2. À FAIRE EN DERNIER : c'est la source la plus fragile (structure des
   sites qui change, blocages anti-scraping). Respecte robots.txt et
   ajoute des délais entre les requêtes.
"""
