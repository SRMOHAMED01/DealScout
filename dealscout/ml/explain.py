"""
explain.py — Explicabilité des prédictions ML avec SHAP (Palier E.3)

Permet d'expliquer pourquoi une entreprise a une probabilité élevée ou faible
d'acquisition en décomposant les contributions des features.
"""

from __future__ import annotations

import logging
from typing import Any
import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier

from ml.train import FEATURE_COLUMNS

logger = logging.getLogger(__name__)


class ShapExplainer:
    def __init__(self, model: XGBClassifier) -> None:
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def explain_instance(self, features_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Computes SHAP values for a single company feature set.
        """
        # Align features
        row = pd.DataFrame([{col: float(features_dict.get(col, 0.0)) for col in FEATURE_COLUMNS}])

        shap_values = self.explainer(row)
        values = shap_values.values[0]
        base_value = float(shap_values.base_values[0]) if hasattr(shap_values.base_values, "__len__") else float(shap_values.base_values)

        contributions = {}
        top_positive_factors = []
        top_negative_factors = []

        for col, val in zip(FEATURE_COLUMNS, values):
            score_contrib = round(float(val), 4)
            contributions[col] = score_contrib

            feature_val = features_dict.get(col, 0.0)
            if score_contrib > 0.05:
                top_positive_factors.append({
                    "feature": col,
                    "value": feature_val,
                    "impact": score_contrib,
                    "direction": "positive",
                })
            elif score_contrib < -0.05:
                top_negative_factors.append({
                    "feature": col,
                    "value": feature_val,
                    "impact": score_contrib,
                    "direction": "negative",
                })

        top_positive_factors.sort(key=lambda x: x["impact"], reverse=True)
        top_negative_factors.sort(key=lambda x: x["impact"])

        return {
            "base_value": round(base_value, 4),
            "feature_contributions": contributions,
            "positive_drivers": top_positive_factors,
            "negative_drivers": top_negative_factors,
        }
