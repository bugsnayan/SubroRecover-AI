"""
SubroRecover AI - Page 2: Claims Management & Registry
"""

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import engine
from frontend.components.ui_components import render_top_banner, render_kpi, render_section_title
from rag.retriever import EvidenceRetriever

retriever = EvidenceRetriever()

def render_page():
    render_top_banner("Insurance Claims Management", "Search, Filter, Inspect Dossiers & Ingest Supporting Documentation")

    # Filter Bar
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        search_query = st.text_input("Search Claims by ID, Claim Number, or Description", placeholder="e.g. CLM-0001, Rear-end, Texas...")
    with f2:
        status_filter = st.selectbox("Subrogation Status", ["All Statuses", "Identified", "Demand Ready", "In Triage", "Closed No Subro", "Under HITL Review"])
    with f3:
        type_filter = st.selectbox("Incident Type", ["All Types", "Rear-end Collision", "T-bone Intersection Impact", "Side-swipe Lane Change", "Failure to Yield", "Single Vehicle Impact"])

    # Query Claims
    query = """
        SELECT c.claim_id, c.claim_number, c.claim_type, c.incident_date, c.incident_state,
               c.claimed_amount, c.paid_amount, c.deductible_paid, c.subrogation_status,
               cu.first_name || ' ' || cu.last_name as policyholder,
               p.policy_number, p.policy_type
        FROM insurance_claims c
        JOIN customers cu ON c.customer_id = cu.customer_id
        JOIN insurance_policies p ON c.policy_id = p.policy_id
        WHERE 1=1
    """
    params = {}
    if search_query:
        query += " AND (c.claim_id LIKE :sq OR c.claim_number LIKE :sq OR c.description LIKE :sq)"
        params["sq"] = f"%{search_query}%"
    if status_filter != "All Statuses":
        query += " AND c.subrogation_status = :st"
        params["st"] = status_filter
    if type_filter != "All Types":
        query += " AND c.claim_type = :ct"
        params["ct"] = type_filter

    query += " ORDER BY c.incident_date DESC LIMIT 100"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    if rows:
        df = pd.DataFrame(rows)
        st.markdown(f"**Showing {len(df)} matching insurance claims:**")

        # Display claim table
        df_display = df.copy()
        df_display["claimed_amount"] = df_display["claimed_amount"].apply(lambda v: f"${v:,.2f}")
        df_display["paid_amount"] = df_display["paid_amount"].apply(lambda v: f"${v:,.2f}")

        st.dataframe(
            df_display[["claim_id", "claim_number", "policyholder", "policy_type", "claim_type", "incident_date", "incident_state", "paid_amount", "subrogation_status"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        render_section_title("Claim Dossier Deep-Dive & Document Upload")

        # Select a claim to inspect
        claim_ids = list(df["claim_id"])
        selected_cid = st.selectbox("Select Claim ID to Inspect Dossier & Evidence:", claim_ids, index=0)

        if selected_cid:
            with engine.connect() as conn:
                claim_detail = conn.execute(text("SELECT * FROM insurance_claims WHERE claim_id = :cid"), {"cid": selected_cid}).mappings().first()
                parties = conn.execute(text("SELECT * FROM involved_parties WHERE claim_id = :cid"), {"cid": selected_cid}).mappings().all()
                docs = conn.execute(text("SELECT * FROM evidence_documents WHERE claim_id = :cid"), {"cid": selected_cid}).mappings().all()
                rep = conn.execute(text("SELECT * FROM accident_reports WHERE claim_id = :cid"), {"cid": selected_cid}).mappings().first()

            t1, t2, t3 = st.tabs(["Claim & Coverage Dossier", "Accident Report & Parties", "Document Intelligence & Upload"])

            with t1:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Claim ID:** `{claim_detail['claim_id']}`")
                    st.markdown(f"**Claim Number:** `{claim_detail['claim_number']}`")
                    st.markdown(f"**Incident Date:** {claim_detail['incident_date']}")
                    st.markdown(f"**Location:** {claim_detail['incident_location']}, {claim_detail['incident_state']}")
                with col_b:
                    st.markdown(f"**Carrier Paid Loss:** `${float(claim_detail['paid_amount']):,.2f}`")
                    st.markdown(f"**Deductible Outlay:** `${float(claim_detail['deductible_paid']):,.2f}`")
                    st.markdown(f"**Subrogation Status:** `{claim_detail['subrogation_status']}`")
                    st.markdown(f"**Description:** {claim_detail['description']}")

            with t2:
                if rep:
                    st.markdown(f"**Police Report No:** `{rep['police_report_number']}` | **Department:** {rep['police_department']}")
                    st.markdown(f"**Citations Issued:** `{rep['citations_issued']}`")
                    st.markdown(f"**Officer Narrative:** {rep['officer_narrative']}")
                st.markdown("---")
                st.markdown("**Involved Parties:**")
                if parties:
                    df_parties = pd.DataFrame(parties)
                    st.dataframe(df_parties[["party_type", "full_name", "vehicle_year_make_model", "insurance_carrier", "estimated_fault_percentage", "citation_received"]], use_container_width=True, hide_index=True)

            with t3:
                st.markdown(f"**Indexed Documents for `{selected_cid}`:**")
                if docs:
                    df_docs = pd.DataFrame(docs)
                    st.dataframe(df_docs[["document_name", "document_type", "ocr_confidence", "is_verified", "upload_date"]], use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("**Upload New Supporting Evidence Document (PDF):**")
                up_file = st.file_uploader(f"Upload PDF for {selected_cid}:", type=["pdf"], key=f"up_{selected_cid}")
                up_type = st.selectbox("Document Classification:", ["Police Crash Report", "Operator Statement", "Certified Repair Estimate", "Arbitration Precedent"], key=f"dt_{selected_cid}")

                if up_file is not None and st.button("Process & Index via ChromaDB", key=f"btn_up_{selected_cid}", type="primary"):
                    os.makedirs(f"uploaded_documents/{selected_cid}", exist_ok=True)
                    save_path = f"uploaded_documents/{selected_cid}/{up_file.name}"
                    with open(save_path, "wb") as f:
                        f.write(up_file.getbuffer())

                    # Index
                    chunks_count = retriever.index_pdf(save_path, claim_id=selected_cid, doc_type=up_type, is_verified=True)

                    # Insert DB record
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO evidence_documents (
                                document_id, claim_id, document_name, document_type,
                                file_path, file_size_bytes, extracted_text,
                                ocr_confidence, is_verified
                            ) VALUES (
                                :did, :cid, :dname, :dtype, :fpath, :fsize, :txt, 0.99, TRUE
                            )
                        """), {
                            "did": f"DOC-UP-{os.urandom(3).hex().upper()}",
                            "cid": selected_cid,
                            "dname": up_file.name,
                            "dtype": up_type,
                            "fpath": save_path,
                            "fsize": len(up_file.getvalue()),
                            "txt": f"Indexed {chunks_count} chunks in ChromaDB."
                        })
                    st.success(f"Successfully processed and indexed '{up_file.name}' into vector store ({chunks_count} chunks)!")
                    st.rerun()
    else:
        st.warning("No insurance claims found matching criteria. Ingest sample data via Pipeline Monitoring.")
