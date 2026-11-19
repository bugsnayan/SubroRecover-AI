"""
SubroRecover AI - Data Cleaning Module
Handles deduplication, missing value imputation, type normalization, and outlier handling.
"""

import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("subrorecover.etl.cleaning")

class DataCleaner:
    """Performs rigorous cleaning on ingested DataFrames."""

    def __init__(self):
        self.cleaning_stats = {
            "duplicates_removed": 0,
            "nulls_imputed": 0,
            "outliers_adjusted": 0
        }

    def clean_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        initial_len = len(df)
        df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)
        self.cleaning_stats["duplicates_removed"] += (initial_len - len(df))

        # Impute missing contact info
        null_email = df["email"].isnull().sum()
        df["email"] = df["email"].fillna("unknown@example.com")
        df["phone"] = df["phone"].fillna("+1-000-000-0000")
        df["risk_profile"] = df["risk_profile"].fillna("Standard")
        self.cleaning_stats["nulls_imputed"] += null_email

        # Strip whitespace
        for col in ["first_name", "last_name", "city", "state", "postal_code"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        return df

    def clean_policies(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        initial_len = len(df)
        df.drop_duplicates(subset=["policy_id"], keep="first", inplace=True)
        self.cleaning_stats["duplicates_removed"] += (initial_len - len(df))

        # Numeric bounds
        df["coverage_limit"] = pd.to_numeric(df["coverage_limit"], errors="coerce").fillna(50000.0)
        df["deductible_amount"] = pd.to_numeric(df["deductible_amount"], errors="coerce").fillna(500.0)
        df.loc[df["coverage_limit"] <= 0, "coverage_limit"] = 50000.0
        df.loc[df["deductible_amount"] < 0, "deductible_amount"] = 500.0

        # Normalize dates
        df["effective_date"] = pd.to_datetime(df["effective_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df["expiration_date"] = pd.to_datetime(df["expiration_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        return df

    def clean_claims(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        initial_len = len(df)
        df.drop_duplicates(subset=["claim_id"], keep="first", inplace=True)
        self.cleaning_stats["duplicates_removed"] += (initial_len - len(df))

        # Amounts
        df["claimed_amount"] = pd.to_numeric(df["claimed_amount"], errors="coerce").fillna(0.0)
        df["paid_amount"] = pd.to_numeric(df["paid_amount"], errors="coerce").fillna(0.0)
        df["deductible_paid"] = pd.to_numeric(df["deductible_paid"], errors="coerce").fillna(0.0)

        # Ensure paid_amount is non-negative
        df.loc[df["paid_amount"] < 0, "paid_amount"] = 0.0

        # Date normalization
        df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df["reported_date"] = pd.to_datetime(df["reported_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        df["claim_status"] = df["claim_status"].fillna("Open")
        df["subrogation_status"] = df["subrogation_status"].fillna("Identified")
        df["description"] = df["description"].fillna("No description provided.")

        return df

    def clean_accident_reports(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.drop_duplicates(subset=["report_id"], keep="first", inplace=True)
        df["officer_narrative"] = df["officer_narrative"].fillna("No officer narrative available.")
        df["citations_issued"] = df["citations_issued"].fillna("None")
        df["diagram_available"] = df["diagram_available"].astype(bool)
        return df

    def clean_involved_parties(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.drop_duplicates(subset=["party_id"], keep="first", inplace=True)
        df["estimated_fault_percentage"] = pd.to_numeric(df["estimated_fault_percentage"], errors="coerce").fillna(0.0)
        df["estimated_fault_percentage"] = df["estimated_fault_percentage"].clip(0.0, 100.0)
        df["citation_received"] = df["citation_received"].astype(bool)
        df["statement_summary"] = df["statement_summary"].fillna("No statement recorded.")
        return df

    def clean_all(self, datasets: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        cleaned = {}
        cleaned["customers"] = self.clean_customers(datasets["customers"])
        cleaned["policies"] = self.clean_policies(datasets["policies"])
        cleaned["claims"] = self.clean_claims(datasets["claims"])
        cleaned["accident_reports"] = self.clean_accident_reports(datasets["accident_reports"])
        cleaned["involved_parties"] = self.clean_involved_parties(datasets["involved_parties"])

        if "evidence_documents" in datasets:
            cleaned["evidence_documents"] = datasets["evidence_documents"].drop_duplicates(subset=["document_id"])
        if "historical_recoveries" in datasets:
            cleaned["historical_recoveries"] = datasets["historical_recoveries"].drop_duplicates(subset=["claim_id"])

        logger.info(f"Data cleaning finished: {self.cleaning_stats}")
        return cleaned, self.cleaning_stats
