"""
SubroRecover AI - Multi-Agent System & LangGraph Workflow Test Suite
"""

import os
import sys
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import SubroRecoverState
from agents.claim_agent import ClaimAnalysisAgent
from agents.evidence_agent import EvidenceAnalysisAgent
from agents.liability_agent import LiabilityAssessmentAgent
from agents.recovery_agent import RecoveryEstimationAgent
from agents.prioritization_agent import CasePrioritizationAgent
from agents.report_agent import InvestigationReportAgent
from agents.workflow import run_investigation_workflow

def test_individual_agents():
    # Construct test state
    state = SubroRecoverState(
        claim_id="CLM-UNIT-TEST",
        claim_data={
            "claim_id": "CLM-UNIT-TEST",
            "claim_number": "CN-TEST",
            "incident_date": "2025-10-01",
            "reported_date": "2025-10-02",
            "claim_type": "Rear-end Collision",
            "incident_location": "Main St & 5th Ave",
            "incident_state": "TX",
            "claimed_amount": 12500.0,
            "paid_amount": 10000.0,
            "deductible_paid": 500.0,
            "description": "Stopped at red light when struck from behind."
        },
        policy_data={"policy_number": "POL-TEST", "coverage_limit": 100000.0, "deductible_amount": 500.0},
        customer_data={"first_name": "John", "last_name": "Doe"},
        accident_report_data={
            "police_report_number": "PD-999",
            "officer_narrative": "Unit 2 failed to control speed and rear-ended Unit 1.",
            "citations_issued": "Sec 545.062 Following Too Closely"
        },
        involved_parties=[
            {"party_type": "Insured Driver", "full_name": "John Doe", "estimated_fault_percentage": 0.0},
            {"party_type": "Adverse Driver", "full_name": "Jane Smith", "estimated_fault_percentage": 100.0, "insurance_carrier": "State Farm"}
        ]
    )

    # 1. Claim Agent
    state = ClaimAnalysisAgent().execute(state)
    assert state.claim_validation_status == "VALID"
    assert state.claim_summary["paid_loss_amount"] == 10000.0

    # 2. Evidence Agent
    state = EvidenceAnalysisAgent().execute(state)
    assert len(state.verified_facts) >= 1

    # 3. Liability Agent
    state = LiabilityAssessmentAgent().execute(state)
    assert state.adverse_fault_pct >= 80.0
    assert state.is_third_party_liable is True

    # 4. Recovery Agent
    state = RecoveryEstimationAgent().execute(state)
    assert state.net_recovery_estimate > 0.0
    assert state.deductible_recovery_estimate > 0.0

    # 5. Prioritization Agent
    state = CasePrioritizationAgent().execute(state)
    assert state.priority_level in ["High", "Medium", "Low"]

    # 6. Report Agent
    state = InvestigationReportAgent().execute(state)
    assert state.workflow_status == "COMPLETED"
    assert len(state.recommended_actions) > 0

def test_full_workflow():
    try:
        final_state = run_investigation_workflow("CLM-0001")
        assert final_state.claim_id == "CLM-0001"
        assert final_state.workflow_status == "COMPLETED"
        assert len(final_state.agent_logs) == 6
        assert final_state.net_recovery_estimate > 0
    finally:
        from scripts.seed_assessments import seed_all_assessments
        seed_all_assessments()
