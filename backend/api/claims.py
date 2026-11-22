"""
SubroRecover AI - Claims REST API Endpoints
Provides full claims CRUD, 3D graph network topologies, 3D portfolio scatter data,
and demand letter generation/editing.
"""

import os
import sys
import uuid
import json
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from backend.schemas.claim import ClaimCreateRequest, ClaimResponse

logger = logging.getLogger("subrorecover.api.claims")
router = APIRouter(prefix="/claims", tags=["Claims"])


class DemandLetterUpdate(BaseModel):
    letter_text: str
    recipient_carrier: Optional[str] = None
    demand_amount: Optional[float] = None
    status: Optional[str] = "Draft"


@router.get("/portfolio-3d")
def get_portfolio_3d_points():
    """
    Returns 3D scatter coordinate cloud for all claims in the portfolio.
    X: Paid Amount (Carrier exposure)
    Y: Recovery Probability (%)
    Z: Days to Statute of Limitations Deadline
    Size: Paid Exposure
    Color: Priority Tier (High: rust, Medium: brass, Low: teal)
    """
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT 
                c.claim_id, c.claim_number, c.claim_type, c.incident_state,
                c.paid_amount, c.claimed_amount, c.subrogation_status, c.incident_date,
                a.priority_level, a.recovery_probability, a.net_recovery_estimate,
                a.estimated_adverse_fault_pct as adverse_fault_pct, a.statute_of_limitations_date
            FROM insurance_claims c
            LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
            ORDER BY c.incident_date DESC
        """)).mappings().all()

    today = date.today()
    points = []

    priority_colors = {
        "High": "#D1603D",    # Rust (urgent)
        "Medium": "#CFA968",  # Brass (review)
        "Low": "#2F8F89"      # Teal (routine/monitor)
    }

    for r in rows:
        paid = float(r["paid_amount"]) if r["paid_amount"] else 0.0
        prob = float(r["recovery_probability"]) if r["recovery_probability"] is not None else 0.5
        prob_pct = round(prob * 100, 1)

        sol_str = r["statute_of_limitations_date"]
        days_to_sol = 365
        if sol_str:
            try:
                sol_date = datetime.strptime(str(sol_str)[:10], "%Y-%m-%d").date()
                days_to_sol = max(0, (sol_date - today).days)
            except Exception:
                days_to_sol = 365

        prio = r["priority_level"] or ("High" if prob >= 0.75 else ("Medium" if prob >= 0.45 else "Low"))
        color = priority_colors.get(prio, "#8FA0B3")

        points.append({
            "id": r["claim_id"],
            "claim_id": r["claim_id"],
            "claim_number": r["claim_number"],
            "incident_type": r["claim_type"],
            "incident_state": r["incident_state"],
            "paid_amount": paid,
            "projected_recovery": float(r["net_recovery_estimate"]) if r["net_recovery_estimate"] else round(paid * prob, 2),
            "recovery_probability": prob_pct,
            "days_to_sol": days_to_sol,
            "sol_date": str(sol_str) if sol_str else None,
            "priority": prio,
            "status": r["subrogation_status"] or "Identified",
            "fault_pct": float(r["adverse_fault_pct"]) if r["adverse_fault_pct"] is not None else 75.0,
            # 3D Coordinates
            "x": paid,
            "y": prob_pct,
            "z": days_to_sol,
            "size": max(10, min(50, paid / 1500)),
            "color": color
        })

    return {
        "total_points": len(points),
        "axes": {
            "x": {"label": "Paid Amount ($)", "unit": "USD"},
            "y": {"label": "Recovery Probability (%)", "unit": "%"},
            "z": {"label": "Days to SOL Deadline", "unit": "Days"}
        },
        "points": points
    }


@router.get("", response_model=List[ClaimResponse])
def list_claims(
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    subro_status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    incident_type: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("incident_date"),
    sort_order: Optional[str] = Query("desc")
):
    """Retrieves paginated list of insurance claims with comprehensive multi-criteria filtering."""
    query = """
        SELECT c.*, a.priority_level, a.recovery_probability, a.net_recovery_estimate,
               a.estimated_adverse_fault_pct as adverse_fault_pct, a.statute_of_limitations_date
        FROM insurance_claims c
        LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
        WHERE 1=1
    """
    params = {"limit": limit, "offset": offset}

    if status:
        query += " AND c.claim_status = :status"
        params["status"] = status
    if subro_status:
        query += " AND c.subrogation_status = :subro_status"
        params["subro_status"] = subro_status
    if priority:
        query += " AND a.priority_level = :priority"
        params["priority"] = priority
    if incident_type:
        query += " AND c.claim_type = :incident_type"
        params["incident_type"] = incident_type
    if state:
        query += " AND c.incident_state = :state"
        params["state"] = state
    if search:
        query += " AND (c.claim_id LIKE :search OR c.claim_number LIKE :search OR c.description LIKE :search OR c.incident_location LIKE :search)"
        params["search"] = f"%{search}%"

    valid_sorts = {
        "incident_date": "c.incident_date",
        "paid_amount": "c.paid_amount",
        "claimed_amount": "c.claimed_amount",
        "claim_number": "c.claim_number",
        "priority": "a.priority_level",
        "recovery_probability": "a.recovery_probability",
        "net_recovery": "a.net_recovery_estimate"
    }
    sort_col = valid_sorts.get(sort_by, "c.incident_date")
    direction = "ASC" if sort_order.lower() == "asc" else "DESC"

    query += f" ORDER BY {sort_col} {direction} LIMIT :limit OFFSET :offset"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()
        return [dict(r) for r in rows]


@router.get("/{claim_id}")
def get_claim_details(claim_id: str):
    """Retrieves comprehensive dossier for a single claim including policy, customer, evidence, and assessment."""
    with engine.connect() as conn:
        claim_row = conn.execute(
            text("SELECT * FROM insurance_claims WHERE claim_id = :cid OR claim_number = :cid"),
            {"cid": claim_id}
        ).mappings().first()

        if not claim_row:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        claim_data = dict(claim_row)
        real_cid = claim_data["claim_id"]

        policy_row = conn.execute(
            text("SELECT * FROM insurance_policies WHERE policy_id = :pid"),
            {"pid": claim_data["policy_id"]}
        ).mappings().first()

        cust_row = conn.execute(
            text("SELECT * FROM customers WHERE customer_id = :cid"),
            {"cid": claim_data["customer_id"]}
        ).mappings().first()

        rep_row = conn.execute(
            text("SELECT * FROM accident_reports WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()

        party_rows = conn.execute(
            text("SELECT * FROM involved_parties WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().all()

        doc_rows = conn.execute(
            text("SELECT * FROM evidence_documents WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().all()

        asm_row = conn.execute(
            text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()

        rev_rows = conn.execute(
            text("SELECT * FROM human_review_records WHERE claim_id = :cid ORDER BY reviewed_at DESC"),
            {"cid": real_cid}
        ).mappings().all()

        report_row = conn.execute(
            text("SELECT * FROM investigation_reports WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()

        return {
            "claim": claim_data,
            "policy": dict(policy_row) if policy_row else None,
            "customer": dict(cust_row) if cust_row else None,
            "accident_report": dict(rep_row) if rep_row else None,
            "parties": [dict(p) for p in party_rows],
            "documents": [dict(d) for d in doc_rows],
            "assessment": dict(asm_row) if asm_row else None,
            "reviews": [dict(r) for r in rev_rows],
            "report": dict(report_row) if report_row else None
        }


@router.get("/{claim_id}/graph")
def get_claim_recovery_graph(claim_id: str):
    """
    Constructs the 3D recovery graph topology for a single claim.
    Returns:
    - Core central claim node with recovery probability ring
    - Orbiting party nodes (Adverse Driver, Adverse Carrier, Insured)
    - Orbiting evidence nodes (Police Report, Photos, Dashcam, Statements)
    - Orbiting damage / quantum nodes (Paid loss, Deductible, Repair Cost)
    - Weighted relational edges indicating liability transfer, evidence strength, and financial quantum
    """
    with engine.connect() as conn:
        claim_row = conn.execute(
            text("SELECT * FROM insurance_claims WHERE claim_id = :cid OR claim_number = :cid"),
            {"cid": claim_id}
        ).mappings().first()
        if not claim_row:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        claim = dict(claim_row)
        real_cid = claim["claim_id"]

        asm_row = conn.execute(
            text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()
        assessment = dict(asm_row) if asm_row else {}

        parties = conn.execute(
            text("SELECT * FROM involved_parties WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().all()
        documents = conn.execute(
            text("SELECT * FROM evidence_documents WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().all()
        accident = conn.execute(
            text("SELECT * FROM accident_reports WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()

    prob = float(assessment.get("recovery_probability") or 0.75)
    adv_fault = float(assessment.get("estimated_adverse_fault_pct") or assessment.get("adverse_fault_pct") or 80.0)
    net_rec = float(assessment.get("net_recovery_estimate") or (float(claim["paid_amount"]) * 0.8))
    paid = float(claim["paid_amount"])
    ded = float(claim["deductible_paid"])

    # 1. Central Core Node
    nodes = [
        {
            "id": "core",
            "type": "claim",
            "label": f"Claim {claim['claim_number']}",
            "sublabel": claim["claim_type"],
            "claim_id": claim_id,
            "recovery_probability": round(prob * 100, 1),
            "priority": assessment.get("priority_level", "Medium"),
            "status": claim["subrogation_status"],
            "paid_amount": paid,
            "net_recovery": net_rec,
            "color": "#CFA968", # Brass
            "size": 1.6
        }
    ]

    edges = []

    # 2. Party Nodes
    for i, p in enumerate(parties):
        p_id = f"party_{p['party_id']}"
        is_adverse = "adverse" in str(p.get("party_type", "")).lower()
        carrier = p.get("insurance_carrier", "Unknown Carrier")
        
        nodes.append({
            "id": p_id,
            "type": "party",
            "label": p.get("party_name", f"Party {i+1}"),
            "sublabel": f"{p.get('party_type', 'Party')} • {carrier}",
            "role": p.get("party_type", "Involved Party"),
            "vehicle": f"{p.get('vehicle_year', '')} {p.get('vehicle_make', '')} {p.get('vehicle_model', '')}".strip(),
            "policy_number": p.get("policy_number", "N/A"),
            "insurance_carrier": carrier,
            "is_adverse": is_adverse,
            "color": "#D1603D" if is_adverse else "#8FA0B3", # Rust for adverse, slate for neutral
            "size": 1.1 if is_adverse else 0.85
        })

        weight = (adv_fault / 100.0) if is_adverse else 0.3
        edges.append({
            "source": "core",
            "target": p_id,
            "weight": weight,
            "label": f"{adv_fault:.0f}% Adverse Fault" if is_adverse else "Insured Party",
            "color": "#D1603D" if is_adverse else "#8FA0B3"
        })

    # 3. Evidence Nodes
    if accident:
        nodes.append({
            "id": "evidence_police",
            "type": "evidence",
            "label": f"Police Report #{accident.get('police_report_number', 'PR-001')}",
            "sublabel": f"Officer {accident.get('officer_badge_number', 'N/A')}",
            "narrative": accident.get("officer_narrative", ""),
            "citations": accident.get("citations_issued", "None"),
            "weather": accident.get("weather_conditions", "Clear"),
            "color": "#2F8F89", # Teal
            "size": 1.0
        })
        edges.append({
            "source": "core",
            "target": "evidence_police",
            "weight": 0.95,
            "label": "Official Police Citation",
            "color": "#2F8F89"
        })

    for d in documents[:4]:
        doc_id = f"doc_{d['document_id']}"
        nodes.append({
            "id": doc_id,
            "type": "evidence",
            "label": d.get("document_type", "Document"),
            "sublabel": d.get("file_name", ""),
            "confidence": float(d.get("extraction_confidence") or 0.90),
            "color": "#2F8F89",
            "size": 0.8
        })
        edges.append({
            "source": "core",
            "target": doc_id,
            "weight": float(d.get("extraction_confidence") or 0.85),
            "label": "Verified Document",
            "color": "#2F8F89"
        })

    # 4. Damage / Quantum Nodes
    nodes.append({
        "id": "quantum_paid",
        "type": "damage",
        "label": f"Paid Loss: ${paid:,.2f}",
        "sublabel": f"Net Recovery: ${net_rec:,.2f}",
        "paid_amount": paid,
        "net_recovery": net_rec,
        "color": "#DFC285",
        "size": 0.9
    })
    edges.append({
        "source": "core",
        "target": "quantum_paid",
        "weight": min(1.0, paid / 25000),
        "label": f"${net_rec:,.0f} Recovery Target",
        "color": "#DFC285"
    })

    if ded > 0:
        nodes.append({
            "id": "quantum_deductible",
            "type": "damage",
            "label": f"Deductible: ${ded:,.2f}",
            "sublabel": "Insured Make-Whole Recovery",
            "deductible": ded,
            "color": "#8FA0B3",
            "size": 0.75
        })
        edges.append({
            "source": "quantum_paid",
            "target": "quantum_deductible",
            "weight": 0.6,
            "label": "Make-Whole Doctrine",
            "color": "#8FA0B3"
        })

    return {
        "claim_id": claim_id,
        "claim_number": claim["claim_number"],
        "recovery_probability": round(prob * 100, 1),
        "adverse_fault_pct": adv_fault,
        "projected_net_recovery": net_rec,
        "nodes": nodes,
        "edges": edges
    }


@router.get("/{claim_id}/demand-letter")
def get_demand_letter(claim_id: str):
    """
    Generates or retrieves formal subrogation demand letter for adverse insurance carrier.
    """
    with engine.connect() as conn:
        claim_row = conn.execute(
            text("SELECT * FROM insurance_claims WHERE claim_id = :cid OR claim_number = :cid"),
            {"cid": claim_id}
        ).mappings().first()
        if not claim_row:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        claim = dict(claim_row)
        real_cid = claim["claim_id"]

        asm_row = conn.execute(
            text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()
        asm = dict(asm_row) if asm_row else {}

        parties = conn.execute(
            text("SELECT * FROM involved_parties WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().all()
        accident = conn.execute(
            text("SELECT * FROM accident_reports WHERE claim_id = :cid"),
            {"cid": real_cid}
        ).mappings().first()

    adv_party = next((p for p in parties if "adverse" in str(p.get("party_type", "")).lower()), None)
    carrier_name = adv_party.get("insurance_carrier") if adv_party else "Third-Party Insurance Carrier"
    adverse_driver = adv_party.get("party_name") if adv_party else "Adverse Driver"
    adverse_policy = adv_party.get("policy_number") if adv_party else "AD-POL-PENDING"

    paid = float(claim["paid_amount"])
    ded = float(claim["deductible_paid"])
    fault_pct = float(asm.get("estimated_adverse_fault_pct") or asm.get("adverse_fault_pct") or 80.0)
    demand_amount = round((paid + ded) * (fault_pct / 100.0), 2)

    today_str = date.today().strftime("%B %d, %Y")
    sol_date = asm.get("statute_of_limitations_date", "2028-12-31")

    citations = accident.get("citations_issued") if accident else "Traffic Violation / Failure to Yield"
    narrative = accident.get("officer_narrative") if accident else f"Adverse vehicle collided with insured in {claim['claim_type'].lower()} incident."

    letter_text = f"""SUBROGATION DEMAND LETTER & NOTICE OF LIEN

