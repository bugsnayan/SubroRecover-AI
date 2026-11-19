"""
SubroRecover AI - Page 3: AI Investigation Workspace
Interactive multi-agent execution cockpit with live telemetry and Human-in-the-Loop review gate.
"""

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import engine
from frontend.components.ui_components import render_top_banner, render_kpi, render_section_title, get_priority_badge
from agents.workflow import run_investigation_workflow
from reports.report_generator import generate_subrogation_pdf

def render_page():
    render_top_banner("AI Investigation & Multi-Agent Workspace", "Autonomous 6-Agent Reasoning Pipeline with Human-in-the-Loop Governance")

    with engine.connect() as conn:
        claims = conn.execute(text("SELECT claim_id, claim_number, claim_type, paid_amount, subrogation_status FROM insurance_claims ORDER BY claim_id ASC LIMIT 100")).mappings().all()

    if not claims:
        st.warning("No claims found in database. Ingest sample data to proceed.")
        return

    claim_map = {f"{c['claim_id']} — {c['claim_number']} ({c['claim_type']} | ${float(c['paid_amount']):,.0f})": c["claim_id"] for c in claims}
    selected_label = st.selectbox("Select Target Claim for AI Subrogation Investigation:", list(claim_map.keys()), index=0)
    claim_id = claim_map[selected_label]

    # Inspection & Action Header
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"**Target Claim File:** `{claim_id}` | System will execute 6 specialized agents in sequence.")
    with col_btn:
        run_trigger = st.button("Trigger AI Investigation", type="primary", use_container_width=True)

    # If triggered, run live LangGraph workflow
    if run_trigger:
        with st.spinner(f"Coordinating LangGraph Agents for Claim {claim_id}..."):
            try:
                final_state = run_investigation_workflow(claim_id)
                st.session_state[f"workflow_{claim_id}"] = final_state
                st.success(f"Investigation completed successfully! Ranked as {final_state.priority_level} Priority.")
            except Exception as e:
                st.error(f"Multi-Agent execution error: {e}")

    # Fetch latest state (either from session or DB)
    state = st.session_state.get(f"workflow_{claim_id}")

    # If not in session, load from DB assessment if exists
    if not state:
        with engine.connect() as conn:
            asm = conn.execute(text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
            inv_rep = conn.execute(text("SELECT * FROM investigation_reports WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
            logs = conn.execute(text("SELECT * FROM agent_execution_logs WHERE claim_id = :cid ORDER BY execution_step ASC"), {"cid": claim_id}).mappings().all()

        if asm:
            st.info(f"Displaying stored assessment for `{claim_id}` (Status: {asm['status']}). You can re-run above anytime.")
            # Display KPIs
            k1, k2, k3, k4 = st.columns(4)
            render_kpi(k1, "Priority Level", asm["priority_level"], f"Score: {float(asm['priority_score']):.2f}")
            render_kpi(k2, "Adverse Fault", f"{float(asm['estimated_adverse_fault_pct']):.1f}%", "Comparative Negligence Split")
            render_kpi(k3, "Net Recovery Estimate", f"${float(asm['net_recovery_estimate']):,.2f}", "Projected Carrier Recovery")
            render_kpi(k4, "Insured Deductible", f"${float(asm['insured_deductible_recovery']):,.2f}", "Make-Whole Refund")

            # Agent logs table
            if logs:
                render_section_title("Agentic Execution Traces (Audit Trail)")
                df_logs = pd.DataFrame(logs)
                st.dataframe(df_logs[["agent_name", "execution_step", "status", "input_payload", "output_payload", "execution_duration_ms"]], use_container_width=True, hide_index=True)

            # Human Review Form
            render_section_title("Human-in-the-Loop Adjuster Sign-Off Gate")
            with st.form(key=f"hitl_form_{claim_id}"):
                c_dec, c_notes = st.columns([1, 2])
                with c_dec:
                    decision = st.selectbox("Adjuster Governance Decision:", ["Approved — Dispatch Demand", "Modified — Adjust Fault/Quantum", "Rejected — Close Subrogation", "Escalate to Legal"])
                    adj_fault = st.number_input("Adjusted Adverse Fault % (Optional):", min_value=0.0, max_value=100.0, value=float(asm["estimated_adverse_fault_pct"]))
                with c_notes:
                    notes = st.text_area("Adjuster Review Notes & Justification:", value="Reviewed evidentiary citations and approved subrogation demand packet.")
                    reviewer = st.text_input("Reviewer Authorized Signature:", value="Senior Claims Adjuster")

                submit_btn = st.form_submit_button("Submit Governance Decision", type="primary")
                if submit_btn:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO human_review_records (
                                review_id, claim_id, assessment_id, reviewer_name,
                                reviewer_role, decision, adjusted_fault_pct, review_notes
                            ) VALUES (
                                :rid, :cid, :aid, :rname, 'Subrogation Specialist', :dec, :afault, :notes
                            )
                        """), {
                            "rid": f"REV-{os.urandom(3).hex().upper()}",
                            "cid": claim_id,
                            "aid": asm["assessment_id"],
                            "rname": reviewer,
                            "dec": decision.split(" — ")[0],
                            "afault": adj_fault,
                            "notes": notes
                        })
                        conn.execute(text("""
                            UPDATE recovery_assessments
                            SET status = :stat, updated_at = CURRENT_TIMESTAMP
                            WHERE claim_id = :cid
                        """), {"stat": f"Adjuster {decision.split(' — ')[0]}", "cid": claim_id})
                    st.success("Human review governance decision recorded in database!")
                    st.rerun()

            # Download Report Button
            if inv_rep:
                render_section_title("Formal Subrogation Investigation Report")
                import json
                try:
                    dossier = json.loads(inv_rep["full_report_json"])
                except Exception:
                    dossier = {}
                pdf_path = generate_subrogation_pdf(dossier)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="Download Court-Ready Investigation PDF (ReportLab)",
                        data=pdf_bytes,
                        file_name=f"Subro_Report_{claim_id}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

        else:
            st.info("No prior assessment found for this claim. Click 'Trigger AI Investigation' above to execute all 6 agents.")
            return

    elif state:
        # Display Live Workflow State
        k1, k2, k3, k4 = st.columns(4)
        render_kpi(k1, "Priority Level", state.priority_level, f"Score: {state.priority_score:.2f}")
        render_kpi(k2, "Adverse Fault", f"{state.adverse_fault_pct:.1f}%", state.negligence_doctrine)
        render_kpi(k3, "Net Recovery Estimate", f"${state.net_recovery_estimate:,.2f}", "Carrier Projected Yield")
        render_kpi(k4, "Insured Deductible", f"${state.deductible_recovery_estimate:,.2f}", "Make-Whole Refund")

        # Tabs for Individual Agent Outputs
        t1, t2, t3, t4, t5, t6 = st.tabs([
            "1. Claim Analysis",
            "2. Evidence & RAG",
            "3. Liability Assessment",
            "4. Recovery Quantum",
            "5. ML Prioritization",
            "6. Unified Dossier"
        ])

        with t1:
            st.markdown(f"**Validation Status:** `{state.claim_validation_status}`")
            st.json(state.claim_summary)

        with t2:
            st.markdown(f"**Verified Document Facts ({len(state.verified_facts)}):**")
            for f in state.verified_facts:
                st.markdown(f"• {f}")
            st.markdown("---")
            st.markdown(f"**Statutory Violations & Citations ({len(state.evidence_citations)}):**")
            for c in state.evidence_citations:
                st.markdown(f"• `{c}`")
            st.json(state.evidence_analysis)

        with t3:
            st.markdown(f"**Jurisdiction & Doctrine:** {state.liability_assessment.get('jurisdiction_state')} — {state.negligence_doctrine}")
            st.markdown(f"**Liability Rationale:** {state.liability_rationale}")
            st.markdown(f"**Third-Party Actionable:** `{state.is_third_party_liable}`")

        with t4:
            st.markdown(f"**Financial Quantum Breakdown:**")
            st.markdown(f"- **Gross Theoretical Potential:** `${state.gross_recovery_estimate:,.2f}`")
            st.markdown(f"- **Make-Whole Insured Deductible Refund:** `${state.deductible_recovery_estimate:,.2f}`")
            st.markdown(f"- **Estimated Collection Overhead (5%):** `${state.estimated_collection_cost:,.2f}`")
            st.markdown(f"- **Net Projected Carrier Recovery:** `${state.net_recovery_estimate:,.2f}`")
            st.markdown(f"**Financial Assumptions:** {state.quantum_rationale}")

        with t5:
            st.markdown(f"**Machine Learning Priority Model Output:**")
            st.markdown(f"- **Priority Tier:** `{state.priority_level}` (Confidence: {state.priority_score*100:.1f}%)")
            st.markdown(f"- **Top Contributing Factors:** {', '.join(state.contributing_factors)}")
            st.json(state.prioritization)

        with t6:
            st.markdown(f"**Executive Dossier Summary:**")
            st.markdown(state.executive_summary)
            st.markdown("**Actionable Recommendations:**")
            for a in state.recommended_actions:
                st.markdown(f"• {a}")
            st.markdown("**Missing Evidence Checklist:**")
            for m in state.missing_documentation_checklist:
                st.markdown(f"• {m}")

            # PDF Download
            pdf_path = generate_subrogation_pdf(state.investigation_report)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="Download Official Court-Ready Investigation PDF",
                    data=pdf_bytes,
                    file_name=f"Subro_Report_{claim_id}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
