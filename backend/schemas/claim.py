"""
SubroRecover AI - Pydantic Request & Response Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ClaimCreateRequest(BaseModel):
    policy_id: str
    customer_id: str
    claim_number: str
    incident_date: str
    reported_date: str
    claim_type: str
    incident_location: str
    incident_state: str = "TX"
    claimed_amount: float
    paid_amount: float
    deductible_paid: float = 500.0
    description: Optional[str] = "Loss reported by insured."

class ClaimResponse(BaseModel):
    claim_id: str
    policy_id: str
    customer_id: str
    claim_number: str
    incident_date: str
    reported_date: str
    claim_type: str
    incident_location: Optional[str]
    incident_state: str
    claimed_amount: float
    paid_amount: float
    deductible_paid: float
    claim_status: str
    subrogation_status: str
    description: Optional[str]

class HumanReviewRequest(BaseModel):
    reviewer_name: str = "Senior Claims Adjuster"
    reviewer_role: str = "Subrogation Specialist"
    decision: str = Field(description="Approved, Modified, Rejected, Escalate to Legal")
    adjusted_fault_pct: Optional[float] = None
    adjusted_net_recovery: Optional[float] = None
    review_notes: Optional[str] = "Adjuster approved subrogation demand package."

class InvestigationTriggerResponse(BaseModel):
    status: str
    claim_id: str
    priority_level: str
    priority_score: float
    adverse_fault_pct: float
    net_recovery_estimate: float
    insured_deductible_recovery: float
    executive_summary: str
    recommended_actions: List[str]
    agent_logs_count: int

class AnalyticsOverviewResponse(BaseModel):
    total_claims_analyzed: int
    potential_recovery_opportunities: int
    total_paid_exposure: float
    projected_net_recovery: float
    priority_distribution: Dict[str, int]
    recovery_status_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
