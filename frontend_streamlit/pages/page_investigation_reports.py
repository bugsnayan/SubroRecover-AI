"""
SubroRecover AI - Page 6: Investigation Reports & Official PDF Demands
"""

import os
import json
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import engine
from frontend.components.ui_components import render_top_banner, render_section_title
from reports.report_generator import generate_subrogation_pdf

def render_page():
    render_top_banner("Subrogation Investigation Reports", "Official 14-Section Court-Ready Dossiers & Formal Recovery Demand Packages")

    with engine.connect() as conn:
        reports = conn.execute(text("""
            SELECT r.report_id, r.claim_id, r.report_number, r.report_title,
                   r.executive_summary, r.is_approved, r.created_at,
                   c.paid_amount, c.subrogation_status,
                   COALESCE(a.priority_level, 'Medium') as priority_level,
                   COALESCE(a.net_recovery_estimate, 0.0) as net_recovery
            FROM investigation_reports r
            JOIN insurance_claims c ON r.claim_id = c.claim_id
            LEFT JOIN recovery_assessments a ON r.claim_id = a.claim_id
            ORDER BY r.created_at DESC
        """)).mappings().all()

    if not reports:
        st.info("No investigation reports have been generated yet. Execute AI investigations in the Workspace.")
        return

    df_reports = pd.DataFrame(reports)

    render_section_title(f"Generated Investigation Reports ({len(df_reports)})")
    st.dataframe(
        df_reports[["report_id", "claim_id", "report_number", "priority_level", "net_recovery", "subrogation_status", "created_at"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    render_section_title("Inspect & Download Formal Subrogation Package")

    report_ids = [r["report_id"] for r in reports]
    selected_rid = st.selectbox("Select Report to Review & Export:", report_ids, index=0)

    if selected_rid:
        with engine.connect() as conn:
            rep_row = conn.execute(text("SELECT * FROM investigation_reports WHERE report_id = :rid"), {"rid": selected_rid}).mappings().first()

        if rep_row:
            raw_json = rep_row["full_report_json"]
            try:
                dossier = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
            except Exception:
                dossier = {}

            c_info, c_down = st.columns([3, 1])
            with c_info:
                st.markdown(f"**Report Number:** `{rep_row['report_number']}` | **Claim ID:** `{rep_row['claim_id']}`")
                st.markdown(f"**Executive Finding:** {rep_row['executive_summary']}")
            with c_down:
                pdf_path = generate_subrogation_pdf(dossier)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"{rep_row['report_number']}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

            # Expandable Raw Dossier JSON
            with st.expander("View Full Structured Dossier JSON", expanded=False):
                st.json(dossier)
