"""
SubroRecover AI - Page 7: Data Pipeline & ETL Health Monitoring
"""

import streamlit as st
import pandas as pd
from data_engineering.monitoring import PipelineMonitor
from data_engineering.pipeline import run_etl_pipeline
from frontend.components.ui_components import render_top_banner, render_kpi, render_section_title

def render_page():
    render_top_banner("Data Engineering Pipeline & Ingestion Health", "ETL Execution Telemetry, Validation Scores, Duplicate Detection & Throughput")

    latest = PipelineMonitor.get_latest_status()
    history = PipelineMonitor.get_history()

    # Ingestion & Telemetry KPIs
    k1, k2, k3, k4 = st.columns(4)
    status_label = latest.get("status", "N/A")
    duration = f"{latest.get('duration_seconds', 0.0):.2f}s"
    loaded = f"{latest.get('records_loaded', 0):,}"
    quality = f"{latest.get('validation_score_pct', 100.0):.1f}%"

    render_kpi(k1, "Latest Pipeline Status", status_label, latest.get("run_id", "Run ID"))
    render_kpi(k2, "Pipeline Runtime", duration, "Extraction to DB Load")
    render_kpi(k3, "Total Loaded Records", loaded, "Across 6 Relational Tables")
    render_kpi(k4, "Data Quality Score", quality, "Referential & Constraint Audit")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Action Row
    col_act, col_info = st.columns([1, 3])
    with col_act:
        if st.button("Trigger Full ETL Pipeline Run", type="primary", use_container_width=True):
            with st.spinner("Executing extraction, cleaning, transformation, validation & database loading..."):
                res = run_etl_pipeline()
                if res.get("status") == "SUCCESS":
                    st.success(f"ETL Execution complete! Loaded {res['total_loaded']} rows in {res['duration_seconds']}s.")
                    st.rerun()
                else:
                    st.error(f"ETL pipeline run failed: {res.get('error')}")

    with col_info:
        st.markdown("**Automated Safeguards:** Deduplication on composite natural keys, ISO-8601 date casting, foreign key orphan checks, and dual database persistence.")

    # Execution History
    render_section_title("Pipeline Execution Run History")
    if history:
        df_hist = pd.DataFrame(history)
        cols_to_show = ["run_id", "status", "duration_seconds", "records_ingested", "records_loaded", "validation_score_pct", "start_time"]
        st.dataframe(
            df_hist[[c for c in cols_to_show if c in df_hist.columns]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No prior execution history found.")

    # Latest Validation Audit
    render_section_title("Data Quality & Integrity Constraint Audit")
    errors = latest.get("errors", [])
    warnings = latest.get("warnings", [])

    if not errors and not warnings:
        st.success("All 12 relational and business constraint checks passed with zero errors or warnings.")
    else:
        if errors:
            st.error(f"Detected {len(errors)} validation errors:")
            for e in errors:
                st.markdown(f"• {e}")
        if warnings:
            st.warning(f"Detected {len(warnings)} validation notices:")
            for w in warnings:
                st.markdown(f"• {w}")
