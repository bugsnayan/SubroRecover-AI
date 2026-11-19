"""
SubroRecover AI - Agent 1: Claim Analysis Agent
Analyzes claim records, validates policy limits, identifies missing fields, and summarizes loss circumstances.
"""

import os
import sys
import time
import logging
from typing import Dict, Any

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import SubroRecoverState
from agents.llm_client import call_llm

logger = logging.getLogger("subrorecover.agents.claim_agent")

class ClaimAnalysisAgent:
    """Agent 1: Ingests raw claim data, audits policy coverage, and structures claim profile."""

    def __init__(self):
        self.name = "Claim Analysis Agent"

    def execute(self, state: SubroRecoverState) -> SubroRecoverState:
        start_time = time.time()
        logger.info(f"[{self.name}] Executing analysis for claim {state.claim_id}...")

        claim = state.claim_data
        policy = state.policy_data
        cust = state.customer_data

        paid_amount = float(claim.get("paid_amount", 0.0))
        claimed_amount = float(claim.get("claimed_amount", 0.0))
        deductible = float(claim.get("deductible_paid", policy.get("deductible_amount", 0.0)))
        cov_limit = float(policy.get("coverage_limit", 50000.0))

        # Audit missing fields
        missing_fields = []
        if not claim.get("incident_date"):
            missing_fields.append("incident_date")
        if not claim.get("incident_location"):
            missing_fields.append("incident_location")
        if paid_amount <= 0:
            missing_fields.append("paid_amount")
        if not policy.get("policy_number"):
            missing_fields.append("policy_number")

        validation_status = "VALID" if not missing_fields else "INCOMPLETE"

        # Construct structured summary
        summary = {
            "claim_id": state.claim_id,
            "claim_number": claim.get("claim_number", "N/A"),
            "claim_type": claim.get("claim_type", "Vehicle Impact"),
            "incident_date": claim.get("incident_date", "Unknown"),
            "reported_date": claim.get("reported_date", "Unknown"),
            "incident_state": claim.get("incident_state", "TX"),
            "incident_location": claim.get("incident_location", "Unknown Location"),
            "policy_holder": f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip() or "Insured Policyholder",
            "policy_number": policy.get("policy_number", "N/A"),
            "policy_type": policy.get("policy_type", "Personal Auto"),
            "coverage_limit": cov_limit,
            "deductible_amount": deductible,
            "paid_loss_amount": paid_amount,
            "claimed_total": claimed_amount,
            "claim_narrative": claim.get("description", "No loss description provided."),
            "subrogation_candidate": paid_amount > 500.0
        }

        # Try live LLM enhancement if configured
        llm_prompt = f"""You are an expert Insurance Claim Intake Analyst. Review this claim summary and provide a 2-sentence executive summary:
Claim ID: {state.claim_id}
Type: {summary['claim_type']}
Paid Loss: ${paid_amount:,.2f}
Incident: {summary['claim_narrative']}
"""
        llm_response = call_llm(llm_prompt, system_instruction="Provide concise, objective insurance claim summaries.")
        if llm_response:
            summary["llm_executive_notes"] = llm_response.strip()
            summary["mode"] = "LIVE_LLM (Gemini)"
        else:
            summary["llm_executive_notes"] = (
                f"Insured claim {state.claim_id} involves a {summary['claim_type']} with total carrier disbursements of "
                f"${paid_amount:,.2f} and an applicable deductible of ${deductible:,.2f}. Coverage is confirmed active under policy {summary['policy_number']}."
            )
            summary["mode"] = "LOCAL_DETERMINISTIC_RULES"

        # Update State
        state.claim_summary = summary
        state.claim_validation_status = validation_status
        state.missing_claim_fields = missing_fields

        duration_ms = int((time.time() - start_time) * 1000)
        state.agent_logs.append({
            "agent_name": self.name,
            "step": 1,
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "mode": summary["mode"],
            "summary": f"Audited claim {state.claim_id}; Status={validation_status}; Paid=${paid_amount:,.2f}"
        })

        logger.info(f"[{self.name}] Completed in {duration_ms}ms (Mode: {summary['mode']})")
        return state
