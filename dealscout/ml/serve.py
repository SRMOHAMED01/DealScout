"""
serve.py — Inférence et scoring prédictif d'acquisition en production (Palier E)
"""

from __future__ import annotations

import logging
from typing import Any
import pandas as pd
from xgboost import XGBClassifier

from ml.explain import ShapExplainer
from ml.train import FEATURE_COLUMNS, load_model, train_model, generate_historical_training_data, save_model

logger = logging.getLogger(__name__)


class AcquisitionPredictor:
    """
    Singleton inference service for real-time M&A acquisition probability.
    """

    def __init__(self) -> None:
        self.model: XGBClassifier | None = None
        self.explainer: ShapExplainer | None = None
        self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> None:
        try:
            self.model = load_model()
            self.explainer = ShapExplainer(self.model)
            logger.info("Loaded pre-trained XGBoost model from registry.")
        except Exception:
            logger.info("No saved model found, training initial baseline model...")
            data = generate_historical_training_data(n_samples=800, seed=42)
            clf, _ = train_model(data)
            save_model(clf)
            self.model = clf
            self.explainer = ShapExplainer(clf)
            logger.info("Baseline model trained and registered.")

    def predict(self, company_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Computes acquisition probability (0-100%) and SHAP explanation.
        """
        row = pd.DataFrame([{col: float(company_dict.get(col, 0.0)) for col in FEATURE_COLUMNS}])
        proba = float(self.model.predict_proba(row)[0, 1])
        prob_percent = round(proba * 100.0, 1)

        explanation = self.explainer.explain_instance(company_dict) if self.explainer else {}

        return {
            "acquisition_probability": prob_percent,
            "shap_explanation": explanation,
        }


# Global predictor instance
predictor = AcquisitionPredictor()


def predict_acquisition(company_features: dict[str, Any]) -> dict[str, Any]:
    return predictor.predict(company_features)
