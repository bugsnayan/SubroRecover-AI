"""
SubroRecover AI - Page 5: Document Intelligence & RAG Exploration
"""

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import engine
from frontend.components.ui_components import render_top_banner, render_section_title
from rag.retriever import EvidenceRetriever
from rag.document_loader import DocumentLoader

retriever = EvidenceRetriever()

def render_page():
    render_top_banner("Document Intelligence & Semantic RAG Search", "Extract, Audit & Interrogate Police Reports, Repair Estimates & Witness Transcripts")

    with engine.connect() as conn:
        docs = conn.execute(text("SELECT * FROM evidence_documents ORDER BY upload_date DESC LIMIT 50")).mappings().all()

    c1, c2 = st.columns([1, 1])

    with c1:
        render_section_title("ChromaDB Semantic Query Engine")
        query_text = st.text_input("Enter Legal / Evidentiary Query:", value="traffic signal red light speed violation impact", placeholder="e.g. failure to yield, cell phone, rear bumper damage...")
        target_claim = st.text_input("Filter by Specific Claim ID (Optional):", value="", placeholder="e.g. CLM-0001")

        if st.button("Execute Vector Search", type="primary"):
            cid_param = target_claim.strip() if target_claim.strip() else None
            results = retriever.vector_store.query(query_text=query_text, n_results=4, claim_id=cid_param)

            if results:
                st.markdown(f"**Found {len(results)} relevant semantic passages:**")
                for idx, r in enumerate(results):
                    meta = r.get("metadata", {})
                    sim = r.get("similarity_score", 0.0)
                    with st.expander(f"Result {idx+1}: {meta.get('document_name', 'Document')} (Page {meta.get('page_number', 1)}) — Relevance: {sim*100:.1f}%", expanded=(idx==0)):
                        st.markdown(f"**Claim Attribution:** `{meta.get('claim_id', 'Unknown')}`")
                        st.markdown(f"**Document Type:** `{meta.get('document_type', 'Evidence')}`")
                        st.markdown(f"**Verified Record:** `{'Yes' if meta.get('is_verified') else 'No'}`")
                        st.markdown("---")
                        st.markdown(f"*{r['text']}*")
            else:
                st.info("No matching passages found. Ensure claim documents are indexed in ChromaDB.")

    with c2:
        render_section_title("Document Ingestion & Text Inspection")
        if docs:
            df_docs = pd.DataFrame(docs)
            st.dataframe(
                df_docs[["document_id", "claim_id", "document_name", "document_type", "ocr_confidence", "is_verified"]],
                use_container_width=True,
                hide_index=True
            )

            # Inspect sample document text
            doc_choices = [f"{d['document_name']} ({d['claim_id']})" for d in docs]
            selected_doc_str = st.selectbox("Select Evidence Record to Inspect:", doc_choices)
            if selected_doc_str:
                sel_idx = doc_choices.index(selected_doc_str)
                sel_doc = docs[sel_idx]
                st.markdown(f"**Extracted Text Sample for `{sel_doc['document_name']}`:**")
                st.text_area("", value=sel_doc["extracted_text"], height=160, disabled=True)
        else:
            st.info("No evidence documents currently recorded in database.")
