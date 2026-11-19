"""
SubroRecover AI - Data Transformation & Feature Engineering Module
Computes analytical indicators, feature aggregations, and prepares relational payloads.
"""

import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("subrorecover.etl.transformation")

class DataTransformer:
    """Transforms cleaned records and derives domain-specific subrogation features."""

    def __init__(self):
        self.transformation_stats = {
            "features_derived": 0
        }

    def transform_claims(self, df_claims: pd.DataFrame, df_parties: pd.DataFrame, df_reports: pd.DataFrame) -> pd.DataFrame:
        df = df_claims.copy()

        # 1. Days to report
        inc_dt = pd.to_datetime(df["incident_date"])
        rep_dt = pd.to_datetime(df["reported_date"])
        df["days_to_report"] = (rep_dt - inc_dt).dt.days.clip(lower=0)

        # 2. Party counts per claim
        party_counts = df_parties.groupby("claim_id")["party_id"].count().rename("party_count")
        df = df.merge(party_counts, on="claim_id", how="left")
        df["party_count"] = df["party_count"].fillna(1).astype(int)

        # 3. Adverse party identification & fault indicator
        adverse_parties = df_parties[df_parties["party_type"] == "Adverse Driver"]
        adv_fault = adverse_parties.groupby("claim_id")["estimated_fault_percentage"].max().rename("max_adverse_fault")
        df = df.merge(adv_fault, on="claim_id", how="left")
        df["max_adverse_fault"] = df["max_adverse_fault"].fillna(0.0)

        # 4. Police report indicator
        reports_map = df_reports.set_index("claim_id")["police_report_number"]
        df["has_police_report"] = df["claim_id"].map(lambda cid: 1 if cid in reports_map and str(reports_map[cid]) != "N/A" else 0)

        # 5. Financial Exposure & Subro Opportunity Indicator
        df["claim_severity"] = pd.cut(
            df["paid_amount"],
            bins=[-np.inf, 5000, 15000, 35000, np.inf],
            labels=["Low Exposure", "Moderate Exposure", "High Exposure", "Catastrophic Exposure"]
        ).astype(str)

        # Composite subrogation heuristic score (0 to 1)
        # Higher score = higher likelihood of actionable subrogation
        score = (
            (df["max_adverse_fault"] / 100.0) * 0.50 +
            df["has_police_report"] * 0.25 +
            (df["party_count"] > 1).astype(int) * 0.15 +
            (df["days_to_report"] <= 5).astype(int) * 0.10
        )
        df["subro_indicator_score"] = score.round(4)

        self.transformation_stats["features_derived"] += 6
        logger.info(f"Derived subrogation features for {len(df)} claims.")
        return df

    def transform_all(self, datasets: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        transformed = dict(datasets)
        transformed["claims_enhanced"] = self.transform_claims(
            datasets["claims"],
            datasets["involved_parties"],
            datasets["accident_reports"]
        )
        return transformed, self.transformation_stats
