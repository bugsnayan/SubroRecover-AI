"""
SubroRecover AI - Data Pipeline Monitoring & Telemetry Module
Tracks ETL run history, data throughput, validation errors, and pipeline health.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("subrorecover.etl.monitoring")

TELEMETRY_LOG_FILE = "data_engineering/etl_monitoring_history.json"

class PipelineMonitor:
    """Records and serves ETL telemetry and operational health metrics."""

    def __init__(self, history_file: str = TELEMETRY_LOG_FILE):
        self.history_file = history_file
        self.current_run = {
            "run_id": f"ETL-RUN-{int(time.time())}",
            "start_time": datetime.utcnow().isoformat() + "Z",
            "end_time": None,
            "duration_seconds": 0.0,
            "status": "RUNNING",
            "records_ingested": 0,
            "records_cleaned": 0,
            "records_transformed": 0,
            "records_loaded": 0,
            "validation_score_pct": 100.0,
            "errors": [],
            "warnings": []
        }

    def record_success(self, load_stats: Dict[str, Any], validation_report: Dict[str, Any], total_ingested: int):
        self.current_run["end_time"] = datetime.utcnow().isoformat() + "Z"
        start_ts = datetime.fromisoformat(self.current_run["start_time"].replace("Z", ""))
        end_ts = datetime.fromisoformat(self.current_run["end_time"].replace("Z", ""))
        self.current_run["duration_seconds"] = round((end_ts - start_ts).total_seconds(), 2)
        self.current_run["status"] = "SUCCESS"
        self.current_run["records_ingested"] = total_ingested
        self.current_run["records_loaded"] = load_stats.get("total_records_loaded", 0)
        self.current_run["validation_score_pct"] = validation_report.get("quality_score_pct", 100.0)
        self.current_run["errors"] = validation_report.get("errors", [])
        self.current_run["warnings"] = validation_report.get("warnings", [])

        self._save_run_history()
        logger.info(f"ETL run {self.current_run['run_id']} recorded successfully ({self.current_run['duration_seconds']}s).")

    def record_failure(self, error_message: str):
        self.current_run["end_time"] = datetime.utcnow().isoformat() + "Z"
        self.current_run["status"] = "FAILED"
        self.current_run["errors"].append(error_message)
        self._save_run_history()
        logger.error(f"ETL run {self.current_run['run_id']} recorded as FAILED: {error_message}")

    def _save_run_history(self):
        history = self.get_history()
        history.insert(0, self.current_run)
        # Keep last 50 runs
        history = history[:50]
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    @classmethod
    def get_history(cls, history_file: str = TELEMETRY_LOG_FILE) -> List[Dict[str, Any]]:
        if not os.path.exists(history_file):
            return []
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def get_latest_status(cls, history_file: str = TELEMETRY_LOG_FILE) -> Dict[str, Any]:
        history = cls.get_history(history_file)
        if history:
            return history[0]
        return {
            "status": "NO_RUNS",
            "message": "No ETL pipeline execution has been recorded yet."
        }
