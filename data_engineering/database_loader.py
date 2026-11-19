"""
SubroRecover AI - Database Loader Module
Loads cleaned and transformed datasets into PostgreSQL / SQLite with transaction safety.
"""

import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from typing import Dict, Any
import pandas as pd
from sqlalchemy import text
from database.connection import engine, init_db

logger = logging.getLogger("subrorecover.etl.loader")

class DatabaseLoader:
    """Loads relational tables into the active database engine."""

    def __init__(self):
        self.engine = engine
        self.load_stats = {
            "customers_loaded": 0,
            "policies_loaded": 0,
            "claims_loaded": 0,
            "reports_loaded": 0,
            "parties_loaded": 0,
            "documents_loaded": 0,
            "total_records_loaded": 0
        }

    def load_table(self, df: pd.DataFrame, table_name: str, primary_key: str) -> int:
        """Loads a DataFrame into a table using append / replace-if-exists strategy."""
        if df.empty:
            return 0

        # Only select columns that exist in the schema
        # We can inspect table columns or write directly with Pandas to_sql with if_exists='append'
        count = 0
        with self.engine.begin() as conn:
            # Delete existing records if reloading sample data to prevent duplicate key constraint
            try:
                conn.execute(text(f"DELETE FROM {table_name}"))
            except Exception as e:
                logger.debug(f"Pre-clean notice for {table_name}: {e}")

            df.to_sql(table_name, conn, if_exists="append", index=False)
            count = len(df)

        logger.info(f"Loaded {count} records into '{table_name}'")
        return count

    def load_all(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Loads all entities in strict foreign key order."""
        init_db()  # Ensure schema exists

        # 1. Customers
        self.load_stats["customers_loaded"] = self.load_table(datasets["customers"], "customers", "customer_id")

        # 2. Policies
        self.load_stats["policies_loaded"] = self.load_table(datasets["policies"], "insurance_policies", "policy_id")

        # 3. Claims (use claims columns matching schema)
        claims_df = datasets["claims"].copy()
        # Drop temporary feature engineering columns if not in SQL schema
        valid_cols = [
            "claim_id", "policy_id", "customer_id", "claim_number", "incident_date",
            "reported_date", "claim_type", "incident_location", "incident_state",
            "claimed_amount", "paid_amount", "deductible_paid", "claim_status",
            "subrogation_status", "description"
        ]
        claims_to_load = claims_df[[c for c in valid_cols if c in claims_df.columns]]
        self.load_stats["claims_loaded"] = self.load_table(claims_to_load, "insurance_claims", "claim_id")

        # 4. Accident Reports
        self.load_stats["reports_loaded"] = self.load_table(datasets["accident_reports"], "accident_reports", "report_id")

        # 5. Involved Parties
        self.load_stats["parties_loaded"] = self.load_table(datasets["involved_parties"], "involved_parties", "party_id")

        # 6. Evidence Documents
        if "evidence_documents" in datasets:
            doc_cols = [
                "document_id", "claim_id", "document_name", "document_type", "file_path",
                "file_size_bytes", "extracted_text", "ocr_confidence", "is_verified", "upload_date"
            ]
            docs_to_load = datasets["evidence_documents"][[c for c in doc_cols if c in datasets["evidence_documents"].columns]]
            self.load_stats["documents_loaded"] = self.load_table(docs_to_load, "evidence_documents", "document_id")

        self.load_stats["total_records_loaded"] = sum([
            self.load_stats["customers_loaded"],
            self.load_stats["policies_loaded"],
            self.load_stats["claims_loaded"],
            self.load_stats["reports_loaded"],
            self.load_stats["parties_loaded"],
            self.load_stats["documents_loaded"]
        ])

        logger.info(f"Database load complete: {self.load_stats['total_records_loaded']} total records loaded.")
        return self.load_stats
