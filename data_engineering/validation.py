"""
SubroRecover AI - Data Validation & Quality Assurance Module
Performs constraint checks, referential integrity verification, and data health audits.
"""

import logging
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger("subrorecover.etl.validation")

class DataValidator:
    """Enforces relational constraints and insurance business rules."""

    def __init__(self):
        self.validation_report = {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "errors": [],
            "warnings": []
        }

    def check_uniqueness(self, df: pd.DataFrame, column: str, dataset_name: str):
        self.validation_report["total_checks"] += 1
        duplicates = df[column].duplicated().sum()
        if duplicates > 0:
            msg = f"Dataset '{dataset_name}' contains {duplicates} duplicate values in primary key '{column}'"
            self.validation_report["errors"].append(msg)
            self.validation_report["failed_checks"] += 1
            logger.warning(msg)
        else:
            self.validation_report["passed_checks"] += 1

    def check_foreign_keys(self, child_df: pd.DataFrame, child_fk: str, parent_df: pd.DataFrame, parent_pk: str, relationship_name: str):
        self.validation_report["total_checks"] += 1
        parent_keys = set(parent_df[parent_pk].dropna())
        child_keys = set(child_df[child_fk].dropna())
        orphans = child_keys - parent_keys
        if orphans:
            msg = f"Foreign key violation in {relationship_name}: {len(orphans)} orphaned keys found (e.g., {list(orphans)[:3]})"
            self.validation_report["errors"].append(msg)
            self.validation_report["failed_checks"] += 1
            logger.error(msg)
        else:
            self.validation_report["passed_checks"] += 1

    def check_numeric_ranges(self, df: pd.DataFrame, column: str, min_val: float, max_val: float, dataset_name: str):
        self.validation_report["total_checks"] += 1
        violations = df[(df[column] < min_val) | (df[column] > max_val)]
        if len(violations) > 0:
            msg = f"Range violation in '{dataset_name}.{column}': {len(violations)} rows outside [{min_val}, {max_val}]"
            self.validation_report["warnings"].append(msg)
            self.validation_report["failed_checks"] += 1
            logger.warning(msg)
        else:
            self.validation_report["passed_checks"] += 1

    def validate_all(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Runs the complete data quality suite across all relational entities."""
        # Uniqueness
        self.check_uniqueness(datasets["customers"], "customer_id", "customers")
        self.check_uniqueness(datasets["policies"], "policy_id", "policies")
        self.check_uniqueness(datasets["claims"], "claim_id", "claims")
        self.check_uniqueness(datasets["accident_reports"], "report_id", "accident_reports")
        self.check_uniqueness(datasets["involved_parties"], "party_id", "involved_parties")

        # Referential Integrity
        self.check_foreign_keys(datasets["policies"], "customer_id", datasets["customers"], "customer_id", "policies -> customers")
        self.check_foreign_keys(datasets["claims"], "policy_id", datasets["policies"], "policy_id", "claims -> policies")
        self.check_foreign_keys(datasets["claims"], "customer_id", datasets["customers"], "customer_id", "claims -> customers")
        self.check_foreign_keys(datasets["accident_reports"], "claim_id", datasets["claims"], "claim_id", "accident_reports -> claims")
        self.check_foreign_keys(datasets["involved_parties"], "claim_id", datasets["claims"], "claim_id", "involved_parties -> claims")

        # Value Ranges
        self.check_numeric_ranges(datasets["claims"], "paid_amount", 0.0, 5000000.0, "claims")
        self.check_numeric_ranges(datasets["involved_parties"], "estimated_fault_percentage", 0.0, 100.0, "involved_parties")

        quality_score = round(self.validation_report["passed_checks"] / max(1, self.validation_report["total_checks"]) * 100.0, 1)
        self.validation_report["quality_score_pct"] = quality_score
        self.validation_report["is_valid"] = (self.validation_report["failed_checks"] == 0)

        logger.info(f"Validation complete: Score={quality_score}% (Passed: {self.validation_report['passed_checks']}/{self.validation_report['total_checks']})")
        return self.validation_report
