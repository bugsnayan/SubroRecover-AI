"""
SubroRecover AI - Page 4: Recovery Intelligence & Financial Exposure
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from database.connection import engine
from frontend.components.ui_components import render_top_banner, render_kpi, render_section_title
from ml.predict import get_model

def render_page():
    render_top_banner("Subrogation Recovery Intelligence", "Comparative Liability Splitting, Recovery Yield Optimization & Exposure Analytics")

    with engine.connect() as conn:
        assessments = conn.execute(text("""
            SELECT a.assessment_id, a.claim_id, a.priority_level, a.priority_score,
                   a.estimated_adverse_fault_pct, a.gross_recovery_estimate,
                   a.net_recovery_estimate, a.insured_deductible_recovery, a.status,
                   c.claim_type, c.paid_amount, c.incident_state, c.subrogation_status
            FROM recovery_assessments a
            JOIN insurance_claims c ON a.claim_id = c.claim_id
            ORDER BY a.net_recovery_estimate DESC
        """)).mappings().all()

    if not assessments:
        st.info("No recovery assessments found. Execute AI investigation on claims to populate recovery intelligence.")
        return

    df_asm = pd.DataFrame(assessments)

    # Recovery KPIs
    total_net = df_asm["net_recovery_estimate"].sum()
    total_gross = df_asm["gross_recovery_estimate"].sum()
    total_ded = df_asm["insured_deductible_recovery"].sum()
    high_count = len(df_asm[df_asm["priority_level"] == "High"])

    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Total Net Recovery Potential", f"${total_net:,.0f}", f"Across {len(df_asm)} Analyzed Claims")
    render_kpi(k2, "Gross Recovery Exposure", f"${total_gross:,.0f}", "Theoretical 100% Liability")
    render_kpi(k3, "Make-Whole Deductibles", f"${total_ded:,.0f}", "Insured Policyholder Refunds")
    render_kpi(k4, "High Yield Targets", f"{high_count}", "Priority Demands Ready")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Visualizations
    col1, col2 = st.columns(2)
    with col1:
        render_section_title("Projected Net Recovery by Claim Incident Type")
        type_net = df_asm.groupby("claim_type")["net_recovery_estimate"].sum().reset_index()
        fig_net = px.bar(
            type_net,
            x="net_recovery_estimate",
            y="claim_type",
            orientation="h",
            color_discrete_sequence=["#1D4ED8"],
            labels={"net_recovery_estimate": "Net Recovery ($)", "claim_type": "Incident Type"}
        )
        fig_net.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_net, use_container_width=True)

    with col2:
        render_section_title("Adverse Fault Distribution vs. Net Recovery Yield")
        fig_scatter = px.scatter(
            df_asm,
            x="estimated_adverse_fault_pct",
            y="net_recovery_estimate",
            color="priority_level",
            color_discrete_map={"High": "#1D4ED8", "Medium": "#F59E0B", "Low": "#10B981"},
            hover_data=["claim_id", "paid_amount"],
            labels={"estimated_adverse_fault_pct": "Adverse Fault %", "net_recovery_estimate": "Net Recovery ($)"}
        )
        fig_scatter.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Detailed Table
    render_section_title("Subrogation Opportunity Register")
    df_table = df_asm.copy()
    df_table["paid_amount"] = df_table["paid_amount"].apply(lambda v: f"${v:,.2f}")
    df_table["net_recovery_estimate"] = df_table["net_recovery_estimate"].apply(lambda v: f"${v:,.2f}")
    df_table["insured_deductible_recovery"] = df_table["insured_deductible_recovery"].apply(lambda v: f"${v:,.2f}")
    df_table["estimated_adverse_fault_pct"] = df_table["estimated_adverse_fault_pct"].apply(lambda v: f"{v:.1f}%")

    st.dataframe(
        df_table[["claim_id", "claim_type", "incident_state", "paid_amount", "estimated_adverse_fault_pct", "net_recovery_estimate", "insured_deductible_recovery", "priority_level", "status"]],
        use_container_width=True,
        hide_index=True
    )
