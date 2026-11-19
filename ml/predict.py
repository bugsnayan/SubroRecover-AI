"""
SubroRecover AI - Machine Learning Prediction Module
Serves inference for subrogation case prioritization.
"""

import os
import sys
import logging
import joblib
import pandas as pd
from typing import Dict, Any, List

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logger = logging.getLogger("subrorecover.ml.predict")

MODELS_DIR = "ml/models"
MODEL_FILE = os.path.join(MODELS_DIR, "rf_priority_model.joblib")

_MODEL_CACHE = None

def get_model():
    """Loads and caches the model artifact; triggers training if missing."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    if not os.path.exists(MODEL_FILE):
        logger.info("Model artifact not found. Triggering automated model training...")
        from ml.train import train_model
        train_model()

    _MODEL_CACHE = joblib.load(MODEL_FILE)
    return _MODEL_CACHE

def predict_case_priority(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts investigation priority tier and returns explainability factors.
    """
    artifact = get_model()
    rf = artifact["model"]
    feature_names = artifact["feature_names"]
    feature_encoders = artifact["feature_encoders"]
    target_encoder = artifact["target_encoder"]
    metrics = artifact.get("metrics", {})

    from ml.train import prepare_features
    df_single = pd.DataFrame([claim_data])
    X_single, _, _ = prepare_features(df_single, is_training=False, encoders=feature_encoders)

    # Reorder columns exactly as in training
    X_single = X_single[feature_names]

    # Predict
    pred_idx = rf.predict(X_single)[0]
    proba = rf.predict_proba(X_single)[0]
    pred_class = target_encoder.inverse_transform([pred_idx])[0]

    # Map class probabilities
    classes = target_encoder.classes_
    class_probs = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}

    # Confidence score for predicted class
    conf_score = class_probs.get(pred_class, round(float(max(proba)), 4))

    # Top contributing features for this prediction
    importances = metrics.get("feature_importances", [])
    top_factors = [item["feature"] for item in importances[:3]]

    # Generate explanatory rationale
    fault = claim_data.get("adverse_fault_pct", 0)
    has_pol = claim_data.get("has_police_report", 0)
    amt = claim_data.get("paid_amount", 0)

    explanation = (
        f"Case assigned '{pred_class}' priority ({conf_score*100:.1f}% confidence). "
        f"Key drivers: Adverse fault assessed at {fault}%, "
        f"Police crash report {'verified present' if has_pol else 'unconfirmed'}, "
        f"and total carrier outlay of ${amt:,.2f}."
    )

    return {
        "priority_level": str(pred_class),
        "priority_score": float(conf_score),
        "class_probabilities": class_probs,
        "top_contributing_factors": top_factors,
        "explanation": explanation
    }

if __name__ == "__main__":
    test_claim = {
        "claim_amount": 18500.0,
        "paid_amount": 16200.0,
        "deductible_amount": 500.0,
        "claim_type": "Rear-end Collision",
        "incident_state": "TX",
        "num_parties": 2,
        "has_police_report": 1,
        "citations_issued": 1,
        "adverse_fault_pct": 95.0,
        "days_to_report": 1
    }
    result = predict_case_priority(test_claim)
    print("Inference Result:", result)
