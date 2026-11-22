"""
SubroRecover AI - Shared Portfolio Metrics Module
Provides unified calculation of high-level KPIs and recovery metrics
guaranteeing 100% mathematical reconciliation across Overview, Assistant,
Reports, and System Telemetry.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from sqlalchemy import text

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine

logger = logging.getLogger("subrorecover.services.metrics")


def sanitize_param(val: Any) -> Optional[str]:
    """Ensures parameter is a valid clean string, handling FastAPI Query default objects."""
    if val is None:
        return None
    if hasattr(val, "default"):
        return None
    s = str(val).strip()
    return s if s and not s.startswith("Query(") else None


def get_portfolio_kpis(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    incident_type: Optional[str] = None,
    state: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    conn=None
) -> Dict[str, Any]:
    """
    Computes official core recovery KPIs across the insurance portfolio.
    Guarantees that Overview endpoints and AI Assistant return identical numbers.
    """
    d_from = sanitize_param(date_from)
    d_to = sanitize_param(date_to)
    i_type = sanitize_param(incident_type)
    st = sanitize_param(state)
    prio = sanitize_param(priority)
    stat = sanitize_param(status)

    where_clauses = ["1=1"]
    params: Dict[str, Any] = {}

    if d_from:
        where_clauses.append("c.incident_date >= :date_from")
        params["date_from"] = d_from
    if d_to:
        where_clauses.append("c.incident_date <= :date_to")
        params["date_to"] = d_to
    if i_type:
        where_clauses.append("c.claim_type = :incident_type")
        params["incident_type"] = i_type
    if st:
        where_clauses.append("c.incident_state = :state")
        params["state"] = st
    if prio:
        where_clauses.append("a.priority_level = :priority")
        params["priority"] = prio
    if stat:
        where_clauses.append("c.subrogation_status = :status")
        params["status"] = stat

    filter_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT
            COUNT(c.claim_id) as total_claims,
            COALESCE(SUM(c.paid_amount), 0.0) as total_paid,
            COALESCE(SUM(a.net_recovery_estimate), 0.0) as projected_net,
            COALESCE(SUM(CASE WHEN c.subrogation_status = 'Closed Recovered' THEN a.net_recovery_estimate ELSE 0.0 END), 0.0) as recovered_to_date,
            COUNT(CASE WHEN a.priority_level = 'High' THEN 1 END) as high_urgency_demands
        FROM insurance_claims c
        LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
        WHERE {filter_sql}
    """

    def _execute(connection):
        row = connection.execute(text(query), params).mappings().first()
        t_claims = int(row["total_claims"]) if row else 0
        t_paid = round(float(row["total_paid"]), 2) if row else 0.0
        p_net = round(float(row["projected_net"]), 2) if row else 0.0
        r_date = round(float(row["recovered_to_date"]), 2) if row else 0.0
        h_urg = int(row["high_urgency_demands"]) if row else 0

        p_rate = round((p_net / t_paid * 100), 1) if t_paid > 0 else 0.0
        a_rate = round((r_date / t_paid * 100), 1) if t_paid > 0 else 0.0
        avg_paid = round(t_paid / t_claims, 2) if t_claims > 0 else 0.0

        return {
            "total_claims": t_claims,
            "total_paid": t_paid,
            "projected_recovery": p_net,
            "recovered_to_date": r_date,
            "high_urgency_demands": h_urg,
            "projected_recovery_rate": p_rate,
            "actual_recovery_rate": a_rate,
            "average_paid_exposure": avg_paid,
            "high_urgency_pct": round((h_urg / t_claims * 100), 1) if t_claims > 0 else 0.0
        }

    if conn is not None:
        return _execute(conn)
    else:
        with engine.connect() as new_conn:
            return _execute(new_conn)
