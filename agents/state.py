"""
SubroRecover AI - Multi-Agent State Definition
Defines the shared state schema passed across all 6 specialized agents in LangGraph.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SubroRecoverState(BaseModel):
    """Shared state object for the multi-agent investigation workflow."""

    # Input Data
    claim_id: str
    claim_data: Dict[str, Any] = Field(default_factory=dict)
    policy_data: Dict[str, Any] = Field(default_factory=dict)
    customer_data: Dict[str, Any] = Field(default_factory=dict)
    accident_report_data: Dict[str, Any] = Field(default_factory=dict)
    involved_parties: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_documents: List[Dict[str, Any]] = Field(default_factory=list)

    # Agent 1 Output: Claim Analysis
    claim_summary: Dict[str, Any] = Field(default_factory=dict)
    claim_validation_status: str = "PENDING"
    missing_claim_fields: List[str] = Field(default_factory=list)

    # Agent 2 Output: Evidence Analysis
    evidence_analysis: Dict[str, Any] = Field(default_factory=dict)
    verified_facts: List[str] = Field(default_factory=list)
    unverified_facts: List[str] = Field(default_factory=list)
    evidence_citations: List[str] = Field(default_factory=list)
    evidence_sources: List[Dict[str, Any]] = Field(default_factory=list)

    # Agent 3 Output: Liability Assessment
    liability_assessment: Dict[str, Any] = Field(default_factory=dict)
    adverse_fault_pct: float = 0.0
    insured_fault_pct: float = 0.0
    negligence_doctrine: str = "Modified Comparative (51% Bar)"
    liability_rationale: str = ""
    is_third_party_liable: bool = False

    # Agent 4 Output: Recovery Estimation
    recovery_estimation: Dict[str, Any] = Field(default_factory=dict)
    gross_recovery_estimate: float = 0.0
    net_recovery_estimate: float = 0.0
    deductible_recovery_estimate: float = 0.0
    estimated_collection_cost: float = 0.0
    quantum_rationale: str = ""

    # Agent 5 Output: Case Prioritization (ML Model + Heuristics)
    prioritization: Dict[str, Any] = Field(default_factory=dict)
    priority_level: str = "Low"  # High, Medium, Low
    priority_score: float = 0.0
    contributing_factors: List[str] = Field(default_factory=list)

    # Agent 6 Output: Investigation Report
    investigation_report: Dict[str, Any] = Field(default_factory=dict)
    executive_summary: str = ""
    recommended_actions: List[str] = Field(default_factory=list)
    missing_documentation_checklist: List[str] = Field(default_factory=list)
    report_id: Optional[str] = None
    pdf_report_path: Optional[str] = None

    # HITL Review Checkpoint
    human_review_status: str = "Pending Review"  # Pending Review, Approved, Modified, Rejected
    human_reviewer_notes: Optional[str] = None

    # Telemetry and Execution Logs
    agent_logs: List[Dict[str, Any]] = Field(default_factory=list)
    workflow_status: str = "INITIALIZED"  # INITIALIZED, RUNNING, COMPLETED, FAILED
    error_message: Optional[str] = None
