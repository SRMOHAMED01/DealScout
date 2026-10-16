"""
companies.py â€” Company endpoints for FastAPI (Palier F)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Depends

from app.schemas.company import (
    CompanyScoreSchema,
    MarketSectorSummary,
    PaginatedResponse,
)
from app.services.scoring_service import service
from app.routers.auth import get_current_user

router = APIRouter(tags=["Companies"])


@router.get("/companies", response_model=PaginatedResponse)
def list_companies(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Returns a paginated list of analyzed companies.
    """
    items, total = service.get_all(limit=limit, offset=offset)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@router.get("/companies/{company_id}")
def get_company(company_id: str):
    """
    Returns the comprehensive Company 360 profile.
    """
    comp = service.get_by_id(company_id)
    if not comp:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")
    return comp


@router.get("/companies/{company_id}/score", response_model=CompanyScoreSchema)
def get_company_score(company_id: str):
    """
    Returns the M&A opportunity score, ranking, strengths, and risk analysis.
    """
    score_data = service.get_score_by_id(company_id)
    if not score_data:
        raise HTTPException(status_code=404, detail=f"Score not available for company '{company_id}'")
    return score_data


@router.get("/market-analysis", response_model=list[MarketSectorSummary])
def get_market_analysis():
    """
    Returns sector-level aggregations and comparative M&A dynamics.
    """
    return service.market_analysis()


@router.get("/companies/{company_id}/ml-score")
def get_company_ml_score(
    company_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Returns the ML acquisition probability (XGBoost + SHAP) for a company.
    Requires authentication.
    """
    comp = service.get_by_id(company_id)
    if not comp:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")

    features = {
        "growth": float(comp.get("growth", comp.get("revenue_growth", 0.0))),
        "revenue": float(comp.get("revenue", 0.0)),
        "profit_margin": float(comp.get("profit_margin", 0.0)),
        "market_score": float(comp.get("market_score", 50.0)),
        "innovation_score": float(comp.get("innovation_score", 50.0)),
        "international_presence": float(comp.get("international_presence", 50.0)),
        "financial_health": float(comp.get("financial_health", 50.0)),
    }

    predict_acquisition = _get_predict_acquisition()
    result = predict_acquisition(features)
    return {
        "company_id": company_id,
        "name": comp.get("name"),
        "acquisition_probability": result["acquisition_probability"],
        "shap_explanation": result["shap_explanation"],
    }


def _get_predict_acquisition():
    from ml.serve import predict_acquisition  # lazy: shap/scipy optional at import time
    return predict_acquisition