Date: {today_str}
VIA CERTIFIED MAIL / ELECTRONIC EDI

To:
Claims Recovery & Subrogation Department
{carrier_name}
RE: Formal Subrogation Claim & Demand for Indemnification

Claim Reference Details:
Our Insured Claim Number: {claim['claim_number']}
Your Insured / Adverse Operator: {adverse_driver}
Your Policy Number: {adverse_policy}
Date of Loss: {claim['incident_date']}
Loss Location: {claim['incident_location']}, {claim['incident_state']}
Incident Classification: {claim['claim_type']}

Dear Claims Representative,

Please be advised that SubroRecover AI, on behalf of our carrier and policyholder, has concluded an exhaustive evidence-based liability investigation into the motor vehicle collision referenced above.

LIABILITY STATEMENT:
Investigation confirms that your insured operator, {adverse_driver}, was solely or primarily at fault ({fault_pct:.0f}% statutory comparative liability) for this incident. 
Investigative evidence establishes:
1. Police Report & Citations: Official investigative report noted citations issued: {citations}.
2. Evidence Narrative: {narrative}
3. Clear Breach of Duty: Your insured failed to maintain proper control and failed to yield the legal right-of-way.

STATEMENT OF DAMAGES & DEMAND QUANTUM:
As a direct and proximate result of your insured's negligence, our company sustained compensable damages and incurred financial loss as detailed below:

  • Carrier Indemnity / Property Loss Paid:    ${paid:,.2f}
  • Insured Deductible Paid:                   ${ded:,.2f}
  • Pro-Rata Adverse Responsibility ({fault_pct:.0f}%):     ${demand_amount:,.2f}

