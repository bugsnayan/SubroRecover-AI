"""
SubroRecover AI - Agent 4: Recovery Estimation Agent
Calculates gross and net recovery exposure, honoring the Make-Whole Doctrine for insured deductibles.
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

logger = logging.getLogger("subrorecover.agents.recovery_agent")

class RecoveryEstimationAgent:
    """Agent 4: Models financial quantum, collection feasibility, and net recovery ranges."""

    def __init__(self):
        self.name = "Recovery Estimation Agent"

    def execute(self, state: SubroRecoverState) -> SubroRecoverState:
        start_time = time.time()
        logger.info(f"[{self.name}] Modeling financial quantum for claim {state.claim_id}...")

        paid_loss = float(state.claim_summary.get("paid_loss_amount", 0.0))
        deductible = float(state.claim_summary.get("deductible_amount", 0.0))
        adverse_fault = float(state.adverse_fault_pct) / 100.0
        is_liable = state.is_third_party_liable

        if not is_liable or adverse_fault <= 0 or paid_loss <= 0:
            gross_recovery = 0.0
            net_recovery = 0.0
            deductible_recovery = 0.0
            est_collection_cost = 0.0
            quantum_rationale = (
                "Subrogation recovery potential is $0.00 as third-party liability was not established "
                "or claim involves zero carrier disbursements."
            )
        else:
            total_claim_exposure = paid_loss + deductible
            gross_recovery = round(total_claim_exposure * adverse_fault, 2)
            
            # Make-Whole Doctrine: Insured deductible is reimbursed pro-rata with adverse fault
            deductible_recovery = round(deductible * adverse_fault, 2)
            
            # Carrier Gross = Paid Loss * adverse_fault
            carrier_gross = round(paid_loss * adverse_fault, 2)
            
            # Estimated administrative / arbitration collection overhead (5%)
            est_collection_cost = round(carrier_gross * 0.05, 2) if carrier_gross > 2000 else 0.0
            
            # Net carrier recovery
            net_recovery = round(max(0.0, carrier_gross - est_collection_cost), 2)
            
            recovery_yield_pct = round((net_recovery / paid_loss) * 100.0, 1) if paid_loss > 0 else 0.0

            quantum_rationale = (
                f"Based on assessed {adverse_fault*100:.1f}% adverse liability: Gross potential is ${gross_recovery:,.2f}. "
                f"Honoring the Make-Whole Doctrine, ${deductible_recovery:,.2f} is allocated to refund the policyholder deductible. "
                f"Net projected carrier recovery is ${net_recovery:,.2f} (a {recovery_yield_pct}% net yield on paid outlay) "
                f"after reserving ${est_collection_cost:,.2f} for standard recovery overhead."
            )

        # Optional LLM financial narrative
        llm_prompt = f"""You are a Subrogation Financial Quantum Auditor. Review these numbers:
Paid Outlay: ${paid_loss:,.2f}
Adverse Fault: {adverse_fault*100:.1f}%
Net Carrier Recovery Estimate: ${net_recovery:,.2f}
Insured Deductible Refund: ${deductible_recovery:,.2f}
Provide a 2-sentence financial explanation emphasizing that recovery depends on adverse carrier limits and solvency."""

        llm_response = call_llm(llm_prompt, system_instruction="Provide concise, accurate insurance subrogation financial reasoning.")
        mode = "LIVE_LLM (Gemini)" if llm_response else "LOCAL_DETERMINISTIC_RULES"

        if llm_response:
            final_rationale = llm_response.strip()
        else:
            final_rationale = quantum_rationale

        recovery_estimation = {
            "paid_loss_amount": paid_loss,
            "deductible_amount": deductible,
            "adverse_fault_multiplier": adverse_fault,
            "gross_recovery_estimate": gross_recovery,
            "insured_deductible_recovery": deductible_recovery,
            "net_carrier_recovery": net_recovery,
            "estimated_collection_cost": est_collection_cost,
            "quantum_rationale": final_rationale,
            "financial_disclaimer": "Estimates reflect theoretical comparative exposure and do not guarantee recovery from adverse carrier.",
            "mode": mode
        }

        # Update State
        state.recovery_estimation = recovery_estimation
        state.gross_recovery_estimate = gross_recovery
        state.net_recovery_estimate = net_recovery
        state.deductible_recovery_estimate = deductible_recovery
        state.estimated_collection_cost = est_collection_cost
        state.quantum_rationale = final_rationale

        duration_ms = int((time.time() - start_time) * 1000)
        state.agent_logs.append({
            "agent_name": self.name,
            "step": 4,
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "mode": mode,
            "summary": f"Calculated Net Recovery=${net_recovery:,.2f}; Deductible Refund=${deductible_recovery:,.2f}"
        })

        logger.info(f"[{self.name}] Completed in {duration_ms}ms (Mode: {mode})")
        return state
