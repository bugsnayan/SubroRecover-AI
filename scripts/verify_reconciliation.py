"""
Automated verification of data consistency, 3x reload determinism,
and mathematical reconciliation between KPIs, funnel, and claims table.
"""

import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

def main():
    client = TestClient(app)
    
    print("--- 1. Testing 3x Reload Determinism ---")
    runs = []
    for i in range(1, 4):
        res = client.get("/api/analytics/overview")
        assert res.status_code == 200
        data = res.json()
        runs.append(data)
        print(f"Run {i}: Success. Total claims: {data['kpis']['claims_ingested']['value']}, Total paid: ${data['kpis']['total_paid_exposure']['value']:,.2f}")

    # Check identical across runs
    assert runs[0] == runs[1] == runs[2], "Error: Numbers varied across reloads!"
    print(">>> 3x Reload Determinism PASSED: 100% identical metrics across all 3 runs.\n")

    print("--- 2. Verifying Mathematical Reconciliation with Database & Funnel ---")
    conn = sqlite3.connect("subro_recover.db")
    conn.row_factory = sqlite3.Row

    # Query DB directly
    db_kpi = conn.execute("""
        SELECT
            COUNT(c.claim_id) as total_claims,
            ROUND(SUM(c.paid_amount), 2) as total_paid,
            ROUND(SUM(a.net_recovery_estimate), 2) as projected_rec,
            ROUND(SUM(CASE WHEN c.subrogation_status = 'Closed Recovered' THEN a.net_recovery_estimate ELSE 0 END), 2) as recovered_to_date,
            COUNT(CASE WHEN a.priority_level = 'High' THEN 1 END) as high_urgency_count
        FROM insurance_claims c
        JOIN recovery_assessments a ON c.claim_id = a.claim_id
    """).fetchone()

    # Query Funnel Endpoint
    funnel_res = client.get("/api/analytics/funnel")
    assert funnel_res.status_code == 200
    funnel_stages = {s["id"]: s for s in funnel_res.json()["stages"]}

    kpis = runs[0]["kpis"]

    # 1. Claims Ingested
    assert kpis["claims_ingested"]["value"] == db_kpi["total_claims"] == funnel_stages["ingested"]["count"] == 180
    print(f"✓ Claims Ingested: {kpis['claims_ingested']['value']} claims (matches DB and Funnel)")

    # 2. Total Paid Exposure
    assert round(kpis["total_paid_exposure"]["value"], 2) == round(db_kpi["total_paid"], 2) == 4486249.06
    print(f"✓ Total Paid Exposure: ${kpis['total_paid_exposure']['value']:,.2f} (matches DB)")

    # 3. Projected Recovery
    assert round(kpis["projected_recovery"]["value"], 2) == round(db_kpi["projected_rec"], 2) == 775422.88
    print(f"✓ Projected Recovery: ${kpis['projected_recovery']['value']:,.2f} (matches DB)")

    # 4. Recovered to Date
    assert round(kpis["recovered_to_date"]["value"], 2) == round(db_kpi["recovered_to_date"], 2) == 203966.10
    print(f"✓ Recovered to Date: ${kpis['recovered_to_date']['value']:,.2f} (matches DB)")

    # 5. Funnel Recovered Count Reconciles with Claims Table Status
    recovered_claims_count = conn.execute("SELECT COUNT(*) FROM insurance_claims WHERE subrogation_status = 'Closed Recovered'").fetchone()[0]
    assert funnel_stages["recovered"]["count"] == recovered_claims_count == 18
    print(f"✓ Funnel Recovered Count: {funnel_stages['recovered']['count']} claims (matches claims with status 'Closed Recovered')")

    # 6. Projected Recovery Rate
    expected_proj_rate = round(db_kpi["projected_rec"] / db_kpi["total_paid"] * 100, 1)
    assert kpis["projected_recovery_rate"]["value"] == expected_proj_rate == 17.3
    print(f"✓ Projected Recovery Rate: {kpis['projected_recovery_rate']['value']}% (reconciles with projected / paid)")

    # 7. Actual Recovery Rate
    expected_act_rate = round(db_kpi["recovered_to_date"] / db_kpi["total_paid"] * 100, 1)
    assert kpis["actual_recovery_rate"]["value"] == expected_act_rate == 4.5
    print(f"✓ Actual Recovery Rate: {kpis['actual_recovery_rate']['value']}% (reconciles with recovered / paid)")

    # 8. High-Urgency Demands
    assert kpis["high_urgency_demands"]["value"] == db_kpi["high_urgency_count"] == 27
    print(f"✓ High-Urgency Demands: {kpis['high_urgency_demands']['value']} claims (matches DB High priority count)")

    # 9. Priority Split
    prios = dict(conn.execute("SELECT priority_level, COUNT(*) FROM recovery_assessments GROUP BY priority_level").fetchall())
    assert prios["High"] == 27 and round(27/180*100, 1) == 15.0
    assert prios["Medium"] == 63 and round(63/180*100, 1) == 35.0
    assert prios["Low"] == 90 and round(90/180*100, 1) == 50.0
    print(f"✓ Priority Split: High: {prios['High']} (15.0%), Medium: {prios['Medium']} (35.0%), Low: {prios['Low']} (50.0%)")

    print("\n>>> ALL MATHEMATICAL RECONCILIATIONS PASSED WITH ZERO DISCREPANCIES! <<<")

if __name__ == "__main__":
    main()
