"""
SubroRecover AI - Model Evaluation Module
Evaluates model performance metrics, confusion matrices, and feature importance rankings.
"""

import os
import sys
import json
import logging

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.train import train_model

logger = logging.getLogger("subrorecover.ml.evaluate")

def run_evaluation() -> dict:
    metrics = train_model()
    print("====================================================================")
    print("SUBRORECOVER AI - RANDOM FOREST MODEL EVALUATION REPORT")
    print("====================================================================")
    print(f"Model Architecture:       {metrics['model_name']}")
    print(f"Accuracy:                 {metrics['accuracy']*100:.2f}%")
    print(f"Precision (Weighted):     {metrics['precision_weighted']*100:.2f}%")
    print(f"Recall (Weighted):        {metrics['recall_weighted']*100:.2f}%")
    print(f"F1-Score (Weighted):      {metrics['f1_score_weighted']*100:.2f}%")
    print(f"ROC-AUC (OVR Weighted):   {metrics['roc_auc_weighted']:.4f}")
    print("\nConfusion Matrix [Low, Medium, High]:")
    for row in metrics["confusion_matrix"]:
        print(" ", row)
    print("\nFeature Importance Rankings:")
    for item in metrics["feature_importances"]:
        print(f"  {item['feature']:<25}: {item['importance']*100:>5.2f}%")
    print("====================================================================")
    return metrics

if __name__ == "__main__":
    run_evaluation()
