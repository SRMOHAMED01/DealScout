"""
Unit tests for Web Scraper Connector (Palier A.1).
"""

from ingestion.connectors.web_scraper import (
    detect_technologies,
    scrape_company_website,
)


def test_detect_technologies():
    sample_html = """
    <html>
      <head><title>Test App</title></head>
      <body>
        <div id="root">Built with React and Python FastAPI</div>
        <script src="https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.js"></script>
        <p>Deploy on AWS Kubernetes clusters</p>
      </body>
    </html>
    """
    detected = detect_technologies(sample_html)
    assert "React" in detected
    assert "Python" in detected
    assert "Vue.js" in detected
    assert "AWS" in detected
    assert "Kubernetes" in detected


def test_scrape_company_website_fallback():
    # Calling with invalid / offline url triggers fallback signals
    res = scrape_company_website("http://non-existent-dummy-domain-xyz123.org", timeout=1)
    assert res["status"] in ("fallback", "success")
    assert "technologies" in res
    assert "product_keywords" in res
    assert "has_careers_page" in res
