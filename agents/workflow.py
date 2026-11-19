"""
SubroRecover AI - Multi-Agent LangGraph Orchestration Workflow
Governs state transitions, routing, telemetry logging, and human-in-the-loop checkpoints.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy import text
from langgraph.graph import StateGraph, START, END

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import SubroRecoverState
from agents.claim_agent import ClaimAnalysisAgent
from agents.evidence_agent import EvidenceAnalysisAgent
from agents.liability_agent import LiabilityAssessmentAgent
from agents.recovery_agent import RecoveryEstimationAgent
from agents.prioritization_agent import CasePrioritizationAgent
from agents.report_agent import InvestigationReportAgent
from database.connection import engine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("subrorecover.agents.workflow")

# Instantiate specialized agent instances
claim_agent = ClaimAnalysisAgent()
evidence_agent = EvidenceAnalysisAgent()
liability_agent = LiabilityAssessmentAgent()
recovery_agent = RecoveryEstimationAgent()
prioritization_agent = CasePrioritizationAgent()
report_agent = InvestigationReportAgent()

# LangGraph Node Callables
def node_claim_analysis(state: SubroRecoverState) -> SubroRecoverState:
    return claim_agent.execute(state)

def node_evidence_analysis(state: SubroRecoverState) -> SubroRecoverState:
    return evidence_agent.execute(state)

def node_liability_assessment(state: SubroRecoverState) -> SubroRecoverState:
    return liability_agent.execute(state)

def node_recovery_estimation(state: SubroRecoverState) -> SubroRecoverState:
    return recovery_agent.execute(state)

def node_case_prioritization(state: SubroRecoverState) -> SubroRecoverState:
    return prioritization_agent.execute(state)

def node_investigation_report(state: SubroRecoverState) -> SubroRecoverState:
    return report_agent.execute(state)

# Conditional Routing
def route_after_liability(state: SubroRecoverState) -> str:
    """If adverse liability is zero, we can still proceed through recovery and report for documentation."""
    return "recovery_estimation"

def build_workflow() -> Any:
    """Builds and compiles the 6-agent LangGraph StateGraph."""
    graph = StateGraph(SubroRecoverState)

    # Add Nodes
    graph.add_node("claim_analysis", node_claim_analysis)
    graph.add_node("evidence_analysis", node_evidence_analysis)
    graph.add_node("liability_assessment", node_liability_assessment)
    graph.add_node("recovery_estimation", node_recovery_estimation)
    graph.add_node("case_prioritization", node_case_prioritization)
    graph.add_node("investigation_report", node_investigation_report)

    # Wire Edges
    graph.add_edge(START, "claim_analysis")
    graph.add_edge("claim_analysis", "evidence_analysis")
    graph.add_edge("evidence_analysis", "liability_assessment")
    graph.add_conditional_edges(
        "liability_assessment",
        route_after_liability,
        {"recovery_estimation": "recovery_estimation"}
    )
    graph.add_edge("recovery_estimation", "case_prioritization")
    graph.add_edge("case_prioritization", "investigation_report")
    graph.add_edge("investigation_report", END)

    compiled_app = graph.compile()
    logger.info("LangGraph Multi-Agent StateGraph compiled successfully.")
    return compiled_app

workflow_app = build_workflow()

def load_claim_state_from_db(claim_id: str) -> SubroRecoverState:
    """Fetches claim, policy, customer, report, and party data from DB to populate initial state."""
    with engine.connect() as conn:
        # 1. Claim
        res = conn.execute(text("SELECT * FROM insurance_claims WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        if not res:
            raise ValueError(f"Claim {claim_id} not found in database.")
        claim_data = dict(res)

        # 2. Policy
        pol_res = conn.execute(text("SELECT * FROM insurance_policies WHERE policy_id = :pid"), {"pid": claim_data["policy_id"]}).mappings().first()
        policy_data = dict(pol_res) if pol_res else {}

        # 3. Customer
        cust_res = conn.execute(text("SELECT * FROM customers WHERE customer_id = :cid"), {"cid": claim_data["customer_id"]}).mappings().first()
        customer_data = dict(cust_res) if cust_res else {}

        # 4. Accident Report
        rep_res = conn.execute(text("SELECT * FROM accident_reports WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        report_data = dict(rep_res) if rep_res else {}

        # 5. Parties
        party_rows = conn.execute(text("SELECT * FROM involved_parties WHERE claim_id = :cid"), {"cid": claim_id}).mappings().all()
        parties = [dict(r) for r in party_rows]

        # 6. Evidence Documents
        doc_rows = conn.execute(text("SELECT * FROM evidence_documents WHERE claim_id = :cid"), {"cid": claim_id}).mappings().all()
        docs = [dict(r) for r in doc_rows]

    state = SubroRecoverState(
        claim_id=claim_id,
        claim_data=claim_data,
        policy_data=policy_data,
        customer_data=customer_data,
        accident_report_data=report_data,
        involved_parties=parties,
        evidence_documents=docs,
        workflow_status="RUNNING"
    )
    return state

def log_agent_executions_to_db(state: SubroRecoverState):
    """Persists execution traces from each agent step to the agent_execution_logs table."""
    try:
        with engine.begin() as conn:
            for log in state.agent_logs:
                log_id = f"LOG-{state.claim_id}-S{log.get('step', 1)}-{int(time.time())}"
                conn.execute(text("""
                    INSERT INTO agent_execution_logs (
                        log_id, claim_id, agent_name, execution_step,
                        status, input_payload, output_payload,
                        execution_duration_ms, error_message
                    ) VALUES (
                        :lid, :cid, :aname, :step, :stat, :inp, :out, :dur, :err
                    )
                """), {
                    "lid": log_id,
                    "cid": state.claim_id,
                    "aname": log.get("agent_name", "Agent"),
                    "step": log.get("step", 1),
                    "stat": log.get("status", "Completed"),
                    "inp": f"Mode: {log.get('mode', 'N/A')}",
                    "out": log.get("summary", ""),
                    "dur": log.get("duration_ms", 0),
                    "err": None
                })
        logger.info(f"Persisted {len(state.agent_logs)} agent execution logs to DB.")
    except Exception as e:
        logger.debug(f"Notice writing agent execution logs: {e}")

def run_investigation_workflow(claim_id: str) -> SubroRecoverState:
    """
    Executes the complete 6-Agent LangGraph investigation pipeline for a given claim.
    """
    logger.info("====================================================================")
    logger.info(f"Triggering SubroRecover LangGraph Workflow for Claim: {claim_id}")
    logger.info("====================================================================")

    initial_state = load_claim_state_from_db(claim_id)
    start_time = time.time()

    # Execute LangGraph StateGraph
    final_state_dict = workflow_app.invoke(initial_state)

    # Cast back to SubroRecoverState if dict returned
    if isinstance(final_state_dict, dict):
        final_state = SubroRecoverState(**final_state_dict)
    else:
        final_state = final_state_dict

    # Persist audit traces
    log_agent_executions_to_db(final_state)

    total_duration = round(time.time() - start_time, 2)
    logger.info("====================================================================")
    logger.info(f"Workflow Complete for {claim_id} in {total_duration}s! Priority={final_state.priority_level} | Net=${final_state.net_recovery_estimate:,.2f}")
    logger.info("====================================================================")

    return final_state

if __name__ == "__main__":
    test_cid = "CLM-0001"
    res = run_investigation_workflow(test_cid)
    print("\nWorkflow Execution Output Summary:")
    print("Claim ID:            ", res.claim_id)
    print("Priority Level:      ", res.priority_level)
    print("Priority Score:      ", res.priority_score)
    print("Adverse Fault:       ", f"{res.adverse_fault_pct}%")
    print("Net Recovery:        ", f"${res.net_recovery_estimate:,.2f}")
    print("Deductible Refund:   ", f"${res.deductible_recovery_estimate:,.2f}")
    print("Executive Summary:   ", res.executive_summary)
    print("Recommended Actions: ", res.recommended_actions)
    print("Agent Logs Count:    ", len(res.agent_logs))
