"""
SubroRecover AI - Enterprise Streamlit Dashboard Application
Main entry point with persistent navigation sidebar and multi-page routing.
"""

import os
import sys
import streamlit as st

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.components.ui_components import apply_enterprise_theme
from frontend.pages import (
    page_executive_overview,
    page_claims_management,
    page_investigation_workspace,
    page_recovery_intelligence,
    page_document_intelligence,
    page_investigation_reports,
    page_pipeline_monitoring,
    page_model_performance
)

# Set Page Config
st.set_page_config(
    page_title="SubroRecover AI — Enterprise Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply corporate CSS
apply_enterprise_theme()

# Sidebar Brand & Navigation
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0px 20px 0px;">
            <div style="font-size: 18px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">SUBRORECOVER AI</div>
            <div style="font-size: 11px; font-weight: 600; color: #1D4ED8; text-transform: uppercase; letter-spacing: 0.05em;">Enterprise Intelligence System</div>
        </div>
    """, unsafe_allow_html=True)

    pages = {
        "Executive Overview": page_executive_overview,
        "Claims Management": page_claims_management,
        "AI Investigation Workspace": page_investigation_workspace,
        "Recovery Intelligence": page_recovery_intelligence,
        "Document Intelligence": page_document_intelligence,
        "Investigation Reports": page_investigation_reports,
        "Data Pipeline Monitoring": page_pipeline_monitoring,
        "Model Performance": page_model_performance
    }

    selected_page_name = st.radio(
        "OPERATIONAL MODULES",
        list(pages.keys()),
        index=0
    )

    st.markdown("---")
    
    # Environment & System Status Pill
    llm_active = bool(os.getenv("GEMINI_API_KEY", "").strip())
    st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 10px; font-size: 11px;">
            <div style="font-weight: 600; color: #0F172A; margin-bottom: 4px;">SYSTEM TELEMETRY</div>
            <div style="color: #475569;">Environment: <b>Local Dev / Eval</b></div>
            <div style="color: #475569;">Database: <b>SQLite (Auto-Resilient)</b></div>
            <div style="color: #475569;">AI Engine: <b>{'Gemini Live' if llm_active else 'Deterministic Grounded'}</b></div>
            <div style="color: #475569; margin-top: 4px; font-size: 10px;">Target: Value Momentum Eval 2027</div>
        </div>
    """, unsafe_allow_html=True)

# Render selected page
selected_module = pages[selected_page_name]
selected_module.render_page()
