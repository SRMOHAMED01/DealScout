"""
explain.py — Explicabilité SHAP (Palier E.3)

À IMPLÉMENTER : même logique que CreditPulse.
1. load_model(path)
2. get_shap_values(model, company_features_df) -> shap.Explanation
3. format_explanation(shap_values, feature_names) -> list[dict]
   [{"feature": "growth", "impact": +0.28, "direction": "increases_probability"}, ...]
"""
