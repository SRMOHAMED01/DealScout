"""
rules_scoring.py — Calcul du score M&A par règles pondérées (Palier D)

FORMULE OFFICIELLE :
  M&A Score = Growth * 0.30
            + Revenue * 0.20
            + Profitability * 0.20
            + Market_Opportunity * 0.15
            + Innovation * 0.10
            + International_Presence * 0.05

Chaque composante est normalisée (min-max scaling de 0 à 100) avant pondération.
Fournit également l'explication granulaire (forces / risques).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
import pandas as pd

logger = logging.getLogger(__name__)

# Poids officiels du scoring M&A v1
WEIGHTS = {
    "growth": 0.30,
    "revenue": 0.20,
    "profitability": 0.20,
    "market": 0.15,
    "innovation": 0.10,
    "international": 0.05,
}


def normalize_min_max(series: pd.Series) -> pd.Series:
    """
    Normalizes a numerical series to [0, 100] using min-max scaling.
    If min == max, returns 50.0 for all elements.
    """
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    min_val = s.min()
    max_val = s.max()

    if max_val == min_val:
        return pd.Series(50.0, index=s.index)

    normalized = ((s - min_val) / (max_val - min_val)) * 100.0
    return normalized.round(2)


def assign_recommendation(score: float) -> str:
    """
    Assigns a business recommendation based on overall M&A score.
    """
    if score >= 85.0:
        return "Cible prioritaire"
    elif score >= 60.0:
        return "À surveiller"
    return "Faible priorité"


def compute_explanation(row: pd.Series, norm_row: pd.Series) -> dict[str, Any]:
    """
    Produces transparent human-readable explanation of the score components,
    strengths, and risks for M&A analysts.
    """
    score = float(row.get("m_and_a_score", 0.0))

    components = {
        "growth": round(float(norm_row["norm_growth"]) * WEIGHTS["growth"], 2),
        "revenue": round(float(norm_row["norm_revenue"]) * WEIGHTS["revenue"], 2),
        "profitability": round(float(norm_row["norm_profitability"]) * WEIGHTS["profitability"], 2),
        "market": round(float(norm_row["norm_market"]) * WEIGHTS["market"], 2),
        "innovation": round(float(norm_row["norm_innovation"]) * WEIGHTS["innovation"], 2),
        "international": round(float(norm_row["norm_international"]) * WEIGHTS["international"], 2),
    }

    strengths = []
    risks = []

    # Financial analysis
    growth = float(row.get("growth", 0.0))
    if growth >= 25.0:
        strengths.append(f"Forte croissance annuelle (+{growth:.1f}%)")
    elif growth < 5.0:
        risks.append(f"Croissance faible ou atone ({growth:.1f}%)")

    margin = float(row.get("profit_margin", 0.0))
    if margin >= 18.0:
        strengths.append(f"Excellente rentabilité opérationnelle ({margin:.1f}%)")
    elif margin < 0.0:
        risks.append(f"Rentabilité négative ({margin:.1f}%)")

    health = float(row.get("financial_health", 50.0))
    if health >= 75.0:
        strengths.append("Bilan solide et faible endettement")
    elif health < 40.0:
        risks.append("Santé financière fragile ou endettement élevé")

    market_score = float(row.get("market_score", 50.0))
    if market_score >= 80.0:
        strengths.append("Opportunité de marché et dynamique sectorielle majeures")

    news_sent = float(row.get("news_sentiment", 0.0))
    if news_sent >= 0.40:
        strengths.append("Sentiment médiatique très favorable")
    elif news_sent <= -0.30:
        risks.append("Actualité récente sous tension médiatique")

    return {
        "score": score,
        "recommendation": assign_recommendation(score),
        "components": components,
        "strengths": strengths,
        "risks": risks,
    }


def compute_scores(df_company_360: pd.DataFrame) -> pd.DataFrame:
    """
    Computes M&A scores for a Company 360 DataFrame, ranks companies, and
    generates score explanations.
    """
    if df_company_360.empty:
        return pd.DataFrame()

    df = df_company_360.copy()

    # Normalize components
    norm_df = pd.DataFrame(index=df.index)
    norm_df["norm_growth"] = normalize_min_max(df["growth"] if "growth" in df.columns else df.get("revenue_growth", 0))
    norm_df["norm_revenue"] = normalize_min_max(df["revenue"])
    norm_df["norm_profitability"] = normalize_min_max(df["profit_margin"])
    norm_df["norm_market"] = normalize_min_max(df.get("market_score", 50.0))
    norm_df["norm_innovation"] = normalize_min_max(df.get("innovation_score", 50.0))
    norm_df["norm_international"] = normalize_min_max(df.get("international_presence", 50.0))

    # Apply weighted formula
    df["m_and_a_score"] = (
        norm_df["norm_growth"] * WEIGHTS["growth"] +
        norm_df["norm_revenue"] * WEIGHTS["revenue"] +
        norm_df["norm_profitability"] * WEIGHTS["profitability"] +
        norm_df["norm_market"] * WEIGHTS["market"] +
        norm_df["norm_innovation"] * WEIGHTS["innovation"] +
        norm_df["norm_international"] * WEIGHTS["international"]
    ).round(2)

    # Ranking
    df = df.sort_values(by="m_and_a_score", ascending=False).reset_index(drop=True)
    df["ranking"] = df.index + 1
    df["recommendation"] = df["m_and_a_score"].apply(assign_recommendation)

    # Risk level classification
    def evaluate_risk(row: pd.Series) -> str:
        health = float(row.get("financial_health", 50.0))
        margin = float(row.get("profit_margin", 0.0))
        if health < 40.0 or margin < -10.0:
            return "High"
        elif health < 65.0:
            return "Medium"
        return "Low"

    df["risk_level"] = df.apply(evaluate_risk, axis=1)

    # Explanations
    explanations = []
    for idx in range(len(df)):
        row = df.iloc[idx]
        norm_row = norm_df.iloc[idx]
        explanations.append(compute_explanation(row, norm_row))
    df["explanation"] = explanations

    return df


def write_to_gold(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """
    Persists scored investment targets to Gold storage (Parquet).
    """
    if output_path is None:
        target_dir = Path("data") / "gold" / "investment_targets"
        target_dir.mkdir(parents=True, exist_ok=True)
        out_file = target_dir / "investment_targets.parquet"
    else:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert complex dict column to json string for parquet compatibility if needed
    save_df = df.copy()
    if "explanation" in save_df.columns:
        import json
        save_df["explanation_json"] = save_df["explanation"].apply(lambda x: json.dumps(x, ensure_ascii=False))
        save_df = save_df.drop(columns=["explanation"])

    save_df.to_parquet(out_file, index=False, engine="pyarrow")
    logger.info("Saved %d investment targets to Gold: %s", len(save_df), out_file)
    return out_file


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("DealScout Rules Scoring Engine ready.")
