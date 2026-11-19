"""
SubroRecover AI - Machine Learning Test Suite
Tests model artifact persistence, accuracy benchmarks, and real-time prioritization inference.
"""

import os
import sys
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.train import train_model
from ml.predict import predict_case_priority

def test_model_training():
    metrics = train_model()
    assert metrics["accuracy"] >= 0.85
    assert metrics["f1_score_weighted"] >= 0.85
    assert len(metrics["feature_importances"]) > 0

def test_model_prediction():
    sample_claim = {
        "claim_amount": 22000.0,
        "paid_amount": 19500.0,
        "deductible_amount": 500.0,
        "claim_type": "Rear-end Collision",
        "incident_state": "TX",
        "num_parties": 2,
        "has_police_report": 1,
        "citations_issued": 1,
        "adverse_fault_pct": 100.0,
        "days_to_report": 0
    }
    pred = predict_case_priority(sample_claim)
    assert pred["priority_level"] in ["High", "Medium", "Low"]
    assert 0.0 <= pred["priority_score"] <= 1.0
    assert len(pred["top_contributing_factors"]) > 0
    assert "adverse_fault_pct" in pred["top_contributing_factors"]
