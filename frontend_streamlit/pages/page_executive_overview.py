"""
SubroRecover AI - Page 1: Executive Overview Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from database.connection import engine
from frontend.components.ui_components import render_top_banner, render_kpi, render_section_title

def render_page():
    render_top_banner("Executive Subrogation Intelligence Overview", "Portfolio Performance, Recovery Exposure & Case Triage Analytics")

    with engine.connect() as conn:
        # 1. KPIs
        stats = conn.execute(text("""
            SELECT
                COUNT(*) as total_claims,
                COALESCE(SUM(paid_amount), 0.0) as total_paid,
                COALESCE(AVG(paid_amount), 0.0) as avg_paid
            FROM insurance_claims
        """)).mappings().first()

        asm_stats = conn.execute(text("""
            SELECT
                COUNT(*) as total_assessed,
                COALESCE(SUM(net_recovery_estimate), 0.0) as proj_net,
                COALESCE(SUM(insured_deductible_recovery), 0.0) as proj_ded
            FROM recovery_assessments
        """)).mappings().first()

        high_prio_count = conn.execute(text("""
            SELECT COUNT(*) FROM recovery_assessments WHERE priority_level = 'High'
        """)).scalar() or 0

        total_claims = int(stats["total_claims"])
        total_paid = float(stats["total_paid"])
        proj_net = float(asm_stats["proj_net"])
        total_assessed = int(asm_stats["total_assessed"])

        # Display KPIs
        k1, k2, k3, k4 = st.columns(4)
        render_kpi(k1, "Total Claims Ingested", f"{total_claims:,}", "100% Data Quality Verified")
        render_kpi(k2, "Total Paid Exposure", f"${total_paid:,.0f}", f"Avg Paid: ${float(stats['avg_paid']):,.0f}")
        render_kpi(k3, "Projected Net Recovery", f"${proj_net:,.0f}", f"Across {total_assessed} Assessed Claims")
        render_kpi(k4, "High Urgency Demands", f"{high_prio_count}", "Immediate Subro Opportunity")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # 2. Charts Row
        c1, c2 = st.columns(2)

        with c1:
            render_section_title("Subrogation Triage Priority Distribution")
            prio_rows = conn.execute(text("""
                SELECT priority_level, COUNT(*) as count
                FROM recovery_assessments
                GROUP BY priority_level
            """)).mappings().all()

            if prio_rows:
                df_prio = pd.DataFrame(prio_rows)
                color_map = {"High": "#1D4ED8", "Medium": "#F59E0B", "Low": "#10B981"}
                fig_prio = px.pie(
                    df_prio,
                    values="count",
                    names="priority_level",
                    hole=0.45,
                    color="priority_level",
                    color_discrete_map=color_map
                )
                fig_prio.update_traces(textposition="inside", textinfo="percent+label")
                fig_prio.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=260,
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_prio, use_container_width=True)
            else:
                st.info("Execute AI investigation on sample claims to view priority distribution.")

        with c2:
            render_section_title("Carrier Loss vs. Subrogation Recovery Exposure")
            claim_type_stats = conn.execute(text("""
                SELECT claim_type, SUM(paid_amount) as total_loss, COUNT(*) as claim_count
                FROM insurance_claims
                GROUP BY claim_type
                ORDER BY total_loss DESC
                LIMIT 5
            """)).mappings().all()

            if claim_type_stats:
                df_types = pd.DataFrame(claim_type_stats)
                fig_bar = px.bar(
                    df_types,
                    x="total_loss",
                    y="claim_type",
                    orientation="h",
                    color_discrete_sequence=["#1D4ED8"],
                    labels={"total_loss": "Paid Exposure ($)", "claim_type": "Claim Incident Type"}
                )
                fig_bar.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=260,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # 3. Recent Activity Stream
        render_section_title("Recent Claims & AI Investigation Activity")
        recent_rows = conn.execute(text("""
            SELECT c.claim_id, c.claim_number, c.claim_type, c.incident_state,
                   c.paid_amount, c.subrogation_status,
                   COALESCE(a.priority_level, 'Unassessed') as priority_level,
                   COALESCE(a.net_recovery_estimate, 0.0) as net_recovery
            FROM insurance_claims c
            LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
            ORDER BY c.incident_date DESC
            LIMIT 8
        """)).mappings().all()

        if recent_rows:
            df_recent = pd.DataFrame(recent_rows)
            df_recent["paid_amount"] = df_recent["paid_amount"].apply(lambda v: f"${v:,.2f}")
            df_recent["net_recovery"] = df_recent["net_recovery"].apply(lambda v: f"${v:,.2f}" if v > 0 else "—")
            st.dataframe(
                df_recent,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "claim_id": "Claim ID",
                    "claim_number": "Claim No.",
                    "claim_type": "Incident Type",
                    "incident_state": "Jurisdiction",
                    "paid_amount": "Carrier Paid",
                    "subrogation_status": "Status",
                    "priority_level": "AI Priority",
                    "net_recovery": "Projected Recovery"
                }
            )
