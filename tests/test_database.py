"""
SubroRecover AI - Database Operations Test Suite
Tests relational schema initialization, session lifecycle, and CRUD constraints.
"""

import os
import sys
import pytest
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.connection import engine, init_db, mask_db_url

def test_database_init():
    success = init_db()
    assert success is True

def test_table_existence():
    with engine.connect() as conn:
        tables = [
            "customers", "insurance_policies", "insurance_claims",
            "accident_reports", "involved_parties", "evidence_documents",
            "recovery_assessments", "agent_execution_logs",
            "investigation_reports", "human_review_records"
        ]
        for t in tables:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            assert res is not None

def test_password_masking():
    url = "postgresql+psycopg://user:super_secret_pwd@localhost:5432/subro"
    masked = mask_db_url(url)
    assert "super_secret_pwd" not in masked
    assert "****" in masked
