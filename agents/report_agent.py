"""
SubroRecover AI - Agent 6: Investigation Report Agent
Synthesizes outputs across all five agents into a unified, court-ready investigation dossier and persists assessments.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import SubroRecoverState
from database.connection import engine
from agents.llm_client import call_llm

logger = logging.getLogger("subrorecover.agents.report_agent")

class InvestigationReportAgent:
    """Agent 6: Consolidates multi-agent intelligence into structured investigation reports."""

    def __init__(self):
        self.name = "Investigation Report Agent"

    def execute(self, state: SubroRecoverState) -> SubroRecoverState:
        start_time = time.time()
        logger.info(f"[{self.name}] Synthesizing final investigation dossier for claim {state.claim_id}...")

        claim_sum = state.claim_summary
        ev_analysis = state.evidence_analysis
        liab = state.liability_assessment
        rec = state.recovery_estimation
        prio = state.prioritization

        report_id = f"RPT-{state.claim_id}-{int(time.time())}"
        report_num = f"SIR-2026-{state.claim_id.replace('CLM-', '')}"

        # 1. Actionable Recommendations
        recommendations = []
        if prio.get("priority_level") == "High":
            recommendations.append("Issue formal Subrogation Demand Package to adverse carrier within 5 business days.")
            recommendations.append("Submit proof-of-loss ledger and certified repair invoice.")
            if state.evidence_citations:
                recommendations.append(f"Cite adverse operator statutory violations ({'; '.join(state.evidence_citations)}) in demand letter.")
        elif prio.get("priority_level") == "Medium":
            recommendations.append("Request recorded statement transcript from adverse driver to resolve disputed points.")
            recommendations.append("Conduct scene photography inspection if liability split is challenged.")
        else:
            recommendations.append("Document file for potential subrogation closure due to insufficient third-party exposure.")

        # 2. Missing Documentation Checklist
        missing_docs = []
        if not ev_analysis.get("has_police_report", False):
            missing_docs.append("Certified Police Traffic Crash Narrative")
        if not state.evidence_citations:
            missing_docs.append("Traffic Court Citation Records")
        if not state.evidence_sources:
            missing_docs.append("Scene Photography / Dashcam Footage")
        if not missing_docs:
            missing_docs.append("None — Case file evidentiary documentation is complete.")

        # 3. Comprehensive Executive Summary
        exec_summary = (
            f"Subrogation investigation for claim {state.claim_id} ({claim_sum.get('claim_type', 'Vehicle Collision')}) "
            f"concluded an estimated {liab.get('adverse_fault_pct', 0.0):.1f}% potential liability against the adverse party "
            f"under {liab.get('jurisdiction_state', 'TX')} {liab.get('negligence_doctrine', 'Comparative Negligence')}. "
            f"Net carrier recoverable exposure is projected at ${rec.get('net_carrier_recovery', 0.0):,.2f} with "
            f"${rec.get('insured_deductible_recovery', 0.0):,.2f} earmarked for insured deductible refund under the Make-Whole Doctrine. "
            f"The Machine Learning evaluation ranked this file as '{prio.get('priority_level', 'Medium')}' Priority "
            f"({prio.get('priority_score', 0.0)*100:.1f}% confidence)."
        )

        # Optional LLM refinement
        llm_prompt = f"""You are a Chief Claims Officer. Synthesize this executive summary into 3 crisp, authoritative sentences:
{exec_summary}
Include actionable conclusion for adjuster sign-off."""

        llm_response = call_llm(llm_prompt, system_instruction="Provide executive insurance claims intelligence summaries.")
        mode = "LIVE_LLM (Gemini)" if llm_response else "LOCAL_DETERMINISTIC_RULES"
        if llm_response:
            final_exec_summary = llm_response.strip()
        else:
            final_exec_summary = exec_summary

        # Build full report dossier object
        dossier = {
            "report_id": report_id,
            "report_number": report_num,
            "claim_id": state.claim_id,
            "generation_timestamp": datetime.utcnow().isoformat() + "Z",
            "executive_summary": final_exec_summary,
            "claim_overview": claim_sum,
            "evidentiary_findings": ev_analysis,
            "verified_facts": state.verified_facts,
            "statutory_citations": state.evidence_citations,
            "liability_assessment": liab,
            "recovery_financials": rec,
            "prioritization_metrics": prio,
            "recommended_actions": recommendations,
            "missing_documentation_checklist": missing_docs,
            "governance_disclaimer": (
                "DISCLAIMER: SubroRecover AI is an automated decision-support system. "
                "Findings do not constitute binding legal determinations or financial guarantees. "
                "Final settlement demand requires authorized Human Adjuster approval."
            ),
            "mode": mode
        }

        # 4. Persist Assessment & Report to Relational Database
        try:
            with engine.begin() as conn:
                # Upsert into recovery_assessments
                conn.execute(text("""
                    INSERT INTO recovery_assessments (
                        assessment_id, claim_id, priority_level, priority_score,
                        estimated_adverse_fault_pct, gross_recovery_estimate,
                        net_recovery_estimate, insured_deductible_recovery,
                        recovery_probability, liability_rationale, quantum_rationale,
                        missing_evidence, status
                    ) VALUES (
                        :aid, :cid, :p_lvl, :p_scr, :adv_flt, :gross, :net, :ded,
                        :prob, :l_rat, :q_rat, :missing, :stat
                    )
                    ON CONFLICT (assessment_id) DO UPDATE SET
                        priority_level = EXCLUDED.priority_level,
                        net_recovery_estimate = EXCLUDED.net_recovery_estimate,
                        status = EXCLUDED.status
                """), {
                    "aid": f"ASM-{state.claim_id}",
                    "cid": state.claim_id,
                    "p_lvl": prio.get("priority_level", "Medium"),
                    "p_scr": prio.get("priority_score", 0.75),
                    "adv_flt": liab.get("adverse_fault_pct", 0.0),
                    "gross": rec.get("gross_recovery_estimate", 0.0),
                    "net": rec.get("net_carrier_recovery", 0.0),
                    "ded": rec.get("insured_deductible_recovery", 0.0),
                    "prob": prio.get("priority_score", 0.75),
                    "l_rat": liab.get("liability_rationale", "")[:500],
                    "q_rat": rec.get("quantum_rationale", "")[:500],
                    "missing": "; ".join(missing_docs),
                    "stat": "Pending Review"
                })

                # Insert or update investigation_reports
                conn.execute(text("""
                    INSERT INTO investigation_reports (
                        report_id, claim_id, report_number, report_title,
                        executive_summary, full_report_json, is_approved
                    ) VALUES (
                        :rid, :cid, :rnum, :rtitle, :esum, :rjson, :appr
                    )
                    ON CONFLICT (report_id) DO UPDATE SET
                        executive_summary = EXCLUDED.executive_summary,
                        full_report_json = EXCLUDED.full_report_json
                """), {
                    "rid": f"RPT-{state.claim_id}",
                    "cid": state.claim_id,
                    "rnum": f"SIR-2026-{state.claim_id.replace('CLM-', '')}",
                    "rtitle": f"Subrogation Investigation Report — {state.claim_id}",
                    "esum": final_exec_summary,
                    "rjson": json.dumps(dossier),
                    "appr": False
                })

                # Update insurance_claims subrogation_status
                new_subro_status = "Demand Ready" if prio.get("priority_level") == "High" else "In Investigation"
                conn.execute(text("""
                    UPDATE insurance_claims
                    SET subrogation_status = :n_stat, updated_at = CURRENT_TIMESTAMP
                    WHERE claim_id = :cid
                """), {"n_stat": new_subro_status, "cid": state.claim_id})

            logger.info(f"Persisted assessment and report records for claim {state.claim_id} to database.")
        except Exception as e:
            logger.warning(f"Notice while persisting to DB: {e}")

        # Update State
        state.report_id = report_id
        state.investigation_report = dossier
        state.executive_summary = final_exec_summary
        state.recommended_actions = recommendations
        state.missing_documentation_checklist = missing_docs
        state.workflow_status = "COMPLETED"

        duration_ms = int((time.time() - start_time) * 1000)
        state.agent_logs.append({
            "agent_name": self.name,
            "step": 6,
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "mode": mode,
            "summary": f"Generated dossier {report_id}; Recommended {len(recommendations)} actions."
        })

        logger.info(f"[{self.name}] Completed in {duration_ms}ms (Mode: {mode})")
        return state
