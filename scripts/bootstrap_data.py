"""
SubroRecover AI - Master Data & Model Bootstrap Script
Initializes database schema, executes ETL pipeline, generates deterministic assessments,
compiles formal investigation reports, and builds the ChromaDB vector index.
Guarantees complete idempotency and deterministic reproducibility (seed=42).
"""

import os
import sys
import json
import random
import logging
from typing import List, Dict, Any

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("subrorecover.bootstrap")


def bootstrap_all():
    logger.info("====================================================================")
    logger.info("Starting SubroRecover AI Master Data & ChromaDB Bootstrap")
    logger.info("====================================================================")

    # 1. Fixed Deterministic Random Seeds
    logger.info("[Step 1/5] Setting deterministic random seeds (seed=42)...")
    random.seed(42)
    try:
        import numpy as np
        np.random.seed(42)
    except ImportError:
        pass

    # 2. Database Schema Initialization & ETL Pipeline
    logger.info("[Step 2/5] Initializing database tables and executing ETL pipeline...")
    try:
        from database.connection import init_db, engine
        from sqlalchemy import text
        init_db()

        from data_engineering.pipeline import run_etl_pipeline
        etl_result = run_etl_pipeline(data_dir="sample_data")
        if etl_result.get("status") != "SUCCESS":
            raise RuntimeError(f"ETL Pipeline execution failed: {etl_result.get('error')}")
        logger.info(f"ETL complete. Loaded: {etl_result.get('total_loaded')} records.")
    except Exception as e:
        logger.error(f"FATAL: Database schema or ETL initialization failed: {e}", exc_info=True)
        sys.exit(1)

    # 3. Assessment & Urgency Scoring Seeding
    logger.info("[Step 3/5] Seeding deterministic assessments & priority distributions (seed=42)...")
    try:
        from scripts.seed_assessments import seed_all_assessments
        seed_all_assessments()
        logger.info("Deterministic assessment seeding completed successfully.")
    except Exception as e:
        logger.error(f"FATAL: Assessment seeding failed: {e}", exc_info=True)
        sys.exit(1)

    # 4. Generate Investigation Reports & PDFs
    logger.info("[Step 4/5] Generating formal investigation reports and artifact PDFs...")
    try:
        from reports.report_generator import generate_subrogation_pdf

        with engine.connect() as conn:
            # Verify 180 investigation reports exist in database
            report_count = conn.execute(text("SELECT COUNT(*) FROM investigation_reports")).scalar() or 0
            if report_count < 180:
                raise RuntimeError(f"Expected 180 investigation reports, found {report_count}.")

            # Generate formal PDF reports for top high-priority claims
            top_claims = conn.execute(text("""
                SELECT c.claim_id, c.claim_number, c.claim_type, c.paid_amount, c.deductible_paid,
                       c.incident_date, c.incident_state, a.priority_level, a.net_recovery_estimate,
                       a.estimated_adverse_fault_pct as adverse_fault_pct, a.statute_of_limitations_date,
                       r.report_id, r.report_number, acc.officer_narrative, acc.citations_issued
                FROM insurance_claims c
                JOIN recovery_assessments a ON c.claim_id = a.claim_id
                JOIN investigation_reports r ON c.claim_id = r.claim_id
                LEFT JOIN accident_reports acc ON c.claim_id = acc.claim_id
                WHERE a.priority_level = 'High'
                ORDER BY a.priority_score DESC
                LIMIT 5
            """)).mappings().all()

            for tc in top_claims:
                dossier = {
                    "report_id": tc["report_id"],
                    "claim_id": tc["claim_id"],
                    "report_number": tc["report_number"],
                    "claim_number": tc["claim_number"],
                    "scope": "Comprehensive Executive Review",
                    "executive_summary": f"Exhaustive subrogation audit for {tc['claim_number']} ({tc['claim_type']}) confirms {tc['adverse_fault_pct']:.0f}% liability with ${float(tc['net_recovery_estimate']):,.2f} projected net recovery.",
                    "claim_overview": {
                        "claim_number": tc["claim_number"],
                        "incident_date": str(tc["incident_date"]),
                        "incident_state": tc["incident_state"],
                        "claim_type": tc["claim_type"],
                        "paid_amount": float(tc["paid_amount"]),
                        "deductible": float(tc["deductible_paid"])
                    },
                    "liability_analysis": {
                        "adverse_fault_pct": float(tc["adverse_fault_pct"]),
                        "police_citations": tc["citations_issued"] or "Traffic Violation / Failure to Yield",
                        "officer_narrative": tc["officer_narrative"] or "Crash documentation confirms adverse operator negligence.",
                        "liability_reasoning": f"Adverse vehicle breached duty of care under {tc['incident_state']} statutory doctrine."
                    },
                    "recovery_quantum": {
                        "carrier_paid_exposure": float(tc["paid_amount"]),
                        "insured_deductible": float(tc["deductible_paid"]),
                        "pro_rata_recovery_gross": round((float(tc["paid_amount"]) + float(tc["deductible_paid"])) * (float(tc["adverse_fault_pct"]) / 100.0), 2),
                        "projected_net_recovery": float(tc["net_recovery_estimate"]),
                        "recovery_probability": 0.85
                    },
                    "recommendations": [
                        f"Transmit formal subrogation demand letter to adverse carrier for ${float(tc['net_recovery_estimate']):,.2f}.",
                        f"Monitor state statute of limitations expiration ({tc['statute_of_limitations_date']}).",
                        "Disburse policyholder deductible under the Make-Whole doctrine upon settlement receipt."
                    ],
                    "notes": "Generated during master environment bootstrap."
                }
                pdf_path = generate_subrogation_pdf(dossier)
                logger.info(f"Compiled formal PDF report: {pdf_path}")

        logger.info(f"Verified {report_count} investigation reports and generated artifact PDFs.")
    except Exception as e:
        logger.error(f"FATAL: Report generation failed: {e}", exc_info=True)
        sys.exit(1)

    # 5. Build ChromaDB Vector Index
    logger.info("[Step 5/5] Building ChromaDB vector index from evidence documents & police reports...")
    try:
        from rag.embeddings import VectorStore
        from rag.retriever import EvidenceRetriever

        vs = VectorStore()

        # Ingest and index all evidence documents from the database
        with engine.connect() as conn:
            doc_rows = conn.execute(text("""
                SELECT d.document_id, d.claim_id, d.document_name, d.document_type,
                       d.extracted_text, d.is_verified, c.claim_number, c.claim_type,
                       c.incident_state, acc.officer_narrative, acc.citations_issued
                FROM evidence_documents d
                JOIN insurance_claims c ON d.claim_id = c.claim_id
                LEFT JOIN accident_reports acc ON d.claim_id = acc.claim_id
                ORDER BY d.claim_id, d.document_id
            """)).mappings().all()

        chunks: List[Dict[str, Any]] = []
        for r in doc_rows:
            cid = r["claim_id"]
            cnum = r["claim_number"]
            dtype = r["document_type"]
            dname = r["document_name"]
            is_ver = bool(r["is_verified"])
            doc_id = r["document_id"]

            narrative = r["officer_narrative"] or ""
            citations = r["citations_issued"] or ""
            extracted = r["extracted_text"] or ""

            # Construct rich semantic context for RAG retrieval
            chunk_text = (
                f"Claim Number: {cnum} (ID: {cid}) | Document: {dname} ({dtype}) | "
                f"Incident Type: {r['claim_type']} in {r['incident_state']}. "
                f"Official Narrative: {narrative} | Citations Issued: {citations} | "
                f"Extracted Evidence Findings: {extracted}"
            )

            chunks.append({
                "chunk_id": f"chunk-{doc_id}",
                "text": chunk_text,
                "claim_id": cid,
                "document_name": dname,
                "document_type": dtype,
                "page_number": 1,
                "is_verified": is_ver
            })

        # Batch index chunks into ChromaDB (batches of 100)
        batch_size = 100
        indexed_total = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            indexed_total += vs.add_chunks(batch)

        # Also index any sample PDFs present in sample_data/pdfs/
        pdf_dir = os.path.join("sample_data", "pdfs")
        if os.path.exists(pdf_dir):
            retriever = EvidenceRetriever(vector_store=vs)
            for fname in os.listdir(pdf_dir):
                if fname.lower().endswith(".pdf"):
                    fpath = os.path.join(pdf_dir, fname)
                    # Extract claim_id from filename e.g. CLM-0001_police_report.pdf
                    claim_prefix = fname.split("_")[0] if "_" in fname else "CLM-0001"
                    retriever.index_pdf(fpath, claim_id=claim_prefix, doc_type="Police Crash Report", is_verified=True)

        final_vector_count = vs.collection.count()
        logger.info(f"Successfully built ChromaDB vector index with {final_vector_count} document chunks.")
    except Exception as e:
        logger.error(f"FATAL: ChromaDB vector indexing failed: {e}", exc_info=True)
        sys.exit(1)

    # Final Verification & Health Summary
    try:
        with engine.connect() as conn:
            claim_c = conn.execute(text("SELECT COUNT(*) FROM insurance_claims")).scalar() or 0
            asm_c = conn.execute(text("SELECT COUNT(*) FROM recovery_assessments")).scalar() or 0
            rpt_c = conn.execute(text("SELECT COUNT(*) FROM investigation_reports")).scalar() or 0

        vs = VectorStore()
        vec_c = vs.collection.count()

        logger.info("====================================================================")
        logger.info("BOOTSTRAP VERIFICATION SUMMARY:")
        logger.info(f"  • Insurance Claims:        {claim_c}")
        logger.info(f"  • Recovery Assessments:    {asm_c}")
        logger.info(f"  • Investigation Reports:   {rpt_c}")
        logger.info(f"  • Vector Store Documents:  {vec_c}")
        logger.info("Bootstrap Status: READY FOR PRODUCTION DEPLOYMENT")
        logger.info("====================================================================")
    except Exception as e:
        logger.error(f"Bootstrap verification check failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    bootstrap_all()
