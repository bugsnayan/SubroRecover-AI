"""
SubroRecover AI - Executive Analytics & Recovery Intelligence API Endpoints
"""

import os
import sys
import logging
from fastapi import APIRouter
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from backend.schemas.claim import AnalyticsOverviewResponse

logger = logging.getLogger("subrorecover.api.analytics")
router = APIRouter(prefix="/analytics", tags=["Executive Analytics"])

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview():
    """
    Computes high-level recovery metrics, financial exposures, and priority distributions.
    """
    with engine.connect() as conn:
        # Total claims and total paid exposure
        claim_stats = conn.execute(text("""
            SELECT
                COUNT(*) as total_claims,
                COALESCE(SUM(paid_amount), 0.0) as total_paid
            FROM insurance_claims
        """)).mappings().first()

        total_claims = int(claim_stats["total_claims"])
        total_paid = float(claim_stats["total_paid"])

        # Recovery assessments metrics
        asm_stats = conn.execute(text("""
            SELECT
                COUNT(*) as total_assessed,
                COALESCE(SUM(net_recovery_estimate), 0.0) as projected_net,
                COALESCE(SUM(gross_recovery_estimate), 0.0) as projected_gross
            FROM recovery_assessments
        """)).mappings().first()

        projected_net = float(asm_stats["projected_net"])

        # Potential opportunities (where net recovery > 0 or priority in ('High', 'Medium'))
        opp_count = conn.execute(text("""
            SELECT COUNT(*) FROM recovery_assessments
            WHERE priority_level IN ('High', 'Medium') AND net_recovery_estimate > 0
        """)).scalar() or 0

        # Priority distribution
        prio_rows = conn.execute(text("""
            SELECT priority_level, COUNT(*) as cnt
            FROM recovery_assessments
            GROUP BY priority_level
        """)).mappings().all()
        prio_dist = {r["priority_level"]: int(r["cnt"]) for r in prio_rows}
        for k in ["High", "Medium", "Low"]:
            prio_dist.setdefault(k, 0)

        # Subrogation status distribution
        status_rows = conn.execute(text("""
            SELECT subrogation_status, COUNT(*) as cnt
            FROM insurance_claims
            GROUP BY subrogation_status
        """)).mappings().all()
        status_dist = {r["subrogation_status"]: int(r["cnt"]) for r in status_rows}

        # Recent Activity Stream
        recent_rows = conn.execute(text("""
            SELECT c.claim_id, c.claim_number, c.claim_type, c.paid_amount,
                   c.subrogation_status, c.incident_date,
                   a.priority_level, a.net_recovery_estimate
            FROM insurance_claims c
            LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
            ORDER BY c.incident_date DESC
            LIMIT 10
        """)).mappings().all()

        recent_activity = [
            {
                "claim_id": r["claim_id"],
                "claim_number": r["claim_number"],
                "claim_type": r["claim_type"],
                "paid_amount": float(r["paid_amount"]),
                "subrogation_status": r["subrogation_status"],
                "incident_date": str(r["incident_date"]),
                "priority_level": r["priority_level"] or "Pending",
                "net_recovery_estimate": float(r["net_recovery_estimate"]) if r["net_recovery_estimate"] is not None else 0.0
            }
            for r in recent_rows
        ]

    return {
        "total_claims_analyzed": total_claims,
        "potential_recovery_opportunities": int(opp_count),
        "total_paid_exposure": total_paid,
        "projected_net_recovery": projected_net,
        "priority_distribution": prio_dist,
        "recovery_status_distribution": status_dist,
        "recent_activity": recent_activity
    }
