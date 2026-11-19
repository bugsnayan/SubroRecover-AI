"""
SubroRecover AI - Claims REST API Endpoints
"""

import os
import sys
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from backend.schemas.claim import ClaimCreateRequest, ClaimResponse

logger = logging.getLogger("subrorecover.api.claims")
router = APIRouter(prefix="/claims", tags=["Claims"])

@router.get("", response_model=List[ClaimResponse])
def list_claims(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    subro_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Retrieves paginated list of insurance claims with optional filtering."""
    query = "SELECT * FROM insurance_claims WHERE 1=1"
    params = {"limit": limit, "offset": offset}

    if status:
        query += " AND claim_status = :status"
        params["status"] = status
    if subro_status:
        query += " AND subrogation_status = :subro_status"
        params["subro_status"] = subro_status
    if search:
        query += " AND (claim_id LIKE :search OR claim_number LIKE :search OR description LIKE :search)"
        params["search"] = f"%{search}%"

    query += " ORDER BY incident_date DESC LIMIT :limit OFFSET :offset"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()
        return [dict(r) for r in rows]

@router.get("/{claim_id}")
def get_claim_details(claim_id: str):
    """Retrieves comprehensive dossier for a single claim including policy, customer, and assessment."""
    with engine.connect() as conn:
        # Claim
        claim_row = conn.execute(text("SELECT * FROM insurance_claims WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        if not claim_row:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        claim_data = dict(claim_row)

        # Policy & Customer
        policy_row = conn.execute(text("SELECT * FROM insurance_policies WHERE policy_id = :pid"), {"pid": claim_data["policy_id"]}).mappings().first()
        cust_row = conn.execute(text("SELECT * FROM customers WHERE customer_id = :cid"), {"cid": claim_data["customer_id"]}).mappings().first()

        # Accident Report
        rep_row = conn.execute(text("SELECT * FROM accident_reports WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()

        # Parties
        party_rows = conn.execute(text("SELECT * FROM involved_parties WHERE claim_id = :cid"), {"cid": claim_id}).mappings().all()

        # Evidence Documents
        doc_rows = conn.execute(text("SELECT * FROM evidence_documents WHERE claim_id = :cid"), {"cid": claim_id}).mappings().all()

        # Assessment
        asm_row = conn.execute(text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()

        # Human Review Records
        rev_rows = conn.execute(text("SELECT * FROM human_review_records WHERE claim_id = :cid ORDER BY reviewed_at DESC"), {"cid": claim_id}).mappings().all()

        return {
            "claim": claim_data,
            "policy": dict(policy_row) if policy_row else None,
            "customer": dict(cust_row) if cust_row else None,
            "accident_report": dict(rep_row) if rep_row else None,
            "parties": [dict(p) for p in party_rows],
            "documents": [dict(d) for d in doc_rows],
            "assessment": dict(asm_row) if asm_row else None,
            "reviews": [dict(r) for r in rev_rows]
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
