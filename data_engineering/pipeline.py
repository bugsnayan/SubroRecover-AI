"""
SubroRecover AI - Master Data Engineering Pipeline
Coordinates extraction, cleaning, feature transformation, validation, loading, and monitoring.
"""

import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from typing import Dict, Any

from data_engineering.ingestion import DataIngestion
from data_engineering.cleaning import DataCleaner
from data_engineering.transformation import DataTransformer
from data_engineering.validation import DataValidator
from data_engineering.database_loader import DatabaseLoader
from data_engineering.monitoring import PipelineMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("subrorecover.etl.pipeline")

def run_etl_pipeline(data_dir: str = "sample_data") -> Dict[str, Any]:
    """
    Executes the full end-to-end Data Engineering ETL workflow.
    Returns complete pipeline execution telemetry and validation summary.
    """
    monitor = PipelineMonitor()
    logger.info("====================================================================")
    logger.info("Starting SubroRecover AI Data Engineering Pipeline Execution")
    logger.info("====================================================================")

    try:
        # Step 1: Extraction / Ingestion
        logger.info("[Step 1/5] Ingesting source datasets...")
        ingestion = DataIngestion(data_dir=data_dir)
        raw_datasets = ingestion.ingest_all()
        total_ingested = sum(len(df) for df in raw_datasets.values())
        logger.info(f"Ingested {total_ingested} records across {len(raw_datasets)} entities.")

        # Step 2: Cleaning & Normalization
        logger.info("[Step 2/5] Cleaning and deduplicating records...")
        cleaner = DataCleaner()
        cleaned_datasets, cleaning_stats = cleaner.clean_all(raw_datasets)

        # Step 3: Transformation & Feature Engineering
        logger.info("[Step 3/5] Transforming features and deriving subrogation indicators...")
        transformer = DataTransformer()
        transformed_datasets, transform_stats = transformer.transform_all(cleaned_datasets)

        # Step 4: Quality Assurance & Constraint Validation
        logger.info("[Step 4/5] Executing validation rules and referential integrity audit...")
        validator = DataValidator()
        validation_report = validator.validate_all(transformed_datasets)

        # Step 5: Relational Database Loading
        logger.info("[Step 5/5] Loading records into relational database...")
        loader = DatabaseLoader()
        load_stats = loader.load_all(transformed_datasets)

        # Record pipeline completion
        monitor.record_success(load_stats, validation_report, total_ingested)

        result = {
            "status": "SUCCESS",
            "run_id": monitor.current_run["run_id"],
            "duration_seconds": monitor.current_run["duration_seconds"],
            "total_ingested": total_ingested,
            "total_loaded": load_stats["total_records_loaded"],
            "load_breakdown": load_stats,
            "cleaning_stats": cleaning_stats,
            "validation_report": validation_report
        }

        logger.info("====================================================================")
        logger.info(f"ETL Pipeline Complete! Status: SUCCESS | Loaded: {load_stats['total_records_loaded']} rows")
        logger.info("====================================================================")
        return result

    except Exception as e:
        logger.error(f"ETL Pipeline execution failed: {e}", exc_info=True)
        monitor.record_failure(str(e))
        return {
            "status": "FAILED",
            "error": str(e),
            "run_id": monitor.current_run["run_id"]
        }

if __name__ == "__main__":
    result = run_etl_pipeline()
    if result["status"] != "SUCCESS":
        sys.exit(1)
