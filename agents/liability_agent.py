"""
SubroRecover AI - Agent 3: Liability Assessment Agent
Evaluates comparative fault splits, negligence doctrines, and third-party responsibility indicators.
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

logger = logging.getLogger("subrorecover.agents.liability_agent")

# State negligence doctrines for US jurisdictions
NEGLIGENCE_DOCTRINES = {
    "TX": ("Modified Comparative Fault (51% Bar)", 0.51),
    "CA": ("Pure Comparative Fault", 1.00),
    "FL": ("Modified Comparative Fault (51% Bar)", 0.51),
    "IL": ("Modified Comparative Fault (51% Bar)", 0.51),
    "OH": ("Modified Comparative Fault (51% Bar)", 0.51),
    "GA": ("Modified Comparative Fault (50% Bar)", 0.50),
    "AZ": ("Pure Comparative Fault", 1.00)
}

class LiabilityAssessmentAgent:
    """Agent 3: Estimates adverse vs insured fault splits grounded in statutory negligence standards."""

    def __init__(self):
        self.name = "Liability Assessment Agent"

    def execute(self, state: SubroRecoverState) -> SubroRecoverState:
        start_time = time.time()
        logger.info(f"[{self.name}] Assessing liability for claim {state.claim_id}...")

        claim_type = state.claim_summary.get("claim_type", "Collision")
        state_code = state.claim_summary.get("incident_state", "TX")
        doctrine_name, bar_limit = NEGLIGENCE_DOCTRINES.get(state_code, ("Modified Comparative Fault (51% Bar)", 0.51))

        # Check evidence cues
        has_police = state.evidence_analysis.get("has_police_report", False)
        citations = state.evidence_citations
        parties = state.involved_parties or []

        # Find adverse driver party record
        adv_party = next((p for p in parties if "Adverse" in p.get("party_type", "")), None)

        # Baseline heuristic fault calculation
        if adv_party and float(adv_party.get("estimated_fault_percentage", 0)) > 0:
            raw_fault = float(adv_party.get("estimated_fault_percentage", 0.0))
        else:
            if "rear-end" in claim_type.lower():
                raw_fault = 100.0 if citations else 90.0
            elif "t-bone" in claim_type.lower() or "yield" in claim_type.lower():
                raw_fault = 95.0 if citations else 80.0
            elif "side-swipe" in claim_type.lower() or "lane" in claim_type.lower():
                raw_fault = 85.0 if citations else 70.0
            elif "single vehicle" in claim_type.lower():
                raw_fault = 0.0
            else:
                raw_fault = 50.0

        adverse_fault_pct = round(max(0.0, min(100.0, raw_fault)), 2)
        insured_fault_pct = round(100.0 - adverse_fault_pct, 2)
        is_subro_viable = (adverse_fault_pct >= (bar_limit * 100.0)) if bar_limit < 1.0 else (adverse_fault_pct > 0)

        # Build liability explanation
        rationale_lines = [
            f"Under {state_code} {doctrine_name}, recovery is permissible when adverse fault meets threshold.",
            f"Preliminary assessment attributes {adverse_fault_pct:.1f}% potential liability to adverse operator "
            f"and {insured_fault_pct:.1f}% to insured based on incident kinematics ({claim_type})."
        ]
        if citations:
            rationale_lines.append(f"Statutory citations ({'; '.join(citations)}) corroborate primary adverse causation.")
        if not has_police:
            rationale_lines.append("Note: Absence of certified police report necessitates witness verification before formal demand.")

        base_rationale = " ".join(rationale_lines)

        # Optional LLM refinement
        llm_prompt = f"""You are a Senior Insurance Subrogation Liability Attorney. Review this preliminary fault assessment:
Claim Type: {claim_type}
Jurisdiction: {state_code} ({doctrine_name})
Adverse Fault Estimate: {adverse_fault_pct}%
Citations: {citations}
Provide a 2-sentence objective liability determination noting this is an investigation finding, not final legal judgment."""

        llm_response = call_llm(llm_prompt, system_instruction="Provide legally grounded, objective subrogation liability analysis.")
        mode = "LIVE_LLM (Gemini)" if llm_response else "LOCAL_DETERMINISTIC_RULES"

        if llm_response:
            final_rationale = llm_response.strip()
        else:
            final_rationale = base_rationale

        liability_assessment = {
            "adverse_fault_pct": adverse_fault_pct,
            "insured_fault_pct": insured_fault_pct,
            "negligence_doctrine": doctrine_name,
            "jurisdiction_state": state_code,
            "is_third_party_liable": is_subro_viable,
            "liability_rationale": final_rationale,
            "statute_of_limitations_years": 2 if state_code in ["TX", "CA", "FL"] else 3,
            "mode": mode
        }

        # Update State
        state.liability_assessment = liability_assessment
        state.adverse_fault_pct = adverse_fault_pct
        state.insured_fault_pct = insured_fault_pct
        state.negligence_doctrine = doctrine_name
        state.liability_rationale = final_rationale
        state.is_third_party_liable = is_subro_viable

        duration_ms = int((time.time() - start_time) * 1000)
        state.agent_logs.append({
            "agent_name": self.name,
            "step": 3,
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "mode": mode,
            "summary": f"Assessed fault: Adverse={adverse_fault_pct}%, Insured={insured_fault_pct}%; Subro Viable={is_subro_viable}"
        })

        logger.info(f"[{self.name}] Completed in {duration_ms}ms (Mode: {mode})")
        return state
