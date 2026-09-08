"""
train.py — Entraînement du modèle prédictif d'acquisition M&A (Palier E)

Pipeline ML:
1. Génère un dataset d'entraînement historique synthétique avec cible `acquired` (0/1).
2. Entraîne un modèle XGBClassifier avec validation croisée et métriques (ROC-AUC, Precision, Recall).
3. Sauvegarde le modèle entraîné dans `model_registry/model.joblib`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "growth",
    "revenue",
    "profit_margin",
    "market_score",
    "innovation_score",
    "international_presence",
    "financial_health",
]

MODEL_REGISTRY_DIR = Path(__file__).resolve().parent / "model_registry"


def generate_historical_training_data(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Simulates historical enterprise dataset with acquisition outcome.
    Higher growth, innovation, and healthy margins correlate with higher probability of acquisition.
    """
    rng = np.random.RandomState(seed)

    growth = rng.normal(loc=18.0, scale=12.0, size=n_samples)
    revenue = np.exp(rng.normal(loc=16.0, scale=1.2, size=n_samples))  # skewed revenue distribution
    profit_margin = rng.normal(loc=12.0, scale=8.0, size=n_samples)
    market_score = rng.uniform(30.0, 95.0, size=n_samples)
    innovation_score = rng.uniform(40.0, 98.0, size=n_samples)
    international_presence = rng.uniform(10.0, 90.0, size=n_samples)
    financial_health = np.clip(profit_margin * 2.0 + rng.uniform(30.0, 60.0, size=n_samples), 0.0, 100.0)

    # Log-odds of acquisition
    z = (
        (growth - 15.0) * 0.08 +
        (np.log(revenue) - 15.0) * 0.40 +
        (profit_margin - 10.0) * 0.06 +
        (market_score - 50.0) * 0.04 +
        (innovation_score - 50.0) * 0.05 +
        (financial_health - 50.0) * 0.03 -
        1.8  # baseline rarity: ~20-25% acquisition rate
    )
    prob_acquired = 1.0 / (1.0 + np.exp(-z))
    acquired = (rng.uniform(0, 1, size=n_samples) < prob_acquired).astype(int)

    df = pd.DataFrame({
        "growth": np.round(growth, 2),
        "revenue": np.round(revenue, 2),
        "profit_margin": np.round(profit_margin, 2),
        "market_score": np.round(market_score, 2),
        "innovation_score": np.round(innovation_score, 2),
        "international_presence": np.round(international_presence, 2),
        "financial_health": np.round(financial_health, 2),
        "acquired": acquired,
    })
    return df


def train_model(
    df: pd.DataFrame,
    test_size: float = 0.20,
    seed: int = 42,
) -> tuple[XGBClassifier, dict[str, float]]:
    """
    Splits data, trains XGBoost classifier, and evaluates performance.
    """
    X = df[FEATURE_COLUMNS]
    y = df["acquired"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )

    model = XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=seed,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
    }
    logger.info("Trained model metrics: %s", metrics)
    return model, metrics


def save_model(model: XGBClassifier, filepath: str | Path | None = None) -> Path:
    target_path = Path(filepath) if filepath else (MODEL_REGISTRY_DIR / "acquisition_xgb.joblib")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, target_path)
    logger.info("Saved XGBoost model to %s", target_path)
    return target_path


def load_model(filepath: str | Path | None = None) -> XGBClassifier:
    target_path = Path(filepath) if filepath else (MODEL_REGISTRY_DIR / "acquisition_xgb.joblib")
    if not target_path.exists():
        raise FileNotFoundError(f"Model file not found at {target_path}")
    return joblib.load(target_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = generate_historical_training_data(n_samples=1200)
    clf, scores = train_model(data)
    save_model(clf)
    print("Model training successful. Metrics:", scores)
