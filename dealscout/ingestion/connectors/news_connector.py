"""
DealScout - News & Market Media Connector
Palier A.1

Responsibility:
    Collect and generate news articles and market sentiment for target companies.
    Supports synthetic generation (offline/MVP) and optional external RSS/NewsAPI fetching.
"""

from __future__ import annotations

import hashlib
import logging
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from ingestion.models import NewsArticle, current_iso_timestamp

logger = logging.getLogger(__name__)

# Templates for synthetic news generation
POSITIVE_HEADLINES = [
    "{company} announces record revenue growth in Q3",
    "{company} closes strategic funding round to expand in Europe and North America",
    "{company} unveils innovative AI-powered enterprise product",
    "{company} named top emerging leader in its sector",
    "Major institutional investors increase stake in {company}",
    "{company} expands international footprint with new market launch",
]

NEUTRAL_HEADLINES = [
    "{company} releases annual sustainability and governance report",
    "{company} announces executive leadership transition",
    "Industry analysis: examining the market positioning of {company}",
    "{company} hosts annual developer and partner conference",
    "{company} completes planned infrastructure and data center migration",
]

NEGATIVE_HEADLINES = [
    "{company} faces headwinds amid tightening market competition",
    "Regulatory scrutiny increases for {company} data privacy compliance",
    "{company} reports temporary margin pressure due to increased R&D spend",
    "Key customer churn impacts {company}'s quarterly expansion forecast",
    "{company} responds to market volatility with conservative guidance",
]

NEWS_SOURCES = [
    "TechCrunch",
    "Bloomberg",
    "Reuters",
    "Financial Times",
    "Forbes",
    "VentureBeat",
    "Les Echos",
    "Tech In Africa",
]


def compute_deterministic_sentiment(text: str) -> float:
    """
    Computes a deterministic sentiment score between -1.0 and +1.0 based on keyword
    lexicon without relying on heavy external LLM services.
    """
    text_lower = text.lower()

    positive_keywords = {
        "record", "growth", "funding", "innovative", "leader", "expand",
        "expansion", "boost", "outperform", "partnership", "success", "profitable"
    }
    negative_keywords = {
        "headwinds", "scrutiny", "pressure", "churn", "volatility", "loss",
        "drop", "lawsuit", "decline", "struggle", "risk", "cut"
    }

    pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
    neg_count = sum(1 for kw in negative_keywords if kw in text_lower)

    if pos_count == 0 and neg_count == 0:
        # Pseudo-random but deterministic based on hash of text
        h = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:4], 16)
        return round((h % 41 - 20) / 100.0, 2)  # Between -0.20 and +0.20

    raw_score = (pos_count - neg_count) / max(1, pos_count + neg_count)
    return round(float(max(-1.0, min(1.0, raw_score))), 2)


def generate_synthetic_news(
    company_id: str,
    company_name: str,
    count: int = 3,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    Generates realistic news articles and media sentiment for a company.
    """
    if seed is not None:
        rng = random.Random(seed + hash(company_id))
    else:
        rng = random.Random()

    articles: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for i in range(count):
        # Category selection: 50% positive, 30% neutral, 20% negative
        category_roll = rng.random()
        if category_roll < 0.50:
            template = rng.choice(POSITIVE_HEADLINES)
            base_sentiment = rng.uniform(0.3, 0.85)
        elif category_roll < 0.80:
            template = rng.choice(NEUTRAL_HEADLINES)
            base_sentiment = rng.uniform(-0.15, 0.20)
        else:
            template = rng.choice(NEGATIVE_HEADLINES)
            base_sentiment = rng.uniform(-0.80, -0.25)

        title = template.format(company=company_name)
        source = rng.choice(NEWS_SOURCES)
        days_ago = rng.randint(1, 90)
        published_date = (now - timedelta(days=days_ago, hours=rng.randint(0, 23))).isoformat()
        news_id = f"NEWS-{uuid.uuid4().hex[:8]}"
        url = f"https://www.{source.lower().replace(' ', '')}.com/article/{news_id.lower()}"
        description = f"{title}. Detailed market analysis regarding {company_name}'s recent performance and strategy."

        sentiment_score = round(base_sentiment, 2)

        article = NewsArticle(
            news_id=news_id,
            company_id=company_id,
            title=title,
            description=description,
            source=source,
            url=url,
            published_at=published_date,
            sentiment=sentiment_score,
        )
        articles.append(article.model_dump())

    return articles


def fetch_news(
    company_id: str,
    company_name: str,
    mode: str = "synthetic",
    count: int = 3,
) -> list[dict[str, Any]]:
    """
    Fetches news either synthetically or via external sources.
    """
    if mode == "synthetic":
        return generate_synthetic_news(company_id, company_name, count=count)

    # Real news fetching placeholder (RSS or NewsAPI)
    logger.info("Real news fetching requested for %s (falling back to synthetic)", company_name)
    return generate_synthetic_news(company_id, company_name, count=count)
