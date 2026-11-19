"""
SubroRecover AI - FastAPI Backend & PDF Generation Test Suite
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from reports.report_generator import generate_subrogation_pdf

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert data["database_connected"] is True

def test_api_claims():
    res = client.get("/claims?limit=5")
    assert res.status_code == 200
    claims = res.json()
    assert len(claims) > 0

    cid = claims[0]["claim_id"]
    res_single = client.get(f"/claims/{cid}")
    assert res_single.status_code == 200
    dossier = res_single.json()
    assert "claim" in dossier
    assert "parties" in dossier

def test_api_analytics():
    res = client.get("/analytics/overview")
    assert res.status_code == 200
    overview = res.json()
    assert overview["total_claims_analyzed"] > 0
    assert "priority_distribution" in overview

def test_pdf_report_compilation():
    test_dossier = {
        "claim_id": "CLM-PDF-TEST",
        "report_id": "RPT-PDF-TEST",
        "executive_summary": "Test executive summary for PDF verification.",
        "claim_overview": {
            "claim_number": "CN-TEST",
            "policy_holder": "Jane Tester",
            "coverage_limit": 100000.0,
            "paid_loss_amount": 12500.0,
            "deductible_amount": 500.0,
            "claim_narrative": "Insured vehicle was struck while stationary."
        },
        "evidentiary_findings": {
            "adverse_party_name": "Adverse Driver",
            "adverse_vehicle": "Ford F-150",
            "adverse_carrier": "State Farm"
        },
        "verified_facts": ["Police crash report indicates adverse driver ran red light."],
        "statutory_citations": ["Sec. 544.007 Disregard Traffic Signal"],
        "liability_assessment": {
            "adverse_fault_pct": 100.0,
            "negligence_doctrine": "Modified Comparative Fault (51% Bar)",
            "liability_rationale": "Clear third-party liability based on police citation."
        },
        "recovery_financials": {
            "gross_recovery_estimate": 13000.0,
            "insured_deductible_recovery": 500.0,
            "estimated_collection_cost": 625.0,
            "net_carrier_recovery": 11875.0
        },
        "prioritization_metrics": {
            "priority_level": "High",
            "priority_score": 0.98
        },
        "recommended_actions": ["Issue immediate demand letter."],
        "missing_documentation_checklist": ["None."],
        "governance_disclaimer": "Automated decision-support test."
    }

    out_file = generate_subrogation_pdf(test_dossier)
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000