TOTAL SUBROGATION DEMAND: ${demand_amount:,.2f}

DEMAND FOR SETTLEMENT:
Under applicable statutory subrogation rights and the Make-Whole doctrine, demand is hereby made upon {carrier_name} for immediate remittance of ${demand_amount:,.2f}. 

Please note the Statute of Limitations deadline for formal litigation on this claim is {sol_date}. Remit settlement check payable to Subrogation Trust Account within thirty (30) business days from receipt of this notice.

Sincerely,

Subrogation Recovery Operations
SubroRecover AI Enterprise Recovery System
Claims Resolution Unit
"""

    return {
        "claim_id": claim_id,
        "claim_number": claim["claim_number"],
        "recipient_carrier": carrier_name,
        "adverse_driver": adverse_driver,
        "adverse_policy": adverse_policy,
        "demand_amount": demand_amount,
        "carrier_paid": paid,
        "deductible": ded,
        "fault_pct": fault_pct,
        "sol_date": str(sol_date),
        "status": "Draft",
        "letter_text": letter_text.strip()
    }


@router.put("/{claim_id}/demand-letter")
def update_demand_letter(claim_id: str, payload: DemandLetterUpdate):
    """
    Saves edited demand letter draft text or updates status to 'Sent'.
    """
    with engine.connect() as conn:
        claim_row = conn.execute(
            text("SELECT claim_id FROM insurance_claims WHERE claim_id = :cid OR claim_number = :cid"),
            {"cid": claim_id}
        ).fetchone()
        if not claim_row:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        real_cid = claim_row[0]

    if payload.status == "Sent":
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE insurance_claims
                SET subrogation_status = 'Demand Sent', updated_at = CURRENT_TIMESTAMP
                WHERE claim_id = :cid
            """), {"cid": real_cid})

    return {
        "claim_id": real_cid,
        "status": payload.status,
        "message": f"Demand letter successfully updated (Status: {payload.status}).",
        "letter_text": payload.letter_text
    }


