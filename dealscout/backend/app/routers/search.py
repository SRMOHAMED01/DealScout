"""
search.py â€” Multi-criteria M&A target search router (Palier F)
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.company import PaginatedResponse
from app.services.scoring_service import service

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=PaginatedResponse)
def search_targets(
    sector: str | None = Query(default=None, description="e.g. FinTech, SaaS, AI"),
    country: str | None = Query(default=None, description="e.g. Morocco, United States, France"),
    min_growth: float | None = Query(default=None, description="Minimum revenue growth YoY in %"),
    min_revenue: float | None = Query(default=None, description="Minimum revenue in USD"),
    min_score: float | None = Query(default=None, description="Minimum M&A score (0-100)"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Multi-criteria search filtering investment targets sorted by M&A score.
    Example: Fonds d'investissement cherchant 'FinTech au Maroc avec croissance > 20%'.
    """
    items, total = service.search(
        sector=sector,
        country=country,
        min_growth=min_growth,
        min_revenue=min_revenue,
        min_score=min_score,
        limit=limit,
        offset=offset,
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }

