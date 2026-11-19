"""
SubroRecover AI - Data Ingestion Module
Handles loading of structured CSV, JSON, and raw feed records.
"""

import os
import json
import logging
from typing import Dict, Any, Tuple
import pandas as pd

logger = logging.getLogger("subrorecover.etl.ingestion")

class DataIngestion:
    """Extracts claim, policy, customer, party, and accident report data."""

    def __init__(self, data_dir: str = "sample_data"):
        self.data_dir = data_dir

    def load_csv(self, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Loads a CSV file and collects ingestion metadata."""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Ingestion source file not found: {filepath}")

        file_size = os.path.getsize(filepath)
        df = pd.read_csv(filepath)
        meta = {
            "source_file": filename,
            "filepath": filepath,
            "file_size_bytes": file_size,
            "raw_row_count": len(df),
            "columns": list(df.columns)
        }
        logger.info(f"Ingested {filename}: {len(df)} records ({file_size} bytes)")
        return df, meta

    def ingest_all(self) -> Dict[str, pd.DataFrame]:
        """Ingests all primary synthetic datasets."""
        datasets = {}
        files = {
            "customers": "customers.csv",
            "policies": "policies.csv",
            "claims": "claims.csv",
            "accident_reports": "accident_reports.csv",
            "involved_parties": "involved_parties.csv",
            "evidence_documents": "evidence_documents.csv",
            "historical_recoveries": "historical_recoveries.csv"
        }

        for key, fname in files.items():
            try:
                df, _ = self.load_csv(fname)
                datasets[key] = df
            except Exception as e:
                logger.error(f"Error ingesting {fname}: {e}")
                raise e

        return datasets