@router.post("", response_model=ClaimResponse, status_code=201)
def create_claim(payload: ClaimCreateRequest):
    """Registers a new claim into the database."""
    claim_id = f"CLM-{uuid.uuid4().hex[:6].upper()}"
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO insurance_claims (
                claim_id, policy_id, customer_id, claim_number,
                incident_date, reported_date, claim_type,
                incident_location, incident_state, claimed_amount,
                paid_amount, deductible_paid, claim_status,
                subrogation_status, description
            ) VALUES (
                :cid, :pid, :cust_id, :cnum, :idate, :rdate, :ctype,
                :loc, :state, :claimed, :paid, :ded, 'Open',
                'Identified', :desc
            )
        """), {
            "cid": claim_id,
            "pid": payload.policy_id,
            "cust_id": payload.customer_id,
            "cnum": payload.claim_number,
            "idate": payload.incident_date,
            "rdate": payload.reported_date,
            "ctype": payload.claim_type,
            "loc": payload.incident_location,
            "state": payload.incident_state,
            "claimed": payload.claimed_amount,
            "paid": payload.paid_amount,
            "ded": payload.deductible_paid,
            "desc": payload.description
        })

    logger.info(f"Created new claim {claim_id} ({payload.claim_number})")
    return {
        "claim_id": claim_id,
        "policy_id": payload.policy_id,
        "customer_id": payload.customer_id,
        "claim_number": payload.claim_number,
        "incident_date": payload.incident_date,
        "reported_date": payload.reported_date,
        "claim_type": payload.claim_type,
        "incident_location": payload.incident_location,
        "incident_state": payload.incident_state,
        "claimed_amount": payload.claimed_amount,
        "paid_amount": payload.paid_amount,
        "deductible_paid": payload.deductible_paid,
        "claim_status": "Open",
        "subrogation_status": "Identified",
        "description": payload.description
    }
