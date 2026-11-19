"""
SubroRecover AI - Multi-Agent Investigation & HITL Governance API Endpoints
"""

import os
import sys
import uuid
import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from agents.workflow import run_investigation_workflow
from backend.schemas.claim import HumanReviewRequest, InvestigationTriggerResponse

logger = logging.getLogger("subrorecover.api.investigation")
router = APIRouter(prefix="/claims", tags=["Investigation & Governance"])

@router.post("/{claim_id}/investigate", response_model=InvestigationTriggerResponse)
def trigger_claim_investigation(claim_id: str):
    """
    Executes the 6-Agent LangGraph workflow on the specified claim.
    """
    try:
        final_state = run_investigation_workflow(claim_id)
        return {
            "status": "COMPLETED",
            "claim_id": claim_id,
            "priority_level": final_state.priority_level,
            "priority_score": final_state.priority_score,
            "adverse_fault_pct": final_state.adverse_fault_pct,
            "net_recovery_estimate": final_state.net_recovery_estimate,
            "insured_deductible_recovery": final_state.deductible_recovery_estimate,
            "executive_summary": final_state.executive_summary,
            "recommended_actions": final_state.recommended_actions,
            "agent_logs_count": len(final_state.agent_logs)
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during agent investigation for {claim_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent investigation failed: {str(e)}")

@router.get("/{claim_id}/assessment")
def get_claim_assessment(claim_id: str):
    """Retrieves the latest recovery assessment and agent execution traces."""
    with engine.connect() as conn:
        asm_row = conn.execute(text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        if not asm_row:
            raise HTTPException(status_code=404, detail=f"No assessment found for claim '{claim_id}'. Run /investigate first.")

        log_rows = conn.execute(text("SELECT * FROM agent_execution_logs WHERE claim_id = :cid ORDER BY execution_step ASC"), {"cid": claim_id}).mappings().all()

        return {
            "claim_id": claim_id,
            "assessment": dict(asm_row),
            "agent_logs": [dict(l) for l in log_rows]
        }

@router.post("/{claim_id}/review")
def submit_human_review(claim_id: str, payload: HumanReviewRequest):
    """
    Records human adjuster review decision (Approved, Modified, Rejected, Escalate).
    Fulfills mandatory Human-in-the-Loop decision governance.
    """
    review_id = f"REV-{uuid.uuid4().hex[:6].upper()}"
    with engine.begin() as conn:
        # Check claim exists
        claim_exists = conn.execute(text("SELECT 1 FROM insurance_claims WHERE claim_id = :cid"), {"cid": claim_id}).scalar()
        if not claim_exists:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")

        # Insert human review record
        conn.execute(text("""
            INSERT INTO human_review_records (
                review_id, claim_id, assessment_id, reviewer_name,
                reviewer_role, decision, adjusted_fault_pct,
                adjusted_net_recovery, review_notes
            ) VALUES (
                :rid, :cid, :aid, :rname, :rrole, :dec, :adj_flt, :adj_net, :notes
            )
        """), {
            "rid": review_id,
            "cid": claim_id,
            "aid": f"ASM-{claim_id}",
            "rname": payload.reviewer_name,
            "rrole": payload.reviewer_role,
            "dec": payload.decision,
            "adj_flt": payload.adjusted_fault_pct,
            "adj_net": payload.adjusted_net_recovery,
            "notes": payload.review_notes
        })

        # Update recovery_assessments status
        new_stat = f"Adjuster {payload.decision}"
        conn.execute(text("""
            UPDATE recovery_assessments
            SET status = :stat, updated_at = CURRENT_TIMESTAMP
            WHERE claim_id = :cid
        """), {"stat": new_stat, "cid": claim_id})

        # Update subrogation status on claim
        subro_status = "Demand Dispatched" if payload.decision == "Approved" else (
            "Closed No Subro" if payload.decision == "Rejected" else "Under HITL Review"
        )
        conn.execute(text("""
            UPDATE insurance_claims
            SET subrogation_status = :sstat, updated_at = CURRENT_TIMESTAMP
            WHERE claim_id = :cid
        """), {"sstat": subro_status, "cid": claim_id})

    logger.info(f"Recorded human review {review_id} for claim {claim_id}: {payload.decision}")
    return {
        "status": "SUCCESS",
        "review_id": review_id,
        "claim_id": claim_id,
        "decision": payload.decision,
        "reviewer": payload.reviewer_name,
        "updated_claim_status": subro_status
    }
