"""
SubroRecover AI - Agent 5: Case Prioritization Agent
Integrates the trained Random Forest classifier to assign predictive priority tiers and explain triage urgency.
"""

import os
import sys
import time
import logging
from typing import Dict, Any

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import SubroRecoverState
from ml.predict import predict_case_priority
from agents.llm_client import call_llm

logger = logging.getLogger("subrorecover.agents.prioritization_agent")

class CasePrioritizationAgent:
    """Agent 5: Synthesizes Machine Learning predictions and triage heuristics into actionable priority scores."""

    def __init__(self):
        self.name = "Case Prioritization Agent"

    def execute(self, state: SubroRecoverState) -> SubroRecoverState:
        start_time = time.time()
        logger.info(f"[{self.name}] Running ML case prioritization for claim {state.claim_id}...")

        # Assemble inference features
        features = {
            "claim_amount": float(state.claim_summary.get("claimed_total", 0.0)),
            "paid_amount": float(state.claim_summary.get("paid_loss_amount", 0.0)),
            "deductible_amount": float(state.claim_summary.get("deductible_amount", 0.0)),
            "claim_type": state.claim_summary.get("claim_type", "Collision"),
            "incident_state": state.claim_summary.get("incident_state", "TX"),
            "num_parties": len(state.involved_parties) if state.involved_parties else 2,
            "has_police_report": 1 if state.evidence_analysis.get("has_police_report", False) else 0,
            "citations_issued": 1 if state.evidence_citations else 0,
            "adverse_fault_pct": float(state.adverse_fault_pct),
            "days_to_report": 1
        }

        # Run ML model inference
        ml_result = predict_case_priority(features)
        priority_level = ml_result.get("priority_level", "Medium")
        priority_score = float(ml_result.get("priority_score", 0.75))
        top_factors = ml_result.get("top_contributing_factors", ["adverse_fault_pct", "citations_issued"])

        # Determine urgency & human review recommendation
        if priority_level == "High":
            triage_action = "EXPEDITE_DEMAND: Subrogation opportunity is compelling with clear adverse liability."
            sla_days = 5
        elif priority_level == "Medium":
            triage_action = "INVESTIGATE_FURTHER: Request additional witness or adverse insurance statements."
            sla_days = 14
        else:
            triage_action = "LOW_PROBABILITY: Consider closing subrogation file unless new evidence emerges."
            sla_days = 30

        # LLM Triage Narrative
        llm_prompt = f"""You are a Claims Triage Director. Review this predictive prioritization:
Claim: {state.claim_id}
Priority Tier: {priority_level} (Score: {priority_score:.2f})
Contributing Factors: {top_factors}
Action: {triage_action}
Provide a 2-sentence guidance note for the claims adjuster."""

        llm_response = call_llm(llm_prompt, system_instruction="Provide concise insurance operational triage guidance.")
        mode = "LIVE_LLM (Gemini)" if llm_response else "LOCAL_DETERMINISTIC_RULES"

        if llm_response:
            guidance = llm_response.strip()
        else:
            guidance = (
                f"Machine learning model assigned '{priority_level}' priority ({priority_score*100:.1f}% confidence) "
                f"driven by {', '.join(top_factors[:2])}. Recommended SLA: {sla_days} days. {triage_action}"
            )

        prioritization = {
            "priority_level": priority_level,
            "priority_score": priority_score,
            "class_probabilities": ml_result.get("class_probabilities", {}),
            "top_contributing_factors": top_factors,
            "recommended_sla_days": sla_days,
            "triage_recommendation": triage_action,
            "adjuster_guidance": guidance,
            "mode": mode
        }

        # Update State
        state.prioritization = prioritization
        state.priority_level = priority_level
        state.priority_score = priority_score
        state.contributing_factors = top_factors

        duration_ms = int((time.time() - start_time) * 1000)
        state.agent_logs.append({
            "agent_name": self.name,
            "step": 5,
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "mode": mode,
            "summary": f"Ranked Case Priority={priority_level} (Score={priority_score:.4f}); SLA={sla_days}d"
        })

        logger.info(f"[{self.name}] Completed in {duration_ms}ms (Mode: {mode})")
        return state
