"""
Unit tests for News Connector (Palier A.1).
"""

from ingestion.connectors.news_connector import (
    generate_synthetic_news,
    fetch_news,
    compute_deterministic_sentiment,
)


def test_generate_synthetic_news():
    articles = generate_synthetic_news("CMP-000001", "Acme Corp", count=5, seed=42)
    assert len(articles) == 5

    for art in articles:
        assert art["company_id"] == "CMP-000001"
        assert "Acme Corp" in art["title"]
        assert -1.0 <= art["sentiment"] <= 1.0
        assert art["url"].startswith("http")
        assert "published_at" in art


def test_compute_deterministic_sentiment():
    pos = compute_deterministic_sentiment("Company announces record growth and outstanding profit")
    assert pos > 0.0

    neg = compute_deterministic_sentiment("Company faces severe headwinds and heavy financial loss")
    assert neg < 0.0


def test_fetch_news_synthetic_mode():
    articles = fetch_news("CMP-000002", "Globex", mode="synthetic", count=2)
    assert len(articles) == 2
    assert articles[0]["company_id"] == "CMP-000002"
