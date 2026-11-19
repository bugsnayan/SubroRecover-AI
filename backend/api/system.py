"""
SubroRecover AI - System, Health, Pipeline & Model Telemetry Endpoints
"""

import os
import sys
import json
import logging
from fastapi import APIRouter
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from data_engineering.monitoring import PipelineMonitor
from data_engineering.pipeline import run_etl_pipeline
from ml.evaluate import run_evaluation

logger = logging.getLogger("subrorecover.api.system")
router = APIRouter(tags=["System & Telemetry"])

@router.get("/health")
def health_check():
    """System health check and database connectivity probe."""
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        logger.error(f"Health probe DB connection failure: {e}")

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "service": "SubroRecover AI Backend",
        "database_connected": db_ok,
        "environment": os.getenv("APP_ENV", "development"),
        "llm_configured": bool(os.getenv("GEMINI_API_KEY", "").strip())
    }

@router.get("/pipeline/status")
def get_pipeline_status():
    """Retrieves ETL execution history and latest data health telemetry."""
    latest = PipelineMonitor.get_latest_status()
    history = PipelineMonitor.get_history()
    return {
        "latest_execution": latest,
        "run_history": history
    }

@router.post("/pipeline/run")
def trigger_pipeline_run():
    """Triggers an on-demand execution of the complete ETL data engineering pipeline."""
    result = run_etl_pipeline()
    return result

@router.get("/model/metrics")
def get_model_metrics():
    """Retrieves Random Forest classification metrics, confusion matrix, and feature importances."""
    metrics_file = "ml/models/model_metrics.json"
    if os.path.exists(metrics_file):
        with open(metrics_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return run_evaluation()
