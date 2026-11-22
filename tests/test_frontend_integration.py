"""
SubroRecover AI - Frontend API Integration Test Suite
Validates that every endpoint requested by the React frontend (under the /api prefix)
returns HTTP 200 with properly structured payloads.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app

client = TestClient(app)

def test_frontend_api_endpoints():
    # 1. Health
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["database_connected"] is True

    # 2. Analytics Overview
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert data["kpis"]["total_claims"]["value"] == 180

    # 3. Analytics Funnel
    res = client.get("/api/analytics/funnel")
    assert res.status_code == 200
    assert "stages" in res.json()

    # 4. Analytics Exposure by Type
    res = client.get("/api/analytics/exposure-by-type")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 5. Analytics Recovery Trends
    res = client.get("/api/analytics/recovery-trends")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 6. Analytics Geographic
    res = client.get("/api/analytics/geographic")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 7. Analytics Needs Attention
    res = client.get("/api/analytics/needs-attention?limit=5")
    assert res.status_code == 200
    assert len(res.json()) <= 5

    # 8. Claims list
    res = client.get("/api/claims?limit=10")
    assert res.status_code == 200
    claims = res.json()
    assert len(claims) > 0

    cid = claims[0]["claim_id"]

    # 9. Claim Dossier
    res = client.get(f"/api/claims/{cid}")
    assert res.status_code == 200
    assert "claim" in res.json()

    # 10. Portfolio 3D
    res = client.get("/api/claims/portfolio-3d")
    assert res.status_code == 200
    pdata = res.json()
    assert "points" in pdata
    assert len(pdata["points"]) == 180

    # 11. Claim 3D Graph
    res = client.get(f"/api/claims/{cid}/graph")
    assert res.status_code == 200
    gdata = res.json()
    assert "nodes" in gdata
    assert "edges" in gdata

    # 12. Demand Letter GET
    res = client.get(f"/api/claims/{cid}/demand-letter")
    assert res.status_code == 200
    assert "letter_text" in res.json()

    # 13. Demand Letter PUT
    res = client.put(f"/api/claims/{cid}/demand-letter", json={
        "letter_text": "Updated demand letter draft.",
        "recipient_carrier": "State Farm"
    })
    assert res.status_code == 200

    # 14. AI Assistant Chat
    res = client.post("/api/assistant/chat", json={
        "query": "What is the liability status of claim CLM-0001?",
        "claim_id": "CLM-0001"
    })
    assert res.status_code == 200
    assert "answer" in res.json()

    # 15. Reports list
    res = client.get("/api/reports?limit=10")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 16. Pipeline status
    res = client.get("/api/pipeline/status")
    assert res.status_code == 200

    # 17. Model metrics
    res = client.get("/api/model/metrics")
    assert res.status_code == 200

    # 18. Static SPA index.html
    res = client.get("/")
    assert res.status_code == 200
    assert "SubroRecover AI" in res.text
