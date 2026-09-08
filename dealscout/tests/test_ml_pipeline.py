"""
Unit tests for Palier E (Machine Learning XGBoost + SHAP).
"""

from pathlib import Path
from ml.train import (
    generate_historical_training_data,
    train_model,
    save_model,
    load_model,
)
from ml.explain import ShapExplainer
from ml.serve import predict_acquisition


def test_generate_historical_data():
    df = generate_historical_training_data(n_samples=200, seed=10)
    assert len(df) == 200
    assert "acquired" in df.columns
    assert set(df["acquired"].unique()).issubset({0, 1})
    assert df["growth"].min() is not None


def test_train_and_save_model(tmp_path: Path):
    df = generate_historical_training_data(n_samples=300, seed=42)
    model, metrics = train_model(df)

    assert "roc_auc" in metrics
    assert metrics["roc_auc"] >= 0.65  # Baseline sensible performance
    assert "f1" in metrics

    model_path = tmp_path / "test_model.joblib"
    saved = save_model(model, filepath=model_path)
    assert saved.exists()

    loaded = load_model(filepath=model_path)
    assert loaded is not None


def test_shap_explainability_and_serve():
    company = {
        "growth": 35.0,
        "revenue": 40_000_000.0,
        "profit_margin": 22.0,
        "market_score": 85.0,
        "innovation_score": 90.0,
        "international_presence": 60.0,
        "financial_health": 80.0,
    }

    result = predict_acquisition(company)
    assert "acquisition_probability" in result
    assert 0.0 <= result["acquisition_probability"] <= 100.0
    assert "shap_explanation" in result

    shap_exp = result["shap_explanation"]
    assert "feature_contributions" in shap_exp
    assert "growth" in shap_exp["feature_contributions"]
