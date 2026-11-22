"""
SubroRecover AI - Deterministic Assessment Seeding Script
Populates recovery_assessments, agent_execution_logs, and investigation_reports
for all 180 claims in sample_data using fixed seed=42 and internally consistent
subrogation mathematics.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Ensure repo root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from database.connection import engine

def seed_all_assessments():
    print("Seeding assessments deterministically across all 180 claims (seed=42)...")
    random.seed(42)

    with engine.connect() as conn:
        claims = conn.execute(text("""
            SELECT c.*, r.officer_narrative, r.citations_issued, r.police_report_number
            FROM insurance_claims c
            LEFT JOIN accident_reports r ON c.claim_id = r.claim_id
            ORDER BY c.claim_id
        """)).mappings().all()

        parties = conn.execute(text("SELECT * FROM involved_parties")).mappings().all()

    parties_by_claim = {}
    for p in parties:
        cid = p["claim_id"]
        if cid not in parties_by_claim:
            parties_by_claim[cid] = []
        parties_by_claim[cid].append(p)

    scored_claims = []
    for c in claims:
        cid = c["claim_id"]
        paid = float(c["paid_amount"])
        claimed = float(c["claimed_amount"])
        deductible = float(c["deductible_paid"])
        state_code = c["incident_state"]
        claim_type = c["claim_type"].lower()
        c_parties = parties_by_claim.get(cid, [])

        has_citations = bool(c["citations_issued"] and str(c["citations_issued"]).lower() not in ["none", "n/a", ""])
        has_police = bool(c["police_report_number"] and str(c["police_report_number"]) != "N/A")

        # Deterministic liability allocation based on incident physics and statutory citations
        if "single vehicle" in claim_type:
            adv_fault = 0.0
            ev_fac = 0.0
        elif "rear-end" in claim_type:
            adv_fault = 100.0 if has_citations else random.choice([85.0, 90.0, 95.0])
            ev_fac = 0.90 if has_citations else 0.75
        elif "t-bone" in claim_type or "intersection" in claim_type:
            adv_fault = random.choice([75.0, 80.0, 85.0, 90.0])
            ev_fac = 0.85 if has_citations else 0.70
        elif "yield" in claim_type:
            adv_fault = random.choice([70.0, 75.0, 80.0, 85.0])
            ev_fac = 0.80 if has_citations else 0.65
        elif "side-swipe" in claim_type:
            adv_fault = random.choice([55.0, 65.0, 75.0])
            ev_fac = 0.65
        elif "backing" in claim_type:
            adv_fault = random.choice([65.0, 75.0])
            ev_fac = 0.70
        elif "hit and run" in claim_type:
            adv_fault = 75.0 if has_police else 30.0
            ev_fac = 0.70 if has_police else 0.35
        else:
            adv_fault = random.choice([50.0, 60.0, 70.0])
            ev_fac = 0.60

        # Recovery probability correlated to liability % and evidence strength
        recovery_prob = round((adv_fault / 100.0) * ev_fac, 3) if adv_fault > 0 else 0.0

        # Projected recovery ~15-25% of paid exposure across the portfolio
        mult = (adv_fault / 100.0)
        net_rec = round(paid * mult * recovery_prob * 0.45, 2)
        gross_rec = round((paid + deductible) * mult * recovery_prob * 0.45, 2)
        ded_rec = round(deductible * mult * recovery_prob * 0.45, 2)

        # SOL date (2 years in TX/CA/FL, 3 years elsewhere)
        inc_date = datetime.strptime(c["incident_date"], "%Y-%m-%d")
        sol_years = 2 if state_code in ["TX", "CA", "FL"] else 3
        sol_date_obj = inc_date + timedelta(days=365 * sol_years)
        sol_date_str = sol_date_obj.strftime("%Y-%m-%d")
        days_to_sol = max(10, (sol_date_obj - datetime(2026, 1, 1)).days)
        sol_urgency = max(0.1, 1.0 - (days_to_sol / 1095.0))

        # Composite urgency score for priority ranking
        urgency_score = net_rec * (1.0 + mult + ev_fac + sol_urgency)

        scored_claims.append({
            "claim": c,
            "claim_id": cid,
            "paid": paid,
            "claimed": claimed,
            "deductible": deductible,
            "state_code": state_code,
            "claim_type_raw": c["claim_type"],
            "adv_fault": adv_fault,
            "ev_fac": ev_fac,
            "recovery_prob": recovery_prob,
            "gross_rec": gross_rec,
            "net_rec": net_rec,
            "ded_rec": ded_rec,
            "sol_date": sol_date_str,
            "days_to_sol": days_to_sol,
            "urgency_score": urgency_score,
            "has_citations": has_citations,
            "has_police": has_police
        })

    # Sort descending by composite urgency score
    scored_claims.sort(key=lambda x: x["urgency_score"], reverse=True)
    total_count = len(scored_claims) # 180

    # Strict priority tiers: ~15% High (27), ~35% Medium (63), ~50% Low (90)
    high_cutoff = 27 # Exactly 15.0%
    med_cutoff = 90  # Exactly 35.0% (27 + 63 = 90)

    # Reconciled workflow statuses:
    # 18 Closed Recovered (10% of ingested)
    # 27 Under Negotiation
    # 27 Demand Sent
    # 60 In Investigation
    # 48 Closed No Subro
    with engine.begin() as conn:
        for rank, item in enumerate(scored_claims):
            cid = item["claim_id"]

            if rank < high_cutoff:
                plvl = "High"
                pscr = round(0.85 + (high_cutoff - rank) * 0.005, 3)
            elif rank < med_cutoff:
                plvl = "Medium"
                pscr = round(0.60 + (med_cutoff - rank) * 0.003, 3)
            else:
                plvl = "Low"
                pscr = round(0.15 + (total_count - rank) * 0.004, 3)

            # Assign statuses ensuring exact funnel numbers
            if 5 <= rank < 23:
                # 18 settled/completed recovery cases
                subro_stat = "Closed Recovered"
            elif rank < 5 or (23 <= rank < 45):
                # 27 active negotiating cases
                subro_stat = "Under Negotiation"
            elif 45 <= rank < 72:
                # 27 demand sent cases
                subro_stat = "Demand Sent"
            elif 72 <= rank < 132:
                # 60 actively triaged/investigated cases
                subro_stat = "In Investigation"
            else:
                # 48 closed no subro / low liability cases
                subro_stat = "Closed No Subro"

            l_rat = (
                f"Assessed {item['adv_fault']:.1f}% adverse liability under {item['state_code']} comparative fault rules. "
                f"{'Official traffic citations confirm driver fault.' if item['has_citations'] else 'Physical impact points and party statements support liability.'}"
            )
            q_rat = (
                f"Projected net recovery of ${item['net_rec']:,.2f} after ${item['ded_rec']:,.2f} policyholder deductible allocation "
                f"(Make-Whole Doctrine) and estimated administrative fees."
            )

            aid = f"ASM-{cid}"
            conn.execute(text("""
                INSERT INTO recovery_assessments (
                    assessment_id, claim_id, priority_level, priority_score,
                    estimated_adverse_fault_pct, gross_recovery_estimate,
                    net_recovery_estimate, insured_deductible_recovery,
                    recovery_probability, statute_of_limitations_date,
                    liability_rationale, quantum_rationale, missing_evidence, status
                ) VALUES (
                    :aid, :cid, :plvl, :pscr, :afault, :gross, :net, :ded,
                    :prob, :sol, :lrat, :qrat, 'None', 'Assessed'
                )
                ON CONFLICT (assessment_id) DO UPDATE SET
                    priority_level = EXCLUDED.priority_level,
                    priority_score = EXCLUDED.priority_score,
                    estimated_adverse_fault_pct = EXCLUDED.estimated_adverse_fault_pct,
                    gross_recovery_estimate = EXCLUDED.gross_recovery_estimate,
                    net_recovery_estimate = EXCLUDED.net_recovery_estimate,
                    insured_deductible_recovery = EXCLUDED.insured_deductible_recovery,
                    recovery_probability = EXCLUDED.recovery_probability,
                    statute_of_limitations_date = EXCLUDED.statute_of_limitations_date,
                    liability_rationale = EXCLUDED.liability_rationale,
                    quantum_rationale = EXCLUDED.quantum_rationale,
                    status = 'Assessed'
            """), {
                "aid": aid,
                "cid": cid,
                "plvl": plvl,
                "pscr": pscr,
                "afault": item["adv_fault"],
                "gross": item["gross_rec"],
                "net": item["net_rec"],
                "ded": item["ded_rec"],
                "prob": item["recovery_prob"],
                "sol": item["sol_date"],
                "lrat": l_rat,
                "qrat": q_rat
            })

            conn.execute(text("""
                UPDATE insurance_claims
                SET subrogation_status = :sstat, updated_at = CURRENT_TIMESTAMP
                WHERE claim_id = :cid
            """), {"sstat": subro_stat, "cid": cid})

            # Upsert investigation report
            existing_rpt = conn.execute(
                text("SELECT report_id FROM investigation_reports WHERE claim_id = :cid"),
                {"cid": cid}
            ).fetchone()

            report_data = {
                "report_id": f"RPT-{cid}",
                "claim_id": cid,
                "priority_level": plvl,
                "adverse_fault_pct": item["adv_fault"],
                "net_recovery_estimate": item["net_rec"],
                "insured_deductible_recovery": item["ded_rec"],
                "statute_of_limitations_date": item["sol_date"],
                "recommendations": [
                    "Issue subrogation demand package to adverse carrier" if item["adv_fault"] >= 70 else "Review witness recorded statements",
                    "Obtain final repair certification and subrogation release"
                ]
            }

            if existing_rpt:
                conn.execute(text("""
                    UPDATE investigation_reports
                    SET executive_summary = :esum,
                        full_report_json = :rjson,
                        is_approved = :appr,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE claim_id = :cid
                """), {
                    "cid": cid,
                    "esum": f"Assessment for {cid} ({item['claim_type_raw']}) assigns {item['adv_fault']:.0f}% liability with ${item['net_rec']:,.2f} projected net recovery.",
                    "rjson": json.dumps(report_data),
                    "appr": plvl == "High"
                })
            else:
                conn.execute(text("""
                    INSERT INTO investigation_reports (
                        report_id, claim_id, report_number, executive_summary,
                        full_report_json, is_approved, created_at
                    ) VALUES (
                        :rid, :cid, :rnum, :esum, :rjson, :appr, CURRENT_TIMESTAMP
                    )
                """), {
                    "rid": f"RPT-{cid}",
                    "cid": cid,
                    "rnum": f"SR-RPT-{cid}",
                    "esum": f"Assessment for {cid} ({item['claim_type_raw']}) assigns {item['adv_fault']:.0f}% liability with ${item['net_rec']:,.2f} projected net recovery.",
                    "rjson": json.dumps(report_data),
                    "appr": plvl == "High"
                })

    print("Deterministic seeding completed successfully.")

if __name__ == "__main__":
    seed_all_assessments()
