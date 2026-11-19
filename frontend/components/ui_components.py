"""
SubroRecover AI - Enterprise UI Component Library
"""

import streamlit as st

def apply_enterprise_theme():
    """Injects custom enterprise CSS into the Streamlit session."""
    try:
        with open("frontend/assets/style.css", "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass

def render_top_banner(page_title: str, subtitle: str = "Enterprise Subrogation Intelligence Platform"):
    """Renders a standard corporate page masthead."""
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div style="font-size: 22px; font-weight: 700; color: #0F172A; letter-spacing: -0.02em;">{page_title}</div>
            <div style="font-size: 13px; color: #64748B; margin-top: 2px;">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def render_kpi(col, title: str, value: str, subtext: str = ""):
    """Renders a compact, high-contrast KPI metric card."""
    with col:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                {"<div class='kpi-subtext'>" + subtext + "</div>" if subtext else ""}
            </div>
        """, unsafe_allow_html=True)

def get_priority_badge(level: str) -> str:
    """Returns HTML for an enterprise priority badge."""
    lvl = str(level).strip().capitalize()
    if lvl == "High":
        return '<span class="badge-high">HIGH PRIORITY</span>'
    elif lvl == "Medium":
        return '<span class="badge-med">MEDIUM PRIORITY</span>'
    elif lvl == "Low":
        return '<span class="badge-low">LOW PRIORITY</span>'
    return f'<span class="badge-info">{level.upper()}</span>'

def render_section_title(title: str):
    """Renders an enterprise section divider."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
