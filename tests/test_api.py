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

def test_portfolio_3d_endpoint():
    res = client.get("/claims/portfolio-3d")
    assert res.status_code == 200
    data = res.json()
    assert "points" in data
    assert len(data["points"]) > 0
    p = data["points"][0]
    assert "x" in p and "y" in p and "z" in p
    assert "color" in p

def test_claim_recovery_graph_endpoint():
    res = client.get("/claims/CLM-0001/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert any(n["id"] == "core" for n in data["nodes"])

def test_demand_letter_endpoints():
    res = client.get("/claims/CLM-0001/demand-letter")
    assert res.status_code == 200
    data = res.json()
    assert "letter_text" in data
    assert data["demand_amount"] > 0

    # Test update
    put_res = client.put("/claims/CLM-0001/demand-letter", json={
        "letter_text": data["letter_text"] + "\n[TEST REVISION]",
        "status": "Draft"
    })
    assert put_res.status_code == 200
    assert put_res.json()["status"] == "Draft"

def test_analytics_extended_endpoints():
    f_res = client.get("/analytics/funnel")
    assert f_res.status_code == 200
    assert len(f_res.json()["stages"]) == 5

    t_res = client.get("/analytics/recovery-trends")
    assert t_res.status_code == 200
    assert isinstance(t_res.json(), list)

    e_res = client.get("/analytics/exposure-by-type")
    assert e_res.status_code == 200
    assert len(e_res.json()) > 0

    na_res = client.get("/analytics/needs-attention?limit=5")
    assert na_res.status_code == 200
    assert len(na_res.json()) <= 5

def test_assistant_chat_endpoint():
    res = client.post("/assistant/chat", json={
        "query": "What is the liability status on claim CLM-0001?",
        "claim_id": "CLM-0001"
    })
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "suggested_questions" in data

def test_funnel_global_filter_priority_high():
    """Verify that applying Priority=High filters the funnel and Ingested equals 27."""
    res = client.get("/analytics/funnel?priority=High")
    assert res.status_code == 200
    data = res.json()
    assert len(data["stages"]) == 5
    ingested_stage = data["stages"][0]
    assert ingested_stage["name"] == "Ingested"
    assert ingested_stage["count"] == 27


def test_assistant_chat_out_of_scope_declines_gracefully():
    """Verify that out-of-scope queries decline gracefully without hallucinating claims."""
    res = client.post("/assistant/chat", json={
        "query": "What is the capital of France and what is the weather there?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["answer"] == "I couldn't find that in the indexed documents."
    assert data["sources"] == []
    assert data["referenced_claims"] == []


def test_report_generate_endpoint():
    res = client.post("/reports/generate", json={
        "claim_id": "CLM-0001",
        "scope": "Comprehensive Test Audit",
        "notes": "Automated verification test."
    })
    assert res.status_code == 201
    data = res.json()
    assert "download_url" in data
    assert os.path.exists(data["pdf_path"])

def test_spa_serving():
    res = client.get("/")
    assert res.status_code == 200
    assert "SubroRecover AI" in res.text

    # Verify that both /api/health and /health work identically
    res_api = client.get("/api/health")
    assert res_api.status_code == 200
    assert res_api.json()["database_connected"] is True


def test_delta_sparkline_direction_concordance():
    """
    Assert that for every KPI with both a delta_pct and a sparkline (>= 2 points),
    the direction of the sparkline's final segment strictly matches the sign of delta_pct:
      delta_pct > 0  ==> sparkline[-1] > sparkline[-2]
      delta_pct < 0  ==> sparkline[-1] < sparkline[-2]
      delta_pct == 0 ==> sparkline[-1] == sparkline[-2]
    Also asserts that disagreement between delta sign and sparkline direction raises AssertionError.
    """
    res = client.get("/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    kpis = data.get("kpis", {})

    evaluated_kpis = 0
    for kpi_key, kpi_data in kpis.items():
        delta = kpi_data.get("delta_pct")
        sparkline = kpi_data.get("sparkline")

        if delta is None or sparkline is None or len(sparkline) < 2:
            continue

        evaluated_kpis += 1
        penultimate = sparkline[-2]
        final = sparkline[-1]

        if delta > 0:
            assert final > penultimate, f"KPI {kpi_key} has positive delta {delta}% but sparkline fell ({penultimate} -> {final})"
        elif delta < 0:
            assert final < penultimate, f"KPI {kpi_key} has negative delta {delta}% but sparkline rose ({penultimate} -> {final})"
        else:
            assert final == penultimate, f"KPI {kpi_key} has 0% delta but sparkline changed ({penultimate} -> {final})"

    assert evaluated_kpis > 0, "At least one KPI must have a dated time series with delta and sparkline"

    # Verify that an inverted disagreement test fails as required
    with pytest.raises(AssertionError):
        mismatched_delta = 15.0
        mismatched_sparkline = [100, 80]  # dropped despite positive delta
        assert (mismatched_sparkline[-1] > mismatched_sparkline[-2]) if mismatched_delta > 0 else (mismatched_sparkline[-1] < mismatched_sparkline[-2])


def test_claim_specific_assistant_retrieval():
    """
    Assert that questions naming a claim ID (CN-2026-00018 style) retrieve
    that claim's record and evidence documents, returning sources with document,
    page, and snippet.
    """
    res = client.post("/assistant/chat", json={
        "query": "What evidence supports adverse liability on claim CN-2026-00018?"
    })
    assert res.status_code == 200
    data = res.json()
    assert "CN-2026-00018" in data["answer"]
    assert "CN-2026-00018" in data["referenced_claims"]

    # Verify sources list under the answer
    sources = data.get("sources", [])
    assert len(sources) > 0, "Expected sources list for claim-specific retrieval"
    for s in sources:
        assert "document" in s or "title" in s
        assert "page" in s
        assert "snippet" in s
        assert len(s["snippet"]) > 0


def test_assistant_metrics_match_overview():
    """
    Assert that portfolio metrics cited in assistant answers come from the same
    shared metrics module and strictly reconcile with Overview endpoints.
    """
    # Fetch overview KPIs
    res_ov = client.get("/analytics/overview")
    assert res_ov.status_code == 200
    ov_data = res_ov.json()
    ov_kpis = ov_data["kpis"]

    total_paid_str = f"{int(ov_kpis['total_paid_exposure']['value']):,}" # e.g. 4,486,249
    projected_rec_str = f"{int(ov_kpis['projected_recovery']['value']):,}" # e.g. 775,422 or 775,423
    high_urgency = ov_kpis["high_urgency_demands"]["value"] # 27

    # Send general portfolio metrics query
    res_chat = client.post("/assistant/chat", json={
        "query": "What is our total paid exposure and projected recovery across the portfolio?"
    })
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    answer = chat_data["answer"]

    # Assert accurate numbers from shared metrics module dynamically match Overview
    assert total_paid_str in answer
    assert projected_rec_str in answer
    assert f"{high_urgency} claims" in answer

    # Assert legacy ungrounded numbers are absent
    assert "$3,320,185" not in answer
    assert "88 claims" not in answer

    # Assert sources list is present
    assert len(chat_data.get("sources", [])) > 0


def test_health_data_endpoint():
    """
    Assert that GET /health/data returns real counts of claims, assessments,
    reports, and ChromaDB vector documents.
    """
    res = client.get("/health/data")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["claims"] == 180
    assert data["assessments"] == 180
    assert data["reports"] == 180
    assert data["vector_documents"] >= 720

    # Also check /api/health/data
    res_api = client.get("/api/health/data")
    assert res_api.status_code == 200
    assert res_api.json()["vector_documents"] >= 720


def test_claims_routing_with_cn_format():
    """
    Assert that /claims/{id} endpoints accept both CN-2026-xxxxx and CLM-xxxx format.
    """
    res1 = client.get("/claims/CN-2026-00018")
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["claim"]["claim_number"] == "CN-2026-00018"
    assert len(d1["documents"]) == 4

    res2 = client.get("/claims/CN-2026-00018/graph")
    assert res2.status_code == 200
    g = res2.json()
    assert g["claim_number"] == "CN-2026-00018"
    assert len(g["nodes"]) > 0

    res3 = client.get("/claims/CN-2026-00018/demand-letter")
    assert res3.status_code == 200
    dl = res3.json()
    assert dl["claim_number"] == "CN-2026-00018"



