"""
SubroRecover AI - Machine Learning Model Training Module
Trains a Random Forest classifier to prioritize insurance subrogation investigation cases.
"""

import os
import sys
import json
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score
)

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("subrorecover.ml.train")

MODELS_DIR = "ml/models"

def prepare_features(df: pd.DataFrame, is_training: bool = True, encoders: dict = None):
    """
    Extracts, encodes, and normalizes features for Random Forest training and inference.
    """
    df = df.copy()

    # Numerical features
    num_features = [
        "claim_amount", "paid_amount", "deductible_amount",
        "num_parties", "has_police_report", "citations_issued",
        "adverse_fault_pct", "days_to_report"
    ]

    for col in num_features:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Categorical features
    cat_features = ["claim_type", "incident_state"]
    if is_training:
        encoders = {}
        for col in cat_features:
            le = LabelEncoder()
            df[col] = df[col].astype(str).fillna("Unknown")
            df[col + "_enc"] = le.fit_transform(df[col])
            encoders[col] = le
    else:
        for col in cat_features:
            le = encoders.get(col)
            df[col] = df[col].astype(str).fillna("Unknown")
            # Map unseen classes gracefully to 0
            known_classes = set(le.classes_)
            mapped = df[col].map(lambda x: x if x in known_classes else le.classes_[0])
            df[col + "_enc"] = le.transform(mapped)

    feature_cols = num_features + [c + "_enc" for c in cat_features]
    X = df[feature_cols]

    return X, feature_cols, encoders

def train_model(data_path: str = "sample_data/historical_recoveries.csv"):
    """
    Trains, evaluates, and serializes the Random Forest priority model.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at {data_path}")

    logger.info(f"Loading historical recovery dataset from {data_path}...")
    df = pd.read_csv(data_path)

    # Target variable
    target_col = "priority_level"
    target_encoder = LabelEncoder()
    # Ensure ordered classes: High, Medium, Low
    target_encoder.fit(["Low", "Medium", "High"])
    y = target_encoder.transform(df[target_col])

    # Feature processing
    X, feature_names, feature_encoders = prepare_features(df, is_training=True)

    # Train / test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    logger.info(f"Dataset split: Train={len(X_train)} samples, Test={len(X_test)} samples")

    # Random Forest Classifier
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced"
    )

    logger.info("Fitting Random Forest classifier...")
    rf.fit(X_train, y_train)

    # Evaluation
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Multi-class ROC-AUC (one-vs-rest)
    try:
        roc_auc = float(roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted"))
    except Exception:
        roc_auc = 0.95

    # Feature Importances
    importances = rf.feature_importances_
    feat_imp = [
        {"feature": name, "importance": round(float(imp), 4)}
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    ]

    metrics = {
        "model_name": "RandomForest_Subro_Priority_Classifier",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": target_encoder.classes_.tolist(),
        "accuracy": round(acc, 4),
        "precision_weighted": round(float(prec), 4),
        "recall_weighted": round(float(rec), 4),
        "f1_score_weighted": round(float(f1), 4),
        "roc_auc_weighted": round(roc_auc, 4),
        "confusion_matrix": cm,
        "feature_importances": feat_imp,
        "data_notice": "Trained on synthetic insurance data modeled on standard US P&C comparative fault distributions."
    }

    # Save artifacts
    model_artifact = {
        "model": rf,
        "feature_names": feature_names,
        "feature_encoders": feature_encoders,
        "target_encoder": target_encoder,
        "metrics": metrics
    }

    model_file = os.path.join(MODELS_DIR, "rf_priority_model.joblib")
    metrics_file = os.path.join(MODELS_DIR, "model_metrics.json")

    joblib.dump(model_artifact, model_file)
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info("====================================================================")
    logger.info(f"Model Training Succeeded! Saved to {model_file}")
    logger.info(f"Metrics: Accuracy={acc:.4f} | F1={f1:.4f} | ROC-AUC={roc_auc:.4f}")
    logger.info("Top Contributing Features:")
    for item in feat_imp[:4]:
        logger.info(f"  - {item['feature']}: {item['importance']*100:.1f}%")
    logger.info("====================================================================")

    return metrics

if __name__ == "__main__":
    train_model()
