"""
Unit tests for Palier D (M&A Rules Scoring Engine).
"""

from pathlib import Path
import pandas as pd

from scoring_engine.rules_scoring import (
    normalize_min_max,
    assign_recommendation,
    compute_scores,
    write_to_gold,
)


def test_normalize_min_max():
    s = pd.Series([10, 20, 30, 40, 50])
    norm = normalize_min_max(s)
    assert norm.iloc[0] == 0.0
    assert norm.iloc[-1] == 100.0
    assert norm.iloc[2] == 50.0


def test_assign_recommendation():
    assert assign_recommendation(90.0) == "Cible prioritaire"
    assert assign_recommendation(70.0) == "À surveiller"
    assert assign_recommendation(45.0) == "Faible priorité"


def test_compute_scores_and_ranking():
    data = pd.DataFrame([
        {
            "company_id": "CMP-1",
            "name": "High Flyer",
            "growth": 50.0,
            "revenue": 50_000_000,
            "profit_margin": 25.0,
            "market_score": 90.0,
            "innovation_score": 95.0,
            "international_presence": 80.0,
            "financial_health": 85.0,
        },
        {
            "company_id": "CMP-2",
            "name": "Slow Mover",
            "growth": 2.0,
            "revenue": 5_000_000,
            "profit_margin": 2.0,
            "market_score": 30.0,
            "innovation_score": 20.0,
            "international_presence": 10.0,
            "financial_health": 40.0,
        }
    ])

    scored = compute_scores(data)
    assert len(scored) == 2
    assert scored.iloc[0]["company_id"] == "CMP-1"
    assert scored.iloc[0]["ranking"] == 1
    assert scored.iloc[1]["ranking"] == 2
    assert scored.iloc[0]["m_and_a_score"] > scored.iloc[1]["m_and_a_score"]
    assert scored.iloc[0]["recommendation"] == "Cible prioritaire"
    assert "components" in scored.iloc[0]["explanation"]


def test_write_to_gold(tmp_path: Path):
    data = pd.DataFrame([
        {"company_id": "CMP-1", "m_and_a_score": 88.0, "ranking": 1, "explanation": {"score": 88.0}}
    ])
    out = write_to_gold(data, output_path=tmp_path / "targets.parquet")
    assert out.exists()
    read_back = pd.read_parquet(out)
    assert len(read_back) == 1
    assert read_back["m_and_a_score"].iloc[0] == 88.0
